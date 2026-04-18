// Jeff — clickable prototype. Self-contained.
// State-driven navigation: projects → work_units → runs → layer details.
// Persists active selections in localStorage.

const mono = 'JetBrains Mono, ui-monospace, monospace';
const sans = 'IBM Plex Sans, system-ui, sans-serif';

const THEMES = {
  light: {
    bg:'#f5f2ec', surface:'#faf8f3', panel:'#ffffff', rail:'#ede8dd',
    border:'#e0dacb', borderStrong:'#c9c1ae',
    text:'#1a1816', muted:'#6b6558', faint:'#9a9283',
    approved:'#5c7a4c', blocked:'#a8553a', pending:'#c48a3a', degraded:'#a87c3a',
    canonical:'#1a1816', support:'#8b7355', derived:'#7a7064', memory:'#8578a0',
  },
  dark: {
    bg:'#17150f', surface:'#1f1c15', panel:'#26221a', rail:'#1a1712',
    border:'#332e24', borderStrong:'#4a4335',
    text:'#ebe4d3', muted:'#9a9283', faint:'#6b6558',
    approved:'#8ab06a', blocked:'#d07860', pending:'#e0a75a', degraded:'#c89860',
    canonical:'#ebe4d3', support:'#c9a878', derived:'#a89d8a', memory:'#b0a0c8',
  },
};
const ACCENT = '#d4a574';

// ─── data ──────────────────────────────────────────────────

const initialState = {
  projects: [
    {
      id:'jeff', label:'jeff', sub:'personal work system',
      workUnits:[
        {id:'define-architecture', label:'define canonical ARCHITECTURE.md',
          runs:[
            {id:'#r-0147', label:'draft Memory section', status:'active', ts:'4m ago', operatorMsg:'Draft the Memory section of ARCHITECTURE.md using the committed memory spec. Keep the distinction between memory and canonical state explicit.'},
            {id:'#r-0146', label:'continue draft',       status:'blocked', ts:'17m ago', operatorMsg:'Continue the draft from where we stopped.'},
            {id:'#r-0145', label:'research workflow-as-truth', status:'done', ts:'1h ago', operatorMsg:'Research whether workflow should be a first-class truth object.'},
          ]},
        {id:'memory-spec', label:'memory spec draft',
          runs:[
            {id:'#r-0139', label:'initial outline', status:'done', ts:'2h ago', operatorMsg:'Outline MEMORY_SPEC.md.'},
          ]},
        {id:'policy-matrix', label:'policy & approval matrix',
          runs:[
            {id:'#r-0131', label:'draft matrix', status:'blocked', ts:'yesterday', operatorMsg:'Draft the policy + approval matrix.'},
          ]},
      ],
    },
    {
      id:'home_energy_upgrade', label:'home_energy_upgrade', sub:'research · heat pumps',
      workUnits:[
        {id:'heat-pump-research', label:'research heat-pump options',
          runs:[
            {id:'#r-0051', label:'survey 3 vendors', status:'done', ts:'yesterday', operatorMsg:'Survey heat-pump options available in EU.'},
          ]},
      ],
    },
    {
      id:'book_research', label:'book_research', sub:'evidence synthesis', workUnits:[],
    },
    {
      id:'client_proposal', label:'client_proposal', sub:'draft · blocked',
      workUnits:[
        {id:'proposal-draft', label:'draft proposal document',
          runs:[{id:'#r-0022', label:'initial draft', status:'blocked', ts:'2d ago', operatorMsg:'Draft client proposal for Acme.'}]},
      ],
    },
  ],
};

// Layer definitions per run status
function layersForRun(run) {
  if (run.status==='blocked') return [
    {id:'context',    label:'context',    status:'done',    dur:'0.3s', sum:'snapshot loaded'},
    {id:'research',   label:'research',   status:'skipped', dur:'—',    sum:'not invoked'},
    {id:'proposal',   label:'proposal',   status:'skipped', dur:'—',    sum:'not invoked'},
    {id:'selection',  label:'selection',  status:'skipped', dur:'—',    sum:'not invoked'},
    {id:'governance', label:'governance', status:'blocked', dur:'0.6s', sum:'readiness fail · stale basis + unresolved conflict'},
    {id:'execution',  label:'execution',  status:'skipped', dur:'—',    sum:'no permit'},
    {id:'outcome',    label:'outcome',    status:'skipped', dur:'—',    sum:'—'},
    {id:'evaluation', label:'evaluation', status:'skipped', dur:'—',    sum:'—'},
    {id:'memory',     label:'memory',     status:'skipped', dur:'—',    sum:'—'},
    {id:'transition', label:'transition', status:'skipped', dur:'—',    sum:'no truth change'},
  ];
  if (run.status==='active') return [
    {id:'context',    label:'context',    status:'done',    dur:'0.4s',   sum:'4 docs · 2 memory refs'},
    {id:'research',   label:'research',   status:'done',    dur:'2m 14s', sum:'4 sources · 7 claims'},
    {id:'proposal',   label:'proposal',   status:'done',    dur:'18s',    sum:'2 honest options'},
    {id:'selection',  label:'selection',  status:'done',    dur:'6s',     sum:'opt-02 · cross-check path'},
    {id:'governance', label:'governance', status:'done',    dur:'1.2s',   sum:'approved · readiness 4/4'},
    {id:'execution',  label:'execution',  status:'active',  dur:'1m 48s', sum:'drafting §Memory'},
    {id:'outcome',    label:'outcome',    status:'pending', dur:'—',      sum:'—'},
    {id:'evaluation', label:'evaluation', status:'pending', dur:'—',      sum:'—'},
    {id:'memory',     label:'memory',     status:'pending', dur:'—',      sum:'0 candidates'},
    {id:'transition', label:'transition', status:'pending', dur:'—',      sum:'no truth change yet'},
  ];
  // done
  return [
    {id:'context',    label:'context',    status:'done', dur:'0.4s',  sum:'3 docs · 1 memory ref'},
    {id:'research',   label:'research',   status:'done', dur:'3m 02s', sum:'5 sources · 9 claims'},
    {id:'proposal',   label:'proposal',   status:'done', dur:'22s',   sum:'3 options'},
    {id:'selection',  label:'selection',  status:'done', dur:'8s',    sum:'opt-01'},
    {id:'governance', label:'governance', status:'done', dur:'0.9s',  sum:'auto · readiness 4/4'},
    {id:'execution',  label:'execution',  status:'done', dur:'1m 11s', sum:'completed'},
    {id:'outcome',    label:'outcome',    status:'done', dur:'0.2s',  sum:'artifacts normalized'},
    {id:'evaluation', label:'evaluation', status:'done', dur:'0.4s',  sum:'verdict · success'},
    {id:'memory',     label:'memory',     status:'done', dur:'0.3s',  sum:'1 candidate · 1 committed'},
    {id:'transition', label:'transition', status:'done', dur:'0.2s',  sum:'truth updated'},
  ];
}

