# Pre-handoff Review — Findings Ledger

> 상태: OPEN(미검증) → VERIFIED(반증 통과) / REFUTED(기각) → FIXED / OWNER-Q(승인 대기) / WONTFIX
> 등급: BLOCKER / MAJOR / MINOR · 증거 없는 등재 금지

| ID | 등급 | 출처 | 발견 | 증거 | 상태 |
|---|---|---|---|---|---|
| F-1 | **MAJOR** | R1 기계 | **[근본원인 확정] view-orders QA ID 충돌** — v1.3이 추가한 QA-M1-06[WF]/07[ADMIN](L1620·1623)이 기존 QA-M1-06[ADMIN·E-26]/07[ADMIN·E-27](L1629·1632)과 **동일 ID 중복**. census 279는 헤더 수로는 정확, 고유 ID가 277이 된 원인. 수리=신규 2건을 QA-M1-08/09로 개명(+census 델타 노트·노션 미러·러너 동기화). ID 불변 규칙상 기존 06/07은 유지 | grep L1620/1623/1629/1632 (헤더 4개 실측) | VERIFIED |
| F-2 | ~~MAJOR~~ | R1 기계 | **기각 — 문서화된 정상 상태.** G-7 정본표 자체가 HUB-5~7 corpus를 '4/5 (CL·TM·IR ship no search pane)'로 명기, closing.md §3.8은 HUB-6/7을 'not built (U-c)'로, tracking-missing.md §3.6은 'builds no search pane, HUB-5/6/7 do not apply'로 선언. 실제 admin에는 G-7 본문이 전 화면 검색을 요구(ADMIN 티어) — 와이어프레임 3종 미구축은 선언된 데모 한계 | _global-rules.md L60-63 · closing.md L413-416 · tracking-missing.md L367 | REFUTED |
| F-3 | NOTE | R1 기계 | 추출기 한계 확인 — F-2 검증 과정에서 정본 7종을 G-7 원문 기준으로 재검 완료(HUB-1~4=8/8, HUB-5~7=5/5 검색 보유 페이지) | F-2 검증 그렙 | CLOSED |
| F-4 | MAJOR | QA재실행 | **OM 결함-문서화 시나리오 8건이 수리 전 상태를 어서션** (QA-IMP-35·SMP-19/30/31/33·CMT-20·GBL-09/10) — a518f5a가 WF-15~21을 화면에 적용했으나 스펙 §2.4/§8.0 rule 4·7과 이 8건은 '[WF-n · proposed]' 기준 그대로. 실측은 전부 스펙 §3 제품 요건과 일치(colspan 7·확인창·토스트 스택·Esc 등) | wf_b72a128f 저널 order-management (2런 안정) | OPEN |
| F-5 | MAJOR | QA재실행 | **VO QA-S6-07 "유일 예상-실패" 선언 스테일** — WF-1(캐리어 배너)이 이미 수리돼 PASS함. §2.4 WF-1 행·§8.0 'expected to FAIL today' 조항·배너 문구 북키핑('· Carrier is not recorded' 추가형) 정비 필요 | wf_b72a128f 저널 view-orders NOTE 1 | OPEN |
| F-6 | MINOR | QA재실행 | TM QA-EMPTY-01의 >300px 절이 inner .mockwrap 앵커로는 **원천 불충족**(기준선 inner=260px, outer=520px가 .mock min-height로 유지) — outer로 재앵커 필요 | wf_b72a128f 저널 tracking-missing | OPEN |
| F-7 | MINOR | QA재실행 | OD §8.1 표의 [WF]=68 잔존 — v1.3 델타(69)로 갱신 안 된 표 1곳 | wf_b72a128f 저널 order-detail | OPEN |
| F-8 | MINOR | QA재실행 | INV QA-GLB-08 clause 3 자기모순(activeElement 어서션 vs 자체 정의문) — 정의문 기준으로 재서술 | wf_b72a128f 저널 stock-status | OPEN |
| F-9 | NOTE | QA재실행 | **[WF] 전량 재실행 654건: 645 PASS · 9 FAIL(전건 spec-stale) · 와이어프레임 결함 0** · 러너 8종=_verify/prehandoff/ · 전 에이전트가 기준선 byte-identical 사전 검증 | wf_b72a128f 완주(2.1M tok, 21분) | VERIFIED |
