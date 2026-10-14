'use strict';
// Only the browser that starts the room loads the Python runtime.
window.AphelionBrowserHost=class {
  static openDB(){return new Promise((resolve,reject)=>{const r=indexedDB.open('aphelion-games',1);r.onupgradeneeded=()=>r.result.createObjectStore('games',{keyPath:'id'});r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(Error('Browser storage is unavailable. Enable storage to host a saved game.'));});}
  static async list(){const db=await this.openDB();try{return await new Promise((resolve,reject)=>{const r=db.transaction('games').objectStore('games').getAll();r.onsuccess=()=>resolve(r.result.sort((a,b)=>b.updated.localeCompare(a.updated)));r.onerror=()=>reject(r.error);});}finally{db.close();}}
  static async start({savedId=null,imported=null,onProgress,onFatal}={}){
    const games=savedId?await this.list():[],saved=games.find(g=>g.id===savedId);
    if(savedId&&!saved)throw Error('Saved game was not found in this browser.');
    const host=new this();host.game=saved||{id:crypto.randomUUID(),name:'Expedition '+new Date().toLocaleString(),updated:new Date().toISOString(),save:imported};host.onFatal=onFatal;
    if(!navigator.locks)throw Error('This browser cannot safely lock saved games. Use a current Chrome, Edge, Firefox or Safari browser.');
    await new Promise((resolve,reject)=>{navigator.locks.request('aphelion-host:'+host.game.id,{ifAvailable:true},async lock=>{if(!lock){reject(Error('This saved game is already hosted in another tab. Close that host first.'));return;}resolve();await new Promise(r=>host.unlock=r);}).catch(reject);});
    host.worker=new Worker(new URL('host-worker.mjs',document.baseURI),{type:'module'});host.pending=new Map();host.persist=Promise.resolve();
    host.worker.onmessage=({data})=>{
      if(data.progress){onProgress?.(data.progress);return;}
      const request=host.pending.get(data.id);if(!request)return;host.pending.delete(data.id);clearTimeout(request.timer);
      if(data.error){request.reject(Error(data.error));return;}
      if(!data.result.save){request.resolve(data.result);return;}
      host.persist=host.persist.then(async()=>{if(data.result.save){host.game.save=data.result.save;await host.save();}return data.result;});
      host.persist.then(request.resolve,error=>{host.failed=true;onFatal?.('Game paused: browser save failed. Export your history before closing this page. '+error.message);request.reject(error);});
    };
    host.worker.onerror=event=>{const error=Error(event.message||'Game rules could not load');for(const r of host.pending.values()){clearTimeout(r.timer);r.reject(error);}host.pending.clear();host.failed=true;onFatal?.(error.message);};
    try{await host.request({type:'init',saved:host.game.save},120000);return host;}catch(error){host.close();throw error;}
  }
  async save(){const db=await this.constructor.openDB();try{await new Promise((resolve,reject)=>{const tx=db.transaction('games','readwrite');this.game.updated=new Date().toISOString();tx.objectStore('games').put(this.game);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error||Error('Save cancelled'));});}finally{db.close();}}
  request(message,timeout=60000){const id=crypto.randomUUID();return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{this.pending.delete(id);this.failed=true;this.onFatal?.('Game paused: the rules engine did not respond. Reload and resume the saved game.');reject(Error('Rules engine timed out'));},timeout);this.pending.set(id,{resolve,reject,timer});this.worker.postMessage({id,...message});});}
  async api(path,body){if(this.failed&&path!=='/api/export')throw Error('Hosting is paused; export your history and reload.');return (await this.request({path,body:body||{}})).packet;}
  close(){this.worker?.terminate();this.unlock?.();}
};
