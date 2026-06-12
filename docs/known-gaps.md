# Known gaps and v0.1 scope exclusions

## v0.1 exclusions (deliberate, documented in README.md)

Status as of v0.4.0: multiple-format publication shipped in v0.3 (five
formats via w3id content negotiation). The remaining four items are
still out of scope.

Closed in v0.4.0 (was parked, not on the original exclusion list): the
NCIt anchor prefix question. Resolution is dual anchoring (decision D4
in iri-and-governance.md) rather than a switch — every NCIt reference
carries both the EVS identifier and the resolvable OBO PURL.

Deferred from the v0.4.0 release: re-running the `examples/` notebooks.
The forward binding inventory (notebook 02) returns two rows per bound
property under dual anchoring, and the committed example CSVs predate
it. The notebooks are pinned warn-not-fail on drift, so nothing breaks;
refresh is a follow-up task.

- SULO or other upper-ontology alignment.
- `USDM_CT.xlsx` enumerated codelist *value* binding (sheet 2 of USDM_CT —
  permitted Code values per codelist). Codelist-level anchoring is in v0.1;
  per-value binding is out.
- Alignment to the existing CDISC Library RDF (Administered Item vocabulary).
- SHACL shapes for instance validation.
- Multiple format publication. Turtle only — no RDF/XML, JSON-LD, or
  NTriples.

## v0.1 — codelist binding annotations

Two new annotation properties bind `Code`-typed property IRIs to their
permitted codelist:

- `usdm:boundCodelist` — `owl:AnnotationProperty`, NCIt IRI value. Anchors the
  codelist by C-code (consistent with `skos:exactMatch` style).
- `usdm:boundCodelistNote` — `owl:AnnotationProperty`, string literal value.
  Lossless preservation of the raw `Has Value List` cell text from
  `USDM_CT.xlsx`, including the free-text references that have no
  extractable C-code.

Source-of-truth split: model structure (classes, properties, cardinality,
hierarchy) comes from `dataStructure.yml`; codelist bindings come from
`USDM_CT.xlsx`. Both files co-pinned at the same DDF-RA release tag.

### Counts (DDF-RA v4.0.0)

USDM_CT lists 67 Y-rows (rows where `Has Value List` starts with `Y`):

- 53 with structured C-code (`Y (Cxxxxxx)`, `Y (SDTM Terminology Codelist Cxxxxxx)`,
  or `Y (Protocol Terminology Codelist Cxxxxxx)`)
- 14 free-text references to external dictionaries (ISO 3166, ISO 639,
  MedDRA, SNOMEDCT, FHIR, etc.)

Of the 67, **10 are inherited duplicates** of a parent's binding (e.g.
`InterventionalStudyDesign.studyType` is an inherited row that duplicates
`StudyDesign.studyType`). v0.1 emits one annotation pair per *declaring*
property, mirroring how `dataStructure.yml` declares attributes. The graph
therefore holds:

- **57** `usdm:boundCodelistNote` triples (declaring class only)
- **45** `usdm:boundCodelist` triples (subset with structured C-code)
- 12 free-text-only bindings (45 + 12 = 57)

### Free-text bindings preserved verbatim

The 12 declaring-class free-text bindings are preserved as
`usdm:boundCodelistNote` strings only (no `usdm:boundCodelist`). They
cover: ISO 3166 country codes, ISO 639 language codes, MedDRA, SNOMEDCT,
WHODrug, ATC, UNII, MED-RT, CPT, NCIt, ICD-class dictionaries, and a
FHIR value set. These are candidates for future external-vocabulary
alignment when CDISC Library RDF alignment lands.

## Triple-count history (DDF-RA v4.0.0)

| Version  | Triples | Delta  | Notes                                                                |
|----------|---------|--------|----------------------------------------------------------------------|
| Prototype baseline | 8,215 | —      | Earlier generator we cannot fully reconstruct.                       |
| v0       | 8,069   | −146   | Mechanical YAML → Turtle.                                            |
| v0.1     | 8,173   | +104 vs v0 (−42 vs prototype) | Adds 45 boundCodelist + 57 boundCodelistNote + 2 annotation property declarations. |
| v0.2     | 8,173   | 0      | w3id namespace adopted (hash semantics); structural counts unchanged. |
| v0.3     | 8,184   | +11 vs v0.2 | Slash IRI semantics (breaking) + ontology-header metadata (title, abstract, description, license, creator, citation, created, modified, vann namespace prefix/URI, widoco:introduction). |
| v0.3.1   | 8,200   | +16 vs v0.3 | owl:versionIRI + 15 owl:AnnotationProperty declarations for dcterms/vann/skos/widoco predicates (decisions D1–D3; header fix — created reverted to 2026-04-27). |
| v0.4.0   | 8,641   | +441 vs v0.3.1 | Dual NCIt anchoring (decision D4): OBO PURL twin on every NCIt reference — 396 skos:exactMatch + 45 usdm:boundCodelist. EVS host found NXDOMAIN 2026-06-12; EVS form kept as identifier (NCI Thesaurus 26.05d still declares it). |

All structural counts match exactly across v0/v0.1 (the new layer is purely
additive on property IRIs):

- 86 named `owl:Class` IRIs (84 NCIt-anchored + 2 Extension classes by design)
- 693 properties (datatype + object combined)
- 312 properties NCIt-anchored
- 80 Concrete + 6 Abstract classes
- 630 Value + 63 Ref properties
- 0 NCIt cross-check mismatches (every source `NCI C-Code` resolves to a
  matching `skos:exactMatch` triple in the graph)
- 0 binding cross-check mismatches (every non-inherited Y-row in `USDM_CT.xlsx`
  resolves to the expected `usdm:boundCodelist` and `usdm:boundCodelistNote`
  triples)

The remaining −42 residual vs the prototype baseline is attributable to
differences between this generator and the unseen prototype that produced
the 8,215 number — likely candidates: language tags on labels, alternate
restriction encoding, or additional ontology header triples we don't emit.
The prototype number is retained in this table as historical context; the
operational baseline used by `30_validate.ipynb` is 8,200 (v0.3.1).

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
