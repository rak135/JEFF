// Jeff wireframe frames. Theme + layout + density + accent driven.
// Truthfulness contract: every pane labels its truth class (canonical/support/derived/local).

const THEMES = {
  light: {
    bg: '#f5f2ec',
    surface: '#faf8f3',
    panel: '#ffffff',
    rail: '#ede8dd',
    border: '#e0dacb',
    borderStrong: '#c9c1ae',
    text: '#1a1816',
    muted: '#6b6558',
    faint: '#9a9283',
    mono: '#3a3630',
    // state colors — muted, warm
    approved: '#5c7a4c',
    blocked: '#a8553a',
    pending: '#c48a3a',
    degraded: '#a87c3a',
    canonical: '#1a1816',
    support: '#8b7355',
    derived: '#7a7064',
    memory: '#8578a0',
  },
  dark: {
    bg: '#17150f',
    surface: '#1f1c15',
    panel: '#26221a',
    rail: '#1a1712',
    border: '#332e24',
    borderStrong: '#4a4335',
    text: '#ebe4d3',
    muted: '#9a9283',
    faint: '#6b6558',
    mono: '#d4cdba',
    approved: '#8ab06a',
    blocked: '#d07860',
    pending: '#e0a75a',
    degraded: '#c89860',
    canonical: '#ebe4d3',
    support: '#c9a878',
    derived: '#a89d8a',
    memory: '#b0a0c8',
  },
};

const ACCENTS = {
  amber: '#d4a574',
  sage:  '#8ba678',
  slate: '#7a8a9c',
};

// ─── primitives ─────────────────────────────────────────────

const mono = 'JetBrains Mono, ui-monospace, monospace';
const sans = 'IBM Plex Sans, system-ui, sans-serif';

function StateDot({color, size=6}) {
  return <span style={{display:'inline-block', width:size, height:size, borderRadius:size, background:color, verticalAlign:'middle'}}/>;
}

function TruthTag({kind, t}) {
  // kind: canonical | support | derived | memory | local
  const map = {
    canonical: {label:'CANONICAL', color:t.canonical},
    support:   {label:'SUPPORT',   color:t.support},
    derived:   {label:'DERIVED',   color:t.derived},
    memory:    {label:'MEMORY',    color:t.memory},
    local:     {label:'UI-LOCAL',  color:t.faint},
  };
  const m = map[kind];
  return (
    <span style={{fontFamily:mono, fontSize:9, letterSpacing:1.2, color:m.color,
      border:`1px solid ${m.color}55`, padding:'2px 6px', borderRadius:2, textTransform:'uppercase'}}>
      {m.label}
    </span>
  );
}

function PanelHeader({title, truth, t, right, small}) {
  return (
    <div style={{
      display:'flex', alignItems:'center', justifyContent:'space-between',
      padding: small ? '8px 12px' : '12px 16px',
      borderBottom:`1px solid ${t.border}`,
      background:t.panel,
    }}>
      <div style={{display:'flex', alignItems:'center', gap:10}}>
        <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.muted, textTransform:'uppercase'}}>{title}</div>
        {truth && <TruthTag kind={truth} t={t}/>}
      </div>
      {right}
    </div>
  );
}

// ─── projects rail (left) ───────────────────────────────────

function ProjectsRail({t, accent, density, activeProject='jeff'}) {
  const pad = density==='dense' ? '6px 10px' : '9px 12px';
  const projects = [
    {id:'jeff',              label:'jeff',              sub:'personal work system', runs:3, status:'active'},
    {id:'home_energy',       label:'home_energy_upgrade', sub:'research · heat pumps', runs:1, status:'idle'},
    {id:'book_research',     label:'book_research',     sub:'evidence synthesis',   runs:0, status:'idle'},
    {id:'client_proposal',   label:'client_proposal',   sub:'draft · blocked',      runs:1, status:'blocked'},
  ];
  return (
    <div style={{background:t.rail, borderRight:`1px solid ${t.border}`, display:'flex', flexDirection:'column', height:'100%'}}>
      <div style={{padding:'14px 14px 10px', borderBottom:`1px solid ${t.border}`}}>
        <div style={{display:'flex', alignItems:'center', gap:8}}>
          <div style={{width:22, height:22, borderRadius:4, background:accent, display:'grid', placeItems:'center',
            fontFamily:mono, fontSize:11, fontWeight:600, color:'#1a1816'}}>J</div>
          <div style={{fontFamily:mono, fontSize:13, color:t.text, fontWeight:500, letterSpacing:-0.2}}>jeff</div>
          <div style={{marginLeft:'auto', fontFamily:mono, fontSize:9, color:t.faint, letterSpacing:1}}>v1</div>
        </div>
      </div>
      <div style={{padding:'10px 12px 6px', display:'flex', alignItems:'center', justifyContent:'space-between'}}>
        <div style={{fontFamily:mono, fontSize:9, letterSpacing:1.5, color:t.faint}}>PROJECTS</div>
        <button style={{background:'transparent', border:`1px solid ${t.border}`, color:t.muted, fontFamily:mono, fontSize:10, padding:'2px 6px', borderRadius:3, cursor:'pointer'}}>+ new</button>
      </div>
      <div style={{flex:1, overflow:'hidden'}}>
        {projects.map(p => {
          const active = p.id === activeProject;
          const statusColor = p.status==='active' ? t.approved : p.status==='blocked' ? t.blocked : t.faint;
          return (
            <div key={p.id} style={{
              padding:pad, margin:'2px 8px',
              background: active ? t.panel : 'transparent',
              border: active ? `1px solid ${t.borderStrong}` : '1px solid transparent',
              borderRadius:4, cursor:'pointer',
            }}>
              <div style={{display:'flex', alignItems:'center', gap:8}}>
                <StateDot color={statusColor}/>
                <div style={{fontFamily:mono, fontSize:12, color:active?t.text:t.muted, fontWeight:active?500:400}}>{p.label}</div>
                <div style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>{p.runs||'—'}</div>
              </div>
              {density!=='dense' && <div style={{fontSize:11, color:t.faint, marginLeft:14, marginTop:2}}>{p.sub}</div>}
            </div>
          );
        })}
      </div>
      <div style={{padding:'10px 14px', borderTop:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:8}}>
        <div style={{width:20, height:20, borderRadius:10, background:t.border}}/>
        <div style={{fontSize:11, color:t.muted}}>operator</div>
        <div style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>⚙</div>
      </div>
    </div>
  );
}

