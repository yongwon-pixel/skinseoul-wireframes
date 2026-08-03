#!/usr/bin/env python3
"""
Adversarial QA execution of view-orders.md §8 [WF] scenarios.

Method 2 harness: executes each [WF] scenario EXACTLY as written in the spec,
using only the selectors / labels / expected strings the spec supplies.
No improvisation from knowledge of the page.

Verdicts:
  PASS       - spec's Then-clause held
  FAIL       - page did something other than what the spec asserts (evidence quoted)
  AMBIGUOUS  - spec does not say what to click / what to assert precisely enough
  UNRUNNABLE - assertion impossible in a static mock and NOT tagged [ADMIN]

Text-comparison convention (see report §Methodology):
  §8.0 rule 6 says "exactly" == trimmed byte-for-byte. That is unworkable for any
  element containing child nodes (source-indentation newlines land inside
  textContent). This harness therefore grades on whitespace-COLLAPSED equality and
  separately records whether byte-for-byte also held, so the rule-6 defect is
  visible without drowning the run in false FAILs.

Run:  python3 qa-view-orders.py [--json out.json]
"""
import json
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = "file:///Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/view-orders/index.html"

PRELUDE = r"""
window.__qa = {
  norm(s){ return (s==null?'':String(s)).replace(/\s+/g,' ').trim(); },
  t(el){ return el ? el.textContent : null; },
  // exact-compare per spec §8.0 r6 -> returns {byte, coll, actual}
  ex(actual, expected){
    const a = actual==null ? '' : String(actual);
    return { byte: a.trim() === expected,
             coll: window.__qa.norm(a) === window.__qa.norm(expected),
             actual: window.__qa.norm(a).slice(0,300),
             expected: expected };
  },
  tab(label){
    const b = [...document.querySelectorAll('.wf-tab')].find(x => x.textContent === label);
    if(!b) throw new Error('no chrome tab with exact text: ' + label);
    b.click();
    return b;
  },
  active(){ const s = document.querySelector('section.state.on'); return s ? s.id : null; },
  btnByText(scope, txt){
    const root = typeof scope === 'string' ? document.querySelector(scope) : scope;
    if(!root) return null;
    return [...root.querySelectorAll('button')].find(b => window.__qa.norm(b.textContent) === txt) || null;
  },
  allBtnTexts(scope){
    const root = typeof scope === 'string' ? document.querySelector(scope) : scope;
    if(!root) return [];
    return [...root.querySelectorAll('button')].map(b => window.__qa.norm(b.textContent));
  },
  fire(el, type){ el.dispatchEvent(new Event(type, {bubbles:true})); },
  // visibility: getClientRects works for position:fixed too (offsetParent does not)
  vis(el){ return !!el && el.getClientRects().length > 0; },
  // strip wireframe annotation chrome (.dot) and the modal close button before comparing
  clean(el){ if(!el) return null; const c=el.cloneNode(true);
    c.querySelectorAll('.dot, button.x, .anno > .dot').forEach(d=>d.remove()); return c.textContent; },
  // dual compare: literal (exactly as the spec says) vs dot-stripped
  ex2(el, expected){
    const lit = window.__qa.norm(window.__qa.t(el));
    const cln = window.__qa.norm(window.__qa.clean(el));
    const e   = window.__qa.norm(expected);
    return {lit: lit===e, cleaned: cln===e, litVal: lit.slice(0,300), cleanVal: cln.slice(0,300), expected: expected};
  },
  cbtn(scope, txt){
    const root = typeof scope === 'string' ? document.querySelector(scope) : scope;
    if(!root) return null;
    return [...root.querySelectorAll('button')].find(b => window.__qa.norm(window.__qa.clean(b)) === txt) || null;
  },
  cbtnTexts(scope){
    const root = typeof scope === 'string' ? document.querySelector(scope) : scope;
    if(!root) return [];
    return [...root.querySelectorAll('button')].map(b => window.__qa.norm(window.__qa.clean(b)));
  },
  dataRows(sel){ return [...document.querySelectorAll(sel)].filter(r=>r.querySelectorAll('td').length>0); },
  ths(sel){ return [...document.querySelectorAll(sel)].map(t => window.__qa.norm(t.textContent)); },
};
window.__mk = (ok, ev, extra) => Object.assign({v: ok ? 'PASS' : 'FAIL', ev: ev}, extra||{});
window.__mk2 = (lit, cleaned, ev, extra) => Object.assign({v: lit ? 'PASS' : 'FAIL', ev: ev, dotOnly: (!lit && cleaned)}, extra||{});
"""

STATE_TABS = {
    "s0":  "0 · Waiting (Before Scan)",
    "s1":  "1 · Scan Result (Last Item Remaining)",
    "s1b": "1b · Scan Result (Normal — 2 Remaining)",
    "s2":  "2 · All Inbounded",
    "s3":  "3 · Outbound Complete",
    "s4":  "4 · Customer Return Mode",
    "s5":  "5 · Hold Order",
    "s6":  "6 · Internal Inbound (Inbound Request)",
    "s6b": "6b · Internal Inbound Complete",
}

# ---------------------------------------------------------------- scenarios --
# Each entry: (id, mode, payload)
#   mode 'js'  -> payload is a JS function body returning {v, ev, ...}
#   mode 'py'  -> payload is a python callable(page) returning dict
#   mode 'note'-> payload is (verdict, evidence)  (recorded without execution)

JS = {}

JS["QA-S0-01"] = r"""
const st = __qa.active();
const tabOn = [...document.querySelectorAll('.wf-tab')].find(b=>b.classList.contains('on'));
const h2 = __qa.ex(__qa.t(document.querySelector('#s0 h2')), 'WMS - View Orders');
const sub = __qa.ex(__qa.t(document.querySelector('#s0 .sub')), 'Search Orders');
const inp = document.querySelector('#s0 .search-input input');
const ph  = inp && inp.placeholder === 'Tracking No / Inbound Order No / Product Order No / Last-mile barcode — scan any number';
const ok = st==='s0' && tabOn && tabOn.textContent==='0 · Waiting (Before Scan)' && h2.coll && sub.coll && inp && inp.value==='' && ph;
return __mk(ok, `active=${st} tabOn="${tabOn&&tabOn.textContent}" h2="${h2.actual}" sub="${sub.actual}" value="${inp&&inp.value}" placeholderMatch=${ph}`,
  {byte: h2.byte && sub.byte});
"""

JS["QA-S0-04"] = r"""
const s0 = document.querySelector('#s0');
const txt = __qa.norm(s0.textContent);
const a = txt.includes('Waiting for scan');
const b = txt.includes('Scan a tracking/product barcode or type a number to switch to that order’s screen instantly')
       || txt.includes("Scan a tracking/product barcode or type a number to switch to that order's screen instantly");
const dashed = [...s0.querySelectorAll('*')].some(e => /dash/i.test(getComputedStyle(e).borderStyle||''));
const card = document.querySelector('#s0 .ordercard');
const literal = txt.match(/Scan a tracking\/product barcode[^·]{0,120}/);
return __mk(a && b && dashed && card===null,
  `hasWaitingForScan=${a} hasScanSentence=${b} dashedPanel=${dashed} ordercard=${card===null?'null':'PRESENT'} literal="${literal?literal[0]:''}"`);
"""

JS["QA-S0-05"] = r"""
const b = [...document.querySelectorAll('#s0 .searchrow button.btn-blue')].find(x=>__qa.norm(x.textContent)==='🔍 Search');
const any = [...document.querySelectorAll('#s0 .searchrow button')].map(x=>__qa.norm(x.textContent));
return __mk(!!b, `btn-blue in #s0 .searchrow with text "🔍 Search" -> ${b?'found':'NOT FOUND'}; buttons in searchrow=${JSON.stringify(any)}`);
"""

JS["QA-S0-06"] = r"""
const t = document.querySelector('#inexpToggle');
const e = __qa.ex(__qa.t(t), '▸ Expected Inbound 4 — 2 with tracking · 1 Partial Inbound');
const tbl = document.querySelector('#inexpTable');
const disp = tbl.style.display;
const vis = t.offsetParent !== null;
return __mk(vis && e.coll && disp==='none',
  `visible=${vis} toggleText="${e.actual}" expected="${e.expected}" inexpTable.style.display="${disp}"`, {byte:e.byte});
"""

JS["QA-S0-07"] = r"""
const t=document.querySelector('#inexpToggle'), tbl=document.querySelector('#inexpTable');
t.click();
const vis1 = tbl.style.display !== 'none';
const arrow1 = __qa.norm(t.textContent).startsWith('▾');
const rows=[...tbl.querySelectorAll('tbody tr')];
const first=rows.map(r=>__qa.norm(r.querySelector('td').textContent));
t.click();
const disp2=tbl.style.display, arrow2=__qa.norm(t.textContent).startsWith('▸');
const want=['202608020001','202607120001','202608020002','202608010004'];
const ok = vis1 && arrow1 && rows.length===4 && JSON.stringify(first)===JSON.stringify(want) && disp2==='none' && arrow2;
return __mk(ok, `afterClick visible=${vis1} arrow▾=${arrow1} rowCount=${rows.length} firstCells=${JSON.stringify(first)} want=${JSON.stringify(want)} | afterSecondClick display="${disp2}" arrow▸=${arrow2}`);
"""

JS["QA-S0-08"] = r"""
document.querySelector('#inexpToggle').click();
const th=__qa.ths('#inexpTable thead th');
const want=['Inbound No.','Sourcing Route','Supplier','Items','Tracking No','Status'];
const rows=[...document.querySelectorAll('#inexpTable tbody tr')];
const r2=rows[1];
const ws=r2?r2.querySelector('.tag-wholesale'):null;
const wsTxt=ws?__qa.norm(ws.textContent):null;
const supplier=r2?__qa.norm(r2.textContent).includes('비엠유통'):false;
const part=r2?r2.querySelector('.tag-part'):null;
const partTxt=part?__qa.norm(part.textContent):null;
const cellTrk=i=>{const c=rows[i]?rows[i].querySelectorAll('td')[4]:null;return c?__qa.norm(c.textContent):null;};
const ok = JSON.stringify(th)===JSON.stringify(want) && wsTxt==='WHOLESALE' && supplier && partTxt==='PARTIAL 620/800' && cellTrk(2)==='—' && cellTrk(3)==='—';
return __mk(ok, `headers=${JSON.stringify(th)} want=${JSON.stringify(want)} row2.tag-wholesale="${wsTxt}" supplier비엠유통=${supplier} row2.tag-part="${partTxt}" row3.TrackingNo="${cellTrk(2)}" row4.TrackingNo="${cellTrk(3)}"`);
"""

JS["QA-S0-09"] = r"""
document.querySelector('#inexpToggle').click();
const els=[...document.querySelectorAll('.tag-smartbuy,.tag-jit,.tag-wholesale,.tag-partnership')];
const bad=els.filter(e=>getComputedStyle(e).backgroundColor!=='rgba(0, 0, 0, 0)')
             .map(e=>({t:__qa.norm(e.textContent),bg:getComputedStyle(e).backgroundColor}));
return __mk(els.length>0 && bad.length===0, `checked=${els.length} nonTransparent=${JSON.stringify(bad.slice(0,6))}`);
"""

JS["QA-S0-10"] = r"""
document.querySelector('#inexpToggle').click();
const row=document.querySelector('#inexpTable .row-part');
if(!row) return __mk(false,'no .row-part inside #inexpTable');
row.click();
const act=__qa.active();
const s0on=document.querySelector('#s0').classList.contains('on');
return __mk(act==='s6' && !s0on, `activeState=${act} #s0.hasClass('on')=${s0on}`);
"""

JS["QA-S0-11"] = r"""
document.querySelector('#inexpToggle').click();
const tbl=document.querySelector('#inexpTable');
const foot=__qa.norm(tbl.parentElement ? tbl.parentElement.textContent : '') ;
const scope=__qa.norm(document.querySelector('#s0').textContent);
const a=scope.includes('Rows with tracking sorted to top');
const b=scope.includes('Click a row = open its reconciliation screen (State 6) without scanning');
const c=scope.includes('Full list: Inbound Request → Request List');
return __mk(a&&b&&c, `sortedToTop=${a} clickRow=${b} fullList=${c}`);
"""

JS["QA-SC-07"] = r"""
const want={s1b:'10323775317888',s2:'10323775316153',s3:'10323775316153',s4:'10322198837710',s5:'10324880021991',s6:'10325661220417'};
const got={}; let ok=true;
for(const k of Object.keys(want)){
  const el=document.querySelector('#'+k+' .search-input input');
  got[k]= el?el.value:null;
  if(got[k]!==want[k]) ok=false;
}
return __mk(ok, `got=${JSON.stringify(got)} want=${JSON.stringify(want)}`);
"""

JS["QA-SC-08"] = r"""
__qa.tab('6b · Internal Inbound Complete');
const el=document.querySelector('#s6b .search-input input');
const ph='Scan a tracking barcode — continue with the next one';
return __mk(el && el.value==='' && el.placeholder===ph, `value="${el&&el.value}" placeholder="${el&&el.placeholder}" expectedPlaceholder="${ph}"`);
"""

JS["QA-SC-17"] = r"""
const ids=['s0','s1','s1b','s2','s3','s4','s5','s6','s6b'];
const ph={}; for(const i of ids){const e=document.querySelector('#'+i+' .search-input input'); ph[i]=e?e.placeholder:null;}
const base=ph.s0; const others=ids.filter(i=>i!=='s6b');
const same=others.every(i=>ph[i]===base);
const diff=ph.s6b!==base;
return __mk(same&&diff, `s0..s6 identical=${same} s6b differs=${diff} s6b="${ph.s6b}"`);
"""

