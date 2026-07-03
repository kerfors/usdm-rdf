# SHACL shapes design (v0.6.0)

Two deliverables, two conformance claims:

- `usdm_v4.shapes.ttl` — **structural layer**: class membership,
  cardinality, datatypes, ranges, closedness. Changes when the model
  changes (per DDF-RA release).
- `usdm_v4.shapes-ct.ttl` — **terminology layer**: permitted `Code`
  values for the DDF-native value sets. Changes when CDISC's value sets
  change. Consumers opt in separately.

## Structural layer: flatten, closed, standalone

Instance graphs produced via `usdm_v4.context.jsonld` type every node
with its concrete class only — no abstract ancestors, no
`rdfs:subClassOf` triples. The shapes therefore assume nothing a bare
instance graph doesn't provide: one `sh:NodeShape` per concrete class
(80; abstract classes have no direct instances by design and get no
shapes), carrying constraints for **all** attributes including
inherited ones, on their declaring-class property IRIs — the same
`Inherited From`-chain rule `20_generate_turtle.ipynb` and
`40_generate_context.ipynb` apply. Validation needs no ontology merge
and no inference; `30_validate.ipynb` runs pyshacl with
`inference="none"` to keep that claim honest.

Shapes are `sh:closed` with `rdf:type` ignored. The closed property
list is exactly what the context can produce: `{Class}-id` and
`{Class}-instanceType` are excluded because the context absorbs them
into `@id`/`@type`.

Cardinality maps mechanically (`1` → minCount 1 + maxCount 1; `0..1` →
maxCount 1; `1..*` → minCount 1; `0..*` → none; `0..2` → maxCount 2 —
the five forms in DDF-RA v4.0.0; any new form fails generation).
Ranges: concrete class → `sh:class`; abstract class → `sh:or` over
concrete descendants (13 declaring-level cases, 20 in the flattened
count); the 4 union ranges → `sh:or` over members, abstract members
expanded (`StudyRole.appliesToIds`: `StudyDesign` → its two concrete
designs). `Ref` attributes additionally get `sh:nodeKind sh:IRI`. A
fail-fast guard asserts redeclared attributes never diverge from their
declaring entry in `Cardinality`, `Type`, or `Relationship Type` —
none do in v4.0.0.

## Terminology layer: severity from published extensibility

Sheet 2 of `USDM_CT.xlsx` (`DDF valid value sets`) publishes 25 value
sets — 125 permitted Concept C-codes — each with a codelist C-code and
an extensibility flag. Each becomes one shape targeting the bound
property's values via `sh:targetObjectsOf`, constraining
`usdm:Code-code` with `sh:in`. Severity is read, not assumed:
**non-extensible → `sh:Violation`** (9), **extensible →
`sh:Warning`** (16) — a sponsor extension on an extensible codelist is
legitimate use flagged for review, not an error. Codelist C-codes are
cross-checked against the sheet-1 bindings; disagreement fails
generation.

## Source boundary

Everything derivable from the two pinned source files is used fully;
nothing new is fetched. Out, deliberately: the 20 bindings backed by
SDTM/Protocol Terminology codelists (their members live in the
quarterly NCI EVS CT publications — a third source with a decoupled
release cadence) and the 12 free-text external dictionary references
(ISO 3166, ISO 639, MedDRA, SNOMEDCT, etc.). Their values pass no
check — documented as out of scope, not as a pass.

## Evidence: CDISC Pilot findings

Against the pilot study (DDF-RA v4.0.0): the structural layer
**conforms** — real published instance data passes all 80 closed
shapes, mutually validating data, context, and shapes. The terminology
layer reports 14 findings: 3 Violations — placeholder codes
`C99905x1/x2/x3` on non-extensible `StudyTitle-type` — and 11
Warnings, including dummy codes (`C12345`, `C99903x1`, …) and two real
NCIt codes used outside their published lists (`C70793` Clinical Study
Sponsor on `Organization-type`; `C132352` Sponsor Approval Date on
`GovernanceDate-type`). The severity split behaving differently on
placeholder codes versus plausible extensions is the design working as
intended.
