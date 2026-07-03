# IRI scheme and governance

This document records the design decisions behind the `usdm-rdf` IRI
scheme and the planned governance handoff to CDISC. It is the canonical
place for the rationale; `README.md` and `CLAUDE.md` cross-reference
here.

## Ontology IRI

`https://w3id.org/cdisc/usdm/v4/` — adopted in v0.3 (slash semantics).

The previous v0.2 namespace `https://w3id.org/cdisc/usdm/v4#` (hash
semantics) is superseded. The shape change is documented in
[v0.2-to-v0.3-migration.md](v0.2-to-v0.3-migration.md). The prior
hash-semantics rationale is preserved verbatim in the appendix below.

### Why w3id

w3id is a redirect service, not a host. Registering an IRI under
`w3id.org/cdisc/usdm/v4` commits to a stable namespace without
committing to a permanent home. If CDISC takes over governance, transfer
is a single PR against the w3id `.htaccess` entry: the redirect target
changes; no minted IRI moves.

### Why slash semantics (`/`) instead of hash (`#`)

Slash semantics gives every minted IRI its own server-side
dereferenceable form. From a deployment standpoint this means w3id
can redirect a class IRI like `…/v4/Activity` to its own HTML anchor
(`index.html#Activity`) and a property IRI like `…/v4/Activity-name` to
the property anchor (`index.html#Activity-name`) — per-IRI dereference
at the redirect layer, as in schema.org and PROV-O. (Per-class HTML
*pages* would be a further refinement; the deployed rendering is a
single WIDOCO page with per-entity anchors.) Hash semantics
forces every IRI to share a single document, which works for raw Turtle
but fails for per-class HTML rendering: a single rendered page would
have to host all 86 classes and 693 properties, and the renderer's
anchor-slug derivation does not align with the IRI fragment in the
general case.

The trade-off is more complex `.htaccess` rewrite rules. Slash
semantics needs at least three rules (class IRI to HTML, property IRI
to anchored HTML, namespace and Turtle requests to the whole TTL)
where hash semantics needed one. The redirect complexity is bounded;
the per-IRI dereferencing benefit is recurrent.

### What dereferencing returns — whole-graph by design

Slash semantics enables per-IRI dereferencing at the redirect layer.
The redirect *target* is a separate question: per-IRI requests can
return either a concept-scoped slice of the graph (Wikidata/DBpedia
pattern) or the whole ontology document (FOAF/schema.org/PROV-O
pattern). This repo serves the whole ontology, deliberately.

USDM v4 is a vocabulary ontology — 86 classes and 693 properties,
totalling roughly 370 KB of Turtle. It sits in the FOAF/schema.org/
PROV-O/Dublin Core/SKOS size and shape class: small, stable,
schema-shaped. Consumers reasoning over the vocabulary want the whole
graph; cache-once-then-everything is the appropriate access pattern.
Concept-scoped slicing is the right answer when the graph is too
large to ship whole (Wikidata, DBpedia, NCIt-as-thesaurus with
~190k concepts) — that pressure does not apply at this scale.

Per-IRI HTML, on the other hand, *is* per-resource: WIDOCO renders one
documentation page with one block per class and per property, and the
slash IRIs anchor to those blocks with fragments. That is the right pattern for human
consumption, where a single 370 KB document with 779 entities is not
navigable. The asymmetry is intentional: HTML serves humans one
entity at a time, RDF serves machines the whole vocabulary at once.

The slice-spec contract a slicing resolver would require — what
triples scope to a class IRI, a property IRI, the ontology IRI — is
therefore not written, and v0.3's resolver is complete as shipped,
not partial.

### Why per-version path (`/v4/`)

USDM v3 and v4 are not the same vocabulary. Encoding the major version
in the path means a future v5 can mint its own namespace without
breaking v4 consumers. Minor versions of USDM v4 (e.g. v4.x.y) continue
to share the namespace `…/cdisc/usdm/v4/`; the per-tag content is
recorded in `owl:versionInfo` on the ontology resource and the source
SHA-256 in the fetch metadata sidecars (`downloads/.fetch_meta.json`,
`downloads/.fetch_meta_ct.json`).

### Version identity (v0.3.1, decisions D1–D3)

Three conventions adopted in v0.3.1, recorded here because the
generator comments reference them:

- **D1 — `dcterms:created` is fixed at 2026-04-27** (first publication,
  v0.1.0) and never advances. It dates the ontology resource, not the
  release; `dcterms:modified` tracks the release date. Per-release
  identity lives in `owl:versionIRI`/`owl:versionInfo`. Known cosmetic
  mismatch: WIDOCO labels `dcterms:created` "Release date" in the HTML
  rendering.
- **D2 — the canonical Turtle is a superset of the WIDOCO render.**
  Every non-built-in annotation predicate the ontology uses (dcterms,
  vann, skos, widoco) is declared `owl:AnnotationProperty` in the
  generator, so derived serializations add no declarations the
  canonical graph lacks. This is also OWL 2 DL hygiene.
