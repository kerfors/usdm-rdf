# Conventions for AI sessions in this repo

## Scope

This repo produces four generated deliverables: `usdm_v4.ttl`,
`usdm_v4.context.jsonld` (JSON-LD 1.1 instance context, since v0.5.0), and
`usdm_v4.shapes.ttl` + `usdm_v4.shapes-ct.ttl` (SHACL structural +
terminology shapes, since v0.6.0). The pipeline is five notebooks. There is
no application code, no service, no API. Resist scope creep — if a task
starts to look like "let's also do X", flag it before implementing.

## Code style

- Python 3 + Pandas where useful. `pyyaml` for YAML, `rdflib` for validation.
- 4-space indentation. No exceptions.
- Complete, copy-paste-ready code. No `# fill this in` placeholders, no `...`.
- Fail-fast. No defensive try/except wrappers around things that should never
  fail. No silent auto-fixes that mask bad source data.
- No emojis in code, comments, or generated files unless explicitly asked.

## Code modification

- When asked to fix one thing, fix only that thing.
- Show a unified diff before editing — wait for approval before applying.
- Never "improve", "simplify", or "clean up" code that wasn't part of the
  request.
- Never remove code that looks redundant — there may be reasons not visible
  in the diff.
- Surgical precision. Bytes outside the requested change must be identical.

## Data integrity

- Never fabricate, simulate, or generate example data.
- Never invent C-Codes, definitions, preferred terms, or class names.
  `dataStructure.yml` is the only source of truth for model structure
  (classes, properties, cardinality, hierarchy). `USDM_CT.xlsx` is the
  only source of truth for codelist bindings.
- If real data is unavailable, state clearly and stop. Do not fall back to
  plausible-looking placeholders.

## Notebook generation

- Generate `.ipynb` files via Python's `json` module. Never write JSON text
  directly.
- Build the notebook as a Python dict with proper structure. Use helper
  functions `markdown_cell()` and `code_cell()`.
- Each cell's `source` field must be a list of strings, each ending with
  `\n`.
- Write with `json.dump(notebook, file, indent=1, ensure_ascii=False)`.
- After generation, verify the notebook opens in Jupyter immediately.

## DDF-RA tag pinning

- The DDF-RA release tag is pinned explicitly at the top of
  `10_fetch_yaml.ipynb`. Bumping it is a deliberate action.
- Both source files (`dataStructure.yml` and `USDM_CT.xlsx`) live at the
  same tag — bumping refreshes them in lockstep. Each gets its own SHA-256
  sidecar (`.fetch_meta.json` and `.fetch_meta_ct.json`).
- `30_validate.ipynb` additionally fetches `CDISC_Pilot_Study.json` at the
  same tag (sidecar `.fetch_meta_pilot.json`). It is test data for the
  instance context check, not a modelling source — `10_fetch_yaml.ipynb`
  holds sources of truth only.
- When the tag is bumped, re-run all four notebooks and update the
  baseline numbers in `30_validate.ipynb`, `40_generate_context.ipynb`,
  and `README.md` if they drift — document the delta in `docs/`.

## Review gates

The pipeline was built in this order, with explicit review at each step:

1. README + CLAUDE.md (proposed text → review → write)
2. Three notebook outlines (markdown structure + cell purpose, no code) →
   review → ok to generate notebooks
3. `10_fetch_yaml.ipynb` → run → confirm `downloads/dataStructure.yml`
4. `20_generate_turtle.ipynb` → run → confirm `usdm_v4.ttl` at repo root
5. `40_generate_context.ipynb` → run → confirm `usdm_v4.context.jsonld` at
   repo root (added v0.5.0; same outline → review → generate pattern)
6. `50_generate_shapes.ipynb` → run → confirm `usdm_v4.shapes.ttl` +
   `usdm_v4.shapes-ct.ttl` at repo root (added v0.6.0; same pattern)
7. `30_validate.ipynb` → run → confirm CSV reports match baselines within
   tolerance for source changes
8. Stage for commit, propose commit message, do not push without confirmation

Future structural changes follow the same pattern: propose → review → generate.

## Out of scope

Do not, unless the user explicitly opens the scope:

- Propose SULO or upper-ontology alignment.
- Propose value binding for codelists backed by external terminology
  packages (SDTM/Protocol Terminology members, free-text dictionary
  references). Pulling SDTM CT in would be a third source file with a
  decoupled release cadence. The 25 DDF-native value sets in sheet 2 of
  `USDM_CT.xlsx` are in scope since v0.6.0 (`usdm_v4.shapes-ct.ttl`).
- Propose alignment to the CDISC Library RDF Administered Item vocabulary.

These are documented in `README.md` as known gaps. Scope openings so far:
multiple-format publication shipped in v0.3 (w3id content negotiation);
the JSON-LD instance context shipped in v0.5.0 (decision D5); SHACL shapes
shipped in v0.6.0 (decision D6, design in `docs/shacl-design.md`).

## IRI scheme

- Ontology IRI: `https://w3id.org/cdisc/usdm/v4/` — slash semantics (v0.3).
  Do not silently change it. Rationale in `docs/iri-and-governance.md`.
- NCIt namespaces (dual anchor since v0.4.0, decision D4 in
  `docs/iri-and-governance.md`): every NCIt reference carries both the EVS
  identifier `http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#` (kept —
  NCI Thesaurus still declares it; host is NXDOMAIN) and the resolvable OBO
  PURL `http://purl.obolibrary.org/obo/NCIT_`. Do not emit one without the
  other.
- Property naming: `{ClassName}-{attributeName}` (class-scoped — attribute
  C-Codes differ per class; hyphen separator un-validated against CDISC
  Library RDF due to API access limitations).
- Project annotation namespace `usdm:` covers `modifier`, `relationshipType`,
  `modelName`, `modelRepresentation`, `boundCodelist`, `boundCodelistNote`.

## When in doubt

Ask. Especially:

- Before changing the IRI scheme.
- Before changing the property-naming convention.
- Before deviating from the mechanical mapping in `README.md`.
- Before adding a dependency beyond `pyyaml` + `rdflib` + `openpyxl` +
  `pyshacl` + standard library.
- Before adding a third source file beyond `dataStructure.yml` and
  `USDM_CT.xlsx`.