// ─── work units sub-rail ─────────────────────────────────────

function WorkUnitsPanel({t, density, activeWu='define-architecture'}) {
  const units = [
    {id:'define-architecture', label:'define canonical ARCHITECTURE.md', runs:3, status:'active', lastRun:'run · 7m ago'},
    {id:'memory-spec',         label:'memory spec draft',                runs:2, status:'idle',   lastRun:'run · 2h ago'},
    {id:'policy-matrix',       label:'policy & approval matrix',         runs:1, status:'blocked', lastRun:'blocked · approval'},
    {id:'research-planners',   label:'survey planning engines',          runs:1, status:'done',   lastRun:'evaluated · degraded'},
  ];
  return (
    <div style={{background:t.surface, display:'flex', flexDirection:'column', height:'100%', borderRight:`1px solid ${t.border}`}}>
      <PanelHeader title="work units · jeff" truth="canonical" t={t}
        right={<button style={{background:'transparent', border:`1px solid ${t.border}`, color:t.muted, fontFamily:mono, fontSize:10, padding:'2px 6px', borderRadius:3, cursor:'pointer'}}>+ new</button>}/>
      <div style={{padding:'8px 10px 4px'}}>
        <div style={{position:'relative'}}>
          <input placeholder="search history…" style={{
            width:'100%', background:t.panel, border:`1px solid ${t.border}`,
            color:t.text, padding:'6px 8px 6px 26px', borderRadius:4,
            fontFamily:mono, fontSize:11, outline:'none',
          }}/>
          <span style={{position:'absolute', left:8, top:6, fontFamily:mono, fontSize:11, color:t.faint}}>⌕</span>
        </div>
      </div>
      <div style={{padding:'6px 10px 4px'}}>
        <div style={{fontFamily:mono, fontSize:9, letterSpacing:1.5, color:t.faint, padding:'6px 4px'}}>ACTIVE · 2</div>
      </div>
      {units.map(u=>{
        const active = u.id===activeWu;
        const sc = u.status==='active'?t.approved:u.status==='blocked'?t.blocked:u.status==='done'?t.degraded:t.faint;
        return (
          <div key={u.id} style={{
            padding: density==='dense' ? '8px 10px' : '10px 12px',
            margin:'1px 6px', borderRadius:3, cursor:'pointer',
            background: active ? t.panel : 'transparent',
            border: active ? `1px solid ${t.border}` : '1px solid transparent',
          }}>
            <div style={{display:'flex', alignItems:'flex-start', gap:8}}>
              <StateDot color={sc} size={6}/>
              <div style={{flex:1, minWidth:0}}>
                <div style={{fontSize:12, color:active?t.text:t.muted, fontWeight:active?500:400, lineHeight:1.3}}>{u.label}</div>
                <div style={{display:'flex', gap:8, marginTop:3, fontFamily:mono, fontSize:10, color:t.faint}}>
                  <span>{u.runs} run{u.runs!==1?'s':''}</span>
                  <span>·</span>
                  <span>{u.lastRun}</span>
                </div>
              </div>
            </div>
          </div>
        );
      })}
      <div style={{padding:'12px 14px 4px'}}>
        <div style={{fontFamily:mono, fontSize:9, letterSpacing:1.5, color:t.faint}}>FOLDERS</div>
      </div>
      {['specs', 'research', 'handoffs'].map(f=>(
        <div key={f} style={{padding:'6px 14px', fontFamily:mono, fontSize:11, color:t.muted, display:'flex', gap:8}}>
          <span style={{color:t.faint}}>▸</span>{f}
        </div>
      ))}
    </div>
  );
}

// ─── conversation (center) ──────────────────────────────────

function Scopebar({t, accent, density}) {
  return (
    <div style={{
      padding: density==='dense' ? '8px 16px' : '12px 18px',
      borderBottom:`1px solid ${t.border}`,
      background:t.panel, display:'flex', alignItems:'center', gap:10, flexWrap:'wrap'
    }}>
      <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.faint}}>SCOPE</div>
      <div style={{fontFamily:mono, fontSize:12, color:t.text}}>
        <span style={{fontWeight:500}}>jeff</span>
        <span style={{margin:'0 6px', color:t.faint}}>/</span>
        <span style={{fontWeight:500, color:accent}}>define-architecture</span>
        <span style={{margin:'0 6px', color:t.faint}}>/</span>
        <span style={{fontWeight:500}}>#r-0147</span>
      </div>
      <div style={{marginLeft:'auto', display:'flex', gap:6}}>
        <span style={{fontFamily:mono, fontSize:10, color:t.approved, border:`1px solid ${t.approved}55`, padding:'2px 6px', borderRadius:2}}>
          <StateDot color={t.approved} size={5}/> &nbsp;ISOLATED
        </span>
        <span style={{fontFamily:mono, fontSize:10, color:t.muted, border:`1px solid ${t.border}`, padding:'2px 6px', borderRadius:2}}>
          policy · default
        </span>
      </div>
    </div>
  );
}

function Message({role, t, accent, children, meta, truth, density}) {
  const isUser = role==='user';
  const isSys  = role==='system';
  const isJeff = role==='jeff';
  const pad = density==='dense' ? '10px 16px' : '16px 18px';
  return (
    <div style={{
      padding:pad, borderBottom:`1px solid ${t.border}`,
      background: isUser ? t.surface : t.panel,
    }}>
      <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:6}}>
        <div style={{
          fontFamily:mono, fontSize:10, letterSpacing:1.5,
          color: isUser ? t.muted : isJeff ? accent : t.pending,
          textTransform:'uppercase'
        }}>
          {isUser?'operator':isJeff?'jeff':'system'}
        </div>
        {truth && <TruthTag kind={truth} t={t}/>}
        {meta && <div style={{fontFamily:mono, fontSize:10, color:t.faint, marginLeft:'auto'}}>{meta}</div>}
      </div>
      <div style={{fontSize: density==='dense'?13:14, lineHeight:1.55, color:t.text}}>{children}</div>
    </div>
  );
}

