import {test} from 'node:test'; import assert from 'node:assert/strict'; import {checkMarkdown} from '../scripts/check-articles.mjs';
test('permits ordinary markdown and source links',()=>assert.equal(checkMarkdown('---\ntitle: Story\n---\n\nAn ordinary [source](https://example.com).'),null));
test('rejects executable raw HTML',()=>assert.match(checkMarkdown('---\ntitle: Story\n---\n\n<script>alert(1)</script>'),/raw HTML/));
test('rejects javascript links',()=>assert.match(checkMarkdown('---\ntitle: Story\n---\n\n[click](javascript:alert)'),/unsafe URL/));
