from pathlib import Path
text = Path("template.yaml").read_text(encoding="utf-8")
assert "s3:GetObject" in text
assert "arn:aws:s3:::my-bucket/assets/*" in text
policy = text.split("PolicyDocument:", 1)[1]
assert "Action: '*'" not in policy and 'Action: "*"' not in policy
assert "Resource: '*'" not in policy and 'Resource: "*"' not in policy
print("aws iam verifier passed")