function Stage({t, label, state, accent}) {
  // state: done | active | pending | blocked | skipped
  const map = {
    done:    {c:t.approved, s:'✓', l:'COMPLETE'},
    active:  {c:accent,     s:'●', l:'IN PROGRESS'},
    pending: {c:t.pending,  s:'○', l:'PENDING'},
    blocked: {c:t.blocked,  s:'✕', l:'BLOCKED'},
    skipped: {c:t.faint,    s:'—', l:'SKIPPED'},
    needs:   {c:t.pending,  s:'!', l:'NEEDS APPROVAL'},
  };
  const m = map[state];
  return (
    <div style={{display:'flex', alignItems:'center', gap:8, padding:'4px 0'}}>
      <div style={{width:18, textAlign:'center', color:m.c, fontFamily:mono, fontSize:12}}>{m.s}</div>
      <div style={{flex:1, fontFamily:mono, fontSize:11, color:t.text}}>{label}</div>
      <div style={{fontFamily:mono, fontSize:9, color:m.c, letterSpacing:1}}>{m.l}</div>
    </div>
  );
}

function LoopProgress({t, accent, stages}) {
  return (
    <div style={{
      margin:'8px 0', padding:'10px 14px',
      background:t.surface, border:`1px solid ${t.border}`, borderRadius:4,
    }}>
      <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:6}}>
        <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.muted}}>RUN · #r-0147 · LOOP</div>
        <div style={{fontFamily:mono, fontSize:10, color:t.faint}}>elapsed 4m 12s</div>
      </div>
      {stages.map((s,i)=><Stage key={i} t={t} accent={accent} {...s}/>)}
    </div>
  );
}

function Composer({t, accent, density, placeholder='Ask within project jeff / define-architecture…'}) {
  return (
    <div style={{padding:density==='dense'?'10px 14px':'14px 16px', borderTop:`1px solid ${t.border}`, background:t.panel}}>
      <div style={{border:`1px solid ${t.borderStrong}`, borderRadius:6, background:t.surface, padding:'10px 12px'}}>
        <div style={{fontSize:13, color:t.faint, minHeight:density==='dense'?40:56, lineHeight:1.5}}>{placeholder}</div>
        <div style={{display:'flex', alignItems:'center', gap:6, marginTop:6, paddingTop:8, borderTop:`1px solid ${t.border}`}}>
          <button style={pillBtn(t)}>＋ attach</button>
          <button style={pillBtn(t)}>⌕ research</button>
          <button style={pillBtn(t)}>⎇ plan</button>
          <div style={{marginLeft:'auto', display:'flex', alignItems:'center', gap:8}}>
            <span style={{fontFamily:mono, fontSize:10, color:t.faint}}>⌘↵ submit as <b style={{color:t.muted}}>proposal request</b></span>
            <button style={{
              background:accent, border:'none', color:'#1a1816',
              fontFamily:mono, fontSize:11, padding:'6px 12px', borderRadius:3, cursor:'pointer', fontWeight:500
            }}>submit →</button>
          </div>
        </div>
      </div>
      <div style={{display:'flex', gap:8, marginTop:8, fontFamily:mono, fontSize:10, color:t.faint}}>
        <span>operator input is a <b style={{color:t.muted}}>request</b>, not truth mutation</span>
      </div>
    </div>
  );
}

function pillBtn(t) {
  return {
    background:'transparent', border:`1px solid ${t.border}`, color:t.muted,
    fontFamily:mono, fontSize:10, padding:'4px 8px', borderRadius:3, cursor:'pointer'
  };
}

// ─── inspector (right) ──────────────────────────────────────

function Inspector({t, accent, density, kind='artifact'}) {
  return (
    <div style={{background:t.surface, display:'flex', flexDirection:'column', height:'100%', borderLeft:`1px solid ${t.border}`}}>
      <div style={{display:'flex', borderBottom:`1px solid ${t.border}`, background:t.panel}}>
        {['artifacts','inspect','trace','memory'].map((tab,i)=>(
          <div key={tab} style={{
            padding:'10px 14px', fontFamily:mono, fontSize:11, letterSpacing:0.3,
            color: i===0?t.text:t.muted, cursor:'pointer',
            borderBottom: i===0?`2px solid ${accent}`:`2px solid transparent`,
          }}>{tab}</div>
        ))}
      </div>
      {kind==='artifact' && <ArtifactBody t={t} accent={accent} density={density}/>}
      {kind==='inspect'  && <InspectBody t={t} accent={accent}/>}
      {kind==='governance' && <GovernanceBody t={t} accent={accent}/>}
    </div>
  );
}

