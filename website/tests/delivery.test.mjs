import {test} from 'node:test';import assert from 'node:assert/strict';import worker from '../../contact-worker/worker.mjs';import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const data={name:'A reader',email:'reader@example.com',message:'A real looking but fictional message.'};
const req=(token='secret',payload=data)=>new Request('https://worker.example/',{method:'POST',headers:{authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify(payload)});
test('rejects unauthorized caller and does not send',async()=>{let sent=0;const env={CONTACT_TOKEN:'secret',CONTACT_FROM:'from@example.com',CONTACT_TO:'to@example.com',EMAIL:{send:async()=>sent++}};assert.equal((await worker.fetch(req('wrong'),env)).status,401);assert.equal(sent,0)});
test('authorized request uses configured recipients',async()=>{let sent;const env={CONTACT_TOKEN:'secret',CONTACT_FROM:'from@example.com',CONTACT_TO:'to@example.com',EMAIL:{send:async x=>sent=x}};assert.equal((await worker.fetch(req(),env)).status,202);assert.equal(sent.to,'to@example.com');assert.equal(sent.replyTo,data.email)});
test('delivery failure returns error',async()=>{const env={CONTACT_TOKEN:'secret',CONTACT_FROM:'from@example.com',CONTACT_TO:'to@example.com',EMAIL:{send:async()=>{throw Error('failed')}}};assert.equal((await worker.fetch(req(),env)).status,502)});
