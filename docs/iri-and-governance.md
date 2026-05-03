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
can redirect a class IRI like `…/v4/Activity` to a per-class HTML page
(`Activity.html`) and a property IRI like `…/v4/Activity-name` to the
same page anchored at the property fragment (`Activity.html#Activity-name`)
— matching the pattern used by schema.org and PROV-O. Hash semantics
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

### Why per-version path (`/v4/`)

USDM v3 and v4 are not the same vocabulary. Encoding the major version
in the path means a future v5 can mint its own namespace without
breaking v4 consumers. Minor versions of USDM v4 (e.g. v4.x.y) continue
to share the namespace `…/cdisc/usdm/v4/`; the per-tag content is
recorded in `owl:versionInfo` on the ontology resource and the source
SHA-256 in the fetch metadata sidecars (`downloads/.fetch_meta.json`,
`downloads/.fetch_meta_ct.json`).

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

This handoff is offered explicitly, not implicitly. The DDF-RA
discussion forum on GitHub is the venue for raising it once v0.2.0 is
tagged and the w3id `.htaccess` PR is merged.

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