function ArtifactBody({t, accent, density}) {
  return (
    <>
      <div style={{padding:'12px 14px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:8}}>
        <div style={{flex:1}}>
          <div style={{fontSize:13, color:t.text, fontWeight:500}}>ARCHITECTURE.md</div>
          <div style={{fontFamily:mono, fontSize:10, color:t.faint, marginTop:2}}>draft · evaluation pending</div>
        </div>
        <TruthTag kind="support" t={t}/>
      </div>
      <div style={{flex:1, overflow:'hidden', padding:'14px 16px', fontFamily:mono, fontSize:11, lineHeight:1.7, color:t.text}}>
        <div style={{color:t.muted}}># Jeff — Canonical Architecture</div>
        <div style={{height:8}}/>
        <div style={{color:t.faint}}>## Purpose</div>
        <div style={{color:t.text, opacity:0.85}}>This document defines the authoritative architecture of Jeff v1.</div>
        <div style={{height:8}}/>
        <div style={{color:t.faint}}>## Layers</div>
        <div style={{color:t.text, opacity:0.85}}>Jeff has nine top-level layers:</div>
        <div style={{paddingLeft:12, color:t.text, opacity:0.85}}>
          <div>- Core</div>
          <div>- Governance</div>
          <div>- Cognitive</div>
          <div>- Action</div>
          <div style={{color:accent}}>- Memory <span style={{color:t.faint, fontSize:10}}>← cursor</span></div>
          <div>- Orchestration</div>
          <div>- Interface</div>
        </div>
        <div style={{height:8}}/>
        <div style={{color:t.faint}}>## Core Principle</div>
        <div style={{color:t.text, opacity:0.85}}>Transitions are the only canonical truth mutation path.</div>
      </div>
      <div style={{padding:'10px 14px', borderTop:`1px solid ${t.border}`, display:'flex', gap:6, background:t.panel}}>
        <button style={pillBtn(t)}>open</button>
        <button style={pillBtn(t)}>copy</button>
        <button style={pillBtn(t)}>diff</button>
        <div style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>not yet truth · evaluation required</div>
      </div>
    </>
  );
}

function InspectBody({t, accent}) {
  const rows = [
    ['run.id', '#r-0147', 'canonical'],
    ['run.status', 'executing', 'canonical'],
    ['outcome.state', '—', 'canonical'],
    ['evaluation.verdict', '—', 'canonical'],
    ['selection.option_id', 'opt-02', 'canonical'],
    ['governance.approval', 'auto · policy-default', 'canonical'],
    ['governance.readiness', 'pass', 'canonical'],
    ['context.sources', '4 docs · 2 memory', 'derived'],
    ['memory.linked', '3 committed', 'memory'],
  ];
  return (
    <div style={{flex:1, overflow:'hidden', padding:'4px 0'}}>
      {rows.map(([k,v,kind],i)=>(
        <div key={i} style={{padding:'8px 14px', display:'flex', gap:10, borderBottom:`1px solid ${t.border}`}}>
          <div style={{fontFamily:mono, fontSize:10, color:t.faint, flex:'0 0 150px'}}>{k}</div>
          <div style={{fontFamily:mono, fontSize:11, color:t.text, flex:1}}>{v}</div>
          <TruthTag kind={kind} t={t}/>
        </div>
      ))}
    </div>
  );
}

function GovernanceBody({t, accent}) {
  return (
    <div style={{padding:14, display:'flex', flexDirection:'column', gap:10}}>
      <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.faint}}>GOVERNANCE · pre-execution</div>

      <div style={{border:`1px solid ${t.pending}`, background:`${t.pending}11`, borderRadius:4, padding:'10px 12px'}}>
        <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:6}}>
          <StateDot color={t.pending}/>
          <div style={{fontFamily:mono, fontSize:11, color:t.pending, letterSpacing:1}}>APPROVAL · REQUIRED</div>
        </div>
        <div style={{fontSize:12, color:t.text, lineHeight:1.5}}>
          Selected option modifies canonical spec files. Policy requires explicit operator approval before execution.
        </div>
        <div style={{display:'flex', gap:6, marginTop:10}}>
          <button style={{
            background:t.approved, color:'#fff', border:'none',
            fontFamily:mono, fontSize:11, padding:'6px 10px', borderRadius:3, cursor:'pointer'
          }}>approve</button>
          <button style={pillBtn(t)}>reject</button>
          <button style={pillBtn(t)}>defer</button>
        </div>
        <div style={{marginTop:8, fontFamily:mono, fontSize:10, color:t.faint}}>approve = request accepted · not yet applied</div>
      </div>

      <div style={{border:`1px solid ${t.border}`, borderRadius:4, padding:'10px 12px', background:t.panel}}>
        <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.faint, marginBottom:6}}>READINESS</div>
        {[
          ['context basis', 'fresh', t.approved],
          ['source provenance', 'ok · 4 sources', t.approved],
          ['conflicts', 'none', t.approved],
          ['scope anchor', 'work_unit ok', t.approved],
        ].map(([k,v,c],i)=>(
          <div key={i} style={{display:'flex', gap:8, padding:'4px 0', fontFamily:mono, fontSize:11}}>
            <div style={{flex:1, color:t.muted}}>{k}</div>
            <div style={{color:t.text}}>{v}</div>
            <StateDot color={c}/>
          </div>
        ))}
      </div>

      <div style={{border:`1px solid ${t.border}`, borderRadius:4, padding:'10px 12px', background:t.panel}}>
        <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.faint, marginBottom:6}}>POLICY · invoked</div>
        <div style={{fontFamily:mono, fontSize:11, color:t.text, lineHeight:1.6}}>
          <div>rule · mutate_canonical_spec</div>
          <div style={{color:t.muted, paddingLeft:12}}>→ require_operator_approval</div>
          <div style={{color:t.muted, paddingLeft:12}}>→ require_readiness</div>
          <div style={{color:t.muted, paddingLeft:12}}>→ emit_transition_intent</div>
        </div>
      </div>
    </div>
  );
}

// ─── screens ────────────────────────────────────────────────

function EmptyScreen({t, accent, density}) {
  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.panel}}>
      <Scopebar t={t} accent={accent} density={density}/>
      <div style={{flex:1, display:'flex', alignItems:'center', justifyContent:'center', padding:40}}>
        <div style={{maxWidth:520, textAlign:'center'}}>
          <div style={{fontFamily:mono, fontSize:11, color:t.faint, letterSpacing:2, marginBottom:14}}>NEW RUN · #r-0148</div>
          <div style={{fontSize:26, color:t.text, letterSpacing:-0.6, fontWeight:500, marginBottom:10, lineHeight:1.25}}>
            What should Jeff work on inside <span style={{color:accent}}>define-architecture</span>?
          </div>
          <div style={{fontSize:13, color:t.muted, lineHeight:1.6, marginBottom:24}}>
            Your input becomes a <b style={{color:t.text}}>request</b>. Jeff will assemble truth-first context, generate 0–3 honest proposals, and only act after governance passes.
          </div>
          <div style={{display:'flex', gap:8, justifyContent:'center', flexWrap:'wrap'}}>
            {['continue layer 3 draft', 'research planning engines', 'review memory for contradictions', 'synthesize recent evaluation'].map(s=>(
              <div key={s} style={{
                padding:'8px 12px', background:t.surface, border:`1px solid ${t.border}`,
                borderRadius:4, fontFamily:mono, fontSize:11, color:t.muted, cursor:'pointer'
              }}>{s}</div>
            ))}
          </div>
        </div>
      </div>
      <Composer t={t} accent={accent} density={density}/>
    </div>
  );
}

