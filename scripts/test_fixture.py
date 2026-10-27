"""Build a fictional article in an isolated temporary copy, never the real site."""
import os,shutil,subprocess,sys,tempfile
from pathlib import Path
NPM='npm.cmd' if os.name=='nt' else 'npm'
ROOT=Path(__file__).resolve().parents[1]
fixture='''---
title: "Fixture story for build verification"
description: "A fictional article used only in automated tests."
category: cyber
author: "Test editor"
published: "2026-01-02"
disclosure: "Fictional test fixture."
sources:
  - title: "Example source"
    url: "https://example.com/fixture"
---
This is fictional text used to exercise article templates.\n'''
with tempfile.TemporaryDirectory(prefix='ibrahimblog-fixture-') as tmp:
 site=Path(tmp)/'website'
 shutil.copytree(ROOT/'website',site,ignore=shutil.ignore_patterns('node_modules','dist','.astro'))
 deps=ROOT/'website/node_modules'
 if not deps.is_dir():raise SystemExit('Website dependencies missing; run npm ci first')
 if os.name=='nt':shutil.copytree(deps,site/'node_modules')
 else:(site/'node_modules').symlink_to(deps,target_is_directory=True)
 path=site/'src/content/articles/fixture-test-only.md';path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():raise SystemExit('Fixture filename already exists in source; refusing to overwrite it')
 path.write_text(fixture,encoding='utf8')
 subprocess.run([NPM,'run','build'],cwd=site,check=True)
 article=site/'dist/articles/fixture-test-only/index.html';html=article.read_text(encoding='utf8')
 for expected in ('Fixture story for build verification','application/ld+json','https://example.com/fixture','Test editor'):
  if expected not in html:raise SystemExit('Missing expected article output: '+expected)
 subprocess.run([sys.executable,str(ROOT/'scripts/check_site.py'),'--site-dir',str(site/'dist')],check=True)
 path.unlink()
 subprocess.run([NPM,'run','build'],cwd=site,check=True)
 if article.exists():raise SystemExit('Fixture remained in clean build')
 print('Isolated fixture article, metadata, links and clean removal: PASS')
