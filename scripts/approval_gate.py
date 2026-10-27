"""Pure checks for a protected editorial environment; never grants approval."""
import argparse,json,sys

def touches_articles(pages):
 for page in pages:
  if not isinstance(page,list):raise ValueError('Invalid PR file listing')
  for item in page:
   if not isinstance(item,dict):raise ValueError('Invalid PR file')
   for key in ('filename','previous_filename'):
    name=item.get(key)
    protected={'scripts/approval_gate.py','.github/workflows/editorial-gate.yml'}
    if isinstance(name,str) and (name.startswith('website/src/content/articles/') or name in protected):return True
 return False

def has_owner_reviewer(environment,owner):
 if not isinstance(environment,dict) or environment.get('name','').lower()!='editorial':return False
 rules=environment.get('protection_rules',[])
 if not isinstance(rules,list):return False
 for rule in rules:
  if not isinstance(rule,dict) or rule.get('type')!='required_reviewers' or rule.get('prevent_self_review',False):continue
  reviewers=rule.get('reviewers',[])
  if isinstance(reviewers,list) and len(reviewers)==1:
   x=reviewers[0]
   if isinstance(x,dict) and x.get('type')=='User' and isinstance(x.get('reviewer'),dict) and str(x['reviewer'].get('login','')).lower()==owner.lower():return True
 return False

def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
 files=sub.add_parser('files');files.add_argument('path');files.add_argument('--changed-count',type=int,required=True)
 env=sub.add_parser('environment');env.add_argument('path');env.add_argument('--owner',required=True)
 args=p.parse_args()
 try:
  data=json.loads(open(args.path,encoding='utf8').read())
  if args.cmd=='files':
   if args.changed_count<0 or args.changed_count>3000:raise ValueError('Cannot safely inspect more than 3000 changed files')
   if not isinstance(data,list) or sum(len(page) for page in data if isinstance(page,list))!=args.changed_count:raise ValueError('Incomplete PR file listing')
   print('true' if touches_articles(data) else 'false');return 0
  if not has_owner_reviewer(data,args.owner):raise ValueError('Editorial environment must require the repository owner as reviewer and allow self-review')
  return 0
 except (OSError,ValueError,TypeError,json.JSONDecodeError) as exc:p.exit(1,str(exc)+'\n')
if __name__=='__main__':raise SystemExit(main())
