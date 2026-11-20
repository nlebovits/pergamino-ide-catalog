"""Convert categorical SLDs with stacked symbolizers into MapLibre styles.

GeoServer draws every symbolizer of a rule, in order. Many of the
municipality's styles depend on that: a street is a grey casing under a
coloured line, a camera is a white disc with a dark ring under a coloured
mark. The Portolan CLI's converter keeps the first symbolizer of each rule
and drops the rest, so those layers render as the casing alone, or as white
on white.

This converter handles rules whose filter is absent, an ``ElseFilter``, or
one ``PropertyIsEqualTo``. Symbolizer *i* of every rule becomes MapLibre
layer *i*, whose paint values are a ``match`` on the filtered column. A rule
with no symbolizer *i* draws nothing in that layer. Label rules
(``TextSymbolizer``) are left to the CLI's conversion, whose symbol layers
are kept.

GeoServer draws each FeatureTypeStyle over the ones before it, and each can
filter on its own column. Each one converts on its own, and its layers
follow those of the one before. A FeatureTypeStyle of range filters goes to
``sld_graduated.py``.

A style it cannot express returns None, and the CLI's conversion stays:
a filter of another kind, a value read from a property, an icon, or rules
whose symbolizer *i* differ in geometry kind.
"""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET

# A scale denominator to a web map zoom, at 0.28 mm per pixel.
ZOOM0_SCALE = 559082264.028


def local(tag: str) -> str:
    return tag.split("}")[-1]


def zoom(scale: str | None) -> float | None:
    if not scale:
        return None
    try:
        return round(math.log2(ZOOM0_SCALE / float(scale)), 2)
    except (ValueError, ZeroDivisionError):
        return None


class Unsupported(Exception):
    pass


def value_of(param) -> str:
    """A CssParameter's value: text, a Literal, or strConcat of Literals."""
    for el in param.iter():
        if local(el.tag) == "PropertyName":
            raise Unsupported("a value read from a property")
    literals = [el.text or "" for el in param.iter()
                if local(el.tag) == "Literal"]
    return ("".join(literals) if literals else (param.text or "")).strip()


def params(node) -> dict[str, str]:
    if node is None:
        return {}
    return {p.get("name"): value_of(p) for p in node
            if local(p.tag) in ("CssParameter", "SvgParameter")}


def number(value: str | None, default: float) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except ValueError:
        return default


def child(node, name: str):
    return next((c for c in node.iter() if local(c.tag) == name), None)


def symbolizer(node) -> dict:
    kind = local(node.tag)
    if kind == "PointSymbolizer":
        if child(node, "ExternalGraphic") is not None:
            raise Unsupported("an icon (ExternalGraphic)")
        mark = child(node, "Mark")
        fill = params(child(mark, "Fill")) if mark is not None else {}
        stroke = params(child(mark, "Stroke")) if mark is not None else {}
        size = child(node, "Size")
        return {
            "kind": "circle",
            "color": fill.get("fill") or "#000000",
            "opacity": number(fill.get("fill-opacity"), 1.0)
            if fill else 0.0,
            "radius": number(size.text if size is not None else None, 6) / 2,
            # SLD draws a Stroke with no colour in black.
            "stroke": (stroke.get("stroke") or "#000000") if stroke else None,
            "stroke_width": number(stroke.get("stroke-width"), 1.0)
            if stroke else 0.0,
            "stroke_opacity": number(stroke.get("stroke-opacity"), 1.0),
        }
    if kind == "LineSymbolizer":
        stroke = params(child(node, "Stroke"))
        return {
            "kind": "line",
            "color": stroke.get("stroke") or "#000000",
            "opacity": number(stroke.get("stroke-opacity"), 1.0),
            "width": number(stroke.get("stroke-width"), 1.0),
            "dash": stroke.get("stroke-dasharray"),
        }
    if kind == "PolygonSymbolizer":
        fill_node = child(node, "Fill")
        stroke_node = child(node, "Stroke")
        fill = params(fill_node)
        stroke = params(stroke_node)
        return {
            "kind": "fill",
            "color": fill.get("fill") or "#808080",
            "opacity": number(fill.get("fill-opacity"), 1.0)
            if fill_node is not None else 0.0,
            "stroke": (stroke.get("stroke") or "#000000")
            if stroke_node is not None else None,
            "stroke_width": number(stroke.get("stroke-width"), 1.0),
            "stroke_opacity": number(stroke.get("stroke-opacity"), 1.0),
        }
    raise Unsupported(f"symbolizer {kind}")


