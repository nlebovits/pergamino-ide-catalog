"""Place a collection's default MapLibre style.

``portolan extract wfs`` converts the SLD style GeoNode serves for a layer
into a MapLibre style. The catalog keeps its own copy at
``styles/default.json``, wired to the collection's PMTiles. A fresh
conversion replaces it only when the cartography differs, so a style fixed
by hand (``tools/generate/fix_styles.py``) survives an extract that changed
nothing upstream.
"""
from __future__ import annotations

import json
from pathlib import Path

import stac_versions as stac
from extract import PMTILES_MAX_ZOOM


def style_body(style: dict) -> str:
    """A style's cartography, without the source wiring that differs."""
    layers = json.loads(json.dumps(style.get("layers", [])))
    for layer in layers:
        layer.pop("source-layer", None)
        layer.pop("source", None)
    return json.dumps(layers, sort_keys=True)


def place_style(folder: Path, fresh: Path | None, leaf: str) -> str:
    """Write ``styles/default.json``; say which style it is."""
    target = folder / "styles" / "default.json"
    current = json.loads(target.read_text()) if target.exists() else None
    new = json.loads(fresh.read_text()) if fresh else None
    if new is not None and (current is None
                            or style_body(new) != style_body(current)):
        chosen, why = new, "GeoNode"
    elif current is not None:
        chosen, why = current, "kept"
    else:
        return "none"
    for layer in chosen.get("layers", []):
        if "source-layer" in layer:
            layer["source-layer"] = leaf
    for source in (chosen.get("sources") or {}).values():
        source["type"] = source.get("type", "vector")
        source["url"] = f"pmtiles://../{leaf}.pmtiles"
        source["minzoom"] = 0
        source["maxzoom"] = PMTILES_MAX_ZOOM
    target.parent.mkdir(parents=True, exist_ok=True)
    stac.write_json(target, chosen)
    return why


# --------------------------------------------------------------------------
# Repairs for defects of the SLD-to-MapLibre conversion. MapLibre rejects the
# whole style on any of them, so the layer renders nothing at all.

NUMERIC = ("BIGINT", "INTEGER", "SMALLINT", "TINYINT", "HUGEINT", "UBIGINT",
           "UINTEGER", "USMALLINT", "UTINYINT", "DOUBLE", "FLOAT", "DECIMAL")


def column_types(parquet: Path) -> dict[str, str]:
    import duckdb

    rows = duckdb.connect().execute(
        "SELECT column_name, column_type FROM (DESCRIBE SELECT * FROM "
        "read_parquet(?))", [str(parquet)]).fetchall()
    return {name: ctype for name, ctype in rows}


