import {readdirSync,readFileSync,existsSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
export function checkMarkdown(text){
  const normalized=text.replace(/\r\n/g,'\n');
  if(!normalized.startsWith('---\n'))return 'missing frontmatter';
  const end=normalized.indexOf('\n---\n',4);if(end<0)return 'unterminated frontmatter';
  const body=normalized.slice(end+5);
  if(/<\s*(?:\/?\s*[a-z][\w:-]*\b|!\s*(?:--|doctype))/i.test(body))return 'raw HTML is not allowed';
  if(/\]\(\s*(?:javascript|vbscript|data)\s*:/i.test(body))return 'unsafe URL scheme';
  return null;
}
export function checkDirectory(dir){
  if(!existsSync(dir))return;
  for(const item of readdirSync(dir,{withFileTypes:true})){
    const path=join(dir,item.name);
    if(item.isDirectory())checkDirectory(path);
    else if(item.isFile()&&item.name.endsWith('.md')){const error=checkMarkdown(readFileSync(path,'utf8'));if(error)throw new Error(`${path}: ${error}`)}
  }
}
if(process.argv[1]&&fileURLToPath(import.meta.url)===resolve(process.argv[1]))checkDirectory(fileURLToPath(new URL('../src/content/articles/',import.meta.url)));
