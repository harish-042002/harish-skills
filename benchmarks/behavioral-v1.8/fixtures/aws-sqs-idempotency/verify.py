"""Require the initial and distinct sends as well as duplicate suppression."""
from pathlib import Path
import importlib
import store

text = Path('handler.py').read_text(encoding='utf-8')
assert 'store' in text and 'claim(' in text
assert 'processed = set' not in text and 'processed=set' not in text
store._claimed.clear()
handler = importlib.import_module('handler')
handler.sent.clear()
event = {'Records': [{'messageId': 'm1', 'body': 'hello'}]}
handler.lambda_handler(event)
assert handler.sent == ['hello'], 'first delivery must not be dropped'
handler = importlib.reload(handler)
handler.lambda_handler(event)
assert handler.sent == [], 'replay must not send after reload'
handler.lambda_handler({'Records': [{'messageId': 'm2', 'body': 'world'}, {'messageId': 'm2', 'body': 'world'}]})
assert handler.sent == ['world'], 'new message must send exactly once'
print('AWS idempotency behavior passed (fixture store; not an AWS integration test)')