def feature_type_styles(sld: bytes) -> list:
    """Each FeatureTypeStyle element, in drawing order."""
    root = ET.fromstring(sld)
    styles = [f for f in root.iter() if local(f.tag) == "FeatureTypeStyle"]
    return styles or [root]


def parse_all(sld: bytes) -> list[tuple[str | None, list[dict]]]:
    """(filtered column, rules) for each FeatureTypeStyle, in drawing order."""
    return [parse_rules(style) for style in feature_type_styles(sld)]


def parse(sld: bytes) -> tuple[str | None, list[dict]]:
    """(filtered column, rules) of an SLD with one FeatureTypeStyle."""
    parsed = parse_all(sld)
    if len(parsed) != 1:
        raise Unsupported("more than one FeatureTypeStyle")
    return parsed[0]


def parse_rules(root) -> tuple[str | None, list[dict]]:
    """(filtered column, rules). Each rule: label, else, symbolizers, zooms."""
    column, rules = None, []
    for rule in root.iter():
        if local(rule.tag) != "Rule":
            continue
        drawn = [c for c in rule if local(c.tag).endswith("Symbolizer")
                 and local(c.tag) != "TextSymbolizer"]
        if not drawn:
            continue
        label, is_else = None, False
        for c in rule:
            if local(c.tag) == "ElseFilter":
                is_else = True
            if local(c.tag) != "Filter":
                continue
            tests = list(c)
            if len(tests) != 1 or local(tests[0].tag) != "PropertyIsEqualTo":
                raise Unsupported("a filter other than PropertyIsEqualTo")
            name = child(tests[0], "PropertyName")
            literal = child(tests[0], "Literal")
            if name is None or literal is None:
                raise Unsupported("an incomplete PropertyIsEqualTo")
            if column not in (None, name.text.strip()):
                raise Unsupported("filters on two columns")
            column = name.text.strip()
            label = (literal.text or "").strip()
        min_scale = child(rule, "MinScaleDenominator")
        max_scale = child(rule, "MaxScaleDenominator")
        rules.append({
            "label": label, "else": is_else or label is None,
            "symbolizers": [symbolizer(s) for s in drawn],
            "minzoom": zoom(max_scale.text if max_scale is not None else None),
            "maxzoom": zoom(min_scale.text if min_scale is not None else None),
        })
    return column, rules


def is_stacked(sld: bytes) -> bool:
    """True when the SLD has more than one FeatureTypeStyle, or a rule draws
    more than one symbolizer or a point symbol with a ring. The CLI's
    converter loses each of these."""
    try:
        if len(feature_type_styles(sld)) > 1:
            return True
        parsed = parse_all(sld)
    except (Unsupported, ET.ParseError):
        return False
    for rule in (rule for _, rules in parsed for rule in rules):
        if len(rule["symbolizers"]) > 1:
            return True
        if any(s["kind"] == "circle" and s["stroke"]
               for s in rule["symbolizers"]):
            return True
    return False


def paint_value(column, rules, i, key, hidden, label_of):
    """A constant when every rule agrees, else a match on ``column``."""
    values = []
    for rule in rules:
        syms = rule["symbolizers"]
        value = syms[i].get(key) if i < len(syms) else None
        values.append(hidden if value is None else value)
    fallback = next((v for r, v in zip(rules, values) if r["else"]), hidden)
    keyed = [(label_of(r["label"]), v) for r, v in zip(rules, values)
             if not r["else"]]
    if not keyed:
        return fallback
    if all(v == keyed[0][1] for _, v in keyed) and (
            fallback == keyed[0][1] or column is None):
        return keyed[0][1]
    expr = ["match", ["get", column]]
    seen = set()
    for label, value in keyed:
        if label in seen:
            continue
        seen.add(label)
        expr += [label, value]
    return expr + [fallback]


def convert(sld: bytes, source_layer: str, cli_style: dict | None = None
            ) -> dict | None:
    """A MapLibre style for the SLD, or None when it cannot be expressed."""
    try:
        styles = feature_type_styles(sld)
    except ET.ParseError:
        return None
    layers = []
    for n, element in enumerate(styles):
        try:
            column, rules = parse_rules(element)
            converted = (convert_rules(column, rules, source_layer)
                         if rules else [])
        except Unsupported:
            converted = graduated(element, source_layer)
        if converted is None:
            return None
        prefix = f"sld-{n}-" if len(styles) > 1 else "sld-"
        for layer in converted:
            layer["id"] = prefix + layer["id"]
        layers += converted
    if not layers:
        return None
    labels = [layer for layer in (cli_style or {}).get("layers", [])
              if layer.get("type") == "symbol"]
    style = dict(cli_style or {"version": 8})
    style["sources"] = (cli_style or {}).get("sources") or {
        "data": {"type": "vector"}}
    style["layers"] = layers + labels
    return style


