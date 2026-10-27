"""Offline integration: simulated sources/models and GitHub, actual Git and Astro."""
import json,os,shutil,subprocess,sys,tempfile,unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import blog,editor,editorial_store,create_review_pr as pr

@unittest.skipUnless(os.name=='posix' and (ROOT/'website/node_modules').is_dir(),'requires installed website dependencies')
class EndToEnd(unittest.TestCase):
 def test_discovery_to_review_pr_and_static_build(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'project';root.mkdir();shutil.copytree(ROOT/'website',root/'website',ignore=shutil.ignore_patterns('node_modules','dist','.astro'))
   baseline_articles={p.relative_to(root/'website/src/content/articles') for p in (root/'website/src/content/articles').rglob('*.md')}
   (root/'.gitignore').write_text('drafts/\ndata/\nwebsite/node_modules/\nwebsite/.astro/\nwebsite/dist/\n')
   def git(*args):return subprocess.run(['git',*args],cwd=root,check=True,capture_output=True,text=True)
   git('init','-b','main');git('config','user.name','Fixture Editor');git('config','user.email','fixture@example.invalid');git('add','.');git('commit','-m','fixture baseline');git('remote','add','origin','https://github.com/fixture/blog.git');git('update-ref','refs/remotes/origin/main','HEAD')
   one={'title':'Fixture product security incident','url':'https://vendor.example/advisory','published':'2026-01-01','feed':'fixture'}
   source='The vendor reported that 50 devices may be affected. '+('The vendor reported an issue with devices. '*10)
   second={'title':'Fixture coverage','url':'https://news.example/coverage','published':'2026-01-01','text':source}
   answer=['The vendor reports 50 devices may be affected [SOURCE 1].','# Fixture product security incident\n\nThe vendor says 50 devices may be affected.\n\n## Sources\nhttps://vendor.example/advisory\nhttps://news.example/coverage','[]']
   with patch.object(blog,'ROOT',root),patch.object(blog,'collect',return_value=[one]),patch.object(blog,'get_page',return_value=(source,one['url'],[])),patch.object(blog,'gather_sources',side_effect=lambda p,c:[p,second]),patch.object(blog,'ask',side_effect=answer),patch.object(sys,'argv',['blog.py','--category','cyber','--job-id','2026-10-26']):blog.main()
   draft=next((root/'drafts').glob('*.md'));quality=json.loads(next((root/'drafts').glob('*.quality.json')).read_text());self.assertFalse(quality['publication_allowed'])
   with closing(editorial_store.connect(root/'data/editorial.sqlite3')) as db, db:editorial_store.transition(db,draft,'REVIEWED','Fixture editor','Checked fixture evidence')
   built=[]
   def runner(*args,capture=False,cwd=None):
    if args[:3]==('gh','repo','view'):return SimpleNamespace(stdout='{"isPrivate":true}')
    if args[:2] in (('git','fetch'),('git','push')):return SimpleNamespace(stdout='')
    if args[:3]==('gh','pr','create'):
     subprocess.run(['npm','run','build'],cwd=Path(cwd)/'website',check=True,capture_output=True,text=True)
     page=Path(cwd)/'website/dist/articles'/draft.stem/'index.html';self.assertTrue(page.is_file());self.assertIn('Fixture product security incident',page.read_text());built.append(True)
     self.assertIn('--draft',args);return SimpleNamespace(stdout='https://example.invalid/pr/1')
    if args[:3]==('git','worktree','remove'):
     site=Path(args[3])/'website';(site/'node_modules').unlink(missing_ok=True)
     shutil.rmtree(site/'dist',ignore_errors=True);shutil.rmtree(site/'.astro',ignore_errors=True)
    result=subprocess.run(list(args),cwd=cwd or root,check=True,capture_output=True,text=True)
    if args[:3]==('git','worktree','add'):(Path(args[5])/'website/node_modules').symlink_to(ROOT/'website/node_modules',target_is_directory=True)
    return result
   with patch.object(pr,'ROOT',root),patch.object(editor,'DRAFTS',root/'drafts'),patch.object(pr,'run',side_effect=runner):
    pr.create(draft.name,'Fixture product security incident','A fictional test article','cyber','2026-10-26','fixture/blog',job_id='2026-10-26')
   self.assertTrue(built);self.assertEqual(git('branch','--show-current').stdout.strip(),'main')
   self.assertEqual(len(git('diff','--name-only','main','review/scheduled-2026-10-26').stdout.splitlines()),1)
   self.assertEqual({p.relative_to(root/'website/src/content/articles') for p in (root/'website/src/content/articles').rglob('*.md')},baseline_articles)
if __name__=='__main__':unittest.main()
