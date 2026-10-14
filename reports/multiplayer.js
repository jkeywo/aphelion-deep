'use strict';
const $=id=>document.getElementById(id), names={engineer:'Fabrication Lead',lead:'Lead Ecologist',systems:'Systems Ecologist'};
const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const hostMode=document.documentElement.dataset.host!=='guest'&&location.protocol!=='file:'&&!new URLSearchParams(location.search).has('guest');
let hostToken=null,invite=null,peer=null,link=null,roomCode='',view=null,previous=null,selected='C',connected=false,hosting=false,joinDetails=null,lastSequence=-1;
let queue=Promise.resolve(), assetRunning=0;
const connections=new Map(),pending=new Map(),images=new Map(),assetQueue=[],assetPending=new Set();
function error(message){$('error').hidden=false;$('error').textContent=message;}
function clearError(){$('error').hidden=true;}
function confirmAction(message){return new Promise(resolve=>{const dialog=$('confirm-action');$('confirm-message').textContent=message;const finish=value=>{dialog.close();resolve(value);};$('confirm-yes').onclick=()=>finish(true);$('confirm-no').onclick=()=>finish(false);dialog.oncancel=e=>{e.preventDefault();finish(false);};dialog.showModal();});}
function status(text){$('connection').textContent=text;}
function cacheKey(){return 'aphelion-multiplayer:'+roomCode+':'+$('role').value;}
function stored(){try{return localStorage.getItem(cacheKey())||'';}catch{return '';}}
function remember(token){try{localStorage.setItem(cacheKey(),token);}catch{}}
async function api(path,body){const r=await fetch(path,body?{method:'POST',headers:{'Content-Type':'application/json','X-Host-Token':hostToken},body:JSON.stringify(body)}:{});const v=await r.json();if(!r.ok)throw Error(v.error||'Host request failed');return v;}
function deliver(packet){
  if(packet.host)acceptView(packet.host);
  for(const id of packet.departed||[]){const conn=connections.get(id);if(conn){conn.send({type:'released'});conn.close();}}
  for(const [id,v]of Object.entries(packet.views||{})){const conn=connections.get(id);if(conn?.open)conn.send({type:'state',view:v});}
}
function bridge(id,message){const operation=queue.then(async()=>{const packet=await api('/api/message',{peer:id,message});deliver(packet);return packet.reply;});queue=operation.catch(()=>{});return operation;}
function receive(message){
  if(!message||typeof message!=='object')return;
  if(message.type==='released'){connected=false;view=null;lastSequence=-1;$('game').hidden=true;$('lobby').hidden=false;error('The host released your seat. Choose an available role to rejoin.');return;}
  if(message.type==='state'){acceptView(message.view);return;}
  const task=pending.get(message.id);if(!task)return;pending.delete(message.id);clearTimeout(task.timer);
  if(message.error)task.reject(Error(message.error));else task.resolve(message.reply);
}
function send(message){
  if(hosting)return bridge('host',message);
  if(!link?.open)return Promise.reject(Error('Disconnected. Reconnect to the host before choosing an action.'));
  const id=crypto.randomUUID();
  return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending.delete(id);reject(Error('No reply from host. Check the connection, then reconnect.'));},25000);pending.set(id,{resolve,reject,timer});link.send({id,message});});
}
function networkOptions(){const text=$('network').value.trim();const options=text?JSON.parse(text):{};if(!options||Array.isArray(options)||typeof options!=='object')throw Error('Connection settings must be a JSON object');return options;}
async function startPeer(){
  if(peer&&!peer.destroyed){peer.destroy();}
  peer=new Peer(undefined,networkOptions());
  peer.on('error',e=>error('Connection: '+e.message+' If peers cannot connect across networks, configure a TURN service.'));
  peer.on('disconnected',()=>{status('Signaling connection lost; reconnecting…');if(!peer.destroyed)peer.reconnect();});
  return new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('PeerJS signaling could not be reached. Check internet or use a custom PeerServer.')),20000);peer.once('open',id=>{clearTimeout(timer);resolve(id);});peer.once('error',e=>{clearTimeout(timer);reject(e);});});
}
async function createRoom(){
  try{clearError();$('create').disabled=true;const boot=await api('/api/host');hostToken=boot.token;const started=await api('/api/start-room',{});invite=started.reply.invite;acceptView(started.host);status('Opening room…');const id=await startPeer();hosting=true;connected=true;roomCode=id+'.'+invite;
    $('room-code').textContent=roomCode;$('join-link').href='https://jkeywo.github.io/aphelion-deep/#room='+encodeURIComponent(roomCode);$('host-room').hidden=false;$('room').hidden=false;$('code-input').hidden=true;$('create').hidden=true;status('Hosting · waiting for human crew');
    peer.on('connection',conn=>{
      const remoteId='remote:'+conn.peer;
      if(connections.size>=8||connections.has(remoteId)){conn.close();return;}
      connections.set(remoteId,conn);
      conn.on('data',async packet=>{if(connections.get(remoteId)!==conn||!packet||typeof packet.id!=='string'||packet.id.length>80)return;
        try{if(JSON.stringify(packet).length>66000)throw Error('Message too large');const reply=await bridge(remoteId,packet.message);if(conn.open)conn.send({id:packet.id,reply});}
        catch(e){if(conn.open)conn.send({id:packet.id,error:e.message});}
      });
      const closed=()=>{if(connections.get(remoteId)!==conn)return;connections.delete(remoteId);api('/api/disconnect',{peer:remoteId}).then(deliver).catch(e=>error(e.message));};
      conn.on('close',closed);conn.on('error',closed);
    });
    render();
  }catch(e){$('create').disabled=false;error(e.message);}
}
async function joinRoom(){
  try{clearError();$('join').disabled=true;
    if(hostMode&&!hosting)throw Error('Create the room first, then claim your role. You can also leave all three roles to guests.');
    if(!hosting){lastSequence=-1;roomCode=$('join-code').value.trim();const dot=roomCode.lastIndexOf('.');if(dot<1)throw Error('Paste the full room code from the host');const hostId=roomCode.slice(0,dot);invite=roomCode.slice(dot+1);status('Connecting to host…');await startPeer();
      link=peer.connect(hostId,{reliable:true,serialization:'binary',label:'aphelion-v1'});link.on('data',receive);
      link.on('close',()=>{connected=false;status('Disconnected · your seat is reserved');$('lobby').hidden=false;$('reconnect').hidden=false;render();});
      link.on('error',e=>error(e.message));
      await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Unable to reach the host. Check the room code or configure TURN in Connection settings.')),20000);link.once('open',()=>{clearTimeout(timer);resolve();});link.once('error',e=>{clearTimeout(timer);reject(e);});});
    }
    const message={type:'join',protocol:1,invite,name:$('name').value.trim(),role:$('role').value,resume:stored()};
    const reply=await send(message);remember(reply.resume);joinDetails=message;connected=true;$('lobby').hidden=true;$('reconnect').hidden=true;status('Connected · '+names[view?.role||message.role]);render();
  }catch(e){error(e.message);$('reconnect').hidden=false;}finally{$('join').disabled=false;}
}
function acceptView(next){
  if(!next||next.protocol!==1||next.sequence<lastSequence)return;
  const old=view,changed=!old||next.sequence!==lastSequence||next.role!==old.role;
  if(old&&next.node!==old.node)previous=old;
  view=next;lastSequence=next.sequence;
  if(changed){if(old?.role&&!view.role)$('lobby').hidden=false;if(view.role&&old?.state.players[view.role]?.at!==view.state.players[view.role]?.at)selected=view.state.players[view.role].at||selected;render();}
}
async function choose(type,value){if(!view?.prompt)return;clearError();try{await send({type,value,node:view.node,key:view.prompt.key,revision:view.revision});}catch(e){error(e.message);try{await send({type:'sync'});}catch{}}}
function cardActions(key){const p=view.prompt;if(!p)return [];
  if(p.kind==='table')return p.options.filter(o=>o.value&&typeof o.value==='object'&&(o.value.card===key||o.value.target===key));
  if(p.key.split(':')[1]==='upkeep-card')return p.options.filter(o=>o.value===key);
  if(p.kind==='table-upkeep')return p.options.filter(o=>Array.isArray(o.value)&&o.value[0]===key);
  return p.cards?.includes(key)?p.options:[];
}
function requestImage(key,face){const id=key+':'+face;if(images.has(id)||assetPending.has(id)||!connected||!view.role)return;assetPending.add(id);assetQueue.push({key,face,id});pumpAssets();}
function pumpAssets(){while(assetRunning<3&&assetQueue.length){const task=assetQueue.shift();assetRunning++;send({type:'asset',card:task.key,face:task.face}).then(reply=>{images.set(task.id,reply.image);for(const img of document.querySelectorAll('img[data-image]'))if(img.dataset.image===task.id)img.src=reply.image;}).catch(()=>{}).finally(()=>{assetPending.delete(task.id);assetRunning--;pumpAssets();});}}
function picture(key){const c=view.cards[key],img=el('img');if(!c)return img;img.alt=c.name+' — '+c.face;img.dataset.image=key+':'+c.face;const cached=images.get(img.dataset.image);if(cached)img.src=cached;else requestImage(key,c.face);return img;}
function zoom(img){if(!img.getAttribute('src'))return;$('zoom').querySelector('img').src=img.src;$('zoom').querySelector('img').alt=img.alt;$('zoom').showModal();}
function card(key,{info,deck=false,drawn=false,owner}={}){const c=view.cards[key];if(!c)return el('span');const box=el('article','card'+(deck?' deck':'')+(drawn?' drawn':''));box.dataset.card=key;
  if(previous&&((info&&!same(info,previous.state.locations[key[0]]?.cards[key]))||(owner===view.role&&!previous.state.players[owner].hand.includes(key))))box.classList.add('changed');
  const b=el('button','picture'),img=picture(key);b.setAttribute('aria-label','Inspect '+c.name);b.append(img);b.onclick=()=>zoom(img);
  let direct=null;if(deck&&view.prompt?.kind==='table'&&view.prompt.location===key[0])direct=view.prompt.options.find(o=>o.value==='reveal');if(drawn&&view.prompt?.kind==='card-face')direct=view.prompt.options[0];
  if(direct?.enabled&&connected){b.onclick=()=>choose('action',direct.value);b.setAttribute('aria-label',direct.label+': '+c.name);}
  box.append(b,el('strong','',c.name),el('small','',c.face==='back'?'Back up':'Front up'));
  if(owner)box.append(el('small','',names[owner]));if(info?.track)box.append(el('span','track',info.track+': '+info.value+' / 5'));
  if(info?.attached_to)box.append(el('small','','Tucked under '+view.cards[info.attached_to]?.name+' · '+info.choice));
  const meta=view.table[key];if(meta?.requirement)box.append(el('small','',meta.requirement));
  for(const option of direct?[direct]:cardActions(key)){if(!option.enabled)continue;const action=el('button','action',option.label);action.disabled=!connected;action.onclick=()=>choose('action',option.value);box.append(action);}
  if(owner===view.role)for(const option of view.prompt?.trades||[]){if(option.value.card!==key)continue;const action=el('button','action',option.label);action.disabled=!connected||!view.ready;action.onclick=()=>choose('trade',option.value);box.append(action);}
  return box;
}
function renderOptions(){const area=$('options');area.replaceChildren();const p=view.prompt;if(!p)return;
  if(p.kind==='assignments'){
    const board=el('div','destinations');board.style.width='100%';
    for(const location of p.locations){const site=el('section','dropzone');site.dataset.location=location;site.append(el('h3','',view.state.locations[location].name));
      for(const [role,player]of Object.entries(view.state.players)){if((view.assignments[role]||player.at)!==location)continue;const token=el('div','token',names[role]+(view.assignments[role]?' · ready':''));token.draggable=role===view.role;token.ondragstart=e=>e.dataTransfer.setData('text/plain',role);site.append(token);}
      site.ondragover=e=>{e.preventDefault();site.classList.add('over');};site.ondragleave=()=>site.classList.remove('over');site.ondrop=e=>{e.preventDefault();site.classList.remove('over');if(e.dataTransfer.getData('text/plain')===view.role)choose('assign',location);};
      const button=el('button','','Go here');button.disabled=!view.role||!view.ready||!connected;button.onclick=()=>choose('assign',location);site.append(button);
      if(view.state.locations[location].top)site.append(card(view.state.locations[location].top));board.append(site);
    }area.append(board,el('p','hint','Only your own player can move. All destinations apply together when the three players have chosen.'));return;
  }
  const list=p.kind==='dilemma'?p.choices.map(c=>({...c,...p.options.find(o=>same(o.value,c.value)),description:c.consequence})):p.options;
  for(const option of list){const item=el('div','choice'+(view.role&&same(view.votes[view.role],option.value)?' voted':'')),button=el('button','',option.label);
    button.disabled=!option.enabled||!connected;button.onclick=()=>choose('action',option.value);item.append(button);
    if(option.description)item.append(el('p','',option.description));
    if(option.blocked)item.append(el('small','','Unavailable · '+option.blocked));
    else if(option.unanimous)item.append(el('small','','Agreement: '+(option.eligible||[]).filter(r=>r in view.votes&&same(view.votes[r],option.value)).length+' / '+option.eligible.length));
    else if(!option.enabled&&option.eligible?.length)item.append(el('small','','For '+option.eligible.map(r=>names[r]).join(', ')));
    area.append(item);
  }
}
function render(){if(!view)return;hideHover();$('room').hidden=false;$('game').hidden=false;$('status').textContent='Turn '+view.turn+' · '+view.state.phase+' · Reactor '+view.state.reactor+' · History #'+view.node;
  const roster=$('roster');roster.replaceChildren();for(const role of Object.keys(names)){const member=view.roster.find(m=>m.role===role),seat=el('div','seat'+(role===view.role?' mine':''));seat.append(el('strong','',names[role]),el('div',member?.online?'online':'offline',member?member.name+(member.online?' · connected':' · disconnected'):'Waiting for a player'));
    if(hosting&&member){const b=el('button','','Release seat');b.onclick=async()=>{if(await confirmAction('Release '+names[role]+' so another person can join?'))try{deliver(await api('/api/release',{role}));}catch(e){error(e.message);}};seat.append(b);}roster.append(seat);}
  $('decision').textContent=view.prompt?.title||(view.status==='complete'?'Three turns complete':'This route is blocked');$('note').textContent=view.prompt?.note||view.error||'';$('waiting').textContent=!view.ready?'Waiting for all three human players to connect.':!view.role?'Host view · join a role above to play.':'You control '+names[view.role]+'.';renderOptions();
  const tabs=$('locations');tabs.replaceChildren();for(const [key,loc]of Object.entries(view.state.locations)){const b=el('button',selected===key?'active':'',loc.name+(previous&&!same(loc,previous.state.locations[key])?' • changed':''));b.onclick=()=>{selected=key;render();};tabs.append(b);}
  const area=$('location'),loc=view.state.locations[selected];area.replaceChildren(el('h2','',loc.name),el('p','muted','Present: '+Object.entries(view.state.players).filter(([_,p])=>p.at===selected).map(([p])=>names[p]).join(', ')));
  for(const n of view.state.control_notes||[])if(n.location===selected)area.append(el('p','track','For Control: '+n.message));
  const stats=el('div','stats');for(const [label,values]of [['Resource',loc.resources],['Capability',loc.capabilities]])for(const [k,v]of Object.entries(values))stats.append(el('span','',label+' · '+k+': '+v));area.append(stats);
  const zone=(title,keys,options={})=>{const z=el('section','zone');z.append(el('h3','',title));const row=el('div','cards');for(const k of keys)row.append(card(k,{info:loc.cards[k],...options}));if(!keys.length)row.append(el('p','muted','None'));z.append(row);return z;};
  const drawn=view.state.drawn_card,deck=drawn?.key[0]===selected?zone('Card being read',[drawn.key],{drawn:true}):zone('Deck · '+loc.remaining+' remaining',loc.top?[loc.top]:[],{deck:true});
  const top=el('div','deck-row');top.append(deck,zone('Beside the deck',loc.set_aside));area.append(top,zone('In play',Object.keys(loc.cards)),zone('Recipes',loc.recipes));
  const discard=el('details');discard.append(el('summary','','Discard · '+loc.discard.length),zone('',loc.discard));area.append(discard);
  const hand=$('hand');hand.replaceChildren(el('h2','',view.role?names[view.role]:'Your hand'));if(view.role){const player=view.state.players[view.role];hand.append(el('p','hint','Give non-role cards to another player at your location.'));const own=el('div','cards');for(const k of player.hand)own.append(card(k,{owner:view.role}));if(!player.hand.length)own.append(el('p','muted','No cards in hand yet.'));hand.append(own);
    for(const [role,other]of Object.entries(view.state.players))if(role!==view.role&&other.at===player.at){hand.append(el('h3','',names[role]+' · shared here'));const row=el('div','cards');for(const k of other.hand)row.append(card(k,{owner:role}));hand.append(row);}
  }else hand.append(el('p','muted','Join a role to see your hand and receive card images.'));
  const history=$('history');history.replaceChildren();for(const n of view.history){const b=el('button',n.id===view.node?'current':'','#'+n.id+' · '+n.label);b.disabled=!hosting;b.onclick=async()=>{if(n.id===view.node)return;if(await confirmAction('Rewind everyone to history point #'+n.id+'? Pending votes and destinations will be cleared.'))try{deliver(await api('/api/rewind',{node:n.id}));}catch(e){error(e.message);}};history.append(b);}
  const events=$('events');events.replaceChildren();for(const text of view.events)events.append(el('p','',text));
}
let hoverImage=null,alt=false;
function hideHover(){const p=$('hover');if(p.matches(':popover-open'))p.hidePopover();p.hidden=true;}
function preview(){if(!alt||!hoverImage?.isConnected||!hoverImage.getAttribute('src')){hideHover();return;}const p=$('hover');p.querySelector('img').src=hoverImage.src;p.querySelector('img').alt=hoverImage.alt;p.hidden=false;if(!p.matches(':popover-open'))p.showPopover();}
document.addEventListener('pointerover',e=>{hoverImage=e.target.closest?.('.card')?.querySelector('img');alt=e.altKey;preview();});document.addEventListener('pointerout',e=>{hoverImage=e.relatedTarget?.closest?.('.card')?.querySelector('img');preview();});
document.addEventListener('keydown',e=>{if(e.key==='Alt'){e.preventDefault();alt=true;preview();}if(e.key==='Escape')hideHover();});document.addEventListener('keyup',e=>{if(e.key==='Alt'){alt=false;hideHover();}});document.addEventListener('click',e=>{if(e.altKey&&e.target.closest('.card')){e.preventDefault();e.stopImmediatePropagation();}},true);window.addEventListener('blur',()=>{alt=false;hideHover();});document.addEventListener('scroll',hideHover,true);
$('close-zoom').onclick=()=>$('zoom').close();$('create').onclick=createRoom;$('join').onclick=joinRoom;$('reconnect').onclick=()=>{$('lobby').hidden=false;joinRoom();};
$('copy-code').onclick=()=>navigator.clipboard.writeText(roomCode).catch(()=>error('Select the room code above and copy it.'));
$('export').onclick=async()=>{try{const data=await api('/api/export'),url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'})),a=el('a');a.href=url;a.download='aphelion-multiplayer-history.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){error(e.message);}};
$('host-start').hidden=!hostMode;
setInterval(()=>{if(connected&&view?.role)send({type:'sync'}).catch(e=>{connected=false;status('Connection lost · reconnect to resume');$('lobby').hidden=false;$('reconnect').hidden=false;error(e.message);render();});},10000);


$('copy-invite').onclick=()=>navigator.clipboard.writeText($('join-link').href).catch(()=>error('Copy the Open player page link instead.'));
if(!hostMode){const code=new URLSearchParams(location.hash.slice(1)).get('room');if(code)$('join-code').value=code;}
