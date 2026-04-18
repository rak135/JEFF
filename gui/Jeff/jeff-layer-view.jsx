// Run-chat screen with inline expandable layer panels.
// Replaces the old LayerDeepDive. Sidebar: work_units expand to show runs;
// clicking a run opens its chat. Inside the chat, each of the 10 layers is
// an expandable panel (Input / Reasoning / Output).

const RC_MONO = 'JetBrains Mono, ui-monospace, monospace';
const RC_SANS = 'IBM Plex Sans, system-ui, sans-serif';

const WU_TREE = [
  {id:'define-architecture', label:'define canonical ARCHITECTURE.md', status:'active', expanded:true,
    runs:[
      {id:'#r-0147', label:'draft Memory section', status:'active',  ts:'4m ago'},
      {id:'#r-0146', label:'continue draft',        status:'blocked', ts:'17m ago'},
      {id:'#r-0145', label:'research: workflow-as-truth', status:'done', ts:'1h ago'},
    ]},
  {id:'memory-spec', label:'memory spec draft', status:'idle', expanded:false,
    runs:[
      {id:'#r-0139', label:'initial outline', status:'done', ts:'2h ago'},
      {id:'#r-0138', label:'research memory patterns', status:'done', ts:'3h ago'},
    ]},
  {id:'policy-matrix', label:'policy & approval matrix', status:'blocked', expanded:false,
    runs:[
      {id:'#r-0131', label:'draft matrix', status:'blocked', ts:'yesterday'},
    ]},
  {id:'research-planners', label:'survey planning engines', status:'done', expanded:false,
    runs:[
      {id:'#r-0122', label:'compare planners', status:'degraded', ts:'2d ago'},
    ]},
];

const LAYERS = [
  {id:'context',    label:'context',    status:'done',    dur:'0.4s',   sum:'4 docs · 2 memory refs'},
  {id:'research',   label:'research',   status:'done',    dur:'2m 14s', sum:'4 sources · 7 claims'},
  {id:'proposal',   label:'proposal',   status:'done',    dur:'18s',    sum:'2 honest options'},
  {id:'selection',  label:'selection',  status:'done',    dur:'6s',     sum:'opt-02 · cross-check path'},
  {id:'governance', label:'governance', status:'done',    dur:'1.2s',   sum:'approval auto · readiness 4/4'},
  {id:'execution',  label:'execution',  status:'active',  dur:'1m 48s', sum:'drafting §Memory'},
  {id:'outcome',    label:'outcome',    status:'pending', dur:'—',      sum:'—'},
  {id:'evaluation', label:'evaluation', status:'pending', dur:'—',      sum:'—'},
  {id:'memory',     label:'memory',     status:'pending', dur:'—',      sum:'0 candidates'},
  {id:'transition', label:'transition', status:'pending', dur:'—',      sum:'no truth change yet'},
];

function rcStatusColor(s, t, accent) {
  return s==='done'?t.approved:s==='active'?accent:s==='blocked'?t.blocked:s==='degraded'?t.degraded:t.faint;
}
function rcStatusGlyph(s) {
  return s==='done'?'✓':s==='active'?'●':s==='blocked'?'✕':s==='degraded'?'△':'○';
}

function TT({t, kind}) {
  const map = {
    canonical:{l:'CANONICAL',c:t.canonical},
    support:{l:'SUPPORT',c:t.support},
    derived:{l:'DERIVED',c:t.derived},
    memory:{l:'MEMORY',c:t.memory},
    local:{l:'UI-LOCAL',c:t.faint},
  };
  const m = map[kind];
  return <span style={{fontFamily:RC_MONO, fontSize:9, letterSpacing:1.2, color:m.c, border:`1px solid ${m.c}55`, padding:'2px 6px', borderRadius:2}}>{m.l}</span>;
}

// ─── sidebar: work_units with expandable runs ──────────────