function ActiveScreen({t, accent, density}) {
  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.panel, minWidth:0}}>
      <Scopebar t={t} accent={accent} density={density}/>
      <div style={{flex:1, overflow:'hidden'}}>
        <Message role="user" t={t} accent={accent} density={density} meta="02:41 · run #r-0147">
          Draft the Memory section of ARCHITECTURE.md using the committed memory spec. Keep the distinction between memory and canonical state explicit.
        </Message>
        <Message role="system" t={t} accent={accent} density={density} truth="canonical" meta="context assembled">
          <div style={{fontFamily:mono, fontSize:11, color:t.muted}}>
            <div>→ read state · jeff/define-architecture/r-0147</div>
            <div>→ retrieved 4 docs · 2 committed memory refs</div>
            <div>→ no unresolved contradictions</div>
          </div>
        </Message>
        <Message role="jeff" t={t} accent={accent} density={density} truth="support" meta="proposal · 2 of 2">
          <div style={{marginBottom:6}}>Two honest options. Selection ≠ execution.</div>
          <div style={{border:`1px solid ${t.border}`, borderRadius:4, padding:10, marginBottom:6, background:t.surface}}>
            <div style={{fontFamily:mono, fontSize:11, color:accent}}>opt-01 · direct draft from committed memory spec</div>
            <div style={{fontSize:12, color:t.muted, marginTop:4}}>Low risk. No new research pass. Assumes memory spec is settled.</div>
          </div>
          <div style={{border:`2px solid ${accent}`, borderRadius:4, padding:10, background:t.surface}}>
            <div style={{fontFamily:mono, fontSize:11, color:accent}}>opt-02 · draft + cross-check against contradictions log  <span style={{color:t.approved}}>✓ selected</span></div>
            <div style={{fontSize:12, color:t.muted, marginTop:4}}>Adds one validation pass. Catches drift. Still bounded.</div>
          </div>
        </Message>
        <div style={{padding:'0 16px'}}>
          <LoopProgress t={t} accent={accent} stages={[
            {label:'context assembled',      state:'done'},
            {label:'proposal · 2 options',   state:'done'},
            {label:'selection · opt-02',     state:'done'},
            {label:'governance · approval',  state:'done'},
            {label:'governance · readiness', state:'done'},
            {label:'execution · drafting',   state:'active'},
            {label:'outcome',                state:'pending'},
            {label:'evaluation',             state:'pending'},
            {label:'transition',             state:'pending'},
          ]}/>
        </div>
        <Message role="jeff" t={t} accent={accent} density={density} truth="support" meta="streaming · execution output">
          <div style={{fontFamily:mono, fontSize:12, color:t.text, lineHeight:1.7}}>
            <div style={{color:t.faint}}>## Memory</div>
            <div>Memory stores useful, committed, retrievable knowledge. Memory does not define current truth.</div>
            <div>Only the Memory module creates memory candidates. Canonical state may reference only <span style={{background:`${accent}22`, padding:'0 3px'}}>committed memory IDs</span><span style={{display:'inline-block', width:8, height:14, background:accent, verticalAlign:'middle', marginLeft:2, animation:'none'}}/></div>
          </div>
        </Message>
      </div>
      <Composer t={t} accent={accent} density={density}/>
    </div>
  );
}

function GovernanceScreen({t, accent, density}) {
  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.panel, minWidth:0}}>
      <Scopebar t={t} accent={accent} density={density}/>
      <div style={{flex:1, overflow:'hidden'}}>
        <Message role="user" t={t} accent={accent} density={density} meta="02:58 · run #r-0147">
          Apply the Memory section edit to ARCHITECTURE.md.
        </Message>
        <Message role="jeff" t={t} accent={accent} density={density} truth="support" meta="selection · opt-02">
          Selection complete. This request would mutate a canonical spec file. Selection is not permission — routing to governance.
        </Message>
        <div style={{padding:'0 16px'}}>
          <div style={{
            margin:'12px 0', border:`1px solid ${t.pending}`, borderRadius:4,
            background:`${t.pending}0f`,
          }}>
            <div style={{padding:'10px 14px', borderBottom:`1px solid ${t.pending}44`, display:'flex', alignItems:'center', gap:10}}>
              <StateDot color={t.pending}/>
              <div style={{fontFamily:mono, fontSize:11, letterSpacing:1.5, color:t.pending}}>GOVERNANCE GATE · APPROVAL REQUIRED</div>
              <div style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>waiting on operator</div>
            </div>
            <div style={{padding:'14px 16px'}}>
              <div style={{fontSize:13, color:t.text, lineHeight:1.55, marginBottom:10}}>
                Jeff is not executing. Approving accepts the action request — the transition is only applied after execution, outcome, and evaluation succeed.
              </div>
              <div style={{display:'grid', gridTemplateColumns:'auto 1fr', gap:'6px 14px', fontFamily:mono, fontSize:11, padding:'8px 0'}}>
                <div style={{color:t.faint}}>rule</div><div style={{color:t.text}}>mutate_canonical_spec</div>
                <div style={{color:t.faint}}>target</div><div style={{color:t.text}}>jeff_planning_docs/v1_doc/ARCHITECTURE.md</div>
                <div style={{color:t.faint}}>scope</div><div style={{color:t.text}}>project · jeff / work_unit · define-architecture</div>
                <div style={{color:t.faint}}>readiness</div><div style={{color:t.approved}}>pass · 4/4</div>
                <div style={{color:t.faint}}>risk</div><div style={{color:t.pending}}>medium · canonical mutation</div>
              </div>
              <div style={{display:'flex', gap:8, marginTop:12}}>
                <button style={{background:t.approved, color:'#fff', border:'none', fontFamily:mono, fontSize:12, padding:'8px 14px', borderRadius:3, cursor:'pointer', fontWeight:500}}>approve request</button>
                <button style={pillBtn(t)}>reject</button>
                <button style={pillBtn(t)}>defer</button>
                <button style={pillBtn(t)}>escalate</button>
                <div style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint, alignSelf:'center'}}>approved ≠ applied</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Composer t={t} accent={accent} density={density} placeholder="Add a note to this approval request…"/>
    </div>
  );
}

