# Pre-handoff Review — Findings Ledger

> 상태: OPEN(미검증) → VERIFIED(반증 통과) / REFUTED(기각) → FIXED / OWNER-Q(승인 대기) / WONTFIX
> 등급: BLOCKER / MAJOR / MINOR · 증거 없는 등재 금지

| ID | 등급 | 출처 | 발견 | 증거 | 상태 |
|---|---|---|---|---|---|
| F-1 | MINOR | R1 기계 | view-orders 고유 QA ID 277개 vs census 자기보고 279 — v1.3에서 +2(QA-M1-06/07) 반영 시 실카운트가 안 맞거나 추출 누락 | r1-machine-findings.md §3 | OPEN |
| F-2 | MAJOR | R1 기계 | 허브 정본 문구 `No matching comments`·`🔍 Search all comments — order no. · author · text`가 8페이지 중 5페이지에서만 그렙됨 — 통일 배치(a518f5a) 잔결 or 표기 변형 의심 | r1-machine-findings.md §4 | OPEN |
| F-3 | NOTE | R1 기계 | R1 §4의 허브 추출에 산문 백틱 오염 다수(`[WF-15] closing` 등) — 코퍼스 결함 아님, 추출기 한계. R4에서 정본 7종을 G-7 원문 기준으로 재추출해 재검 | r1-machine-findings.md §4 | OPEN |
| F-4 | MAJOR | QA재실행 | **OM 결함-문서화 시나리오 8건이 수리 전 상태를 어서션** (QA-IMP-35·SMP-19/30/31/33·CMT-20·GBL-09/10) — a518f5a가 WF-15~21을 화면에 적용했으나 스펙 §2.4/§8.0 rule 4·7과 이 8건은 '[WF-n · proposed]' 기준 그대로. 실측은 전부 스펙 §3 제품 요건과 일치(colspan 7·확인창·토스트 스택·Esc 등) | wf_b72a128f 저널 order-management (2런 안정) | OPEN |
| F-5 | MAJOR | QA재실행 | **VO QA-S6-07 "유일 예상-실패" 선언 스테일** — WF-1(캐리어 배너)이 이미 수리돼 PASS함. §2.4 WF-1 행·§8.0 'expected to FAIL today' 조항·배너 문구 북키핑('· Carrier is not recorded' 추가형) 정비 필요 | wf_b72a128f 저널 view-orders NOTE 1 | OPEN |
| F-6 | MINOR | QA재실행 | TM QA-EMPTY-01의 >300px 절이 inner .mockwrap 앵커로는 **원천 불충족**(기준선 inner=260px, outer=520px가 .mock min-height로 유지) — outer로 재앵커 필요 | wf_b72a128f 저널 tracking-missing | OPEN |
| F-7 | MINOR | QA재실행 | OD §8.1 표의 [WF]=68 잔존 — v1.3 델타(69)로 갱신 안 된 표 1곳 | wf_b72a128f 저널 order-detail | OPEN |
| F-8 | MINOR | QA재실행 | INV QA-GLB-08 clause 3 자기모순(activeElement 어서션 vs 자체 정의문) — 정의문 기준으로 재서술 | wf_b72a128f 저널 stock-status | OPEN |
| F-9 | NOTE | QA재실행 | **[WF] 전량 재실행 654건: 645 PASS · 9 FAIL(전건 spec-stale) · 와이어프레임 결함 0** · 러너 8종=_verify/prehandoff/ · 전 에이전트가 기준선 byte-identical 사전 검증 | wf_b72a128f 완주(2.1M tok, 21분) | VERIFIED |