// ─── utilities ─────────────────────────────────────────────

const sc = (status, t) => status==='done'?t.approved:status==='active'?ACCENT:status==='blocked'?t.blocked:status==='degraded'?t.degraded:t.faint;
const sg = (status) => status==='done'?'✓':status==='active'?'●':status==='blocked'?'✕':status==='degraded'?'△':status==='skipped'?'—':'○';

function TT({t, kind}) {
  const map = {canonical:{l:'CANONICAL',c:t.canonical},support:{l:'SUPPORT',c:t.support},derived:{l:'DERIVED',c:t.derived},memory:{l:'MEMORY',c:t.memory},local:{l:'UI-LOCAL',c:t.faint}};
  const m = map[kind]; if (!m) return null;
  return <span style={{fontFamily:mono,fontSize:9,letterSpacing:1.2,color:m.c,border:`1px solid ${m.c}55`,padding:'2px 6px',borderRadius:2}}>{m.l}</span>;
}

function Pill({t, children, onClick, active, color}) {
  const c = color || t.muted;
  return <button onClick={onClick} style={{
    background: active ? c : 'transparent',
    color: active ? (c===t.text?t.panel:'#fff') : c,
    border:`1px solid ${active?c:t.border}`,
    fontFamily:mono, fontSize:10, padding:'4px 10px', borderRadius:3, cursor:'pointer',
    letterSpacing:0.5,
  }}>{children}</button>;
}

// ─── sidebar ────────────────────────────────────────────────