- **D3 — `owl:versionIRI` is bare-numeric in-namespace:**
  `https://w3id.org/cdisc/usdm/v4/0.3.1`. A leading digit cannot
  collide with entity IRIs (classes are CamelCase, properties
  `{ClassName}-{attributeName}` — both start uppercase). One generic
  w3id rewrite rule (`^([0-9]+\.[0-9]+\.[0-9]+)$` → the tag-pinned raw
  Turtle) makes every versionIRI dereference to its own release with
  no per-release w3id PR. Version-pinned dereference is therefore a
  standing capability, including for already-released versions.

### NCIt anchoring (v0.4.0, decision D4)

Every NCIt reference in the graph — 396 `skos:exactMatch` (84 classes,
312 properties) and 45 `usdm:boundCodelist` — carries exactly two
IRIs for the same concept:

- the EVS identifier, `http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#Cxxxxx`
- the OBO PURL, `http://purl.obolibrary.org/obo/NCIT_Cxxxxx`

One rule, no exceptions: an NCIt reference is never emitted in one
form without the other. The generator enforces this structurally; the
validation notebook cross-checks both forms; the WIDOCO post-processor
fails on any entity where the pair is malformed.

Evidence behind the decision (observed 2026-06-12):

- `ncicb.nci.nih.gov` is NXDOMAIN — the EVS namespace host no longer
  exists in DNS.
- NCI Thesaurus 26.05d (dated 2026-05-26, fetched from the official
  EVS download) still declares that namespace as its own — so the EVS
  form remains the correct *identifier*, published by the authority
  itself. Dropping it would break identity joins with NCI's own OWL
  and with CDISC Library RDF usage.
- The OBO PURL form resolves (HTTP 303 → Ontobee, 200) — so it is the
  correct *locator*.

The dual anchor keeps both roles: EVS for identity, OBO PURL for
dereference. HTML rendering hyperlinks the PURL and preserves the EVS
IRI as a tooltip. `usdm:boundCodelist` is consequently multi-valued
(two IRIs per bound property) from v0.4.0 — consumers joining on a
single value should filter by namespace prefix.

### Concept lifecycle across versions (position recorded 2026-07-02, mechanism parked)

The version identity story above covers rendering releases: every
release resolves immutably via its `owl:versionIRI`, so a reference
can be pinned and never drifts. It does not answer a harder question,
raised publicly in response to the announcement article: what happens
to a minted IRI when the underlying USDM concept changes meaning, is
deprecated, is split into multiple concepts, or disappears in a later
model version?

The question decomposes into three layers, recorded here so the
eventual mechanism is designed rather than improvised:

- **Detection is mechanical.** On a DDF-RA tag bump, diffing
  `dataStructure.yml` across tags surfaces added, removed, and
  re-coded classes and attributes. This extends the existing
  convention of documenting baseline deltas in `docs/` on every tag
  bump. Not built: only one source tag (v4.0.0) exists, so there is
  nothing to diff against yet.
- **Annotation is mechanical, given a decision.** The generator could
  emit `owl:deprecated true` plus a replacement link (e.g.
  `dcterms:isReplacedBy`, one-to-many for splits) as mechanically as
  it emits everything else — but only from an authoritative decision
  source. No such source exists in DDF-RA today, and this repo will
  not infer lifecycle events from a diff. A removal and a rename look
  identical in a diff; only a human assertion distinguishes them.
- **The assertion is governance.** Someone must say, out loud and on
  the record: this concept is gone, replaced by that one; this concept
  split into those two. That is a decision about what CDISC's names
  mean over time, and the natural asserting body is the USDM
  Governance Group. This is part of what the governance handoff
  (below) offers to transfer.

The per-version path (`/v4/`) bounds the problem but does not solve
it: a future USDM v5 mints its own namespace, so v4 IRIs never break —
but cross-version continuity links (which v5 concept continues this
v4 concept?) are the same governance question in namespace form.

Nothing in this section is implemented. It is the design position the
repo will follow when a second source tag or a UGG lifecycle decision
makes it actual.

### JSON-LD instance context (v0.5.0, decision D5)

`usdm_v4.context.jsonld` is a JSON-LD 1.1 context generated from the
same `dataStructure.yml` as the ontology. Applied to USDM API instance
JSON (the wire format exchanged by DDF-compliant systems), it yields
an RDF graph whose predicates and types are exactly the ontology's
IRIs.

- **`id` → `@id`, `instanceType` → `@type`.** Every typed object in
  published USDM instances carries both (verified: 1,953 of 1,953 in
  the DDF-RA v4.0.0 CDISC Pilot example). Class names are context
  terms resolving to `usdm:{ClassName}`.
- **Type-scoped contexts (JSON-LD 1.1) reconcile flat instance keys
  with class-scoped property IRIs.** Each class term embeds a context
  mapping each serialization key to
  `usdm:{DeclaringClass}-{attributeName}`, following the YAML
  `Inherited From` chain — the same declaring-class rule
  `20_generate_turtle.ipynb` applies.
