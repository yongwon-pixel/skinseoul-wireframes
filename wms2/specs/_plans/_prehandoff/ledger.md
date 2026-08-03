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
| F-10 | **BLOCKER** | R4b 노션 | **노션 미러 표 셀 손상 — 개발자가 노션만 보면 정보를 잃는다.** RTO §5.1 이벤트 표에서 DC-1·DC-7·DC-12·DC-19 4행이 셀 내부 `\|` 이스케이프로 쪼개져 **"Surfaced in UI?" 열 값이 통째로 소실**, DC-7은 페이로드 필드(`label_id`·`source` enum·`reprint_seq`·`job_id`→DC-12 링크)까지 삭제. td 개수는 6개로 정상이라 구조 검사로는 안 잡힘 | RTO 미러 감사(에이전트 실측, notion_page.md L1139·1187·1227·1283) | VERIFIED |
| F-11 | **BLOCKER** | 기계 | **동일 손상 위험 41행 전수 식별** — IR 13 · INV 11 · TM 10 · RTO 4 · OD 2 · VO 1. RTO는 4/4 전부 실측 손상 확인됐으므로 나머지 37행도 손상 추정(개별 확인 필요). 근본 수리 = 정본에서 셀 내 `\|` 표기를 파이프 없는 형태(`∈ {a, b}` / `/`)로 교체 → 미러 재게시 | 전 스펙 grep(escaped-pipe 표 행 41개, 파일·행번호·개수 실측) | VERIFIED |
| F-12 | **MAJOR** | R4b 노션 | **표 셀 안 HTML 태그 리터럴이 노션에서 실제 태그로 오인돼 셀 분할** — OM §10 Decision Log 마지막 행에서 인라인 코드 `<th>`가 셀을 쪼개고 `</td>` 문자열이 본문에 노출, Detail/Where 열이 한 칸씩 밀림(텍스트 삭제는 없음). 동일 위험 전수 15행: TM 5 · CL 4 · OD 2 · RTO 2 · OM 1 · INV 1 (`<th>`·`<td>`·`<table>`·`<br>`·`<span>`) | OM 미러 감사 실측 + 전 스펙 grep | VERIFIED |
| F-13 | **BLOCKER** | R4b 노션 | **미러에 원본에 없는 문장이 날조됨(LLM 리페어 흔적)** — IR DC-11에 `trigger gains request_edited/request_cancelled`(레포 전문 grep 0건), IR DC-25에 `, 2026-08-03` 추가, CL §3.8에 HUB-7 괄호절과 "(The right-hand column below is the pre-fix drawing, kept for provenance.)" 통째 신설. 표 손상과 달리 **정상 산문으로 읽혀 더 위험** | IR·CL 미러 감사 실측(각 레포 grep 대조) | VERIFIED |
| F-14 | **BLOCKER** | R4b 노션 | **VO 미러에서 표 행 4개가 앞 행에 병합돼 소실** — BR-58(근거·결정일 열 전멸)·E-94(상황 열)·결정로그 v21 행·G-7 v1.2 행. 전부 2026-08-03 추가분. 추가로 DC-36 셀 절단, QA-C-18이 **G-7 발행 이전 초안 그대로**("no assertable literal until [G-7] publishes them")라 개발자가 정반대로 이해 | VO 미러 감사 실측 | VERIFIED |
| F-15 | **MAJOR** | R4b 노션 | **OD 미러가 OD-WFX-1 수리를 미반영(5곳)** — QA-STA-4가 [ADMIN]으로 남아 있고 §8.3은 "deliberately absent from the [WF] run"이라 정반대 지시. 꼬리 요약도 68/93(레포 69/92). **부수 발견: 레포 §8.1 표 자체도 68/93 잔존**(F-7과 동일 건) | OD 미러 감사 실측 | VERIFIED |
| F-16 | **MAJOR** | R4b 노션 | CL 미러 부가 손상 — §6.3 Deep links 표가 `<td>` 리터럴로 3열화·본문 깨짐, DC-7 페이로드 `+`→`•` 무단 치환, §8.16 커버리지 문장 1개 소실(코드펜스 뒤 개행 없는 레포 quirk가 원인 추정) | CL 미러 감사 실측 | VERIFIED |
| F-17 | **BLOCKER** | 종합 | **노션 미러 전체 신뢰 불가 — 부분 수리 아닌 전면 재게시 필요.** 6페이지 감사에서 전부 손상 확인(RTO 4행·OM 1·VO 6·IR 13·OD 7·CL 4). 재발 방지 선행조건: 정본에서 표 셀 내 `\|` 41행·HTML 태그 리터럴 15행 제거 + 코드펜스 개행 quirk 수정 | F-10~F-16 종합 | VERIFIED |
