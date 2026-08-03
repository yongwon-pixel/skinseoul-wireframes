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
| F-18 | **BLOCKER** | R4b 노션 | TM 미러: `\|` 10/10행 전부 손상 — DC-3·8·11·20·24는 **UI-visible 열 값 삭제**, DC-13은 페이로드 enum 7개 중 5개+UI열까지 소실(td 6개로 조기 종료), DC-14는 `\|`→`/` 무단 치환. §2.2 표는 `<th>` 리터럴로 전 행에 팬텀 5열 추가 | TM 미러 감사 실측 | VERIFIED |
| F-19 | **MAJOR** | R4b 노션 | **블록쿼트 안 마크다운 표가 노션에서 표로 렌더 안 됨** — TM §5.1 서두 "Shared concept" 표(4행)가 `\|`·`\|---\|` 이스케이프 그대로 노출된 산문으로 표시 | TM 미러 감사(레포 L621) | VERIFIED |
| F-20 | **BLOCKER** | 교차 | **PD-66 처리가 레포·노션 양쪽 모두 불완전 — 정본 자체의 내부 모순.** 레포 TM 배너는 "PD-66 OWNER-DECIDED"인데 본문 7곳 이상(§3.2.2·§3.7·E-3·§8.0·QA-VAL-10·§9.1·§10)이 여전히 "미결정·NO-DEFAULT·BLOCKED". 노션은 5곳을 RESOLVED로 갱신했으나 2곳(§8.0 totals·§10 결정로그)은 옛 텍스트 → 노션도 자기모순. **C-103(모순 사냥 BLOCKER 후보)과 동일 건, 독립 2회 검출** | TM 미러 감사 + 모순 사냥 C-103 | VERIFIED |
| | | | **— R2 반증 결과 (17/17, 2.93M tok) —** | | |
| F-21 | **BLOCKER** | R2 (C-23) | **취소된 입고 요청의 송장 스캔 동작이 정반대** — VO는 "등록 번호는 **항상** State 6"(BR-17·[L-S1-1] 우선순위 1·G-10 "Every registered number"), IR v1.3은 "취소 시 **매칭 비활성화** → 미인식 풀 낙하"(BR-34·E-96). VO 전문에 CANCELLED·deactivat 각 0건. 두 QA(IR QA-C-30 vs VO L1177)를 한 구현이 동시 통과 불가 | 반증 2/2 생존(양측 독립 경로) | VERIFIED |
| F-22 | **BLOCKER** | R2 (C-42) | **미인식 등록 슬랙 알림의 멘션 대상 상충** — VO 라우팅표 "none (channel post)" vs TM "의심 PIC 전원 @멘션(1인 1회)". TM의 push-not-poll 설계(검색·수동 PIC 조회 제거 근거) 전체가 이 멘션에 의존 | 반증 2/2 생존 | VERIFIED |
| F-23 | **MAJOR** | R2 (C-32) | **창고 로컬 타임존 이원화** — INV BR-32 "모든 시각 KST(Asia/Seoul)" vs OD §3.0.3 "warehouse local (**SGT**)". 양쪽 X-리스트·CP 목록·전역규칙 어디에도 미선언(전역규칙에 KST/SGT 문자열 0건). 같은 이벤트가 화면마다 1시간 어긋나 렌더 | 반증 2인 생존(등급 MAJOR/BLOCKER 분할 → 보수적 MAJOR) | VERIFIED |
| F-24 | 재판정 | R2 (C-55) | 출고/출고취소 시 재고 원장 기록 여부 — OD는 `inventory.movement` 필수, VO는 재고 이벤트 없음. **반증 1/2 분할**(BLOCKER vs MINOR) → 3차 심판 대기 | 반증 분할 | OPEN |
| F-25 | **MAJOR** | R2 (C-103)=F-20 | **[방향 정정·실측 확정] PD-66은 `tracking-missing.md` 한 문서만 미반영.** VO는 완전 반영(§3.12 Decided·E-63·QA-CV-22 un-defer·OQ-1 RESOLVED), PD 레지스터도 OWNER-DECIDED 명기. TM만 6곳 잔존(L199 'Nullability is undecided'·L403·L796 E-3 'No behavior is specified'·L932 BLOCKED 집계·L1207 QA-VAL-10 BLOCKED·L1359·L1402 §9.1 제목). **노션 TM 미러는 오히려 RESOLVED로 갱신돼 있어 레포가 stale한 쪽** — 노션 편집이 레포로 역이관 안 된 케이스 | 반증 분할 + F-20 독립 확인 | VERIFIED |
| F-26 | MAJOR | R2 | **경계면·전역규칙 MAJOR 13건 생존** (C-15·16·17·24·25·26·27·33·35·46·47·56·58) — 상세는 r2-contradiction-raw.md | 반증 개별 통과 | VERIFIED |
| F-27 | NOTE | R2 | 반증에서 **19건 기각·17건 MINOR 강등** — 선언된 divergence·이력 서술·층위 차이로 설명됨. 오탐률 36/49(73%)로 적대 검증의 실효 확인 | 반증 집계 | CLOSED |
| F-28 | **BLOCKER** | R4b 노션 | INV 미러: `\|` 11/11행 전부 손상 — BR "damaged/lost" 분류·DC-17/21/31 페이로드+Note 열·E-21의 DC-17/PD-5 상호참조·QA-NAV-08/GLB-08/GLB-11의 어서션 절이 **페이지 어디에도 없음**(0-hit 검증). DC-6 9열화로 §5.1 표 전체에 팬텀 2열 | INV 미러 감사 실측 | VERIFIED |
| F-29 | **MAJOR** | 총괄감사 | **레포 자체 표 문법 결함 — 인라인 코드 안 이스케이프 안 된 생 `|`** 7곳(order-management L585×2·591·597·601·612, order-detail L1111)이 마크다운 표 열을 깨뜨림. 다른 6개 스펙은 `\|`로 정확히 이스케이프하는 내부 불일치. 파급: OM DC 표가 9열로 넓어져 노션에서 정상 행 45개가 빈 셀 패딩 | 직접 grep 실측(7곳 전건) | VERIFIED |
| F-30 | MINOR | 총괄감사 | 닫는 백틱 직후 `+`가 노션에서 `•`로 치환 — 10파일 70행 83건. 대부분 가독성 문제지만 최소 1건 의미 훼손(`No dots `6`+ exist` = "6번 이상 점 없음" → `6` • exist) | 총괄 미러 감사 실측 | VERIFIED |
| F-31 | **MAJOR** | R2 (C-55) | **[3차 심판 확정] 출고 시 재고 원장 — MAJOR(BLOCKER 아님).** VO는 출고 재고 이동을 어디서도 말하지 않으나(DC-39 origin이 전부 입고 방향) **금지하지도 않아** 동시 만족 가능. 단 RTO는 명시("decrements on-hand… consumes the reservation", 별도 이벤트 2종), INV는 소비만 하고 생산 안 함 → VO DC-39 커버리지 누락. 부수: 이 건이 "이름 문제"로 오분류돼 있음(TM 공유개념표·VO CP-7·OD X-8이 "names, not behaviors"라 단언하나 이 짝은 열거 자체가 다름) | 3차 심판(VO·OD·INV·RTO 4문서 대조) | VERIFIED |
| F-32 | 검증대기 | R3 dev-eyes | **개발자 시선 감사 9/9 — 질문 236건(BLOCKER 47·MAJOR 125·MINOR 64)**, 판정 BLOCKED 6 / BUILDABLE-WITH-QUESTIONS 3. 콘텐츠 분류 평균 **규범 78.7% · 참고 12.6% · 과정잔여물 8.6%**(감독 추정 30%보다 훨씬 낮음). 이동 후보 74건·모호 [ADMIN] QA 118건. **BLOCKER 47건은 반증 전이라 미확정** | wf_f0afbcf5(2.4M tok) | OPEN |
| | | | **— 오너 결정 (2026-08-03, 아티팩트 388947b2) —** | | |
| D-1 | 결정 | F-21 | **취소된 입고 요청의 송장 스캔 = 미인식 풀로 낙하** (IR 쪽이 정본). VO의 "등록 번호는 항상 State 6"을 "**매칭이 활성인**(취소되지 않은) 요청에 등록된 번호"로 한정. 반영 대상: `_global-rules.md` [G-10]·[G-11](CANCELLED 터미널) · `view-orders.md` [L-S1-1] 우선순위 1·BR-17·[L-S6-1]·신규 E번호·§9.5 CP 행. IR은 이미 정합 | 오너 답변 | 반영대기 |
| D-2 | 결정 | F-22 | **미인식 등록 슬랙 알림 = 의심 담당자 @멘션**(TM 쪽이 정본). 반영 대상: `_global-rules.md` Slack 라우팅표 · `view-orders.md` 라우팅표("none (channel post)" → 멘션) + **와이어프레임 view-orders M2b 안내 문구(L1531)**. TM 스펙·와이어프레임은 이미 정합(L226·L232에 "@mentions the suspected PICs") | 오너 답변 | 반영대기 |
| D-3 | 결정 | F-23 | **창고 로컬 타임존 = KST(Asia/Seoul) 확정.** 반영 대상: `order-detail.md` §3.0.3의 "warehouse local (SGT)" → KST · `_global-rules.md`에 타임존 규칙 신설(현재 KST/SGT 언급 0건 = 중재 규칙 부재가 이원화의 근본원인). INV는 이미 KST | 오너 답변 | 반영대기 |
| D-4 | 결정 | F-32 | **과정잔여물 이동/삭제 = 하지 않음 (오너 2026-08-03).** 이동 후보 74건(전체 8.6%)은 본문에 그대로 존치. 근거: AI가 1차 독자라 길이 비용이 낮고, 검증 통과한 QA 어서션·상호참조 구조를 재차 흔드는 리스크가 이득보다 크며, 실제 소음 판정은 개발자가 읽은 뒤가 정확. **핸드오프 후 개발자 피드백 기반 정리로 이월** | 오너 답변 | CLOSED |