- **`Relationship Type: Ref` attributes coerce to `"@type": "@id"`**,
  so id-string cross-references become graph links. In the pilot
  example all 1,257 links resolve to typed nodes, 0 dangling.
- **No `@base` in the published context.** `id` values are
  document-scoped; they expand relative to the consuming document's
  location. A shared context must not fix a base.
- **Consequence:** the `{Class}-id` and `{Class}-instanceType`
  property IRIs (148 of 693) never appear in context-derived instance
  graphs — node identity and `rdf:type` carry that information.

### SHACL shape IRIs (v0.6.0, decision D6)

- Structural shapes: `usdm:{ClassName}-shape`; terminology shapes:
  `usdm:{DeclaringClass}-{attributeName}-ct-shape`. Same namespace as
  the ontology — collision-free because no attribute is named `shape`
  and attribute names contain no hyphens (verified at generation).
- Shapes graph IRIs: `https://w3id.org/cdisc/usdm/v4/shapes` and
  `https://w3id.org/cdisc/usdm/v4/shapes-ct`, in-namespace paths (no
  class bears those lowercase names). `owl:versionInfo` tracks the
  repo release.
- Serving the shapes files under w3id follows the `context.jsonld`
  fixed-path pattern at the next re-pin.
- Design rationale (flatten, closed, standalone, severity from
  extensibility, source boundary) in `docs/shacl-design.md`.

## Property naming

Class-scoped: `{ClassName}-{attributeName}`, hyphen-separated.

### Why class-scoped

Attribute-level NCI C-Codes in DDF-RA v4.0.0 differ per declaring
class: e.g. `Activity-name` and `StudyDesign-name` map to different
`skos:exactMatch` targets. Collapsing across classes would erase that
information.

### Why hyphen as separator

Hyphen is URL-clean (no encoding), unambiguous in human reading, and
matches common W3C ontology practice. Dot reads as path or property
traversal in some tools. Underscore is fine but less common in property
IRIs.

### Caveat — un-validated against CDISC Library RDF

CDISC Library RDF endpoints sit behind CDISC-membership-tier API
access, which the maintainer does not have. The hyphen separator was
chosen on URL/practice grounds; whether it aligns with the property
naming convention used in CDISC Library RDF (Administered Item
vocabulary, etc.) has not been verified.

If a future review finds divergence, the response will be a deliberate
re-emit under a parallel namespace or an explicit deprecation, not a
silent rebase. Minted IRIs in `https://w3id.org/cdisc/usdm/v4/…` are
treated as stable from v0.3 forward.

## Governance handoff

The transfer mechanism is the redirect, not the artifact. At any
point, CDISC can take over by:

1. Hosting `usdm_v4.ttl` (and any HTML rendering, shapes graph, etc.)
   under their own infrastructure.
2. Submitting a w3id PR that changes the redirect target.

No minted IRI changes. No consumer needs to refetch.

This handoff is offered explicitly, not implicitly. The venue for
raising it is the **USDM Governance Group (UGG)**, the CDISC body that
provides oversight, decisionmaking, and strategic direction for USDM.
Introductory contact is via the DDF feedback form at
<https://www.cdisc.org/ddf> (categories *Suggestions for improvements
to USDM* or *Model extensions*); UGG membership itself is by annual
nomination. The DDF-RA GitHub repo is for technical feedback on the
published artefacts (UML, CT, API, IG, Conformance Rules) and is not
the governance venue.

## Project annotation namespace

`usdm:` covers six annotation properties, declared in the ontology
header:

- `usdm:modifier` — Concrete vs Abstract on classes
- `usdm:relationshipType` — Value vs Ref on attributes
- `usdm:modelName` — `Model Name` field from source
- `usdm:modelRepresentation` — `Model Representation` field from source
- `usdm:boundCodelist` — NCIt IRI for the codelist that bounds a
  Code-typed property
- `usdm:boundCodelistNote` — raw `Has Value List` cell text from
  `USDM_CT.xlsx` (lossless, including free-text references that have no
  extractable C-code)

## Appendix — v0.2 (superseded) hash-semantics rationale

The v0.2 namespace was `https://w3id.org/cdisc/usdm/v4#`. The
rationale below is preserved verbatim from the v0.2 documentation for
audit purposes. It was superseded in v0.3 by the slash-semantics
section above; the trigger was a pyLODE rendering spike that revealed
hash + single-page HTML + camelCased anchor slugs broke per-IRI
fragment resolution.

> Hash semantics keeps every minted IRI a fragment of one document. From
> a deployment standpoint this means the w3id `.htaccess` redirects a
> single resource, and the served Turtle (or any future HTML rendering)
> carries every class and property under one URL. Slash semantics would
> require either per-IRI redirect rules or a `RewriteRule` translating
> each sub-path to the hosting target plus a fragment — workable but
> fiddly, and locks in more `.htaccess` complexity at registration time.
>
> The trade-off is per-class URLs that are slightly less aesthetic
> (`…/v4#Activity` vs `…/v4/Activity`). Simplification at the redirect
> layer was judged the larger win.