function BlockedScreen({t, accent, density}) {
  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.panel, minWidth:0}}>
      <Scopebar t={t} accent={accent} density={density}/>
      <div style={{padding:'10px 16px', borderBottom:`1px solid ${t.border}`, background:`${t.blocked}11`, display:'flex', alignItems:'center', gap:10}}>
        <StateDot color={t.blocked}/>
        <div style={{fontFamily:mono, fontSize:11, color:t.blocked, letterSpacing:1.5}}>RUN · BLOCKED</div>
        <div style={{fontFamily:mono, fontSize:11, color:t.muted}}>readiness failed · stale basis</div>
        <div style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>run #r-0146 · 17m ago</div>
      </div>

      <div style={{flex:1, overflow:'hidden'}}>
        <Message role="user" t={t} accent={accent} density={density} meta="run #r-0146">
          Continue the draft from where we stopped.
        </Message>
        <Message role="jeff" t={t} accent={accent} density={density} truth="support" meta="evaluation · degraded">
          <div style={{border:`1px solid ${t.blocked}`, borderRadius:4, padding:'12px 14px', background:`${t.blocked}0a`}}>
            <div style={{fontFamily:mono, fontSize:11, color:t.blocked, letterSpacing:1, marginBottom:8}}>HONEST ESCALATION</div>
            <div style={{fontSize:13, color:t.text, lineHeight:1.55, marginBottom:10}}>Execution was not attempted. Two conditions block honest continuation:</div>
            <div style={{fontFamily:mono, fontSize:11, lineHeight:1.7}}>
              <div><span style={{color:t.blocked}}>✕</span> <b style={{color:t.text}}>stale basis</b> <span style={{color:t.muted}}>— context snapshot is 2 runs behind canonical state</span></div>
              <div><span style={{color:t.blocked}}>✕</span> <b style={{color:t.text}}>unresolved conflict</b> <span style={{color:t.muted}}>— memory#m-0093 contradicts doc#POLICY_AND_APPROVAL_SPEC §4.2</span></div>
              <div><span style={{color:t.approved}}>✓</span> <b style={{color:t.text}}>what can continue safely</b> <span style={{color:t.muted}}>— read-only inspection and research</span></div>
            </div>
            <div style={{display:'flex', gap:6, marginTop:12, flexWrap:'wrap'}}>
              <button style={pillBtn(t)}>revalidate context</button>
              <button style={pillBtn(t)}>resolve contradiction →</button>
              <button style={pillBtn(t)}>read-only continue</button>
              <button style={pillBtn(t)}>escalate to operator</button>
            </div>
          </div>
        </Message>
        <Message role="system" t={t} accent={accent} density={density} truth="derived" meta="run trace">
          <div style={{fontFamily:mono, fontSize:11, color:t.muted, lineHeight:1.7}}>
            <div><span style={{color:t.approved}}>●</span> trigger · operator request</div>
            <div><span style={{color:t.approved}}>●</span> state read · ok</div>
            <div><span style={{color:t.approved}}>●</span> context · assembled</div>
            <div><span style={{color:t.blocked}}>●</span> readiness · fail · stale basis, unresolved conflict</div>
            <div><span style={{color:t.faint}}>○</span> proposal · skipped</div>
            <div><span style={{color:t.faint}}>○</span> selection · skipped</div>
            <div><span style={{color:t.faint}}>○</span> execution · skipped</div>
            <div><span style={{color:t.blocked}}>●</span> transition · <b>not applied</b> · no truth change</div>
          </div>
        </Message>
      </div>
      <Composer t={t} accent={accent} density={density} placeholder="Respond to escalation…"/>
    </div>
  );
}

