# Known gaps and v0 scope exclusions

## v0 exclusions (deliberate, documented in README.md)

- SULO or other upper-ontology alignment.
- `USDM_CT.xlsx` enumerated codelist value binding (only the class- and
  attribute-level C-Codes already in the YAML are emitted).
- Alignment to the existing CDISC Library RDF (Administered Item vocabulary).
- SHACL shapes for instance validation.
- Multiple format publication. Turtle only — no RDF/XML, JSON-LD, or
  NTriples.

## Triple-count residual vs prototype baseline (DDF-RA v4.0.0)

Prototype baseline: 8,215 triples.
Current generator output: 8,069 triples (delta: −146).

All structural counts match exactly:

- 86 named `owl:Class` IRIs (84 NCIt-anchored + 2 Extension classes by design)
- 693 properties (datatype + object combined)
- 312 properties NCIt-anchored
- 80 Concrete + 6 Abstract classes
- 630 Value + 63 Ref properties
- 0 NCIt cross-check mismatches (every source `NCI C-Code` resolves to a
  matching `skos:exactMatch` triple in the graph)

The −146 residual is attributable to differences between this generator and
the unseen prototype that produced the 8,215 number — likely candidates:
language tags on labels, alternate restriction encoding, or additional
ontology header triples we don't emit. We chose to keep the prototype
number as the baseline so source drift remains visible in
`reports/validation.csv` on every run.

## Standalone definitions

`skos:definition` is emitted whenever a source `Definition` field is present,
whether or not the entity is also `NCI C-Code`-anchored. This adds 126
property-level definitions on attributes that have a `Definition` but no
`NCI C-Code` in DDF-RA v4.0.0. Decision: preserve, don't collapse.

## `usdm:` annotation namespace

Four annotation properties: `usdm:modifier`, `usdm:relationshipType`,
`usdm:modelName`, `usdm:modelRepresentation`. The fourth was added when the
YAML audit revealed a `Model Representation` field on 504 of 693
non-inherited attributes that was not in the original mapping table.

## Union types in `rdfs:range`

Four attributes in DDF-RA v4.0.0 have multi-element `Type` lists, mapped to
`owl:unionOf` blank nodes:

- `Condition.contextIds` → 2-class union
- `Condition.appliesToIds` → 5-class union
- `ProductOrganizationRole.appliesToIds` → 2-class union
- `StudyRole.appliesToIds` → 2-class union

These aren't just an emission detail. Two of them —
`Condition.appliesToIds` and `StudyRole.appliesToIds` — are polymorphic
associations: reference attributes whose target class varies by usage. UML
expresses this awkwardly (or not at all); `owl:unionOf` captures the
structure honestly, so the RDF rendering exposes a semantic feature of
USDM v4 that the source UML hides.

The `owl:Class` triple count over the whole graph is 90 (86 named + 4 union
blank nodes). Validation queries filter on `isIRI(?c)` to count only named
classes.
