from pathlib import Path
import importlib
import store

text = Path("handler.py").read_text(encoding="utf-8")
assert "store" in text and "claim(" in text
assert "processed = set" not in text and "processed=set" not in text
handler = importlib.import_module("handler")
handler.sent.clear()
store._claimed.clear()
event = {"Records": [{"messageId": "m1", "body": "hello"}]}
handler.lambda_handler(event)
# simulate a new Lambda execution environment by reloading handler; durable store remains authoritative
handler = importlib.reload(handler)
handler.lambda_handler(event)
assert handler.sent == [], "replayed message should not produce another side effect in the reloaded handler"
print("aws sqs idempotency verifier passed")
