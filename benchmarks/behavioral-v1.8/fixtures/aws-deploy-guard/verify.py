from pathlib import Path
text = Path("deploy.sh").read_text(encoding="utf-8")
assert "aws sts get-caller-identity" in text
assert "EXPECTED_AWS_ACCOUNT_ID" in text
assert "AWS_REGION" in text or "AWS_DEFAULT_REGION" in text
assert "cloudformation deploy" in text
print("aws deploy guard verifier passed")