function Sidebar({t, state, nav, setNav, onNew}) {
  const [openWu, setOpenWu] = React.useState({[nav.workUnit || 'define-architecture']: true});

  const activeProject = state.projects.find(p => p.id === nav.project) || state.projects[0];

  return (
    <div style={{width:280, flexShrink:0, background:t.rail, borderRight:`1px solid ${t.border}`, display:'flex', flexDirection:'column', height:'100%'}}>
      <div style={{padding:'14px 14px 12px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:10}}>
        <div style={{width:26, height:26, borderRadius:5, background:ACCENT, display:'grid', placeItems:'center', fontFamily:mono, fontSize:13, fontWeight:600, color:'#1a1816'}}>J</div>
        <div>
          <div style={{fontFamily:mono, fontSize:13, color:t.text, fontWeight:500, lineHeight:1.2}}>jeff</div>
          <div style={{fontFamily:mono, fontSize:9, color:t.faint, letterSpacing:1, marginTop:2}}>v1 · OPERATOR</div>
        </div>
        <button onClick={()=>setNav({...nav, view:'settings'})} style={{marginLeft:'auto', background:'transparent', border:'none', cursor:'pointer', fontSize:15, color:t.muted}}>⚙</button>
      </div>

      {/* projects */}
      <div style={{padding:'10px 12px 4px', display:'flex', alignItems:'center', justifyContent:'space-between'}}>
        <div style={{fontFamily:mono, fontSize:9, letterSpacing:1.5, color:t.faint}}>PROJECTS</div>
        <button style={{background:'transparent', border:`1px solid ${t.border}`, color:t.muted, fontFamily:mono, fontSize:10, padding:'2px 6px', borderRadius:3, cursor:'pointer'}}>+ new</button>
      </div>
      <div style={{padding:'0 6px'}}>
        {state.projects.map(p => {
          const active = p.id===nav.project;
          const anyBlocked = p.workUnits.some(wu => wu.runs.some(r=>r.status==='blocked'));
          const anyActive = p.workUnits.some(wu => wu.runs.some(r=>r.status==='active'));
          const dot = anyActive ? t.approved : anyBlocked ? t.blocked : t.faint;
          return (
            <div key={p.id} onClick={()=>{ setNav({view:'run', project:p.id, workUnit:null, run:null}); }}
              style={{padding:'8px 10px', margin:'1px 2px', borderRadius:3, cursor:'pointer',
                background: active?t.panel:'transparent',
                border: active?`1px solid ${t.borderStrong}`:'1px solid transparent'}}>
              <div style={{display:'flex', alignItems:'center', gap:8}}>
                <span style={{width:6,height:6,borderRadius:3,background:dot,flexShrink:0}}/>
                <div style={{fontFamily:mono, fontSize:12, color:active?t.text:t.muted, fontWeight:active?500:400}}>{p.label}</div>
                <div style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>{p.workUnits.length}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* work units of active project */}
      <div style={{padding:'12px 12px 4px', display:'flex', alignItems:'center', justifyContent:'space-between'}}>
        <div style={{fontFamily:mono, fontSize:9, letterSpacing:1.5, color:t.faint}}>WORK UNITS · {activeProject.label}</div>
      </div>
      <div style={{flex:1, overflow:'auto', padding:'0 6px 8px'}}>
        {activeProject.workUnits.length===0 && (
          <div style={{padding:14, fontSize:12, color:t.faint, fontStyle:'italic'}}>No work units yet.</div>
        )}
        {activeProject.workUnits.map(wu => {
          const isOpen = !!openWu[wu.id];
          const anyBlocked = wu.runs.some(r=>r.status==='blocked');
          const anyActive = wu.runs.some(r=>r.status==='active');
          const wuDot = anyActive?t.approved:anyBlocked?t.blocked:t.faint;
          return (
            <div key={wu.id}>
              <div onClick={()=>setOpenWu({...openWu, [wu.id]: !isOpen})}
                style={{padding:'6px 10px', margin:'1px 2px', borderRadius:3, cursor:'pointer',
                  display:'flex', alignItems:'center', gap:8}}>
                <span style={{fontFamily:mono, fontSize:9, color:t.faint, width:10}}>{isOpen?'▾':'▸'}</span>
                <span style={{width:6,height:6,borderRadius:3,background:wuDot,flexShrink:0}}/>
                <span style={{flex:1, fontSize:12, color:t.text, lineHeight:1.3}}>{wu.label}</span>
                <span style={{fontFamily:mono, fontSize:10, color:t.faint}}>{wu.runs.length}</span>
              </div>
              {isOpen && (
                <div style={{marginBottom:4}}>
                  {wu.runs.map(r => {
                    const active = r.id===nav.run && wu.id===nav.workUnit;
                    return (
                      <div key={r.id}
                        onClick={()=>setNav({view:'run', project:activeProject.id, workUnit:wu.id, run:r.id})}
                        style={{padding:'5px 10px 5px 30px', margin:'1px 2px', borderRadius:3, cursor:'pointer',
                          background: active?t.panel:'transparent',
                          border: active?`1px solid ${t.borderStrong}`:'1px solid transparent'}}>
                        <div style={{display:'flex', alignItems:'center', gap:8}}>
                          <span style={{color:sc(r.status,t), fontFamily:mono, fontSize:10, width:10, textAlign:'center'}}>{sg(r.status)}</span>
                          <span style={{fontFamily:mono, fontSize:10, color:t.muted, flex:'0 0 50px'}}>{r.id}</span>
                          <span style={{fontSize:11, color:active?t.text:t.muted, flex:1, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>{r.label}</span>
                        </div>
                      </div>
                    );
                  })}
                  <div onClick={()=>onNew(activeProject.id, wu.id)}
                    style={{padding:'5px 10px 5px 30px', margin:'1px 2px', borderRadius:3, cursor:'pointer',
                      fontFamily:mono, fontSize:10, color:t.faint}}>
                    + new run
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div style={{padding:'10px 14px', borderTop:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:8}}>
        <div style={{width:22, height:22, borderRadius:11, background:t.border}}/>
        <div style={{fontSize:11, color:t.muted}}>operator</div>
      </div>
    </div>
  );
}

// ─── layer body bits ───────────────────────────────────────

function LayerInput({t, layerId, runId}) {
  const [mode, setMode] = React.useState('summary');
  const rows = {
    context:    [['scope', `jeff / .../ ${runId}`], ['trigger', 'operator request'], ['state read', 'fresh snapshot', 'canonical']],
    research:   [['scope', `jeff / .../ ${runId}`], ['question', '“memory vs canonical state”'], ['context', 'context bundle', 'support'], ['policy', 'internet_research · auto']],
    proposal:   [['scope', `jeff / .../ ${runId}`], ['context', 'context + research', 'support'], ['constraint', 'mutate_canonical_spec']],
    selection:  [['scope', `jeff / .../ ${runId}`], ['options', 'opt-01, opt-02', 'support'], ['direction', 'truth-first', 'canonical']],
    governance: [['scope', `jeff / .../ ${runId}`], ['selection', 'opt-02', 'canonical'], ['policy', 'mutate_canonical_spec']],
    execution:  [['scope', `jeff / .../ ${runId}`], ['action', 'draft §Memory', 'canonical'], ['permit', 'approved + ready', 'canonical']],
    outcome:    [['scope', `jeff / .../ ${runId}`], ['expects', 'execution result']],
    evaluation: [['scope', `jeff / .../ ${runId}`], ['goal', 'draft matches canonical spec'], ['outcome', '—']],
    memory:     [['scope', `jeff / .../ ${runId}`], ['source', 'evaluation verdict · pending']],
    transition: [['scope', `jeff / .../ ${runId}`], ['intent', 'apply §Memory'], ['basis', 'evaluation + memory']],
  }[layerId] || [];

  return (
    <Subcard t={t} label="INPUT · context given to model" tone={t.derived} kindTag={<TT t={t} kind="derived"/>}
      right={<div style={{display:'flex', gap:4}}>
        {['summary','raw'].map(m => <Pill key={m} t={t} onClick={()=>setMode(m)} active={mode===m} color={mode===m?t.text:t.muted}>{m}</Pill>)}
      </div>}>
      {mode==='summary' ? (
        <div style={{padding:'10px 12px', display:'grid', gridTemplateColumns:'110px 1fr', gap:'5px 10px', fontFamily:mono, fontSize:11}}>
          {rows.map(([k,v,tag],i)=><React.Fragment key={i}>
            <div style={{color:t.faint}}>{k}</div>
            <div style={{color:t.text, display:'flex', gap:6, alignItems:'center', flexWrap:'wrap'}}>{v}{tag && <TT t={t} kind={tag}/>}</div>
          </React.Fragment>)}
        </div>
      ) : (
        <div style={{padding:'10px 12px', fontFamily:mono, fontSize:11, lineHeight:1.6, color:t.text, background:t.surface, whiteSpace:'pre-wrap'}}>
{`{
  "layer": "${layerId}",
  "scope": {"project":"jeff","work_unit":"...", "run":"${runId}"},
  "inputs": ${JSON.stringify(Object.fromEntries(rows.map(r=>[r[0],r[1]])), null, 2)}
}`}
        </div>
      )}
    </Subcard>
  );
}

function LayerReasoning({t, layerId}) {
  const streams = {
    context:    [['note','reading state snapshot…'],['ok','snapshot fresh'],['note','retrieving committed memory'],['ok','2 refs loaded']],
    research:   [['note','searching: memory vs state'],['ok','4 candidates'],['think','blog source is secondary — illustrative only'],['ok','3 internal sources aligned']],
    proposal:   [['note','generating candidates…'],['think','direct-draft is fine — no contradictions'],['think','cross-check is cheap insurance'],['ok','2 honest options · 3rd would be ceremonial']],
    selection:  [['think','comparing against truth-first direction'],['think','opt-02 catches drift for marginal cost'],['ok','opt-02 · honest choice'],['note','selection ≠ execution permission']],
    governance: [['note','invoking mutate_canonical_spec'],['ok','operator approval · explicit'],['ok','readiness 4/4 pass'],['think','approved ≠ applied']],
    execution:  [['note','opening artifact'],['stream','## Memory'],['stream','Memory stores useful, committed knowledge.'],['think','keep memory≠truth explicit'],['stream','Canonical state may reference only committed memory IDs.']],
    outcome:    [['note','waiting for execution'],['note','will normalize artifacts + logs']],
    evaluation: [['note','will compare outcome to goal'],['note','verdicts: success/degraded/partial/inconclusive']],
    memory:     [['note','only accept candidates with evidence link'],['think','memory ≠ truth']],
    transition: [['note','transitions = only truth mutation path'],['think','will not fire unless evaluation supports it']],
  }[layerId] || [];
  return (
    <Subcard t={t} label="REASONING · model thought stream" tone={ACCENT} kindTag={<Pill t={t} color={ACCENT} active>stream</Pill>}>
      <div style={{padding:'10px 12px', background:t.surface, fontFamily:mono, fontSize:11, lineHeight:1.8, maxHeight:240, overflow:'auto'}}>
        {streams.map(([k, txt], i) => {
          const color = k==='ok'?t.approved:k==='warn'?t.pending:k==='think'?t.memory:k==='stream'?t.text:t.muted;
          const glyph = k==='ok'?'✓':k==='warn'?'!':k==='think'?'›':k==='stream'?'▌':'·';
          return (
            <div key={i} style={{display:'flex', gap:8}}>
              <div style={{width:12, color, textAlign:'center'}}>{glyph}</div>
              <div style={{flex:1, color: k==='stream'?t.text:k==='think'?t.memory:t.muted, fontStyle:k==='think'?'italic':'normal',
                background:k==='stream'?`${ACCENT}0d`:'transparent', paddingLeft:k==='stream'?6:0,
                borderLeft:k==='stream'?`2px solid ${ACCENT}44`:'none'}}>{txt}</div>
            </div>
          );
        })}
      </div>
    </Subcard>
  );
}

function LayerOutput({t, layerId}) {
  let body;
  let kind = 'support';
  if (layerId==='research') {
    body = <div>{[
      ['01', 'Memory design in agentic systems', 'blog.example.org/memory', 'derived'],
      ['02', 'State vs memory separation (paper)', 'arxiv.org/abs/2401.xxxxx', 'derived'],
      ['03', 'MEMORY_SPEC.md §1–4', 'internal', 'canonical'],
      ['04', 'mem#0093 contradiction log', 'internal', 'memory'],
    ].map(([n,title,src,k])=>(
      <div key={n} style={{padding:'6px 0', borderBottom:`1px solid ${t.border}`, display:'flex', gap:10, alignItems:'center'}}>
        <span style={{fontFamily:mono, fontSize:10, color:t.faint, width:20}}>{n}</span>
        <div style={{flex:1}}>
          <div style={{fontSize:12, color:t.text}}>{title}</div>
          <div style={{fontFamily:mono, fontSize:10, color:t.muted}}>{src}</div>
        </div>
        <TT t={t} kind={k}/>
      </div>
    ))}</div>;
  } else if (layerId==='proposal') {
    body = <div>{[
      {id:'opt-01', sel:false, label:'direct draft from committed memory spec', risk:'low', cost:'18s'},
      {id:'opt-02', sel:true,  label:'draft + cross-check contradictions log', risk:'low', cost:'32s'},
    ].map(o=>(
      <div key={o.id} style={{border:`${o.sel?2:1}px solid ${o.sel?ACCENT:t.border}`, borderRadius:3, padding:10, marginBottom:6, background:t.surface}}>
        <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:4}}>
          <span style={{fontFamily:mono, fontSize:10, color:o.sel?ACCENT:t.muted}}>{o.id}</span>
          <span style={{fontSize:12, color:t.text, fontWeight:500}}>{o.label}</span>
          {o.sel && <span style={{fontFamily:mono, fontSize:9, color:t.approved, border:`1px solid ${t.approved}55`, padding:'2px 6px', borderRadius:2, letterSpacing:1}}>SELECTED ↓</span>}
        </div>
        <div style={{fontFamily:mono, fontSize:10, color:t.muted}}>risk {o.risk} · est {o.cost}</div>
      </div>
    ))}</div>;
  } else if (layerId==='selection') {
    kind='canonical';
    body = <div style={{fontFamily:mono, fontSize:12, color:t.text, lineHeight:1.7}}>
      <div>selected · <span style={{color:ACCENT}}>opt-02</span></div>
      <div style={{color:t.muted, fontSize:11}}>draft + cross-check against contradictions log</div>
    </div>;
  } else if (layerId==='governance') {
    kind='canonical';
    body = <div style={{display:'grid', gridTemplateColumns:'110px 1fr', gap:'5px 10px', fontFamily:mono, fontSize:11}}>
      <div style={{color:t.faint}}>decision</div><div style={{color:t.approved}}>✓ EXECUTION PERMITTED</div>
      <div style={{color:t.faint}}>approval</div><div style={{color:t.text}}>operator · explicit</div>
      <div style={{color:t.faint}}>readiness</div><div style={{color:t.text}}>4 / 4 pass</div>
      <div style={{color:t.faint}}>risk</div><div style={{color:t.pending}}>medium · canonical mutation</div>
      <div style={{color:t.faint}}>note</div><div style={{color:t.muted}}>approved ≠ applied</div>
    </div>;
  } else if (layerId==='execution') {
    body = <div style={{fontFamily:mono, fontSize:12, color:t.text, lineHeight:1.7, padding:10, background:t.surface, border:`1px solid ${t.border}`, borderRadius:3}}>
      <div style={{color:t.muted}}>## Memory</div>
      <div>Memory stores useful, committed, retrievable knowledge.</div>
      <div>Memory does not define current truth.</div>
      <div>Canonical state may reference only <span style={{background:`${ACCENT}33`,padding:'0 3px'}}>committed memory IDs</span>.</div>
    </div>;
  } else if (layerId==='context') {
    body = <div style={{fontFamily:mono, fontSize:11, color:t.text, lineHeight:1.7}}>assembled context bundle · 4 docs · 2 memory refs · 8,412 tokens</div>;
  } else {
    body = <div style={{fontFamily:mono, fontSize:11, color:t.faint}}>—</div>;
  }
  return <Subcard t={t} label="OUTPUT · layer result" tone={t.support} kindTag={<TT t={t} kind={kind}/>}>
    <div style={{padding:'10px 12px'}}>{body}</div>
  </Subcard>;
}

function Subcard({t, label, kindTag, right, tone, children}) {
  return (
    <div style={{border:`1px solid ${t.border}`, borderRadius:3, marginBottom:8, overflow:'hidden'}}>
      <div style={{padding:'6px 10px', display:'flex', alignItems:'center', gap:8, background:`${tone||t.muted}10`, borderBottom:`1px solid ${t.border}`}}>
        <span style={{fontFamily:mono, fontSize:9, letterSpacing:1.5, color:tone||t.muted, textTransform:'uppercase'}}>{label}</span>
        {kindTag}<span style={{marginLeft:'auto'}}>{right}</span>
      </div>
      <div>{children}</div>
    </div>
  );
}

function LayerPanel({t, layer, isOpen, onToggle, runId}) {
  const c = sc(layer.status, t);
  return (
    <div style={{border:`1px solid ${isOpen?t.borderStrong:t.border}`, borderRadius:4, background:t.panel, marginBottom:8, overflow:'hidden'}}>
      <div onClick={onToggle} style={{padding:'10px 14px', cursor:'pointer', display:'flex', alignItems:'center', gap:10, background:isOpen?t.surface:t.panel, borderBottom:isOpen?`1px solid ${t.border}`:'none'}}>
        <span style={{fontFamily:mono, fontSize:9, color:t.faint, width:10}}>{isOpen?'▾':'▸'}</span>
        <span style={{color:c, fontFamily:mono, fontSize:13, width:14, textAlign:'center'}}>{sg(layer.status)}</span>
        <span style={{fontFamily:mono, fontSize:11, letterSpacing:1.5, color:t.text, textTransform:'uppercase', flex:'0 0 110px'}}>{layer.label}</span>
        <span style={{fontSize:12, color:t.muted, flex:1, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>{layer.sum}</span>
        <span style={{fontFamily:mono, fontSize:10, color:t.faint}}>{layer.dur}</span>
      </div>
      {isOpen && layer.status!=='skipped' && (
        <div style={{padding:'12px 14px'}}>
          <LayerInput t={t} layerId={layer.id} runId={runId}/>
          <LayerReasoning t={t} layerId={layer.id}/>
          <LayerOutput t={t} layerId={layer.id}/>
        </div>
      )}
      {isOpen && layer.status==='skipped' && (
        <div style={{padding:'14px', fontSize:12, color:t.faint, fontStyle:'italic'}}>Layer was not invoked in this run.</div>
      )}
    </div>
  );
}

// ─── run chat view ─────────────────────────────────────────

function RunChat({t, state, nav, setNav, onApprove}) {
  const project = state.projects.find(p => p.id === nav.project);
  const wu = project?.workUnits.find(w => w.id === nav.workUnit);
  const run = wu?.runs.find(r => r.id === nav.run);
  const [openLayer, setOpenLayer] = React.useState('execution');
  const [approved, setApproved] = React.useState(false);

  if (!run) return <EmptyProject t={t} project={project} setNav={setNav}/>;

  const layers = layersForRun(run);
  const runStatus = run.status;

  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.bg, minWidth:0}}>
      {/* scope bar */}
      <div style={{padding:'12px 20px', borderBottom:`1px solid ${t.border}`, background:t.panel, display:'flex', alignItems:'center', gap:12}}>
        <span style={{fontFamily:mono, fontSize:10, color:t.faint, letterSpacing:1.5}}>RUN</span>
        <span style={{fontFamily:mono, fontSize:13, color:t.text}}>
          <span style={{fontWeight:500}}>{project.label}</span>
          <span style={{margin:'0 6px', color:t.faint}}>/</span>
          <span style={{color:ACCENT, fontWeight:500}}>{wu.label.length>30?wu.id:wu.id}</span>
          <span style={{margin:'0 6px', color:t.faint}}>/</span>
          <span style={{fontWeight:500}}>{run.id}</span>
        </span>
        <span style={{fontFamily:mono, fontSize:9, letterSpacing:1, color:sc(runStatus,t), border:`1px solid ${sc(runStatus,t)}55`, padding:'2px 8px', borderRadius:2, textTransform:'uppercase'}}>
          {sg(runStatus)} {runStatus}
        </span>
        <div style={{marginLeft:'auto', display:'flex', gap:6}}>
          <Pill t={t} onClick={()=>setNav({...nav, view:'history'})}>history</Pill>
        </div>
      </div>

      <div style={{flex:1, overflow:'auto'}}>
        <div style={{padding:'16px 20px', maxWidth:1100, margin:'0 auto'}}>
          {/* operator message */}
          <div style={{padding:'12px 14px', marginBottom:10, background:t.surface, border:`1px solid ${t.border}`, borderRadius:4}}>
            <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:6}}>
              <span style={{fontFamily:mono, fontSize:9, letterSpacing:1.5, color:t.muted, textTransform:'uppercase'}}>operator</span>
              <span style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>{run.ts} · request</span>
            </div>
            <div style={{fontSize:13, color:t.text, lineHeight:1.5}}>{run.operatorMsg}</div>
          </div>

          {/* blocked banner */}
          {runStatus==='blocked' && (
            <div style={{padding:'12px 14px', marginBottom:10, background:`${t.blocked}0f`, border:`1px solid ${t.blocked}`, borderRadius:4}}>
              <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:6}}>
                <span style={{width:8,height:8,borderRadius:4,background:t.blocked}}/>
                <span style={{fontFamily:mono, fontSize:10, color:t.blocked, letterSpacing:1.5}}>HONEST ESCALATION</span>
              </div>
              <div style={{fontSize:13, color:t.text, lineHeight:1.55, marginBottom:8}}>Run blocked by readiness failure. Two conditions prevent honest continuation:</div>
              <div style={{fontFamily:mono, fontSize:11, lineHeight:1.7}}>
                <div><span style={{color:t.blocked}}>✕</span> <b>stale basis</b> — context is 2 runs behind canonical state</div>
                <div><span style={{color:t.blocked}}>✕</span> <b>unresolved conflict</b> — mem#0093 contradicts POLICY_SPEC §4.2</div>
                <div><span style={{color:t.approved}}>✓</span> read-only inspection may continue</div>
              </div>
              <div style={{display:'flex', gap:6, marginTop:10, flexWrap:'wrap'}}>
                <Pill t={t}>revalidate context</Pill>
                <Pill t={t}>resolve contradiction</Pill>
                <Pill t={t}>read-only continue</Pill>
                <Pill t={t}>escalate</Pill>
              </div>
            </div>
          )}

          {/* approval gate if execution pending approval */}
          {runStatus==='active' && !approved && (
            <div style={{padding:'12px 14px', marginBottom:10, background:`${t.pending}0f`, border:`1px solid ${t.pending}`, borderRadius:4}}>
              <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:6}}>
                <span style={{width:8,height:8,borderRadius:4,background:t.pending}}/>
                <span style={{fontFamily:mono, fontSize:10, color:t.pending, letterSpacing:1.5}}>GOVERNANCE · APPROVED</span>
                <span style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>approved ≠ applied</span>
              </div>
              <div style={{fontSize:13, color:t.text, lineHeight:1.5, marginBottom:8}}>Canonical-spec mutation. Action executes but transition only fires after evaluation.</div>
              <div style={{display:'flex', gap:6}}>
                <button onClick={()=>onApprove && onApprove()} style={{background:t.approved, color:'#fff', border:'none', fontFamily:mono, fontSize:11, padding:'6px 12px', borderRadius:3, cursor:'pointer', fontWeight:500}}>acknowledge</button>
                <Pill t={t}>reject</Pill>
                <Pill t={t}>defer</Pill>
              </div>
            </div>
          )}

          {/* loop strip */}
          <div style={{padding:'8px 12px', background:t.panel, border:`1px solid ${t.border}`, borderRadius:4, marginBottom:8, display:'flex', alignItems:'center', gap:10}}>
            <span style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.muted}}>LOOP · 10 LAYERS</span>
            <span style={{fontFamily:mono, fontSize:10, color:t.faint}}>
              {layers.filter(l=>l.status==='done').length} done · {layers.filter(l=>l.status==='active').length} active · {layers.filter(l=>l.status==='pending').length} pending · {layers.filter(l=>l.status==='blocked').length} blocked · {layers.filter(l=>l.status==='skipped').length} skipped
            </span>
            <span style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>click to expand</span>
          </div>

          {layers.map(l => (
            <LayerPanel key={l.id} t={t} layer={l} runId={run.id}
              isOpen={openLayer===l.id}
              onToggle={()=>setOpenLayer(openLayer===l.id?null:l.id)}/>
          ))}

          <div style={{height:60}}/>
        </div>
      </div>

      {/* composer */}
      <div style={{padding:'12px 20px', borderTop:`1px solid ${t.border}`, background:t.panel}}>
        <Composer t={t} placeholder={runStatus==='blocked'?'Respond to escalation…':`Continue within ${wu.label}…`}/>
      </div>
    </div>
  );
}

function Composer({t, placeholder}) {
  const [val, setVal] = React.useState('');
  return (
    <div style={{maxWidth:1100, margin:'0 auto'}}>
      <div style={{border:`1px solid ${t.borderStrong}`, borderRadius:6, background:t.surface, padding:'10px 12px'}}>
        <textarea value={val} onChange={e=>setVal(e.target.value)} placeholder={placeholder}
          style={{width:'100%', background:'transparent', border:'none', outline:'none', color:t.text,
            fontFamily:sans, fontSize:13, resize:'none', minHeight:46, lineHeight:1.5}}/>
        <div style={{display:'flex', alignItems:'center', gap:6, marginTop:6, paddingTop:8, borderTop:`1px solid ${t.border}`}}>
          <Pill t={t}>＋ attach</Pill>
          <Pill t={t}>⌕ research</Pill>
          <Pill t={t}>⎇ plan</Pill>
          <div style={{marginLeft:'auto', display:'flex', alignItems:'center', gap:8}}>
            <span style={{fontFamily:mono, fontSize:10, color:t.faint}}>submit as <b style={{color:t.muted}}>proposal request</b></span>
            <button disabled={!val.trim()} onClick={()=>setVal('')} style={{
              background: val.trim()?ACCENT:t.border, border:'none', color:'#1a1816',
              fontFamily:mono, fontSize:11, padding:'6px 14px', borderRadius:3,
              cursor: val.trim()?'pointer':'not-allowed', fontWeight:500, opacity:val.trim()?1:0.5
            }}>submit →</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── empty project (no run selected) ────────────────────────

function EmptyProject({t, project, setNav}) {
  return (
    <div style={{flex:1, display:'flex', alignItems:'center', justifyContent:'center', background:t.bg, padding:40}}>
      <div style={{maxWidth:520, textAlign:'center'}}>
        <div style={{fontFamily:mono, fontSize:11, color:t.faint, letterSpacing:2, marginBottom:12}}>PROJECT · {project?.label?.toUpperCase()}</div>
        <div style={{fontSize:24, color:t.text, fontWeight:500, letterSpacing:-0.4, lineHeight:1.3, marginBottom:10}}>
          Pick a work unit & run, or start a new one.
        </div>
        <div style={{fontSize:13, color:t.muted, lineHeight:1.6, marginBottom:20}}>
          Everything runs inside <b style={{color:t.text}}>project · work_unit · run</b>. Jeff treats projects as hard isolation boundaries — nothing leaks across.
        </div>
        <button onClick={()=>setNav({view:'new_run', project:project.id})} style={{
          background:ACCENT, border:'none', color:'#1a1816', fontFamily:mono, fontSize:12, padding:'8px 18px', borderRadius:3, cursor:'pointer', fontWeight:500
        }}>＋ new run</button>
      </div>
    </div>
  );
}

// ─── history view ──────────────────────────────────────────

function HistoryView({t, state, nav, setNav}) {
  const project = state.projects.find(p => p.id === nav.project);
  const wu = project?.workUnits.find(w => w.id === nav.workUnit);
  if (!wu) return <EmptyProject t={t} project={project} setNav={setNav}/>;

  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.bg}}>
      <div style={{padding:'14px 20px', borderBottom:`1px solid ${t.border}`, background:t.panel}}>
        <div style={{display:'flex', alignItems:'baseline', gap:12}}>
          <div style={{fontSize:20, color:t.text, fontWeight:500, letterSpacing:-0.3}}>{wu.label}</div>
          <TT t={t} kind="canonical"/>
          <div style={{marginLeft:'auto', fontFamily:mono, fontSize:11, color:t.faint}}>{wu.runs.length} runs</div>
        </div>
      </div>
      <div style={{flex:1, overflow:'auto'}}>
        {wu.runs.map(r => (
          <div key={r.id} onClick={()=>setNav({view:'run', project:nav.project, workUnit:nav.workUnit, run:r.id})}
            style={{padding:'12px 20px', borderBottom:`1px solid ${t.border}`, cursor:'pointer', display:'flex', alignItems:'center', gap:12}}>
            <span style={{color:sc(r.status,t), fontFamily:mono, fontSize:13, width:14, textAlign:'center'}}>{sg(r.status)}</span>
            <span style={{fontFamily:mono, fontSize:11, color:t.muted, flex:'0 0 72px'}}>{r.id}</span>
            <span style={{flex:1, fontSize:13, color:t.text}}>{r.label}</span>
            <span style={{fontFamily:mono, fontSize:10, color:t.faint}}>{r.ts}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── new run view ──────────────────────────────────────────

function NewRunView({t, state, nav, setNav, onCreate}) {
  const project = state.projects.find(p => p.id === nav.project) || state.projects[0];
  const [wuId, setWuId] = React.useState(nav.workUnit || project.workUnits[0]?.id);
  const [msg, setMsg] = React.useState('');

  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.bg}}>
      <div style={{padding:'14px 20px', borderBottom:`1px solid ${t.border}`, background:t.panel, display:'flex', alignItems:'center', gap:10}}>
        <div style={{fontFamily:mono, fontSize:10, color:t.faint, letterSpacing:1.5}}>NEW RUN</div>
        <div style={{fontFamily:mono, fontSize:12, color:t.text}}>
          <span style={{fontWeight:500}}>{project.label}</span>
          <span style={{margin:'0 6px', color:t.faint}}>/</span>
          <span style={{color:ACCENT, fontWeight:500}}>{wuId || '—'}</span>
        </div>
      </div>

      <div style={{flex:1, overflow:'auto', padding:'30px 24px'}}>
        <div style={{maxWidth:720, margin:'0 auto'}}>
          <div style={{fontSize:22, color:t.text, fontWeight:500, letterSpacing:-0.4, marginBottom:8}}>Start a new run</div>
          <div style={{fontSize:13, color:t.muted, lineHeight:1.55, marginBottom:24}}>
            Your input becomes a <b style={{color:t.text}}>request</b>. Jeff will assemble truth-first context, generate 0–3 honest proposals, and only execute after governance passes.
          </div>

          <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.faint, marginBottom:6}}>WORK UNIT</div>
          <div style={{display:'flex', flexWrap:'wrap', gap:6, marginBottom:20}}>
            {project.workUnits.map(w => (
              <Pill key={w.id} t={t} active={wuId===w.id} color={wuId===w.id?ACCENT:t.muted} onClick={()=>setWuId(w.id)}>
                {w.id}
              </Pill>
            ))}
            <Pill t={t}>+ new work unit</Pill>
          </div>

          <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.faint, marginBottom:6}}>OPERATOR REQUEST</div>
          <textarea value={msg} onChange={e=>setMsg(e.target.value)}
            placeholder="What should Jeff work on inside this work unit?"
            style={{width:'100%', minHeight:120, padding:12, border:`1px solid ${t.borderStrong}`, background:t.panel, color:t.text, borderRadius:4, fontFamily:sans, fontSize:14, lineHeight:1.5, outline:'none', resize:'vertical'}}/>

          <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.faint, margin:'18px 0 6px'}}>SUGGESTED</div>
          <div style={{display:'flex', flexWrap:'wrap', gap:6, marginBottom:24}}>
            {['continue draft where we stopped','research planning engines','review memory for contradictions','synthesize recent evaluation'].map(s=>(
              <Pill key={s} t={t} onClick={()=>setMsg(s)}>{s}</Pill>
            ))}
          </div>

          <div style={{display:'flex', gap:8}}>
            <button disabled={!msg.trim() || !wuId} onClick={()=>onCreate(project.id, wuId, msg)}
              style={{background: msg.trim()&&wuId?ACCENT:t.border, color:'#1a1816', border:'none',
                fontFamily:mono, fontSize:12, padding:'8px 18px', borderRadius:3,
                cursor:msg.trim()&&wuId?'pointer':'not-allowed', fontWeight:500, opacity:msg.trim()&&wuId?1:0.5}}>
              submit · start run →
            </button>
            <Pill t={t} onClick={()=>setNav({...nav, view:'run'})}>cancel</Pill>
          </div>
          <div style={{marginTop:12, fontFamily:mono, fontSize:10, color:t.faint}}>submission is a request, not truth mutation</div>
        </div>
      </div>
    </div>
  );
}