function WorkUnitTree({t, accent, activeRun, onPickRun}) {
  const [open, setOpen] = React.useState({
    'define-architecture': true,
    'memory-spec': false,
    'policy-matrix': false,
    'research-planners': false,
  });
  return (
    <div style={{background:t.surface, borderRight:`1px solid ${t.border}`, display:'flex', flexDirection:'column', height:'100%'}}>
      <div style={{padding:'12px 14px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:8}}>
        <div style={{width:20, height:20, borderRadius:4, background:accent, display:'grid', placeItems:'center', fontFamily:RC_MONO, fontSize:10, fontWeight:600, color:'#1a1816'}}>J</div>
        <div style={{fontFamily:RC_MONO, fontSize:12, color:t.text}}>jeff</div>
        <TT t={t} kind="canonical"/>
      </div>
      <div style={{padding:'10px 12px 4px', fontFamily:RC_MONO, fontSize:9, letterSpacing:1.5, color:t.faint}}>WORK UNITS</div>
      <div style={{flex:1, overflow:'hidden'}}>
        {WU_TREE.map(wu => {
          const sc = rcStatusColor(wu.status, t, accent);
          const isOpen = open[wu.id];
          return (
            <div key={wu.id}>
              <div onClick={()=>setOpen({...open, [wu.id]: !isOpen})} style={{
                padding:'7px 10px', margin:'1px 6px', borderRadius:3, cursor:'pointer',
                display:'flex', alignItems:'center', gap:8,
                background:'transparent',
              }}>
                <span style={{fontFamily:RC_MONO, fontSize:9, color:t.faint, width:10}}>{isOpen?'▾':'▸'}</span>
                <span style={{width:6, height:6, borderRadius:3, background:sc, flexShrink:0}}/>
                <span style={{flex:1, fontSize:12, color:t.text, lineHeight:1.3}}>{wu.label}</span>
                <span style={{fontFamily:RC_MONO, fontSize:10, color:t.faint}}>{wu.runs.length}</span>
              </div>
              {isOpen && (
                <div style={{marginBottom:6}}>
                  {wu.runs.map(r => {
                    const active = r.id===activeRun;
                    const rc = rcStatusColor(r.status, t, accent);
                    return (
                      <div key={r.id} onClick={()=>onPickRun && onPickRun(r.id)} style={{
                        padding:'6px 10px 6px 30px', margin:'1px 6px', borderRadius:3, cursor:'pointer',
                        background: active?t.panel:'transparent',
                        border: active?`1px solid ${t.borderStrong}`:'1px solid transparent',
                      }}>
                        <div style={{display:'flex', alignItems:'center', gap:8}}>
                          <span style={{color:rc, fontFamily:RC_MONO, fontSize:10}}>{rcStatusGlyph(r.status)}</span>
                          <span style={{fontFamily:RC_MONO, fontSize:10, color:t.muted, flex:'0 0 52px'}}>{r.id}</span>
                          <span style={{fontSize:11, color:active?t.text:t.muted, flex:1, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>{r.label}</span>
                        </div>
                        <div style={{paddingLeft:70, fontFamily:RC_MONO, fontSize:9, color:t.faint, marginTop:2}}>{r.ts}</div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
      <div style={{padding:'8px 14px', borderTop:`1px solid ${t.border}`, fontFamily:RC_MONO, fontSize:9, color:t.faint}}>
        expand work_unit · click run to open chat
      </div>
    </div>
  );
}

// ─── layer panel (collapsed + expanded) ────────────────────

function LayerChatPanel({t, accent, layer, isOpen, onToggle}) {
  const c = rcStatusColor(layer.status, t, accent);
  return (
    <div style={{
      border:`1px solid ${isOpen?t.borderStrong:t.border}`, borderRadius:4,
      background:t.panel, marginBottom:8, overflow:'hidden',
    }}>
      <div onClick={onToggle} style={{
        padding:'10px 14px', cursor:'pointer', display:'flex', alignItems:'center', gap:10,
        background: isOpen ? t.surface : t.panel,
        borderBottom: isOpen ? `1px solid ${t.border}` : 'none',
      }}>
        <span style={{fontFamily:RC_MONO, fontSize:9, color:t.faint, width:10}}>{isOpen?'▾':'▸'}</span>
        <span style={{color:c, fontFamily:RC_MONO, fontSize:13, width:14, textAlign:'center'}}>{rcStatusGlyph(layer.status)}</span>
        <span style={{fontFamily:RC_MONO, fontSize:11, letterSpacing:1.5, color:t.text, textTransform:'uppercase', flex:'0 0 110px'}}>{layer.label}</span>
        <span style={{fontSize:12, color:t.muted, flex:1}}>{layer.sum}</span>
        <span style={{fontFamily:RC_MONO, fontSize:10, color:t.faint}}>{layer.dur}</span>
      </div>
      {isOpen && <LayerBody t={t} accent={accent} layerId={layer.id}/>}
    </div>
  );
}

// ─── layer body — Input / Reasoning / Output ───────────────

function LayerBody({t, accent, layerId}) {
  const [inputMode, setInputMode] = React.useState('summary');
  const lb = LAYER_BODY[layerId] || LAYER_BODY.execution;

  return (
    <div style={{padding:'12px 14px'}}>
      {/* INPUT */}
      <Subcard t={t} label="INPUT · context given to model" tone={t.derived} kindTag={<TT t={t} kind="derived"/>}
        right={
          <div style={{display:'flex', gap:4}}>
            {['summary','raw'].map(m => (
              <button key={m} onClick={()=>setInputMode(m)} style={{
                background:inputMode===m?t.text:'transparent', color:inputMode===m?t.panel:t.muted,
                border:`1px solid ${inputMode===m?t.text:t.border}`,
                fontFamily:RC_MONO, fontSize:9, padding:'2px 8px', borderRadius:2, cursor:'pointer',
                textTransform:'uppercase', letterSpacing:1,
              }}>{m}</button>
            ))}
          </div>
        }>
        {inputMode==='summary' ? (
          <div style={{padding:'10px 12px', display:'grid', gridTemplateColumns:'110px 1fr', gap:'5px 10px', fontFamily:RC_MONO, fontSize:11}}>
            {lb.input.map(([k,v,tag],i)=>(
              <React.Fragment key={i}>
                <div style={{color:t.faint}}>{k}</div>
                <div style={{color:t.text, display:'flex', alignItems:'center', gap:6, flexWrap:'wrap'}}>{v}{tag && <TT t={t} kind={tag}/>}</div>
              </React.Fragment>
            ))}
          </div>
        ) : (
          <div style={{padding:'10px 12px', fontFamily:RC_MONO, fontSize:11, lineHeight:1.7, color:t.text, background:t.surface, whiteSpace:'pre-wrap'}}>{lb.raw}</div>
        )}
      </Subcard>

      {/* REASONING */}
      <Subcard t={t} label="REASONING · model thought stream" tone={accent}
        kindTag={<span style={{fontFamily:RC_MONO, fontSize:9, letterSpacing:1, color:accent, border:`1px solid ${accent}55`, padding:'2px 6px', borderRadius:2}}>STREAM</span>}
        right={<span style={{fontFamily:RC_MONO, fontSize:10, color:t.faint}}>{lb.dur}</span>}>
        <div style={{padding:'10px 12px', background:t.surface, fontFamily:RC_MONO, fontSize:11, lineHeight:1.8, maxHeight:260, overflow:'hidden'}}>
          {lb.reasoning.map((l,i)=>{
            const color = l.k==='ok'?t.approved:l.k==='warn'?t.pending:l.k==='think'?t.memory:l.k==='stream'?t.text:t.muted;
            const glyph = l.k==='ok'?'✓':l.k==='warn'?'!':l.k==='think'?'›':l.k==='stream'?'▌':'·';
            return (
              <div key={i} style={{display:'flex', gap:8}}>
                <div style={{width:12, color, textAlign:'center'}}>{glyph}</div>
                <div style={{
                  flex:1,
                  color: l.k==='stream'?t.text:l.k==='think'?t.memory:t.muted,
                  fontStyle: l.k==='think'?'italic':'normal',
                  background: l.k==='stream'?`${accent}0d`:'transparent',
                  paddingLeft: l.k==='stream'?6:0,
                  borderLeft: l.k==='stream'?`2px solid ${accent}44`:'none',
                }}>{l.txt}</div>
              </div>
            );
          })}
        </div>
      </Subcard>

      {/* OUTPUT */}
      <Subcard t={t} label="OUTPUT · layer result" tone={t.support} kindTag={<TT t={t} kind={lb.outputKind || 'support'}/>}
        right={<span style={{fontFamily:RC_MONO, fontSize:10, color:t.faint}}>{lb.outputMeta}</span>}>
        <div style={{padding:'10px 12px'}}>{lb.output({t, accent})}</div>
      </Subcard>

      <div style={{display:'flex', gap:6, marginTop:6, fontFamily:RC_MONO, fontSize:10}}>
        <button style={rcPill(t)}>copy input</button>
        <button style={rcPill(t)}>copy output</button>
        <button style={rcPill(t)}>re-run with edited input</button>
        <span style={{marginLeft:'auto', color:t.faint, alignSelf:'center'}}>re-run = operator request, not mutation</span>
      </div>
    </div>
  );
}

function Subcard({t, label, kindTag, right, tone, children}) {
  return (
    <div style={{border:`1px solid ${t.border}`, borderRadius:3, marginBottom:8, overflow:'hidden'}}>
      <div style={{
        padding:'6px 10px', display:'flex', alignItems:'center', gap:8,
        background:`${tone||t.muted}10`, borderBottom:`1px solid ${t.border}`,
      }}>
        <span style={{fontFamily:RC_MONO, fontSize:9, letterSpacing:1.5, color:tone||t.muted, textTransform:'uppercase'}}>{label}</span>
        {kindTag}
        <span style={{marginLeft:'auto'}}>{right}</span>
      </div>
      <div>{children}</div>
    </div>
  );
}

function rcPill(t) {
  return {background:'transparent', border:`1px solid ${t.border}`, color:t.muted, fontFamily:RC_MONO, fontSize:10, padding:'3px 8px', borderRadius:3, cursor:'pointer'};
}

// ─── per-layer bodies ──────────────────────────────────────

const LAYER_BODY = {
  context: {
    dur:'0.4s elapsed', outputMeta:'support · not truth',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['trigger', 'operator request · 02:41'],
      ['state read', 'project + work_unit + run snapshot', 'canonical'],
    ],
    raw: '{\n  "trigger": {"kind":"operator_request", "text":"Draft the Memory section…"},\n  "scope": {"project":"jeff","work_unit":"define-architecture","run":"#r-0147"}\n}',
    reasoning: [
      {k:'note', txt:'reading state snapshot…'},
      {k:'ok',   txt:'snapshot fresh · no staleness'},
      {k:'note', txt:'retrieving committed memory matching work_unit'},
      {k:'ok',   txt:'2 memory refs loaded'},
      {k:'note', txt:'loading referenced spec sections'},
      {k:'ok',   txt:'4 docs parsed · 412 lines'},
    ],
    outputKind: 'support',
    output: ({t, accent}) => (
      <div style={{fontFamily:RC_MONO, fontSize:11, color:t.text, lineHeight:1.7}}>
        <div>assembled context bundle · 4 docs · 2 memory refs · 8,412 tokens</div>
        <div style={{color:t.muted, marginTop:4}}>→ handed to research, proposal</div>
      </div>
    ),
  },

  research: {
    dur:'2m 14s elapsed', outputMeta:'4 sources · 7 claims',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['question', '“how does memory stay distinct from canonical state in working agent systems?”'],
      ['context', 'context/r-0147 bundle', 'support'],
      ['policy', 'internet_research · auto · scoped'],
    ],
    raw: '{\n  "question": "how does memory stay distinct from canonical state…",\n  "max_sources": 6,\n  "provenance_required": true\n}',
    reasoning: [
      {k:'note',  txt:'searching: "memory vs state agentic systems"'},
      {k:'ok',    txt:'4 candidate sources'},
      {k:'note',  txt:'fetching blog.example.org/memory'},
      {k:'think', txt:'this source is secondary — treat as illustrative, not authoritative'},
      {k:'ok',    txt:'arxiv paper retrieved · peer-reviewed'},
      {k:'note',  txt:'cross-checking against internal MEMORY_SPEC.md'},
      {k:'ok',    txt:'3 internal sources aligned'},
      {k:'note',  txt:'extracting claims with provenance'},
    ],
    outputKind: 'support',
    output: ({t, accent}) => (
      <div>
        {[
          ['01', 'Memory design in agentic systems', 'blog.example.org/memory', 'derived'],
          ['02', 'State vs memory separation (paper)', 'arxiv.org/abs/2401.xxxxx', 'derived'],
          ['03', 'Jeff MEMORY_SPEC.md §1–4', 'internal', 'canonical'],
          ['04', 'mem#0093 contradiction log', 'internal', 'memory'],
        ].map(([n, title, src, k])=>(
          <div key={n} style={{padding:'6px 0', borderBottom:`1px solid ${t.border}`, display:'flex', gap:10, alignItems:'center'}}>
            <span style={{fontFamily:RC_MONO, fontSize:10, color:t.faint, width:20}}>{n}</span>
            <div style={{flex:1}}>
              <div style={{fontSize:12, color:t.text}}>{title}</div>
              <div style={{fontFamily:RC_MONO, fontSize:10, color:t.muted}}>{src}</div>
            </div>
            <TT t={t} kind={k}/>
          </div>
        ))}
        <div style={{marginTop:8, fontFamily:RC_MONO, fontSize:10, color:t.faint}}>→ 7 claims extracted, each with source-id</div>
      </div>
    ),
  },

  proposal: {
    dur:'18s', outputMeta:'2 of max 3',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['context', 'context bundle + research findings', 'support'],
      ['constraint', 'mutate_canonical_spec · approval required'],
    ],
    raw: '{\n  "max_options": 3,\n  "allow_zero": true,\n  "require_honesty": true\n}',
    reasoning: [
      {k:'note',  txt:'generating candidate paths…'},
      {k:'think', txt:'direct-draft is fine — no unresolved contradictions'},
      {k:'think', txt:'but mem#0093 was previously flagged; a cross-check pass is cheap insurance'},
      {k:'ok',    txt:'2 honest options · 3rd option would be ceremonial, dropping'},
      {k:'warn',  txt:'reminder · proposal may return 0–3 · fake alternatives forbidden'},
    ],
    outputKind: 'support',
    output: ({t, accent}) => (
      <div>
        {[
          {id:'opt-01', sel:false, label:'direct draft from committed memory spec', risk:'low', assume:'memory spec is settled', cost:'18s'},
          {id:'opt-02', sel:true,  label:'draft + cross-check against contradictions log', risk:'low', assume:'contradictions log fresh', cost:'32s'},
        ].map(o=>(
          <div key={o.id} style={{
            border:`${o.sel?2:1}px solid ${o.sel?accent:t.border}`, borderRadius:3, padding:10, marginBottom:6, background:t.surface,
          }}>
            <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:4}}>
              <span style={{fontFamily:RC_MONO, fontSize:10, color:o.sel?accent:t.muted}}>{o.id}</span>
              <span style={{fontSize:12, color:t.text, fontWeight:500}}>{o.label}</span>
              {o.sel && <span style={{fontFamily:RC_MONO, fontSize:9, letterSpacing:1, color:t.approved, border:`1px solid ${t.approved}55`, padding:'2px 6px', borderRadius:2}}>SELECTED ↓</span>}
            </div>
            <div style={{fontFamily:RC_MONO, fontSize:10, color:t.muted}}>risk {o.risk} · assumes {o.assume} · est {o.cost}</div>
          </div>
        ))}
      </div>
    ),
  },

  selection: {
    dur:'6s', outputMeta:'canonical · opt-02',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['options', 'opt-01, opt-02', 'support'],
      ['direction', 'project jeff · truth discipline', 'canonical'],
    ],
    raw: '{\n  "options": ["opt-01","opt-02"],\n  "allow_reject_all": true,\n  "allow_defer": true\n}',
    reasoning: [
      {k:'think', txt:'comparing against project direction: truth-first discipline'},
      {k:'think', txt:'opt-02 catches drift for marginal cost'},
      {k:'ok',    txt:'opt-02 selected · honest choice'},
      {k:'note',  txt:'selection is NOT execution permission · routing to governance'},
    ],
    outputKind: 'canonical',
    output: ({t, accent}) => (
      <div style={{fontFamily:RC_MONO, fontSize:12, color:t.text, lineHeight:1.7}}>
        <div>selected · <span style={{color:accent}}>opt-02</span></div>
        <div style={{color:t.muted, fontSize:11}}>draft + cross-check against contradictions log</div>
        <div style={{marginTop:8, color:t.faint, fontSize:10}}>non-selection outcomes also legal: reject-all · defer · escalate</div>
      </div>
    ),
  },

  governance: {
    dur:'1.2s', outputMeta:'canonical · approved',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['selection', 'opt-02', 'canonical'],
      ['policy', 'mutate_canonical_spec'],
    ],
    raw: '{\n  "rule": "mutate_canonical_spec",\n  "required": ["approval","readiness"]\n}',
    reasoning: [
      {k:'note',  txt:'invoking policy · mutate_canonical_spec'},
      {k:'note',  txt:'→ require_operator_approval'},
      {k:'ok',    txt:'operator approval · explicit'},
      {k:'note',  txt:'→ require_readiness'},
      {k:'ok',    txt:'context basis · fresh'},
      {k:'ok',    txt:'source provenance · ok'},
      {k:'ok',    txt:'conflicts · none'},
      {k:'ok',    txt:'scope anchor · work_unit ok'},
      {k:'ok',    txt:'readiness pass · 4/4'},
      {k:'think', txt:'approved ≠ applied — execution has not yet run'},
    ],
    outputKind: 'canonical',
    output: ({t, accent}) => (
      <div style={{display:'grid', gridTemplateColumns:'110px 1fr', gap:'5px 10px', fontFamily:RC_MONO, fontSize:11}}>
        <div style={{color:t.faint}}>decision</div><div style={{color:t.approved}}>✓ EXECUTION PERMITTED</div>
        <div style={{color:t.faint}}>approval</div><div style={{color:t.text}}>operator · explicit</div>
        <div style={{color:t.faint}}>readiness</div><div style={{color:t.text}}>4 / 4 pass</div>
        <div style={{color:t.faint}}>risk</div><div style={{color:t.pending}}>medium · canonical mutation</div>
        <div style={{color:t.faint}}>note</div><div style={{color:t.muted}}>approved is not applied; transition still required</div>
      </div>
    ),
  },

  execution: {
    dur:'1m 48s elapsed', outputMeta:'partial · not yet truth',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['action', 'draft §Memory of ARCHITECTURE.md', 'canonical'],
      ['permit', 'governance · approved + ready', 'canonical'],
      ['refs', 'MEMORY_SPEC.md · mem#0087 · mem#0093'],
    ],
    raw: '{\n  "action": {"kind":"draft_section","file":"ARCHITECTURE.md","section":"Memory"},\n  "permit_id":"gov#0147-1"\n}',
    reasoning: [
      {k:'note',   txt:'opening artifact path'},
      {k:'stream', txt:'## Memory'},
      {k:'stream', txt:'Memory stores useful, committed, retrievable knowledge.'},
      {k:'stream', txt:'Memory does not define current truth.'},
      {k:'think',  txt:'must keep the distinction explicit; don’t blur with state'},
      {k:'warn',   txt:'mem#0093 flagged earlier · cross-checking'},
      {k:'ok',     txt:'no unresolved conflict at this time'},
      {k:'stream', txt:'Canonical state may reference only committed memory IDs.'},
      {k:'note',   txt:'draft continues…'},
    ],
    outputKind: 'support',
    output: ({t, accent}) => (
      <div style={{fontFamily:RC_MONO, fontSize:12, color:t.text, lineHeight:1.7, padding:10, background:t.surface, border:`1px solid ${t.border}`, borderRadius:3}}>
        <div style={{color:t.muted}}>## Memory</div>
        <div>Memory stores useful, committed, retrievable knowledge.</div>
        <div>Memory does not define current truth.</div>
        <div>Canonical state may reference only <span style={{background:`${accent}33`, padding:'0 3px'}}>committed memory IDs</span>.</div>
        <div style={{color:t.faint, opacity:0.6}}>(continues…)</div>
      </div>
    ),
  },

  outcome: {
    dur:'pending', outputMeta:'awaits execution',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['expects', 'execution result · normalized'],
    ],
    raw: '{\n  "normalize": true,\n  "capture": ["artifacts","logs","measurements"]\n}',
    reasoning: [
      {k:'note', txt:'waiting for execution to complete'},
      {k:'note', txt:'will normalize: artifacts, logs, timing, observable changes'},
    ],
    outputKind: 'support',
    output: ({t}) => <div style={{fontFamily:RC_MONO, fontSize:11, color:t.faint}}>no outcome recorded yet</div>,
  },

  evaluation: {
    dur:'pending', outputMeta:'awaits outcome',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['goal', 'draft §Memory matches canonical MEMORY_SPEC'],
      ['outcome', '—'],
    ],
    raw: '{\n  "verdicts": ["success","degraded","partial","inconclusive","failed","recovery","revalidate"]\n}',
    reasoning: [
      {k:'note', txt:'will compare outcome to goal + policy'},
      {k:'note', txt:'may emit: success, degraded, partial, inconclusive, recovery-needed'},
    ],
    outputKind: 'canonical',
    output: ({t}) => <div style={{fontFamily:RC_MONO, fontSize:11, color:t.faint}}>verdict not yet formed</div>,
  },

  memory: {
    dur:'pending', outputMeta:'0 candidates',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['source', 'evaluation verdict · pending'],
    ],
    raw: '{\n  "commit_policy": "auto · require_evidence_link",\n  "candidate_max": 3\n}',
    reasoning: [
      {k:'note',  txt:'will only accept candidates with evidence link'},
      {k:'think', txt:'memory is not truth · canonical state may only reference committed memory IDs'},
    ],
    outputKind: 'memory',
    output: ({t}) => <div style={{fontFamily:RC_MONO, fontSize:11, color:t.faint}}>no memory candidates yet</div>,
  },

  transition: {
    dur:'pending', outputMeta:'no truth change yet',
    input: [
      ['scope', 'jeff / define-architecture / #r-0147'],
      ['intent', 'apply §Memory into ARCHITECTURE.md'],
      ['basis', 'evaluation verdict + committed memory'],
    ],
    raw: '{\n  "intent": "apply_section",\n  "preconditions": ["evaluation=success","memory=committed_or_empty"]\n}',
    reasoning: [
      {k:'note',  txt:'transitions are the only canonical truth mutation path'},
      {k:'think', txt:'will not fire unless evaluation supports it'},
    ],
    outputKind: 'canonical',
    output: ({t}) => <div style={{fontFamily:RC_MONO, fontSize:11, color:t.faint}}>no transition emitted · truth unchanged</div>,
  },
};

// ─── chat header + scope ───────────────────────────────────

function RunChatHeader({t, accent, runId='#r-0147'}) {
  return (
    <>
      <div style={{padding:'12px 20px', borderBottom:`1px solid ${t.border}`, background:t.panel, display:'flex', alignItems:'center', gap:12}}>
        <div style={{fontFamily:RC_MONO, fontSize:10, color:t.faint, letterSpacing:1.5}}>RUN</div>
        <div style={{fontFamily:RC_MONO, fontSize:13, color:t.text}}>
          <span style={{fontWeight:500}}>jeff</span>
          <span style={{margin:'0 6px', color:t.faint}}>/</span>
          <span style={{color:accent, fontWeight:500}}>define-architecture</span>
          <span style={{margin:'0 6px', color:t.faint}}>/</span>
          <span style={{fontWeight:500}}>{runId}</span>
        </div>
        <span style={{fontFamily:RC_MONO, fontSize:9, letterSpacing:1, color:accent, border:`1px solid ${accent}55`, padding:'2px 6px', borderRadius:2}}>● EXECUTING</span>
        <div style={{marginLeft:'auto', fontFamily:RC_MONO, fontSize:10, color:t.faint}}>elapsed 4m 12s</div>
      </div>
    </>
  );
}

// ─── full run-chat screen ──────────────────────────────────

function RunChatScreen({tweaks}) {
  const t = (window.__JEFF_THEMES || {})[tweaks.theme || 'light'] || fallbackRcTheme(tweaks.theme);
  const accent = (window.__JEFF_ACCENTS || {})[tweaks.accent || 'amber'] || '#d4a574';
  const [activeRun, setActiveRun] = React.useState('#r-0147');
  const [openLayer, setOpenLayer] = React.useState('execution');

  return (
    <div data-screen-label="run-chat" style={{width:'100%', height:'100%', display:'flex', background:t.bg, fontFamily:RC_SANS, color:t.text}}>
      <div style={{width:260, flexShrink:0}}>
        <WorkUnitTree t={t} accent={accent} activeRun={activeRun} onPickRun={setActiveRun}/>
      </div>
      <div style={{flex:1, display:'flex', flexDirection:'column', minWidth:0}}>
        <RunChatHeader t={t} accent={accent} runId={activeRun}/>

        <div style={{flex:1, overflow:'hidden', padding:'14px 20px'}}>
          {/* Operator message at the top */}
          <div style={{padding:'12px 14px', marginBottom:10, background:t.surface, border:`1px solid ${t.border}`, borderRadius:4}}>
            <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:4}}>
              <span style={{fontFamily:RC_MONO, fontSize:9, letterSpacing:1.5, color:t.muted, textTransform:'uppercase'}}>operator</span>
              <span style={{marginLeft:'auto', fontFamily:RC_MONO, fontSize:10, color:t.faint}}>02:41 · request</span>
            </div>
            <div style={{fontSize:13, color:t.text, lineHeight:1.5}}>
              Draft the Memory section of ARCHITECTURE.md using the committed memory spec. Keep the distinction between memory and canonical state explicit.
            </div>
          </div>

          {/* Loop header strip */}
          <div style={{padding:'8px 12px', background:t.panel, border:`1px solid ${t.border}`, borderRadius:4, marginBottom:8, display:'flex', alignItems:'center', gap:10}}>
            <span style={{fontFamily:RC_MONO, fontSize:10, letterSpacing:1.5, color:t.muted}}>LOOP · 10 LAYERS</span>
            <span style={{fontFamily:RC_MONO, fontSize:10, color:t.faint}}>5 done · 1 active · 4 pending</span>
            <span style={{marginLeft:'auto', fontFamily:RC_MONO, fontSize:10, color:t.faint}}>click a layer to inspect input / reasoning / output</span>
          </div>

          {/* Layer panels */}
          {LAYERS.map(l => (
            <LayerChatPanel key={l.id} t={t} accent={accent} layer={l}
              isOpen={openLayer===l.id}
              onToggle={()=>setOpenLayer(openLayer===l.id?null:l.id)}/>
          ))}
        </div>
      </div>
    </div>
  );
}

function fallbackRcTheme(mode) {
  return mode==='dark' ? {
    bg:'#17150f', surface:'#1f1c15', panel:'#26221a', rail:'#1a1712',
    border:'#332e24', borderStrong:'#4a4335',
    text:'#ebe4d3', muted:'#9a9283', faint:'#6b6558',
    approved:'#8ab06a', blocked:'#d07860', pending:'#e0a75a', degraded:'#c89860',
    canonical:'#ebe4d3', support:'#c9a878', derived:'#a89d8a', memory:'#b0a0c8',
  } : {
    bg:'#f5f2ec', surface:'#faf8f3', panel:'#ffffff', rail:'#ede8dd',
    border:'#e0dacb', borderStrong:'#c9c1ae',
    text:'#1a1816', muted:'#6b6558', faint:'#9a9283',
    approved:'#5c7a4c', blocked:'#a8553a', pending:'#c48a3a', degraded:'#a87c3a',
    canonical:'#1a1816', support:'#8b7355', derived:'#7a7064', memory:'#8578a0',
  };
}

window.RunChatScreen = RunChatScreen;
// Keep a no-op alias so the main HTML keeps loading even if it still refs LayerDeepDive.
window.LayerDeepDive = RunChatScreen;
