# UGG handoff dossier

## Purpose

This is the internal briefing file for the governance conversation with
the USDM Governance Group (UGG). It gathers, in one place and in a
register suitable for CDISC readers, what exists, what is being
offered, what a transfer involves, and which questions only a
governance body can answer. When UGG responds, excerpt from here —
sections "The offer in one paragraph" and "Transfer checklist" are
written to be lifted verbatim.

This document is not the outreach message itself, and it introduces no
new decisions. Everything here is sourced from `iri-and-governance.md`,
`known-gaps.md`, `shacl-design.md`, and `README.md`; those remain the
canonical records.

## What exists today

Four generated deliverables, published at stable web identifiers under
`https://w3id.org/cdisc/usdm/v4/` and regenerated mechanically from the
files CDISC already publishes in DDF-RA (`dataStructure.yml` and
`USDM_CT.xlsx`, co-pinned at release tag v4.0.0):

- **`usdm_v4.ttl` — the ontology.** USDM v4 as a formal vocabulary: 86
  classes and 693 attributes, each with a stable identifier, carrying
  the NCI C-Codes, definitions, cardinality, and inheritance already
  present in `dataStructure.yml`. Every C-Code-bearing entity links to
  NCI Thesaurus in both the identifier form CDISC Library uses and a
  form that resolves in a browser. For CDISC this means the USDM model
  itself becomes queryable data — the same question ("which attributes
  are bound to which codelist?") that today requires reading the spec
  can be answered by a query.
- **`usdm_v4.context.jsonld` — the instance context.** A single file
  that, applied to USDM API instance JSON (the DDF wire format,
  unchanged), reads it as a graph using the ontology's identifiers.
  Verified against the CDISC Pilot example study published in DDF-RA:
  all 1,953 typed objects and all 1,257 cross-references resolve, none
  dangling, no unmapped keys.
- **`usdm_v4.shapes.ttl` + `usdm_v4.shapes-ct.ttl` — machine-checkable
  conformance rules (SHACL).** The structural layer checks instance
  data against the model (80 class shapes); the terminology layer
  checks coded values against the 25 DDF-native value sets in
  `USDM_CT.xlsx`, with severity derived from codelist extensibility.
  Run against the CDISC Pilot example, the structural layer passes and
  the terminology layer reports 14 findings — placeholder and extension
  codes in the published example, i.e. the checks find real things.

Around the deliverables: a five-notebook pipeline that regenerates
everything from a pinned DDF-RA tag with SHA-256 verification of
sources; seven worked example notebooks; rendered HTML documentation
per class and attribute; a CI guard that verifies the published
deliverables parse and match baselines on every change; and a decision
log (D1–D6, below). Licensing mirrors the source: code MIT, generated
content CC-BY-4.0.

**Status: draft, explicitly not a normative CDISC artifact.** That
label is the point of this dossier.

## The offer in one paragraph

The transfer mechanism is the redirect, not the artifact. The
identifiers live under `w3id.org`, a community-run permanent-identifier
service: every identifier is a redirect to wherever the files are
actually hosted. CDISC can take over at any point by (1) hosting the
files — or the whole repository — under its own infrastructure and (2)
submitting one pull request to the w3id registry changing the redirect
target. No published identifier changes, nothing breaks for anyone
already using them, and no consumer needs to re-fetch anything. The
offer is explicit: adopt as much or as little as wanted, from "CDISC
hosts and governs everything" down to "the community maintains it and
CDISC merely knows it exists."

## Precedent inside CDISC, and the LinkML question

The practice this dossier proposes is not foreign to CDISC — a sibling
standard already runs it in production. COSMoS
(`github.com/cdisc-org/COSMoS`, Biomedical Concepts and SDTM Dataset
Specializations) publishes its model as one LinkML schema per artifact
type (`model/cosmos_bc_model.yaml` and siblings), publishes every
concept as an instance YAML file in dated release packages, generates
JSON Schema, Python classes, diagrams, and documentation from the
schema with standard generators, and validates every instance file
against the schema in scripted checks. Model as data, artifacts
generated rather than hand-written, conformance checks falling out of
the schema — for Biomedical Concepts this is CDISC's current practice,
not a proposal. What COSMoS does not have, and what this dossier
offers for USDM, is the naming layer: persistent, resolvable, governed
identifiers for the concepts themselves. (COSMoS instances point at
NCI Thesaurus by href; the concepts have no dereferenceable CDISC
namespace of their own.)

The obvious question is then why usdm-rdf is not itself built on
LinkML. The answer: the offer is toolchain-neutral, and the value is
not in the format conversion. A generic schema-to-OWL or
schema-to-SHACL generator is a mechanical mapping; nothing in it
produces the decisions recorded in this dossier — dual NCIt anchoring,
declaring-class property identifiers, severity derived from codelist
extensibility, the version-identity conventions D1–D3. Those are
semantic and governance decisions, and someone had to make them
regardless of toolchain. If CDISC implements an official USDM pipeline
the COSMoS way — a LinkML rendering of the model with generated
artifacts — nothing in this offer stands in the way: the decision log
becomes the acceptance criteria, and the w3id redirect lets the
published identifiers survive a toolchain swap unchanged. For the
record, the maintainer has followed LinkML since Solbrig and Mungall
introduced it in 2021 and publicly welcomed CDISC's adoption of it in
April 2023
(<https://kerfors.github.io/tweetsreborn/2023/04/1651485700213145600.html>)
— the direct-generator route for USDM was chosen with LinkML on the
table, not in ignorance of it.

One more reason this section exists now: independent semantic
renderings of USDM keep appearing — this repository, the Fuseki/SPARQL
demonstrator shown at a d4k deep-dive, and a third-party LinkML
documentation site whose generated pages are already being mistaken
for an official CDISC artifact. Each new derivative restates the same
fact: the tooling is available to everyone, and the names still have
no owner. That is the situation the proposal asks UGG to resolve.

## Decision log D1–D6

What UGG would inherit, one entry per recorded decision. Full rationale
in `iri-and-governance.md`.

- **IRI scheme (v0.3, load-bearing).** `https://w3id.org/cdisc/usdm/v4/`
  with per-entity identifiers (`…/v4/Activity`,
  `…/v4/Activity-name`). The major version in the path means a future
  USDM v5 gets its own namespace without breaking v4 users. Identifiers
  are treated as stable from v0.3 forward — this is the one commitment
  a successor should not reopen.
- **D1–D3 — version identity (v0.3.1, conventions).** Creation date
  fixed at first publication; every release is separately and
  permanently addressable (e.g. `…/v4/0.6.0` fetches exactly the 0.6.0
  ontology, forever, with no registry change per release); derived
  renderings never carry statements the canonical file lacks.
  Inheritable as-is.
- **D4 — dual NCIt anchoring (v0.4.0, load-bearing rule).** Every NCI
  Thesaurus reference carries two forms: the EVS identifier (the form
  NCI's own OWL and CDISC Library use — correct for identity, but its
  host no longer exists in DNS) and the OBO PURL (resolves in a
  browser — correct for access). One rule, no exceptions, enforced at
  generation and checked at validation.
- **D5 — JSON-LD instance context (v0.5.0, deliverable).** The wire
  format is untouched; the context is a lens over it. Scope could be
  revisited by a successor without affecting the ontology.
- **D6 — SHACL in two layers (v0.6.0, deliverable).** Structure and
  terminology are separate files because they answer different
  questions and fail differently. The source boundary is deliberate:
  only value sets actually published inside `USDM_CT.xlsx` are checked;
  external terminology packages (SDTM CT, MedDRA, ISO…) are out of
  scope — see open questions.
- **Property naming (revisitable, flagged).** Attributes are named
  `{ClassName}-{attributeName}` because attribute-level C-Codes differ
  per class. The hyphen separator is deliberately un-validated against
  CDISC Library RDF — that requires membership-tier API access the
  maintainer does not have. If CDISC review finds divergence, the
  recorded position is a deliberate re-emit or explicit deprecation,
  never a silent change to published identifiers.

## Transfer checklist

In order, if CDISC decides to adopt. Steps 1–3 are the actual
transfer; 4–6 are follow-ons that need CDISC-side capabilities.

1. **Decide the hosting home.** Options in ascending involvement:
   leave the GitHub repo where it is and mirror releases; fork/transfer
   the repo into the CDISC GitHub organization; or host the four
   deliverable files on CDISC web infrastructure. The pipeline is five
   notebooks with four dependencies (pyyaml, rdflib, openpyxl, pyshacl)
   — no service, no API, nothing to operate.
2. **One w3id pull request** changing the redirect targets in the
   registry entry for `/cdisc/usdm/v4/`. The existing entry already
   handles format negotiation (Turtle, RDF/XML, JSON-LD, N-Triples,
   HTML), per-version fetching, and the fixed paths for the context and
   shapes files — the PR only repoints where those redirects land.
3. **Update the status label** from "draft, not a normative CDISC
   artifact" to whatever CDISC decides it is.
4. **Take over the release procedure.** When DDF-RA publishes a new
   tag: bump the pinned tag, re-run the pipeline, review the baseline
   deltas, release. The procedure is documented (`CLAUDE.md`,
   tag-pinning section) and the CI guard catches broken or partial
   publications automatically.
5. **Validate property naming against CDISC Library RDF** (see decision
   log) — an afternoon's work for someone with Library API access, and
   the one recorded decision that external review could overturn.
6. **Decide the open questions below** — these were always governance
   questions; the handoff just gives them their proper owner.

## What only UGG can decide

Three questions are parked in the repo not for lack of code but for
lack of an authoritative decision source. They are part of what the
handoff offers to transfer.

1. **Concept lifecycle.** When a USDM concept is deprecated, split, or
   removed in a later version, what happens to its identifier? The
   detection is mechanical (diff the source across tags) and the
   annotation is mechanical (deprecation flags, replacement links) —
   but the assertion "this concept is gone, replaced by that one" is a
   statement about what CDISC's names mean over time. A diff cannot
   distinguish a removal from a rename; only a governance body can.
   Recorded position: `iri-and-governance.md`, "Concept lifecycle
   across versions".
2. **Property naming alignment.** See decision log and checklist step
   5 — needs CDISC Library RDF access.
3. **External terminology scope.** The terminology checks stop at the
   value sets published inside `USDM_CT.xlsx`. Extending to SDTM CT or
   Protocol Terminology members means taking a dependency on the
   quarterly NCI EVS CT publications — a third source with its own
   release cadence, which is a pinning-policy decision before it is a
   technical one.

## Status log

Venue note: introductory contact with UGG is via the DDF feedback form
at <https://www.cdisc.org/ddf> (categories *Suggestions for
improvements to USDM* or *Model extensions*); UGG membership is by
annual nomination. The DDF-RA GitHub repo is for technical feedback on
published artifacts and is not the governance venue.

- 2026-05-04 — w3id registration for the current namespace merged
  (perma-id/w3id.org #6012, slash semantics; supersedes the v0.2
  registration #5994). Same day: DDF-RA discussion #706 posted
  (show-and-tell) — technical venue, recognized afterwards as not the
  governance channel.
- 2026-06-12 — v0.4.0 released (dual NCIt anchoring, D4); w3id re-pin
  #6190 merged. **UGG proposal submitted via the DDF feedback form**
  (<https://www.cdisc.org/ddf>).
- 2026-07-02 — comment posted on CDISC President/CEO Chris Decker's
  article "Humpty Dumpty Clinical Data", noting matter-of-factly that
  the governance question sits with the UGG — surfaces the pending
  proposal without pressing it.
- 2026-07-04 — v0.5.0 and v0.6.0 released (instance context D5, SHACL
  shapes D6); w3id re-pin PRs #6302 and #6303 merged; announcement
  articles published on LinkedIn.
- As of 2026-07-05: no response and no confirmation of receipt on the
  UGG proposal.
- 2026-08-03 — section "Precedent inside CDISC, and the LinkML
  question" added, after verifying that COSMoS runs a full
  LinkML-based model-as-data pipeline (schema, generated artifacts,
  scripted instance validation) — a CDISC-internal precedent for what
  this dossier proposes. Prompted by community attention to LinkML
  following Lex Jansen's passing.

Append new events above this line as they happen.
