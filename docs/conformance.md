# Portolan Conformance

Conformance means passing [rashid](https://github.com/portolan-sdi/rashid),
not claiming to conform, so it runs in CI:

```bash
python3 tests/test_conformance.py
```

That gate fails on any error-severity finding whose rule is not listed below.
The list starts empty and it must never grow without a row here. A known
deviation with an issue number is a debt someone can pay off. A silently
widened allow-list is a false claim about what this catalog conforms to.

## Accepted deviations

None. The catalog declares Portolan v0.3.0, and rashid 0.4.0 finds 0 errors
with no disabled rule and no severity override.

## Open warnings

Warnings do not fail the gate, and they need no entry in `ACCEPTED`. They are
listed here so that each one has a stated reason.

| Rule | Where | Reason |
|---|---|---|
| PTL-DAT-020 | every vector collection | The source publishes no column descriptions. GeoNode's `attribute_set` returns a null `description` for every attribute. The spec forbids placeholder text (PORTO-FMT-079), so the columns stay undescribed and each collection README says why. |
| PTL-CAT-001 | `ambiente-y-agro/` | This group holds 30 collections, and the rule warns above 20. The grouping follows the publisher's own themes, and splitting it would invent a hierarchy the source does not have. |

## Info findings

Info findings need no action. Two appear on every run:

| Rule | Where | Reason |
|---|---|---|
| PTL-PRO-002 | every vector collection | The rule asks for a `canonical` link when the upstream publishes its own STAC catalog. GeoNode does not. Its API root (`/api/v2/`) lists no STAC resource, and `/stac`, `/api/stac` and `/api/v2/stac` return 404. |
| PTL-DAT-006 | current and archived files under 200 rows | rashid needs 200 rows to judge spatial ordering, so it reports that it could not. `tools/extract.py` sorts every new extract on a Hilbert curve, whatever its size. |

## A separate matter: stac-check cannot read the Portolan schema

This is not a rashid deviation and does not belong in the table above. It is a
tool defect in the advisory gate, recorded here because it is otherwise
mystifying to anyone reading CI output.

`tests/test_stac_valid.py` runs stac-check, which delegates schema validation to
stac-validator. Validating any object that declares the Portolan profile
extension raises:

```
'list' object has no attribute 'get'
[Schema: https://schemas.portolan-sdi.org/portolan/v0.3.0/schema.json]
```

**Evidence it is not this catalog's fault.** The published schema is well formed
— no non-dict entry appears in any `oneOf`, `allOf`, or `anyOf`. More decisively,
the Portolan spec's own reference catalog, which exists to be the conformance
exemplar, fails with exactly the same message on the same schema. No change to
this catalog can avoid it.

**How it is handled.** `test_stac_valid.py` treats this one message as known,
and only when the failing schema is the Portolan one. Every other stac-check
error still fails the build. The count of skipped objects is printed on every
run rather than hidden, so the exception cannot quietly outlive the bug.

**Tracking**: [portolan-spec#157](https://github.com/portolan-sdi/portolan-spec/issues/157).

**Remove this when the upstream fix lands.** Until then rashid is the gate, which
is the standing rule anyway: where stac-check and rashid disagree, rashid wins.
The clearest instance is stac-check recommending a `rel: self` link, which
`PTL-LNK-005` forbids, because a static catalog that hardcodes its own location
cannot be mirrored or moved.

<!--
When you accept one, add a row and a section explaining it, like this:

| Rule | Where | Why accepted | Tracking |
|---|---|---|---|
| PTL-VIZ-001 | all thumbnails | WebP is not yet permitted; the size saving is 4x | portolan-spec#121 |

Then add the rule id to ACCEPTED in tests/test_conformance.py. Both, or
neither.
-->