function HistoryScreen({t, accent, density}) {
  const runs = [
    {id:'#r-0147', label:'draft Memory section',              state:'executing', verdict:'—',            ts:'4m ago'},
    {id:'#r-0146', label:'continue draft',                    state:'blocked',   verdict:'readiness fail', ts:'17m ago'},
    {id:'#r-0145', label:'research: workflow-as-truth',       state:'done',      verdict:'inconclusive', ts:'1h ago'},
    {id:'#r-0144', label:'revise Core layer prose',           state:'done',      verdict:'success',      ts:'2h ago'},
    {id:'#r-0143', label:'propose layer ordering',            state:'done',      verdict:'success · partial', ts:'3h ago'},
    {id:'#r-0142', label:'sync memory candidates',            state:'done',      verdict:'degraded',     ts:'4h ago'},
    {id:'#r-0141', label:'check contradictions log',          state:'done',      verdict:'success',      ts:'5h ago'},
  ];
  const verdictColor = (v) => v.startsWith('success')?t.approved:v==='inconclusive'||v==='degraded'||v.startsWith('readiness')?t.degraded:t.faint;

  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.panel, minWidth:0}}>
      <Scopebar t={t} accent={accent} density={density}/>
      <div style={{padding:'14px 18px', borderBottom:`1px solid ${t.border}`}}>
        <div style={{display:'flex', alignItems:'baseline', gap:12}}>
          <div style={{fontSize:20, color:t.text, fontWeight:500, letterSpacing:-0.3}}>define-architecture</div>
          <TruthTag kind="canonical" t={t}/>
          <div style={{fontFamily:mono, fontSize:11, color:t.faint, marginLeft:'auto'}}>7 runs · 2 active memory · last transition 2h ago</div>
        </div>
        <div style={{fontSize:12, color:t.muted, marginTop:6, lineHeight:1.5}}>Define the first canonical ARCHITECTURE.md for project jeff. Bounded to v1 backbone.</div>
      </div>
      <div style={{padding:'10px 18px', borderBottom:`1px solid ${t.border}`, display:'flex', gap:8, fontFamily:mono, fontSize:11}}>
        {['all runs · 7','executing · 1','blocked · 1','success · 4','degraded · 1'].map((f,i)=>(
          <div key={f} style={{
            padding:'4px 10px', borderRadius:3,
            background: i===0?t.surface:'transparent',
            border:`1px solid ${i===0?t.borderStrong:t.border}`, color:i===0?t.text:t.muted, cursor:'pointer'
          }}>{f}</div>
        ))}
      </div>
      <div style={{flex:1, overflow:'hidden'}}>
        {runs.map((r,i)=>(
          <div key={r.id} style={{
            padding: density==='dense' ? '8px 18px' : '12px 18px',
            borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:12,
            background: i===0?t.surface:'transparent'
          }}>
            <StateDot color={r.state==='executing'?accent:r.state==='blocked'?t.blocked:t.approved}/>
            <div style={{fontFamily:mono, fontSize:11, color:t.muted, flex:'0 0 72px'}}>{r.id}</div>
            <div style={{flex:1, fontSize:13, color:t.text}}>{r.label}</div>
            <div style={{fontFamily:mono, fontSize:10, color:verdictColor(r.verdict), letterSpacing:1}}>{r.verdict.toUpperCase()}</div>
            <div style={{fontFamily:mono, fontSize:10, color:t.faint, flex:'0 0 60px', textAlign:'right'}}>{r.ts}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SettingsScreen({t, accent, density}) {
  return (
    <div style={{flex:1, display:'flex', flexDirection:'column', background:t.panel, minWidth:0}}>
      <div style={{padding:'16px 20px', borderBottom:`1px solid ${t.border}`}}>
        <div style={{fontFamily:mono, fontSize:10, color:t.faint, letterSpacing:1.5}}>SETTINGS</div>
        <div style={{fontSize:22, color:t.text, fontWeight:500, letterSpacing:-0.4, marginTop:4}}>Policy, readiness & operator preferences</div>
      </div>
      <div style={{flex:1, overflow:'hidden', padding:'18px 20px', display:'grid', gridTemplateColumns:'200px 1fr', gap:24}}>
        <div style={{display:'flex', flexDirection:'column', gap:2}}>
          {['Policy', 'Approval rules', 'Readiness', 'Memory', 'Model adapters', 'Tool adapters', 'Appearance', 'About'].map((s,i)=>(
            <div key={s} style={{
              padding:'8px 10px', borderRadius:3, fontSize:13, cursor:'pointer',
              background: i===0?t.surface:'transparent',
              border: i===0?`1px solid ${t.border}`:'1px solid transparent',
              color: i===0?t.text:t.muted,
              fontFamily: i===0?sans:sans, fontWeight: i===0?500:400
            }}>{s}</div>
          ))}
        </div>
        <div style={{display:'flex', flexDirection:'column', gap:16, overflow:'hidden'}}>
          <div style={{border:`1px solid ${t.border}`, borderRadius:4, background:t.surface}}>
            <div style={{padding:'10px 14px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:8}}>
              <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.muted}}>POLICY · RULES</div>
              <TruthTag kind="canonical" t={t}/>
            </div>
            {[
              ['mutate_canonical_spec', 'require_operator_approval · require_readiness', true],
              ['internet_research',     'auto · scoped to active project',                true],
              ['external_tool_call',    'require_readiness · log trace',                  true],
              ['memory_commit',         'auto · require_evidence_link',                   true],
              ['long_running_autonomy', 'disabled · v1',                                  false],
            ].map(([rule, effect, on],i)=>(
              <div key={i} style={{padding:'10px 14px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:12}}>
                <div style={{flex:'0 0 220px', fontFamily:mono, fontSize:12, color:t.text}}>{rule}</div>
                <div style={{flex:1, fontFamily:mono, fontSize:11, color:t.muted}}>{effect}</div>
                <div style={{
                  width:32, height:18, borderRadius:9, position:'relative',
                  background: on?t.approved:t.border, flexShrink:0
                }}>
                  <div style={{position:'absolute', top:2, left: on?16:2, width:14, height:14, borderRadius:7, background:'#fff'}}/>
                </div>
              </div>
            ))}
          </div>

          <div style={{border:`1px solid ${t.border}`, borderRadius:4, background:t.surface}}>
            <div style={{padding:'10px 14px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:8}}>
              <div style={{fontFamily:mono, fontSize:10, letterSpacing:1.5, color:t.muted}}>APPEARANCE</div>
              <TruthTag kind="local" t={t}/>
            </div>
            <div style={{padding:'14px', display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
              <div>
                <div style={{fontSize:11, color:t.muted, fontFamily:mono, marginBottom:4}}>theme</div>
                <div style={{display:'flex', gap:4}}>
                  {['light','dark'].map(v=>(
                    <div key={v} style={{padding:'6px 12px', border:`1px solid ${v==='light'?accent:t.border}`, color:v==='light'?t.text:t.muted, borderRadius:3, fontFamily:mono, fontSize:11, cursor:'pointer'}}>{v}</div>
                  ))}
                </div>
              </div>
              <div>
                <div style={{fontSize:11, color:t.muted, fontFamily:mono, marginBottom:4}}>density</div>
                <div style={{display:'flex', gap:4}}>
                  {['spacious','dense'].map(v=>(
                    <div key={v} style={{padding:'6px 12px', border:`1px solid ${v==='spacious'?accent:t.border}`, color:v==='spacious'?t.text:t.muted, borderRadius:3, fontFamily:mono, fontSize:11, cursor:'pointer'}}>{v}</div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── top nav variant ────────────────────────────────────────

function TopNavShell({t, accent, density, children}) {
  return (
    <div style={{height:'100%', display:'flex', flexDirection:'column', background:t.bg}}>
      <div style={{background:t.panel, borderBottom:`1px solid ${t.border}`, padding:'0 18px', display:'flex', alignItems:'center', gap:14, height:46}}>
        <div style={{display:'flex', alignItems:'center', gap:8}}>
          <div style={{width:22, height:22, borderRadius:4, background:accent, display:'grid', placeItems:'center', fontFamily:mono, fontSize:11, fontWeight:600, color:'#1a1816'}}>J</div>
          <div style={{fontFamily:mono, fontSize:13, color:t.text, fontWeight:500}}>jeff</div>
        </div>
        <div style={{width:1, height:22, background:t.border}}/>
        <div style={{display:'flex', gap:4}}>
          {[
            {l:'jeff', active:true, status:t.approved},
            {l:'home_energy_upgrade', status:t.faint},
            {l:'book_research', status:t.faint},
            {l:'client_proposal', status:t.blocked},
          ].map(p=>(
            <div key={p.l} style={{
              padding:'6px 12px', borderRadius:3, fontFamily:mono, fontSize:11,
              background: p.active?t.surface:'transparent',
              border: p.active?`1px solid ${t.border}`:'1px solid transparent',
              color: p.active?t.text:t.muted, display:'flex', alignItems:'center', gap:6, cursor:'pointer'
            }}>
              <StateDot color={p.status} size={5}/>{p.l}
            </div>
          ))}
          <div style={{padding:'6px 8px', fontFamily:mono, fontSize:11, color:t.faint, cursor:'pointer'}}>+</div>
        </div>
        <div style={{flex:1}}/>
        <div style={{fontFamily:mono, fontSize:11, color:t.muted}}>⌕  search history</div>
        <div style={{fontFamily:mono, fontSize:11, color:t.muted}}>⚙</div>
      </div>
      <div style={{background:t.surface, borderBottom:`1px solid ${t.border}`, padding:'0 18px', display:'flex', alignItems:'center', gap:4, height:36}}>
        {['define-architecture','memory-spec','policy-matrix','research-planners', '+'].map((w,i)=>(
          <div key={w} style={{
            padding:'4px 10px', borderRadius:3, fontFamily:mono, fontSize:11,
            background: i===0?t.panel:'transparent',
            border: i===0?`1px solid ${t.border}`:'1px solid transparent',
            color: i===0?t.text:t.muted, cursor:'pointer'
          }}>{w}</div>
        ))}
        <div style={{marginLeft:'auto', fontFamily:mono, fontSize:10, color:t.faint}}>work_unit · active</div>
      </div>
      <div style={{flex:1, display:'flex', minHeight:0}}>
        <div style={{flex:1, display:'flex', flexDirection:'column', minWidth:0}}>{children}</div>
        <div style={{width:300, flexShrink:0}}>
          <Inspector t={t} accent={accent} density={density} kind="artifact"/>
        </div>
      </div>
    </div>
  );
}

function ClassicShell({t, accent, density, children, rightKind='artifact'}) {
  return (
    <div style={{height:'100%', display:'flex', background:t.bg}}>
      <div style={{width:220, flexShrink:0}}>
        <div style={{height:'100%', background:t.rail, borderRight:`1px solid ${t.border}`, display:'flex', flexDirection:'column'}}>
          <div style={{padding:'12px 14px', borderBottom:`1px solid ${t.border}`, display:'flex', alignItems:'center', gap:8}}>
            <div style={{width:20, height:20, borderRadius:4, background:accent, display:'grid', placeItems:'center', fontFamily:mono, fontSize:10, fontWeight:600, color:'#1a1816'}}>J</div>
            <div style={{fontFamily:mono, fontSize:12, color:t.text}}>jeff / define-arch</div>
          </div>
          <div style={{padding:'8px 10px', fontFamily:mono, fontSize:9, letterSpacing:1.5, color:t.faint}}>RUNS</div>
          {[
            ['#r-0147', 'draft Memory', 'exec', accent],
            ['#r-0146', 'continue draft', 'blocked', t.blocked],
            ['#r-0145', 'research workflow', 'done', t.approved],
            ['#r-0144', 'revise Core', 'done', t.approved],
            ['#r-0143', 'layer ordering', 'done', t.approved],
          ].map(([id,l,s,c],i)=>(
            <div key={id} style={{padding:'6px 12px', margin:'1px 6px', borderRadius:3, background:i===0?t.panel:'transparent', border:i===0?`1px solid ${t.border}`:'1px solid transparent', display:'flex', gap:8, alignItems:'center'}}>
              <StateDot color={c} size={5}/>
              <div style={{fontFamily:mono, fontSize:10, color:t.faint, flex:'0 0 46px'}}>{id}</div>
              <div style={{fontSize:11, color:i===0?t.text:t.muted, flex:1, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>{l}</div>
            </div>
          ))}
          <div style={{padding:'12px 10px', fontFamily:mono, fontSize:9, letterSpacing:1.5, color:t.faint}}>PROJECTS</div>
          {['jeff','home_energy_upgrade','book_research','client_proposal'].map((p,i)=>(
            <div key={p} style={{padding:'5px 14px', fontFamily:mono, fontSize:11, color:i===0?t.text:t.muted}}>
              {i===0?'▾':'▸'} {p}
            </div>
          ))}
        </div>
      </div>
      <div style={{flex:1, display:'flex', flexDirection:'column', minWidth:0}}>{children}</div>
      <div style={{width:280, flexShrink:0}}>
        <Inspector t={t} accent={accent} density={density} kind={rightKind}/>
      </div>
    </div>
  );
}

function TripleShell({t, accent, density, children, rightKind='artifact'}) {
  return (
    <div style={{height:'100%', display:'flex', background:t.bg}}>
      <div style={{width:200, flexShrink:0}}>
        <ProjectsRail t={t} accent={accent} density={density}/>
      </div>
      <div style={{width:250, flexShrink:0}}>
        <WorkUnitsPanel t={t} density={density}/>
      </div>
      <div style={{flex:1, display:'flex', flexDirection:'column', minWidth:0}}>{children}</div>
      <div style={{width:300, flexShrink:0}}>
        <Inspector t={t} accent={accent} density={density} kind={rightKind}/>
      </div>
    </div>
  );
}

// ─── main frame router ──────────────────────────────────────

function JeffFrame({screen, tweaks}) {
  const t = THEMES[tweaks.theme || 'light'];
  const accent = ACCENTS[tweaks.accent || 'amber'];
  const density = tweaks.density || 'spacious';
  const layout = tweaks.layout || 'triple';

  let inner;
  let rightKind = 'artifact';
  if (screen==='empty')       inner = <EmptyScreen t={t} accent={accent} density={density}/>;
  else if (screen==='active') { inner = <ActiveScreen t={t} accent={accent} density={density}/>; rightKind='artifact'; }
  else if (screen==='governance') { inner = <GovernanceScreen t={t} accent={accent} density={density}/>; rightKind='governance'; }
  else if (screen==='blocked') { inner = <BlockedScreen t={t} accent={accent} density={density}/>; rightKind='inspect'; }
  else if (screen==='history') { inner = <HistoryScreen t={t} accent={accent} density={density}/>; rightKind='inspect'; }
  else if (screen==='settings'){ inner = <SettingsScreen t={t} accent={accent} density={density}/>; rightKind='inspect'; }

  const Shell = layout==='classic' ? ClassicShell : layout==='topnav' ? TopNavShell : TripleShell;

  return (
    <div data-screen-label={screen} style={{width:'100%', height:'100%', background:t.bg, color:t.text, fontFamily:sans}}>
      <Shell t={t} accent={accent} density={density} rightKind={rightKind}>{inner}</Shell>
    </div>
  );
}

window.JeffFrame = JeffFrame;
window.__JEFF_THEMES = THEMES;
window.__JEFF_ACCENTS = ACCENTS;