---

## 최종 집계 (2026-08-04 마감)

| 단계 | 원시 발견 | 확정 | 반증률 |
|---|---|---|---|
| R1 기계 검증 | 3 | 2 (F-1 ID중복·F-3 폐기) | — |
| R2a QA 전량 재실행 (647건) | 9 FAIL | 9 (전건 spec-stale, **와이어프레임 결함 0**) | — |
| R2b 모순 사냥 | 134 | 17 (BLOCKER 2·MAJOR 15) | 73% |
| R3 개발자 시선 | 236 (BLOCKER 47) | 6 (전부 MAJOR로 강등) | 87% |
| R4 노션 미러 | 7페이지 감사 | 7/7 손상 → 전면 재게시 | — |
| **합계** | **417+** | **~30** | — |

### 최종 게이트 (커밋 5465bca)
- 기계 검증 4종: 전역 ID 인용 무결성 OK · QA ID 중복 0 · 마크다운 표 열 정합 0 · 노션 파괴 위험 0
- `[WF]` QA **647/647 PASS · FAIL 0 · 회귀 0** (VO 136 · OD 69 · RTO 93 · INV 75 · OM 77 · TM 66 · CL 74 · IR 57)
- 러너 엄격성: OM 8건은 뮤테이션 테스트(수리 되돌린 사본)로 8/8 검출 확인 — 통과시키려 느슨해진 검사 없음

### 방법론 교훈 (다음 라운드에 적용)
1. **적대 반증이 핵심 장치였다.** 원시 발견의 73~87%가 오탐(선언된 divergence·이력 서술·층위 차이·"다른 문서가 이미 답함"). 반증 없이 수리했다면 없는 결함 수백 건을 고치며 문서를 부풀렸을 것.
2. **감독의 지시도 검증 대상.** QA-M1-08/09 개명 지시가 이미 점유된 번호였고, 담당 에이전트가 잡아 10/11로 정정. 지시를 그대로 따랐다면 중복을 옮기기만 했을 것.
3. **와이어프레임만 고치면 스펙·러너가 깨진다.** D-2 반영 때 실제로 발생(QA-M2-11 FAIL) — 문구 변경은 항상 화면·스펙·러너 3곳 동시 처리.
4. **노션 부분 수정 금지.** 부분 수정이 날조 문장과 행 병합의 원인. 전면 재게시 + 재fetch 검증만 사용.
