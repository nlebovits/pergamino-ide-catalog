#!/usr/bin/env python3
"""The repairs to the Portolan CLI's SLD conversion.

The CLI's converter loses parts of the municipality's SLDs. Two modules fix
its output, and each fix is checked here on a small SLD, without network
access:

- ``generate/sld_stacked.py`` converts again when a rule stacks symbolizers,
  a point mark has a ring, or the SLD has several FeatureTypeStyles.
- ``styles.repair`` types ``match`` labels to the column, fills colours the
  CLI left blank, adds strokes, and halves a categorical point's ``Size``.
  A second repair changes nothing.

Run: python3 tests/test_styles.py
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import styles  # noqa: E402
from generate import sld_stacked  # noqa: E402

errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


HEAD = ('<StyledLayerDescriptor version="1.0.0" '
        'xmlns="http://www.opengis.net/sld" '
        'xmlns:ogc="http://www.opengis.net/ogc"><NamedLayer><Name>x</Name>'
        '<UserStyle>')
TAIL = '</UserStyle></NamedLayer></StyledLayerDescriptor>'


def sld(*feature_type_styles: str) -> bytes:
    body = "".join(f"<FeatureTypeStyle>{f}</FeatureTypeStyle>"
                   for f in feature_type_styles)
    return (HEAD + body + TAIL).encode()


def equal_to(field: str, value: str) -> str:
    return (f'<ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>{field}'
            f'</ogc:PropertyName><ogc:Literal>{value}</ogc:Literal>'
            f'</ogc:PropertyIsEqualTo></ogc:Filter>')


def between(field: str, low: float, high: float) -> str:
    return (f'<ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan>'
            f'<ogc:PropertyName>{field}</ogc:PropertyName>'
            f'<ogc:Literal>{low}</ogc:Literal></ogc:PropertyIsGreaterThan>'
            f'<ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>{field}'
            f'</ogc:PropertyName><ogc:Literal>{high}</ogc:Literal>'
            f'</ogc:PropertyIsLessThanOrEqualTo></ogc:And></ogc:Filter>')


def css(name: str, value) -> str:
    return f'<CssParameter name="{name}">{value}</CssParameter>'


def line(color: str, width: float) -> str:
    return (f'<LineSymbolizer><Stroke>{css("stroke", color)}'
            f'{css("stroke-width", width)}</Stroke></LineSymbolizer>')


def polygon(color: str) -> str:
    return f'<PolygonSymbolizer><Fill>{css("fill", color)}</Fill></PolygonSymbolizer>'


def mark(fill: str, size: float, stroke: str | None = None) -> str:
    ring = (f'<Stroke>{css("stroke", stroke)}{css("stroke-width", 2)}'
            f'</Stroke>' if stroke else "")
    return (f'<PointSymbolizer><Graphic><Mark><WellKnownName>circle'
            f'</WellKnownName><Fill>{css("fill", fill)}</Fill>{ring}</Mark>'
            f'<Size>{size}</Size></Graphic></PointSymbolizer>')


def rule(filter_xml: str, *symbolizers: str) -> str:
    return f"<Rule>{filter_xml}{''.join(symbolizers)}</Rule>"


def layers_by_id(style: dict) -> dict:
    return {layer["id"]: layer for layer in style["layers"]}


# --- sld_stacked: a casing under a coloured line --------------------------
CASING = sld(
    rule(equal_to("material", "asfalto"),
         line("#747474", 7), line("#e31a1c", 6))
    + rule(equal_to("material", "tierra"),
         line("#747474", 7), line("#a6611a", 6)))
check(sld_stacked.is_stacked(CASING), "two symbolizers in a rule stack")
style = sld_stacked.convert(CASING, "calles", {"version": 8, "layers": [
    {"id": "labels", "type": "symbol", "source": "data",
     "source-layer": "calles", "layout": {"text-field": ["get", "nombre"]}}]})
ids = [layer["id"] for layer in style["layers"]]
check(ids == ["sld-0-line", "sld-1-line", "labels"],
      f"symbolizer i becomes layer i, and the CLI's labels stay last: {ids}")
casing, colour = style["layers"][0], style["layers"][1]
check(casing["paint"]["line-color"][3::2][:2] == ["#747474", "#747474"],
      f"every rule draws the casing colour: {casing['paint']}")
check(casing["paint"]["line-opacity"][-1] == 0,
      f"GeoServer draws no feature that no rule matches: {casing['paint']}")
check(colour["paint"]["line-color"] == [
    "match", ["get", "material"], "asfalto", "#e31a1c",
    "tierra", "#a6611a", "#000000"],
      f"a value that differs is a match: {colour['paint']['line-color']}")
check(casing["paint"]["line-width"][3] == 7.0
      and colour["paint"]["line-width"][3] == 6.0,
      "each layer keeps its own width")

# --- sld_stacked: a point mark with a ring --------------------------------
RING = sld(rule(equal_to("tipo", "A"), mark("#ffffff", 10, "#1f78b4")))
check(sld_stacked.is_stacked(RING), "a mark with a stroke is stacked")
paint = sld_stacked.convert(RING, "x")["layers"][0]["paint"]
check(paint["circle-stroke-color"][3] == "#1f78b4"
      and paint["circle-stroke-width"][3] == 2.0,
      f"the ring becomes the circle stroke: {paint}")
check(paint["circle-radius"][3] == 5.0,
      f"SLD Size is a diameter, so the radius is half: {paint}")

# A Stroke that gives only a width is black, never null.
NO_COLOUR = sld(rule(
    equal_to("tipo", "A"),
    '<PointSymbolizer><Graphic><Mark><Fill>' + css("fill", "#ffffff")
    + '</Fill><Stroke>' + css("stroke-width", 1)
    + '</Stroke></Mark><Size>6</Size></Graphic></PointSymbolizer>'),
    )
paint = sld_stacked.convert(NO_COLOUR, "x")["layers"][0]["paint"]
check(paint.get("circle-stroke-color") == "#000000",
      f"a stroke with no colour draws black: {paint}")

# A rule with no symbolizer i hides that layer for its value.
UNEVEN = sld(
    rule(equal_to("tipo", "A"), mark("#ff0000", 6, "#123456"))
    + rule(equal_to("tipo", "B"), mark("#00ff00", 6)))
paint = sld_stacked.convert(UNEVEN, "x")["layers"][0]["paint"]
check(paint["circle-stroke-color"] == [
    "match", ["get", "tipo"], "A", "#123456", "B", "#000000", "#000000"],
      f"a rule with no stroke leaves no null in the match: {paint}")
check(paint["circle-stroke-width"] == [
    "match", ["get", "tipo"], "A", 2.0, "B", 0.0, 0],
      f"a rule with no stroke draws a zero-width one: {paint}")

# --- sld_stacked: several FeatureTypeStyles -------------------------------
LAYERED = sld(
    rule(equal_to("tipo", "abierto"), polygon("#1d91de")),
    rule(between("peso", 0, 4), polygon("#d7191c"))
    + rule(between("peso", 4, 8), polygon("#fdae61"))
    + rule(equal_to("peso", "-1"), polygon("#b2b2b2")))
check(sld_stacked.is_stacked(LAYERED),
      "several FeatureTypeStyles count as stacked")
style = sld_stacked.convert(LAYERED, "x")
by_id = layers_by_id(style)
check(list(by_id) == ["sld-0-0-fill", "sld-1-graduated-fill"],
      f"each FeatureTypeStyle converts on its own, in order: {list(by_id)}")
check(by_id["sld-0-0-fill"]["paint"]["fill-color"][1] == ["get", "tipo"],
      "the first FeatureTypeStyle matches its own column")
ramp = by_id["sld-1-graduated-fill"]["paint"]["fill-color"]
check(ramp[:4] == ["match", ["get", "peso"], "-1", "#b2b2b2"]
      and ramp[-1][0] == "step",
      f"an equality rule beside the ranges wraps the ramp: {ramp}")

UNSUPPORTED = sld(rule(
    equal_to("tipo", "A"),
    '<PointSymbolizer><Graphic><ExternalGraphic/></Graphic>'
    '</PointSymbolizer>', mark("#fff", 6)))
check(sld_stacked.convert(UNSUPPORTED, "x") is None,
      "an icon cannot be expressed, so the CLI's conversion stays")

# --- styles.type_labels ---------------------------------------------------
MATCH = ["match", ["get", "c"], 227, "#f00", 330, "#0f0", "#ccc"]
out, note = styles.type_labels(MATCH, "VARCHAR")
check(out == ["match", ["get", "c"], "227", "#f00", "330", "#0f0", "#ccc"],
      f"a text column takes text labels: {out}")
out, note = styles.type_labels(
    ["match", ["get", "c"], "-1", "#aaa", "#ccc"], "DECIMAL(38,0)")
check(out == ["match", ["get", "c"], -1, "#aaa", "#ccc"],
      f"a whole-number decimal takes integer labels, even from text: {out}")
out, note = styles.type_labels(
    ["match", ["get", "c"], 1.5, "#aaa", "#ccc"], "DOUBLE")
check(out == ["match", ["to-string", ["get", "c"]], "1.5", "#aaa", "#ccc"],
      f"a fractional label is matched as text: {out}")
check(styles.type_labels(out, "DOUBLE") == (out, None),
      "typed labels are left alone")

# --- styles.repair --------------------------------------------------------
CONCAT = sld(rule(
    equal_to("zona", "norte"),
    '<PolygonSymbolizer><Fill><CssParameter name="fill">'
    '<ogc:Function name="strConcat"><ogc:Literal>#</ogc:Literal>'
    '<ogc:Literal>33a02c</ogc:Literal></ogc:Function></CssParameter>'
    '</Fill></PolygonSymbolizer>'))
blank = {"version": 8, "layers": [{
    "id": "categorical-fill", "type": "fill",
    "paint": {"fill-color": ["match", ["get", "zona"], "norte", " ",
                             "#cccccc"]}}]}
notes = styles.repair(blank, {"zona": "VARCHAR"}, CONCAT)
check(blank["layers"][0]["paint"]["fill-color"][3] == "#33a02c",
      f"a blank colour comes from the SLD's strConcat: {notes}")

ONE_RULE = sld(rule("", polygon("#ffffff").replace(
    "</PolygonSymbolizer>",
    f'<Stroke>{css("stroke", "#333333")}</Stroke></PolygonSymbolizer>')))
white = {"version": 8, "layers": [{
    "id": "fill-0", "type": "fill", "paint": {"fill-color": "#ffffff"}}]}
styles.repair(white, {}, ONE_RULE)
check(white["layers"][0]["paint"].get("fill-outline-color") == "#333333",
      f"a white fill gets the SLD's outline: {white['layers'][0]['paint']}")

SIZES = sld(rule(equal_to("tipo", "a"), mark("#f00", 8))
            + rule(equal_to("tipo", "b"), mark("#0f0", 4)))
cli = {"version": 8, "layers": [{
    "id": "categorical-circle", "type": "circle",
    "paint": {"circle-color": ["match", ["get", "tipo"], "a", "#f00",
                               "b", "#0f0", "#cccccc"],
              "circle-radius": ["match", ["get", "tipo"], "a", 8.0,
                                "b", 4.0, 5.0]}}]}
styles.repair(cli, {"tipo": "VARCHAR"}, SIZES)
radius = cli["layers"][0]["paint"]["circle-radius"]
check(radius[:6] == ["match", ["get", "tipo"], "a", 4.0, "b", 2.0],
      f"a categorical point's radius is half its SLD Size: {radius}")
again = copy.deepcopy(cli)
check(styles.repair(again, {"tipo": "VARCHAR"}, SIZES) == []
      and again == cli, "a second repair changes nothing")

if errors:
    print("\n".join(f"error  {e}" for e in errors))
    raise SystemExit(1)
print("OK: stacked SLDs convert, and the CLI's styles repair once")
