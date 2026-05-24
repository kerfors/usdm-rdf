# Leveraging the 2015 PhUSE CT schema for v0.4 codelist-value binding

This is a scoping note, not a decision. It captures what is reusable from
the 2015 PhUSE *CDISC Standards in RDF Reference Guide* (Final 1.0,
2015-06-18) when scope is opened for codelist *value* binding — sheet 2
of `USDM_CT.xlsx`. Codelist value binding is currently out-of-scope per
`README.md` and `CLAUDE.md`; this document does not change that.

## What v0.3 does today

`usdm_v4.ttl` carries codelist-level anchors only. A `Code`-typed
property has `usdm:boundCodelist <ncit:Cxxxxx>` pointing at the codelist
IRI, plus `usdm:boundCodelistNote` carrying the verbatim `Has Value List`
cell text from sheet 1 of `USDM_CT.xlsx`. The codelist itself is not
instantiated and its permitted values are not present in the graph.
57 declaring-class bindings; 45 with a structured C-code; 12 free-text
references to external dictionaries (ISO 3166, ISO 639, MedDRA,
SNOMEDCT, FHIR, etc.) preserved verbatim.

## What v0.4 would add

For each codelist with a structured C-code, materialise the value
domain and its permitted values from sheet 2 of `USDM_CT.xlsx`, so
that the `usdm:boundCodelist` annotation dereferences to a real graph
rather than just naming an NCIt IRI.

## The 2015 guide as a pattern source

§3.2 of the guide defines the CT schema (`cts:`) as a thin predicate
layer on top of the meta-model schema (`mms:`). It adds no classes of
its own — the predicates reflect properties already used by the NCI EVS
RDF publication of CDISC CT. This matters: reusing `cts:` predicates
aligns the value graph with a real published artifact (the EVS CDISC CT
graph), not just with a 2015 paper.

### Class shape (from `mms:`)

A codelist is an `mms:EnumeratedValueDomain` (subclass of
`mms:ValueDomain`). Each permitted value is an `mms:PermissibleValue`.
The link from value to codelist is `mms:inValueDomain`. A codelist may
declare `mms:subsetOf` another enumerated value domain — the pattern
the guide uses for CDASH codelists as subsets of SDTM codelists.

### Predicates (from `cts:`)

On a permissible value, and on an enumerated value domain where
applicable:

| Property (Table 2 label)      | Carries                                                  |
|-------------------------------|----------------------------------------------------------|
| CDISC Definition              | Verbatim CDISC definition (NCI provenance noted)         |
| CDISC Submission Value        | String that flows into the dataset column                |
| CDISC Synonyms                | Applicable synonyms for the preferred term               |
| NCI Code                      | C-code as a literal property                             |
| NCI Preferred Term            | NCIt preferred term                                      |

On an enumerated value domain only:

| Property (Table 2 label) | Carries                                       |
|--------------------------|-----------------------------------------------|
| Codelist Name            | Descriptive codelist label                    |
| Is Extensible Codelist   | Whether terms may be added by sponsors        |

The exact local-name spelling of the predicate IRIs (`cts:cdiscSubmissionValue`,
`cts:nciCode`, etc.) is taken from the EVS publication, which is the
source of truth.

### NCIt anchoring — literal vs IRI

`cts:nciCode` carries the C-code as a literal on the permissible value.
This is distinct from `skos:exactMatch` to an `ncit:Cxxxxx` IRI. Both
are useful and they are not redundant: the literal supports SPARQL
without dereferencing; the IRI supports navigation. The EVS graph
carries both.

## Why reuse rather than mint `usdm:` equivalents

Minting `usdm:permittedValue`, `usdm:submissionValue`, `usdm:nciCode`
under the project namespace would give up alignment with the NCI EVS
RDF graph for no real ontological gain. The cost of importing `mms:`
just for the value-domain pattern is small —
`mms:EnumeratedValueDomain`, `mms:PermissibleValue`, `mms:ValueDomain`,
`mms:inValueDomain` are localised to CT and do not bleed into the
native-OWL rendering of the USDM classes themselves.

## The open architectural question

Two defensible approaches:

1. **Mint locally.** Instantiate each codelist and its permitted values
   inside `usdm_v4.ttl`. Self-contained; one file dereferences the whole
   model and its CT. Cost: the graph grows substantially, and CT updates
   require re-running the pipeline.

2. **Reference into EVS.** Reference `ncit:C66767` (or equivalent) as
   the `EnumeratedValueDomain` and let the value triples come from the
   EVS-published CDISC CT graph. Cleaner federation; smaller deliverable;
   CT updates inherited automatically. Cost: depends on whether the EVS
   graph IRIs match what the `usdm:boundCodelist` annotations point to,
   and whether those IRIs are reliably dereferenceable.

Settling this is the central v0.4 design decision. Both depend on the
shape of the EVS-published CDISC CT graph being verified — currently
not done, because CDISC Library RDF access is not available (see
project memory).

## What this document does not decide

Codelist-value binding remains out-of-scope until scope is explicitly
opened. The 12 free-text references to external dictionaries are
preserved verbatim in `usdm:boundCodelistNote` and are not in the
leverage path described here — they are not CDISC CT and the 2015 guide
does not cover them.

## Source

PhUSE CS Semantic Technology Working Group. *CDISC Standards in RDF
Reference Guide*. Version 1.0 Final. 2015-06-18. §3.1 Meta-Model Schema,
§3.2 CT Schema, §3.3 CDISC Schema.
