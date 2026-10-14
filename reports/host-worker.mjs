// The authoritative rules run off the UI thread in the host's browser.
import {loadPyodide} from 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs';
let python,host,serial=Promise.resolve();
const hash=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
async function load(saved){
  self.postMessage({progress:'Loading game rules…'});
  python=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/'});
  const response=await fetch(new URL('browser-bundle.json',import.meta.url));
  if(!response.ok)throw Error('Could not download the game rules. Reload and try again.');
  const bundle=await response.json();
  const hashes=Object.fromEntries(Object.keys(bundle.files).sort().map(k=>[k,bundle.files[k].sha256]));
  if(await hash(new TextEncoder().encode(JSON.stringify(hashes)))!==bundle.binding)throw Error('Rules binding mismatch');
  for(const [path,file]of Object.entries(bundle.files)){
    if(!/^(aphelion_deep\/[a-z_]+\.py|aphelion_deep\/data\/[a-z]+\.json|reports\/cards\/manifest\.json|reviewed\.json)$/.test(path))throw Error('Invalid rules bundle path');
    const bytes=new TextEncoder().encode(file.text);
    if(await hash(bytes)!==file.sha256)throw Error('Rules bundle fingerprint mismatch');
    python.FS.mkdirTree('/game/'+(path.includes('/')?path.slice(0,path.lastIndexOf('/')):''));
    python.FS.writeFile('/game/'+path,bytes);
  }
  python.globals.set('saved_json',JSON.stringify(saved));
  python.globals.set('rules_binding',bundle.binding);
  await python.runPythonAsync(`
import sys, json
sys.path.insert(0, '/game')
from aphelion_deep.browser_runtime import BrowserHost
browser_host = BrowserHost('/game', rules_binding, json.loads(saved_json))
`);
  self.postMessage({progress:'Opening your game…'});
}
async function execute(message){
  if(message.type==='init'){await load(message.saved||null);return {ready:true};}
  python.globals.set('request_json',JSON.stringify(message));
  const packet=JSON.parse(python.runPython(`
request = json.loads(request_json)
packet = browser_host.dispatch(request['path'], request.get('body'))
json.dumps({'packet': packet, 'save': browser_host.session.data if request['path'] not in ('/api/host', '/api/export', '/api/facilitator-asset') and request.get('body', {}).get('message', {}).get('type') not in ('asset', 'sync') else None})
`));
  const asset=packet.packet.reply;
  if(asset?.asset){
    const response=await fetch(new URL('cards/'+encodeURIComponent(asset.asset),import.meta.url));
    if(!response.ok)throw Error('Card image could not be loaded');
    const bytes=new Uint8Array(await response.arrayBuffer());
    if(await hash(bytes)!==asset.sha256)throw Error('Card image fingerprint mismatch');
    let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
    asset.image='data:image/webp;base64,'+btoa(binary);delete asset.asset;delete asset.sha256;
  }
  return packet;
}
self.onmessage=event=>{
  const message=event.data;
  serial=serial.then(async()=>{try{self.postMessage({id:message.id,result:await execute(message)});}catch(error){self.postMessage({id:message.id,error:error.message});}});
};
