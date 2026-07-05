"""CI guard: deliverable integrity checks for the committed artifacts.

Verifies that the four generated deliverables at repo root parse and
match the operational baselines. This is a guard against broken or
partial commits, not a re-run of the pipeline — the deep checks live
in notebooks/30_validate.ipynb and notebooks/60_validate_study.ipynb.

Baselines below are a third copy of the numbers in 30_validate.ipynb
and README.md. When the DDF-RA tag is bumped and baselines drift,
update all three (see CLAUDE.md, "DDF-RA tag pinning").

Run from repo root: python scripts/ci_check.py
"""

import json
import sys

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, SH

# Operational baselines (DDF-RA v4.0.0, repo v0.6.0).
EXPECTED_ONTOLOGY_TRIPLES = 8642
EXPECTED_NAMED_CLASSES = 86
EXPECTED_STRUCTURAL_NODESHAPES = 80
EXPECTED_CT_NODESHAPES = 25
EXPECTED_JSONLD_VERSION = 1.1

failures = []


def check(name, actual, expected):
    if actual == expected:
        print(f"ok    {name}: {actual}")
    else:
        print(f"FAIL  {name}: expected {expected}, got {actual}")
        failures.append(name)


# 1. Ontology parses; triple count and named-class count match baseline.
ontology = Graph().parse("usdm_v4.ttl", format="turtle")
check("usdm_v4.ttl triple count", len(ontology), EXPECTED_ONTOLOGY_TRIPLES)
named_classes = sum(
    1 for c in ontology.subjects(RDF.type, OWL.Class) if isinstance(c, URIRef)
)
check("usdm_v4.ttl named owl:Class count", named_classes, EXPECTED_NAMED_CLASSES)

# 2. Structural shapes parse; NodeShape count matches baseline.
structural = Graph().parse("usdm_v4.shapes.ttl", format="turtle")
structural_shapes = sum(1 for _ in structural.subjects(RDF.type, SH.NodeShape))
check(
    "usdm_v4.shapes.ttl sh:NodeShape count",
    structural_shapes,
    EXPECTED_STRUCTURAL_NODESHAPES,
)

# 3. Terminology shapes parse; NodeShape count matches baseline.
ct = Graph().parse("usdm_v4.shapes-ct.ttl", format="turtle")
ct_shapes = sum(1 for _ in ct.subjects(RDF.type, SH.NodeShape))
check("usdm_v4.shapes-ct.ttl sh:NodeShape count", ct_shapes, EXPECTED_CT_NODESHAPES)

# 4. Instance context is valid JSON with a single top-level @context,
#    declares JSON-LD 1.1, and its type-scoped context count matches the
#    ontology's named-class count (cross-deliverable invariant).
with open("usdm_v4.context.jsonld", encoding="utf-8") as f:
    context_doc = json.load(f)
check(
    "usdm_v4.context.jsonld top-level keys",
    sorted(context_doc.keys()),
    ["@context"],
)
context = context_doc["@context"]
check("usdm_v4.context.jsonld @version", context.get("@version"), EXPECTED_JSONLD_VERSION)
type_scoped = sum(
    1 for v in context.values() if isinstance(v, dict) and "@context" in v
)
check(
    "usdm_v4.context.jsonld type-scoped contexts == named classes",
    type_scoped,
    named_classes,
)

if failures:
    print(f"\n{len(failures)} check(s) failed: {', '.join(failures)}")
    sys.exit(1)
print("\nAll deliverable integrity checks passed.")
