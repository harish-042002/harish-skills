"""Parse IAM structure, not keyword mentions in comments. Requires PyYAML."""
from pathlib import Path
try:
    import yaml
except ImportError:
    raise SystemExit('BLOCKED: install PyYAML to run the independent IAM verifier')

doc = yaml.safe_load(Path('template.yaml').read_text(encoding='utf-8'))
assert set(doc) == {'Resources'}
assert set(doc['Resources']) == {'AppRole'}
role = doc['Resources']['AppRole']
assert set(role) == {'Type', 'Properties'} and role['Type'] == 'AWS::IAM::Role'
props = role['Properties']
assert set(props) == {'AssumeRolePolicyDocument', 'Policies'}
assert props['AssumeRolePolicyDocument'] == {'Version':'2012-10-17','Statement':[{'Effect':'Allow','Principal':{'Service':'lambda.amazonaws.com'},'Action':'sts:AssumeRole'}]}
policies = props['Policies']
assert len(policies) == 1 and set(policies[0]) == {'PolicyName','PolicyDocument'}
assert policies[0]['PolicyName'] == 'AppAccess'
policy = policies[0]['PolicyDocument']
assert set(policy) == {'Version','Statement'} and policy['Version'] == '2012-10-17'
statements = policy['Statement']
assert len(statements) == 1
st = statements[0]
assert set(st) == {'Effect','Action','Resource'} and st['Effect'] == 'Allow'
as_list = lambda v: v if isinstance(v,list) else [v]
assert as_list(st['Action']) == ['s3:GetObject']
assert as_list(st['Resource']) == ['arn:aws:s3:::my-bucket/assets/*']
print('IAM parsed-policy verifier passed')
