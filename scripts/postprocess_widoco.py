"""
postprocess_widoco.py — inject NCIt + usdm:* metadata into WIDOCO HTML.

Reads the v0.3 usdm_v4.ttl, walks every <div class="entity" id="X">
block in the WIDOCO output, and inserts a project-metadata block
(preferred term, NCIt anchor, modifier or relationship type / model
name / model representation / codelist binding / codelist binding
raw) for each.

Fail-fast contract:
  - Every entity div in the HTML must resolve to an IRI in the graph.
  - Every named owl:Class / owl:DatatypeProperty / owl:ObjectProperty
    in the graph (under the usdm namespace) must have a matching div
    in the HTML.

Usage:
    python postprocess_widoco.py <widoco-output-dir> <ttl-path>
"""

import html
import re
import sys
from pathlib import Path

import rdflib
from rdflib.namespace import OWL, RDF, SKOS

USDM_NS = "https://w3id.org/cdisc/usdm/v4/"
NCIT_NS = "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#"

USDM = rdflib.Namespace(USDM_NS)


def one(g, s, p):
    """Return single object value, or None. Raise on multiple."""
    vals = list(g.objects(s, p))
    if len(vals) > 1:
        raise ValueError(f"multiple values for {s} {p}: {vals}")
    return vals[0] if vals else None


def render_metadata(g, local_name, kind, iri):
    """Build the <dl class="usdm-metadata"> block for one entity."""
    rows = []

    pref = one(g, iri, SKOS.prefLabel)
    if pref is not None:
        rows.append(("preferred term", html.escape(str(pref))))

    exact = one(g, iri, SKOS.exactMatch)
    if exact is not None and isinstance(exact, rdflib.URIRef) and str(exact).startswith(NCIT_NS):
        ccode = str(exact)[len(NCIT_NS):]
        rows.append(("NCIt anchor", f'<a href="{html.escape(str(exact))}">ncit:{html.escape(ccode)}</a>'))

    if kind == "class":
        mod = one(g, iri, USDM["modifier"])
        if mod is not None:
            rows.append(("modifier", html.escape(str(mod))))
    elif kind == "property":
        rt = one(g, iri, USDM["relationshipType"])
        if rt is not None:
            rows.append(("relationship type", html.escape(str(rt))))
        mn = one(g, iri, USDM["modelName"])
        if mn is not None:
            rows.append(("model name", html.escape(str(mn))))
        mr = one(g, iri, USDM["modelRepresentation"])
        if mr is not None:
            rows.append(("model representation", html.escape(str(mr))))
        bc = one(g, iri, USDM["boundCodelist"])
        if bc is not None and isinstance(bc, rdflib.URIRef) and str(bc).startswith(NCIT_NS):
            ccode = str(bc)[len(NCIT_NS):]
            rows.append(("codelist binding", f'<a href="{html.escape(str(bc))}">ncit:{html.escape(ccode)}</a>'))
        bcn = one(g, iri, USDM["boundCodelistNote"])
        if bcn is not None:
            rows.append(("codelist binding (raw)", f'<pre>{html.escape(str(bcn))}</pre>'))

    if not rows:
        return ""

    out = ['  <dl class="usdm-metadata">']
    for label, value in rows:
        out.append(f'   <dt>{label}</dt>')
        out.append(f'   <dd>{value}</dd>')
    out.append('  </dl>')
    return "\n".join(out) + "\n  "


CSS_BLOCK = """

/* usdm-rdf post-processor: project-metadata block injected per entity */
dl.usdm-metadata {
    margin: 0.5em 0;
    padding: 0.5em 1em;
    border-left: 3px solid #888;
    background: #f6f6f6;
}
dl.usdm-metadata dt {
    font-weight: bold;
    margin-top: 0.3em;
}
dl.usdm-metadata dd {
    margin-left: 1.5em;
}
dl.usdm-metadata pre {
    margin: 0.2em 0;
    font-size: 0.9em;
    white-space: pre-wrap;
}
"""


ENTITY_RE = re.compile(
    r'(<div class="entity" id="(?P<id>[^"]+)">[\s\S]*?)'
    r'(<dl class="description"|<div class="description")'
)


def main():
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <widoco-output-dir> <ttl-path>", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(sys.argv[1])
    ttl_path = Path(sys.argv[2])

    if not out_dir.is_dir():
        sys.exit(f"not a directory: {out_dir}")
    if not ttl_path.is_file():
        sys.exit(f"file not found: {ttl_path}")

    g = rdflib.Graph()
    g.parse(ttl_path, format="turtle")

    # Build entity registry: local_name -> ("class"|"property", IRI)
    entities = {}
    for s in g.subjects(RDF.type, OWL.Class):
        if isinstance(s, rdflib.URIRef) and str(s).startswith(USDM_NS):
            entities[str(s)[len(USDM_NS):]] = ("class", s)
    for s in g.subjects(RDF.type, OWL.DatatypeProperty):
        if isinstance(s, rdflib.URIRef) and str(s).startswith(USDM_NS):
            entities[str(s)[len(USDM_NS):]] = ("property", s)
    for s in g.subjects(RDF.type, OWL.ObjectProperty):
        if isinstance(s, rdflib.URIRef) and str(s).startswith(USDM_NS):
            entities[str(s)[len(USDM_NS):]] = ("property", s)

    print(f"graph: {len(entities)} named entities under {USDM_NS}", file=sys.stderr)

    found_ids = set()
    n_files = 0
    n_patched = 0

    for html_path in sorted(out_dir.rglob("*.html")):
        text = html_path.read_text(encoding="utf-8")
        if 'class="entity"' not in text:
            continue
        n_files += 1
        file_count = 0

        def sub(m):
            nonlocal file_count
            local = m.group("id")
            if local not in entities:
                raise ValueError(f"unknown entity in {html_path}: {local!r} not in graph")
            found_ids.add(local)
            file_count += 1
            kind, iri = entities[local]
            block = render_metadata(g, local, kind, iri)
            if not block:
                return m.group(0)
            return m.group(1) + block + m.group(3)

        new_text = ENTITY_RE.sub(sub, text)
        if new_text != text:
            html_path.write_text(new_text, encoding="utf-8")
            print(f"  patched {file_count} entities in {html_path.relative_to(out_dir)}", file=sys.stderr)
            n_patched += file_count

    missing = set(entities.keys()) - found_ids
    if missing:
        sample = sorted(missing)[:5]
        raise ValueError(
            f"{len(missing)} graph entities have no matching HTML div "
            f"(sample: {sample})"
        )

    extra_css = out_dir / "doc" / "resources" / "extra.css"
    if extra_css.is_file():
        with extra_css.open("a", encoding="utf-8") as f:
            f.write(CSS_BLOCK)
    else:
        extra_css.parent.mkdir(parents=True, exist_ok=True)
        extra_css.write_text(CSS_BLOCK.lstrip(), encoding="utf-8")

    print(f"DONE: patched {n_patched} entity divs across {n_files} files; appended CSS to {extra_css}", file=sys.stderr)


if __name__ == "__main__":
    main()