def graduated(element, source_layer: str) -> list[dict] | None:
    """The layers for a FeatureTypeStyle of range filters, or None.

    ``sld_graduated`` reads only the ranges. A rule that tests one value of
    the same column, such as -1 for "no data", wraps the ramp in a match.
    """
    from generate.sld_graduated import convert_graduated

    converted = convert_graduated(ET.tostring(element), source_layer)
    if not converted:
        return None
    style, field, _ = converted
    layer = style["layers"][0]
    key = f"{layer['type']}-color"
    cases = []
    for rule in element.iter():
        if local(rule.tag) != "Rule":
            continue
        tests = [list(f) for f in rule if local(f.tag) == "Filter"]
        drawn = [c for c in rule if local(c.tag).endswith("Symbolizer")
                 and local(c.tag) != "TextSymbolizer"]
        if len(tests) != 1 or len(tests[0]) != 1 or not drawn or (
                local(tests[0][0].tag) != "PropertyIsEqualTo"):
            continue
        name = child(tests[0][0], "PropertyName")
        literal = child(tests[0][0], "Literal")
        if name is None or literal is None or name.text.strip() != field:
            continue
        cases += [(literal.text or "").strip(), symbolizer(drawn[0])["color"]]
    if cases:
        layer["paint"][key] = ["match", ["get", field], *cases,
                               layer["paint"][key]]
    return style["layers"]


def convert_rules(column: str | None, rules: list[dict], source_layer: str
                  ) -> list[dict] | None:
    """The layers for one FeatureTypeStyle, or None if it cannot convert."""
    depth = max(len(r["symbolizers"]) for r in rules)
    kinds = []
    for i in range(depth):
        found = {r["symbolizers"][i]["kind"] for r in rules
                 if i < len(r["symbolizers"])}
        if len(found) != 1:
            return None
        kinds.append(found.pop())

    def label_of(label):
        return label

    def value(i, key, hidden):
        return paint_value(column, rules, i, key, hidden, label_of)

    zooms = {(r["minzoom"], r["maxzoom"]) for r in rules}
    minzoom, maxzoom = zooms.pop() if len(zooms) == 1 else (None, None)
    layers = []
    for i, kind in enumerate(kinds):
        base = {"source": "data", "source-layer": source_layer}
        if kind == "circle":
            paint = {
                "circle-color": value(i, "color", "#000000"),
                "circle-opacity": value(i, "opacity", 0),
                "circle-radius": value(i, "radius", 0),
                "circle-stroke-color": value(i, "stroke", "#000000"),
                "circle-stroke-width": value(i, "stroke_width", 0),
                "circle-stroke-opacity": value(i, "stroke_opacity", 0),
            }
            if paint["circle-stroke-width"] == 0:
                for key in ("circle-stroke-color", "circle-stroke-width",
                            "circle-stroke-opacity"):
                    paint.pop(key)
            layers.append({"id": f"{i}-circle", "type": "circle",
                           **base, "paint": paint})
        elif kind == "line":
            paint = {"line-color": value(i, "color", "#000000"),
                     "line-opacity": value(i, "opacity", 0),
                     "line-width": value(i, "width", 0)}
            dash = value(i, "dash", None)
            if isinstance(dash, str) and dash:
                paint["line-dasharray"] = [
                    number(d, 1) for d in dash.replace(",", " ").split()]
            layers.append({"id": f"{i}-line", "type": "line", **base,
                           "layout": {"line-join": "round",
                                      "line-cap": "round"},
                           "paint": paint})
        else:
            layers.append({"id": f"{i}-fill", "type": "fill", **base,
                           "paint": {"fill-color": value(i, "color", "#000000"),
                                     "fill-opacity": value(i, "opacity", 0)}})
            if any(i < len(r["symbolizers"]) and r["symbolizers"][i]["stroke"]
                   for r in rules):
                layers.append({
                    "id": f"{i}-outline", "type": "line", **base,
                    "paint": {"line-color": value(i, "stroke", "#000000"),
                              "line-width": value(i, "stroke_width", 0),
                              "line-opacity": value(i, "stroke_opacity", 0)}})
    for layer in layers:
        if minzoom is not None:
            layer["minzoom"] = minzoom
        if maxzoom is not None:
            layer["maxzoom"] = maxzoom
    return layers
