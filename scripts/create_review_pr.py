#!/usr/bin/env python3
"""Create a draft PR in a separate worktree. Never merges or approves."""
import argparse,datetime as dt,json,re,subprocess,sys,tempfile,uuid
from pathlib import Path
import editor
ROOT=Path(__file__).resolve().parents[1]

def run(*args,capture=False,cwd=None):
 return subprocess.run(list(args),cwd=cwd or ROOT,check=True,text=True,capture_output=capture)

def create(draft,title,description,category,date,repository,allow_public=False,job_id=None):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repository):raise ValueError('invalid repository')
 if job_id and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',job_id):raise ValueError('invalid job id')
 article=editor.selected(draft);editor.artifacts(article)
 remote=run('git','remote','get-url','origin',capture=True).stdout.strip().removesuffix('.git').lower()
 if remote not in (f'https://github.com/{repository.lower()}',f'git@github.com:{repository.lower()}'):raise ValueError('origin does not match repository')
 info=json.loads(run('gh','repo','view',repository,'--json','isPrivate',capture=True).stdout)
 if info.get('isPrivate') is not True and not allow_public:raise ValueError('Public PRs expose drafts. Pass --allow-public only if you explicitly want that exposure.')
 run('git','fetch','origin','main')
 branch='review/scheduled-'+job_id if job_id else 'review/'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d')+'-'+uuid.uuid4().hex[:10]
 folder=Path(tempfile.mkdtemp(prefix='ibrahimblog-review-'))
 run('git','worktree','add','-b',branch,str(folder),'origin/main')
 previous=editor.PUBLIC
 try:
  editor.PUBLIC=folder/'website'/'src'/'content'/'articles'
  output=editor.stage(article,title,description,category,date)
 finally:editor.PUBLIC=previous
 relative=output.relative_to(folder).as_posix()
 run('git','add','--',relative,cwd=folder)
 run('git','commit','-m','Prepare article for editorial review',cwd=folder)
 run('git','push','-u','origin',branch,cwd=folder)
 result=run('gh','pr','create','--repo',repository,'--base','main','--head',branch,'--draft','--title','Review: '+title,'--body','Editorial review is required. Review every claim against the original sources before any publication decision.',capture=True,cwd=folder)
 # A failed operation leaves the worktree intact for inspection.
 run('git','worktree','remove',str(folder))
 return result.stdout.strip()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('draft');ap.add_argument('--title',required=True);ap.add_argument('--description',required=True);ap.add_argument('--category',choices=sorted(editor.CATEGORIES),required=True);ap.add_argument('--date',required=True);ap.add_argument('--repo',default='ibrahim1101/ibrahim-blog');ap.add_argument('--allow-public',action='store_true');ap.add_argument('--job-id',help=argparse.SUPPRESS);args=ap.parse_args()
 try:
  print('Draft PR:',create(args.draft,args.title,args.description,args.category,args.date,args.repo,args.allow_public,args.job_id));print('This PR is a draft and is not a publication approval.')
 except (ValueError,OSError,subprocess.CalledProcessError,json.JSONDecodeError) as e:
  print('PR preparation failed:',e,file=sys.stderr);print('Inspect local review worktrees and remote branches before retrying.',file=sys.stderr);return 1
 return 0
if __name__=='__main__':raise SystemExit(main())
