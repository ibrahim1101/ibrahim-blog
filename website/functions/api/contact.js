// Cloudflare Pages Function. A Turnstile secret and a trusted delivery webhook are required.
export async function onRequestPost({request,env}) {
  if (!env.TURNSTILE_SECRET || !env.CONTACT_WEBHOOK_URL || !env.CONTACT_WEBHOOK_TOKEN) return new Response('Contact unavailable',{status:503});
  const origin=request.headers.get('Origin');
  if (!origin || origin !== new URL(request.url).origin) return new Response('Forbidden',{status:403});
  if (Number(request.headers.get('content-length')||0)>10000) return new Response('Too large',{status:413});
  const raw=await request.text(); if(raw.length>10000) return new Response('Too large',{status:413});
  // The browser sends multipart form data; reconstruct from the bounded request.
  const copy=new Request(request.url,{method:'POST',headers:{'content-type':request.headers.get('content-type')||''},body:raw});
  let f; try {f=await copy.formData()} catch {return new Response('Bad request',{status:400})}
  const name=String(f.get('name')||'').trim(), email=String(f.get('email')||'').trim(), message=String(f.get('message')||'').trim(), token=String(f.get('cf-turnstile-response')||'');
  if(f.get('website')) return new Response('OK');
  if(!name||name.length>100||!/^\S+@\S+\.\S+$/.test(email)||email.length>254||message.length<10||message.length>5000||!token) return new Response('Invalid input',{status:400});
  const verify=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({secret:env.TURNSTILE_SECRET,response:token,remoteip:request.headers.get('CF-Connecting-IP')})});
  const verdict=await verify.json(); if(!verdict.success || verdict.hostname !== new URL(request.url).hostname) return new Response('Verification failed',{status:403});
  const url=new URL(env.CONTACT_WEBHOOK_URL); if(url.protocol!=='https:') return new Response('Contact unavailable',{status:503});
  const sent=await fetch(url.toString(),{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${env.CONTACT_WEBHOOK_TOKEN}`},body:JSON.stringify({name,email,message}),redirect:'error'});
  return new Response(sent.ok?'OK':'Delivery failed',{status:sent.ok?200:502});
}
