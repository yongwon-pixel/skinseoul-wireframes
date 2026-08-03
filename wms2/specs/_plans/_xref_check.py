#!/usr/bin/env python3
"""상호참조 무결성: review가 인용한 PD/WF ID가 레지스터에 실제로 존재하는가.
주의(2026-08-03 교훈): 감독의 '기대 의미'를 하드코딩하지 말 것 — 그 방식이 오진을 낳았다.
검사는 문서에서 추출한 것만 대상으로 한다."""
import io, re, sys, os
D = os.path.dirname(os.path.abspath(__file__))
L = lambda n: io.open(os.path.join(D, n), encoding='utf-8').read()
review, pdreg, wfreg = L('_review.md'), L('_provisional-decisions.md'), L('_wireframe-fixes.md')
# 정정 노트(회고 서술)는 인용이 아니므로 제외
body = review.split('## Cross-reference note')[0]
cited_pd = set(re.findall(r'PD-\d+', body)); cited_wf = set(re.findall(r'WF-\d+', body))
have_pd = set(re.findall(r'\[(PD-\d+)\]', pdreg)); have_wf = set(re.findall(r'\[(WF-\d+)\]', wfreg))
key = lambda x: int(x.split('-')[1])
fails = []
miss_pd = sorted(cited_pd - have_pd, key=key); miss_wf = sorted(cited_wf - have_wf, key=key)
if miss_pd: fails.append(f'review 인용인데 레지스터에 없는 PD: {miss_pd}')
if miss_wf: fails.append(f'review 인용인데 없는 WF: {miss_wf}')
for name, reg in [('PD', pdreg), ('WF', wfreg)]:
    ids = re.findall(r'^\W*\*\*\[(' + name + r'-\d+)\]', reg, re.M)
    dup = sorted({i for i in ids if ids.count(i) > 1}, key=key)
    if dup: fails.append(f'{name} 중복 헤딩: {dup}')
print(f'PD entries {len(have_pd)} · WF entries {len(have_wf)} · review cites PD {len(cited_pd)} / WF {len(cited_wf)}')
for f in fails: print('FAIL', f)
print('XREF OK' if not fails else f'XREF FAILED: {len(fails)}')
sys.exit(1 if fails else 0)
