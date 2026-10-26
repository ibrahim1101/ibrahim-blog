"""Build a temporary, explicitly fictional article; always remove it after testing."""
import subprocess,sys,os
from pathlib import Path
NPM = 'npm.cmd' if os.name == 'nt' else 'npm'
ROOT=Path(__file__).resolve().parents[1]; path=ROOT/'website/src/content/articles/fixture-test-only.md'
if path.exists(): raise SystemExit('Fixture file already exists; refusing to overwrite it')
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
try:
 path.write_text(fixture,encoding='utf-8')
 subprocess.run([NPM,'run','build'],cwd=ROOT/'website',check=True)
 article=ROOT/'website/dist/articles/fixture-test-only/index.html'
 html=article.read_text(encoding='utf-8')
 for expected in ('Fixture story for build verification','application/ld+json','https://example.com/fixture','Test editor'):
  if expected not in html: raise SystemExit('Missing expected article output: '+expected)
 subprocess.run([sys.executable,str(ROOT/'scripts/check_site.py')],check=True)
 print('Fixture article, metadata, source link and static routes: PASS')
finally: path.unlink(missing_ok=True)
# Rebuild empty production content; fixture must never remain in the deliverable.
subprocess.run([NPM,'run','build'],cwd=ROOT/'website',check=True)
if (ROOT/'website/dist/articles/fixture-test-only/index.html').exists(): raise SystemExit('Fixture remained in clean build')