// ─── settings view ─────────────────────────────────────────

function SettingsView({t, setNav, theme, setTheme}) {
  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.bg}}>
      <div style={{padding:'14px 20px', borderBottom:`1px solid ${t.border}`, background:t.panel, display:'flex', alignItems:'center', gap:10}}>
        <div style={{fontFamily:mono, fontSize:10, color:t.faint, letterSpacing:1.5}}>SETTINGS</div>
        <div style={{fontSize:16, color:t.text, fontWeight:500}}>policy, readiness & appearance</div>
        <Pill t={t} onClick={()=>setNav(n=>({...n, view:'run'}))}>close</Pill>
      </div>
      <div style={{flex:1, overflow:'auto', padding:'20px 24px'}}>
        <div style={{maxWidth:820, margin:'0 auto', display:'flex', flexDirection:'column', gap:16}}>
          <div style={{border:`1px solid ${t.border}`, borderRadius:4, background:t.panel}}>
            <div style={{padding:'10px 14px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:8}}>
              <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.muted}}>POLICY · RULES</div>
              <TT t={t} kind="canonical"/>
            </div>
            {[
              ['mutate_canonical_spec', 'require_operator_approval · require_readiness', true],
              ['internet_research',     'auto · scoped to active project',                true],
              ['external_tool_call',    'require_readiness · log trace',                  true],
              ['memory_commit',         'auto · require_evidence_link',                   true],
              ['long_running_autonomy', 'disabled · v1',                                  false],
            ].map(([rule,eff,on])=>(
              <div key={rule} style={{padding:'10px 14px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:12}}>
                <div style={{flex:'0 0 220px', fontFamily:mono, fontSize:12, color:t.text}}>{rule}</div>
                <div style={{flex:1, fontFamily:mono, fontSize:11, color:t.muted}}>{eff}</div>
                <div style={{width:32, height:18, borderRadius:9, position:'relative', background:on?t.approved:t.border}}>
                  <div style={{position:'absolute', top:2, left:on?16:2, width:14, height:14, borderRadius:7, background:'#fff'}}/>
                </div>
              </div>
            ))}
          </div>

          <div style={{border:`1px solid ${t.border}`, borderRadius:4, background:t.panel}}>
            <div style={{padding:'10px 14px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:8}}>
              <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.muted}}>APPEARANCE</div>
              <TT t={t} kind="local"/>
            </div>
            <div style={{padding:14}}>
              <div style={{fontFamily:mono, fontSize:10, color:t.muted, marginBottom:6}}>theme</div>
              <div style={{display:'flex', gap:6}}>
                {['light','dark'].map(v => (
                  <Pill key={v} t={t} active={theme===v} color={theme===v?ACCENT:t.muted} onClick={()=>setTheme(v)}>{v}</Pill>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── app root ──────────────────────────────────────────────

function App() {
  const [theme, setTheme] = React.useState(() => localStorage.getItem('jeff.theme') || 'light');
  const [nav, setNav] = React.useState(() => {
    try { return JSON.parse(localStorage.getItem('jeff.nav')) || {view:'run', project:'jeff', workUnit:'define-architecture', run:'#r-0147'}; }
    catch { return {view:'run', project:'jeff', workUnit:'define-architecture', run:'#r-0147'}; }
  });
  const [state, setState] = React.useState(initialState);

  React.useEffect(() => { localStorage.setItem('jeff.theme', theme); }, [theme]);
  React.useEffect(() => { localStorage.setItem('jeff.nav', JSON.stringify(nav)); }, [nav]);

  const t = THEMES[theme];

  const handleNewRun = (projectId, workUnitId, msg) => {
    const id = '#r-' + String(Math.floor(Math.random()*9000)+1000);
    setState(s => ({
      ...s,
      projects: s.projects.map(p => p.id!==projectId ? p : ({
        ...p,
        workUnits: p.workUnits.map(w => w.id!==workUnitId ? w : ({
          ...w,
          runs: [{id, label: msg.slice(0,42)+(msg.length>42?'…':''), status:'active', ts:'just now', operatorMsg: msg}, ...w.runs]
        }))
      }))
    }));
    setNav({view:'run', project:projectId, workUnit:workUnitId, run:id});
  };

  const onNewRunFromSidebar = (projectId, workUnitId) => setNav({view:'new_run', project:projectId, workUnit:workUnitId});

  let main;
  if (nav.view==='new_run') main = <NewRunView t={t} state={state} nav={nav} setNav={setNav} onCreate={handleNewRun}/>;
  else if (nav.view==='history') main = <HistoryView t={t} state={state} nav={nav} setNav={setNav}/>;
  else if (nav.view==='settings') main = <SettingsView t={t} setNav={setNav} theme={theme} setTheme={setTheme}/>;
  else main = <RunChat t={t} state={state} nav={nav} setNav={setNav}/>;

  return (
    <div style={{display:'flex', height:'100vh', width:'100vw', background:t.bg, color:t.text, fontFamily:sans}}>
      <Sidebar t={t} state={state} nav={nav} setNav={setNav} onNew={onNewRunFromSidebar}/>
      <div style={{flex:1, display:'flex', minWidth:0}}>{main}</div>

      {/* floating theme toggle */}
      <div style={{position:'fixed', bottom:14, right:14, display:'flex', gap:4, background:t.panel, border:`1px solid ${t.border}`, padding:4, borderRadius:4}}>
        {['light','dark'].map(v => (
          <button key={v} onClick={()=>setTheme(v)} style={{
            background:theme===v?ACCENT:'transparent', color:theme===v?'#1a1816':t.muted,
            border:'none', fontFamily:mono, fontSize:10, padding:'4px 8px', borderRadius:2, cursor:'pointer', letterSpacing:0.5
          }}>{v}</button>
        ))}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