def as_text(value) -> str:
    """A number the way MapLibre's ``to-string`` writes it: 1.0 is "1"."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def is_integral(value) -> bool:
    """True for a whole number, or text that reads as one ("-1", "2.0")."""
    if isinstance(value, bool):
        return False
    try:
        return float(value).is_integer()
    except (TypeError, ValueError):
        return False


def type_labels(expr: list, ctype: str) -> tuple[list, str | None]:
    """Make every label of a ``match`` on ``["get", col]`` one valid type.

    A text column takes text labels. An integer column takes integer labels.
    A decimal column is matched as text, because MapLibre allows only integer
    number labels.
    """
    head, body, fallback = expr[:2], expr[2:-1], expr[-1]
    labels = body[0::2]
    flat = [x for label in labels for x in (label if isinstance(label, list)
                                             else [label])]
    numeric = ctype.split("(")[0] in NUMERIC
    integral = all(is_integral(x) for x in flat)
    if numeric and integral:
        convert, note = (lambda x: int(float(x))), None
    else:
        convert = as_text
        note = "labels matched as text"
        if numeric and head[1][:1] != ["to-string"]:
            head = [head[0], ["to-string", head[1]]]
    if head == expr[:2] and all(
            convert(x) == x and type(convert(x)) is type(x) for x in flat):
        return expr, None
    out = list(head)
    for label, value in zip(body[0::2], body[1::2]):
        if isinstance(label, list):
            label = [convert(x) for x in label]
        else:
            try:
                label = convert(label)
            except ValueError:
                continue
        out += [label, value]
    return out + [fallback], note or "labels typed to the column"


def is_color_slot(prop: str) -> bool:
    return prop.endswith("-color")


def sld_colors(sld: bytes) -> dict[str, dict[str, str]]:
    """{label: {"fill"|"stroke": colour}} from each rule's literal or
    ``strConcat`` of literals, for rules with one PropertyIsEqualTo."""
    import xml.etree.ElementTree as ET

    out: dict[str, dict[str, str]] = {}
    for rule in ET.fromstring(sld).iter():
        if not rule.tag.endswith("}Rule"):
            continue
        literal = None
        for el in rule.iter():
            if el.tag.endswith("PropertyIsEqualTo"):
                lits = [c for c in el if c.tag.endswith("Literal")]
                literal = (lits[0].text or "").strip() if lits else None
        if literal is None:
            continue
        for param in rule.iter():
            if not (param.tag.endswith("CssParameter")
                    or param.tag.endswith("SvgParameter")):
                continue
            name = param.get("name")
            if name not in ("fill", "stroke"):
                continue
            text = "".join((lit.text or "") for lit in param.iter()
                           if lit.tag.endswith("Literal"))
            text = text or (param.text or "")
            out.setdefault(literal, {}).setdefault(name, text.strip())
    return out


def blank_colors(style: dict) -> bool:
    for layer in style.get("layers", []):
        for prop, value in (layer.get("paint") or {}).items():
            if is_color_slot(prop) and isinstance(value, list):
                if any(isinstance(v, str) and not v.strip() for v in value):
                    return True
    return False


def fill_blank_colors(expr: list, prop: str, colors: dict) -> list:
    """Replace blank colour outputs with the colour the SLD rule computes."""
    which = "stroke" if ("outline" in prop or prop.startswith("line")) \
        else "fill"
    out = list(expr[:2])
    for label, value in zip(expr[2:-1:2], expr[3:-1:2]):
        if isinstance(value, str) and not value.strip():
            value = colors.get(as_text(label), {}).get(which) or expr[-1]
        out += [label, value]
    return out + [expr[-1]]


def sld_strokes(sld: bytes) -> list[tuple[str, float] | None]:
    """The stroke of each symbolizer of a one-rule SLD, in order.

    Each entry is (colour, width), or None for a symbolizer with no stroke.
    The list is empty unless the SLD has exactly one rule. SLD's default
    stroke colour is black, so a stroke that gives only a width is black.
    """
    import xml.etree.ElementTree as ET

    rules = [r for r in ET.fromstring(sld).iter() if r.tag.endswith("}Rule")]
    if len(rules) != 1:
        return []
    out: list[tuple[str, float] | None] = []
    for symbolizer in rules[0]:
        if not symbolizer.tag.endswith("Symbolizer") or \
                symbolizer.tag.endswith("TextSymbolizer"):
            continue
        strokes = [el for el in symbolizer.iter()
                   if el.tag.endswith("}Stroke")]
        if not strokes:
            out.append(None)
            continue
        params = {p.get("name"): (p.text or "").strip() for p in strokes[0]
                  if p.tag.endswith("CssParameter")
                  or p.tag.endswith("SvgParameter")}
        try:
            width = float(params.get("stroke-width") or 1)
        except ValueError:
            width = 1.0
        out.append((params.get("stroke") or "#000000", width))
    return out


def needs_stroke(style: dict) -> bool:
    """A fill or circle layer that draws no outline."""
    for layer in style.get("layers", []):
        paint = layer.get("paint") or {}
        if layer.get("type") == "fill" and "fill-outline-color" not in paint:
            return True
        if layer.get("type") == "circle" and "circle-stroke-color" not in paint:
            return True
    return False


def add_stroke(style: dict,
               strokes: list[tuple[str, float] | None]) -> list[str]:
    """Give each layer the outline its SLD symbolizer declares.

    Layers pair with symbolizers by order when the counts agree. Otherwise
    every layer takes the first stroke.
    """
    layers = [layer for layer in style.get("layers", [])
              if layer.get("type") != "symbol"]
    if len(strokes) != len(layers):
        first = next((s for s in strokes if s), None)
        strokes = [first] * len(layers)
    notes = []
    for layer, stroke in zip(layers, strokes):
        if stroke is None:
            continue
        color, width = stroke
        paint = layer.setdefault("paint", {})
        if layer.get("type") == "fill" and "fill-outline-color" not in paint:
            paint["fill-outline-color"] = color
            notes.append(f"{layer.get('id')}: outline from the SLD")
        elif layer.get("type") == "circle" and \
                "circle-stroke-color" not in paint:
            paint["circle-stroke-color"] = color
            paint["circle-stroke-width"] = min(width, 3.0)
            notes.append(f"{layer.get('id')}: stroke from the SLD")
    return notes


def point_radius(style: dict, sld: bytes) -> list[str]:
    """Set the CLI's categorical point radius to half the SLD ``Size``.

    SLD ``Size`` is a mark's diameter. The CLI halves it for unfiltered
    rules but uses it as the radius for categorical ones, so those points
    draw at twice the publisher's size. The radius is read from the SLD, not
    halved in place, so a second repair leaves it unchanged.
    """
    import xml.etree.ElementTree as ET

    from generate import sld_stacked

    layers = [layer for layer in style.get("layers", [])
              if layer.get("id") == "categorical-circle"]
    if not layers:
        return []
    try:
        column, rules = sld_stacked.parse(sld)
    except (sld_stacked.Unsupported, ET.ParseError):
        return []
    if not rules or any(rule["symbolizers"][0]["kind"] != "circle"
                        for rule in rules):
        return []
    # The CLI's default for a value no rule names is a size of 5.
    radius = sld_stacked.paint_value(column, rules, 0, "radius", 2.5,
                                     lambda label: label)
    notes = []
    for layer in layers:
        paint = layer.setdefault("paint", {})
        if paint.get("circle-radius") != radius:
            paint["circle-radius"] = radius
            notes.append(f"{layer['id']}.circle-radius: half the SLD Size")
    return notes


def repair(style: dict, types: dict[str, str],
           sld: bytes | None = None) -> list[str]:
    """Fix the style in place; return a note per change."""
    notes = point_radius(style, sld) if sld else []
    colors = sld_colors(sld) if sld else {}
    strokes = sld_strokes(sld) if sld else []
    if strokes:
        notes += add_stroke(style, strokes)
    for layer in style.get("layers", []):
        paint = layer.get("paint") or {}
        for prop, value in list(paint.items()):
            if not (isinstance(value, list) and value[:1] == ["match"]
                    and isinstance(value[1], list) and value[1][:1] == ["get"]):
                continue
            column = value[1][1]
            if column in types:
                value, note = type_labels(value, types[column])
                if note:
                    notes.append(f"{layer.get('id')}.{prop}: {note}")
            if is_color_slot(prop) and any(
                    isinstance(v, str) and not v.strip() for v in value):
                value = fill_blank_colors(value, prop, colors)
                notes.append(f"{layer.get('id')}.{prop}: colours from the SLD")
            paint[prop] = value
    return notes
