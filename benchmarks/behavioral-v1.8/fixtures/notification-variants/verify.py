from pathlib import Path
import ast

from catalogue import STATE_VARIANTS
from selector import reachable_variants

states = {"NORMAL", "CORE", "DECLINING", "INCONSISTENT"}
assert set(STATE_VARIANTS) == states
for state in states:
    rows = STATE_VARIANTS[state]
    assert len(rows) == 5, (state, len(rows))
    assert len(set(rows)) == 5
    assert len(reachable_variants(state)) >= 5

source = Path("catalogue.py").read_text(encoding="utf-8")
tree = ast.parse(source)
assert not any(isinstance(n, (ast.For, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) for n in ast.walk(tree)), "catalogue must stay explicit, not dynamically generated"
combined = "\n".join(Path(p).read_text(encoding="utf-8") for p in ["catalogue.py", "selector.py"])
for forbidden in ["confidence", "response_stage", "learning", "telemetry", "dynamic_variant"]:
    assert forbidden not in combined.lower(), forbidden
print("notification verifier passed")
