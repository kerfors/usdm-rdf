# Conventions for AI sessions in this repo

## Scope

This repo produces a single Turtle file: `usdm_v4.ttl`. The pipeline is three
notebooks. There is no application code, no service, no API. Resist scope
creep — if a task starts to look like "let's also do X", flag it before
implementing.

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
- When the tag is bumped, re-run all three notebooks and update the
  baseline numbers in `30_validate.ipynb` and `README.md` if they drift —
  document the delta in `docs/`.

## Review gates

The pipeline was built in this order, with explicit review at each step:

1. README + CLAUDE.md (proposed text → review → write)
2. Three notebook outlines (markdown structure + cell purpose, no code) →
   review → ok to generate notebooks
3. `10_fetch_yaml.ipynb` → run → confirm `downloads/dataStructure.yml`
4. `20_generate_turtle.ipynb` → run → confirm `usdm_v4.ttl` at repo root
5. `30_validate.ipynb` → run → confirm CSV report matches baseline within
   tolerance for source changes
6. Stage for commit, propose commit message, do not push without confirmation

Future structural changes follow the same pattern: propose → review → generate.

## What v0.1 is **not** for

Do not, in this iteration:

- Propose SULO or upper-ontology alignment.
- Propose binding `USDM_CT.xlsx` enumerated codelist *values* (sheet 2 of
  USDM_CT — permitted Code values per codelist). Codelist-level anchoring
  is in scope; per-value binding is not.
- Propose alignment to the CDISC Library RDF Administered Item vocabulary.
- Propose SHACL shapes.
- Propose RDF/XML, JSON-LD, or NTriples publication.

These are documented in `README.md` as known gaps. Treat them as out-of-scope
unless the user explicitly opens that scope.

## IRI scheme

- Ontology IRI: `https://w3id.org/cdisc/usdm/v4#` — hash semantics. Do not
  silently change it. Rationale in `docs/iri-and-governance.md`.
- NCIt namespace: `http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#`.
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
  standard library.
- Before adding a third source file beyond `dataStructure.yml` and
  `USDM_CT.xlsx`.
