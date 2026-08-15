# R1 — 기계 검증 결과 (원시 발견, 판정은 에이전트/감독이)

생성: 2026-08-03 · 기준선 태그 review-baseline-20260803

## 1. 전역 ID 인용 무결성
- 정의: G 15개 · PD 86개
- 전 문서: 미정의 G/PD 인용 0건 ✓

## 2. 페이지 로컬 ID (인용 but 표-정의 부재 — 후보, 에이전트 확인 필요)
- **view-orders**: E: ['E-18', 'E-51']
- **ready-to-outbound**: BR: ['BR-51'] · E: ['E-01', 'E-02', 'E-03', 'E-04', 'E-05', 'E-06', 'E-07', 'E-08', 'E-09'] · DC: ['DC-01', 'DC-02', 'DC-03', 'DC-04', 'DC-05', 'DC-06', 'DC-07', 'DC-08', 'DC-09']
- **stock-status**: E: ['E-1', 'E-2', 'E-3', 'E-4', 'E-5', 'E-6', 'E-7', 'E-8', 'E-9', 'E-10', 'E-11', 'E-12', 'E-13', 'E-14', 'E-15', 'E-16', 'E-17', 'E-18', 'E-19', 'E-20', 'E-21', 'E-22', 'E-23', 'E-24', 'E-25', 'E-26', 'E-27', 'E-28', 'E-29', 'E-30', 'E-31', 'E-32', 'E-33', 'E-34', 'E-35', 'E-36', 'E-37', 'E-38', 'E-39', 'E-40', 'E-41', 'E-42', 'E-43', 'E-44', 'E-45', 'E-46', 'E-47', 'E-48', 'E-49', 'E-50', 'E-51', 'E-52', 'E-53', 'E-54', 'E-55', 'E-56', 'E-57', 'E-58', 'E-59', 'E-60', 'E-61', 'E-62', 'E-63', 'E-64', 'E-65', 'E-66', 'E-67', 'E-68', 'E-69', 'E-70', 'E-71', 'E-72', 'E-73', 'E-74', 'E-75', 'E-76', 'E-77', 'E-78', 'E-79', 'E-80', 'E-81', 'E-82', 'E-83', 'E-84', 'E-85', 'E-86', 'E-87', 'E-88', 'E-89', 'E-90', 'E-91', 'E-92', 'E-93', 'E-94', 'E-95', 'E-96', 'E-97', 'E-98']
- **inbound-request**: BR: ['BR-53'] · E: ['E-01', 'E-02', 'E-03', 'E-04', 'E-05', 'E-06', 'E-07', 'E-08', 'E-09', 'E-14']

## 3. QA 시나리오 수 재계산 vs 자기보고 census
- view-orders: 고유 QA ID 277 / 자기보고 279  ← **불일치** · [WF] 토큰 167 (보고 136) · [ADMIN] 토큰 163 (보고 143)
- order-detail: 고유 QA ID 161 / 자기보고 ? · [WF] 토큰 90 (보고 ?) · [ADMIN] 토큰 109 (보고 ?)
- ready-to-outbound: 고유 QA ID 201 / 자기보고 ? · [WF] 토큰 104 (보고 ?) · [ADMIN] 토큰 124 (보고 ?)
- stock-status: 고유 QA ID 200 / 자기보고 ? · [WF] 토큰 89 (보고 ?) · [ADMIN] 토큰 140 (보고 ?)
- order-management: 고유 QA ID 171 / 자기보고 ? · [WF] 토큰 84 (보고 ?) · [ADMIN] 토큰 104 (보고 ?)
- tracking-missing: 고유 QA ID 168 / 자기보고 ? · [WF] 토큰 93 (보고 ?) · [ADMIN] 토큰 123 (보고 ?)
- closing: 고유 QA ID 192 / 자기보고 ? · [WF] 토큰 90 (보고 ?) · [ADMIN] 토큰 147 (보고 ?)
- inbound-request: 고유 QA ID 130 / 자기보고 ? · [WF] 토큰 70 (보고 ?) · [ADMIN] 토큰 103 (보고 ?)
  (토큰 수는 본문 인용 포함이라 보고치보다 클 수 있음 — ID 카운트가 1차 신호)

## 4. 정본 문자열 (허브 카피·슬랙 ID·이벤트명)
- G-7 정본 허브 문구 추출: 20건
  - `[WF-15] closing`: 0/8  ← **0/8 페이지만**
  - `[WF-NEW-E]`: 0/8  ← **0/8 페이지만**
  - `[IR-WFX-1]`: 0/8  ← **0/8 페이지만**
  - `_wireframe-fixes.md`: 0/8  ← **0/8 페이지만**
  - `@ Mentions`: 8/8 ✓
  - `Comments mentioning me · Click to open the order`: 8/8 ✓
  - ` pane header | `: 0/8  ← **0/8 페이지만**
  - `Unstar to remove from the list`: 8/8 ✓
  - `… from list`: 0/8  ← **0/8 페이지만**
  - `… from the list`: 0/8  ← **0/8 페이지만**
  - `… from this list`: 0/8  ← **0/8 페이지만**
  - `Unstar to remove`: 8/8 ✓
  - `closing.md`: 0/8  ← **0/8 페이지만**
  - `tracking-missing.md`: 0/8  ← **0/8 페이지만**
  - `order-detail.md`: 0/8  ← **0/8 페이지만**
  - `Mark all read`: 8/8 ✓
  - `Mark all as read`: 0/8  ← **0/8 페이지만**
  - `{n} results · newest first · click to open the order`: 0/8  ← **0/8 페이지만**
  - `No matching comments`: 5/8  ← **5/8 페이지만**
  - `🔍 Search all comments — order no. · author · text`: 5/8  ← **5/8 페이지만**
- 슬랙 토큰 `C0BMGEWM5QA`: 스펙 9개 문서에서 인용
- 슬랙 토큰 `#unrecognized-tracking`: 스펙 9개 문서에서 인용
- 슬랙 토큰 `#wholesale-ops`: 스펙 8개 문서에서 인용
- 슬랙 토큰 `#partnership-kr`: 스펙 8개 문서에서 인용
- 슬랙 토큰 `#fulfillment-admin-comments`: 스펙 9개 문서에서 인용
- 이벤트명 `comment.posted`: 8/8 스펙
- 이벤트명 `order.outbounded`: 6/8 스펙
- 이벤트명 `print.job_result`: 7/8 스펙
- 이벤트명 `comment.auto_posted`: 6/8 스펙

## 5. 스테일 패턴 그렙
- `Daily Shipping Status auto` (PD-71 폐기 전 문구): closing:1
- `Request Inbound` (은퇴 명칭): order-detail:9, stock-status:6, WF/order-detail:1
- `OWNER-PENDING\]` tags below are superseded` ((배너 정상)): 0건 ✓
- `SAMPLE-3SET` (PD-51 이전 샘플 표기(라벨)): 0건 ✓
- `which sample and how many` (PD-51 이전 요건 서술): order-detail:1, ready-to-outbound:3, order-management:2, _global-rules:1, WF/order-management:1
