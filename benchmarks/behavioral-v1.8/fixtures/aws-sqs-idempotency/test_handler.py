import handler


def test_sends_once_in_one_process():
    event = {"Records": [{"messageId": "m1", "body": "hello"}]}
    handler.lambda_handler(event)
    handler.lambda_handler(event)
    assert handler.sent == ["hello"]
