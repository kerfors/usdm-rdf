# SHACL shapes design (v0.7.0)

Two deliverables, two conformance claims:

- `usdm_v4.shapes.ttl` — **structural layer**: class membership,
  cardinality, datatypes, ranges, closedness. Changes when the model
  changes (per DDF-RA release).
- `usdm_v4.shapes-ct.ttl` — **terminology layer**: one shape per
  codelist binding USDM states; permitted `Code` values for the
  DDF-native value sets, deactivated shapes for the rest. Changes when
  CDISC's bindings or value sets change. Consumers opt in separately.

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

## Terminology coverage: 25 checked, 20 declared and deactivated

Sheet 1 of `USDM_CT.xlsx` binds 45 declaring-class attributes to a
codelist C-code (67 `Has Value List` rows; 45 distinct properties after
collapsing inherited rows to the declaring class; 12 further properties
reference free-text external dictionaries and carry no C-code). The
ontology publishes every one of the 45 as `usdm:boundCodelist` on the
property IRI. Only 25 of them have a value set in sheet 2, so only 25
carry a `sh:in` check. The other 20 — 19 SDTM Terminology codelists
(`StudyEpoch.type` C99079, `InterventionalStudyDesign.model` C99076,
`StudyDesign.studyType` C99077, `StudyDesign.studyPhase` C66737,
`InterventionalStudyDesign.blindingSchema` C66735,
`PopulationDefinition.plannedSex` C66732, `Quantity.unit` C71620,
`Administration.route` C66729, `EligibilityCriterion.category` C66797,
…) and `StudyArm.type` C174222 (Protocol Terminology) — have their
members in NCI EVS, not in the USDM deliverables.

Since v0.7.0 each of those 20 is a `sh:NodeShape` with
`sh:targetObjectsOf` the bound property, `sh:deactivated true`, no
constraint, and the EVS subset URL as `rdfs:seeAlso` (the 25 active
shapes carry the same `rdfs:seeAlso`). Validators skip deactivated
shapes, so every `conforms` result is unchanged from v0.6.0. What
changes is that "not checked here" is now a positive assertion in the
shapes graph rather than an inference from a shape's absence:

    SELECT ?property ?codelist WHERE {
      ?shape a sh:NodeShape ; sh:deactivated true ;
             sh:targetObjectsOf ?property ; rdfs:seeAlso ?codelist }

Extensibility is published for the 25 (as severity) and not for the 20
— sheet 2 does not list them, and the NCI EVS package is not a source
of this repo. `terminology conforms=True` therefore reads: no finding
among the 25 checked codelists. `60_validate_study.ipynb` prints that
scope on the result line and lists the coded values in the document
that fall under a deactivated shape, so a consumer sees what was not
looked at rather than only what passed. On the CDISC Pilot that table
holds 88 coded values on 16 of the 20 deactivated bindings — 31
`EligibilityCriterion-category`, 16 `Encounter-contactModes`, 5
`StudyEpoch-type`, … — next to the 14 findings on the checked side.

## Source boundary

Everything derivable from the two pinned source files is used fully;
nothing new is fetched. Out, deliberately: the members of the 20
codelists backed by SDTM/Protocol Terminology (they live in the
quarterly NCI EVS CT publications — a third source with a decoupled
release cadence; the bindings themselves are in, as deactivated shapes)
and the 12 free-text external dictionary references (ISO 3166, ISO 639,
MedDRA, SNOMEDCT, etc.). Their values pass no check — documented as out
of scope, not as a pass.

The terminology layer has one source of truth: sheet 2 of
`USDM_CT.xlsx` at the pinned tag. The NCI EVS publication of the same
codelists is a second source, and the two can disagree. Known case:
for `StudyTitle.type`, EVS subset `C207419` lists `C207646` (Study
Acronym) where sheet 2 lists `C94108` (Study Protocol Version
Acronym). The codelist is non-extensible, so a document built against
EVS gets a Violation here (see `examples/validation_audit.csv`). The
shapes encode the xlsx side because that is the pinned source; they do
not arbitrate. Such a Violation is a finding about the two CDISC
publications, reported as one, and the divergence itself is a
governance item for CDISC, not a defect in the document.

## What structural conformance does not say

The instance graph is produced by the JSON-LD context, and the context
maps only the serialization keys the model declares, scoped by the
object's `instanceType`. A key the model does not declare, or a declared
key placed on a class that does not carry it, yields no triple - that is
JSON-LD 1.1 behaviour with no `@vocab`, not a choice made here. The closed
structural shapes therefore never see such keys, and `conforms=True` is a
statement about the graph, not about the JSON. The context-conformance
check (step 1 of `60_validate_study.ipynb`, "unmapped keys") is the only
detector for this class of defect, which is why it runs before lifting.
Specimen: `previousId`/`nextId` written on `StudyArm` by a generator that
assumed the epoch/element chaining pattern generalises - real attribute
names, absent from that class - pass both SHACL layers and are caught
only by the context check.

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

A second run (2026-09-03) used five USDM v4 documents from an independent
generator that had never seen the shapes - study shells and SoA-only
documents for two protocols, 37 to 687 objects each, 6,620 triples in
total, one author. All five pass both SHACL layers with zero findings,
and all five trip the context check on the same attribute pair (the
`StudyArm` specimen above). Every finding on those documents was a real
defect in the input; the shapes produced no false positives. The
documents themselves are not committed - four derive from protocols under
copyright or marked confidential - so the claim rests on this record.
