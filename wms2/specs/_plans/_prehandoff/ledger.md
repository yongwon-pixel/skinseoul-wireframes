# Pre-handoff Review — Findings Ledger

> 상태: OPEN(미검증) → VERIFIED(반증 통과) / REFUTED(기각) → FIXED / OWNER-Q(승인 대기) / WONTFIX
> 등급: BLOCKER / MAJOR / MINOR · 증거 없는 등재 금지

| ID | 등급 | 출처 | 발견 | 증거 | 상태 |
|---|---|---|---|---|---|
| F-1 | MINOR | R1 기계 | view-orders 고유 QA ID 277개 vs census 자기보고 279 — v1.3에서 +2(QA-M1-06/07) 반영 시 실카운트가 안 맞거나 추출 누락 | r1-machine-findings.md §3 | OPEN |
| F-2 | MAJOR | R1 기계 | 허브 정본 문구 `No matching comments`·`🔍 Search all comments — order no. · author · text`가 8페이지 중 5페이지에서만 그렙됨 — 통일 배치(a518f5a) 잔결 or 표기 변형 의심 | r1-machine-findings.md §4 | OPEN |
| F-3 | NOTE | R1 기계 | R1 §4의 허브 추출에 산문 백틱 오염 다수(`[WF-15] closing` 등) — 코퍼스 결함 아님, 추출기 한계. R4에서 정본 7종을 G-7 원문 기준으로 재추출해 재검 | r1-machine-findings.md §4 | OPEN |