JS["QA-S1-01"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const rows=[...document.querySelectorAll('#s1 tbody tr.row-hit')];
const tds=rows[0]?[...rows[0].querySelectorAll('td')]:[];
const skuLit=tds[1]?__qa.norm(tds[1].textContent):null;
const skuCln=tds[1]?__qa.norm(__qa.clean(tds[1])):null;
const badge=rows[0]?rows[0].querySelector('.tag-pending'):null;
const bt=badge?__qa.norm(badge.textContent):null;
const lit = rows.length===1 && skuLit==='100005104' && bt==='PENDING';
const cln = rows.length===1 && skuCln==='100005104' && bt==='PENDING';
return __mk2(lit, cln, `row-hit count=${rows.length} skuCell literal="${skuLit}" dotStripped="${skuCln}" tag-pending="${bt}"`);
"""

JS["QA-S1-06"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const bb=document.querySelector('#s1 .bulkbar');
const texts=__qa.allBtnTexts(bb);
const cnt=__qa.ex(__qa.t(bb.querySelector('.cnt')), '1 selected · Processing all triggers auto Outbound (Hold orders: Inbound only)');
const ok = texts.includes('Bulk Inbound (Selected)') && texts.includes('Inbound + Outbound All Remaining') && cnt.coll;
return __mk(ok, `bulkbar buttons=${JSON.stringify(texts)} .cnt="${cnt.actual}" expected="${cnt.expected}"`, {byte:cnt.byte});
"""

JS["QA-S1-07"] = r"""
__qa.tab('1b · Scan Result (Normal — 2 Remaining)');
const e=__qa.ex(__qa.t(document.querySelector('#s1b .bulkbar .cnt')), '2 not yet inbounded — processing all triggers auto Outbound (Hold orders: Inbound only)');
return __mk(e.coll, `actual="${e.actual}" expected="${e.expected}"`, {byte:e.byte});
"""

JS["QA-S1-08"] = r"""
const ids=['s1','s1b','s2','s3','s4','s5']; const got={};
for(const i of ids) got[i]= !!document.querySelector('#'+i+' .bulkbar');
return __mk(Object.values(got).every(Boolean), `bulkbar present per state=${JSON.stringify(got)}`);
"""

JS["QA-S1-09"] = r"""
const cardBtnLit={}, cardBtnCln={}, deleoHits=[];
for(const [id,lbl] of Object.entries(window.__tabs)){
  __qa.tab(lbl);
  const c=document.querySelector('#'+id+' .ordercard');
  if(c){ cardBtnLit[id]=__qa.allBtnTexts(c).filter(t=>/Outbound/.test(t));
         cardBtnCln[id]=__qa.cbtnTexts(c).filter(t=>/Outbound/.test(t)); }
  else { cardBtnLit[id]='no .ordercard'; cardBtnCln[id]='no .ordercard'; }
  const n=(document.body.innerText.match(/Deleo/g)||[]).length;
  if(n) deleoHits.push(id+':'+n);
}
const bad=v=>Object.entries(v).filter(([k,x])=>Array.isArray(x)&&x.length&&!x.every(t=>t==='Outbound'||t==='✓ Outbounded'));
const litOK = bad(cardBtnLit).length===0 && deleoHits.length===0;
const clnOK = bad(cardBtnCln).length===0 && deleoHits.length===0;
return __mk2(litOK, clnOK, `literal=${JSON.stringify(cardBtnLit)} dotStripped=${JSON.stringify(cardBtnCln)} DeleoInnerTextHits=${JSON.stringify(deleoHits)}`);
"""

JS["QA-S1-11"] = r"""
const ids=['s1','s1b','s2','s3','s4','s5']; const viol=[];
for(const i of ids){
  for(const tr of document.querySelectorAll('#'+i+' tbody tr')){
    const p=tr.querySelector('.tag-pending');
    if(p && (tr.querySelector('.tag-smartbuy')||tr.querySelector('.tag-wholesale')||tr.querySelector('.tag-partnership'))){
      viol.push(i+' :: '+__qa.norm(tr.textContent).slice(0,90));
    }
  }
}
return __mk(viol.length===0, `PENDING+non-JIT rows=${JSON.stringify(viol)}`);
"""

JS["QA-S1-12"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const tdCells=[...document.querySelectorAll('#s1 table.tbl tbody td')].filter(td=>/^\d+$/.test(__qa.norm(__qa.clean(td))));
const tdInfo=tdCells.map(c=>({t:__qa.norm(__qa.clean(c)),cls:c.className}));
const spans=[...document.querySelectorAll('#s1 table.tbl tbody span.qty, #s1 table.tbl tbody span.qty-warn')].map(sp=>({t:__qa.norm(sp.textContent),cls:sp.className}));
const two=spans.filter(m=>m.t==='2'), ones=spans.filter(m=>m.t==='1');
const spanOK = two.length>0 && two.every(m=>/qty-warn/.test(m.cls)) && ones.length>0 && ones.every(m=>/\bqty\b/.test(m.cls)&&!/qty-warn/.test(m.cls));
const cellOK = tdInfo.some(c=>c.t==='2'&&/qty-warn/.test(c.cls));
return __mk(cellOK, `SPEC SAYS "cell" (td): tdQtyCells=${JSON.stringify(tdInfo)} -> td carries class qty-warn? ${cellOK}. The classes actually live on a child <span>: spans=${JSON.stringify(spans)} -> spanReadingHolds=${spanOK}`,
  {dotOnly:false, altPass:spanOK});
"""

JS["QA-S1-13"] = r"""
const want=['','SKU','Image','Product Name','Product Name KR','Size','Qty','Barcode','Inbound Order No','Tracking No','Inbound Status','Sourcing Route','Location','Actions'];
const ids=['s1','s1b','s2','s3','s4','s5']; const lit={}, cln={}; let litOK=true, clnOK=true;
for(const i of ids){
  const th=[...document.querySelectorAll('#'+i+' table.tbl thead th')];
  lit[i]=th.map(t=>__qa.norm(t.textContent));
  cln[i]=th.map(t=>__qa.norm(__qa.clean(t)));
  if(th.length!==14 || JSON.stringify(lit[i])!==JSON.stringify(want)) litOK=false;
  if(th.length!==14 || JSON.stringify(cln[i])!==JSON.stringify(want)) clnOK=false;
}
return __mk2(litOK, clnOK, `literal=${JSON.stringify(lit)} dotStripped=${JSON.stringify(cln)} want=${JSON.stringify(want)}`);
"""

JS["QA-S1-14"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const rows=[...document.querySelectorAll('#s1 table.tbl tbody tr')];
const info=rows.map(r=>{const tds=[...r.querySelectorAll('td')];return {cls:r.className||'(none)', sku:__qa.norm(__qa.clean(tds[1])), loc:__qa.norm(__qa.clean(tds[12]))};});
const ex=info.find(x=>/row-exist/.test(x.cls));
const others=info.filter(x=>!/row-exist/.test(x.cls));
const ok = ex && ex.sku==='100024743' && ex.loc==='A-03-2' && others.every(o=>o.loc==='–');
return __mk(!!ok, `scopedTo #s1 table.tbl (spec's bare "#s1 tbody" also matches the .logtbl). rows=${JSON.stringify(info)}`);
"""

JS["QA-S1-15"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const rows=[...document.querySelectorAll('#s1 table.tbl tbody tr')];
const out=rows.map(r=>{const tds=[...r.querySelectorAll('td')];const en=tds[3],kr=tds[4];
  return {enB:en&&en.querySelector('b')?__qa.norm(en.querySelector('b').textContent):null,
          krB:kr&&kr.querySelector('b')?__qa.norm(kr.querySelector('b').textContent):null,
          krTxt:kr?__qa.norm(__qa.clean(kr)).slice(0,60):null};});
const brands=['COSRX','Dr.Jart+','The Face Shop','Medicube'];
const ok = out.every(o=>o.enB&&o.krB&&o.enB===o.krB) && brands.every(b=>out.some(o=>o.enB===b));
return __mk(ok, `rows=${JSON.stringify(out)} requiredBrands=${JSON.stringify(brands)}`);
"""

JS["QA-S1-16"] = r"""
const ids=['s1','s1b','s2','s3']; const got={}; let ok=true;
for(const i of ids){
  const rows=[...document.querySelectorAll('#'+i+' table.tbl tbody tr')];
  const bc=[...document.querySelectorAll('#'+i+' table.tbl input.bcin')].map(x=>x.placeholder);
  const target=rows.find(r=>__qa.norm(__qa.clean(r)).includes('100024743'));
  const hasBcin=target?!!target.querySelector('input.bcin'):false;
  const cells=rows.filter(r=>!r.querySelector('input.bcin')).map(r=>{const tds=[...r.querySelectorAll('td')];return __qa.norm(__qa.clean(tds[7]));});
  // spec wording: "rows with a known barcode render text beginning '✓ '" -> a '–' cell has no known barcode
  const known=cells.filter(t=>t!=='–');
  got[i]={bcinPlaceholders:bc,row100024743HasBcin:hasBcin,barcodeCellsWithoutInput:cells};
  if(!hasBcin||!bc.length||!bc.every(pl=>pl==='Enter barcode')||!known.every(t=>t.startsWith('✓ '))) ok=false;
}
return __mk(ok, `${JSON.stringify(got)} | NOTE: State 1b has a third variant ('–' = no barcode, no input) that the scenario does not describe.`);
"""

JS["QA-S1-18"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const inp=document.querySelector('#s1 .shelf input');
const orig=inp.value;
inp.value='3'; __qa.fire(inp,'input');
const btns=[...document.querySelectorAll('#s1 button.flsave')].filter(b=>b.offsetParent!==null);
return __mk(btns.length===0, `shelf input original value="${orig}" set to "3"; visible button.flsave count=${btns.length}`);
"""

JS["QA-S1-19"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const sec=document.querySelector('#s1 .logsec');
if(!sec) return __mk(false,'#s1 .logsec is null');
const titled=__qa.norm(__qa.clean(sec)).includes('Inbound / Outbound Log');
const hdrRow=[...sec.querySelectorAll('tbody tr, thead tr')].find(r=>r.querySelectorAll('th').length>0);
const th=hdrRow?[...hdrRow.querySelectorAll('th')].map(t=>__qa.norm(__qa.clean(t))):[];
const dataRows=[...sec.querySelectorAll('tbody tr')].filter(r=>r.querySelectorAll('td').length>0);
const memos=dataRows.map(r=>{const t=[...r.querySelectorAll('td')];return __qa.norm(__qa.clean(t[t.length-1]));});
const want=['Time','Action','SKU','Qty','Worker','Memo'];
const bareTbodyCount=sec.querySelectorAll('tbody tr').length;
return __mk(titled && JSON.stringify(th)===JSON.stringify(want) && dataRows.length===3 && memos.includes('1 box damaged — restocked, needs inspection'),
  `heading="Inbound / Outbound Log" found=${titled} headers=${JSON.stringify(th)} dataRows(td-bearing)=${dataRows.length} bare "tbody tr" count=${bareTbodyCount} (header row lives INSIDE tbody) memos=${JSON.stringify(memos)}`);
"""

JS["QA-S1-20"] = r"""
const el=document.querySelector('#s1b .logsec');
return __mk(el===null, `#s1b .logsec = ${el===null?'null':'PRESENT'} (spec: this WF result documents demo limitation L-4)`);
"""

JS["QA-S1-03"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const r=document.querySelector('#s1 tbody tr.row-hit');
const lits=__qa.allBtnTexts(r), clns=__qa.cbtnTexts(r);
const t=__qa.cbtn(r,'Inbound + Outbound');
const lit = lits.includes('Inbound + Outbound') && t && t.classList.contains('btn-green');
const cln = clns.includes('Inbound + Outbound') && t && t.classList.contains('btn-green');
return __mk2(lit, cln, `row-hit buttons literal=${JSON.stringify(lits)} dotStripped=${JSON.stringify(clns)} class="${t?t.className:'n/a'}"`);
"""

JS["QA-S1-04"] = r"""
__qa.tab('1b · Scan Result (Normal — 2 Remaining)');
const r=document.querySelector('#s1b tbody tr.row-hit');
const texts=r?__qa.allBtnTexts(r):null;
const ob=__qa.btnByText('#s1b .ordercard','Outbound');
return __mk(!!r && texts.includes('Inbound') && !texts.includes('Inbound + Outbound') && ob && ob.classList.contains('btn-gray'),
  `row-hit buttons=${JSON.stringify(texts)} ordercard Outbound class="${ob?ob.className:'ABSENT'}"`);
"""

JS["QA-S1-05"] = r"""
__qa.tab('1b · Scan Result (Normal — 2 Remaining)');
const rows=[...document.querySelectorAll('#s1b tbody tr')].filter(r=>r.querySelector('.tag-pending'));
const skus=rows.map(r=>{const t=[...r.querySelectorAll('td')];return __qa.norm(t[1].textContent);});
return __mk(rows.length===2 && skus.includes('100005104') && skus.includes('100038120'), `pendingRows=${rows.length} skus=${JSON.stringify(skus)}`);
"""

JS["QA-S1-10"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const rows=[...document.querySelectorAll('#s1 tbody tr')];
const badges=rows.map(r=>{const b=r.querySelector('.tag-smartbuy,.tag-jit,.tag-wholesale,.tag-partnership');return b?__qa.norm(b.textContent):null;});
const pend=rows.filter(r=>r.querySelector('.tag-pending')).map(r=>{const b=r.querySelector('.tag-smartbuy,.tag-jit,.tag-wholesale,.tag-partnership');return b?__qa.norm(b.textContent):null;});
const want=['SMART BUY','JIT (Coupang)','WHOLESALE','PARTNERSHIP'];
const ok = want.every(w=>badges.includes(w)) && pend.length===1 && pend[0]==='JIT (Coupang)';
return __mk(ok, `routeBadges=${JSON.stringify(badges)} pendingRowRoutes=${JSON.stringify(pend)}`);
"""

JS["QA-S2-01"] = r"""
__qa.tab('2 · All Inbounded');
const bare=[...document.querySelectorAll('#s2 tbody tr')];
const rows=[...document.querySelectorAll('#s2 table.tbl tbody tr')];
const tags=rows.map(r=>{const t=r.querySelector('.tag-inbounded');return t?__qa.norm(t.textContent):null;});
const ob=__qa.cbtn('#s2 .ordercard','Outbound');
const litSel = bare.length===4;
const ok = rows.length===4 && tags.every(t=>t==='INBOUNDED') && ob && ob.classList.contains('btn-green');
return __mk(ok && litSel, `SPEC SELECTOR "#s2 tbody tr" returns ${bare.length} rows (it also matches the .logtbl); scoped to table.tbl it returns ${rows.length}. tags=${JSON.stringify(tags)} Outbound class="${ob?ob.className:'ABSENT'}"`,
  {selectorDefect: !litSel, altPass: ok});
"""

JS["QA-S2-02"] = r"""
__qa.tab('2 · All Inbounded');
const bb=document.querySelector('#s2 .bulkbar');
const bs=[...bb.querySelectorAll('button')];
const cls=bs.map(b=>({t:__qa.norm(b.textContent),c:b.className}));
const e=__qa.ex(__qa.t(bb.querySelector('.cnt')),'Nothing left to bulk-process — all items inbounded');
return __mk(bs.length>0 && bs.every(b=>b.classList.contains('btn-gray')) && e.coll,
  `buttons=${JSON.stringify(cls)} .cnt="${e.actual}" expected="${e.expected}"`,{byte:e.byte});
"""

JS["QA-S2-03"] = r"""
__qa.tab('2 · All Inbounded');
const r=document.querySelector('#s2 table.tbl tbody tr');
const before=document.querySelector('#s2 table.tbl tbody').innerHTML;
const litBtn=__qa.btnByText(r,'Cancel Inbound');
const b=__qa.cbtn(r,'Cancel Inbound');
if(!b) return __mk(false,'no button (even dot-stripped) with text "Cancel Inbound"; texts='+JSON.stringify(__qa.allBtnTexts(r)));
b.click();
const m=document.querySelector('#m-cancel');
const h=m.querySelector('header');
const e=__qa.ex2(h,'Cancel Inbound — 100038120');
const after=document.querySelector('#s2 table.tbl tbody').innerHTML;
const lit = !!litBtn && m.classList.contains('open') && e.lit && before===after;
const cln = m.classList.contains('open') && e.cleaned && before===after;
return __mk2(lit, cln, `literal button match=${!!litBtn} (row button textContent="${__qa.allBtnTexts(r)}") open=${m.classList.contains('open')} header literal="${e.litVal}" dotAndCloseStripped="${e.cleanVal}" expected="${e.expected}" tbodyUnchanged=${before===after}`);
"""

JS["QA-S2-04"] = r"""
__qa.tab('2 · All Inbounded');
const before=document.querySelector('#s2 table.tbl tbody').innerHTML;
const r=document.querySelector('#s2 table.tbl tbody tr');
__qa.cbtn(r,'Cancel Inbound').click();
const m=document.querySelector('#m-cancel');
const close=__qa.cbtn(m.querySelector('.foot'),'Close');
if(!close) return __mk(false,'no .foot button "Close"; foot buttons='+JSON.stringify(__qa.cbtnTexts(m.querySelector('.foot'))));
close.click();
const after=document.querySelector('#s2 table.tbl tbody').innerHTML;
return __mk(!m.classList.contains('open') && before===after, `openAfterClose=${m.classList.contains('open')} tbodyByteIdentical=${before===after}`);
"""

JS["QA-S3-01"] = r"""
__qa.tab('3 · Outbound Complete');
const lits=__qa.allBtnTexts('#s3 .ordercard'), clns=__qa.cbtnTexts('#s3 .ordercard');
const b=__qa.cbtn('#s3 .ordercard','✓ Outbounded');
const pill=document.querySelector('#s3 .ordercard .status');
const pOK=pill && __qa.norm(pill.textContent)==='Prepare Shipment' && pill.classList.contains('st-prepare');
const lit = lits.includes('✓ Outbounded') && b && b.classList.contains('btn-gray') && pOK;
const cln = clns.includes('✓ Outbounded') && b && b.classList.contains('btn-gray') && pOK;
return __mk2(lit, cln, `ordercard buttons literal=${JSON.stringify(lits)} dotStripped=${JSON.stringify(clns)} class="${b?b.className:'n/a'}" pill="${pill?__qa.norm(pill.textContent):null}"/${pill?pill.className:null}`);
"""

JS["QA-S3-03"] = r"""
__qa.tab('3 · Outbound Complete');
const rows=[...document.querySelectorAll('#s3 table.tbl tbody tr')];
const lit=rows.map(r=>[...r.querySelectorAll('button')].map(x=>({t:__qa.norm(x.textContent),g:x.classList.contains('btn-gray')}))).flat();
const cln=rows.map(r=>[...r.querySelectorAll('button')].map(x=>({t:__qa.norm(__qa.clean(x)),g:x.classList.contains('btn-gray')}))).flat();
const red=[...document.querySelectorAll('#s3 table.tbl tbody .btn-red-line')];
const litOK=lit.length>0&&lit.every(x=>x.t==='Cancel Inbound'&&x.g)&&red.length===0;
const clnOK=cln.length>0&&cln.every(x=>x.t==='Cancel Inbound'&&x.g)&&red.length===0;
return __mk2(litOK, clnOK, `literal=${JSON.stringify(lit)} dotStripped=${JSON.stringify(cln)} tbody .btn-red-line=${red.length}`);
"""

JS["QA-S3-04"] = r"""
__qa.tab('3 · Outbound Complete');
const toasts=[...document.querySelectorAll('#s3 .toast, .toast')];
const found=toasts.find(t=>__qa.norm(t.textContent).includes('✓ Outbound complete — Order 413865'));
const sub=found?found.querySelector('small'):null;
const e=sub?__qa.ex(__qa.t(sub),'Status: prepare shipment'):{coll:false,actual:'no <small>',expected:'Status: prepare shipment',byte:false};
return __mk(!!found && e.coll, `toastTexts=${JSON.stringify(toasts.map(t=>__qa.norm(t.textContent).slice(0,90)))} small="${e.actual}"`,{byte:e.byte});
"""

JS["QA-S3-05"] = r"""
__qa.tab('3 · Outbound Complete');
const sec=document.querySelector('#s3 .logsec');
const dataRows=[...sec.querySelectorAll('tbody tr')].filter(r=>r.querySelectorAll('td').length>0);
const cells=dataRows.map(r=>[...r.querySelectorAll('td')].map(t=>__qa.norm(__qa.clean(t))));
const newest=cells[0]||[];
const bare=sec.querySelectorAll('tbody tr').length;
return __mk(dataRows.length===5 && newest.includes('OUTBOUND') && newest.includes('All (4 SKU)') && newest.includes('5'),
  `dataRows(td-bearing)=${dataRows.length} bare "tbody tr"=${bare} newest=${JSON.stringify(newest)}`);
"""

JS["QA-S4-01"] = r"""
__qa.tab('4 · Customer Return Mode');
const b=document.querySelector('#s4 .retbanner');
const lead=b.querySelector('b,strong,.big');
const e1=__qa.ex2(lead,'⟲ Customer Return Order');
const litBody=__qa.norm(b.textContent).replace(__qa.norm(lead.textContent),'').trim();
const clnBody=__qa.norm(__qa.clean(b)).replace(__qa.norm(__qa.clean(lead)),'').trim();
const want='A returned tracking barcode was scanned — Order 412990 · Tracking 10322198837710';
const lit=e1.lit && litBody===want, cln=e1.cleaned && clnBody===want;
return __mk2(lit, cln, `lead="${e1.litVal}" bodyLiteral="${litBody}" bodyDotStripped="${clnBody}" expected="${want}"`);
"""

JS["QA-S4-03"] = r"""
__qa.tab('4 · Customer Return Mode');
const c=document.querySelector('#s4 .ordercard');
const texts=c?__qa.allBtnTexts(c):null;
return __mk(!!c && !texts.includes('Outbound') && !texts.includes('🖨 Print'), `#s4 .ordercard buttons=${JSON.stringify(texts)}`);
"""

JS["QA-S4-04"] = r"""
__qa.tab('4 · Customer Return Mode');
const bb=document.querySelector('#s4 .bulkbar');
const bs=[...bb.querySelectorAll('button')].map(b=>({t:__qa.norm(b.textContent),c:b.className}));
const e=__qa.ex(__qa.t(bb.querySelector('.cnt')),'Opens the restock confirmation modal — confirm qty · location · memo per item, then process in bulk');
const ok = bs.length>=3 && bs[0].t==='Bulk Inbound (Selected)' && /btn-gray/.test(bs[0].c)
        && bs[1].t==='Inbound + Outbound All Remaining' && /btn-gray/.test(bs[1].c)
        && bs[2].t==='Restock Selected to Warehouse (3)' && /btn-green/.test(bs[2].c) && e.coll;
return __mk(ok, `buttons=${JSON.stringify(bs)} .cnt="${e.actual}" expected="${e.expected}"`,{byte:e.byte});
"""

JS["QA-S4-05"] = r"""
__qa.tab('4 · Customer Return Mode');
const rows=[...document.querySelectorAll('#s4 tbody tr')];
const btns=rows.map(r=>{const b=[...r.querySelectorAll('button')];return b.map(x=>({t:__qa.norm(x.textContent),c:x.className}));}).flat();
const cnt=[...document.querySelectorAll('#s4 *')].map(e=>__qa.norm(e.textContent)).find(t=>/^Found \d+ item\(s\) in this order · Found \d+ order\(s\)$/.test(t));
return __mk(btns.length>0 && btns.every(b=>b.t==='Cancel Inbound → Add Stock' && /btn-red-line/.test(b.c)) && cnt==='Found 3 item(s) in this order · Found 1 order(s)',
  `rowButtons=${JSON.stringify(btns)} counter="${cnt}"`);
"""

JS["QA-S4-07"] = r"""
__qa.tab('4 · Customer Return Mode');
__qa.btnByText('#s4 .bulkbar','Restock Selected to Warehouse (3)').click();
const m=document.querySelector('#m-restock');
const lead='Confirm the products, quantities, and locations to restock. Products with existing stock get their current location auto-filled. Restock qty defaults to 0 — enter only the qty actually returned (0 = excluded).';
const ps=[...m.querySelectorAll('p,div')].map(e=>__qa.norm(e.textContent));
const hit=ps.find(t=>t===__qa.norm(lead));
const th=__qa.ths('#m-restock thead th');
const rows=[...m.querySelectorAll('tbody tr')];
const want=['Product','Ordered Qty','Restock Qty','Location'];
return __mk(!!hit && JSON.stringify(th)===JSON.stringify(want) && rows.length===3,
  `leadParagraphFound=${!!hit} headers=${JSON.stringify(th)} want=${JSON.stringify(want)} bodyRows=${rows.length} | nearestLead="${(ps.find(t=>t.startsWith('Confirm the products'))||'').slice(0,240)}"`);
"""

JS["QA-S4-08"] = r"""
__qa.tab('4 · Customer Return Mode');
__qa.btnByText('#s4 .bulkbar','Restock Selected to Warehouse (3)').click();
const m=document.querySelector('#m-restock');
const rows=[...m.querySelectorAll('tbody tr')];
const info=rows.map(r=>{
  const tds=[...r.querySelectorAll('td')];
  const qty=r.querySelector('input.qtyin')||tds[2]?.querySelector('input');
  const loc=r.querySelector('input.locin')||tds[3]?.querySelector('input');
  return {name:__qa.norm(tds[0].textContent).slice(0,40), qty:qty?qty.value:null, loc:loc?loc.value:null,
          locPh:loc?loc.placeholder:null, locNeed: !!(loc&&loc.closest('.loc-need'))};});
const anua=info.find(x=>/Anua/i.test(x.name));
const others=info.filter(x=>!/Anua/i.test(x.name)).map(x=>x.loc);
const footer=__qa.allBtnTexts(m);
const ok = anua && anua.qty==='0' && anua.loc==='' && anua.locPh==='required' && anua.locNeed
        && others.includes('A-03-2') && others.includes('B-01-4') && footer.includes('Confirm Restock (2)');
return __mk(!!ok, `rows=${JSON.stringify(info)} modalButtons=${JSON.stringify(footer)}`);
"""

JS["QA-S4-09"] = r"""
__qa.tab('4 · Customer Return Mode');
__qa.btnByText('#s4 .bulkbar','Restock Selected to Warehouse (3)').click();
const t=__qa.norm(document.querySelector('#m-restock').textContent);
const a=t.includes('Anua has restock qty 0 → excluded.');
const b=t.includes('if qty > 0 with no location, confirm stays disabled');
const c=t.includes('On completion, Current Stocks quantities and locations update automatically.');
return __mk(a&&b&&c, `amber1=${a} amber2=${b} blueNote=${c} | modalText="${t.slice(0,400)}"`);
"""

JS["QA-S4-10"] = r"""
__qa.tab('4 · Customer Return Mode');
__qa.btnByText('#s4 .bulkbar','Restock Selected to Warehouse (3)').click();
const ta=document.querySelector('#m-restock textarea.mtextarea');
const want='Return reason · condition (visible damage etc.) · notes — also recorded in the order’s Comments history and the inbound log';
const want2="Return reason · condition (visible damage etc.) · notes — also recorded in the order's Comments history and the inbound log";
const got=ta?ta.placeholder:null;
return __mk(!!ta && (got===want||got===want2), `textarea.mtextarea=${!!ta} placeholder="${got}"`);
"""

JS["QA-S4-06"] = r"""
__qa.tab('4 · Customer Return Mode');
__qa.cbtn('#s4 .bulkbar','Restock Selected to Warehouse (3)').click();
const m=document.querySelector('#m-restock');
const e=__qa.ex2(m.querySelector('header'),'Warehouse Restock — Order 412990');
return __mk2(m.classList.contains('open')&&e.lit, m.classList.contains('open')&&e.cleaned,
  `open=${m.classList.contains('open')} header literal="${e.litVal}" (contains the ✕ close button) stripped="${e.cleanVal}" expected="${e.expected}"`);
"""

JS["QA-S4-02"] = r"""
__qa.tab('4 · Customer Return Mode');
const pill=document.querySelector('#s4 .ordercard .status');
const pills=[...document.querySelectorAll('#s4 .status')].map(p=>__qa.norm(p.textContent));
return __mk(pill && __qa.norm(pill.textContent)==='refunded' && !pills.includes('returned'), `statusPills=${JSON.stringify(pills)}`);
"""

JS["QA-S5-01"] = r"""
__qa.tab('5 · Hold Order');
const b=document.querySelector('#s5 .holdbanner');
const lead=b.querySelector('b,strong,.big');
const e1=__qa.ex2(lead,'⏸ Hold Shipment');
const litBody=__qa.norm(b.textContent).replace(__qa.norm(lead.textContent),'').trim();
const clnBody=__qa.norm(__qa.clean(b)).replace(__qa.norm(__qa.clean(lead)),'').trim();
const want='CS team put this order on Hold per customer request (address change) — Order 414102 · Requested by Sara(CS) 07-13 09:20';
const pill=document.querySelector('#s5 .ordercard .status');
const pOK=pill&&__qa.norm(pill.textContent)==='On Hold'&&pill.classList.contains('st-hold');
return __mk2(e1.lit&&litBody===want&&pOK, e1.cleaned&&clnBody===want&&pOK,
  `lead="${e1.litVal}" bodyLiteral="${litBody}" bodyDotStripped="${clnBody}" expected="${want}" pill="${pill?__qa.norm(pill.textContent):null}"/${pill?pill.className:null}`);
"""

JS["QA-S5-03"] = r"""
__qa.tab('5 · Hold Order');
const bb=document.querySelector('#s5 .bulkbar');
const a=__qa.btnByText(bb,'Bulk Inbound (Selected)');
const c=__qa.btnByText(bb,'Inbound + Outbound All Remaining');
const e=__qa.ex(__qa.t(bb.querySelector('.cnt')),'Hold order — Inbound allowed, Outbound blocked (ship after Hold release)');
return __mk(a&&a.classList.contains('btn-green-line')&&c&&c.classList.contains('btn-gray')&&e.coll,
  `BulkInbound class="${a?a.className:'ABSENT'}" AllRemaining class="${c?c.className:'ABSENT'}" .cnt="${e.actual}" expected="${e.expected}"`,{byte:e.byte});
"""

JS["QA-S5-04"] = r"""
__qa.tab('5 · Hold Order');
const sec=document.querySelector('#s5 .logsec');
if(!sec) return __mk(false,'#s5 .logsec null');
const rows=[...sec.querySelectorAll('tbody tr')].map(r=>[...r.querySelectorAll('td')].map(t=>__qa.norm(t.textContent)));
const hit=rows.find(r=>r.includes('HOLD Applied'));
return __mk(!!hit && hit.includes('Sara (CS)') && hit.includes('Customer address change request — shipment held'),
  `rows=${JSON.stringify(rows)}`);
"""

JS["QA-S5-05"] = r"""
__qa.tab('5 · Hold Order');
const c=document.querySelector('#s5 .ordercard');
const texts=c?__qa.allBtnTexts(c):null;
return __mk(!!texts && texts.includes('🖨 Print'), `#s5 .ordercard buttons=${JSON.stringify(texts)}`);
"""

JS["QA-S5-02"] = r"""
__qa.tab('5 · Hold Order');
const lits=__qa.allBtnTexts('#s5 .ordercard'), clns=__qa.cbtnTexts('#s5 .ordercard');
const b=__qa.cbtn('#s5 .ordercard','Outbound');
return __mk2(lits.includes('Outbound')&&b&&b.classList.contains('btn-gray'), !!b&&b.classList.contains('btn-gray'),
  `ordercard buttons literal=${JSON.stringify(lits)} dotStripped=${JSON.stringify(clns)} class="${b?b.className:'ABSENT'}"`);
"""

JS["QA-S5-06"] = r"""
const ids=Object.keys(window.__tabs);
const hits=[];
for(const i of ids){ __qa.tab(window.__tabs[i]);
  for(const b of document.querySelectorAll('button')){
    const t=__qa.norm(b.textContent);
    if(t==='Hold Shipment'||t==='Release Hold') hits.push(i+':'+t);
  }
}
return __mk(hits.length===0, `matches=${JSON.stringify(hits)}`);
"""

JS["QA-S6-01"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const big=__qa.ex(__qa.t(document.querySelector('#s6 .intbanner .big')),'📦 Internal Inbound — Inbound Request');
const warn=__qa.ex(__qa.t(document.querySelector('#s6 .intbanner .warnline')),'Not a customer order · Goes into Inventory · No Outbound step');
const kv=__qa.norm(__qa.t(document.querySelector('#s6 .intbanner .kv'))||'');
const want=['Inbound No. 202607120001','WHOLESALE','비엠유통','Requested by Dean · 07-12','Expected arrival 07-18'];
const miss=want.filter(w=>!kv.includes(w));
return __mk(big.coll && warn.coll && miss.length===0,
  `big="${big.actual}" warnline="${warn.actual}" kv="${kv}" missingFromKv=${JSON.stringify(miss)}`,{byte:big.byte&&warn.byte});
"""

JS["QA-S6-02"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const a=document.querySelector('#s6 .intbanner a');
return __mk(!!a && __qa.norm(a.textContent)==='View in Inbound Request List →' && a.getAttribute('href').endsWith('../inbound-request/index.html#reqlist'),
  `text="${a?__qa.norm(a.textContent):null}" href="${a?a.getAttribute('href'):null}"`);
"""

JS["QA-S6-03"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const tiles=[...document.querySelectorAll('#s6 .tile')];
const info=tiles.map(t=>({txt:__qa.norm(t.textContent),cls:t.className}));
return __mk(tiles.length===4, `tileCount=${tiles.length} tiles=${JSON.stringify(info)}`);
"""

JS["QA-S6-04"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const el=document.querySelector('#s6 .scannote');
const w1='Now scan product barcodes — each scan adds +1 to that product’s received qty (continuous scanning · cursor auto-return · warning sound for products not in the request)';
const w2=w1.replace('’',"'");
const a=__qa.ex2(el,w1), b=__qa.ex2(el,w2);
return __mk2(a.lit||b.lit, a.cleaned||b.cleaned, `literal="${a.litVal}" dotStripped="${a.cleanVal}" expected="${w2}"`);
"""

JS["QA-S6-05"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const th=[...document.querySelectorAll('#s6 table thead th')];
const lit=th.map(t=>__qa.norm(t.textContent)), cln=th.map(t=>__qa.norm(__qa.clean(t)));
const want=['SKU No.','Brand','Product Name','Expected Qty','Received Qty','Location','Status'];
const rows=[...document.querySelectorAll('#s6 table tbody tr')];
const r1=rows[0],r2=rows[1];
const d1=r1?r1.querySelector('.tag-done'):null,p2=r2?r2.querySelector('.tag-part'):null;
const rowsOK=r1&&r1.classList.contains('row-done')&&d1&&__qa.norm(d1.textContent)==='✓ INBOUNDED'&&r2&&r2.classList.contains('row-part')&&p2&&__qa.norm(p2.textContent)==='In progress · 180 remaining';
return __mk2(JSON.stringify(lit)===JSON.stringify(want)&&rowsOK, JSON.stringify(cln)===JSON.stringify(want)&&rowsOK,
  `headers literal=${JSON.stringify(lit)} dotStripped=${JSON.stringify(cln)} want=${JSON.stringify(want)} rowsOK=${rowsOK}`);
"""

JS["QA-S6-06"] = r"""
const hits=[];
for(const id of ['s6','s6b']){
  for(const el of document.querySelectorAll('#'+id+' th, #'+id+' label')){
    if(__qa.norm(el.textContent).includes('Carrier')) hits.push(id+' <'+el.tagName+'> "'+__qa.norm(el.textContent)+'"');
  }
}
return __mk(hits.length===0, `th/label containing "Carrier"=${JSON.stringify(hits)}`);
"""

JS["QA-S6-07"] = r"""
__qa.tab('6b · Internal Inbound Complete');
const b=document.querySelector('#s6b .donebanner');
const t=__qa.norm(b?b.textContent:'');
const has=t.includes('Carrier recorded automatically');
return __mk(!has, `#s6b .donebanner text="${t.slice(0,300)}" containsCarrierClause=${has}`, {expectedKnownFail:true});
"""

JS["QA-S6-08"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const a=__qa.btnByText('#s6','Confirm Full Inbound (180 remaining)');
const b=__qa.btnByText('#s6','Save Partial Inbound');
return __mk(!!a && a.classList.contains('btn-gray') && !!b && b.classList.contains('btn-line'),
  `confirmBtn=${a?'"'+a.className+'"':'NOT FOUND'} partialBtn=${b?'"'+b.className+'"':'NOT FOUND'} allS6Buttons=${JSON.stringify(__qa.allBtnTexts('#s6'))}`);
"""

JS["QA-S6-09"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const want='On confirm: reflected in Inventory (Current Stocks) · Inbound Request List switches to INBOUNDED · Received Date recorded automatically';
const els=[...document.querySelectorAll('#s6 *')].map(e=>__qa.norm(e.textContent));
const hit=els.find(t=>t===want);
const near=els.filter(t=>t.startsWith('On confirm:')).sort((a,b)=>a.length-b.length)[0];
return __mk(!!hit, `exactMatchFound=${!!hit} nearest="${near||''}" expected="${want}"`);
"""

JS["QA-S6-10"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const inp=document.querySelector('#s6 tbody tr:nth-child(2) input.qtyin');
if(!inp) return __mk(false,'#s6 tbody tr:nth-child(2) input.qtyin is null');
inp.value='130'; __qa.fire(inp,'input');
const btn=[...document.querySelectorAll('#s6 button.flsave')].filter(b=>b.offsetParent!==null);
return __mk(btn.length>0 && __qa.norm(btn[0].textContent)==='Save',
  `visible button.flsave count=${btn.length} text="${btn[0]?__qa.norm(btn[0].textContent):null}" (spec §2.3 L-13 says .flsave is NOT wired to .qtyin, but this scenario is tagged [WF])`);
"""

JS["QA-S6-17"] = r"""
__qa.tab('6b · Internal Inbound Complete');
const big=__qa.ex(__qa.t(document.querySelector('#s6b .donebanner .big')),'✓ Full Inbound Complete — Inbound No. 202607120001');
const kv=__qa.norm(__qa.t(document.querySelector('#s6b .donebanner .kv'))||'');
const want=['Received 800 / 800 (2 SKUs)','Inventory updated (A-05-11 · B-02-07)','Inbound Request List switched to INBOUNDED'];
const miss=want.filter(w=>!kv.includes(w));
return __mk(big.coll && miss.length===0, `big="${big.actual}" kv="${kv}" missing=${JSON.stringify(miss)}`,{byte:big.byte});
"""

JS["QA-S6-18"] = r"""
__qa.tab('6b · Internal Inbound Complete');
const rows=[...document.querySelectorAll('#s6b tbody tr')];
const info=rows.map(r=>({cls:r.className, done:!!r.querySelector('.tag-done'), tag:r.querySelector('.tag-done')?__qa.norm(r.querySelector('.tag-done').textContent):null,
  cells:[...r.querySelectorAll('td')].map(t=>__qa.norm(t.textContent))}));
const inputs=document.querySelectorAll('#s6b tbody input').length;
const recv=info.map(i=>i.cells[4]);
return __mk(rows.length===2 && info.every(i=>/row-done/.test(i.cls)&&i.tag==='✓ INBOUNDED') && inputs===0 && recv[0]==='500' && recv[1]==='300',
  `rows=${JSON.stringify(info)} inputsInTbody=${inputs}`);
"""

JS["QA-S6-19"] = r"""
__qa.tab('6b · Internal Inbound Complete');
const n=document.querySelector('#s6b .note');
const want='Cursor returns to the search box immediately on completion — scan the next tracking number with no refresh. This stock is visible in Inventory (Current Stocks) with its locations.';
const e=__qa.ex2(n,want);
return __mk2(e.lit, e.cleaned, `literal="${e.litVal}" dotStripped="${e.cleanVal}" expected="${want}"`);
"""

JS["QA-S6-20"] = r"""
const bad=[];
for(const id of ['s6','s6b']){
  const sc=document.querySelector('#'+id);
  if(__qa.btnByText(sc,'Outbound')) bad.push(id+':Outbound button');
  if(sc.querySelector('.bulkbar')) bad.push(id+':.bulkbar');
  if(sc.querySelector('.ordercard')) bad.push(id+':.ordercard');
  if([...sc.querySelectorAll('button')].some(b=>__qa.norm(b.textContent).startsWith('🖨 Print Return Labels'))) bad.push(id+':PrintReturnLabels');
}
return __mk(bad.length===0, `violations=${JSON.stringify(bad)}`);
"""

JS["QA-S6-21"] = r"""
__qa.tab('6b · Internal Inbound Complete');
const ts=[...document.querySelectorAll('#s6b .toast, .toast')];
const hit=ts.find(t=>__qa.norm(t.textContent).includes('✓ Inbound complete — Inbound No. 202607120001'));
const sub=hit?hit.querySelector('small'):null;
const e=sub?__qa.ex(__qa.t(sub),'Inventory updated · Request list INBOUNDED · ready for the next tracking scan'):{coll:false,actual:'no <small>',byte:false};
return __mk(!!hit && e.coll, `toasts=${JSON.stringify(ts.map(t=>__qa.norm(t.textContent).slice(0,110)))} sub="${e.actual}"`,{byte:e.byte});
"""

JS["QA-S6-12"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const btns=document.querySelectorAll('#s6 button.qedit');
const row=btns[1].closest('tr');
const rowHasSku=__qa.norm(__qa.clean(row)).includes('100052124');
btns[1].click();
const m=document.querySelector('#m-qtyedit');
const e=__qa.ex2(m.querySelector('header'),'Edit Expected Qty — Inbound No. 202607120002');
const inputs=[...m.querySelectorAll('input')].map(i=>i.value);
const txt=__qa.norm(__qa.clean(m));
const helper=txt.includes('300 → 120 (−180)');
const opts=[...m.querySelectorAll('select option')].map(o=>__qa.norm(o.textContent));
const want=['Damaged/defective — cannot accept','Supplier qty change','Other'];
const rest=m.classList.contains('open')&&inputs.includes('120')&&helper&&want.every(w=>opts.includes(w));
return __mk2(e.lit&&rest, e.cleaned&&rest,
  `qedit[1] rowContainsSKU100052124=${rowHasSku} header literal="${e.litVal}" stripped="${e.cleanVal}" inputs=${JSON.stringify(inputs)} helperFound=${helper} options=${JSON.stringify(opts)}`);
"""

JS["QA-S6-13"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
document.querySelectorAll('#s6 button.qedit')[1].click();
const sel=document.querySelector('#m-qtyedit select');
const opts=[...sel.querySelectorAll('option')].map(o=>__qa.norm(o.textContent));
return __mk(opts.length===3 && opts[2]==='Other', `optionCount=${opts.length} options=${JSON.stringify(opts)}`);
"""

JS["QA-S6-14"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
document.querySelectorAll('#s6 button.qedit')[1].click();
const m=document.querySelector('#m-qtyedit');
const ta=m.querySelector('textarea');
const txt=__qa.norm(__qa.clean(m));
const q=['Confirm Full Inbound enabled','auto-posted as a Comment on this Inbound Request','the requester (@Dean) gets a Slack alert','the request list qty cell shows the edit history (300→120)'];
const res=q.map(x=>({q:x,found:txt.includes(x)}));
const ci=q.map(x=>({q:x,foundCaseInsensitive:txt.toLowerCase().includes(x.toLowerCase())}));
const foot=__qa.cbtnTexts(m.querySelector('.foot'));
const ok=ta&&ta.value==='1 box damaged — 180 units rejected, returned to supplier'&&res.every(r=>r.found)&&foot.includes('Save Qty Edit');
return __mk(ok, `textarea="${ta?ta.value:null}" quotedFragments=${JSON.stringify(res)} caseInsensitive=${JSON.stringify(ci)} footButtons=${JSON.stringify(foot)} | actualSentence="${(txt.match(/The request list qty cell[^.]*\./)||[''])[0]}"`);
"""

JS["QA-S6-15"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
__qa.cbtn('#s6','Save Partial Inbound').click();
const m=document.querySelector('#m-partial');
const e=__qa.ex2(m.querySelector('header'),'Save Partial Inbound — Inbound No. 202607120001');
const txt=__qa.norm(__qa.clean(m));
const lead=txt.includes('Only 620 of the 800 expected units have been received (180 remaining).');
const line=txt.includes('1025 Dokdo Cleanser, 150ml — expected 300 / received 120 / remaining 180');
const opts=[...m.querySelectorAll('select option')].map(o=>__qa.norm(o.textContent));
const want=['Split shipment — remainder arriving later','Short delivery (needs supplier confirmation)','Partially damaged — will be returned to supplier'];
const rest=m.classList.contains('open')&&lead&&line&&want.every(w=>opts.includes(w));
return __mk2(e.lit&&rest, e.cleaned&&rest,
  `header literal="${e.litVal}" stripped="${e.cleanVal}" leadFound=${lead} perSkuLineFound=${line} options=${JSON.stringify(opts)}`);
"""

JS["QA-S6-16"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
__qa.btnByText('#s6','Save Partial Inbound').click();
const m=document.querySelector('#m-partial');
const txt=__qa.norm(m.textContent);
const a=txt.includes('added to Inventory immediately');
const b=txt.includes('Partial Inbound (620/800)');
const c=txt.includes('3 stages: REQUESTED → PARTIAL → INBOUNDED');
const d=txt.includes('rescan the same tracking number to continue in State 6');
const ta=m.querySelector('textarea');
const ph=ta?ta.placeholder:null;
const wantPh1='e.g. Remaining 180 units arriving Friday — also recorded in the request’s Comments';
const wantPh2="e.g. Remaining 180 units arriving Friday — also recorded in the request's Comments";
const foot=__qa.allBtnTexts(m);
return __mk(a&&b&&c&&d&&(ph===wantPh1||ph===wantPh2)&&foot.includes('Save Partial Inbound'),
  `notes={inv:${a},partial:${b},stages:${c},rescan:${d}} placeholder="${ph}" buttons=${JSON.stringify(foot)}`);
"""

JS["QA-S6-11"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const locs=[...document.querySelectorAll('#s6 tbody input.locin')];
const vals=locs.map(l=>l.value);
if(locs.length<2) return __mk(false,'input.locin count='+locs.length+' values='+JSON.stringify(vals));
locs[1].value='B-02-08'; __qa.fire(locs[1],'input');
const btn=[...document.querySelectorAll('#s6 button.flsave')].filter(b=>b.offsetParent!==null);
return __mk(vals[0]==='A-05-11' && vals[1]==='B-02-07' && btn.length>0,
  `locinValues=${JSON.stringify(vals)} flsaveVisibleAfterInput=${btn.length}`);
"""

JS["QA-M1-01"] = r"""
__qa.tab('Modal: Cancel Inbound');
const m=document.querySelector('#m-cancel');
const e=__qa.ex2(m.querySelector('header'),'Cancel Inbound — 100038120');
const yes=document.querySelector('input[name="restock"][value="yes"]');
const q=document.querySelector('#restockQty');
const t=__qa.norm(__qa.clean(m));
const note=t.includes('The SKU’s Reserved Quantity → Available updates automatically.')||t.includes("The SKU's Reserved Quantity → Available updates automatically.");
const rest=yes&&yes.checked&&q&&q.value==='2'&&note;
return __mk2(e.lit&&rest, e.cleaned&&rest,
  `header literal="${e.litVal}" stripped="${e.cleanVal}" yesChecked=${yes?yes.checked:null} restockQty="${q?q.value:null}" noteFound=${note}`);
"""

JS["QA-M1-02"] = r"""
__qa.tab('Modal: Cancel Inbound');
const no=document.querySelector('input[name="restock"][value="no"]');
const yes=document.querySelector('input[name="restock"][value="yes"]');
const q=document.querySelector('#restockQty');
no.checked=true; __qa.fire(no,'change');
const s1={disabled:q.disabled, value:q.value};
yes.checked=true; __qa.fire(yes,'change');
const s2={disabled:q.disabled, value:q.value};
return __mk(s1.disabled===true && s1.value==='' && s2.disabled===false && s2.value==='2',
  `afterNo=${JSON.stringify(s1)} afterYes=${JSON.stringify(s2)}`);
"""

JS["QA-M1-03"] = r"""
__qa.tab('Modal: Cancel Inbound');
const m=document.querySelector('#m-cancel');
const txt=__qa.norm(m.textContent);
const helper=txt.includes('Default = qty that was inbounded (editable) · disabled when "No" is selected')
          || txt.includes('Default = qty that was inbounded (editable) · disabled when “No” is selected');
const ta=m.querySelector('textarea');
const ph=ta?ta.placeholder:null;
const wp1='Cancellation reason or notes — also recorded in the order’s Comments history';
const wp2="Cancellation reason or notes — also recorded in the order's Comments history";
const uc=txt.includes('a JIT order placed by mistake when warehouse stock exists');
return __mk(helper && (ph===wp1||ph===wp2) && uc, `helperFound=${helper} memoPlaceholder="${ph}" useCaseFound=${uc}`);
"""

JS["QA-M1-04"] = r"""
__qa.tab('Modal: Cancel Inbound');
const m=document.querySelector('#m-cancel');
const foot=m.querySelector('.foot');
const texts=__qa.cbtnTexts(foot);
m.click();
const closed=!m.classList.contains('open');
return __mk(texts.length===2&&texts[0]==='Close'&&texts[1]==='Confirm'&&closed,
  `(spec never names the footer element; used .foot) buttons=${JSON.stringify(texts)} closedByBackdrop=${closed}`);
"""

JS["QA-M2-01"] = r"""
__qa.tab('Modal: Unrecognized Barcode');
const m=document.querySelector('#m-unrec');
const e=__qa.ex2(m.querySelector('header'),'Barcode Not Recognized');
const txt=__qa.norm(__qa.clean(m));
const lead=txt.includes('No order matches the scanned barcode 8809110223344.');
const instr=txt.includes('Enter the Coupang purchase order number to find matching products and register the tracking number on the spot.');
const no=document.querySelector('#unrecNo');
const rest=m.classList.contains('open')&&lead&&instr&&no&&no.value==='12101316464794';
return __mk2(e.lit&&rest, e.cleaned&&rest,
  `header literal="${e.litVal}" stripped="${e.cleanVal}" leadFound=${lead} instructionFound=${instr} unrecNo="${no?no.value:null}"`);
"""

JS["QA-M2-02"] = r"""
__qa.tab('Modal: Unrecognized Barcode');
document.querySelector('#unrecSearch').click();
const f=document.querySelector('#unrecFound'), n=document.querySelector('#unrecNone');
const vis=f.offsetParent!==null || getComputedStyle(f).display!=='none';
const rows=[...f.querySelectorAll('tbody tr')];
const th=__qa.ths('#unrecFound thead th');
const want=['Image','Product Name','Order','Qty','Tracking No',''];
const c=rows[0]?[...rows[0].querySelectorAll('td')].map(t=>__qa.norm(t.textContent)):[];
const noneHidden=getComputedStyle(n).display==='none';
const r1=__qa.norm(rows[0]?rows[0].textContent:'');
return __mk(vis && rows.length===2 && JSON.stringify(th)===JSON.stringify(want) &&
  r1.includes('Pore Remedy Renewing Foam Cleanser') && r1.includes('포어레미디 리뉴잉 폼 클렌저') &&
  r1.includes('414230') && r1.includes('10323100835644') && noneHidden,
  `visible=${vis} rows=${rows.length} headers=${JSON.stringify(th)} want=${JSON.stringify(want)} row1Cells=${JSON.stringify(c)} unrecNoneHidden=${noneHidden}`);
"""

JS["QA-M2-03"] = r"""
__qa.tab('Modal: Unrecognized Barcode');
document.querySelector('#unrecSearch').click();
const want='Clicking match registers the tracking number on that line and closes this window — rescanning the same barcode is then recognized normally.';
const els=[...document.querySelectorAll('#unrecFound *, #m-unrec *')].map(e=>__qa.norm(e.textContent));
const hit=els.find(t=>t===want);
const near=els.filter(t=>t.startsWith('Clicking match')).sort((a,b)=>a.length-b.length)[0];
return __mk(!!hit, `exactNoteFound=${!!hit} nearest="${near||''}"`);
"""

JS["QA-M2-05"] = r"""
__qa.tab('Modal: Unrecognized Barcode');
document.querySelector('#unrecNo').value='99999999999999';
document.querySelector('#unrecSearch').click();
const f=document.querySelector('#unrecFound'), n=document.querySelector('#unrecNone');
const fh=getComputedStyle(f).display==='none';
const nv=getComputedStyle(n).display!=='none';
const t=__qa.norm(n.textContent);
return __mk(fh && nv && t.includes('No products match') && t.includes('possible typo or a number from another channel'),
  `unrecFoundHidden=${fh} unrecNoneVisible=${nv} unrecNoneText="${t.slice(0,200)}"`);
"""

JS["QA-M2-06"] = r"""
__qa.tab('Modal: Unrecognized Barcode');
document.querySelector('#unrecNo').value='99999999999999';
document.querySelector('#unrecSearch').click();
document.querySelector('#unrecToSend').click();
const m1=document.querySelector('#m-unrec'), m2=document.querySelector('#m-unrec2');
const c=document.querySelector('#unrecCarried'), cn=document.querySelector('#unrecCarriedNo');
const cvis=c?getComputedStyle(c).display!=='none':false;
return __mk(!m1.classList.contains('open') && m2.classList.contains('open') && cvis && cn && __qa.norm(cn.textContent)==='99999999999999',
  `m-unrec.open=${m1.classList.contains('open')} m-unrec2.open=${m2.classList.contains('open')} unrecCarriedVisible=${cvis} unrecCarriedNo="${cn?__qa.norm(cn.textContent):null}"`);
"""

JS["QA-M2-07"] = r"""
__qa.tab('Modal: Unrecognized Barcode');
document.querySelector('#unrecNoNum').click();
const m2=document.querySelector('#m-unrec2');
const c=document.querySelector('#unrecCarried');
return __mk(m2.classList.contains('open') && c && c.style.display==='none',
  `m-unrec2.open=${m2.classList.contains('open')} #unrecCarried style.display="${c?c.style.display:null}" computed="${c?getComputedStyle(c).display:null}"`);
"""

JS["QA-M2-08"] = r"""
const files=document.querySelectorAll('input[type=file]').length;
const bad=[];
for(const st of Object.keys(window.__tabs)){
  __qa.tab(window.__tabs[st]);
  const t=document.body.innerText;
  for(const w of ['Photo','사진','Upload','Camera']) if(t.includes(w)) bad.push(st+':'+w);
}
for(const mid of ['m-cancel','m-unrec','m-unrec2','m-restock','m-retlabel','m-partial','m-qtyedit']){
  const lbl={'m-cancel':'Modal: Cancel Inbound','m-unrec':'Modal: Unrecognized Barcode','m-unrec2':'Modal: Send to Missing Tracking List','m-restock':'Modal: Customer Return Restock','m-retlabel':'Modal: Return Label','m-partial':'Modal: Save Partial Inbound','m-qtyedit':'Modal: Edit Expected Qty'}[mid];
  __qa.tab(lbl);
  const t=document.body.innerText;
  for(const w of ['Photo','사진','Upload','Camera']) if(t.includes(w)) bad.push(mid+':'+w);
}
return __mk(files===0 && bad.length===0, `input[type=file]=${files} forbiddenWordHits=${JSON.stringify(bad)}`);
"""

JS["QA-M2-09"] = r"""
__qa.tab('Modal: Unrecognized Barcode');
const m=document.querySelector('#m-unrec');
const texts=__qa.cbtnTexts(m.querySelector('.foot'));
const want='Demo: look up with this value = match-found path · change the value = no-match path';
const els=[...m.querySelectorAll('*')].map(e=>__qa.norm(__qa.clean(e)));
const hint=els.includes(want);
return __mk(texts.length===2&&texts[0]==='No order number'&&texts[1]==='Cancel'&&hint,
  `(spec never names the footer element; used .foot) footButtons=${JSON.stringify(texts)} demoHintExact=${hint}`);
"""

JS["QA-M2-10"] = r"""
__qa.tab('Modal: Send to Missing Tracking List');
const m=document.querySelector('#m-unrec2');
const e=__qa.ex2(m.querySelector('header'),'Send to Missing Tracking List');
const txt=__qa.norm(__qa.clean(m));
const lead=txt.includes('Barcode 8809110223344 — send it to the Missing Tracking List?');
const prompt=txt.includes('Enter the product name (English — autocomplete · Korean name shown alongside)');
const auto=m.querySelector('.auto input');
const opts=[...m.querySelectorAll('.opt')];
const first=opts[0];
const firstTxt=first?__qa.norm(__qa.clean(first)):null;
const inputs=[...m.querySelectorAll('input')].map(i=>i.value);
const ta=m.querySelector('textarea');
const wp='e.g. Box label damaged, looks like a 1+1 set — shown in the Missing Tracking List and the Slack alert';
const checks={lead,prompt,autoVal:auto?auto.value:null,optCount:opts.length,firstSel:first?first.classList.contains('sel'):null,
  firstHasEN:firstTxt?firstTxt.includes('Beauty of Joseon — Glow Serum : Propolis + Niacinamide, 30ml'):null,
  firstHasKR:firstTxt?firstTxt.includes('프로폴리스 나이아신아마이드 글로우 세럼'):null,
  qtyInputValues:inputs, memoPh:ta?ta.placeholder:null, memoPhMatches:ta?ta.placeholder===wp:null};
const rest=lead&&prompt&&auto&&auto.value==='glow ser'&&opts.length===3&&checks.firstSel&&checks.firstHasEN&&checks.firstHasKR&&inputs.includes('1')&&checks.memoPhMatches;
return __mk2(e.lit&&rest, e.cleaned&&rest,
  `header literal="${e.litVal}" stripped="${e.cleanVal}" checks=${JSON.stringify(checks)} firstOpt="${firstTxt}"`);
"""

JS["QA-M2-11"] = r"""
__qa.tab('Modal: Send to Missing Tracking List');
const m=document.querySelector('#m-unrec2');
const want='On send, the #unrecognized-tracking channel gets an "Unrecognized product added" alert (product name · barcode · qty · memo · order number if lookup failed) → shown in the unrecognized pool on the Missing Tracking List page.';
const els=[...m.querySelectorAll('*')].map(e=>__qa.norm(e.textContent));
const hit=els.find(t=>t===want || t===want.replace(/"/g,'“').replace(/“Unrecognized product added”/,'“Unrecognized product added”'));
const near=els.filter(t=>t.startsWith('On send,')).sort((a,b)=>a.length-b.length)[0];
return __mk(!!hit, `exactNoteFound=${!!hit} nearest="${near||''}"`);
"""

JS["QA-M4-01"] = r"""
__qa.tab('Modal: Return Label');
const m=document.querySelector('#m-retlabel');
const e=__qa.ex2(m.querySelector('header'),'Print Return Labels — 2 Selected Products (Supplier Return)');
const chips=[...m.querySelectorAll('.cchip')].map(c=>__qa.norm(__qa.clean(c)));
const want=['CJ대한통운','롯데택배','한진택배','우체국택배','로젠택배','✎ Custom'];
const on=[...m.querySelectorAll('.cchip.on')].map(c=>__qa.norm(__qa.clean(c)));
const rest=m.classList.contains('open')&&JSON.stringify(chips)===JSON.stringify(want)&&on.length===1&&on[0]==='CJ대한통운';
return __mk2(e.lit&&rest, e.cleaned&&rest,
  `header literal="${e.litVal}" stripped="${e.cleanVal}" chips=${JSON.stringify(chips)} onChips=${JSON.stringify(on)}`);
"""

JS["QA-M4-02"] = r"""
__qa.tab('Modal: Return Label');
const th=__qa.ths('#m-retlabel thead th');
const want=['Product Name KR','Size (optional)','Qty (optional)'];
const rows=[...document.querySelectorAll('#m-retlabel tbody tr')];
const info=rows.map(r=>{const tds=[...r.querySelectorAll('td')];
  const b=tds[0].querySelector('b');
  const ins=[...r.querySelectorAll('input')].map(i=>i.value);
  return {brand:b?__qa.norm(b.textContent):null, name:__qa.norm(tds[0].textContent), inputs:ins};});
return __mk(JSON.stringify(th)===JSON.stringify(want) && info.length>=2 && info[0].brand==='Dr.Jart+' && info[1].brand==='Medicube',
  `headers=${JSON.stringify(th)} want=${JSON.stringify(want)} rows=${JSON.stringify(info)}`);
"""

JS["QA-M4-03"] = r"""
__qa.tab('Modal: Return Label');
const c=document.querySelector('#rlPreviewCarrier');
const m=document.querySelector('#m-retlabel');
const lines=[...m.querySelectorAll('*')].map(e=>__qa.norm(e.textContent));
const l1=lines.includes('Dr.Jart+ 포어레미디 리뉴잉 폼 클렌저 · 150ml · 1개');
const l2=lines.includes('Medicube 제로 모공 패드 2.0 · 2개');
const nearest=lines.filter(t=>t.startsWith('Dr.Jart+ 포어')||t.startsWith('Medicube 제로')).slice(0,4);
return __mk(c && __qa.norm(c.textContent)==='CJ대한통운' && l1 && l2,
  `#rlPreviewCarrier="${c?__qa.norm(c.textContent):null}" line1Exact=${l1} line2Exact=${l2} previewLines=${JSON.stringify(nearest)}`);
"""

JS["QA-M4-04"] = r"""
__qa.tab('Modal: Return Label');
document.querySelector('#cchipCustom').click();
const row=document.querySelector('#rlCustomRow');
const rowVis=getComputedStyle(row).display!=='none';
const ae=document.activeElement===document.getElementById('rlCarrierCustom');
const pc=document.querySelector('#rlPreviewCarrier');
const p1=__qa.norm(pc.textContent);
const on=[...document.querySelectorAll('#m-retlabel .cchip.on')].map(c=>__qa.norm(c.textContent));
const inp=document.querySelector('#rlCarrierCustom');
inp.value='대신택배'; __qa.fire(inp,'input');
const p2=__qa.norm(pc.textContent);
return __mk(rowVis && ae && p1==='Carrier name' && on.length===1 && on[0]==='✎ Custom' && p2==='대신택배',
  `rlCustomRowVisible=${rowVis} activeElementIsCustomInput=${ae} previewAfterChipClick="${p1}" onChips=${JSON.stringify(on)} previewAfterTyping="${p2}"`);
"""

JS["QA-M4-05"] = r"""
__qa.tab('Modal: Return Label');
const rows=[...document.querySelectorAll('#m-retlabel tbody tr')];
const r2=rows[1];
const ins=r2?[...r2.querySelectorAll('input')]:[];
const sizeIn=ins[0];
const want='Use case: during inbound scanning, return items to the supplier (e.g. Coupang seller) when wrong/damaged items are found. Printing puts carrier name + product name (KR) + size + qty on the label — size/qty omitted if empty; attach it to the return box.';
const els=[...document.querySelectorAll('#m-retlabel *')].map(e=>__qa.norm(e.textContent));
const hit=els.includes(want);
const near=els.filter(t=>t.startsWith('Use case:')).sort((a,b)=>a.length-b.length)[0];
return __mk(sizeIn && sizeIn.value==='' && sizeIn.placeholder==='omitted if empty' && hit,
  `row2 sizeInput value="${sizeIn?sizeIn.value:null}" placeholder="${sizeIn?sizeIn.placeholder:null}" noteExact=${hit} nearestNote="${(near||'').slice(0,240)}"`);
"""

JS["QA-M4-06"] = r"""
__qa.tab('Modal: Return Label');
const t=__qa.cbtnTexts(document.querySelector('#m-retlabel .foot'));
return __mk(t.length===2&&t[0]==='Cancel'&&t[1]==='🖨 Print', `(spec never names the footer element; used .foot) footButtons=${JSON.stringify(t)}`);
"""

JS["QA-M4-07"] = r"""
const present={}, absent={};
for(const [id,lbl] of Object.entries(window.__tabs)){
  __qa.tab(lbl);
  const b=[...document.querySelectorAll('#'+id+' button')].find(x=>__qa.norm(x.textContent)==='🖨 Print Return Labels (2)');
  if(['s1','s1b','s2','s3'].includes(id)) present[id]=!!b;
  if(['s4','s5','s6','s6b'].includes(id)) absent[id]=!!b;
}
__qa.tab(window.__tabs.s1);
const b1=[...document.querySelectorAll('#s1 button')].find(x=>__qa.norm(x.textContent)==='🖨 Print Return Labels (2)');
let opened=false;
if(b1){ b1.click(); opened=document.querySelector('#m-retlabel').classList.contains('open'); }
return __mk(Object.values(present).every(Boolean) && Object.values(absent).every(v=>v===false) && opened,
  `presentIn=${JSON.stringify(present)} presentInStatesThatShouldNotHaveIt=${JSON.stringify(absent)} clickOpensM4=${opened}`);
"""

JS["QA-C-01"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const p=document.querySelector('#cpanel1');
const vis=p && getComputedStyle(p).display!=='none';
const items=[...p.querySelectorAll('.c-item')];
const first=items[0];
const at=first?first.querySelector('span.at'):null;
const comp=p.querySelector('input');
const ph=comp?comp.placeholder:null;
const wp1='Write a comment — @name sends an automatic Slack alert (order no · text · time · author)';
const btn=[...p.querySelectorAll('button')].map(b=>__qa.norm(b.textContent));
return __mk(vis && items.length===2 && first && __qa.norm(first.textContent).includes('Dean') && at && __qa.norm(at.textContent).includes('@Yongwon') && ph===wp1 && btn.includes('Post'),
  `visible=${vis} cItemCount=${items.length} firstAuthorHasDean=${first?__qa.norm(first.textContent).includes('Dean'):null} span.at="${at?__qa.norm(at.textContent):null}" composerPlaceholder="${ph}" buttons=${JSON.stringify(btn)}`);
"""

JS["QA-C-02"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const card=document.querySelector('#s1 .ordercard');
const btn=[...card.querySelectorAll('button')].find(b=>__qa.norm(b.textContent).startsWith('💬 Comments'));
const badge=btn?btn.querySelector('.badge-n'):null;
const p=document.querySelector('#cpanel1');
const v0=getComputedStyle(p).display!=='none';
btn.click(); const v1=getComputedStyle(p).display!=='none';
btn.click(); const v2=getComputedStyle(p).display!=='none';
return __mk(!!badge && __qa.norm(badge.textContent)==='2' && v0===true && v1===false && v2===true,
  `badge="${badge?__qa.norm(badge.textContent):null}" visibleBefore=${v0} afterClick1=${v1} afterClick2=${v2}`);
"""

JS["QA-C-03"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const b=document.querySelector('button[data-open="inbox1"]');
if(!b) return __mk(false,'button[data-open="inbox1"] not found');
b.click();
const dd=document.querySelector('#inbox1');
const tabs=[...dd.querySelectorAll('.tabs *')].map(e=>__qa.norm(e.textContent)).filter(t=>t);
const men=tabs.find(t=>t.startsWith('@ Mentions'));
const sav=tabs.find(t=>t.startsWith('★ Saved'));
const txt=__qa.norm(dd.textContent);
const hdr=txt.includes("Comments where I’m tagged · Click to open the order page") || txt.includes("Comments where I'm tagged · Click to open the order page");
const mark=txt.includes('Mark all as read');
return __mk(dd.classList.contains('open') && !!men && /3/.test(men||'') && !!sav && hdr && mark,
  `open=${dd.classList.contains('open')} tabTexts=${JSON.stringify(tabs.slice(0,6))} headerFound=${hdr} markAllAsRead=${mark}`);
"""

JS["QA-C-04"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
document.querySelector('button[data-open="inbox1"]').click();
const dd=document.querySelector('#inbox1');
const all=[...dd.querySelectorAll('.it')];
const visible=all.filter(e=>__qa.vis(e));
const unread=visible.filter(e=>e.classList.contains('unread'));
const orders=visible.map(e=>{const m=__qa.norm(e.textContent).match(/41\d{4}/);return m?m[0]:null;});
return __mk(visible.length===4&&unread.length===3&&JSON.stringify(orders)===JSON.stringify(['413865','413712','413650','413501']),
  `(spec says "the mentions pane" but names no selector; used visible .it) allItInDropdown=${all.length} visible=${visible.length} unread=${unread.length} orders=${JSON.stringify(orders)}`);
"""

JS["QA-C-06"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
document.querySelector('button[data-open="inbox1"]').click();
const dd=document.querySelector('#inbox1');
const s=dd.querySelector('.csearch input');
s.value='restock'; __qa.fire(s,'input');
const tabs=dd.querySelector('.tabs');
const tabsHidden=getComputedStyle(tabs).display==='none';
const txt=__qa.norm(dd.textContent);
const hdr=txt.includes('2 results · newest first · click to open the order page');
const marks=[...dd.querySelectorAll('mark')].map(m=>__qa.norm(m.textContent));
const orders=[...dd.querySelectorAll('.it')].filter(e=>e.offsetParent!==null).map(e=>{const m=__qa.norm(e.textContent).match(/41\d{4}/);return m?m[0]:null;});
return __mk(tabsHidden && hdr && marks.length>0 && JSON.stringify(orders)===JSON.stringify(['413650','412990']),
  `tabsHidden=${tabsHidden} headerFound=${hdr} markCount=${marks.length} visibleResultOrders=${JSON.stringify(orders)}`);
"""

JS["QA-C-07"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
document.querySelector('button[data-open="inbox1"]').click();
const dd=document.querySelector('#inbox1');
const s=dd.querySelector('.csearch input');
s.value='zzzznotfound'; __qa.fire(s,'input');
const txt=__qa.norm(dd.textContent);
return __mk(txt.includes('No matching Comments'), `panelText="${txt.slice(0,220)}"`);
"""

JS["QA-C-08"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
document.querySelector('button[data-open="inbox1"]').click();
const dd=document.querySelector('#inbox1');
const s=dd.querySelector('.csearch input');
s.value='restock'; __qa.fire(s,'input');
s.value=''; __qa.fire(s,'input');
const tabs=dd.querySelector('.tabs');
const vis=getComputedStyle(tabs).display!=='none';
const panes=[...dd.querySelectorAll('.pane')].map(p=>({cls:p.className,disp:getComputedStyle(p).display}));
return __mk(vis, `tabsVisible=${vis} panes=${JSON.stringify(panes)}`);
"""

JS["QA-C-05"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
document.querySelector('button[data-open="inbox1"]').click();
const dd=document.querySelector('#inbox1');
const savedTab=[...dd.querySelectorAll('.tabs *')].find(e=>__qa.norm(e.textContent).startsWith('★ Saved'));
savedTab.click();
const visIts=[...dd.querySelectorAll('.it')].filter(e=>e.offsetParent!==null);
const orders=visIts.map(e=>{const m=__qa.norm(e.textContent).match(/41\d{4}/);return m?m[0]:null;});
const stars=visIts.map(e=>{const s=e.querySelector('button.star');return s?s.className:null;});
const txt=__qa.norm(dd.textContent);
const hdr=txt.includes("Comments I saved · Click to open the order page")&&txt.includes('Unstar to remove from list');
return __mk(visIts.length===2 && JSON.stringify(orders)===JSON.stringify(['413712','412990']) && stars.every(c=>c&&/\bon\b/.test(c)) && hdr,
  `visibleEntries=${visIts.length} orders=${JSON.stringify(orders)} starClasses=${JSON.stringify(stars)} headerFound=${hdr}`);
"""

JS["QA-C-09"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const st=document.querySelector('#cpanel1 .c-item button.star');
if(!st) return __mk(false,'no button.star inside first #cpanel1 .c-item');
const c0=st.className; st.click(); const c1=st.className; st.click(); const c2=st.className;
return __mk(!/\bon\b/.test(c0)&&/\bon\b/.test(c1)&&!/\bon\b/.test(c2), `class before="${c0}" afterClick1="${c1}" afterClick2="${c2}"`);
"""

JS["QA-C-10"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const b=document.querySelector('button[data-open="inbox6"]');
if(!b) return __mk(false,'button[data-open="inbox6"] not found');
b.click();
const dd=document.querySelector('#inbox6');
const badge=b.querySelector('.badge-n');
const txt=__qa.norm(dd.textContent);
const hdr=txt.includes("Comments where I’m tagged · Click to open the item")||txt.includes("Comments where I'm tagged · Click to open the item");
return __mk(badge && __qa.norm(badge.textContent)==='2' && txt.includes('Inbound 202607120001') && txt.includes('Inbound 202607100005') && hdr,
  `badge="${badge?__qa.norm(badge.textContent):null}" hasReq1=${txt.includes('Inbound 202607120001')} hasReq2=${txt.includes('Inbound 202607100005')} headerFound=${hdr} paneHeader="${(txt.match(/Comments where[^·]*· [^·]*/)||[''])[0]}"`);
"""

JS["QA-C-11"] = r"""
const want='🔍 Search all Comments — order no · author · text';
const got={}; let ok=true;
for(const id of ['s0','s1','s1b','s2','s3','s4','s5']){
  __qa.tab(window.__tabs[id]);
  const dd=document.querySelector('#'+id+' .inboxdd');
  const inp=dd?dd.querySelector('.csearch input'):null;
  got[id]= inp?inp.placeholder:(dd?'no .csearch input':'no .inboxdd');
  if(!inp||inp.placeholder!==want) ok=false;
}
return __mk(ok, `perState=${JSON.stringify(got)} want="${want}"`);
"""

JS["QA-LG-01"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const f=document.querySelector('#scanfloat');
if(!f) return __mk(false,'#scanfloat null in State 1');
const h=f.querySelector('header');
const txt=__qa.norm(h?h.textContent:'');
const badge=h?[...h.querySelectorAll('*')].map(e=>__qa.norm(e.textContent)).filter(t=>t==='4'):[];
const ul=f.querySelector('ul'), ft=f.querySelector('footer');
const ulHidden=ul?getComputedStyle(ul).display==='none':null;
const ftHidden=ft?getComputedStyle(ft).display==='none':null;
return __mk(f.classList.contains('collapsed') && txt.includes('📡 Live Barcode Feed') && badge.length>0 && ulHidden===true && ftHidden===true,
  `collapsed=${f.classList.contains('collapsed')} header="${txt}" badge4Found=${badge.length>0} ulHidden=${ulHidden} footerHidden=${ftHidden}`);
"""

JS["QA-LG-02"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const f=document.querySelector('#scanfloat');
f.querySelector('header').click();
const lis=[...f.querySelectorAll('ul li')];
const x=f.querySelector('.x');
const ft=f.querySelector('footer');
const ftTxt=__qa.norm(ft?ft.textContent:'');
const ftBtn=ft?[...ft.querySelectorAll('button')].map(b=>__qa.norm(b.textContent)):[];
const exact=ftTxt.replace(/Export by date/,'').trim();
return __mk(!f.classList.contains('collapsed') && x && __qa.norm(x.textContent)==='–' && lis.length===4 && ftTxt.includes('Max 20 on screen · full history in backend') && ftBtn.includes('Export by date'),
  `collapsedRemoved=${!f.classList.contains('collapsed')} .x="${x?__qa.norm(x.textContent):null}" liCount=${lis.length} footerText="${ftTxt}" footerButtons=${JSON.stringify(ftBtn)}`);
"""

JS["QA-LG-03"] = r"""
const res={};
for(const id of ['s1b','s2','s3','s4','s5','s6','s6b']){
  __qa.tab(window.__tabs[id]);
  const f=document.querySelector('#scanfloat');
  res[id]= f ? __qa.vis(f) : 'absent-from-DOM';
}
const anyVisible=Object.values(res).some(v=>v===true);
return __mk(!anyVisible, `#scanfloat visible per state (getClientRects) = ${JSON.stringify(res)}; it lives inside #s1 so it hides with the state (documents demo limitation L-3)`);
"""

JS["QA-GL-01"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const ts=[...document.querySelectorAll('#s1 .toast')];
const hit=ts.find(t=>__qa.norm(t.textContent).includes('✓ Inbound complete — 100040311'));
const sub=hit?hit.querySelector('small'):null;
const e=sub?__qa.ex(__qa.t(sub),'No refresh · ready for the next scan'):{coll:false,actual:'no <small>',byte:false};
return __mk(!!hit && e.coll, `toasts=${JSON.stringify(ts.map(t=>__qa.norm(t.textContent).slice(0,100)))} sub="${e.actual}"`,{byte:e.byte});
"""

JS["QA-GL-11"] = r"""
const res={};
for(const id of ['s1','s1b','s2','s3','s4','s5']){
  __qa.tab(window.__tabs[id]);
  res[id]={bodyScrollWidth:document.body.scrollWidth, clientWidth:document.documentElement.clientWidth,
           ok: document.body.scrollWidth<=document.documentElement.clientWidth};
}
return __mk(Object.values(res).every(r=>r.ok), JSON.stringify(res));
"""

JS["QA-GL-13"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const nav=document.querySelector('nav,header.nav,.nav')||document.body;
const t=__qa.norm(nav.textContent);
const need=['SkinSeoul','Operation AI ▾','Catalog Management ▾','OMS Center ▾','Site Management ▾','💬 Comments','Yongwon Ryu','Logout'];
const miss=need.filter(n=>!t.includes(n));
const h2=__qa.ex(__qa.t(document.querySelector('#s1 h2')),'WMS - View Orders');
const subs=[...document.querySelectorAll('#s1 .sub')].map(s=>__qa.norm(s.textContent));
return __mk(miss.length===0 && h2.coll && subs.includes('Search Orders') && subs.includes('Search Results'),
  `navMissing=${JSON.stringify(miss)} h2="${h2.actual}" subs=${JSON.stringify(subs)}`,{byte:h2.byte});
"""

JS["QA-GL-14"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const c=document.querySelector('#s1 .ordercard');
const t=__qa.norm(c.textContent);
const oid=t.includes('Order ID: 413865');
const pill=c.querySelector('.status.st-processing');
const tq=t.includes('Total Quantity: 5');
__qa.tab(window.__tabs.s6); const c6=document.querySelector('#s6 .ordercard');
__qa.tab(window.__tabs.s6b); const c6b=document.querySelector('#s6b .ordercard');
return __mk(oid && pill && __qa.norm(pill.textContent)==='Processing' && tq && c6===null && c6b===null,
  `orderIdFound=${oid} pill="${pill?__qa.norm(pill.textContent):null}" totalQty=${tq} s6.ordercard=${c6===null?'null':'PRESENT'} s6b.ordercard=${c6b===null?'null':'PRESENT'}`);
"""

JS["QA-NG-08"] = r"""
const files=document.querySelectorAll('input[type=file]').length;
const seg=document.querySelector('.seg');
const bad=[];
for(const [id,lbl] of Object.entries(window.__tabs)){
  __qa.tab(lbl);
  if(document.body.innerText.includes('Deleo')) bad.push(id+':Deleo');
  for(const b of document.querySelectorAll('button')){
    const t=__qa.norm(b.textContent);
    if(t==='Hold Shipment'||t==='Release Hold') bad.push(id+':'+t);
  }
}
return __mk(files===0 && seg===null && bad.length===0, `input[type=file]=${files} .seg=${seg===null?'null':'PRESENT'} violations=${JSON.stringify(bad)}`);
"""

JS["QA-NG-09"] = r"""
const hrefs=[...document.querySelectorAll('[href]')].map(a=>a.getAttribute('href'));
const bad=hrefs.filter(h=>h && (h.includes('inbound-receiving')||h.includes('procurement-hub')));
return __mk(bad.length===0, `allHrefs=${JSON.stringify(hrefs)} offending=${JSON.stringify(bad)}`);
"""

JS["QA-NG-10"] = r"""
const navAnchors=[...document.querySelectorAll('a[href]')]
  .map(a=>a.getAttribute('href'))
  .filter(h=>h && !h.startsWith('#') && !h.startsWith('javascript:'));
const inlineOnclick=[...document.querySelectorAll('[onclick]')].map(e=>e.getAttribute('onclick'));
const navOnclick=inlineOnclick.filter(s=>/location|window\.open|submit\(/.test(s));
return __mk(navAnchors.length===0 && navOnclick.length===0,
  `document-navigating anchors=${JSON.stringify(navAnchors)} navigating onclick=${JSON.stringify(navOnclick)}`);
"""

JS["QA-CV-02"] = r"""
const res={};
for(const id of ['s1','s1b','s2','s3','s5','s4']){
  __qa.tab(window.__tabs[id]);
  const c=document.querySelector('#'+id+' .ordercard');
  res[id]= c ? __qa.allBtnTexts(c).includes('🖨 Print') : 'no ordercard';
}
return __mk(['s1','s1b','s2','s3','s5'].every(k=>res[k]===true) && res.s4===false, JSON.stringify(res));
"""

JS["QA-CV-05"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const head=document.querySelector('#s1 table.tbl thead input[type=checkbox]');
const rows=[...document.querySelectorAll('#s1 table.tbl tbody tr')];
const cbs=rows.map(r=>{const c=r.querySelector('input[type=checkbox]');return {has:!!c,checked:c?c.checked:null,hit:r.classList.contains('row-hit')};});
const hitChecked=cbs.filter(c=>c.hit).every(c=>c.checked===true);
__qa.tab(window.__tabs.s4);
const h4=document.querySelector('#s4 table.tbl thead input[type=checkbox]');
const r4=[...document.querySelectorAll('#s4 table.tbl tbody tr input[type=checkbox]')].map(c=>c.checked);
return __mk(!!head && cbs.every(c=>c.has) && hitChecked && h4 && h4.checked && r4.length===3 && r4.every(Boolean),
  `s1 headerCheckbox=${!!head} s1 rows=${JSON.stringify(cbs)} s4 headerChecked=${h4?h4.checked:null} s4 rowChecked=${JSON.stringify(r4)}`);
"""

JS["QA-CV-06"] = r"""
const out={};
for(const id of ['s1','s5']){
  __qa.tab(window.__tabs[id]);
  const c=[...document.querySelectorAll('#'+id+' *')].map(e=>__qa.norm(e.textContent)).find(t=>/^Found \d+ item\(s\) in this order · Found \d+ order\(s\)$/.test(t));
  out[id]={counter:c, rows:document.querySelectorAll('#'+id+' table.tbl tbody tr').length};
}
return __mk(out.s1.counter==='Found 4 item(s) in this order · Found 1 order(s)' && out.s1.rows===4 &&
            out.s5.counter==='Found 2 item(s) in this order · Found 1 order(s)' && out.s5.rows===2, JSON.stringify(out));
"""

JS["QA-CV-07"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const t=__qa.norm(document.querySelector('#s1').textContent);
const need=['single-item orders auto-print the label the moment the barcode is scanned',
'Existing Inventory stock does not count as inbound history',
'Confirming a match writes the tracking number directly onto that order’s product line',
'Scanning the tracking number of an Inbound Request (I) switches to the dedicated Internal Inbound screen'];
const need2=need.map(s=>s.replace(/’/g,"'"));
const miss=need.filter((s,i)=>!t.includes(s)&&!t.includes(need2[i]));
return __mk(miss.length===0, `missingVerbatimRules=${JSON.stringify(miss)}`);
"""

JS["QA-CV-08"] = r"""
__qa.tab('5 · Hold Order');
const want='The Hold itself is applied via the "Hold Shipment" button in OMS/Order detail or Order Management (CS team). View Orders only displays the resulting status and blocks outbound.';
const els=[...document.querySelectorAll('#s5 *')].map(e=>__qa.norm(e.textContent));
const hit=els.includes(want)||els.includes(want.replace(/"/g,'“').replace('“Hold Shipment”','“Hold Shipment”'));
const near=els.filter(t=>t.startsWith('The Hold itself')).sort((a,b)=>a.length-b.length)[0];
return __mk(hit, `exactParagraphFound=${hit} nearest="${(near||'').slice(0,300)}"`);
"""

JS["QA-CV-09"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const t=__qa.norm(document.querySelector('#s6').textContent);
const need=['Received Date recorded automatically','automatic Carrier recording is not supported, confirmed 2026-08-03','Inbound Request List status auto-switches REQUESTED / PARTIAL → INBOUNDED','this screen has no Outbound'];
const miss=need.filter(s=>!t.includes(s));
return __mk(miss.length===0, `missing=${JSON.stringify(miss)}`);
"""

JS["QA-CV-10"] = r"""
__qa.tab('6 · Internal Inbound (Inbound Request)');
const t=__qa.norm(document.querySelector('#s6').textContent);
const want='may have multiple tracking numbers registered (split shipments) — every registered number matches and enters this screen (2026-08-03)';
return __mk(t.includes(want), `found=${t.includes(want)} | s6 legend excerpt="${(t.match(/.{0,60}multiple tracking numbers.{0,140}/)||[''])[0]}"`);
"""

JS["QA-CV-12"] = r"""
__qa.tab('3 · Outbound Complete');
const b=[...document.querySelectorAll('#s3 button')].find(x=>__qa.norm(__qa.clean(x))==='🖨 Print Return Labels (2)');
const rows=[...document.querySelectorAll('#s3 table.tbl tbody tr')];
const lit=rows.map(r=>[...r.querySelectorAll('button')].map(x=>({t:__qa.norm(x.textContent),g:x.classList.contains('btn-gray')}))).flat();
const cln=rows.map(r=>[...r.querySelectorAll('button')].map(x=>({t:__qa.norm(__qa.clean(x)),g:x.classList.contains('btn-gray')}))).flat();
return __mk2(!!b&&lit.length>0&&lit.every(x=>x.t==='Cancel Inbound'&&x.g), !!b&&cln.length>0&&cln.every(x=>x.t==='Cancel Inbound'&&x.g),
  `printReturnLabels=${!!b} rowButtons literal=${JSON.stringify(lit)} dotStripped=${JSON.stringify(cln)}`);
"""

JS["QA-CV-18"] = r"""
document.querySelector('#inexpToggle').click();
const bad=[];
for(const id of ['s0','s1','s1b','s2','s3','s4','s5']){
  if(id!=='s0') __qa.tab(window.__tabs[id]);
  for(const e of document.querySelectorAll('#'+id+' .tag-smartbuy, #'+id+' .tag-jit, #'+id+' .tag-wholesale, #'+id+' .tag-partnership')){
    const cs=getComputedStyle(e);
    if(cs.backgroundColor!=='rgba(0, 0, 0, 0)') bad.push(id+' bg='+cs.backgroundColor);
    if(cs.textTransform!=='uppercase' && __qa.norm(e.textContent)!==__qa.norm(e.textContent).toUpperCase()) bad.push(id+' notUppercase="'+__qa.norm(e.textContent)+'"');
    if(parseInt(cs.fontWeight,10)<600) bad.push(id+' fontWeight='+cs.fontWeight);
  }
}
return __mk(bad.length===0, `violations=${JSON.stringify(bad.slice(0,12))}`);
"""

JS["QA-CV-20"] = r"""
const b=document.querySelector('#annoToggle');
b.click();
const on=document.body.classList.contains('no-anno');
const dots=[...document.querySelectorAll('.dot')];
const legs=[...document.querySelectorAll('.legend')];
const dotsHidden=dots.every(d=>getComputedStyle(d).display==='none'||d.offsetParent===null);
const legHidden=legs.every(l=>getComputedStyle(l).display==='none'||l.offsetParent===null);
const t1=__qa.norm(b.textContent);
b.click();
const off=document.body.classList.contains('no-anno');
const t2=__qa.norm(b.textContent);
return __mk(on && dotsHidden && legHidden && t1==='Show annotations' && !off && t2==='Hide annotations',
  `no-annoAdded=${on} dotsHidden=${dotsHidden} legendsHidden=${legHidden} textAfter="${t1}" restored=${!off} textRestored="${t2}"`);
"""

JS["QA-CV-11"] = r"""
__qa.tab('4 · Customer Return Mode');
const inp=document.querySelector('#s4 .search-input input');
const leg=document.querySelector('#s4 .legend');
const items=leg?[...leg.children].map(e=>__qa.norm(e.textContent).slice(0,120)):null;
return {v:'AMBIGUOUS', ev:`searchValue="${inp?inp.value:null}" (checkable) BUT legend entries 4/5 are asserted only as "states the qty-without-location confirm block" / "states that the unified search auto-detects return barcodes" with no quoted string and no selector for indexing legend entries. legendChildren=${JSON.stringify(items?items.slice(0,7):null)}`};
"""

JS["QA-GL-02"] = r"""
return {v:'AMBIGUOUS', ev:'Scenario says "assert the binding rule only" for the send-sound handler. No DOM-observable assertion is given (no attribute, no class, no marker); event listeners added via addEventListener are not enumerable from page script. Spec provides no instruction for how to observe the binding.'};
"""

JS["QA-S6-03b"] = ""  # placeholder removed


JS["QA-S0-03"] = r"""
const seg=document.querySelector('#s0 .seg');
const hits=[...document.querySelectorAll('#s0 *')].filter(e=>e.children.length===0 && __qa.norm(e.textContent).includes('Matched field')).map(e=>__qa.norm(e.textContent));
return __mk(seg===null && hits.length===0, `#s0 .seg=${seg===null?'null':'PRESENT'} elementsContaining"Matched field"=${JSON.stringify(hits)}`);
"""


JS["QA-SC-06"] = r"""
__qa.tab('1 · Scan Result (Last Item Remaining)');
const el=document.querySelector('#s1 .search-input input');
return __mk(el && el.value==='10323775316153', `#s1 .search-input input value="${el?el.value:null}" expected="10323775316153"`);
"""


DIALOGS = []

PY_SCENARIOS = []


def scen_S3_02(page):
    """QA-S3-02: alert with exact text on Cancel Outbound click."""
    msgs = DIALOGS
    msgs.clear()
    page.evaluate("() => __qa.tab('3 · Outbound Complete')")
    info = page.evaluate("""() => {
      const all=[...document.querySelectorAll('#s3 .ordercard button')];
      const bLit=all.find(x=>x.classList.contains('btn-red-line') && __qa.norm(x.textContent)==='Cancel Outbound');
      const bCln=all.find(x=>x.classList.contains('btn-red-line') && __qa.norm(__qa.clean(x))==='Cancel Outbound');
      return {found: !!bCln, literalMatch: !!bLit, texts: __qa.allBtnTexts('#s3 .ordercard'), cleaned: __qa.cbtnTexts('#s3 .ordercard')};
    }""")
    if not info["found"]:
        return {"v": "FAIL", "ev": f"no button.btn-red-line with text 'Cancel Outbound' on #s3 ordercard; buttons={info['texts']}"}
    page.evaluate("""() => [...document.querySelectorAll('#s3 .ordercard button.btn-red-line')].find(x=>__qa.norm(__qa.clean(x))==='Cancel Outbound').click()""")
    page.wait_for_timeout(200)
    want = "Status rollback: prepare shipment → processing"
    ok = len(msgs) == 1 and msgs[0] == want and info["literalMatch"]
    cleaned_ok = len(msgs) == 1 and msgs[0] == want
    return {"v": "PASS" if ok else "FAIL", "dotOnly": (not ok and cleaned_ok),
            "ev": f"button literal-text match={info['literalMatch']} (literal buttons={info['texts']}, dot-stripped={info['cleaned']}); dialogs={msgs!r} expected={want!r}"}


def scen_S1_17(page):
    """QA-S1-17: shelf micro-save chip + ~1s auto-hide, no reload."""
    page.evaluate("() => __qa.tab('1 · Scan Result (Last Item Remaining)')")
    page.evaluate("() => { window.__navCount = (window.__navCount||0); }")
    setup = page.evaluate("""() => {
      const inp=document.querySelector('#s1 .shelf input');
      if(!inp) return {err:'#s1 .shelf input null'};
      const before=inp.value;
      inp.value='9'; __qa.fire(inp,'input');
      const b=[...document.querySelectorAll('#s1 button.flsave')].filter(x=>x.offsetParent!==null);
      return {before, visible:b.length, text: b[0]?__qa.norm(b[0].textContent):null};
    }""")
    if setup.get("err"):
        return {"v": "FAIL", "ev": setup["err"]}
    page.evaluate("""() => { const inp=document.querySelector('#s1 .shelf input'); inp.focus();
      inp.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
      inp.dispatchEvent(new KeyboardEvent('keyup',{key:'Enter',bubbles:true})); }""")
    page.wait_for_timeout(120)
    after = page.evaluate("""() => {
      const b=[...document.querySelectorAll('#s1 button.flsave')];
      const v=b.filter(x=>x.offsetParent!==null);
      return {text: v[0]?__qa.norm(v[0].textContent):(b[0]?__qa.norm(b[0].textContent):null), cls: (v[0]||b[0])?(v[0]||b[0]).className:null, visible: v.length};
    }""")
    page.wait_for_timeout(1100)
    gone = page.evaluate("""() => [...document.querySelectorAll('#s1 button.flsave')].filter(x=>x.offsetParent!==null).length""")
    reloaded = page.evaluate("() => performance.getEntriesByType('navigation').length")
    ok = (setup["visible"] > 0 and setup["text"] == "Save"
          and after["text"] == "✓ Saved" and "ok" in (after["cls"] or "")
          and gone == 0)
    return {"v": "PASS" if ok else "FAIL",
            "ev": f"afterInput visible={setup['visible']} text={setup['text']!r}; afterEnter text={after['text']!r} class={after['cls']!r}; visibleAfter~1.1s={gone}; navigationEntries={reloaded}"}


def scen_M2_04(page):
    """QA-M2-04: match -> modal closes, #unrecToast with exact text, hides ~4s."""
    page.evaluate("() => __qa.tab('Modal: Unrecognized Barcode')")
    page.evaluate("() => document.querySelector('#unrecSearch').click()")
    probe = page.evaluate("""() => {
      const r=document.querySelector('#unrecFound tbody tr');
      const b=r?r.querySelector('.trkmatch'):null;
      return {hasRow:!!r, hasBtn:!!b, btnText: b?__qa.norm(b.textContent):null};
    }""")
    if not probe["hasBtn"]:
        return {"v": "FAIL", "ev": f"no .trkmatch in first #unrecFound row; probe={probe}"}
    page.evaluate("() => document.querySelector('#unrecFound tbody tr .trkmatch').click()")
    page.wait_for_timeout(150)
    st = page.evaluate("""() => {
      const m=document.querySelector('#m-unrec'), t=document.querySelector('#unrecToast');
      const vis = t ? (getComputedStyle(t).display!=='none' && __qa.vis(t)) : false;
      const sub = t?t.querySelector('small'):null;
      return {open:m.classList.contains('open'), toastVisible:vis, toastText:t?__qa.norm(t.textContent):null, sub: sub?__qa.norm(sub.textContent):null};
    }""")
    ok_now = (not st["open"] and st["toastVisible"]
              and "✓ Tracking No 10323100835644 matched and registered" in (st["toastText"] or "")
              and "Order 414230" in (st["sub"] or st["toastText"] or "")
              and "rescanning the same barcode is now recognized" in (st["sub"] or st["toastText"] or ""))
    page.wait_for_timeout(4300)
    later = page.evaluate("""() => { const t=document.querySelector('#unrecToast'); return t?(getComputedStyle(t).display!=='none' && __qa.vis(t)):false; }""")
    ok = ok_now and later is False
    return {"v": "PASS" if ok else "FAIL",
            "ev": f"btnText={probe['btnText']!r} modalOpenAfter={st['open']} toastVisible={st['toastVisible']} toastText={st['toastText']!r} sub={st['sub']!r} visibleAfter4.3s={later}"}


def scen_M2_12(page):
    """QA-M2-12: #gtoast exact text, m-unrec2 closes, hides ~2.6s, no reload."""
    page.evaluate("() => __qa.tab('Modal: Send to Missing Tracking List')")
    exists = page.evaluate("() => !!document.querySelector('#unrec2Send')")
    if not exists:
        return {"v": "FAIL", "ev": "#unrec2Send not found"}
    page.evaluate("() => document.querySelector('#unrec2Send').click()")
    page.wait_for_timeout(150)
    st = page.evaluate("""() => {
      const g=document.querySelector('#gtoast'), m=document.querySelector('#m-unrec2');
      const vis=g?(getComputedStyle(g).display!=='none'&&__qa.vis(g)):false;
      const sub=g?g.querySelector('small'):null;
      return {vis, txt:g?__qa.norm(g.textContent):null, sub:sub?__qa.norm(sub.textContent):null, open:m.classList.contains('open')};
    }""")
    ok_now = (st["vis"] and "✓ Sent to Missing Tracking List" in (st["txt"] or "")
              and (st["sub"] or "") == "PIC notified via #unrecognized-tracking · No refresh"
              and not st["open"])
    page.wait_for_timeout(2800)
    later = page.evaluate("""() => { const g=document.querySelector('#gtoast'); return g?(getComputedStyle(g).display!=='none'&&__qa.vis(g)):false; }""")
    nav = page.evaluate("() => performance.getEntriesByType('navigation').length")
    ok = ok_now and later is False
    return {"v": "PASS" if ok else "FAIL",
            "ev": f"gtoastVisible={st['vis']} text={st['txt']!r} sub={st['sub']!r} m-unrec2.open={st['open']} visibleAfter2.8s={later} navigationEntries={nav}"}


PY = {
    "QA-S3-02": scen_S3_02,
    "QA-S1-17": scen_S1_17,
    "QA-M2-04": scen_M2_04,
    "QA-M2-12": scen_M2_12,
}

ORDER = [
    "QA-S0-01", "QA-S0-03", "QA-S0-04", "QA-S0-05", "QA-S0-06", "QA-S0-07", "QA-S0-08", "QA-S0-09", "QA-S0-10", "QA-S0-11",
    "QA-SC-06", "QA-SC-07", "QA-SC-08", "QA-SC-17",
    "QA-S1-01", "QA-S1-03", "QA-S1-04", "QA-S1-05", "QA-S1-06", "QA-S1-07", "QA-S1-08", "QA-S1-09", "QA-S1-10",
    "QA-S1-11", "QA-S1-12", "QA-S1-13", "QA-S1-14", "QA-S1-15", "QA-S1-16", "QA-S1-17", "QA-S1-18", "QA-S1-19", "QA-S1-20",
    "QA-S2-01", "QA-S2-02", "QA-S2-03", "QA-S2-04",
    "QA-S3-01", "QA-S3-02", "QA-S3-03", "QA-S3-04", "QA-S3-05",
    "QA-S4-01", "QA-S4-02", "QA-S4-03", "QA-S4-04", "QA-S4-05", "QA-S4-06", "QA-S4-07", "QA-S4-08", "QA-S4-09", "QA-S4-10",
    "QA-S5-01", "QA-S5-02", "QA-S5-03", "QA-S5-04", "QA-S5-05", "QA-S5-06",
    "QA-S6-01", "QA-S6-02", "QA-S6-03", "QA-S6-04", "QA-S6-05", "QA-S6-06", "QA-S6-07", "QA-S6-08", "QA-S6-09",
    "QA-S6-10", "QA-S6-11", "QA-S6-12", "QA-S6-13", "QA-S6-14", "QA-S6-15", "QA-S6-16", "QA-S6-17", "QA-S6-18",
    "QA-S6-19", "QA-S6-20", "QA-S6-21",
    "QA-M1-01", "QA-M1-02", "QA-M1-03", "QA-M1-04",
    "QA-M2-01", "QA-M2-02", "QA-M2-03", "QA-M2-04", "QA-M2-05", "QA-M2-06", "QA-M2-07", "QA-M2-08", "QA-M2-09",
    "QA-M2-10", "QA-M2-11", "QA-M2-12",
    "QA-M4-01", "QA-M4-02", "QA-M4-03", "QA-M4-04", "QA-M4-05", "QA-M4-06", "QA-M4-07",
    "QA-C-01", "QA-C-02", "QA-C-03", "QA-C-04", "QA-C-05", "QA-C-06", "QA-C-07", "QA-C-08", "QA-C-09", "QA-C-10", "QA-C-11",
    "QA-LG-01", "QA-LG-02", "QA-LG-03",
    "QA-GL-01", "QA-GL-02", "QA-GL-11", "QA-GL-13", "QA-GL-14",
    "QA-NG-08", "QA-NG-09", "QA-NG-10",
    "QA-CV-02", "QA-CV-05", "QA-CV-06", "QA-CV-07", "QA-CV-08", "QA-CV-09", "QA-CV-10", "QA-CV-11", "QA-CV-12",
    "QA-CV-18", "QA-CV-20",
]

TABS_JS = "window.__tabs=" + json.dumps(STATE_TABS, ensure_ascii=False) + ";"


def main():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        ctx.add_init_script(PRELUDE + TABS_JS)
        page = ctx.new_page()
        page.on("dialog", lambda d: (DIALOGS.append(d.message), d.dismiss()))
        for sid in ORDER:
            page.goto(URL)
            page.wait_for_timeout(60)
            try:
                if sid in PY:
                    r = PY[sid](page)
                else:
                    body = JS[sid]
                    r = page.evaluate("() => { " + body + " }")
            except Exception as e:  # noqa: BLE001
                r = {"v": "ERROR", "ev": f"{type(e).__name__}: {e}"}
            r["id"] = sid
            results.append(r)
            print(f"{r['v']:<10} {sid}  {str(r.get('ev'))[:220]}")
        browser.close()

    counts = {}
    for r in results:
        counts[r["v"]] = counts.get(r["v"], 0) + 1
    print("\n== SUMMARY ==")
    print(counts)
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        with open(out, "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)
        print("wrote", out)


if __name__ == "__main__":
    main()
