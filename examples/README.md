# examples/

Demonstration notebooks for the USDM-RDF deliverables (`../usdm_v4.ttl`,
`../usdm_v4.context.jsonld`, `../usdm_v4.shapes.ttl`,
`../usdm_v4.shapes-ct.ttl`). Each notebook is self-contained — open in
JupyterLab, run all cells. All seven are pinned to the v0.5.0 baseline
(8,642 triples); the triple-count sanity check warns (does not fail) on
drift, so a future DDF-RA tag bump won't break the examples.

Since v0.4.0 every NCIt reference carries two IRI forms (EVS identifier and
OBO PURL — decision D4 in `../docs/iri-and-governance.md`). Tabular outputs
present them as paired `_evs` / `_obo` columns, one row per class/attribute;
scalar lookups filter to the EVS form, whose local name is the bare C-code.

## Notebooks

### `01_model_navigation.ipynb`

USDM v4 as a queryable data dictionary. SPARQL walks classes, properties,
cardinality (reconstructed from `owl:Restriction`), and the four polymorphic
`owl:unionOf` ranges. Joins to a flat `(class, attribute)` table with all
metadata columns including the binding annotations and the paired NCIt
anchor columns.

Output: `data_dictionary.csv` — 693 rows × 19 columns.

### `02_codelist_bindings.ipynb`

Forward inventory of the 57 declaring-class CT bindings, source-categorized
(`cdisc_library` / `sdtm_ct` / `protocol_ct` / `external`) by parsing the
`usdm:boundCodelistNote` text. Inheritance-aware reverse lookup: given a
codelist C-code, find every USDM concrete class carrying it via
`rdfs:subClassOf*`. Demo on `C66732` (Sex) returns `PopulationDefinition`
plus its concrete subclasses `StudyCohort` and `StudyDesignPopulation`.

Output: `reverse_codelist_index.csv` — 53 rows.

### `03_coverage_gap_analysis.ipynb`

Partitions every declared Code-typed property (range `Code` / `AliasCode` /
`ResponseCode`) into three buckets: `structured` (45) / `free_text` (12) /
`unbound` (10). Inheritance-aware effective coverage per concrete class.
Gap report shows the 7 concrete classes with at least one unbound Code-typed
property — all by USDM design, not a binding-layer oversight.

Output: `code_typed_coverage.csv` — 72 rows × 9 columns.

### `04_resolve_permitted_terms.ipynb`

Closes the loop from a USDM property's `usdm:boundCodelist` to the actual
permitted Code values, via NCI EVS. CDISC contributes its codelists to NCIt
as subsets, so the binding C-codes (`C99077`, `C188724`, `C174222`, …)
*are* NCIt subset IDs and resolve through one open API endpoint regardless
of which CDISC package contributes them. Demos on three properties drawn
from three different source categories (SDTM CT, CDISC Library plain form,
Protocol CT).

No CSV output (permitted-term tables are codelist-specific).

### `05_polymorphic_associations.ipynb`

Makes USDM v4's polymorphism queryable. SPARQL enumerates the four polymorphic
attributes (range = `owl:unionOf`), runs reverse range lookup — given a target
class, find every attribute that can hold it, direct or via union. Demos on
`Activity` (7 attributes: 5 direct + 2 via union) and `BiomedicalConcept` (4
attributes: 3 direct + 1 via union). Step 4 surfaces classes reachable from
object properties *only* via polymorphism — `ScheduledActivityInstance` in
v0.4.0.

Output: `polymorphic_reverse_index.csv` — 341 rows (330 direct + 11 via union),
80 distinct target classes.

### `06_query_instance_data.ipynb`

Multi-study SPARQL over instance data — the basics. Loads four real
protocols from `data4knowledge/usdm_data` (USDM Excel-to-JSON renderings,
pinned commit; a fifth file without a `usdmVersion` envelope is skipped by
the load gate) as named graphs in one Dataset. This works because the
instance context sets no `@base` (decision D5): document-scoped ids get
per-file base IRIs, so identical ids never collide and `GRAPH ?study`
doubles as provenance. Queries build up from one-row-per-study basics
(study code, brief title) through orientation (titles, design types,
phases) to a corpus census: which USDM classes real E2J outputs
instantiate, counts per study, decorated with `skos:definition` and the
paired NCIt anchors from the model graph — model and data share IRIs, so
the join needs no mapping table.

No CSV output.

### `07_validation_audit.ipynb`

The extended case: model, shapes, and instance data combined. Same corpus
as notebook 06, plus both SHACL layers, validated per study with pyshacl.
The validation reports are themselves RDF and load as named graphs
(`<study>#shacl-structural`, `<study>#shacl-ct`), so one SELECT decorates
every finding with the focus node's class (study graph), the violated
property's definition (model graph), and the expected cardinality
(structural shapes graph). A terminology closeup assembles actual code,
decode, permitted values (`sh:in`), and bound codelist from four graph
kinds in one query. Findings in this corpus: a systemic
empty-required-collection pattern across three studies, one dangling-ref
data error, and one codelist-drift specimen (C207646 vs C94108 on
`StudyTitle-type`).

Output: `validation_audit.csv` — 12 rows × 10 columns.

## Dependencies

- Notebooks 01–03, 05: `rdflib`, `pandas`. No network.
- Notebook 04: same plus `requests`. Calls `https://api-evsrest.nci.nih.gov/`
  — open API, no key or membership required.
- Notebook 06: `rdflib`, `pandas`. Network on first run only — fetches the
  study JSONs from the pinned `data4knowledge/usdm_data` commit into
  `../downloads/d4k/` (SHA-256 sidecar `.fetch_meta_examples.json`).
- Notebook 07: same plus `pyshacl`. Shares the notebook 06 downloads.

## Outputs

CSVs are tracked in git and regenerated on every notebook run. Diffs reflect
either source changes (`dataStructure.yml`, `USDM_CT.xlsx`) or generator
changes.

## What these notebooks do *not* show

- Inheritance walking is exercised in cases 2, 3, and 4 but the case 1 data
  dictionary is the as-declared view only — class shows its own attributes,
  not inherited ones.
- Free-text bindings (the 12 declaring-class bindings without a structured
  C-code) appear in inventories but cannot be resolved by case 4 — they
  point to external dictionaries (ISO 3166, MedDRA, SNOMEDCT, FHIR, …) with
  no single REST API.
- Alignment to CDISC Library RDF Administered Item IRIs is deferred (would
  replace the NCI EVS call in case 4 with a federated SPARQL query against
  Library RDF).
