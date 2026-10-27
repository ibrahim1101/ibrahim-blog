// Cloudflare Pages Function. A Turnstile secret and a trusted delivery webhook are required.
async function boundedBody(request,limit=10000){
  if(Number(request.headers.get('content-length')||0)>limit)throw new Error('large');
  if(!request.body)throw new Error('missing');
  const reader=request.body.getReader(),chunks=[];let total=0;
  try{for(;;){const {value,done}=await reader.read();if(done)break;total+=value.byteLength;if(total>limit){throw new Error('large')}chunks.push(value)}}finally{reader.releaseLock()}
  const bytes=new Uint8Array(total);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength}return bytes;
}
export async function onRequestPost({request,env}) {
  if (!env.TURNSTILE_SECRET || !env.CONTACT_WEBHOOK_URL || !env.CONTACT_WEBHOOK_TOKEN) return new Response('Contact unavailable',{status:503});
  const origin=request.headers.get('Origin');
  if (!origin || origin !== new URL(request.url).origin) return new Response('Forbidden',{status:403});
  let raw; try {raw=await boundedBody(request)} catch {return new Response('Too large or missing',{status:413})}
  // The browser sends multipart form data; reconstruct from the bounded request.
  const copy=new Request(request.url,{method:'POST',headers:{'content-type':request.headers.get('content-type')||''},body:raw});
  let f; try {f=await copy.formData()} catch {return new Response('Bad request',{status:400})}
  const name=String(f.get('name')||'').trim(), email=String(f.get('email')||'').trim(), message=String(f.get('message')||'').trim(), token=String(f.get('cf-turnstile-response')||'');
  if(f.get('website')) return new Response('OK');
  if(!name||name.length>100||!/^\S+@\S+\.\S+$/.test(email)||email.length>254||message.length<10||message.length>5000||!token) return new Response('Invalid input',{status:400});
  try {
  const verify=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({secret:env.TURNSTILE_SECRET,response:token,remoteip:request.headers.get('CF-Connecting-IP')})});
  const verdict=await verify.json(); if(!verdict.success || verdict.hostname !== new URL(request.url).hostname) return new Response('Verification failed',{status:403});
  const url=new URL(env.CONTACT_WEBHOOK_URL); if(url.protocol!=='https:') return new Response('Contact unavailable',{status:503});
  const sent=await fetch(url.toString(),{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${env.CONTACT_WEBHOOK_TOKEN}`},body:JSON.stringify({name,email,message,clientIp:request.headers.get('CF-Connecting-IP')||'unknown'}),redirect:'error'});
  return new Response(sent.ok?'OK':'Delivery failed',{status:sent.ok?200:sent.status===429?429:502});
  } catch {return new Response('Delivery unavailable',{status:502})}
}
