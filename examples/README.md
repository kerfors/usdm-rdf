# examples/

Demonstration notebooks for the v0.3 USDM-RDF Turtle file (`../usdm_v4.ttl`).
Each notebook is self-contained — open in JupyterLab, run all cells. All five
are pinned to v0.3 binding shape; the triple-count sanity check warns (does
not fail) on drift, so a future DDF-RA tag bump won't break the examples.

## Notebooks

### `01_model_navigation.ipynb`

USDM v4 as a queryable data dictionary. SPARQL walks classes, properties,
cardinality (reconstructed from `owl:Restriction`), and the four polymorphic
`owl:unionOf` ranges. Joins to a flat `(class, attribute)` table with all
v0.3 metadata columns including the binding annotations.

Output: `data_dictionary.csv` — 693 rows × 16 columns.

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
property — all by USDM design, not v0.3 oversight.

Output: `code_typed_coverage.csv` — 72 rows.

### `04_resolve_permitted_terms.ipynb`

Closes the loop from a USDM property's `usdm:boundCodelist` to the actual
permitted Code values, via NCI EVS. CDISC contributes its codelists to NCIt
as subsets, so the v0.3 binding C-codes (`C99077`, `C188724`, `C174222`, …)
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
v0.3.

Output: `polymorphic_reverse_index.csv` — 341 rows (330 direct + 11 via union),
80 distinct target classes.

## Dependencies

- Notebooks 01–03, 05: `rdflib`, `pandas`. No network.
- Notebook 04: same plus `requests`. Calls `https://api-evsrest.nci.nih.gov/`
  — open API, no key or membership required.

## Outputs

CSVs are tracked in git and regenerated on every notebook run. Diffs reflect
either source changes (`dataStructure.yml`, `USDM_CT.xlsx`) or v0.3 generator
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
