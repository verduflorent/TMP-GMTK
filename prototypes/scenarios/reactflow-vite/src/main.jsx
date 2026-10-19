import React, { useState, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import { ReactFlow, Background, Controls, MiniMap, Handle, Position, MarkerType, ReactFlowProvider, useReactFlow } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './style.css';

const initialScenes = [
  {id:'s1', title:'Arrivée au complexe', position:{x:250,y:20}, order:1, icons:'▤ ▧'},
  {id:'s2', title:'Rencontrer Nadia', position:{x:10,y:240}, order:2, icons:'◉ ✎'},
  {id:'s3', title:'Explorer les lieux', position:{x:490,y:240}, order:3, icons:'▤ ⚔'},
  {id:'s4', title:'Bureau du directeur', position:{x:250,y:460}, order:4, icons:'◉'}
];
const initialLinks = [
  {id:'t1',source:'s1',target:'s2',label:'Parler à Nadia'},
  {id:'t2',source:'s1',target:'s3',label:'Explorer'},
  {id:'t3',source:'s2',target:'s4',label:'Voir le directeur'},
  {id:'t4',source:'s3',target:'s4',label:'Rejoindre le bureau'}
];
const nextId=(prefix,items)=>prefix+(Math.max(0,...items.map(x=>Number(x.id.replace(/\D/g,''))||0))+1);
function SceneNode({data,selected}) {
 return <div className={'scene'+(selected?' selected':'')}>
  <Handle type="target" position={Position.Top} isConnectable={true}/>
  <div className="scene-header"><span>SCÈNE {String(data.order).padStart(2,'0')}</span><span>TMP / MJ</span></div>
  <div className="scene-title">{data.title}</div>
  <div className="scene-bottom"><span>{data.icons||'▤'}</span><button className="nodrag" onClick={()=>data.open(data.id)}>Ouvrir</button></div>
  <Handle type="source" position={Position.Bottom} isConnectable={true}/>
 </div>;
}
const nodeTypes={scene:SceneNode};
function Board(){
 const [scenes,setScenes]=useState(initialScenes);
 const [links,setLinks]=useState(initialLinks);
 const [selected,setSelected]=useState('s1');
 const [selectedLink,setSelectedLink]=useState(null);
 const [source,setSource]=useState(null);
 const [reader,setReader]=useState(false);
 const [status,setStatus]=useState('Prototype local · aucun enregistrement serveur');
 const flow=useReactFlow();
 const choose=useCallback(id=>{setSelected(id);setSelectedLink(null);setReader(false);if(id)requestAnimationFrame(()=>flow.setCenter((scenes.find(s=>s.id===id)?.position.x??0)+120,(scenes.find(s=>s.id===id)?.position.y??0)+75,{zoom:Math.max(flow.getZoom(),.7),duration:300}))},[flow,scenes]);
 const nodes=scenes.map(s=>({id:s.id,type:'scene',position:s.position,selected:selected===s.id,data:{...s,open:id=>{choose(id);setReader(true)}}}));
 const edges=links.map(t=>({id:t.id,source:t.source,target:t.target,label:t.label,type:'smoothstep',markerEnd:{type:MarkerType.ArrowClosed,color:'#b72530'},style:{stroke:'#b72530',strokeWidth:2},labelStyle:{fill:'#fff'},labelBgStyle:{fill:'#26303e',fillOpacity:1}}));
 const createLink=(a,b)=>{if(!scenes.some(s=>s.id===a)||!scenes.some(s=>s.id===b))return;setLinks(v=>[...v,{id:nextId('t',v),source:a,target:b,label:'Continuer'}]);setSource(null);setStatus('Transition créée')};
 const onConnect=useCallback(c=>{if(c.source&&c.target)createLink(c.source,c.target)},[links,scenes]);
 const save=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({scenes,transitions:links},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='scenario-reactflow.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
 const load=async e=>{const f=e.target.files?.[0];if(!f)return;try{const d=JSON.parse(await f.text());if(!Array.isArray(d.scenes)||!Array.isArray(d.transitions)||d.scenes.length>500||d.transitions.length>1000)throw Error('Format ou taille invalide');const ids=new Set(d.scenes.map(s=>s.id));if(ids.size!==d.scenes.length||d.scenes.some(s=>!Number.isFinite(s.position?.x)||!Number.isFinite(s.position?.y))||d.transitions.some(t=>!ids.has(t.source)||!ids.has(t.target)))throw Error('Références invalides');setScenes(d.scenes);setLinks(d.transitions);setSelected(null);setSelectedLink(null);setTimeout(()=>flow.fitView({padding:.2}),80);setStatus('Import terminé')}catch(err){setStatus('Erreur : '+err.message)}e.target.value=''};
 const current=scenes.find(s=>s.id===selected);
 const edge=links.find(t=>t.id===selectedLink);
 return <div className="app"><header><h1>MES SCÉNARIOS / REACT FLOW</h1>
 <button onClick={()=>{const id=nextId('s',scenes);setScenes(v=>[...v,{id,title:'Nouvelle scène',order:v.length+1,position:{x:180+v.length*35,y:120+v.length*35},icons:'▤'}]);choose(id)}}>+ Scène</button>
 <button onClick={()=>{setSource(selected);setStatus(selected?'Clique une destination':'Sélectionne d’abord une scène source')}}>Relier deux scènes</button>
 <button onClick={()=>flow.zoomIn()}>+</button><button onClick={()=>flow.zoomOut()}>−</button><button onClick={()=>flow.fitView({padding:.2})}>Cadrer</button>
 <button onClick={save}>Exporter JSON</button><label className="import-button">Importer JSON<input type="file" accept=".json" hidden onChange={load}/></label><small>{status}</small></header>
 <div className="workspace"><main><ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView onConnect={onConnect}
 onNodesChange={changes=>setScenes(prev=>prev.map(s=>{const c=changes.find(c=>c.id===s.id&&c.type==='position'&&c.position);return c?{...s,position:c.position}:s}))}
 onNodeClick={(_,node)=>{if(source)createLink(source,node.id);else choose(node.id)}}
 onEdgeClick={(_,e)=>{setSelectedLink(e.id);setSelected(null)}}
 onPaneClick={()=>setSource(null)} connectionRadius={45} connectOnClick={true} nodesConnectable={true} minZoom={.15} maxZoom={2.5}>
 <Background color="#344558" gap={22}/><Controls/><MiniMap pannable zoomable/></ReactFlow></main>
 <aside><h2>{reader?'Lecture de scène':'Éditeur de scène'}</h2><p>Sélectionne une carte. Tire une flèche depuis sa poignée rouge inférieure vers une autre carte, ou utilise « Relier deux scènes ».</p>
 <div className="scene-nav"><button disabled={!selected||scenes.findIndex(s=>s.id===selected)<=0} onClick={()=>{const sorted=[...scenes].sort((a,b)=>a.order-b.order);const i=sorted.findIndex(s=>s.id===selected);if(i>0)choose(sorted[i-1].id)}}>← Précédente</button><button disabled={!selected||[...scenes].sort((a,b)=>a.order-b.order).findIndex(s=>s.id===selected)>=scenes.length-1} onClick={()=>{const sorted=[...scenes].sort((a,b)=>a.order-b.order);const i=sorted.findIndex(s=>s.id===selected);if(i>=0&&i<sorted.length-1)choose(sorted[i+1].id)}}>Suivante →</button></div><label>Scène</label><select value={selected||''} onChange={e=>choose(e.target.value)}><option value="">— Choisir —</option>{scenes.map(s=><option key={s.id} value={s.id}>{s.order} · {s.title}</option>)}</select>
 {current&&reader&&<section className="reader"><h3>{current.title}</h3><p>Prévisualisation de scène (rubriques à venir).</p><h4>Transitions</h4>{links.filter(t=>t.source===current.id).map(t=><button key={t.id} onClick={()=>{choose(t.target);setReader(true)}}>{t.label} →</button>)}<button onClick={()=>setReader(false)}>Modifier</button></section>}
 {!reader&&current&&<section key={current.id}><label>Titre</label><input defaultValue={current.title} onBlur={e=>setScenes(v=>v.map(s=>s.id===current.id?{...s,title:e.target.value}:s))}/><label>Ordre</label><input type="number" defaultValue={current.order} onBlur={e=>setScenes(v=>v.map(s=>s.id===current.id?{...s,order:Number(e.target.value)}:s))}/><button onClick={()=>{setScenes(v=>v.filter(s=>s.id!==current.id));setLinks(v=>v.filter(t=>t.source!==current.id&&t.target!==current.id));choose(null)}}>Supprimer la scène</button><h3>Transitions</h3>{links.filter(t=>t.source===current.id).map(t=><button key={t.id} onClick={()=>{setSelectedLink(t.id);setSelected(null)}}>{t.label} →</button>)}</section>}
 {edge&&<section key={edge.id}><h3>Transition</h3><label>Libellé</label><input defaultValue={edge.label} onBlur={e=>setLinks(v=>v.map(t=>t.id===edge.id?{...t,label:e.target.value}:t))}/><label>Destination</label><select value={edge.target} onChange={e=>setLinks(v=>v.map(t=>t.id===edge.id?{...t,target:e.target.value}:t))}>{scenes.map(s=><option key={s.id} value={s.id}>{s.title}</option>)}</select><button onClick={()=>{setLinks(v=>v.filter(t=>t.id!==edge.id));setSelectedLink(null)}}>Supprimer la flèche</button></section>}
 <p className="hint">Prototype expérimental, aucune connexion à Django ou Neon.</p></aside></div></div>;
}
createRoot(document.getElementById('root')).render(<ReactFlowProvider><Board/></ReactFlowProvider>);
