processed = set()
sent = []


def send_notification(body: str) -> None:
    sent.append(body)


def lambda_handler(event, context=None):
    for record in event["Records"]:
        message_id = record["messageId"]
        if message_id in processed:
            continue
        send_notification(record["body"])
        processed.add(message_id)
    return {"batchItemFailures": []}
