#!/usr/bin/env python3
"""P3-2 산출물 상호참조 무결성 검사 — review가 인용한 PD/WF가 레지스터에 같은 의미로 존재하는가."""
import io, re, sys, os

D = os.path.dirname(os.path.abspath(__file__))
def load(n): return io.open(os.path.join(D, n), encoding='utf-8').read()

review = load('_review.md')
pdreg = load('_provisional-decisions.md')
wfreg = load('_wireframe-fixes.md')

# review가 기대하는 의미 (감독이 고정 배정한 것)
EXPECT = {
 'PD-1': ['role', 'permission'],
 'PD-2': ['sound', 'audio'],
 'PD-21': ['auto-outbound', 'auto outbound', 'auto-trigger outbound'],
 'PD-27': ['sample'],
 'PD-34': ['failure'],
 'PD-36': ['picking'],
 'PD-46': ['location'],
 'PD-5': ['remov', 'delete', 'toast'],
 'PD-68': ['csv', 'closing report'],
 'PD-80': ['other'],
}
WF_EXPECT = {
 'WF-1': ['carrier'],
 'WF-2': ['carrier'],
 'WF-5': ['panel', 'warning'],
 'WF-10': ['v1', 'css', 'leftover'],
 'WF-9': ['picking', 'sample'],
}

def entry_text(reg, key, span=600):
    m = re.search(r'\[' + re.escape(key) + r'\]', reg)
    if not m: return None
    return reg[m.start():m.start()+span].lower()

fails, warns = [], []
for key, words in EXPECT.items():
    txt = entry_text(pdreg, key)
    if txt is None:
        fails.append(f'{key}: 레지스터에 없음'); continue
    if not any(w.lower() in txt for w in words):
        fails.append(f'{key}: 의미 불일치 — 기대 {words} / 실제 "{txt[:90].strip()}"')
for key, words in WF_EXPECT.items():
    txt = entry_text(wfreg, key)
    if txt is None:
        fails.append(f'{key}: WF 레지스터에 없음'); continue
    if not any(w.lower() in txt for w in words):
        fails.append(f'{key}: 의미 불일치 — 기대 {words}')

# review가 인용한 모든 PD/WF가 레지스터에 존재하는가
cited_pd = set(re.findall(r'PD-\d+', review))
have_pd = set(re.findall(r'\[(PD-\d+)\]', pdreg))
missing = sorted(cited_pd - have_pd, key=lambda x: int(x.split('-')[1]))
if missing: fails.append(f'review 인용인데 레지스터에 없는 PD: {missing}')
cited_wf = set(re.findall(r'WF-\d+', review))
have_wf = set(re.findall(r'\[(WF-\d+)\]', wfreg))
mwf = sorted(cited_wf - have_wf, key=lambda x: int(x.split('-')[1]))
if mwf: fails.append(f'review 인용인데 없는 WF: {mwf}')

# 중복 번호
for name, reg, pat in [('PD', pdreg, r'\[(PD-\d+)\]'), ('WF', wfreg, r'\[(WF-\d+)\]')]:
    ids = re.findall(r'^\W*\*\*\[(' + name + r'-\d+)\]', reg, re.M)
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: warns.append(f'{name} 중복 헤딩: {sorted(dup)}')

print(f'PD entries: {len(have_pd)} · WF entries: {len(have_wf)} · review cites PD {len(cited_pd)} / WF {len(cited_wf)}')
for w in warns: print('WARN', w)
for f in fails: print('FAIL', f)
print('XREF OK' if not fails else f'\nXREF FAILED: {len(fails)}')
sys.exit(1 if fails else 0)
