// Private delivery adapter for the Pages contact form. Deploy only with a restricted EMAIL binding.
async function boundedBody(request,limit=12000){
  if(Number(request.headers.get('content-length')||0)>limit)throw new Error('large');
  if(!request.body)throw new Error('missing');
  const reader=request.body.getReader(), chunks=[];let size=0;
  try{for(;;){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>limit){throw new Error('large')}chunks.push(value)}}finally{reader.releaseLock()}
  const data=new Uint8Array(size);let offset=0;for(const chunk of chunks){data.set(chunk,offset);offset+=chunk.byteLength}return new TextDecoder().decode(data);
}
async function equalSecret(a,b){
  const enc=new TextEncoder();const [x,y]=await Promise.all([crypto.subtle.digest('SHA-256',enc.encode(a)),crypto.subtle.digest('SHA-256',enc.encode(b))]);
  const p=new Uint8Array(x),q=new Uint8Array(y);let diff=0;for(let i=0;i<p.length;i++)diff|=p[i]^q[i];return diff===0;
}
export default {async fetch(request,env){
  if(request.method!=='POST')return new Response('Method not allowed',{status:405,headers:{Allow:'POST'}});
  if(!env.CONTACT_TOKEN||!env.CONTACT_FROM||!env.CONTACT_TO||!env.EMAIL)return new Response('Unavailable',{status:503});
  const auth=request.headers.get('Authorization')||'';if(!auth.startsWith('Bearer ')||!(await equalSecret(auth.slice(7),env.CONTACT_TOKEN)))return new Response('Unauthorized',{status:401});
  let item;try{item=JSON.parse(await boundedBody(request))}catch{return new Response('Invalid request',{status:400})}
  const name=typeof item.name==='string'?item.name.trim():'',email=typeof item.email==='string'?item.email.trim():'',message=typeof item.message==='string'?item.message.trim():'';
  if(!name||name.length>100||/[\r\n]/.test(name)||email.length>254||!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)||message.length<10||message.length>5000)return new Response('Invalid request',{status:400});
  try{await env.EMAIL.send({from:env.CONTACT_FROM,to:env.CONTACT_TO,replyTo:email,subject:'IbrahimBlog contact message',text:`Name: ${name}\nEmail: ${email}\n\n${message}`});return new Response('Accepted',{status:202})}catch{return new Response('Delivery unavailable',{status:502})}
}};
