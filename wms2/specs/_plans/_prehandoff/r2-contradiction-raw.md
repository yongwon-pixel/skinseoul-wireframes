# R2 — 모순 사냥 원시 발견 (미검증, 적대 반증 전)

워크플로우 wf_c9f3e0ec-652 · 15/16 완료(register-vs-spec은 크레딧 한도로 미실행) · 4.57M 토큰 · 29분

> **이 문서의 주장은 아직 검증되지 않았다.** 반증 통과분만 ledger.md로 승격한다.


## 경계면 페어 감사 — shipping-label ↔ view-orders (ready-to-outbound 함께 정독)

### [C-1] MAJOR — shipping-label §5는 View Orders(order Print·single-item auto-print)와 RTO(row Print·Bulk Print Labels)를 '내부 송장(PACKING)을 발행하는 표면'으로 계약하지만, 두 화면 스펙의 프린트 파이프라인·이벤트 어디에도 내부 송장이라는 산출물이 존재하지 않는다 — VO는 산출물을 'the order's shipping label' 단일 개념으로만 서술하고(DC-28 surface enum에 송장 구분 없음), RTO는 산출물 타입을 {shipping_label, picking_list} 둘로 한정해 내부 송장의 슬롯이 없다. 각 화면 스펙만 보고 구현하면 내부 송장은 어느 표면에서도 출력되지 않는다.

- `shipping-label.md`: "`[G-4]` instant print (no dialog, no preview, correct carrier automatically) from every Print surface that emits the internal invoice: View Orders (order Print, single-item auto-print), RTO (row Print, Bulk Print Labels), Order Detail (Print)."
- `view-orders.md`: "Clicking prints the order's shipping label through the local print agent per `[G-4]`. Persists `[DC-28]` `surface=order_label`"
- `view-orders.md`: "`surface` ∈ {order_label, auto_single_item, return_labels}"
- `ready-to-outbound.md`: "**Three print surfaces on this page** — and exactly three:"
- `ready-to-outbound.md`: "`artifact_type` ∈ {`shipping_label`,`picking_list`}"

주: shipping-label §1은 '디스패치 시 두 문서(캐리어 라벨+내부 송장)가 출력되며 혼동 금지'라고 못박았으므로, VO/RTO의 프린트 이벤트(DC-28/29, DC-6/7/12)가 2문서 출력을 모델링하지 않는 것은 단순 용어 차이가 아니라 계약 편측 존재. VO QA-NG-02/E-20의 'one label print' 단언도 2문서 모델과 충돌 소지.

### [C-2] MAJOR — shipping-label은 'fully CONFIRMED·frozen'(v1.2, 2026-08-03)인데 VO §6.4/§9.1과 RTO §9.1은 라벨·송장 레이아웃을 여전히 'Phase 3-1(추후 별도 오너 세션)' 미래 작업으로 서술하는 드리프트가 있고, VO는 내부 문서를 'DELEO A4 picking sheet'로 지칭해 확정된 통합 내부 송장(전 캐리어 공통 100×150mm 서멀·가로)과 모순된다.

- `shipping-label.md`: "**Status:** **fully CONFIRMED** (owner, 2026-08-03) — carrier-label policy, unified internal invoice, and all three §6 items are decided. No open questions."
- `shipping-label.md`: "One internal-invoice format for **all** carriers. YUN switches from portrait to landscape; DELEO keeps landscape; a future carrier (FedEx etc.) inherits the format with zero changes."
- `view-orders.md`: "what is physically on the DELEO A4 picking sheet and the YUN 4×6 carrier label, including the sample-set dual view `[G-13]` — is **out of scope** for this spec and is handled in Phase 3-1 with the owner (§9.1)."
- `ready-to-outbound.md`: "**Label and invoice layout content** — what is drawn on a Deleo or YUN label, field placement, barcode position, sample-row rendering on the printed artifact | **Phase 3-1**, a separate owner session after Phase 3."

주: out-of-scope 위임 자체는 정당하나, 위임 대상이 이미 같은 디렉토리에 확정본으로 존재하는데 '미래 세션'으로 서술 + 산출물 물성('A4')이 확정 스펙(100×150mm 서멀)과 어긋남. 핸드오프 독자가 확정본의 존재를 놓치게 만드는 포인터 부패.

### [C-3] MAJOR — RTO M1 헤더 {units}의 정의('테이블이 렌더하는 그 집합의 Σ(qty)')와 WF-9 적용 후의 테이블(샘플 행 ×1 포함 5행)이 충돌한다 — 정의대로 계산하면 9인데 QA-M1-01은 8 units를 단언한다. 동시에 shipping-label §3.3은 내부 지류에서 샘플 세트를 총수량에 포함(9 = 8 products + 1 sample set)하기로 확정했으므로, 같은 '내부 종이 위 총수량' 개념이 두 문서에서 반대로 간다(송장=포함 확정, 피킹리스트=제외 단언·정의는 모호).

- `ready-to-outbound.md`: "| `{units}` | `Σ(qty)` over the **pickable (inbounded) lines only** — the same set the table renders."
- `ready-to-outbound.md`: "it equals exactly `Print Pick Locations — Picking List (3 orders selected · 4 SKUs · 8 units total)`"
- `ready-to-outbound.md`: "row 5 `Product` reads exactly `sample set` — no sample type and no per-type quantity — and its `Qty` reads `×1` inside a `<b>` element"
- `shipping-label.md`: "**The sample set counts toward `총수량` and `합계`** — the invoice verifies what is physically in the box, so paper and box must agree (e.g. `9 = 8 products + 1 sample set`)"

주: WF-9 적용 전(4행)에는 정의와 수치가 일치했으나 샘플 행이 추가되면서 {units} 정의문이 재조정되지 않았다. 개발자가 정의문대로 구현하면 QA-M1-01이 실패하고, QA대로 구현하면 정의문 위반. 샘플 포함/제외 중 어느 쪽이든 명문 판정 필요.

### [C-4] MINOR — 같은 샘플 세트 픽에 대한 로케이션 서술이 두 내부 지류에서 갈린다 — 내부 송장은 'location = sample shelf'(로케이션 값을 표기)인데, 피킹 리스트는 '로케이션 없음, `Sample` 마커 렌더·정렬 불참'으로 서술한다. 피커가 걷는 지류(M1)에는 샘플 위치가 없고, 검수용 지류(송장)에는 있다.

- `shipping-label.md`: "one amber-tinted row rendered as exactly `sample set` (no type, no per-type qty — PD-51), location = sample shelf"
- `ready-to-outbound.md`: "followed by the sample-set row, whose first cell is a `.locpill` reading `Sample` rather than a location code"
- `ready-to-outbound.md`: "the sample row is **last** and is excluded from the location ordering: it carries no location, so it cannot participate in the ascending sort"

주: RTO E-66은 '등록 로케이션 없는 샘플 SKU는 unknown-marker 규칙'이라고 해 샘플 SKU에 로케이션이 있을 수 있음을 전제 — 샘플의 로케이션 모델(있음/없음/마커)이 문서 간 미정렬.

### [C-5] MINOR — 박스 실물 수량의 서술이 선언 없이 분기한다 — shipping-label은 'paper and box must agree'로 샘플 포함 9를 확정했는데, RTO Total Items는 스스로를 'the count of physical units to put in the box'라 정의하면서 라인아이템 합만 계산(샘플 미포함, 샘플 주문이면 8)하고, VO 주문 카드의 'Total Quantity: {n}'도 샘플 포함 여부를 무언급한다. RTO가 {items}/{units} 분기는 정밀하게 선언한 것과 달리 이 분기는 어느 문서에도 선언돼 있지 않다.

- `shipping-label.md`: "the invoice verifies what is physically in the box, so paper and box must agree (e.g. `9 = 8 products + 1 sample set`)"
- `ready-to-outbound.md`: "**Value.** `Σ(quantity)` over **all** line items of the order — the count of physical units to put in the box."
- `view-orders.md`: "`Order ID: {id}` (blue) · `Order Status:` + status pill · `Total Quantity: {n}`"

### [C-6] MINOR — 내부 송장 상품명 칼럼에 EN 브랜드 볼드 프리픽스 요구가 빠져 있다 — RTO는 G-6를 '한국어 이름 어디서나 bold EN brand 필수'로 읽어 M1·Ready Item Details에 강제(BR-6, 브랜드 누락을 결함 RTO-WFX-5로 등록)하는데, 같은 내부 지류인 송장의 §3.3 상품명은 'Korean product name'만 명시해 브랜드 프리픽스 여부가 미정의다.

- `shipping-label.md`: "**상품명** — Korean product name (label content is data and stays Korean `[G-6]`)."
- `ready-to-outbound.md`: "Korean product names in *Ready Item Details* and in the M1 picking list, with the **EN brand in bold** [G-6]."
- `ready-to-outbound.md`: "[G-6] requires the bold EN brand on Korean names everywhere, and [BR-6] requires Korean names in exactly these two surfaces. Near-identical Korean names exist in the catalogue (`마데카 크림 타이트닝` vs `마데카 크림 타임 리버스`), so the brand prefix is the disambiguator."
- `shipping-label.md`: "Capacity at these sizes ≈ 9 item rows per page."

주: 브랜드 프리픽스를 넣으면 행 폭·페이지 용량(9행) 산정에도 영향 — 침묵으로 두면 두 내부 지류가 다른 이름 표기를 갖게 됨.

### [C-7] MINOR — 캐노니컬 이벤트 `print.job_result`의 페이로드 상태 어휘가 두 프린트 표면 스펙에서 다르다 — VO DC-29는 status ∈ {success, pending, agent_offline, printer_unreachable, timeout, rejected}, RTO DC-12는 state queued→sent→done|failed + failure_reason. 이름은 캐노니컬로 공유한다고 선언하면서 상태 모델이 갈리는데, 이 분기는 VO CP-7(페이지 스코프 이름 5종 목록)에도 등재돼 있지 않다.

- `view-orders.md`: "`status` ∈ {success, pending, agent_offline, printer_unreachable, timeout, rejected}"
- `ready-to-outbound.md`: "`state` `queued` → `sent` → `done` \| `failed`, `failure_reason` (agent unreachable / printer offline / timeout)"

주: 양쪽 다 리터럴 명명은 dev 결정으로 위임하고 있어 완화되지만, 캐노니컬 이벤트를 화면 간 조인하는 소비자는 두 스키마 매핑이 필요 — 미선언 드리프트.

### [C-8] MINOR — [쌍 감사 범위 밖 부수 발견 — view-orders 내부] v1.3에서 추가된 M1 로케이션 시나리오가 기존 ID를 재사용해 QA-M1-06과 QA-M1-07이 각각 2회 등장(ID 충돌)하고, §8.14 집계(279 / 136 WF / 143 ADMIN / 92 negatives)와 §10.3 Traceability(277 / 135 / 142 / 91)가 서로 불일치한다(§10.3이 v1.3 델타 미반영).

- `view-orders.md`: "**QA-M1-06 [WF]** `[L-M1]` `[BR-58]`"
- `view-orders.md`: "**QA-M1-06 [ADMIN]** `[E-26]` — *negative*"
- `view-orders.md`: "| Total scenarios | **279** |"
- `view-orders.md`: "**QA scenarios: 277** — 135 `[WF]` / 142 `[ADMIN]`"

주: QA-M1-07도 동일하게 [ADMIN] E-94판과 [ADMIN] E-27판이 공존. 'ID 불변·재번호 금지' 체제에서 중복 부여는 인용 충돌을 만들므로 신규 항목에 새 번호(QA-M1-16 등) 부여가 필요 — 재번호가 아니라 신규 채번이라 불변 규칙 위반이 아님.

**대조 후 이상 없음:** 캐리어 라벨 정책: shipping-label §2(캐리어 기본 출력 그대로·carrier-agnostic forward-binding) ↔ VO BR-40/L-S1-10(캐리어명 라벨 금지·Deleo 제거) ↔ RTO BR-10(캐리어 해석은 주문 단위) — 모순 없음 · 샘플 세트 캐리어 전달 이원화: shipping-label §3.4('(+ sample set)'를 마지막 상품명에 append, 별도 라인·수량·가격 미전달) ↔ RTO BR-21 rationale('The carrier-facing label only appends (+ sample set)') — 일치 · 샘플 행 문자열: shipping-label §3.3 'exactly sample set (no type, no per-type qty — PD-51)' ↔ RTO PD-51 결정·QA-M1-05('sample set — no sample type and no per-type quantity') — 일치 · 내부 송장 데이터 소스: 사이즈=라인아이템 Size 칼럼(VO 테이블 Size 칼럼 실재, QA-S1-13), 로케이션=SKU 등록 로케이션·1 SKU 1 로케이션(G-14 ↔ VO BR-21), JIT 등 무로케이션 '—' 표기(VO Location 칼럼 '–' 관행과 개념 일치) — 모순 없음 · G-4 즉시 인쇄 프로토콜(다이얼로그·프리뷰·새 탭 금지, print.job_result 영속): shipping-label §2/§5 ↔ VO §6.4 ↔ RTO §6.4 — 일치 · shipping-label §5의 표면 명칭 열거(order Print / single-item auto-print / row Print / Bulk Print Labels)는 VO [L-F3]·[L-S1-Fa], RTO [L-F6]·[L-3]의 실제 컨트롤과 명칭 수준에서 전부 대응(내부 송장 개념 부재는 발견 1로 별도) — 누락·유령 표면 없음 · 인쇄 실패 비차단 원칙: VO BR-15/E-39 ↔ RTO BR-31/BR-9b — 상호 일치, shipping-label과 충돌 없음 · M4 공급사 반품 라벨은 shipping-label 문서 분류(디스패치 2문서) 밖의 별개 지류로 양쪽 다 명확히 분리 — 혼선 없음

## WMS 2.0 마감 전 검토 — 경계면 페어 감사: closing.md ↔ view-orders.md (기준선 review-baseline-20260803). 초점: 스캔 프로토콜(G-1 델타), Prepare Shipment 전이, Amend Closing, 카운팅 병합(PD-7)

### [C-9] MAJOR — 같은 서버 액션(order.outbounded)의 아웃바운드 게이트가 두 스펙에서 다르다 — closing M1 게이트는 '취소 플래그 아님(not order.cancelled)'을 요구하며 이를 '전역 술어(VO BR-9와 동일, no page exception)'라고 주장하지만, VO BR-9에는 취소 플래그 조건이 없고 VO E-35는 cancelled를 status_forbids_outbound 사유로 처리해 '취소=플래그(9번째 상태 아님)'라는 양 스펙 공통 교리와 모순된다(언더라잉 status가 processing인 취소 주문은 BR-9를 통과하므로 status 사유로 거부될 수 없다).

- `wms2/specs/closing.md`: "m1_enabled = zero_packing_checked
             AND every(line.inbound_status == INBOUNDED) AND line_count >= 1
             AND order.status == processing
             AND not order.cancelled"
- `wms2/specs/closing.md`: "View Orders `BR-9` and `order-detail.md` L-9 both state the outbound gate as **iff every line is INBOUNDED**, with no page exception; a closing-only side door would ship an order whose goods were never received"
- `wms2/specs/view-orders.md`: "`Outbound` is enabled **iff** the order has ≥1 line **and** every line is INBOUNDED **and** status ∈ {`processing`, `pending`} **and** not on hold **and** not already outbounded."
- `wms2/specs/view-orders.md`: "Order is refunded or cancelled mid-flow, then outbound is attempted | Rejected with the reason named in the toast; persists `[DC-44]` with `reason=status_forbids_outbound` `[BR-9]`."

주: VO대로 구현하면 취소 플래그 주문(언더라잉 processing, 전 라인 INBOUNDED)에 Outbound 버튼이 활성화되고, DC-44 사유 enum에도 cancelled 항목이 없다. closing E-56/QA-M1-10은 같은 케이스를 서버 거부로 QA-단언한다. VO BR-9에 'not cancelled(flag)' 추가 + DC-44 사유 enum 정리가 필요.

### [C-10] MAJOR — 캐노니컬 공유 이벤트(order.status_changed / order.outbounded)의 페이로드가 두 작성자 간에 어긋난다 — 상태값 레지스터(closing: 소문자-하이픈 'prepare-shipment' 의무, VO: 공백형 'prepare shipment')와 판별자 스킴(VO DC-8: 닫힌 enum trigger∈{manual, combined_last_item, bulk_all_remaining}에 closing 값 없음 vs closing DC-14: source=closing_m1)이 서로 다르다.

- `wms2/specs/closing.md`: "This spec uses the label register in prose and in every rendered string, and the value register in every `DC-*` payload (e.g. DC-13 `processing → prepare-shipment`)."
- `wms2/specs/view-orders.md`: "| **DC-9** ⓒ | `order.status_changed` | order | `order_id`, `reason` ∈ {outbound, cancel_outbound, external} | `processing → prepare shipment` / `prepare shipment → processing` |"
- `wms2/specs/view-orders.md`: "| **DC-8** ⓒ | `order.outbounded` | order | `order_id`, `sku_set[]`, `total_qty`, `trigger` ∈ {manual, combined_last_item, bulk_all_remaining} | — |"
- `wms2/specs/closing.md`: "DC-14 | `order.outbounded` | same action as DC-13 (the semantic action alongside the state transition) | resolver | order | `order_id`, `source=closing_m1`, `correlation_id` (identical to DC-13), `idempotency_key`"

주: 양 스펙과 _global-rules 모두 이 이벤트명을 '어디서든 byte-identical' 캐노니컬로 선언하지만, 같은 이벤트를 두 페이지가 다른 값 표기·다른 출처 필드로 쓰면 다운스트림 조인이 깨진다. closing의 M3a-D19 정규화(값=소문자-하이픈)가 VO DC-9/토스트·QA 문자열에 미반영된 개정 드리프트.

### [C-11] MAJOR — 딥링크 경로 형식에 대해 두 스펙이 정반대의 규범 주장을 QA로 고정했다 — closing은 디렉토리형이 '[G-12]로 확정(fixed), index.html형 금지'라며 2026-08-03 정규화 완료를 선언하고, VO는 같은 날짜 기준으로 G-12의 디렉토리형을 '예시적(illustrative)·크로스페이지 불일치'로 규정하고 index.html형을 전면 채택하며 코퍼스 차원 확정은 미결(CP-8)이라고 명시한다.

- `wms2/specs/closing.md`: "the **directory form** `../{slug}/#{anchor}` fixed by `[G-12]`, never `../order-detail/index.html#…` (cross-page defect M3a-D16, normalized 2026-08-03)"
- `wms2/specs/view-orders.md`: "`[G-12]`'s illustrative directory form (`../inbound-request/#reqlist`) is a cross-page inconsistency, not a second permitted form on this page (§9.5 CP-8)."
- `wms2/specs/view-orders.md`: "`[G-12]` fixes one form corpus-wide. If the directory form wins, the wireframe `href`, §3/§6.2 and QA-S6-02 change together — never the spec alone"

주: _global-rules.md G-12 실문은 'e.g. … `../inbound-request/#reqlist`' 예시뿐이라 어느 쪽 독해도 강제하지 않는다. closing QA-HIST-11과 VO QA-S6-02가 서로 반대 형식을 단언하므로, G-12에 형식을 명문화하고 진 쪽 스펙·QA를 같은 패스에서 고쳐야 한다.

### [C-12] MINOR — VO의 크로스페이지 레지스터 CP-5가 closing의 2026-08-03 M3a-D3 교정(취소=플래그, 언더라잉 상태+Cancelled 마커 렌더링) 이후에도 'closing이 Cancelled를 주문 상태로 쓴다'는 교정 전 상태를 현재형으로 기술하고 있다 — CP-1/CP-4/CP-6에는 붙은 ✅ RESOLVED 마크가 없다.

- `wms2/specs/view-orders.md`: "**`closing` uses `Cancelled` as an order status** in its verdict matrix, `BR-20`, `[E-5]` and PD-76's title."
- `wms2/specs/closing.md`: "Corrected 2026-08-03 (cross-page defect M3a-D3); the register title of `[PD-76 · OWNER-PENDING]` still lists "Cancelled" among the statuses and needs the same correction at the owner's next pass — the behavior specified here is the corrected one."

주: 행동 계약 자체는 이미 양 스펙이 일치(언더라잉 상태+마커). CP-5의 '잔여 수정' 지시가 이미 이행됐으므로 CP-5를 RESOLVED로 갱신해야 기준선 독자가 미결로 오독하지 않는다. PD-76 레지스터 제목 수정은 양쪽 다 잔여로 인정.

### [C-13] MINOR — closing의 M1 전파 계약이 VO에 존재하지 않는 표면·행동을 단언한다 — 'View Orders의 Processing working set에서 빠진다/더는 리스팅하지 않는다(수동 리프레시 없이)'고 쓰지만 VO는 주문 리스트가 없는 단일 스캔 허브이고, VO 자신의 외생 상태변경 모델은 액션 시점 서버 거부 + '해당 뷰 리프레시 시 렌더'(E-34)로, 무조작 푸시 갱신을 어디에도 약속하지 않는다.

- `wms2/specs/closing.md`: "Then View Orders no longer lists it in the `Processing` working set, Order Detail shows `Prepare Shipment` plus the closing-sourced comment, Order Management's status counts update, and Ready to be Outbounded recomputes its eligibility — all without a manual refresh on those screens"
- `wms2/specs/view-orders.md`: "The server rejects the outbound with an explicit hold error; red toast; the banner and the disabled button render on refresh of that view; persists `[DC-44]` with `reason=on_hold`."

주: closing §6.2 표의 'the order leaves the `Processing` working set' 행도 동일 문제. closing 스스로 전파 메커니즘·지연을 DQ-4(개발 결정)로 열어두었으므로, QA-M1-12의 VO 절은 'VO에서 해당 주문을 다시 열람/스캔하면 갱신된 상태가 보인다' 수준으로 재기술하는 것이 안전하다.

### [C-14] MINOR — 상태 렌더링 레지스터 불일치 — closing은 8개 상태값을 '렌더 문자열에서는 항상 타이틀케이스 라벨'(refunded→Refunded, M3a-D19 크로스페이지 정규화)로 못박았지만, VO는 State 4 상태 필을 소문자 `refunded`로 byte-exact QA 단언하고([ADMIN] 교정 트윈 없음) 토스트도 값 레지스터('Status: prepare shipment')로 렌더한다 — VO 내부의 다른 필(`Prepare Shipment`, `On Hold`)과도 어긋난다.

- `wms2/specs/closing.md`: "**Status label vs status value.** The 8 statuses are stored as **lowercase-hyphenated values** (`pending` · `processing` · `on-hold` · `completed` · `refunded` · `failed` · `shipped` · `prepare-shipment`) and rendered as **title-case labels**."
- `wms2/specs/view-orders.md`: "Given State 4, Then the order-card status pill text is exactly `refunded`, and the token `returned` does **not** appear as a status value anywhere in `#s4`"
- `wms2/specs/view-orders.md`: "green toast `✓ Outbound complete — Order {id}` / `Status: prepare shipment`"

주: QA-S4-02는 [WF] 단언이라 데모 카피 기록일 수 있으나, VO에는 어드민에서 라벨 레지스터를 쓰라는 [ADMIN] 트윈이 없어 소문자 필이 그대로 구현 목표로 읽힌다. QA-S3-01/QA-S5-01은 타이틀케이스라 페이지 내에서도 혼재.

**대조 후 이상 없음:** PD-7 동시성 모델: closing BR-30(카운팅=서버 병합, 단일값=낙관적 버전 체크) ↔ VO BR-44(State 6 카운팅 병합, 주문 편집 낙관적 409) — 동일 모델, 동일 PD 인용 · PD-8 트래킹 네임스페이스: closing §3.6/E-13(마감은 아웃바운드 트래킹만 해석, 인바운드 번호=unknown) ↔ VO BR-45/E-8(VO에서 충돌 시 인바운드 우선) — 상보적이며 충돌 없음 · unknown-order ↔ unrecognized 풀 비연결: closing BR-23/§6.1 '#unrecognized-tracking 비라우팅' ↔ VO §6.1 'Closing의 unknown은 이 페이지의 unrecognized와 disjoint' — 양방향 명시 일치 · G-7 Comments 허브 카피 HUB-1…HUB-7: 양 스펙 인용 문자열 바이트 일치(2026-08-03 WF-15/WF-VO-1 동일 커밋 반영) · Slack @mention 라우팅: 채널 #fulfillment-admin-comments(C0BMGEWM5QA)·페이로드 필드·PD-4 실패 시 비롤백 시맨틱 — 양쪽 동일 · G-3 오디오 분담: G-3b TTS 'Please check this order'=closing 전용(VO §6.5 'No TTS on this page' 명시), G-3c 오제품 경고음=VO 전용(closing §6.6 'No' 명시), G-3a는 버튼 클래스 스코프로 상호 정합 · G-1 스캔 프로토콜 델타: 포커스 복귀+전체선택, 클릭-애니웨어 리포커스(입력 필드 제외), 무리프레시 — 페이지별 델타가 상충하지 않음 · 8-status 어휘 집합: closing §3.7 매핑 테이블 ↔ VO BR-12/L-S4-6 — 값 집합 자체는 동일(레지스터 표기만 F2/F6에서 지적) · Amend Closing(§3.24-3.25): VO 측 계약 위반 없음 — M1 재사용은 기존 DC-13/DC-14 체인·stale 거부로 커버되고, VO가 참조해야 할 신규 표면 없음 · 이중 스캔 처리 비대칭: closing E-54(단일 리드 더블엔터 억제) vs VO E-67(State 6 이중 방출 이중 계수) — 카운터 시맨틱이 다른 의도적 설계로 양쪽 모두 근거 명시, 결함 아님 · 마감 게이트 유비: VO BR-18 'the same gating class as the Closing page' ↔ closing BR-3 exact-match — 정합

## 경계면 페어 감사 — order-management ↔ ready-to-outbound (기준선 review-baseline-20260803). 양 스펙 전문 정독 + 와이어프레임 HTML·_global-rules.md·_provisional-decisions.md 교차 확인.

### [C-15] MAJOR — WF-9(피킹 리스트 샘플 행)·PD-36의 현재 상태가 문서 간·문서 내에서 정반대로 서술된다 — RTO §3.15/QA-E-20은 '2026-08-03 적용 완료·PD-36 사실상 확정'이라 하고, RTO §2.4·§9.4·OQ-1 말미와 OM §9.1은 '샘플 행 없음·PD-36 승인 대기로 블록'이라 한다(와이어프레임 실측은 행이 존재 = 적용 완료 측이 사실).

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "**WF-9 was applied to the wireframe on 2026-08-03** (owner-approved batch): M1 now renders one amber-tinted `sample set` row for order `422165` ... `[PD-36]` is thereby settled in the affirmative for the modal"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "M1 picking list has no sample-set rows, while [G-13] requires internal picking artifacts to show **which** sample and **how many**. Fix is **conditional** on owner approval of PD-36 *and* an answer to PD-51."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "**WF-9** — add sample rows to the M1 picking table | **Conditional** — blocked on `[PD-36]` approval **and** OQ-1 (`[PD-51]`)"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "wireframe fix **WF-9** (adding sample rows to M1) is no longer gated on a definition source — only owner approval of `[PD-36]` remains. QA-E-20 unblocks once PD-36 lands."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "Unblocks the internal-invoice and picking-list *content*; `_wireframe-fixes` WF-9 now waits on `[PD-36]` only"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/ready-to-outbound/index.html`: "<!-- WF-9 (2026-08-03): sample-set picking line per [G-13]/[BR-21] — PD-51 v1 keeps the single label "sample set" -->"

주: 와이어프레임(index.html L361-362)에는 샘플 행이 실제로 존재하므로 §3.15/QA-M1-03(5행 [WF] 단언)/QA-E-20 측이 사실이고, RTO §2.4 레지스터 행·§9.4 백로그 표·OQ-1 말미 문장·§6.2/DC-5의 'once PD-36 lands', 그리고 OM §9.1의 'WF-9 now waits on PD-36 only'가 미전파 스테일. 취소선·이력 표기가 아닌 현행 상태 표들이라 이력 서술 면제에 해당하지 않음. 헤더의 owner-decided 목록(PD-1~8,51,55,66,71,74,79)에 PD-36이 없어 'settled in the affirmative' 주장과 OWNER-PENDING 태그 사이의 근거 충돌도 남는다.

### [C-16] MAJOR — MKT 오더 PIC의 타입 계약이 정면 충돌한다 — OM은 자유 텍스트 PIC를 허용하고 그것이 'RTO에 렌더된다'고 명시(BR-4·E-59)하는데, RTO [L-8]은 'PIC resolves to a system user'(PD-33)로 못박고 자유 텍스트 분기를 전혀 정의하지 않는다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "**Free-text PIC:** stored as a display string, not a user reference. It renders in the order list PIC column and in RTO"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "**PIC defaults to the logged-in user and accepts free text.** The select lists system users; `✎ Custom` accepts any string, which `Search PIC` matches as a substring. | The real PIC is sometimes an agency contact or a campaign owner with no admin account; forcing a system user would produce a false record."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "PIC resolves to a system user `[PD-33 · OWNER-PENDING]`; if unset, render an explicit `PIC: —` rather than an empty line [E-42]; if the user was deactivated, render the stored display name unchanged plus a neutral marker rather than dropping the line [E-71]."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_plans/_provisional-decisions.md`: "**[PD-33] PIC edit — free text or user picker, and is the new PIC notified?**
Provisional: **System-user picker; no automatic Slack notification** (use an @mention comment to notify).
Rationale: PIC feeds filters and mention routing, so it must resolve to a real user; auto-notifying every reassignment would be noise.
Pages: OD (Q-A11/L-5), OM (custom-PIC exception, PD-51 area)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "| **DC-14** | `order.mkt_surfaced` | system | order | `import_batch_ref` (Order Management), `pic_user`, `rto_visible_at`"

주: RTO의 PIC 소스는 오직 OM 임포트인데, 그 소스가 자유 텍스트를 허용한다(OM DC-12 payload: pic type `user_ref|free_text`). PD-33 레지스터 스스로 'OM (custom-PIC exception)'을 명기하고 RTO를 적용 페이지로 나열하지도 않는데, RTO는 PD-33을 무예외 인용. 자유 텍스트 PIC('Agency — Lumi')가 RTO에 표출되는 순간 [L-8]의 user-ref 전제(E-71 비활성 사용자 마커, DC-14 `pic_user` 필드)가 성립하지 않는다.

### [C-17] MAJOR — 공유 컴포넌트인 Comments 허브의 클릭 라우팅 계약이 갈린다 — OM(BR-32)·G-7은 허브 행이 inbound request/pool item일 수 있고 클릭이 '그 엔티티의 화면'으로 라우트된다고 하는데, RTO §3.10·§6.2는 무조건 'opens the order (Order Detail)'로 못박는다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "Click on any hub entry opens the order (Order Detail) [G-12]."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "The hub is identical on all eight screens; only the entry points differ."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "**The Comments hub corpus is cross-entity.** Rows surfaced here may reference orders, inbound requests or unrecognized-pool items `[G-7]`; a click routes to that entity's own screen `[PD-67 · OWNER-PENDING]`."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "`[G-7]` makes pool items a first-class commentable type and the hub searches all comments, so this page's hub cannot assume every row is an order."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "Commentable entity types include orders **and** inbound requests **and** unrecognized-pool items."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "The hub is one component with one string; "click opens the entity" is the behavior, and the word `order` is not re-worded per entity type."

주: G-7이 '단일 컴포넌트·click opens the entity'를 명시하고 허브 검색은 전 코퍼스를 대상으로 하므로 RTO 허브에도 비-오더 행이 표출될 수 있다. OM의 BR-32 논거('이 페이지의 허브는 모든 행이 오더라고 가정할 수 없다')는 RTO에 동일하게 적용되는데 RTO는 정확히 그 가정을 명문화했다. RTO §3.10/§6.2/QA-L10-12의 라우팅 문장을 엔티티 라우팅으로 교정 필요.

### [C-18] MINOR — OM §6.3이 임포트 후 도착지를 `../ready-to-outbound/#marketing`(Marketing view 활성화)으로 계약하지만, RTO 스펙·와이어프레임 어디에도 `#marketing` 프래그먼트로 탭을 활성화하는 수신측 계약이 존재하지 않는다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "| Confirmed import | Ready to be Outbonded, Marketing view | `../ready-to-outbound/#marketing` — MKT orders are listed there immediately, regardless of stock (BR-1) |"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "| V-3 | **Marketing** | `.vtab[data-view="mkt"]` | `MKT-40233` | `Found 1 order(s) with items ready for outbound` |"

주: RTO의 Marketing 뷰 도달 경로는 탭 클릭뿐이며(V-3), 와이어프레임 HTML에 location.hash/hashchange 핸들러가 0건임을 실측 확인. OM의 QA는 디렉토리형 href(`../{slug}/#anchor`)를 단언하므로 프래그먼트 계약이 편측에만 존재한다. 링크 자체는 RTO 페이지로 열리고 All 뷰에도 MKT 행이 보이므로 동작은 완만히 열화하나, 'Marketing view'라는 약속은 수신측 미정의.

### [C-19] MINOR — carrier_unresolved 후속 조치의 오너 존재 여부가 상반된다 — OM §6.2는 '풀필먼트 담당자에게 수동 Slack 연락(PD-55 owner-decided)'이라 하고, RTO §6.1은 현행 산문으로 'No route and no owner exist for that follow-up'이라 주장한다(RTO 자신의 §9.2 OQ-2 해답과도 모순).

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "**"Not connected — contact the Fulfillment Center" orders raise no Slack alert.** No route and no owner exist for that follow-up — that is precisely the gap recorded as `[PD-55 · NO-DEFAULT]` (§9.2 OQ-2)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "**`carrier_unresolved` row created** → no automated Slack route; the follow-up is manual Slack contact with the fulfillment person in charge (`[PD-55]` owner-decided 2026-08-03, §9.1)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "**The answer.** Unblocking is **manual coordination — contact the fulfillment person in charge via Slack**. v1 ships no in-admin release/carrier-assignment UI and no automated Slack route."

주: 헤더의 supersession 공지(PD-55 포함)가 인라인 태그는 무효화하지만, 'No route and no owner exist'는 태그가 아닌 현행 사실 서술이라 공지로 덮이지 않는다. '자동 Slack 라우트 없음' 부분은 양쪽 일치 — 갈리는 것은 오너 존재 서술뿐.

### [C-20] MINOR — '8화면 동일'이라 선언된 허브의 닫힘 계약이 갈린다 — OM은 outside click + Esc 두 경로를 규범으로 명시하는데, RTO는 outside click만 명시하고 Esc는 스펙 전체에서 부재한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "**Dismissal:** the panel closes on an outside click and on `Esc`."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "Dropdown anchored top-right; **closes on outside click**, stays open on clicks inside (normative)."

주: RTO QA-L10-09도 outside click만 단언. 동일 컴포넌트 선언(RTO §3.10 'identical on all eight screens')하에서 한쪽만 Esc를 규범화한 드리프트 — 침묵 대 명시 유형이라 MINOR.

### [C-21] MINOR — 동일 허브의 `Mark all read` 확인 서피스가 갈린다 — RTO는 G-2/BR-34 근거로 녹색 토스트 `✓ All mentions marked as read`를 규범(spec-defined)으로 부여했는데, OM의 같은 액션(E-39·QA-CMT-10)은 토스트 없이 배지 클리어만 서술한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "with a right-aligned `Mark all read` action (HUB-4) [DC-4]. On use it shows the green toast `✓ All mentions marked as read` **(spec-defined)** because the change spans rows the operator may not be looking at [G-2] [BR-34]."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "**Badge:** equals the unread mention count; `Mark all read` clears it to zero without a page reload ([E-39])."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "Then every `.unread` tint is removed, the nav badge clears to `0` without a page reload, and `[DC-24] comment.mark_all_read` persists with the 3 comment ids and `count=3`"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "The hub is identical on all eight screens; only the entry points differ."

주: RTO의 근거(읽음 상태 변경이 시야 밖 행에 걸침 → G-2 토스트)는 코퍼스 공통 논리라 OM 허브에도 동일 적용돼야 한다. OM은 명시적 부정은 아니고 무언급이므로 MINOR — 다만 QA 스위트가 양 페이지에서 상반된 기대를 기계 단언하게 되는 지점.

### [C-22] MINOR — PD-51로 개정된 G-13('sample set' 단일 표기, which/how-many 폐기)이 반영되지 않은 현행 산문이 양쪽에 남아 있다 — OM §1.3은 '피커에게 which sample·how many를 알려야 한다'를 현재형 규범 근거로 서술하고, RTO §2.4 WF-9 행도 '[G-13] requires ... which sample and how many'를 현행 요구로 서술한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "the sample dual-view rule `[G-13]` exists because the picker must be told *which* sample and *how many*, while the carrier-facing data must not be told (tax handling)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md`: "Internal invoice and picking artifacts render **"sample set" only** in v1 — no type/qty breakdown (`[PD-51]` owner-decided 2026-08-03)"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md`: "M1 picking list has no sample-set rows, while [G-13] requires internal picking artifacts to show **which** sample and **how many**."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_plans/_provisional-decisions.md`: "[G-13]'s "which sample and how many" requirement is amended accordingly."

주: 두 인용 모두 이력 표기(취소선·'was'·날짜 한정) 없이 현재형으로 G-13 요구를 진술하므로 이력 서술 면제 대상이 아니다. PD-36 레지스터 항목의 Provisional 문구('list WHICH sample and HOW MANY per [G-13]')도 같은 계열의 미개정 텍스트.

**대조 후 이상 없음:** MKT 즉시 표출 계약: OM BR-1·모달 노트('appear immediately in Ready to be Outbonded (Marketing view) regardless of stock or inbound status') ↔ RTO BR-3/[L-8]('shown immediately on import, regardless of stock or inbound status') — 문구·결정일(2026-07-23)·리버설 이력까지 일치 · MKT 행 시각 처리: 퍼플 틴트 토큰(--mkt-soft #F3EEFF)·MKT 배지·PIC 표기 — 양쪽 토큰값 일치(클래스명 tr.mkt vs .row-mkt는 페이지별 마크업 차이로 계약 아님) · 머지 가드: OM BR-18/§3.9.4/E-37 ↔ RTO §3.8 Merging/E-59 — PD-59 인용·차단 문구·머지된 오더의 stale 거부까지 정합 · carrier_unresolved 메커니즘 본체: amber 문자열 'Not connected — contact the Fulfillment Center' byte 동일, 라벨 인쇄만 no_carrier로 거부(E-61↔DC-28), Bulk Outbound 비차단, v1 인-어드민 해제 UI 없음 — 양쪽 §9의 PD-55 해답 본문 일치(§6.1 산문 1곳 제외, 발견 5) · 샘플 규칙 본체: 캐리어 대면 '(+ sample set)' 마지막 상품명 append ↔ 내부 'sample set' 단일 라인(v1, 타입/수량 무분해), MKT 오더 샘플 미매칭(OM BR-17/E-35/E-56 ↔ RTO 샘플 행이 422165 세일즈 오더에만 존재) — 내용 자체는 정합(상태 서술 충돌은 발견 1·8) · Slack 라우팅: 양쪽 모두 #fulfillment-admin-comments(C0BMGEWM5QA) 단일 확정 라우트, 멘션 fan-out은 단수 mentioned-user payload로 정합(RTO E-75의 per-distinct-mention 계약과 OM DC-20 payload 모순 없음) · 허브 캐노니컬 스트링: HUB-1~7 — OM(2026-08-03 'Unstar to remove from the list'로 이동 기록)과 RTO('all seven already matched') 모두 G-7 v1.2 값과 일치 · idempotency 이벤트명 차이(OM DC-28 idempotency.duplicate_suppressed vs RTO DC-11 idempotency.duplicate_rejected): OM §5가 M3a D14로 선언한 의도된 미수렴 — 결함으로 등재하지 않음 · 딥링크 경로형: 양쪽 모두 디렉토리형 ../{slug}/#anchor (OM §6.3 path-form 노트 ↔ RTO §6.2 ../order-detail/) — 일치 · RTO 정렬·탭 술어: regular→MKT→JIT 전역 정렬, Marketing 탭='manually imported MKT orders', MKT+JIT 중복 시 MKT 우선(BR-36) — OM 측 서술과 충돌 지점 없음, 흐름 이벤트 소유권(OM DC-9 쓰기 ↔ RTO DC-14 표출 기록)도 정합

## 경계면 페어 감사 — view-orders ↔ inbound-request (기준선 review-baseline-20260803, 양쪽 스펙 전문 정독 + grep 재검증)

### [C-23] BLOCKER — IR v1.3의 PD-79 CANCELLED 라이프사이클이 VO에 전혀 미반영 — 취소된 요청의 등록 송장 스캔에 대해 VO는 '항상 State 6 진입', IR은 '매칭 비활성화로 미인식 풀 낙하'로 정반대 동작을 규정한다 (VO 전문에 CANCELLED 요청 상태·PD-79·deactivation 언급 0건, grep 실측).

- `wms2/specs/view-orders.md`: "1. **Inbound-request tracking number** → **State 6**, always, never a customer-order state. Every tracking number registered on the request matches, including the 2nd and 3rd of a split shipment `[G-10]`."
- `wms2/specs/inbound-request.md`: "**View Orders tracking matching is deactivated** for every number registered on the request, atomically with the cancellation — a subsequent scan of such a number does **not** match and falls to the unrecognized pool like any unknown barcode (`[E-96]`)."
- `wms2/specs/view-orders.md`: "| **DC-38** | `inbound_request.status_changed` | request | `inbound_no`, `trigger` ∈ {partial_save, full_confirm} | `REQUESTED → PARTIAL → INBOUNDED` |"
- `wms2/specs/view-orders.md`: "| **BR-17** | A tracking number registered on an Inbound Request always opens State 6, and **every** tracking number of a split shipment matches the same request; partial arrivals accumulate."

주: 파급 지점: ① VO 해석 정밀도 규칙(L-S1-1)·BR-17이 '등록된 번호는 무조건 매치'로 남아 있음 ② VO의 요청 상태 어휘(DC-38, L-S0-2 'REQUESTED and PARTIAL … INBOUNDED is never listed')에 CANCELLED 부재 ③ E-84(렌더 후 INBOUNDED 전이된 뱃지 행 클릭)의 CANCELLED 대응 케이스 부재 ④ VO §9.5 CP-1~CP-9 어디에도 이 신기능 관련 행 없음. IR 단독으로는 폐쇄돼 있으나 VO 리졸버 구현자는 VO만 읽고 취소 요청을 State 6에 진입시키게 됨.

### [C-24] MAJOR — 예상수량 변경 원점의 배타성 주장 충돌 — VO는 '예상수량 편집은 M6에서만 발생하며 Inbound Request 리스트는 편집 컨트롤이 없다'고 규정하는데, IR의 PD-79 Edit 기능은 REQUESTED 요청의 Order Qty를 데스크에서 (사유 enum 없이) 편집한다.

- `wms2/specs/view-orders.md`: "- **Origin rule:** expected-qty edits originate **only here**. The Inbound Request list *displays* the resulting history and offers no edit control `[G-11]`."
- `wms2/specs/inbound-request.md`: "Given a `REQUESTED` request whose Order Qty is edited from `200` to `260` and whose Supplier is changed"
- `wms2/specs/inbound-request.md`: "Click `✎ Edit` on a `REQUESTED` row → the **New Request form opens prefilled with the request's saved values** (route, lines, costs, supplier, tracking, expected arrival, memo) in **edit mode**"
- `wms2/specs/view-orders.md`: "| **BR-22** | Expected-qty edits require a reason from the fixed enum, may never go below the already-received quantity, may not be `0`, originate **only** in M6, and **never auto-transition** the request to INBOUNDED."

주: 같은 입력(요청의 예상수량)에 두 원점·두 검증 규칙: M6=사유 필수+received 하한, IR Edit=사유 없음(diff 오토코멘트만). VO §9.1도 IR의 편집 범위를 'route/supplier/unit cost'로만 인정해 qty 편집을 배제. IR 자신도 §3.3.5에 'Edits originate only in View Orders M6. There is no edit affordance on this page'라는 구 문구와 BR-13을 그대로 남겨 내부적으로도 §3.3.11과 충돌 — REQUESTED-only 데스크 편집 예외를 양쪽 배타 문구에 명시하는 개정 필요.

### [C-25] MAJOR — IR §5.2의 'VO가 쓰는 이벤트' 계약이 VO의 실제 이벤트 대장과 불일치 — DC-9는 VO에 존재하지 않는 이벤트명이고, DC-7/DC-8은 같은 이벤트명에 페이로드·인코딩이 다르다.

- `wms2/specs/inbound-request.md`: "| **DC-9** | `inbound_request.received_date_recorded` | View Orders State 6 at full receipt | `request_id`, `received_at` (= scan time). **No carrier field** `[PD-9 · OWNER-PENDING]` | Received Date column `[L-S3-10]` |"
- `wms2/specs/view-orders.md`: "| **DC-37** | `inbound_request.fully_inbounded` | request | `inbound_no`, `lines[] = {sku, expected, received, location}`, `received_date` (auto), **no carrier field** `[BR-24]` | — |"
- `wms2/specs/inbound-request.md`: "| **DC-7** | `inbound_request.status_changed` | View Orders State 6 (scan flow) | `request_id`, `old_status` → `new_status`, `received_so_far`, `expected_total`, `causing_scan_event_id`, operator | Status pill `[L-S3-5]`, chips `[L-S3-1]` |"
- `wms2/specs/inbound-request.md`: "| **DC-8** | `inbound_request.expected_qty_edited` | View Orders M6 | `request_id`, `line_id`, `old_qty` → `new_qty`, `reason` ∈ `damaged_defective\|supplier_qty_change\|other`, `reason_memo\|null`, editor | `✎ 300→180 (damaged)` in the Qty cell, per the `BR-30` token map |"
- `wms2/specs/view-orders.md`: "| **DC-35** | `inbound_request.expected_qty_edited` | request line | `inbound_no`, `sku`, `reason` (enum, verbatim string), `memo`, `editor` | `expected {old} → {new}` |"

주: 세 갈래: ① VO는 `received_date`를 DC-37 내부 필드로만 기록 — `inbound_request.received_date_recorded`라는 독립 이벤트는 VO 대장(DC-1~47)에 없음(IR QA-A-27/QA-E-03이 이를 단정) ② DC-7이 요구하는 received_so_far/expected_total/causing_scan_event_id가 VO DC-38(inbound_no+trigger뿐)에 없음 — IR의 PARTIAL n/m 렌더가 읽을 필드를 생산자가 선언 안 함 ③ 같은 이벤트명에서 reason 인코딩이 IR=snake 토큰(damaged_defective) vs VO='enum, verbatim string', 키 명도 request_id/line_id vs inbound_no/sku. 이 셋은 VO CP-7의 5개 선언 목록에도, IR §5 naming caveat(DC-23·DC-15만)에도 미포함 — 미선언 계약 불일치.

### [C-26] MAJOR — 캐노니컬 이벤트 `comment.auto_posted`의 종류 enum이 양쪽에서 서로 다르고(필드명 kind vs trigger 포함), VO가 요청에 남긴다는 partial_saved 코멘트가 요청 코멘트 스레드의 주 표면인 IR의 enum에 없다.

- `wms2/specs/view-orders.md`: "| **DC-23** ⓒ | `comment.auto_posted` | inbound_request · order | `source = system`, `kind` ∈ {expected_qty_edit, match_confirmed, partial_saved, cancel_inbound_memo, return_restock_memo}, structured `old`/`new` payload | system-authored, same pipeline |"
- `wms2/specs/inbound-request.md`: "| **DC-11** | `comment.auto_posted` (`source=system`) | Memo materialisation at registration; expected-qty edit; unrecognized match confirmed; request edited; request cancelled (both 2026-08-03) | system (on behalf of the causing actor) | `inbound_no`, `text`, `trigger` ∈ `memo_materialization\|expected_qty_edit\|unrecognized_match_confirmed\|request_edited\|request_cancelled`, `caused_by_event_id` | Comment thread |"
- `wms2/specs/view-orders.md`: "- `Save Partial Inbound` (M5) raises a **comment on the request** but **no separate Slack route** — the requester learns of it through the comment pipeline if they are mentioned."

주: ⓒ(캐노니컬 = byte-identical 요구) 이벤트인데 판별 필드명(kind/trigger)과 값 집합이 페이지마다 다름. VO M5는 partial_saved 종류로 요청에 오토코멘트를 남긴다고 규정하나 IR DC-11 enum에 해당 트리거가 없고, 같은 개념이 VO=match_confirmed vs IR=unrecognized_match_confirmed로 갈림. 요청 코멘트 스레드를 조인해 읽는 소비자는 두 어휘를 매핑해야 하며 어느 쪽도 이 divergence를 선언하지 않음.

### [C-27] MAJOR — State 0 Expected Inbound 뱃지의 멤버십 술어 불일치 — VO(뱃지 소유 페이지)는 'REQUESTED·PARTIAL 전부'로 규정하고, IR은 'Expected arrival 공란 요청은 뱃지·확장 테이블에서 제외'라는 추가 게이트를 단정한다.

- `wms2/specs/view-orders.md`: "- **Scope:** only unfinished requests appear — `REQUESTED` and `PARTIAL`. An `INBOUNDED` request is never listed `[E-84]`."
- `wms2/specs/inbound-request.md`: "Blank is allowed, renders as an empty Expected arrival cell, and excludes the request from the "Expected Inbound" badge (`[E-54]`)."
- `wms2/specs/inbound-request.md`: "the request is **excluded** from the View Orders "Expected Inbound N" badge and its expandable table."

주: VO의 뱃지 테이블 컬럼(Inbound No.·Sourcing Route·Supplier·Items·Tracking No·Status)에는 Expected arrival 열 자체가 없고 제외 규칙 언급도 전무. IR 규칙대로면 '송장도 없고 도착예정일도 공란'인 REQUESTED 요청은 VO의 파손 라벨 경로(E-47: 뱃지 행 클릭으로 무스캔 State 6 진입)에서 도달 불가가 됨 — 어느 술어가 맞는지 한쪽으로 확정 필요.

### [C-28] MINOR — State 6 배너 딥링크 경로 표기 불일치 — VO는 `../inbound-request/index.html#reqlist`로 전면 통일(§9.5 CP-8 선언)했으나 IR §6.2는 여전히 디렉토리형 `../inbound-request/#reqlist`로 표기하고 IR 쪽에는 아무 플래그가 없다.

- `wms2/specs/inbound-request.md`: "| **Inbound** | View Orders **State 6** banner → `../inbound-request/#reqlist` | Opens the **Request List** tab [G-12]."
- `wms2/specs/view-orders.md`: "**Path form:** this page writes the deep link in the `index.html#anchor` form everywhere — `[L-S6-2]`, §6.2 and QA-S6-02 — because that is the shipped `href` the `[WF]` assertion reads. `[G-12]`'s illustrative directory form (`../inbound-request/#reqlist`) is a cross-page inconsistency, not a second permitted form on this page (§9.5 CP-8)."

주: VO CP-8이 [G-12] 차원의 해소를 배정해 두긴 했으나, CP-8 본문은 갈라선 쪽으로 [G-12]와 'some specs'만 지목 — 링크의 도착 페이지인 IR 자신이 디렉토리형을 쓰고 있다는 사실은 어느 쪽에도 기록돼 있지 않음. IR §6.2 한 줄 수정이면 닫힘.

### [C-29] MINOR — PD-66(무식별자 풀 항목) 해소 상태 드리프트 — VO는 '오너 결정 완료, 케이스 부존재'로 본문까지 개정했으나 IR §9.2 OQ-2는 여전히 '어느 쪽도 행동 미규정, 오너 결정 필요'라고 서술한다.

- `wms2/specs/view-orders.md`: "- **Decided (`[PD-66]`, owner 2026-08-03):** the no-identifier case does not exist — either a tracking number or an order number is always present."
- `wms2/specs/inbound-request.md`: "*No behavior is specified on either side.* **Owner decision required.**"

주: IR 헤더 배너(PD-66 OWNER-DECIDED, 인라인 태그 supersede)가 형식상 우선하므로 규범 충돌은 아니나, IR은 같은 배너 아래에서 OQ-1은 'RESOLVED'로 본문을 재작성하고 OQ-2는 방치 — 'No behavior is specified on either side'는 VO E-63/QA-CV-22가 이미 행동(식별자 필수, 거부 단정)을 규정한 현재 상태와 사실관계가 어긋남.

### [C-30] MINOR — 공유 데모 엔티티의 수치·소유 불일치 — 같은 Inbound No. 202607120001이 VO에서는 PARTIAL 620/800·송장 10325661220417, IR에서는 PARTIAL 120/180·송장 10324880021991이고, 그 10324880021991은 VO State 5(고객주문 홀드)의 스캔값으로도 등장해 양측 데이터를 한 세계로 읽으면 VO 자신의 인바운드 우선 해석 규칙과 모순된다.

- `wms2/specs/view-orders.md`: "row 2 contains `.tag-wholesale` with text `WHOLESALE`, supplier `비엠유통`, and a `.tag-part` badge reading exactly `PARTIAL 620/800`"
- `wms2/specs/inbound-request.md`: "Then row `202607120001` shows the status pill `PARTIAL 120/180`"
- `wms2/specs/view-orders.md`: "the search input's value is non-empty in every one of them: `10323775317888`, `10323775316153`, `10323775316153`, `10322198837710`, `10324880021991`, `10325661220417` respectively."
- `wms2/specs/inbound-request.md`: "And row `202607120001` renders the single number `10324880021991` with no `Add tracking` button"
- `wms2/specs/inbound-request.md`: "Then row `202607120004` renders two tracking numbers `10325661220417` and `10325661220418` in the Tracking No cell with the note `2 tracking numbers — all matching active`"

주: 두 와이어프레임은 별개 정적 목이라 데모 정합이 규범은 아니지만, 양쪽 QA가 [WF]로 byte-exact 단정하는 값들임: ① 202607120001 수량·송장 상이 ② VO State 5의 스캔값 10324880021991이 IR에서는 '매칭 활성' 인바운드 송장 — BR-45/E-8(인바운드 우선)대로면 State 5로 해석될 수 없는 번호 ③ VO State 6이 202607120001에 대해 스캔했다는 10325661220417을 IR은 202607120004 소유로 기재. 시드/데모 데이터를 교차 참조해 구현·QA하는 순간 혼선을 유발하므로 데모 일관화 또는 '페이지 간 데모 비공유' 명시 권고.

### [C-31] MINOR — M6 모달의 계약 문구가 소비 표면(IR Request List Qty 셀) 렌더 형식을 다르게 서술 — VO 모달 카피는 '(300→120)' 즉 {old}→{new}만 표기한다고 하나 IR/BR-30은 `✎ {old}→{new} ({reason token})`으로 사유 토큰이 항상 붙는다.

- `wms2/specs/view-orders.md`: "`The request list qty cell shows the edit history (300→120).` — that fourth fragment is **sentence-initial in the modal**, so it is quoted here with its capital `T` and closing period"
- `wms2/specs/inbound-request.md`: "this page renders the history inline in the **Qty cell**, in the format `✎ {old}→{new} ({reason token})` as a `.route-note` with `title="Expected qty edit history"`. Demo row `202607120001` renders `✎ 300→180 (damaged)`"

주: VO 쪽은 byte-exact 와이어프레임 모달 카피(QA-S6-14 [WF] 단정 대상)라 스펙 서술이 아니라 화면 문구지만, 상대 화면의 실제 렌더 계약(✎ 접두·토큰 필수)과 다르게 안내함. 데모 수치(300→120 vs 300→180)도 상이. 모달 카피를 IR BR-30 형식에 맞춰 개정하거나 VO에 '축약 서술' 주석을 다는 것이 안전.

**대조 후 이상 없음:** 멀티 송장(G-10): 요청당 무제한 등록·전 번호 독립 매치·PARTIAL 누적·같은 송장 재스캔 시 잔량부터 재개(VO E-22/BR-17 ↔ IR L-S3-7/E-44) — 일치 · 수신 파이프라인 3단계(REQUESTED→PARTIAL→INBOUNDED)·PARTIAL 비필수 정차(IR E-89)·PARTIAL 필 산술 = received/expected(양측이 동일한 [G-11] 델타를 각각 선언, VO PARTIAL 620/800 ↔ IR PARTIAL 120/180 형식) — 일치 · 송장 uniqueness: 시스템 전역 유일·타 요청 등록 시 상대 Inbound No. 명시 차단(VO E-64/PD-82 ↔ IR BR-15/E-21=E-35)·전문자열 등가 매칭(E-73)·인바운드/아웃바운드 네임스페이스 분리 및 인바운드 우선(VO BR-45/E-8 ↔ IR BR-16/E-22) — 일치 · INBOUNDED 터미널 의미론: 추가 송장 차단→신규 요청(PD-85, VO 없음·IR E-28), 완료 요청 재스캔 = VO 읽기 전용 6b+info 토스트(E-17) ↔ IR 결과 링크·역링크 부재(L-R10) — 일치 · Carrier 미기록·Received Date 자동(스캔 시각, PARTIAL은 '–', 완료 시점 기록): VO BR-24/WF-1 ↔ IR BR-12/L-S3-10/WF-2 — 일치 · 수동 수신 상태 전이 금지: IR BR-11/L-R12(데스크는 CANCELLED만) ↔ VO BR-52(State 6 = 유일 확정 경로) — 일치 · M6 계약: reason 3옵션·세 번째 라벨 'Other'(양측 동일 C-11 채택), received 하한 하드블록(VO E-24 ↔ IR E-42), 정확 일치로 낮춰도 auto-confirm 없음(VO E-23 ↔ IR E-43), 오토코멘트+@requester Slack 채널 #fulfillment-admin-comments C0BMGEWM5QA 동일 — 일치 · 오버수령: warn-and-count·cap 금지·n>m unclamped 렌더·full confirm 차단(VO BR-19/E-15 ↔ IR E-92/QA-C-22) — 일치 · 미인식 풀 복구 루프: 전용 등록 경로 기각·풀 재사용·요청 생성→송장 등록→사유 'routed to inbound request'+Inbound No. 캡처→재스캔 State 6(VO BR-48 ↔ IR BR-19/DC-21/E-53) — 일치 · 모닝 no-tracking Slack 체크 소유권: IR 소유(#wholesale-ops/#partnership-kr) ↔ VO §6.1 'Not routed from this page' 명시 — 일치 · 카탈로그 스냅샷 의미론: 요청 라인은 선택 시점 스냅샷·재파생 금지(VO L-S6-5 ↔ IR E-66/E-91) — 일치 · 프로덕션 딥링크 도착 계약: 특정 Inbound No.로 필터(VO §6.2/L-S6-2 ↔ IR L-F5/QA-G-07) — 일치 (경로 표기형만 MINOR 발견 참조)

## 경계면 페어 감사 — stock-status ↔ order-detail (레포: /Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs, 기준선 review-baseline-20260803). 두 문서 전문 정독 후 동일 물리 사실·이벤트·검증·상호 인용·개정 드리프트 대조.

### [C-32] BLOCKER — 같은 창고의 '로컬 타임존'을 stock-status는 KST(Asia/Seoul), order-detail은 SGT로 규범 선언하고 있어, 두 페이지가 공유하는 동일 재고이동 이벤트가 화면마다 1시간 어긋난 시각으로 렌더된다 — 어느 쪽 X-리스트/충돌 선언에도 없는 미선언 정면 모순.

- `wms2/specs/stock-status.md`: "**All timestamps render in KST (Asia/Seoul)**: `YYYY-MM-DD HH:MM` in list columns, `HH:MM:SS` in audit-session detail. No relative times ("2 hours ago") anywhere. | Warehouse staff reconcile against paper and against carrier portals, both of which are wall-clock KST."
- `wms2/specs/order-detail.md`: "| `[L-3]` Actor Log `Time` | `MM-DD HH:mm` (`07-01 09:32`), year omitted | **warehouse local (SGT)**, not printed | persisted event |"
- `wms2/specs/order-detail.md`: "a rendered time that omits its zone (Actor Log, comments) is warehouse local by definition, never browser local."

주: order-detail DC-21은 'the ledger row the Inventory screen reads'로 명시돼 있어 같은 이벤트가 양쪽 화면(Actor Log ↔ Stock History)에 렌더된다. 둘 다 2026-08-03에 확정된 규칙(BR-32 vs BR-43)이며 서로 반대다.

### [C-33] MAJOR — order-detail은 Inventory M4 릴리스의 효과로 '해당 라인이 PENDING으로 복귀 + Inventory가 DC-21 기장'을 계약으로 주장하지만, stock-status의 [L-M4] Confirm 효과에는 라인 상태 쓰기가 전혀 없다(DC-4/DC-5/DC-6만 persist, M4를 '수령 역전'이 아닌 '예약 해제'로 모델링) — 선언된 [X-1]/§3.16 충돌표는 restock 컨트롤 비대칭만 다루고 이 계약은 어느 쪽에도 선언돼 있지 않다.

- `wms2/specs/order-detail.md`: "| Inventory M4 — reservation released on a line of this order `[PD-45 · OWNER-PENDING]` | the line returns to `PENDING` and `Latest Inventory Count` refreshes | `DC-21` written by Inventory; Order Detail renders the result and must not write a second movement |"
- `wms2/specs/order-detail.md`: "Both paths write `DC-21`; the server must ensure one line's receipt is reversed **once** — the second attempt is a stale-entity rejection `[PD-6 · OWNER-PENDING]`, not a second movement."
- `wms2/specs/stock-status.md`: "| **Yes** | `[DC-4]` reserve released (Reserved 8 → 5) **+** `[DC-5]` restocked (Available 34 → 37). Stock History gains a `RESERVE` release row. Toast: `Reservation released — Order {id} · restocked +{n}` |"
- `wms2/specs/stock-status.md`: "reserved `before → after` (8 → 5); released qty; release reason (`phantom` \| `manual`); order status at release; memo id?"

주: 이벤트명 차이(inventory.movement vs stock.reserve_released/stock.restocked)는 [X-8] '5개 공유 개념' 선언으로 일부 커버되나, '라인 PENDING 복귀'는 stock-status 어디에도 없다. stock-status의 M4가 이 효과를 내지 않으면 order-detail §5.3 랜딩 계약은 이행 불가.

### [C-34] MAJOR — stock-status M4 메모의 듀얼라이트(주문 Comments 히스토리에 `comment.posted`·`source=m4-memo`)를 받는 order-detail의 코멘트 택소노미에 이 랜딩을 표현할 자리가 없다 — DC-26은 `source=human`, DC-32의 origin enum은 {unrecognized_match_confirmed, expected_qty_edit}뿐이고, §5.3 'Inventory M4' 랜딩 행에도 코멘트 랜딩이 없다. 같은 캐노니컬 이벤트명(comment.posted)에 양립 불가한 payload.

- `wms2/specs/stock-status.md`: "A written memo **dual-writes**: it is stored on the release event **and** posted to the order's Comments history `[DC-11]` with `source=m4-memo`."
- `wms2/specs/order-detail.md`: "`comment.posted` | `[L-1]` Add Comment | `comment_id`, `body_raw` (verbatim), `mentions[]` (resolved, deduplicated user ids `[E-80]`), `unresolved_mention_tokens[]`, `source=human`"
- `wms2/specs/order-detail.md`: "`origin` ∈ {`unrecognized_match_confirmed`, `expected_qty_edit`}"
- `wms2/specs/order-detail.md`: "**System comments.** Comments arriving from another screen's pipeline (unrecognized-match confirmation) render in this same thread and persist with `source=system` (`DC-32 comment.auto_posted`)"

주: stock-status는 QA-RES-08에서 '메모가 Order 409112의 Comments history에 나타난다'를 [ADMIN] 시나리오로 단언하지만, 수신 측 스펙에는 m4-memo를 분류할 source/origin 값이 없다.

### [C-35] MAJOR — order-detail은 'cancelled는 상태값이 아니라 플래그'(BR-12)로 확정하고 [X-3]에서 위반자로 Closing만 지목했지만, stock-status [L-M3]도 Status 컬럼에 `cancelled`를 상태값으로 렌더하고 팬텀 술어를 'order status ∈ {cancelled, refunded}'로 정의한다 — Inventory 측 위반은 미선언.

- `wms2/specs/stock-status.md`: "**Phantom predicate:** order status ∈ {`cancelled`, `refunded`} **AND** the reservation was never released."
- `wms2/specs/stock-status.md`: "| 409112 | 2026-07-02 | Liam Chen | `cancelled` (red) + `SUSPECTED PHANTOM` (amber) | 3 | 07-02 09:10 | `Cancel Inbound` (red outline) |"
- `wms2/specs/order-detail.md`: "**Cancellation is a flag on the order, not a ninth status:** a cancelled order keeps whatever status value it carried and gains a cancellation marker"
- `wms2/specs/order-detail.md`: "**`Cancelled` as a status value.** Closing renders `Cancelled` in an `Order Status` column; the 8-status vocabulary has no such value."

주: 8값 어휘 기준으로 refunded는 상태지만 cancelled는 아니므로, stock-status의 팬텀 술어는 order-detail 모델에서는 'cancellation flag OR status=refunded'로 재정의돼야 한다. [X-3] 목록에 Inventory 추가가 필요.

### [C-36] MAJOR — stock-status는 [L-M3] Order ID를 Order Detail 딥링크로 규범 지정하지만, order-detail의 DC-34 entry_path 닫힌 enum에는 Inventory발 도착값이 없다 — 'all must land on this page, with DC-34.entry_path set accordingly'라는 계약 아래 이 도착은 분류 불능(사실상 direct로 오기록).

- `wms2/specs/stock-status.md`: "| `[L-M3]` `Order ID` (e.g. `407812`, `413650`, `409112`) | Order Detail | Opens that order. Rendered blue and bold |"
- `wms2/specs/order-detail.md`: "**Inbound (how operators arrive here) — all must land on this page, with `DC-34.entry_path` set accordingly:**"
- `wms2/specs/order-detail.md`: "`entry_path` ∈ {`direct`, `view_orders_row`, `comments_hub`, `slack_deep_link`, `tracking_missing_match`, `clone_link`, `order_management_row`, `rto_row`}"

주: DC-34의 존재 이유가 '도착 경로 분포로 투자 판단'인데, 팬텀 조사→릴리스 전 딥링크(운영상 중요한 경로)가 enum에서 빠져 있다. order-detail §6.2 인바운드 표에도 Inventory 행이 없다.

### [C-37] MAJOR — JIT 재고 수량 계약 모순: order-detail은 'JIT 라인은 Latest Inventory Count = 0이 정상(no warehouse stock backs them)'을 규칙·QA로 못박았지만, stock-status BR-7은 JIT 잔여 재고가 창고에 실재하며 리스트·필터·판매 대상이라고 확정한다 — 동일 SKU 픽스처도 충돌(order-detail은 100005104/100043697/100012534 count 0 단언, stock-status는 같은 SKU에 Available 16/4/6·Total 18/9 단언).

- `wms2/specs/order-detail.md`: "**`Latest Inventory Count = 0` on a JIT line is correct, not an error.** | JIT items are purchased after the order; no warehouse stock backs them."
- `wms2/specs/order-detail.md`: "the rows with SKUs `100005104`, `100043697` and `100012534` (all `JIT (Coupang)`) show `Latest Inventory Count` = `0`"
- `wms2/specs/stock-status.md`: "**JIT residual stock is listed and filterable.** `JIT` is an option in the Sourcing Route filter and JIT rows appear in Current Stocks like any other route."
- `wms2/specs/stock-status.md`: "SKU column values exactly `100031877, 100024743, 100005088, 100004819, 100039958, 100005104, 100040311, 100012534, 100043697, 100038120, 100045210` and `Available` values `82, 61, 55, 34, 23, 16, 11, 6, 4, 2, 1`"

주: order-detail [L-10]은 이 값을 'the live warehouse stock for that SKU'로 정의하므로 라우트 무관하게 stock-status의 수량과 같아야 한다. 잔여 JIT 재고가 존재하는 순간(스톡-status가 정상 상태로 규정) order-detail QA-REN-20의 '인바운드 전 0, 아웃바운드 후 0' 단언은 성립 불가. 픽스처 세계는 원가(15,000/30,630)까지 맞춘 의도적 정합 세계라 우연 불일치로 보기 어려움.

### [C-38] MINOR — order-detail BR-4의 크로스페이지 노트가 INV-WFX-2 적용(2026-08-03) 이후 낡았다 — 'Inventory 폼 노트가 여전히 Request Inbound로 보내고 그 문자열을 QA로 byte-exact 단언한다'고 현재형으로 기술하지만, stock-status는 같은 날 수정 적용을 완료했고 QA는 수정된 문구와 'Request Inbound 전무'를 단언한다.

- `wms2/specs/order-detail.md`: "Inventory's `[L-F2]` form note still sends operators to "Request Inbound on View Orders / the order detail" and asserts that string byte-exactly in its QA."
- `wms2/specs/stock-status.md`: "**APPLIED 2026-08-03** — the wireframe note now reads the corrected copy (`… use the row Inbound buttons on View Orders or Order Detail.`); `QA-FRM-03` asserts the corrected string at `[WF]` tier, `QA-FRM-20` additionally asserts the total absence of `Request Inbound` at `[ADMIN]` tier."

주: 행동 결론('이름 재도입 금지')은 양쪽 동일하므로 서술 드리프트만 해당. 취소선/이력 서술이 아니라 현재형 주장이라 등재.

### [C-39] MINOR — order-detail이 emit하고 'Inventory 화면이 읽는' DC-21의 movement_type 4종 중 역전 2종(cancel_inbound_restock, cancel_outbound_reversal)을 stock-status Stock History의 닫힌 4-배지 어휘(INBOUND/OUTBOUND/RESERVE/ADJUST)로 매핑할 방법이 미정의이며, 어느 매핑도 stock-status BR-3의 배지 의미론('INBOUND/OUTBOUND = 물리적 도크 통과')과 충돌한다.

- `wms2/specs/order-detail.md`: "`movement_type` ∈ {`inbound`, `cancel_inbound_restock`, `outbound`, `cancel_outbound_reversal`}, `source_event_id`, `balance_after`"
- `wms2/specs/order-detail.md`: "`DC-21` is the ledger row the Inventory screen reads."
- `wms2/specs/stock-status.md`: "**Type badges** (`.ty`): `INBOUND` (green) · `OUTBOUND` (blue) · `RESERVE` (purple) · `ADJUST` (red)."
- `wms2/specs/stock-status.md`: "Keeps the logistics history clean: `INBOUND`/`OUTBOUND` mean goods physically crossed the dock. Mixing corrections into them destroys throughput analysis."

### [C-40] MINOR — 동일 주문·동일 SKU 픽스처 드리프트: stock-status는 Order 407847에 SKU 100004819의 INBOUND +6(PENDING) 이동을 단언하지만 order-detail의 Order 407847은 4개 라인(100005104/100043697/100005088/100012534)·수량 각 1로 100004819를 포함하지 않으며, SKU 100005104의 KR 명칭도 '포어레미디 리뉴잉 폼'(stock-status) vs '포어레미디 리뉴잉 폼 클렌저'(order-detail)로 갈린다.

- `wms2/specs/stock-status.md`: "the only `tr.pending` row is the `INBOUND +6` row (tracking `12101316464794`, carrier `Coupang`, order `407847`, auditor `Miranti`)"
- `wms2/specs/order-detail.md`: "The live-admin capture it reproduces is Order **#407847** (customer Maytal Saltoon, AU, carrier YUN, 4 line items)."
- `wms2/specs/stock-status.md`: "the row for SKU `100005104` renders `<b>Dr.Jart+</b> 포어레미디 리뉴잉 폼`"
- `wms2/specs/order-detail.md`: "KR: **Dr.Jart+** 포어레미디 리뉴잉 폼 클렌저"

주: stock-status의 Stock History 검색 컨텍스트는 SKU 100004819(카드·이벤트 모두 해당 SKU). 두 픽스처 세계는 원가·주문번호·채널까지 의도적으로 정합시켜 놓았으므로(15,000/30,630 원가 일치) 이 두 건은 잔여 드리프트로 보임. 양쪽 모두 [WF] QA가 byte 단언.

### [C-41] MINOR — Cancel Inbound 3-계약 충돌(X-1)의 귀책 서술이 상충: stock-status는 '조정 의무는 다른 두 스펙(View Orders·Order Detail)에 있다'고 쓰고, order-detail은 '어느 행도 이 페이지 행동의 결함이 아니다'라며 자기 계약(BR-49)을 방어한다 — 충돌 자체는 양쪽 선언됐지만 오너 판정 전 조정 주체 안내가 반대 방향이다.

- `wms2/specs/stock-status.md`: "**Inventory therefore does not change its behavior**; the reconciliation is owed by the other two specs (and, if the owner picks a different winner, by a dated delta here)."
- `wms2/specs/order-detail.md`: "**None is a defect in this page's behavior** — in every row this spec's position is either the one the global rule supports or the one that cannot be changed without editing the wireframe (SST)."

주: stock-status는 [G-8]('units must land somewhere')를 근거로 자기 계약이 유일하게 원장을 닫는다고 주장하고, order-detail은 BR-41 대칭성(전량 수령=전량 역전)을 근거로 방어한다. 양쪽 다 SST(각자의 와이어프레임)를 인용하므로 오너 판정 시 어느 한쪽 논거 문단은 수정 필요.

**대조 후 이상 없음:** Cancel Inbound 3-계약 충돌의 상호 선언 자체 — order-detail [X-1]과 stock-status §3.16 충돌표의 3개 화면 계약 기술(라디오 유무·수량 캡·remainder 처리)이 서로 일치 · one-reversal-per-line 상호 인용 — stock-status §3.16이 인용한 'Order Detail §6.5의 수렴 보장'이 order-detail §6.5에 실제로 존재하고 문구 취지 일치 · Comments hub 카피(X-6/HUB-1~7) — 'Unstar to remove from the list' 포함 양측 문자열·해소 서술 일치 · 코멘트 검색 캡처 분쟁 — stock-status DC-33(persist) vs order-detail NE-8(non-event)이 양쪽 모두 [G-8] 분쟁으로 상호 선언되어 있고 서술 일치 · Slack 라우팅 — #fulfillment-admin-comments(C0BMGEWM5QA) 채널·payload 필드·비-라우트(#unrecognized-tracking 등) 양측 일치 · product.barcode_registered 발원 분담 — stock-status 캐노니컬 emit, order-detail §5.2 명시적 비-emit으로 정합 · G-3(a) 송신음 범위 — outbound-class 버튼(－ Record Outbound / 📦 Outbound)에만 적용, TTS·경고음 부재 양측 일치(C-5) · 통화 규율 — 무 FX·₩ 원가 렌더 양측 일치, 원가 픽스처(15,000/30,630)가 stock-status 감사 손실액(−15,000/+61,260)과 산술 정합 · 중복 트래킹 경고-후-허용 독트린 — 양쪽 [E-49]의 warn+explicit-confirm 패턴 일치 · 수정된 Inventory [L-F2] 노트의 컨트롤 지칭('row Inbound buttons on View Orders or Order Detail')과 order-detail의 실제 컨트롤 문법(per-row Inbound) 일치 · PD-6 오너 확정 헤더 문구 — 양 문서 동일한 2026-08-03 결정 상태 업데이트 블록 · PENDING 인바운드 확인 경로 — stock-status BR-18(View Orders State 6/Inbound Request 전용)과 order-detail §5.2(inbound-request lifecycle 이벤트 비-emit)가 정합(order-detail의 per-line inbound는 별개 개념으로 상호 배타 선언됨)

## WMS 2.0 마감 전 검토 — 경계면 페어 감사: view-orders ↔ tracking-missing (기준선 review-baseline-20260803, 두 스펙 전문 정독 + _global-rules.md·_inputs/slack-routing.md 라우팅 정본 실측 대조)

### [C-42] BLOCKER — M2b 등록 시 발사되는 #unrecognized-tracking 메시지의 멘션 타깃이 정면 상충한다 — view-orders 라우팅 표는 "none (channel post)", tracking-missing은 "suspected PIC 전원 @멘션(1인 1회)"이며, tracking-missing의 push-not-poll 설계 전체(검색·수동 PIC 검색 제거의 근거)가 이 멘션에 의존한다.

- `view-orders.md`: "| 1 | **M2b** `Send to Missing Tracking List` `[L-M2b]` | `#unrecognized-tracking` (no channel ID is published in `_slack-routing.md`; it is resolved at wiring time) | tracking no., product, qty, memo, registrant, suspected orders | none (channel post) |"
- `tracking-missing.md`: "| 1 | Unrecognized barcode sent to the Missing Tracking List (i.e. a pool row is created) | **`#unrecognized-tracking`** — the routing table publishes no channel ID for it; dev resolves the ID at wiring time (§9.2 D-11) | tracking no., product, qty, memo, registrant, suspected orders | @mentions the **suspected PICs** computed at intake, each exactly once `[BR-39]` | `[DC-4]` |"
- `tracking-missing.md`: "**BR-6** | **Registration auto-notifies `#unrecognized-tracking` and @mentions the suspected PICs.** No human triggers this notification."

주: 정본 실측: _inputs/slack-routing.md와 _global-rules.md §Slack routing 둘 다 이 행에 멘션 타깃 컬럼이 없어 중재 불가(양쪽 페이지가 각자 반대로 보간). VO 자신의 M2b 토스트 sub-line "PIC notified via #unrecognized-tracking"은 TM 쪽과 일치 — VO §6.1 행이 고립된 서술일 가능성이 높으나 오너 확정 필요. 부수: VO는 정본을 `_slack-routing.md`로, TM은 `_global-rules.md`로 각각 다르게 지목(실제 파일은 `_inputs/slack-routing.md`).

### [C-43] MAJOR — PD-66이 view-orders에는 OWNER-DECIDED로 반영(식별자 필수, OQ-1 해소, QA-CV-22 un-deferred)됐으나 tracking-missing 본문은 여전히 NO-DEFAULT·미결(§9.1, E-3, L-1 col 1 nullability, QA-VAL-10 BLOCKED)로 남은 개정 미반영 드리프트다.

- `view-orders.md`: "**Decided (`[PD-66]`, owner 2026-08-03):** the no-identifier case does not exist — either a tracking number or an order number is always present. The registration contract stands: an identifier is required, and M2b never accepts a pool entry without one (see §9.2 OQ-1, resolved)."
- `tracking-missing.md`: "**`[PD-66]` — Can an item enter the pool with NO tracking number (label destroyed, auto-collection failed)?**
- **Status:** not decided. **No default was adopted and no behavior is specified anywhere in this document.**"
- `tracking-missing.md`: "Nullability is undecided — see `[PD-66 · OWNER-PENDING]` and §9.1"

주: TM 헤더 배너는 66을 OWNER-DECIDED로 명시하므로 인라인 태그는 면책되나, §9.1의 "not decided" 산문·QA-VAL-10 BLOCKED·총계의 BLOCKED 1건은 현행 규범 서술이라 QA 판정이 두 문서에서 갈린다. 추가 주의: VO의 결정 문안("tracking **or** order number")은 주문번호만 있고 트래킹이 없는 풀 항목을 허용하는 것으로 읽히는데, 그 경우 TM이 지적한 "매칭이 라인에 기입할 값이 없다"는 문제가 그대로 남는다 — 결정 반영 시 문안 정합도 함께 필요.

### [C-44] MAJOR — 온더스팟 M2 매칭의 이벤트 계약이 불일치한다 — tracking-missing은 DC-8(풀 아이템 OPEN→MATCHED)에 source=view-orders-m2를 요구하지만 양쪽 모두 온더스팟 매칭은 "풀에 들어가지 않는다"고 규정하고, view-orders의 대응 이벤트 DC-41은 registrant를 null로 정의해 "@registrant 멘션·자기멘션 억제" 계약의 대상이 없다.

- `tracking-missing.md`: "**QA-XPG-04 [ADMIN]** — Given a match is performed **on View Orders M2** (on-the-spot), Then the same auto-comment and `#fulfillment-admin-comments` route fire, with `source: view-orders-m2` on `[DC-8]`"
- `tracking-missing.md`: "the tracking number is matched and registered on the spot and **the item never enters this pool** — this is why the pool's Order No column is almost always `–`"
- `view-orders.md`: "**DC-41** | `unrecognized.tracking_matched` | order line | `order_id`, `sku`, `product_line_id`, `tracking_no null → {value}`, `barcode`, `resolver`, `registrant` (null for on-the-spot matches), `mention_suppressed` ∈ {true,false}"

주: DC-8은 엔벨로프에 pool_item_id를 필수로 하는 풀 라이프사이클 이벤트라 풀에 들어간 적 없는 항목에서 발생 불가. 유일하게 정합한 해석은 "이미 풀에 있는 항목을 벤치에서 M2로 재해결하는 경로"인데, 그 경로(M2 매칭이 OPEN 풀 아이템을 닫는가)는 view-orders에 전혀 없음. QA-DATA-12(두 source 대조)도 같은 전제 위에 있다. VO §6.2의 "this page is one of two writers"라는 모호한 문구도 이 지점에서 해석이 갈린다.

### [C-45] MAJOR — 같은 액션(M2b send)의 인테이크 이벤트가 이름·페이로드 모두 다르다 — tracking-missing DC-1은 tracking_no(스캔 시 자동수집, "carried on the intake payload")와 네임스페이스 태깅을 요구하지만 view-orders DC-42 페이로드에는 tracking_no도 네임스페이스도 없다.

- `tracking-missing.md`: "`null → {barcode, product_id (autocomplete pick), product_name_en, product_name_kr, size, qty, memo (nullable), tracking_no (auto-collected at scan time), order_no (nullable — carried only when the lookup failed), registrant_id, center, created_at, status: OPEN}`"
- `tracking-missing.md`: "**Namespace:** the number is stored with the namespace the scan originated in — `outbound` for a customer parcel, `inbound` for an unrequested supplier arrival `[BR-11]`"
- `view-orders.md`: "**DC-42** | `unrecognized.sent_to_pool` | pool item | `barcode`, `chosen_product_sku`, `chosen_product_name_en`, `qty`, `memo`, `carried_failed_order_no`, `registrant`, `suspected_orders[]`"

주: tracking_no는 매칭이 라인에 기입하는 이 플로우의 핵심 데이터인데 업스트림 인테이크 이벤트에 없다(서버가 DC-1 raw scan에서 유도한다고 선해할 수는 있으나 어느 문서도 그렇게 말하지 않음). 네임스페이스(outbound/inbound) 판정 주체·시점도 VO에 캡처 배관이 없다. 이 이름 쌍(DC-42↔DC-1)은 TM §5.1 공유개념 표에도 VO CP-7에도 미신고 — 양쪽 모두 '갈림은 선언한다'는 원칙을 표방하면서 이 갈림은 침묵.

### [C-46] MAJOR — M2b send의 중복 방지 계약이 갈린다 — tracking-missing E-1은 tracking_no+barcode 서버 dedupe와 "already in pool" 피드백을 업스트림(View Orders)에 요구하지만, view-orders는 G-9 확정 액션 범위를 E-13에 "한 번에 열거"한다고 선언하면서 M2b send를 목록에서 빠뜨렸고 already-in-pool 피드백 스펙도 전무하다.

- `tracking-missing.md`: "Exactly **one** pool row exists. The server dedupes on `tracking_no + barcode` while an OPEN item exists; the second attempt gets "already in pool" feedback **upstream** on View Orders. Persist `[DC-2]`."
- `view-orders.md`: "**E-13** | Double-click on `Inbound`, `Inbound + Outbound`, `Outbound`, `Confirm Full Inbound`, `Confirm Restock`, `Save Partial Inbound`, `Save Qty Edit`, or `Confirm` (M1) | Exactly **one** server mutation."
- `view-orders.md`: "**No page delta on `[G-9]`.** This page's scope of "confirming action" is enumerated once, at `[E-13]`, and the rejected duplicate persists `[DC-13]` so the fix is provable."

주: VO의 QA-NG-01(더블클릭 스윕)에도 M2b `Send to Missing Tracking List`가 없다. TM E-1이 요구하는 업스트림 피드백은 VO M2b의 어떤 상태·토스트·엣지케이스로도 존재하지 않아 구현자가 VO만 읽으면 빠뜨린다.

### [C-47] MAJOR — M2 주문번호 룩업의 이벤트 정의가 갈린다 — tracking-missing DC-3(View Orders에서 발생)는 result enum에 sent_to_pool을 포함하고 이것만으로 룩업 실패율 KPI를 산출한다고 못박았지만, view-orders의 동일 액션 이벤트 DC-40은 {matched, no_match} 2값 enum이라 그 KPI가 산출 불가하다.

- `tracking-missing.md`: "**DC-3** | `unrecognized_lookup.attempted` | Registrant | The View Orders M2 order-number lookup runs | `{barcode, entered_order_no or null, result: matched \| no_match \| sent_to_pool}` | **Silent.** Source of the lookup-failure-rate figure `[BR-35]`"
- `view-orders.md`: "**DC-40** | `unrecognized.lookup_executed` | — | `barcode`, `entered_order_no`, `result` ∈ {matched, no_match}, `candidate_count`"
- `tracking-missing.md`: "**QA-DATA-04 [ADMIN]** — Given 100 View Orders lookups of which 12 ended in `sent_to_pool`, Then the lookup-failure rate is computable from `[DC-3]` alone `[BR-35]`."

주: 이름 갈림 자체는 페이지 스코프 명명 원칙으로 허용될 수 있으나, 이 쌍은 TM §5.1 공유개념 표(4개)에도 VO CP-7(5개)에도 미신고이며 enum 차이는 이름이 아니라 행동(기록 가능한 결과 집합)의 차이다.

### [C-48] MAJOR — 코멘트 허브 검색 문자열(HUB-5/6/7)의 적용 범위가 상충한다 — view-orders QA-C-18은 "8개 화면 전부 byte-identical, 어느 화면이든 차이는 실패"로 단언하는데 tracking-missing은 admin에 검색 입력 탑재를 의무화하면서도 "이 페이지는 검색 페인을 만들지 않으므로 HUB-5/6/7은 해당 없음"이라고 선언한다.

- `view-orders.md`: "Given the admin's Comments hub on any screen, Then its user-visible strings are byte-identical to the `[G-7]` canonical set and identical on all eight screens: ... `{n} results · newest first · click to open the order` (HUB-5) · `No matching comments` (HUB-6) · `🔍 Search all comments — order no. · author · text` (HUB-7). ... Also asserted unconditionally: a per-screen difference is a failure, whichever screen holds it."
- `tracking-missing.md`: "This page builds no search pane, so HUB-5 / HUB-6 / HUB-7 do not apply here."
- `tracking-missing.md`: "The dropdown markup on this page is missing that input (`WF-NEW-A`). The admin must ship it; the query is persisted `[DC-23]`."

주: TM이 admin에 검색을 의무화한 이상 결과 헤더·빈 결과·플레이스홀더 문자열이 필요해지는데 TM은 이를 미규정 + N/A 선언, VO는 canonical 강제 — 같은 컨트롤에 두 계약. QA-CMT-07도 기능만 단언하고 문자열은 비워둠.

### [C-49] MINOR — view-orders CP-8이 tracking-missing을 index.html 경로 폼 진영으로 기술하지만, tracking-missing은 이미 디렉토리 폼으로 정규화하고 index.html 변형 재도입을 금지해 CP-8의 상대 페이지 성격 규정이 스테일이다.

- `view-orders.md`: "**Deep-link path form** — `[G-12]` and some specs write `../{slug}/#anchor`; this page, `tracking-missing` and this page's `[WF]` QA write `../{slug}/index.html#anchor`."
- `tracking-missing.md`: "**Path form (normalized 2026-08-03, cross-page defect m3a D16).** All cross-page links use the **directory form** `../{slug}/#{anchor}` — the form `[G-12]` itself uses ... The `index.html` variant that earlier drafts of this spec used is **not** to be re-introduced; QA asserts the directory form."

주: 불일치 자체는 CP-8로 선언돼 있고 해소는 G-12 소관이나, CP-8의 진영 분류가 사실과 달라 코퍼스 정규화 결정 시 오도한다. 두 페이지가 서로를 가리키는 링크가 서로 다른 href 폼으로 단언되는 실질 효과도 있음.

### [C-50] MINOR — tracking-missing DC-17(unrecognized_item.rescan_resolved)은 View Orders에서 발생·기록되는 이벤트로 규정되지만, view-orders의 이벤트 대장(DC-1…DC-47, 무결 보장)에는 대응 이벤트가 없다.

- `tracking-missing.md`: "**DC-17** | `unrecognized_item.rescan_resolved` | Bench operator, on View Orders | Rescanning the same barcode/tracking after `[DC-9]` | `{pool_item_id, order_id, line_id, scanned_at, scanner_actor}` — links the physical scan back to the resolution"
- `view-orders.md`: "**Data-capture events: DC-1 … DC-47**, no gaps, plus 10 declared NON-events and per-class retention/export terms."

주: VO에서 재스캔은 DC-1(scan.submitted)로만 남는다. TM QA-XPG-01이 admin의 View Orders 스캔 경로에 대해 [DC-17] 영속을 단언하므로, VO 스펙대로 구현하면 이 시나리오는 실패한다.

### [C-51] MINOR — 정본(canonical) 크로스페이지 이벤트명 개수가 문서 간 다르다 — view-orders §5는 "9 groups covering 11 literal names", tracking-missing은 "the ten canonical cross-page names"로 서술한다.

- `view-orders.md`: "The canonical cross-page names — **9 groups covering 11 literal names** — must be byte-identical wherever they appear and are marked ⓒ"
- `tracking-missing.md`: "The ten canonical cross-page names fixed by `_global-rules.md` are used byte-identically here: `comment.posted`, `comment.mention_notified`, `comment.starred` / `comment.unstarred`, `comment.read` / `comment.mark_all_read`, `comment.auto_posted`."

주: _global-rules.md 실측(§Cross-page event names)은 9그룹/11리터럴로 VO §5와 일치. VO 자신의 CP-7에도 "The 10 canonical names"가 있어 '10'은 양쪽에 퍼진 오기로 보임 — byte-identity 감사 시 로스터 크기부터 어긋난다.

### [C-52] MINOR — M2b의 온스크린 계약이 약속하는 Slack 알림 필드(product name · barcode · qty · memo · 실패 주문번호)와 양쪽 §6.1/DC-4가 규정하는 실제 페이로드(tracking no. · product · qty · memo · registrant · suspected orders)가 불일치한다.

- `view-orders.md`: "**On-screen contract:** `On send, the #unrecognized-tracking channel gets an "Unrecognized product added" alert (product name · barcode · qty · memo · order number if lookup failed) → shown in the unrecognized pool on the Missing Tracking List page.`"
- `tracking-missing.md`: "`{channel: "#unrecognized-tracking", payload: {tracking_no, product, qty, memo, registrant, suspected_orders[]}, mentioned_pic_ids[] (deduplicated [BR-39]), truncated_candidate_count, message_ts, delivery: ok \| failed, error?}`"

주: 온스크린 문자열은 와이어프레임 byte-exact 인용이라 수정 주체가 와이어프레임 편집 패스인지 라우팅 표인지부터 판정 필요. barcode·carried order no.는 페이로드에 없고 tracking_no·suspected orders는 화면 문구에 없다.

### [C-53] MINOR — 같은 페이지가 사용자 문안에서 두 이름으로 불린다 — view-orders의 M2b 계열 문자열은 "Missing Tracking List (page)", tracking-missing의 페이지 아이덴티티는 "WMS - Unrecognized Tracking List"다.

- `view-orders.md`: "with a `Send to Missing Tracking List` button (`#unrecToSend`) that opens **M2b carrying the failed order number**."
- `tracking-missing.md`: "`<h2>`: `WMS - Unrecognized Tracking List` (hyphen-minus with single spaces, not an en dash)."

주: 둘 다 각자 와이어프레임의 byte-exact 인용이라 스펙 오류라기보다 코퍼스 명명 미정규화(허브 문자열 HUB-1~7처럼 canonical화된 적 없음). 운영자가 버튼 이름으로 페이지를 찾는 동선에서 혼선 소지.

### [C-54] MINOR — REMOVED 상태 풀 아이템의 허브 엔트리 클릭 타깃이 갈린다 — view-orders(및 tracking-missing §3.6)는 "row 또는 matched order" 2분기인데 tracking-missing QA-CMT-14는 REMOVED에 대해 "read-only historical view" 3분기를 요구하며, REMOVED 항목에는 matched order가 존재하지 않는다.

- `view-orders.md`: "Clicking a pool-item entry opens the tracking-missing page focused on that row, or the matched order if it was already resolved `[PD-67 · OWNER-PENDING]`."
- `tracking-missing.md`: "When it is clicked after the item reached `REMOVED`, Then a read-only historical view of the removed item opens — in no case is a dead link or a 404 produced `[E-31]`, `[E-60]`, `[BR-29]`, `[PD-67 · OWNER-PENDING]`."

주: 허브는 G-7상 8개 화면 공통 단일 컨트롤이므로 VO 화면의 허브에서 REMOVED 항목을 클릭하면 VO 계약상 행선지가 정의되지 않는다(매치드 오더 부재). TM 내부에서도 §3.6(2분기) vs QA-CMT-14(3분기)가 갈려 있어 정본 문장 확정 후 양쪽 동기 필요.

**대조 후 이상 없음:** 매칭 파이프라인 행동면 핵심: 라인 단위 매칭(TM BR-5 ↔ VO L-S1-Fb/M2), 매칭 후 같은 바코드 재스캔 정상 인식(VO BR-27 ↔ TM E-15/QA-XPG-01 — 이벤트 영속만 F9), 풀 등록 단일 진입점(TM BR-1 ↔ VO BR-48·M2b) — 서술 일치 · M2 실패 주문번호 캐리 계약: VO E-3/E-4(carried number 유무) ↔ TM L-1 col 2·E-2(표시 전용, 후보 계산 불개입, M1 카드 'Order no. {n}') — 일치 · 언리퀘스티드 인바운드 루트: TM L-S1-Fb 4단계(요청 생성→송장 입력→사유부 제거→재스캔 State 6) ↔ VO R-5/BR-48, 별도 등록 경로 기각 양쪽 동일 명기 · 자기멘션 억제(PD-16): VO BR-28 ↔ TM BR-28/DC-27/E-54 — 억제 규칙·코멘트는 여전히 게시 문구 동일(대상 null 문제는 F3에 한정) · #fulfillment-admin-comments 채널 ID C0BMGEWM5QA 및 매치 확정 라우트(코멘트 자동 게시 + @registrant) — 양쪽·정본 3자 일치 · Closing 'unknown order'와 이 풀의 분리: VO §6.1 'different, disjoint' ↔ TM BR-32/QA-XPG-05 — 일치 · 코멘트 허브 HUB-1~4 canonical 문자열: VO WF-VO-1 적용 ↔ TM WF-NEW-E 적용, 문자열 byte 동일(HUB-5/6/7 범위만 F7) · Slack 실패 비차단·재시도·데드레터(PD-4/BR-42), 서버 confirm 재검증(PD-6), 낙관적 버전 체크(PD-7), 단일 admin 역할(G-15/PD-1), 코멘트 append-only(PD-3) — 페어 간 일치 · M2b 입력 검증: 제품 autocomplete 강제(VO E-74 ↔ TM E-4 상호참조), qty 양의 정수(VO E-75 ↔ TM Qty ≥ 1) — 일치 · inbound/outbound 트래킹 네임스페이스 분리·충돌 시 inbound-request 우선(VO BR-45/E-8 ↔ TM BR-19/E-11/QA-VAL-04) — 모델 일치(네임스페이스 인테이크 캡처 배관만 F4) · 사진 캡처 영구 삭제(PD-63): VO BR-41 ↔ TM BR-13 — hold→deletion 체인 포함 일치

## WMS 2.0 마감 전 경계면 페어 감사 — view-orders.md ↔ order-detail.md. 양 스펙의 §1~§7·§9·§10 전문 및 임무 초점 QA 구간(VO §8.4/§8.8 M1, OD QA-INB/QA-OUT) 정독 후, 행별 Inbound/Cancel Inbound(M1·DC-11·PD-49·X-1), Outbound/Cancel Outbound, 상태 변경, 이벤트 계약, 상호 인용을 대조.

### [C-55] BLOCKER — 같은 물리 액션(주문 Outbound/Cancel Outbound)의 재고 원장 계약이 정반대다 — OD는 outbound·cancel-outbound마다 inventory.movement를 기록하도록 요구하지만 VO의 재고 이벤트(DC-39)에는 outbound 계열 origin이 아예 없고 VO의 Outbound/Cancel Outbound persist 목록에도 재고 이벤트가 없다.

- `order-detail.md`: "5. Persist `DC-21 inventory.movement` for the outbound deltas."
- `order-detail.md`: "| **DC-21** | `inventory.movement` | emitted by DC-10 / DC-11 / DC-19 / DC-20 | `sku`, `location` (when warehouse-kept), `delta` (signed), `movement_type` ∈ {`inbound`, `cancel_inbound_restock`, `outbound`, `cancel_outbound_reversal`}, `source_event_id`, `balance_after`"
- `view-orders.md`: "`origin` ∈ {full_inbound, partial_inbound, return_restock, cancel_inbound_restock, **cancel_inbound_remainder**}"
- `view-orders.md`: "When `Outbound` is clicked while enabled, Then `order.outbounded` persists with `trigger=manual` and the full SKU set, `order.status_changed` persists `processing → prepare shipment`, and State 3 renders in place with no reload."
- `order-detail.md`: "**And** `inventory.movement` rows persist with `movement_type=outbound` (`DC-21`)"

주: 라인별 inbound도 동일 구조: OD DC-10은 항상 DC-21(movement_type=inbound)을 동반하지만(QA-INB-6), VO DC-6 item.inbounded는 어떤 재고 이벤트도 동반하지 않는다(§5.2·DC-39 origin 열거에 고객주문 inbound 없음). OD E-90은 'JIT 라인은 inbound 시 카운트 증가, outbound 시 0 복귀'라고 명시 — VO 계약대로 구현하면 VO에서 출고한 주문은 재고가 차감되지 않아 화면별로 원장이 갈라진다. 공유 서버 전제(CP-1 '서버는 한 번의 reversal…')와 정면 충돌.

### [C-56] MAJOR — '절대 diverge 금지'로 선언된 Cancel Outbound 페어가 이벤트 계약에서 이미 divergent다 — 동일 이름 order.outbound_cancelled의 페이로드가 다르고(order_id 단독 vs lines[]+reason), VO는 canonical order.status_changed(reason=cancel_outbound/outbound)를 함께 남기지만 OD의 Outbound·Cancel Outbound persist 목록에는 status_changed가 없으며, VO E-56의 shipped/completed 거부 가드가 OD엔 없다.

- `view-orders.md`: "Order Detail carries the same `Cancel Outbound` with the same rollback semantics `[PD-26 · OWNER-PENDING]`; that control is specced on Order Detail, not here, but the two must never diverge."
- `view-orders.md`: "| **DC-12** | `order.outbound_cancelled` | order | `order_id` | (emits `[DC-9]`) |"
- `order-detail.md`: "| **DC-20** | `order.outbound_cancelled` | Cancel Outbound `[BR-19]` | `lines[]{sku, qty}`, `prepare-shipment → processing`, `reason` (optional) | Actor Log `CANCEL OUTBOUND` |"
- `view-orders.md`: "| **DC-9** ⓒ | `order.status_changed` | order | `order_id`, `reason` ∈ {outbound, cancel_outbound, external} | `processing → prepare shipment` / `prepare shipment → processing` |"
- `order-detail.md`: "Clicking it: confirm step → persist `DC-20 order.outbound_cancelled` (all SKUs/qty, prior status → `processing`, actor, ts, optional reason) + `DC-21` reversal movements → green toast `Outbound cancelled`"
- `view-orders.md`: "**E-56** | `Cancel Outbound` attempted on an order that has already shipped/completed | Rejected with a red toast naming the current status; no rollback `[PD-6 · OWNER-PENDING]`."

주: canonical 이벤트 order.status_changed 소비자는 VO발 출고/롤백 전이는 보지만 OD발 전이는 못 본다(OD DC-1은 source=detail-dropdown 전용, L-9 persist 목록에 DC-1 없음). 같은 이름의 order.outbound_cancelled가 화면에 따라 다른 스키마로 쌓이는 것도 데이터 레이어 충돌. OD의 outbounded 이후 footer에는 Cancel Outbound가 유일한데 shipped/completed로 넘어간 뒤의 거부 규칙은 OD에 부재.

### [C-57] MAJOR — VO v1.3(v21, 'owner review — M1 restock location')이 추가한 M1 위치 계약(BR-58·E-94·DC-11 restock_location, '위치 없는 재고 입고 금지')이 OD에 미반영된 드리프트다 — OD의 Cancel Inbound는 위치 입력·게이트 없이 전량 restock을 강제하고(DC-11에 위치 필드 없음, DC-21 location은 'when warehouse-kept'), X-1 선언문도 Yes/No+qty 두 컨트롤만 명시해 위치 계약을 누락한다.

- `view-orders.md`: "**Spec version:** 1.3 (owner review — M1 restock location)"
- `view-orders.md`: "**BR-58** | **Restocked stock never enters Inventory location-less.** M1 pre-fills the SKU's registered location (editable — an edit relocates the SKU, one location per SKU `[G-14]`); when the SKU has no registered location, a location is **required** and `Confirm` stays disabled until one is entered."
- `view-orders.md`: "**E-94** | M1 restock on a SKU with **no registered location** (JIT residual entering warehouse stock for the first time) | The location field renders empty with no default; `Confirm` stays **disabled** until a location is entered `[BR-58]`."
- `order-detail.md`: "**Cancel Inbound contract.** View Orders M1 and Inventory M4 expose a restock Yes/No + an editable Restock Qty; this page has neither and hard-codes `restock=true` on the full line qty."
- `order-detail.md`: "If the owner adopts the M1/M4 form here, `[L-2]` gains the two controls and `DC-11` gains `restock` (bool) + `restock_qty`; `[BR-49]` is deleted."
- `order-detail.md`: "| **DC-11** | `line_item.inbound_cancelled` | `[L-2]` Cancel Inbound | `line_id`, `sku`, `qty` (**always the full line qty**), `INBOUNDED → PENDING`, `restock=true` (**always — no Yes/No and no qty input on this page** `[BR-49]` `[X-1]`), `note` (free text, may be empty)"

주: 결과: 등록 위치가 없는 JIT 라인(=M1 스스로 명명한 대표 사용례)을 OD에서 Cancel Inbound하면 위치 없는 재고가 생성돼 VO BR-20/BR-58(owner 결정, 2026-08-03)의 불변식을 위반한다. X-1/CP-1의 선언 범위가 v21 이전 상태에 머물러 있어 '선언된 충돌'로도 커버되지 않음 — X-1 문구 갱신 + OD 측 위치 처리 방침(차단이든 위임이든) 명시 필요.

### [C-58] MAJOR — canonical 이벤트 order.status_changed의 저장 literal이 두 스펙에서 다르다 — VO는 페이로드·QA에서 공백형 `prepare shipment`를 지속하지만 OD는 하이픈형 `prepare-shipment`를 'verbatim' 계약으로 명시하고 X-9에서 VO도 하이픈 어휘를 쓴다고 단정한다.

- `view-orders.md`: "| **DC-9** ⓒ | `order.status_changed` | order | `order_id`, `reason` ∈ {outbound, cancel_outbound, external} | `processing → prepare shipment` / `prepare shipment → processing` |"
- `view-orders.md`: "When `Cancel Outbound` is confirmed, Then status persists `prepare shipment → processing`, **all line inbound states are unchanged**, and `order.outbound_cancelled` + `order.status_changed` persist."
- `order-detail.md`: "The eight strings above are the **stored values** — lowercase, hyphenated — and every event payload uses them verbatim (`DC-1 old_status → new_status`, `processing → prepare-shipment`)."
- `order-detail.md`: "this page and View Orders use `prepare-shipment` / `on-hold` / `processing` as the vocabulary"

주: VO는 BR-9/BR-12 상태 목록에선 하이픈형을 쓰면서 §3 본문·§5.2 DC-9·QA-S2-05/QA-S3-06/E-86의 지속값 서술에선 일관되게 공백형을 쓴다(VO 토스트 sub-line `Status: prepare shipment`는 OD의 value/label 매핑상 어느 레지스터에도 안 맞는 제3형). byte-identical을 요구하는 canonical 이벤트에서 두 QA 스위트가 서로 다른 literal을 단언 중 — 한쪽은 실서버 대비 반드시 실패한다.

### [C-59] MAJOR — 양쪽 모두 '공유 개념의 이벤트명 이원화는 정확히 5개'라고 선언(CP-7/X-8)하지만, 이 페어만 대조해도 선언 밖의 이원화가 최소 3개 더 있다 — cancel-inbound(item.inbound_cancelled vs line_item.inbound_cancelled), bulk 부모(item.bulk_inbound_batch vs line_item.bulk_inbound_submitted), 가드 차단 기록(order.mutation_rejected vs order.action_rejected).

- `view-orders.md`: "**Five shared concepts carry a different event name on every page** — idempotent duplicate suppressed, stock moved, comment search executed, Slack dispatch outcome, line received."
- `order-detail.md`: "**Below the canonical ten, five shared *concepts* carry a different name on each page** — idempotent duplicate suppressed (`action.idempotency_suppressed` here), stock moved (`inventory.movement` here), comment search executed (declared a **non**-event here, `NE-8`), Slack dispatch outcome (folded into `comment.mention_notified` here), line received (`line_item.inbounded` here)."
- `view-orders.md`: "| **DC-11** | `item.inbound_cancelled` | order line"
- `order-detail.md`: "| **DC-9** | `order.action_rejected` | any guard-blocked attempt `[BR-47]`"
- `view-orders.md`: "| **DC-44** | `order.mutation_rejected` | order / line | `attempted_action`, `reason` ∈ {on_hold, status_forbids_outbound, already_outbounded, line_locked_after_outbound, stale_version, no_lines, session_expired}"
- `view-orders.md`: "| **DC-7** | `item.bulk_inbound_batch` | order"
- `order-detail.md`: "| **DC-12** | `line_item.bulk_inbound_submitted` | `[L-2]` Bulk Inbound Selected Items"

주: 같은 물리 사실의 reason enum도 미매핑(예: 출고 후 라인취소 차단 — VO reason=line_locked_after_outbound vs OD reason_code=order_outbounded; stale — stale_version vs stale_entity). 매치 기입 페어(VO DC-41 unrecognized.tracking_matched vs OD DC-18 line_item.tracking_written)도 원장 미등재 이원화 후보. 이 원장의 존재 이유가 '교차 조인 시 매핑 누락 방지'인데, '5개' 완전성 주장 자체가 틀려 그 기능이 무너진다 — 양쪽 CP-7/X-8 목록 갱신 필요.

### [C-60] MINOR — 같은 사실(cancel-inbound 사유 메모)의 지속 경로가 다르다 — VO는 '메모는 이중 지속, 단일 귀속 금지'(DC-11.memo + DC-23 주문 코멘트)인데 OD의 note는 DC-11에만 남고 OD의 자동코멘트 origin enum에 cancel 사유가 없다.

- `view-orders.md`: "Memos are **dual-persisted, never single-homed**: M1's memo lands in `[DC-11].memo` **and** as a `[DC-23]` comment on the order"
- `order-detail.md`: "| **DC-32** | `comment.auto_posted` | system comment lands on this order | `comment_id`, `source=system`, `origin` ∈ {`unrecognized_match_confirmed`, `expected_qty_edit`}, `origin_ref`, `mentions[]`"

주: 어느 화면에서 취소했는지에 따라 주문 코멘트 스레드에 취소 사유가 보였다 안 보였다 한다. X-1 선언(컨트롤 유무)에 포함되지 않은 미선언 차이.

### [C-61] MINOR — 같은 주문의 '같은 로그'가 두 페이지에서 다른 계약을 갖는다 — 제목(Inbound / Outbound Log vs Inbound / Outbound Actor Log), 컬럼명(Worker·Memo vs Operator·Note), 동일 이벤트의 액션 문자열(INBOUND Cancelled (Restocked) vs CANCEL INBOUND (Restock)), 포함 이벤트 집합(VO는 HOLD Applied·Return Restock 표시, OD는 DC-10/11/12/19/20 쿼리로 한정)이 전부 다르고 어느 쪽도 이 차이를 선언하지 않는다.

- `view-orders.md`: "a table at the bottom of States 1, 1b, 2, 3, 4, 5 headed `Inbound / Outbound Log` with columns `Time · Action · SKU · Qty · Worker · Memo`, newest first. Action values seen in the wireframe: `INBOUND` (green), `OUTBOUND` (blue), `INBOUND Cancelled (Restocked)` (red), `Return Restock (Stock added)` (green), `HOLD Applied` (red)."
- `order-detail.md`: "Table (`.logtbl`) columns, in order: **Time · Action · SKU · Qty · Operator · Note**."
- `order-detail.md`: "It is a query over `DC-10`, `DC-11`, `DC-12`, `DC-19`, `DC-20`. If the log and the event store ever disagree, the event store is ground truth."
- `order-detail.md`: "| `DC-11` cancel inbound | `CANCEL INBOUND (Restock)` | the SKU | restocked qty | `.act-cancel` (red)"

주: 둘 다 '지속 이벤트 위의 뷰'라는 동일 독트린(G-8)을 선언하면서 같은 이벤트를 다른 문자열로 byte-단언(VO QA-M1-05 vs OD QA-INB-8)하고, VO 로그에는 CANCEL OUTBOUND 행 문법이 없다. 페이지별 뷰라 허용될 수 있으나 X-1~X-9/CP-1~CP-9 어디에도 선언돼 있지 않다.

### [C-62] MINOR — OD가 지속하는 도착 경로 `view_orders_row`('View Orders — order row click → order detail')의 상대편 어포던스가 VO 스펙에 존재하지 않는다 — VO의 크로스페이지 링크 표에 Order Detail행이 없고, VO에선 입력 밖 아무 클릭이나 검색창 재포커스로 정의된다.

- `order-detail.md`: "| View Orders — order row click | order detail for that order | `view_orders_row` |"
- `view-orders.md`: "**Trigger:** (a) any click anywhere on the page that is not inside another input, and (b) completion of any inbound/outbound/confirming action, and (c) closing any modal, and (d) completion of State 6b."

주: VO §6.2의 outbound 링크 목록(inbound-request·tracking-missing·order line만)과 §9.4 금지 목록 어디에도 행 클릭 → Order Detail 내비게이션이 없다. OD DC-34 enum이 유령 경로를 갖거나 VO에 미기재 어포던스가 있는 것 — 어느 쪽인지 한쪽에 명시 필요.

### [C-63] MINOR — 같은 액션의 성공 토스트 문구가 페이지별로 다른데(VO `✓ Inbound complete — {SKU}`/`✓ Outbound complete — Order {id}` vs OD `Inbounded — {SKU}`/`Outbound sent — {n} item(s)`), OD의 D-2는 토스트 문구의 '8화면 byte-identical'을 조건으로 걸어 자기모순을 만든다.

- `view-orders.md`: "the byte-exact strings this page uses are `✓ Inbound complete — {SKU}` with sub-line `No refresh · ready for the next scan`; `✓ Outbound complete — Order {id}` with `Status: prepare shipment`"
- `order-detail.md`: "| `[L-2]` per-row **Inbound** | `Inbounded — {SKU}` | red, names the rejection reason |"
- `order-detail.md`: "The success strings in §3.0.2 are the assertable contract; wording may change only if it stays byte-identical across all 8 screens"

주: 페이지별 토스트 레지스트리 자체는 허용 가능한 설계지만, D-2의 'byte-identical across all 8 screens' 절이 이미 성립 불가능한 전제(스펙끼리 이미 다름)를 담고 있다. D-2 문구를 페이지 스코프로 한정하거나 문구를 통일해야 함.

### [C-64] MINOR — VO CP-1이 order-detail에 요구한 잔여 수정('전량 restock을 §3에 명시하고 이유를 적을 것')은 OD L-2/BR-49로 이미 이행됐는데 CP-1은 미해결로 남아 있다 — 같은 표에서 CP-4는 RESOLVED로 마킹된 것과 비대칭.

- `view-orders.md`: "`order-detail` must either gain the Yes/No + qty controls or state in §3 that it always restocks the full line qty and why."
- `order-detail.md`: "**Cancel Inbound on this page always restocks the full line quantity** `[BR-49]` `[X-1]`. There is **no restock Yes/No choice and no Restock Qty input** on Order Detail — the symmetric counterpart of "per-line inbound is all-or-nothing" `[BR-41]`: a receipt taken in full is reversed in full."
- `view-orders.md`: "**CP-4** ✅ **RESOLVED 2026-08-03**"

주: 부기 드리프트. 단, F3(위치 계약 미반영)을 반영하면 CP-1을 단순 RESOLVED 처리하면 안 되고 위치 계약을 포함해 재기술해야 한다.

### [C-65] MINOR — 같은 기능(주문별 코멘트 컴포저)의 placeholder가 두 페이지에서 다른 문구로 같은 Slack 계약을 서술한다 — 허브 카피 이원화(CP-4/X-6)와 동일한 실패 계급인데 컴포저는 대상에서 빠져 있다.

- `view-orders.md`: "The composer placeholder is `Write a comment — @name sends an automatic Slack alert (order no · text · time · author)`."
- `order-detail.md`: "`Write a comment — @name to notify via Slack (order no. · text · time · author included). Per-order history accumulates here.`"

주: 어느 스펙도 컴포저 카피를 크로스페이지 계약으로 선언하지 않아 규범 위반은 아니다. CP-4의 교훈('각자 자기 스펙만 읽는 동안 이원화는 보이지 않았다') 적용 후보로 보고.

### [C-66] MINOR — VO의 M1 QA 시나리오 ID가 v21 개정에서 충돌했다 — QA-M1-06과 QA-M1-07이 각각 두 번 존재한다(신규 [WF] BR-58 / [ADMIN] E-94 쌍이 기존 [ADMIN] E-26 / E-27 쌍과 같은 번호).

- `view-orders.md`: "**QA-M1-06 [WF]** `[L-M1]` `[BR-58]`"
- `view-orders.md`: "**QA-M1-06 [ADMIN]** `[E-26]` — *negative*"
- `view-orders.md`: "**QA-M1-07 [ADMIN]** `[E-94]` `[BR-58]` — *negative*"
- `view-orders.md`: "**QA-M1-07 [ADMIN]** `[E-27]` `[BR-57]` `[DC-39]` `[PD-49 · OWNER-PENDING]`"

주: 단일 문서(view-orders.md §8.8) 내 결함이라 페어 임무 범위 밖이지만, 임무 초점인 M1 v21 개정부에서 발견돼 보고한다. ID 불변 규칙상 재번호가 아니라 신규 항목에 새 번호(QA-M1-10/11 등) 부여가 필요 — wf-minor-fixes 라우팅 후보.

**대조 후 이상 없음:** 자동 아웃바운드 경계 — VO BR-6('Order Detail never auto-outbounds') ↔ OD BR-5/C-7/QA-OUT-6 완전 일치 · 출고 후 행별 Cancel Inbound 잠금 — VO BR-10/L-S3-4/E-55 ↔ OD BR-14/E-10/QA-INB-10, 차단 사유 문구 `Cancel Outbound first`까지 일치(단 거부 이벤트명·reason 값 차이는 finding 5에 귀속) · Outbound enable predicate — VO BR-9 ↔ OD BR-1/L-9: 조건 동치(≥1 line·전 라인 INBOUNDED·status∈{processing,pending}), 차단 status 6종 집합 일치, 0-line 주문 출고 불가(VO E-60 ↔ OD E-55) 일치 · 상태 어휘 — 8-status 집합·`returned` 없음·`cancelled`는 상태 아닌 플래그(VO BR-12/CP-5 ↔ OD BR-12/L-8/X-3) 일치(literal 표기형 문제만 finding 4) · 라인 상태기계 — PENDING↔INBOUNDED 2값 배타·OUTBOUNDED 부재·Cancel Outbound의 라인 상태 불간섭(VO L-S1b-21/BR-11/CP-2 ↔ OD BR-50/L-10/X-4) 일치 · Hold 의미론 — hold 중 Inbound 허용·Outbound 차단(UI+서버), hold 사유 optional free text를 배너에 verbatim 렌더(VO BR-7/L-S5-1~3/PD-20 ↔ OD BR-2/BR-24/L-14/DC-2) 일치 · Hold 오리진 — VO L-S5-F/CP-6 'OMS/Order Detail(Change Status → on-hold)만' ↔ OD L-8/DC-2·DC-3 소유 구조 일치, VO에 hold 적용/해제 어포던스 부재 상호 확인 · Comments hub — HUB-1~7 카피 7종 byte 대조 완료, 양쪽 동일(CP-4 ↔ X-6 해소 기록도 상호 일치), 배지=미읽음 멘션 수 의미론 일치 · Slack 라우팅 — 채널 #fulfillment-admin-comments(C0BMGEWM5QA)·페이로드 필드·멘션 본문 @ 방식·비라우트 목록(outbound/cancel/print 등 v1 무알림)·실패 시 비차단+지속·재시도(VO §6.1/BR-42 ↔ OD §6.1/BR-38) 일치 · 언인식 매치 파이프라인 — 매치가 주문 라인에 tracking 기입, 재스캔 정상 해석, 단일 파이프라인 자동코멘트+Slack, resolver==registrant 억제(VO BR-27/BR-28/DC-41 ↔ OD BR-35/§5.3/DC-18·DC-32) 흐름 일치(이벤트명 이원화만 finding 5에 귀속) · 부분 배치 의미론 — 부분 실패는 partial로 보고·성공 라인 비롤백·실패 라인 명시(VO BR-55/E-72 ↔ OD E-73/QA-INB-16), 이미 INBOUNDED 라인 멱등 스킵 일치 · PD-49 잔여 조정 — OD는 전량 restock이라 remainder가 구조적으로 발생하지 않아 VO BR-57/E-27의 ADJUST(−remainder) 계약과 충돌 없음(컨트롤 유무 차이는 X-1/CP-1로 선언됨)

## 전역규칙 준수 감사 — stock-status.md vs _global-rules.md (기준선 review-baseline-20260803). 양 문서 전문 정독 + HUB 문자열·글리프 코드포인트 바이트 검증 수행.

### [C-67] MAJOR — [L-M4]는 사유(reason) 필드를 가진 파괴적 액션인데 스펙이 사유를 선택 사항으로 만들고, PD-5 규칙을 재서술하면서 G-2의 'plus a reason' 요소를 누락했다 — CONFIRMED 전역규칙과의 미신고 델타.

- `specs/_global-rules.md`: "**Every removal/deletion-class (destructive) action takes a confirm dialog, plus a reason where the flow already carries a reason field, plus the toast.** **CONFIRMED 2026-08-03 (owner, PD-5).**"
- `specs/stock-status.md`: "**Step 4 — Memo (optional).** Textarea, placeholder `Cancellation reason or notes — if written, also recorded in the order's Comments history`."
- `specs/stock-status.md`: "Destructive action → confirm step + toast, both mandatory `[PD-5 · OWNER-PENDING]`."

주: §3.16은 스스로 'The most destructive action available on this page'라 선언하고, 플로우에 사유 필드(메모, placeholder가 'Cancellation reason'으로 시작)가 이미 존재한다 — G-2의 'a reason where the flow already carries a reason field' 조건에 정확히 해당한다. 그런데 'An empty memo produces **no** comment'로 빈 사유를 허용하고, 가드 문장은 규칙을 'confirm step + toast, both mandatory' 2요소로 재서술해 사유 요소를 떨어뜨렸다. G-2를 '기존 사유 필드를 활용하라(신설 불요)'로 읽는 대안 해석도 가능하나, 그 경우에도 델타 선언 없이 재서술로 요소를 누락한 것은 계약 위반이다.

### [C-68] MAJOR — §3 전문(preamble)이 G-9의 동시편집 규칙 본문을 재서술하면서 '+ non-green toast'를 누락하고 counting-flow 예외의 범위 한정('State 6 receive, closing scans')을 삭제해, 이 페이지의 감사 카운팅이 서버 머지 대상인 것처럼 읽히게 만든다 — 같은 스펙의 단일 세션 차단 설계(E-23/BR-14)와 충돌.

- `specs/_global-rules.md`: "**Concurrent edits** by two operators resolve by optimistic version check → 409 → reload the row + non-green toast; counting flows (State 6 receive, closing scans) merge server-side instead. **CONFIRMED 2026-08-03 (owner, PD-7).**"
- `specs/stock-status.md`: "concurrent edits resolve by optimistic version check → 409 → reload the row, except counting flows which merge server-side `[PD-7 · OWNER-PENDING]`."
- `specs/stock-status.md`: "**Two auditors start an audit simultaneously** | The second is blocked: `Stock audit already in progress — started {HH:MM} by {auditor}`. Exactly one active session per warehouse"

주: _global-rules.md 서두의 계약('Screen specs cite these by ID (`[G-n]`) and describe **page deltas only** — they never restate a rule body')을 정면 위반하는 상이한 재서술. G-9는 머지 대상 counting flow를 State 6 receive·closing scans로 한정하는데, 스펙 전문은 한정 없이 'counting flows ... merge server-side'라고 써서 이 페이지 유일의 counting flow(재고 감사)가 머지되는 듯 읽힌다 — 실제 이 페이지는 BR-14/E-23으로 동시 감사를 차단하고 PD-6 재계산으로 처리한다. §3.8/E-7은 non-green toast를 복원하지만 전문의 재서술 자체가 표류했다.

### [C-69] MINOR — 전역규칙이 PD-4로 CONFIRMED한 재시도 방식(자동 재발송 + exponential backoff, 개발자 결정은 N뿐)을 스펙이 'Retry policy is a developer decision'으로 통째로 개발자 위임해 확정 범위를 잘못 넓혔다.

- `specs/_global-rules.md`: "the failure is queued in a background retry queue and re-sent automatically with exponential backoff. Every dispatch result is persisted [G-8]. An item still undelivered after N retries (N = developer decision) is flagged in the admin notification log. No dedicated queue screen in v1. **CONFIRMED 2026-08-03 (owner, PD-4).**"
- `specs/stock-status.md`: "Delivery failures are persisted (`[DC-12]` with `result = failed`) and retried. **A failed notification never blocks or rolls back the primary action, and never rolls anything back** `[PD-4 · OWNER-PENDING]` `[E-65]`. An `@mention` naming someone who is not in the workspace resolves to `result = failed`, reason `unknown_user`; the comment still posts `[E-88]`. Retry policy is a developer decision."
- `specs/stock-status.md`: "| Slack | Retry policy for failed deliveries `[PD-4 · OWNER-PENDING]`; whether an audit-confirmed notification is ever added"

주: 전역규칙에서 개발자 결정으로 남은 것은 재시도 횟수 N뿐이고 exponential backoff·admin-log 플래그는 오너 확정 사항이다. §6.1·§9.2 두 곳 모두 '재시도 정책' 전체를 개발자 결정으로 재서술해, 고정 간격 재시도 구현도 스펙 준수로 읽힐 여지를 만든다. (인용 중 §6.1 문장은 원문이 'never blocks or rolls back the primary action, and never rolls anything back'이 아니라 'never blocks the release, the audit confirm, or any other primary action, and never rolls anything back'임 — 요지는 동일.)

### [C-70] MINOR — 오너 확정된 PD-1·PD-3·PD-4에 대응하는 BR-28·BR-23·BR-30의 Decided 컬럼이 여전히 'Provisional 2026-08-03'로 남아 있다 — 헤더 면책 문구는 '태그(tags)'만 명시적으로 커버하므로 이 산문 셀들은 옛 상태 서술로 남는다.

- `specs/_global-rules.md`: "PD-1 through PD-8, 51, 55, 66, 71, 74, 79 were owner-decided on 2026-08-03 — their register entries carry the ruling."
- `specs/stock-status.md`: "| **BR-23** | **This page adds no comment edit or delete affordance**, in the hub or anywhere else. `[G-7]` `[PD-3 · OWNER-PENDING]` | The comment corpus is an audit and AI-training asset; a per-page mutation path would silently rewrite it. | Provisional 2026-08-03 |"
- `specs/stock-status.md`: "any inline `[PD-{these} · OWNER-PENDING]` or `[PD-{these} · NO-DEFAULT]` tags below are superseded — see `_provisional-decisions.md` for the decisions."

주: BR-28('Provisional 2026-08-03', PD-1)·BR-30('Provisional 2026-08-03', PD-4)도 동일. 인라인 [PD-n · OWNER-PENDING] 태그 잔존 자체는 헤더 면책으로 의도된 장치라 결함으로 세지 않았으나, Decided 컬럼의 'Provisional'은 태그가 아닌 본문 산문이며 규칙의 현재 지위 서술로 읽힌다. §10 결정 로그의 'Global rule (provisional)' 행들은 이력 서술이라 제외.

### [C-71] MINOR — 0행 익스포트 성공 시 'non-green toast'를 지정한 §3.20 델타가 G-2의 'Green for success, red for failure' 본문과 충돌한다(익스포트는 성공했는데 초록이 아님).

- `specs/_global-rules.md`: "**Every confirming action** — register, confirm, cancel, send, save, remove/delete — shows a top-right toast stating what happened. Green for success, red for failure."
- `specs/stock-status.md`: "Zero rows → the export is still produced with headers only, plus a non-green toast `Exported 0 rows`."

주: G-9가 409 경로에 'non-green toast'를 도입하므로 제3색 자체는 전역 어휘에 존재하지만, 그것은 실패성 결과에 대한 것이다. 0행 익스포트는 파일이 생산된 성공 케이스인데 스펙 자신의 QA-GLB-01('both Exports ... green on success and red on failure')과도 어긋난다. 델타 선언('page delta on [G-2]') 없이 도입된 제3색이라는 점이 문제의 핵심.

**대조 후 이상 없음:** [G-7] 허브 캐논 문자열 HUB-1~HUB-7 — 스크립트로 바이트 대조, 7종 전부 두 문서에서 byte-identical (§3.12·QA-COM-02/04/05, HUB-5의 {n} 치환형 '1/0/2 results' 렌더 포함). 로컬 변형 없음 · §3.18 글리프 계약의 사실 주장 — 코드포인트 실측으로 검증: _global-rules.md [G-3]는 실제 U+2212 MINUS SIGN('− Record Outbound'), 스펙 버튼은 U+FF0B/U+FF0D 전각. 스펙 주장이 정확하며 §10 D12에서 갚아야 할 조정으로 선언됨(은닉 아님) · [G-3] 오디오 스코프 — − Record Outbound에만 send sound(§3.19·§6.5·QA-FRM-11), ＋ Record Inbound 무음(QA-FRM-12), TTS는 Closing 전용, 경고음은 VO State 6 델타라는 서술 모두 G-3 (a)(b)(c)와 일치 · [G-4] 프린트 — G-4의 print surface 목록에 Inventory 부재 ↔ BR-27/§6.4/E-98/QA-NAV-06의 '프린트 없음' 부정 단언 정합. print.job_result 미발행 선언도 일치 · [G-5] 소싱 루트 — 무색 검정 볼드(QA-CS-08), JIT (채널) 괄호형, OTHER (channel) [PD-80] 태그 상태(전역에서도 여전히 OWNER-PENDING) 일치. 필터의 OTHER 6번째 옵션은 페이지 델타로 적법 선언 · [G-6] 네이밍 — KR명 EN 브랜드 볼드, '— (신규)' 데이터 문자열 유지, QA-GLB-09 한글 allow-list 구성 모두 정합 · [G-7] 나머지 — append-only(BR-23·QA-COM-10), 채널 #fulfillment-admin-comments(C0BMGEWM5QA), 페이로드 필드, 엔티티 유형(order/inbound request/pool item) 정합 · [G-8] — 34 DC/13 NE 선언 구조, views-over-events 독트린, BR-26 리젝션 퍼시스트(전역 본문의 'operator-initiated must persist'와 양립) 정합 · [G-1] — 'View Orders (all states), Closing' 스코프 ↔ §1.1A·§9.1 #11·QA-GLB-08의 비스캔면 선언 정합 · [G-9] 멱등성 자체 — 더블클릭 1효과, client debounce + server key 서술(QA-GLB-03 등) 정합 (동시편집 재서술 결함은 별도 등재) · [G-10]/[G-11] — 트래킹 네임스페이스 분리·일치 가능(E-63), PENDING 확정의 VO State 6/IR 전속(BR-18), 예상수량 편집 VO M6 전속 정합 · [G-12]/[G-13]/[G-14]/[G-15] — 딥링크 실링크, 샘플 UI 부재(QA-NAV-08), 감사전용 UI 세트·동적 라인 리스트(BR-5/BR-6은 DOM 바인딩+파스 규칙의 적법 델타), 단일 롤·게이트 무추가(BR-28) 정합

## 전역규칙 준수 감사 — closing.md vs _global-rules.md (기준선 review-baseline-20260803)

### [C-72] MAJOR — closing.md 헤더는 [WF-15]를 현재형으로 'remains open'이라 서술하지만, _global-rules.md [G-7] v1.2는 8개 와이어프레임·8개 QA 스위트가 동일 커밋에서 canonical로 이동 완료됐다고 CONFIRMED로 못박았고, closing.md 자신의 §2.3/§3.8도 fixed로 기록해 헤더가 옛 상태로 남아 있다 (§10 로그의 '적용 안 함'과 §2.3의 '6건 배치 적용' 귀속도 상호 모순).

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "**`[WF-4]` `[WF-5]` `[WF-7]` `[WF-8]` `[WF-12]` were applied to the wireframe on 2026-08-03** (owner-approved batch — §2.3); `[WF-15]` remains open (corpus-wide `[G-7]` fix)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "**[G-7] publishes the seven canonical hub strings** (HUB-1…HUB-7) as byte-exact cross-page contract, closing cross-page defect M3a D7. All eight wireframes and all eight spec QA suites were moved to these values in the same commit."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "`[WF-15]` **(fixed 2026-08-03)** Comments hub pane headers and the unstar hint diverged from the cross-page `[G-7]` contract"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "`[WF-15]` deliberately **not** applied (corpus-wide `[G-7]` precondition, §2.3)"

주: §2.3는 'The six `(fixed 2026-08-03)` rows were applied to `wms2/closing/index.html` in the owner-approved wireframe-edit batch'라 6건(WF-15 포함)을 배치에 귀속시키고, §3.8은 WF-15가 [G-7] v1.2와 '같은 커밋'에서 적용됐다 하고, §10은 그 배치에서 '적용 안 함'이라 한다. 현재 규범 상태(전역규칙 CONFIRMED)는 fixed이므로 헤더 line 9와 §10 서술이 stale.

### [C-73] MAJOR — closing.md §3.21/§6.6은 PD-2(송신음 스코프)를 여전히 '오너가 해소해야 할 열린 긴장'으로 서술하고 reversal-impact 절까지 유지하지만, _global-rules.md [G-3a]는 PD-2를 owner CONFIRMED로 종결했다 — 게다가 확정된 규칙의 열거에는 closing M1 버튼이 여전히 빠져 있어 스펙의 'by class 적용'과 규칙 열거가 형식상 어긋난 채 남았다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "Note the tension the owner is being asked to resolve: PD-2's enumeration names View Orders, RTO, Order Detail and Inventory and does **not** name closing, while adjudication C-5's verdict is scope-by-button-class ("every outbound-class button on every page"), which does reach this button. This spec applies the rule by class. Reversal impact if the owner scopes PD-2 by page instead: delete this clause"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "(a) **Send sound** — outbound-class buttons play a short synthesized rising sweep (Web Audio, no external files). Scope: every outbound-class button on every page — View Orders (Outbound, Inbound + Outbound, bulk), RTO (Bulk Outbound), Order Detail (Outbound), Inventory (− Record Outbound). **CONFIRMED 2026-08-03 (owner, PD-2).**"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "`[G-3a]` send sound | **Yes — one button only**: M1's `[Process Outbound → resolve warning]`, as an outbound-class button `[PD-2 · OWNER-PENDING]`. PD-2's page enumeration does not name closing; adjudication C-5's button-class scope does."

주: 행동 자체(클래스 스코프로 M1에 사운드 적용)는 확정 규칙의 헤드라인 스코프와 일치. 결함은 (1) 이미 판결난 사안을 '오너 대기'로 계속 서술하는 stale 내러티브, (2) 확정 규칙의 열거가 closing M1을 명기하지 않아 [G-3a]만 읽는 구현자는 반대 결론에 도달할 수 있다는 잔여 모호성. 헤더의 PD 태그 일괄 supersession은 태그만 커버하고 이 산문은 커버하지 못한다.

### [C-74] MINOR — closing.md §6.1은 Slack 재전송을 통째로 'Retry policy is a developer decision'으로 위임하지만, 전역규칙(PD-4 CONFIRMED)은 백그라운드 재시도 큐 + 지수 백오프 자동 재전송 + N회 초과 시 admin 로그 플래그를 규칙으로 고정하고 N만 개발자 결정으로 남긴다 — 확정 규칙 본문을 다르게 재서술한 계약 위반.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "A failed Slack dispatch is persisted (DC-17 with `delivery_status=failure`) and retried; it never blocks the UI and never rolls anything back. Retry policy is a developer decision."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "the failure is queued in a background retry queue and re-sent automatically with exponential backoff. Every dispatch result is persisted [G-8]. An item still undelivered after N retries (N = developer decision) is flagged in the admin notification log."

### [C-75] MINOR — closing.md QA-HUB-09는 검색결과 헤더(HUB-5)를 '결과가 있는 검색'에 조건화해 서술하지만, [G-7]의 reading rule은 0건 검색에서도 헤더가 항상 렌더되고 HUB-6이 별도 노드로 뒤따른다고 규정한다 — 이 QA 문구대로면 0건 시 헤더를 생략한 구현도 통과한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "And a search returning results renders the header "{n} results · newest first · click to open the order", while a search with no match renders exactly "No matching comments""
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "`{n}` in HUB-5 is a count substituted at render time, never a literal — a zero-hit search still renders the header, followed by HUB-6 as a separate node."

### [C-76] MINOR — [G-7] v1.2는 canonical 문자열을 7종(HUB-7 포함)으로 발행하고 '8개 스펙 QA 스위트가 모두 이 값으로 이동했다'고 주장하지만, closing.md의 유일한 hub-copy ADMIN 시나리오 QA-HUB-09는 HUB-1…HUB-6만 단언하고 HUB-7(검색 placeholder)은 스펙 QA 어디에서도 단언되지 않는다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "**QA-HUB-09 `[ADMIN]`** — the hub carries the canonical cross-page copy `[G-7]` HUB-1…HUB-6 `[WF-15]`"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "HUB-7 (search placeholder) is one beyond the six the register enumerated — same component, same defect class, unambiguous 4/5 majority."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "A page may not introduce a local variant of any of the seven."

주: §3.8 표에는 HUB-7이 포함돼 있어 문자열 자체는 스펙에 존재. 결손은 QA 단언 커버리지뿐.

### [C-77] MINOR — closing.md §3.8은 M3a-D7이 pane header에서 'closing과 inbound-request 두 페이지'를 outlier로 찾았다고 서술하지만, [G-7]의 corpus basis는 HUB-1/HUB-2 majority가 5/8(OD·RTO·INV·OM·TM)이라 비-majority 페이지는 VO를 포함한 3개다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "Cross-page defect M3a-D7 found closing and inbound-request to be the two outliers on the pane headers."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "| **HUB-1** | `@ Mentions` pane header | `Comments mentioning me · Click to open the order` | **majority 5/8** (OD · RTO · INV · OM · TM) |"

주: 8페이지 − majority 5 = VO·CL·IR 3개가 비-majority. VO가 pane header에서 majority였다면 corpus basis는 6/8이어야 한다.

### [C-78] MINOR — Amend 플로우가 [G-2] CONFIRMED 의무 두 건을 비껴간다: `closing.startAmend` 성공(CONFIRMED→AMENDING 상태 변경, DC-26 영속)은 확인성 액션인데 토스트가 정의돼 있지 않고(앰버 배너만), `[✕ Exit amendment]`는 작업 변경분을 폐기하는 파괴성 액션인데 confirm 다이얼로그가 정의돼 있지 않다(같은 페이지의 Cancel Closing은 0스캔에도 항상 묻는다).

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "**On `[Amend — open the closing]`.** `closing.startAmend(session_id, idempotency_key)` [G-9] → the `[BR-41]` guard is evaluated server-side; on pass, `CONFIRMED → AMENDING`, DC-26 persisted, and the screen enters amendment mode (§3.24) with no page refresh [G-2]."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "An explicit exit discards the working changes from the record, retains any added scan rows in the audit log [G-8], returns the session to `CONFIRMED` v{n}, and persists DC-29 (E-81)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "**Every confirming action** — register, confirm, cancel, send, save, remove/delete — shows a top-right toast stating what happened."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "**Every removal/deletion-class (destructive) action takes a confirm dialog, plus a reason where the flow already carries a reason field, plus the toast.** **CONFIRMED 2026-08-03 (owner, PD-5).**"

주: 분류는 논쟁 여지 있음: startAmend는 M3 다이얼로그를 통과하고 DC-29는 토스트를 갖는다(진입=다이얼로그만/토스트 없음, 이탈=토스트만/다이얼로그 없음의 비대칭). QA-AMEND-05([WF])는 Exit 클릭 즉시 복원을 단언해 다이얼로그 부재가 데모 한계가 아니라 스펙 의도로 읽힌다. 델타로 의도했다면 명시적 델타 선언이 없다.

### [C-79] MINOR — closing.md §6.3/QA-HIST-11은 딥링크 URL의 '디렉토리 형식 `../{slug}/#{anchor}`'이 [G-12]에 의해 고정됐다고 주장하지만, [G-12] 본문은 링크의 실재성만 규정하고 형식은 예시 하나로만 보여줄 뿐 canonical 형식을 규정하지 않는다 — 인용이 규칙이 말하지 않는 내용을 주장(사냥 대상 3).

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "Wireframe path `../order-detail/#{order_id}` — the **directory form** `../{slug}/#{anchor}` fixed by `[G-12]`, never `../order-detail/index.html#…` (cross-page defect M3a-D16, normalized 2026-08-03)"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "Cross-page references are real links, not decoration — e.g. View Orders State 6 banner → `../inbound-request/#reqlist` opens the Request List tab."

주: 형식 규범 자체는 M3a-D16 정규화의 산물로 8페이지가 공유하는 듯하나, 그 규범의 소재지가 [G-12] 본문이 아니므로 'fixed by [G-12]' 귀속은 부정확. [G-12]에 형식 문장을 추가하거나 인용을 M3a-D16으로 돌리는 편이 정확하다.

### [C-80] MINOR — closing.md는 전역규칙 본문을 두 곳에서 재서술한다(§5 서두가 [G-8]의 'actor · timestamp · entity · old→new · quantity' 독트린 문장을, §3.13 clause 10이 [G-1]의 3불변을 그대로 반복) — 현재는 의미 드리프트가 없으나 '스펙은 델타만 서술하고 규칙 본문을 재서술하지 않는다'는 전역 계약 위반이라 향후 드리프트 위험이 있다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "Doctrine [G-8]: every operator-initiated action persists **actor · timestamp · entity · old value → new value · quantity**."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md`: "**Continuous scanning** — the page-local expression of [G-1]: the scanner's automatic Enter substitutes for the Scan button, the cursor returns to the scan input with the text fully selected, the next scan overwrites it, and the page never refreshes between scans."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "Screen specs cite these by ID (`[G-n]`) and describe **page deltas only** — they never restate a rule body."

주: §3.13은 와이어프레임 legend footer(페이지 산출물)를 규범으로 선언하는 맥락이라 완화 사유가 있음. 내용 모순은 없어 MINOR.

**대조 후 이상 없음:** [G-1] 스캐너 프로토콜 — closing 델타(시작 전 disable, 확정 후 disable [PD-73])는 '델타는 추가만 가능, 3불변 제거 금지' 계약 내이며 §3.2가 '3불변 무손상'을 명시 · [G-2] no-refresh·토스트 커버리지 — start/confirm/cancel/target edit/M1/M2/re-confirm/amend-cancel 전부 토스트+무리프레시 명시 (Amend 진입 토스트·이탈 다이얼로그 2건만 별도 지적) · [G-2] PD-5 reason 조항 — M2 삭제의 'no reason field'는 'reason 필드를 이미 가진 플로우에서만 reason'이라는 규칙 조건과 무충돌 · [G-4]/[PD-68] — closing은 CSV-only·print 비표면, 양쪽 문서 모두 PD-68을 pending으로 유지해 일치 (§3.18, §6.5, E-49, BR-24, §9.1) · [G-7] HUB-1…HUB-7 문자열 — closing §3.8 표의 7종 canonical 문자열이 전역규칙과 바이트 일치 (·, —, 이모지 포함) · [G-7] 코멘트 대상 엔티티 — 'closing 세션은 commentable 아님'은 전역 목록(orders/inbound requests/pool items)과 무충돌; @mention 채널 ID(C0BMGEWM5QA)·payload 필드 일치 · [G-8] 이벤트 레지스터·NON-event 선언 — §5.1~§5.4 전부 독트린 계약 내; print.job_result·product.barcode_registered NON-event 선언은 허용 델타 · [G-9]/[PD-7] — BR-30의 counting=server merge / single-value=optimistic 409 분리가 전역규칙과 일치 · [G-10]/[PD-8] — 인바운드/아웃바운드 트래킹 네임스페이스 분리와 closing의 outbound-only 매칭(§3.6, E-13)이 일치 · [G-12] 링크 실재성 — Order ID 실링크·새 탭 델타·'inbound-request 딥링크 없음' 선언 모두 무충돌 (형식 귀속 건만 별도 지적) · [G-13]/[G-14]/[G-15]/[G-5]/[G-6]/[G-11] — closing의 아웃오브스코프 처리·단일 롤·샘플 비표면 선언이 전역규칙과 일치 · Cross-page event names — §5.1의 order.status_changed / order.outbounded / comment.* 가 전역 canonical 목록과 바이트 일치

## 전역규칙 준수 감사 — order-management.md vs _global-rules.md (모순 사냥)

### [C-81] MAJOR — §1.3이 [G-13] 듀얼뷰의 존재 이유를 '피커에게 어떤 샘플을 몇 개인지 알려줘야 한다'로 서술하는데, 이는 G-13이 PD-51 확정으로 명시적으로 폐기(supersede)한 옛 요구사항을 현재 규범 근거로 주장하는 것이다 (§10 결정로그 2026-08-03 행에도 동일한 폐기된 문구가 반전 기록 없이 잔존).

- `order-management.md`: "the sample dual-view rule `[G-13]` exists because the picker must be told *which* sample and *how many*, while the carrier-facing data must not be told (tax handling). That asymmetry is decided here, on this screen, by an operator who will never see its consequence. It is therefore written down in full (BR-8)"
- `_global-rules.md`: "**v1 makes no sample distinction** — internal invoices and picking labels also render **"sample set" only**: no sample type, no per-type quantity."
- `_global-rules.md`: "**CONFIRMED 2026-08-03 (owner, PD-51)** — this supersedes the earlier "which sample and how many" internal-artifact requirement"
- `order-management.md`: "internal invoice and picking artifacts show which sample and how many | BR-8, `[G-13]` |"

주: 스펙 자신의 규범부(BR-8, §3.6.4, §3.6.5, E-34, QA-SMP-46)는 전부 PD-51 개정본과 일치하게 갱신됨 — §1.3(목적 서사)과 §10 로그 행(2026-08-03 'Sample dual-view confirmed')만 옛 상태로 남았다. §1.3은 이력 표기 없이 현재형으로 서술되고 'written down in full (BR-8)'이라며 정반대 내용의 BR-8을 가리키므로 의도된 이력 서술로 볼 수 없음. §10 로그에는 PD-51 판결을 기록한 후속 행이 없어(R-1~R-3 같은 반전 체인 부재) 'Nothing recorded here may be silently dropped' 원칙상 함정.

### [C-82] MINOR — Slack 실패 재발송 정책: 전역규칙(PD-4 확정)은 '지수 백오프로 자동 재발송, N만 개발자 결정'으로 고정했는데 스펙은 두 곳에서 '재시도 정책 전체가 개발자 결정'이라고 더 넓게 재서술한다 (계약상 델타만 서술해야 하는 규칙 본문의 상이한 재서술).

- `_global-rules.md`: "the failure is queued in a background retry queue and re-sent automatically with exponential backoff. Every dispatch result is persisted [G-8]. An item still undelivered after N retries (N = developer decision) is flagged in the admin notification log."
- `order-management.md`: "Delivery failures are retried and persisted as `[DC-20]` with the failure outcome; they never block the comment or roll it back (BR-24, `[PD-4 · OWNER-PENDING]`). Retry policy is a developer decision."
- `order-management.md`: "retry policy is a §9.3 developer decision)."

주: 전역규칙은 백오프 형태(지수)와 자동 재발송을 오너 확정했고 개발자 재량은 N뿐이다. 스펙의 'Retry policy is a developer decision'(§6.1, E-50)과 QA-CMT-24의 '§9.3 developer decision' 주장은 개발자에게 확정 사항까지 재량으로 넘긴다. 게다가 §9.3 위임 표에는 Slack retry 항목 자체가 없어 §9.3 참조도 공허하다.

### [C-83] MINOR — G-5 라우트 렌더링 소비자 목록과 스펙 주장의 상호 모순: 스펙은 이 페이지의 주문 테이블이 [G-5] 소싱 라우트를 렌더한다고 주장하지만 G-5의 소비자 열거에 Order Management가 없고, 동시에 스펙 §6.6/§6.7은 'JIT는 이 화면에 전혀 나타나지 않는다'고 단언하는데 G-5상 JIT는 주문 측에서 발생하는 4개 주문-facing 배지 중 하나라 라우트 배지가 렌더되는 테이블에는 JIT 배지가 나타날 수 있다.

- `_global-rules.md`: "All route labels render as **colorless black bold text**, never colored pills. Route origin = Inbound Request; consumers = View Orders badges, Inventory, Order Detail."
- `_global-rules.md`: "JIT is never a requestable inbound route — it arises order-side."
- `order-management.md`: "sourcing-route rendering (`[G-5]`), pagination (`.pager`), and the `2,818 orders` count semantics."
- `order-management.md`: "**JIT** appears nowhere on this screen. No JIT sourcing route is selectable here, no residual-stock figure is computed, displayed, filtered, exported or reported here, and none may be added."
- `order-management.md`: "The only route rendering this page sees at all is inside the unchanged order table"

주: 두 갈래: (a) G-5 소비자 열거(VO·Inventory·Order Detail)에 이 페이지가 없는데 스펙 §3.9.1·§6.6은 이 페이지 테이블에서 G-5 렌더링이 일어난다고 주장 — 어느 쪽이든 한쪽 수정 필요. (b) §6.7 item 11의 'JIT appears nowhere on this screen' 단언은 같은 문단의 캐리브아웃('route rendering ... inside the unchanged order table')과 G-5의 JIT=주문측 배지 정의와 충돌 — 개발자가 이 문장을 근거로 무변경 계약(BR-11) 대상인 테이블에서 JIT 배지를 제거할 위험.

### [C-84] MINOR — 전역규칙 v1.1이 PD-1/2/3/4/5/7/8을 CONFIRMED 처리하고 'tags removed'를 선언했는데, 스펙 본문에는 PD-1~PD-7의 `[PD-n · OWNER-PENDING]` 태그가 약 20곳에 잔존하고 §9.1은 이들을 여전히 살아있는 pending 의존성·가역 결정으로 서술한다(PD-5/PD-6 'Reversal impact if the owner rejects' 표, §3.7.5의 'reversing PD-5 removes this confirm step').

- `_global-rules.md`: "Owner decisions applied: PD-1→[G-15], PD-2→[G-3a], PD-3→[G-7], PD-5→[G-2], PD-7→[G-9], PD-8→[G-10] now **CONFIRMED**; tags removed."
- `order-management.md`: "This page's **behaviour-bearing** PD dependencies are **PD-1, PD-2, PD-3, PD-4, PD-5, PD-6, PD-7, PD-20, PD-22, PD-27, PD-28, PD-35, PD-36, PD-52, PD-53, PD-54, PD-56, PD-57, PD-58, PD-59, PD-63, PD-67, PD-80** (23)"
- `order-management.md`: "reversing PD-5 removes this confirm step and leaves the toast."
- `_global-rules.md`: "**Every removal/deletion-class (destructive) action takes a confirm dialog, plus a reason where the flow already carries a reason field, plus the toast.** **CONFIRMED 2026-08-03 (owner, PD-5).**"

주: 완화 요인: 스펙 문두 배너가 'any inline `[PD-{these} · OWNER-PENDING]` or `[PD-{these} · NO-DEFAULT]` tags below are superseded'로 명시 커버 — 태그 자체는 의도된 처리로 볼 수 있다. 그러나 §9.1의 PD-5/PD-6 가역성 표와 §3.7.5의 확장·가역 프레이밍은 태그가 아닌 산문이고, G-2가 확정한 '모든 파괴적 액션에 확인 다이얼로그' 전역 규칙과 달리 이 확인 스텝을 여전히 '레지스터 목록 밖 페이지 확장(철회 가능)'으로 서술한다 — PD-5 확정 후에는 성립하지 않는 프레이밍.

**대조 후 이상 없음:** [G-7] 허브 캐노니컬 문자열 HUB-1~HUB-7 — §3.10과 QA-CMT 블록(02·03·04·05·10·18) 전부 바이트 일치, HUB-3 3/2/2/1 코퍼스 분기 서사도 G-7 표와 일치 · 크로스페이지 이벤트 이름 canon 11종 — §5 서두 선언과 전역규칙 목록 집합 일치, DC-28(idempotency.duplicate_suppressed)의 '비캐노니컬 개념' 선언도 사실과 일치 · Slack 라우팅 — @mention 단일 루트·채널 #fulfillment-admin-comments(C0BMGEWM5QA)·페이로드 필드 일치, 타 3채널(무ID·타화면 소속) 서술 정확, 이 페이지에서 루트 미발명(§6.2) · [G-2] 적용 — 3개 확정 액션(임포트 확정·기간 시작·기간 취소) 토스트, 무리로드 계약, RTO Bulk Outbound 예외의 오프페이지 스코프 · [G-1]/[G-3]/[G-4]/[G-10]/[G-11]/[G-14] N/A 선언 — 각 규칙의 표면 열거(스캔=VO·Closing, 사운드=VO·RTO·OD·INV, 프린트 표면 목록)와 일치 · [G-6] 프로덕트 네이밍 — M1 프리뷰 브랜드 볼드, 한국어 문자열 부재 선언과 G-6 데이터 조항의 정합 · [G-9] 멱등성·동시편집 — 내용상 일치(BR-27은 규칙 본문 재서술이나 문면 동일, 상이점 없음) · [G-13] 규범 조항 — BR-6/BR-7/BR-8, §3.6.4/§3.6.5, E-34, QA-SMP-46 모두 PD-51 개정본('sample set' only)과 일치, PD-36 헤지도 양 문서 동일 (§1.3·§10만 예외 — findings 참조) · [G-15] 단일 어드민 롤(BR-22), [G-8] 캡처 독트린·NON-event 선언 메커니즘(§5.4), [G-12] 디렉토리형 딥링크(../slug/#anchor) — G-12 자체 예시 형식과 일치

## 전역규칙 준수 감사 — ready-to-outbound.md vs _global-rules.md (기준선 review-baseline-20260803, 모순 사냥)

### [C-85] MAJOR — PD-36 결정 상태가 두 문서에서 정반대다 — _global-rules [G-13]은 피킹리스트 sample-set 라인의 존재 여부 자체가 아직 OWNER-PENDING이라고 하는데, 스펙 §3.15는 오너 승인 배치로 WF-9가 적용되어 PD-36이 긍정으로 '확정(settled)'됐다고 선언하고 QA-M1-03이 [WF] 티어로 오늘 당장 sample 행 존재를 단언한다.

- `_global-rules.md`: "whether the picking list carries a sample-set line at all remains `[PD-36 · OWNER-PENDING]` (if it does, the line reads "sample set")"
- `ready-to-outbound.md`: "**WF-9 was applied to the wireframe on 2026-08-03** (owner-approved batch): M1 now renders one amber-tinted `sample set` row for order `422165` … `[PD-36]` is thereby settled in the affirmative for the modal; `[PD-51]` fixed the content"
- `ready-to-outbound.md`: "**QA-M1-03 `[WF]` — Row count, location-ascending sort, and the trailing sample row** … has exactly **5** rows: four product rows … followed by the sample-set row"

주: 스펙 내부도 갈라져 있음: §9.4는 "WF-9 … **Conditional** — blocked on `[PD-36]` approval"로, §9.2 OQ-1은 "only owner approval of `[PD-36]` remains. QA-E-20 unblocks once PD-36 lands"로 G-13 쪽(펜딩)과 일치하는 반면, §3.15·QA-E-20("unblocked 2026-08-03")·QA-M1-03~06은 확정·적용 상태를 규범으로 서술. 어느 쪽이 맞든 한 문서는 수정 필요.

### [C-86] MAJOR — 스펙 §2.4의 WF-9 등재 행이 [G-13]을 '어떤 샘플을 몇 개(which sample and how many)' 표기를 요구하는 규칙으로 인용하는데, 이는 G-13이 PD-51 오너 확정으로 명시적으로 폐기(supersede)한 옛 요구사항이다 — 현행 규칙과 다른 내용을 규칙 명의로 주장하는 인용 결함이며, 'an answer to PD-51'이 남았다는 조건 서술도 옛 상태다.

- `ready-to-outbound.md`: "**WF-9** | M1 picking list has no sample-set rows, while [G-13] requires internal picking artifacts to show **which** sample and **how many**. Fix is **conditional** on owner approval of PD-36 *and* an answer to PD-51."
- `_global-rules.md`: "**v1 makes no sample distinction** — internal invoices and picking labels also render **"sample set" only**: no sample type, no per-type quantity. … **CONFIRMED 2026-08-03 (owner, PD-51)** — this supersedes the earlier "which sample and how many" internal-artifact requirement"
- `ready-to-outbound.md`: "| **WF-9** — add sample rows to the M1 picking table | **Conditional** — blocked on `[PD-36]` approval **and** OQ-1 (`[PD-51]`) |"

주: §10 결정 로그의 C-8 행("[G-13] doctrine wins — internal picking artifacts list which sample and how many")은 날짜 박힌 이력 서술이라 제외했으나, §2.4 등재 행과 §9.4 백로그 행은 현재 상태 서술(present tense)이므로 결함. 개발자가 §2.4만 읽으면 PD-51이 폐기한 샘플 타입별 표기를 구현하게 된다.

### [C-87] MAJOR — §9.3 D-12의 제약 열 'multiple mentions stay one message [E-75]'는 v1.2에서 교정된 @멘션 팬아웃 계약(멘션된 사용자별 1메시지 — 스펙이 [G-7]의 코퍼스 전체 계약이라고 못박은 것)과 정반대의 옛(v1.0/v1.1) 동작을 규범으로 남기고 있으며, 근거로 인용한 E-75 자체가 반대 내용을 말한다.

- `ready-to-outbound.md`: "| **D-12** | Slack retry policy on delivery failure [DC-2] | Never blocks or rolls back [BR-30]; multiple mentions stay one message [E-75] |"
- `ready-to-outbound.md`: "**One Slack message per distinct resolved mention**: a comment naming three different people produces three messages … This is [G-7]'s corpus-wide contract — its payload field is a single mentioned user"
- `_global-rules.md`: "the message body @mentions the person, so Slack raises a personal notification … Payload: entity no., comment text, time, author, mentioned user, deep link. **CONFIRMED by owner 2026-08-03.**"

주: §10.1 역전 체인 8이 "one message naming every mentioned user (v1.0/v1.1) → corrected on 2026-08-03"으로 기록한 바로 그 교정이 D-12 행에는 반영되지 않은 잔재. E-75·§3.9·§6.1·DC-2·QA-L9-11·QA-DC-02는 전부 교정본이고 D-12만 옛 문장.

### [C-88] MAJOR — [G-4]는 캐리어 라벨을 '각 캐리어의 기존 기본 출력물을 그대로(verbatim) 인쇄 — 커스텀 캐리어 라벨 레이아웃은 존재하지 않고 앞으로도 만들지 않는다'로 오너 확정했는데, 스펙 §9.1(및 §6.4 항목 6)은 'Deleo나 YUN 라벨에 무엇이 그려지는지, 필드 배치, 바코드 위치'를 Phase 3-1의 별도 오너 세션에서 정할 미래 설계 주제로 서술해 확정 사항을 다시 연다.

- `_global-rules.md`: "Carrier labels themselves are always **each carrier's existing default output, printed verbatim** — no custom carrier-label layout exists or will be built, for YUN, DELEO, or any carrier added later (e.g. FedEx). Only the internal invoice ("PACKING") is ours to design — see `specs/shipping-label.md`. **CONFIRMED 2026-08-03 (owner).**"
- `ready-to-outbound.md`: "| **Label and invoice layout content** — what is drawn on a Deleo or YUN label, field placement, barcode position, sample-row rendering on the printed artifact | **Phase 3-1**, a separate owner session after Phase 3."

주: 내부 송장(PACKING)·sample-row 렌더링 부분은 G-4가 '우리 설계 영역'으로 인정하므로 Phase 3-1 회부가 정당하나, 'what is drawn on a Deleo or YUN label' 부분은 G-4상 결정 대상 자체가 아니다(캐리어 기본 출력 그대로). §6.4 항목 6 "Label layout content is out of scope — Phase 3-1"도 같은 결함을 공유.

### [C-89] MAJOR — [G-2]는 '모든 confirming action — register, confirm, cancel, send, save, remove/delete — 은 우상단 토스트를 띄운다'를 오너 강조로 확정했는데, 스펙 BR-34/§4.1은 영속 상태 변경인 ★ star/unstar(DC-3로 persist)와 M1 Cancel에 토스트 없음을 규범으로 정하고, 그 경계 문장이 아직 [G-2]에 없음을 스스로 인정한다 — 페이지 스펙이 전역규칙 본문을 로컬에서 개정하는 계약 위반이자 규칙 본문과의 모순.

- `_global-rules.md`: "**Every confirming action** — register, confirm, cancel, send, save, remove/delete — shows a top-right toast stating what happened. Green for success, red for failure."
- `ready-to-outbound.md`: "| `[L-9]` `★` star / unstar | In-place: glyph fills / empties | none |"
- `ready-to-outbound.md`: "That sentence belongs in [G-2] itself; until it lands there, both pages carry it."

주: 자기 선언된 이탈(adjudication C-6 인용, 오너가 문자적으로 읽으면 토스트 한 줄 추가로 끝난다는 완화 경로 포함)이지만, 마감 시점에 [G-2] 본문이 미개정 상태라 두 문서가 '★는 토스트를 띄우는가'에 다른 답을 준다. star는 DC-3 `comment.starred/unstarred`로 영속되는 상태 변경이라 G-2 문자적 해석(save류)에 걸린다. 해소는 G-2에 경계 문장 승격 또는 스펙 표 수정 중 하나.

### [C-90] MINOR — PD-71 상태 모순 — _global-rules는 PD-71을 2026-08-03 오너 확정 목록에 포함('owner decision round is fully closed')하는데, 스펙 §9.2는 'PD-71 remains open', §6.3은 'the register marks it *not decided*'라고 현재형 프로즈로 반대 상태를 단언한다(스펙 자신의 헤더 OWNER-DECIDED 목록과도 충돌).

- `_global-rules.md`: "PD-1 through PD-8, 51, 55, 66, 71, 74, 79 were owner-decided on 2026-08-03 — their register entries carry the ruling. The owner decision round is fully closed"
- `ready-to-outbound.md`: "is cited in §6.3 as context but is **owned by `closing.md`**, and no behavior on this page rests on it; PD-71 remains open.)"
- `ready-to-outbound.md`: "its column mapping is an open question owned by the closing spec `[PD-71 · NO-DEFAULT]` — the register marks it *not decided*"

주: 스펙 헤더의 태그 supersede 선언은 '인라인 태그'만 커버하며, §9.2·§6.3·§9.1의 프로즈 단언(remains open / undecided)은 커버 밖. 이 페이지 동작에는 영향 없음(스펙 스스로 명시)이라 MINOR이나, closing.md 오너에게는 오독 위험.

### [C-91] MINOR — §5 서두의 'Doctrine [G-8]' 문장이 G-8 규칙 본문을 예시만 바꿔 재서술한다('UI logs (actor log, scan feed, audit history)' → 'UI surfaces (comment history, hub badges)') — 전역규칙 헤더의 'they never restate a rule body' 계약 위반이며, v1.2 결정 로그가 '재서술 3건을 델타로 정리했다'고 주장한 뒤에도 잔존.

- `_global-rules.md`: "Screen specs cite these by ID (`[G-n]`) and describe **page deltas only** — they never restate a rule body."
- `_global-rules.md`: "UI logs (actor log, scan feed, audit history) are **views over persisted events**, never the only copy."
- `ready-to-outbound.md`: "**Doctrine [G-8]:** UI surfaces (comment history, hub badges) are **views over persisted events**, never the only copy. Anything operator-initiated that is not explicitly declared a NON-event below **must** persist."

주: 실질 의미는 동일해 행동 모순은 아니고 계약 형식 위반. 같은 부류로 BR-13/E-9의 "The known current-admin bug processes double clicks twice — this is a mandatory regression test, not a feature to reproduce"가 G-9 본문("A known current-admin bug processes double clicks twice — this must be fixed, not reproduced")을 근사 재서술함.

### [C-92] MINOR — Slack 재시도 정책 위임 범위 모순 — 전역규칙(PD-4 확정)은 '지수 백오프로 자동 재발송 + N회 후 어드민 알림 로그 플래그'를 고정하고 N만 개발자 결정으로 남겼는데, 스펙 §6.1/D-12는 'Retry policy is a developer decision'으로 정책 전체를 위임하며 D-12 제약 열에 지수 백오프·어드민 플래그 요건이 없다.

- `_global-rules.md`: "the failure is queued in a background retry queue and re-sent automatically with exponential backoff. Every dispatch result is persisted [G-8]. An item still undelivered after N retries (N = developer decision) is flagged in the admin notification log."
- `ready-to-outbound.md`: "the comment commits first; Slack delivery is a side effect that is retried and persisted [DC-2] and never blocks the UI or rolls anything back `[PD-4 · OWNER-PENDING]` [BR-30]. Retry policy is a developer decision [D-12]."

주: 전역규칙이 이미 형태(지수 백오프)와 실패 표면(어드민 로그 플래그)을 확정했으므로 스펙의 전면 위임 문구는 축소 서술. 개발자가 D-12만 읽으면 백오프 없는 고정 간격 재시도도 계약 내라고 판단할 수 있다.

### [C-93] MINOR — QA-M1-04가 'v1 assigns no SKU to the sample set'의 근거로 [G-13]을 인용하지만, G-13 본문에는 샘플 세트의 SKU 부여에 관한 조항이 없다(있는 것은 '샘플 구분 없음·타입/수량 미표기'뿐) — 규칙이 말하지 않는 내용을 규칙 명의로 주장하는 인용.

- `ready-to-outbound.md`: "the fifth (sample) row's SKU cell reads `—`, because v1 assigns no SKU to the sample set [G-13] [BR-21]"
- `_global-rules.md`: "**v1 makes no sample distinction** — internal invoices and picking labels also render **"sample set" only**: no sample type, no per-type quantity."

주: G-13 [G-13] 전문(§93~96행)에 SKU 언급 자체가 없음. 'no sample distinction'에서의 그럴듯한 추론이지만, 스펙 규율상 추론이면 페이지 델타(spec-defined)로 표기해야 하고 [G-13] 인용으로 못박으면 안 됨. 모순은 아니어서 MINOR.

### [C-94] MINOR — PD-55는 전역규칙·스펙 §9.2 OQ-2 모두 오너 확정(2026-08-03)인데, §6.1 non-route 표는 이를 현재형으로 'No route and no owner exist for that follow-up — that is precisely the gap recorded as [PD-55 · NO-DEFAULT]'라며 미해결 갭으로 서술한다(DC-28·QA-L3-07의 `[PD-55 · NO-DEFAULT]` 태그도 잔존).

- `ready-to-outbound.md`: "**"Not connected — contact the Fulfillment Center" orders raise no Slack alert.** No route and no owner exist for that follow-up — that is precisely the gap recorded as `[PD-55 · NO-DEFAULT]` (§9.2 OQ-2)."
- `_global-rules.md`: "PD-1 through PD-8, 51, 55, 66, 71, 74, 79 were owner-decided on 2026-08-03"
- `ready-to-outbound.md`: "**OQ-2 — "Not connected — contact the Fulfillment Center" orders: what unblocks them, and who owns it?** `[PD-55]` — **RESOLVED, OWNER-DECIDED 2026-08-03**"

주: 인라인 태그는 스펙 헤더의 supersede 선언(PD-55 포함)으로 커버되나, §6.1 프로즈의 'gap'·'no owner exist' 프레이밍은 결정 내용(팔로우업 오너=풀필먼트 담당자, 수동 Slack 조율)과 어긋난 옛 상태. 실질 동작(자동 라우트 없음)은 결정과 일치하므로 MINOR.

**대조 후 이상 없음:** [G-1] 스캐너 프로토콜 — 스펙 BR-25/§1.4의 'N/A 선언'은 G-1 적용범위 열거(View Orders·Closing)와 일치, 침해 없음 · [G-2] 유일 리프레시 예외 — BR-8·§3.4 step 7의 'sole designed exception, 2026-07-09' 서술이 G-2 본문·날짜와 일치 · [G-3] 오디오 — 송출음은 Bulk Outbound 단 1개 컨트롤(§6.5, QA-L4-04), TTS·경고음 부재 선언 모두 G-3(a)(b)(c) 스코프와 일치 · [G-4] 인쇄 표면 3종(row Print·Bulk Print Labels·M1 picking list) — G-4의 RTO 표면 목록과 정확히 일치, 실패의 red toast + print.job_result 영속도 일치 (레이아웃 Phase 3-1 건 제외) · [G-5] 소싱 라우트 배지 — 이 페이지 무배지 + 소비자 목록(View Orders·Inventory·Order Detail)이 G-5와 일치, OTHER(channel) PD-80 펜딩 상태도 양쪽 일치 · [G-6] 상품명 — Ready Item Details·M1 한국어명 + 볼드 EN 브랜드, 데이터 비번역 원칙 일치([RTO-WFX-5]는 와이어프레임 결함으로 올바르게 등재) · [G-7] 허브 캐노니컬 문자열 HUB-1~HUB-7 — §3.10·QA-L10 전 문자열 바이트 일치, 채널 #fulfillment-admin-comments(C0BMGEWM5QA)·페이로드 필드·검색 전범위(all comments) 일치 · [G-9] 멱등성 — 배치 키+주문별 키, 이중클릭 버그 회귀 테스트(QA-L4-07), 낙관적 버전 체크→409→비녹색 토스트(BR-29) 실질 일치 · [G-12] 딥링크 — Order ID 실링크 요건과 [RTO-WFX-3] 결함 등재 방향 일치 · [G-14]/[G-15] 인용 — 위치 1:1(PD-46 펜딩 상태 양쪽 일치)·단일 어드민 롤+행위자 기록 일치 · 크로스페이지 캐노니컬 이벤트명 — §5.1의 comment.posted/mention_notified/starred/unstarred/read/mark_all_read·order.outbounded·order.status_changed·print.job_result 전부 전역 철자와 일치 · Slack 라우팅 — @멘션 라우트 페이로드 및 명시적 non-route(#unrecognized-tracking·#wholesale-ops·#partnership-kr 미발화 사유)가 전역 표와 일치

## 전역규칙 준수 감사 — order-detail.md vs _global-rules.md (기준선 review-baseline-20260803). 두 문서 전문 정독 + 검증 필요 대목은 _plans/_provisional-decisions.md·shipping-label.md 재조회로 확정.

### [C-95] MAJOR — 전역규칙이 '오너 결정 라운드 완전 종결(PD-55·71·74 포함 owner-decided)'을 선언했는데, order-detail 본문(§9.2·§6.4·[L-9]·QA-OUT-13)은 이 셋을 여전히 '미결정(NO provisional default)' 실질 서술로 유지한다 — 같은 표에서 PD-51 행만 RESOLVED로 갱신돼 갱신 패턴이 선택 적용됐다.

- `specs/_global-rules.md`: "PD-1 through PD-8, 51, 55, 66, 71, 74, 79 were owner-decided on 2026-08-03 — their register entries carry the ruling. The owner decision round is fully closed"
- `specs/order-detail.md`: "### 9.2 Owner questions with NO provisional default

These have **no** specified behavior and none may be invented."
- `specs/order-detail.md`: "**What unblocks such an order, and who owns it, is undecided** `[PD-55 · NO-DEFAULT]` — this page states the display and the block, and invents no manual carrier-assignment affordance"
- `specs/order-detail.md`: "**Correction path when an extra parcel is found AFTER a closing is confirmed.** No reopen/amend affordance exists anywhere, and inventing one changes the immutability model."
- `specs/order-detail.md`: "The SS Daily Shipping Status sheet is updated from **Closing** `[PD-71 · NO-DEFAULT]`."
- `specs/_plans/_provisional-decisions.md`: "**[PD-55]** … **OWNER-DECIDED 2026-08-03**: Unblocking is **manual coordination — contact the fulfillment person in charge via Slack**. v1 ships no in-admin release/carrier-assignment UI."
- `specs/_plans/_provisional-decisions.md`: "**[PD-71]** … **OWNER-DECIDED 2026-08-03**: The sheet is retired entirely — no integration; admin Closing History replaces it."
- `specs/_plans/_provisional-decisions.md`: "**[PD-74]** … Owner decision: **Amend Closing** — each confirmed Closing History row carries [Amend]"

주: 행동 자체는 대부분 결정과 일치(이 페이지는 어차피 어포던스를 만들지 않음)하나 3건 모두 실질 서술이 구식: ① PD-55 — '누가 언블록하나'는 답이 나왔고(수동 Slack 조율) §9.2의 'no Slack route exists' 서술도 낡음 ② PD-71 — §6.4가 '시트가 Closing에서 갱신된다'고 단언하나 시트는 전면 폐기됨(통합 부재) — 통합 감사를 오도 ③ PD-74 — QA-OUT-13의 'a Closing concern with no decided path'는 거짓(Amend Closing이 closing.md v1.3에 스펙됨). 문서 상단 배너가 '인라인 태그는 superseded'라 하지만 §9.2의 산문·§6.4의 사실 단언은 태그가 아니며, 같은 §9.2 표의 PD-51 행은 'RESOLVED — OWNER-DECIDED 2026-08-03'로 갱신돼 있어 갱신 누락임이 문서 내부적으로도 드러난다.

### [C-96] MINOR — [G-4]가 라벨 레이아웃 문제를 종결(캐리어 라벨=디폴트 verbatim 확정 + 내부 인보이스=specs/shipping-label.md)로 CONFIRMED했는데, order-detail은 4곳([L-13]·§6.3·§9.1·BR-28)에서 여전히 'Phase 3-1, 오너와의 별도 세션으로 이연'이라 서술하고 shipping-label.md를 한 번도 가리키지 않는다.

- `specs/_global-rules.md`: "Carrier labels themselves are always **each carrier's existing default output, printed verbatim** — no custom carrier-label layout exists or will be built, for YUN, DELEO, or any carrier added later (e.g. FedEx). Only the internal invoice ("PACKING") is ours to design — see `specs/shipping-label.md`. **CONFIRMED 2026-08-03 (owner).**"
- `specs/order-detail.md`: "| **Label / invoice layout content** | Deferred to **Phase 3-1**, a separate session with the owner. This spec covers print *behavior* `[G-4]` only, never what is printed on the label. |"
- `specs/shipping-label.md`: "**Status:** **fully CONFIRMED** (owner, 2026-08-03) — carrier-label policy, unified internal invoice, and all three §6 items are decided. No open questions."
- `specs/order-detail.md`: "**Label layout content is out of scope** — Phase 3-1. This section specifies print *behavior* only."

주: 'out of scope for this spec'는 여전히 옳으나 '오너와의 별도 세션으로 이연'은 낡음 — 그 결정은 이미 내려졌고 산출물(shipping-label.md, fully CONFIRMED)이 존재한다. 개발자가 존재하는 스펙을 기다리게 만들 수 있음. 수정은 포인터 교체 1줄×4곳.

### [C-97] MINOR — BR-39가 [G-2]의 PD-5 확정 문안을 재서술하면서(계약상 스펙은 델타만 서술) 'reason field'를 'reason enum'으로 바꿔 적용 범위를 좁혔다 — 자유텍스트 reason 필드(Cancel Inbound note, Cancel Outbound reason)는 field이지만 enum이 아니다.

- `specs/_global-rules.md`: "**Every removal/deletion-class (destructive) action takes a confirm dialog, plus a reason where the flow already carries a reason field, plus the toast.** **CONFIRMED 2026-08-03 (owner, PD-5).**"
- `specs/order-detail.md`: "| **BR-39** | **Every removal or deletion gets a confirm step and a toast**, and a reason where a reason enum already exists in the flow. | `[GD-5]` `[C-6]` `[PD-5 · OWNER-PENDING]`; the wireframe's silent removals are gaps, not decisions. | 2026-08-03 |"

주: 실제 페이지 동작([L-2] Cancel Inbound 확인창의 optional note, [BR-19] Cancel Outbound의 optional reason)은 G-2 원문 쪽과 일치하므로 행동 충돌은 없음. 그러나 규칙 본문 재서술 + 어휘 드리프트(field→enum)는 '델타만 서술' 계약 위반이며, BR-39만 읽는 구현자는 reason 캡처 범위를 좁게 해석할 수 있다.

### [C-98] MINOR — DC-32의 origin enum에 `expected_qty_edit`가 포함돼 있으나, [G-11]과 이 스펙 자신의 §5.3·QA-DC-5에 따르면 expected-qty 자동 코멘트는 인바운드 요청에만 달리고 주문에는 절대 달리지 않는다 — 이 페이지에서 발생 불가능한 enum 값.

- `specs/_global-rules.md`: "Editing recomputes remaining quantity and the full-confirm gate, auto-posts a comment on the request, and notifies the requester [G-7]."
- `specs/order-detail.md`: "| **DC-32** | `comment.auto_posted` | system comment lands on this order | `comment_id`, `source=system`, `origin` ∈ {`unrecognized_match_confirmed`, `expected_qty_edit`}, `origin_ref`, `mentions[]` | thread, flagged system |"
- `specs/order-detail.md`: "**no** line-item change on this order; the auto-comment lands on the **inbound request**, not here"

주: QA-DC-5도 'a View Orders M6 expected-qty edit produces **no** line-item change and **no** comment on this order'를 단언한다. DC-32 트리거가 'system comment lands on this order'이므로 enum에서 `expected_qty_edit`를 빼거나, 크로스 엔티티 이벤트임을 명시해야 함.

### [C-99] MINOR — 스펙이 크로스페이지 캐노니컬 이벤트명을 '10개(the canonical ten)'로 반복 서술하나, _global-rules의 캐노니컬 목록은 `product.barcode_registered`를 포함해 11개 이름이다.

- `specs/_global-rules.md`: "`comment.posted` · `comment.mention_notified` · `comment.starred` / `comment.unstarred` · `comment.read` / `comment.mark_all_read` · `comment.auto_posted` (`source=system`) · `product.barcode_registered` · `order.status_changed` · `order.outbounded` · `print.job_result`."
- `specs/order-detail.md`: "The **10 canonical names are byte-identical everywhere** `[C-12]`; this is the tier below them."
- `specs/order-detail.md`: "**Below the canonical ten, five shared *concepts* carry a different name on each page**"

주: §5.2가 barcode_registered 미발생을 별도 선언하므로 페이지 목록 자체는 정당하나, [X-8]과 §5의 '캐논=10' 카운트는 전역 목록(11)에 대한 오기술. §5 Naming 문단도 '_global-rules의 캐노니컬 이름: [10개 나열]' 형태라 목록이 전부인 것처럼 읽힘.

### [C-100] MINOR — [L-1] 9단계의 셀프멘션 Slack 발송 억제는 [G-7] 본문('@mention은 멘션된 사람에게 Slack으로 통지')이 예외 없이 요구하는 통지를 페이지 델타로 제거한 것이며, 스펙 스스로 오너 결정이 없는 dev default임을 인정한다.

- `specs/_global-rules.md`: "`@mention` notifies the mentioned person through Slack: **#fulfillment-admin-comments** (`C0BMGEWM5QA`) — the message body @mentions the person, so Slack raises a personal notification"
- `specs/order-detail.md`: "Self-mention (author == mentioned user) posts normally but suppresses the dispatch — no self-notification, recorded as `DC-27.suppressed_reason=self_mention`. … no owner decision exists for a human `@self` in a free-text comment.** Suppression is therefore the **dev default**, recorded in §9.4 D-19, not a registered provisional decision `[E-60]`"

주: 동작 자체는 합리적이고 억제 사실이 DC-27에 영속되지만, G-7 본문에는 이 카브아웃이 없다. G-7 개정(또는 PD 등록) 없이 페이지가 규칙 행동을 삭제한 형태 — 스펙이 D-19로 자진 신고한 만큼 오너 확인 대상으로 승격하는 것이 안전.

### [C-101] MINOR — BR-10·[L-11]이 KR 브랜드 볼드를 '이 페이지의 델타([G-6]를 1열→2열로 확장)'라고 규정하나, G-6 본문이 이미 전역적으로 '한국어 제품명도 EN 브랜드 볼드를 단다'고 명시한다 — 규칙이 말하지 않는 baseline(1열)을 주장하는 인용.

- `specs/_global-rules.md`: "Korean product names also carry the EN brand in bold (e.g. **Dr.Jart+** 포어레미디 리뉴잉 폼 클렌저)."
- `specs/order-detail.md`: "| **BR-10** | **Brand is bold-prefixed on both the EN and the KR product name** — page delta on `[G-6]`, which this page applies to two columns instead of one."

주: 렌더링 결과는 완전히 일치(QA-REN-6 포함)하므로 행동 결함은 아님. 그러나 'G-6가 원래 1열 규칙'이라는 프레이밍은 오기술이며, 다른 스펙이 이를 근거로 KR열 브랜드 볼드를 '델타 없는 페이지엔 불요'로 읽을 여지를 만든다.

### [C-102] MINOR — §3.0.2에서 주소 편집 실패만 '인라인 필드 에러, 토스트 없음'으로 규정해, [G-2]의 '모든 확인성 액션은 토스트 — 실패는 빨간색' 문안과 어긋나는 유일한 실패 행이다.

- `specs/_global-rules.md`: "**Every confirming action** — register, confirm, cancel, send, save, remove/delete — shows a top-right toast stating what happened. Green for success, red for failure."
- `specs/order-detail.md`: "| `[L-F9]` address ✎ | `Billing address updated` / `Shipping address updated` | inline field error, no toast `[E-54]` |"

주: E-54의 검증은 '캐리어 요건' 대조라 서버측 판정일 가능성이 높은데도 토스트가 면제됨 — §3.0.2의 다른 모든 실패 열은 red 토스트를 명시한다. 클라이언트 사전검증(E-17~19)과 동급의 pre-action 거절로 해석하면 방어 가능하므로, 결함 확정이 아니라 G-2 해석 명문화(검증 차단은 확인성 액션 미성립) 또는 red 토스트 통일 중 택일이 필요한 지점.

**대조 후 이상 없음:** [G-1] 스캐너 프로토콜 — 스펙의 적용 제외 선언([BR-30])은 G-1의 스코프 문구('Applies to every scan surface: View Orders (all states), Closing')와 정합. 인바리언트 제거가 아니라 스코프 밖 선언 · [G-2] 무리프레시 — '이 페이지는 리프레시 예외 없음'은 G-2의 유일 예외(RTO Bulk Outbound)와 정합. 파괴적 액션 confirm+토스트도 전면 반영([C-6]·BR-39 행동부) · [G-3](a) 사운드 스코프 — G-3 CONFIRMED 목록의 'Order Detail (Outbound)'과 [L-9] step 2·BR-29 일치. (b) TTS·(c) 경고음 부재 선언도 G-3 원문의 페이지 귀속과 일치 · [G-4] 인쇄 동작 — 즉시 출력·브라우저 다이얼로그 금지·실패 red 토스트·print.job_result 영속 모두 일치. 프린트 서피스 목록('Order Detail (Print)')과 'View Label은 프리뷰' 구분도 정합 (Phase 3-1 이연 문구만 별도 지적) · [G-5] 소싱 루트 — 오더-페이싱 4배지, JIT 채널 괄호(Coupang/Naver/Other retail), 무색 검정 볼드(colorless, QA-REN-4의 transparent+#14101B), OTHER 부재([C-3]/[X-5]) 모두 정합 · [G-7] 허브 캐노니컬 카피 — HUB-1~HUB-7 일곱 문자열을 [L-7]·QA-HUB-1/3/4와 바이트 단위 대조: 전부 일치. {n} 치환 규칙('1 results' 허용)·'order' 고정 어휘 규칙도 준수. [X-6] RESOLVED 서술은 G-7 v1.2 변경이력과 일치 · [G-7] Slack 라우팅 — §6.1 행 1·2의 채널(#fulfillment-admin-comments)·ID(C0BMGEWM5QA)·페이로드·@registrant 대상이 전역 라우팅 표와 일치, 'pending' 미기재 준수([C-2]) · [G-8] 데이터 캡처 — 논이벤트 16건의 명시적 선언 구조는 G-8의 'Specs may declare explicit NON-events' 위임과 정합. NE-8(코멘트 검색)의 크로스페이지 이견은 [X-8]로 자진 등재돼 있음 · [G-9] 멱등성 — 클라 디바운스+서버 키, 동시편집 409→행 리로드+non-green 토스트([E-21]·DC-37)가 G-9 CONFIRMED 문안과 일치. 카운팅 플로우 병합 조항은 이 페이지에 해당 플로우 없음 · [G-10] 트래킹 네임스페이스 — [L-4] 분리표(inbound vs outbound, 일치 허용·해석 분리)가 G-10 CONFIRMED와 정합 · [G-12] 딥링크 — §6.2의 '특정 엔티티로 해석' 서술이 G-12와 일치 · [G-13]/PD-51 — v1 'sample set only'(타입·수량 무표기)가 [L-10]·BR-34·E-57·QA-REN-16·§5.3에 일관 전파됨. 클론의 샘플 미복사도 G-13 기간 규칙 근거로 정합

## 전역규칙 준수 감사 — tracking-missing.md(전문 1541행 정독) vs _global-rules.md v1.2(전문 정독). 경로: /Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/. 대조 축: (1) 전역규칙 재서술 (2) 페이지 델타 모순 (3) [G-n] 인용 오귀속 (4) CONFIRMED 사항의 옛 상태 잔존.

### [C-103] BLOCKER — 전역규칙 헤더(와 스펙 배너)는 PD-66을 2026-08-03 오너 결정 완료로 선언했는데, 스펙 본문(§9.1, [E-3], QA-VAL-10, [L-1] 1열)은 여전히 '미결정·행동 미기술·QA 영구 BLOCKED' 상태라 결정된 행동이 스펙에 부재한다.

- `_global-rules.md`: "PD-1 through PD-8, 51, 55, 66, 71, 74, 79 were owner-decided on 2026-08-03 — their register entries carry the ruling. The owner decision round is fully closed"
- `tracking-missing.md`: "- **Status:** not decided. **No default was adopted and no behavior is specified anywhere in this document.**"
- `tracking-missing.md`: "**QA-VAL-10 [ADMIN] BLOCKED** — Intake of an item with **no tracking number** `[E-3]`. `[PD-66 · OWNER-PENDING]` is NO-DEFAULT: no behavior is specified, so this path has **no acceptance criteria**."
- `tracking-missing.md`: "PD-1 through PD-8, 51, 55, 66, 71, 74, 79 are now **OWNER-DECIDED** (PD-6 confirmed 2026-08-03 — the owner decision round is fully closed); any inline `[PD-{these} · OWNER-PENDING]` or `[PD-{these} · NO-DEFAULT]` tags below are superseded"

주: 배너는 '태그'만 supersede한다고 선언하는데 §9.1은 태그가 아니라 'Status: not decided'라는 규범 서술 전체다. §9.1이 명시한 파급 범위(View Orders M2b 검증 규칙, [L-1] 1열 nullability, §3.4.3 step 2)가 전부 이미 내려진 결정을 기다리는 척 방치돼 있고 QA-VAL-10은 판정 불가로 고정된다. 마감 전 결정 내용 반영 필수.

### [C-104] MAJOR — 전역규칙이 CONFIRMED 처리한 PD-1/3/4/6/7/8/51을 스펙 §9.1 인벤토리가 '14 entries still OWNER-PENDING'·'PD-51 NO-DEFAULT'로, 읽기 계약 item 2가 '이 페이지의 확정은 PD-5와 PD-60뿐'으로 서술해 옛 결정 상태가 규범 텍스트로 잔존한다.

- `tracking-missing.md`: "PD-1, PD-3, PD-4, PD-6, PD-7, PD-8, PD-16, PD-61, PD-62, PD-63, PD-64, PD-65, PD-67, PD-80 — **14 entries still OWNER-PENDING**."
- `_global-rules.md`: "Owner decisions applied: PD-1→[G-15], PD-2→[G-3a], PD-3→[G-7], PD-5→[G-2], PD-7→[G-9], PD-8→[G-10] now **CONFIRMED**; tags removed."
- `tracking-missing.md`: "Once the owner rules, the tag becomes `[PD-n · CONFIRMED {date}]` and the behavior stops being reversible-by-tag — on this page that is `[PD-5]` and `[PD-60]` (2026-08-03)."
- `tracking-missing.md`: "PD-51 is NO-DEFAULT and owned by order-management / RTO / order-detail, cross-referenced from here only"
- `_global-rules.md`: "**CONFIRMED 2026-08-03 (owner, PD-51)** — this supersedes the earlier "which sample and how many" internal-artifact requirement"

주: 14개 중 6개(PD-1/3/4/6/7/8)는 전역규칙과 스펙 자신의 배너 둘 다 오너 결정 완료로 선언한 항목이다. §9.1의 합산 문장 '(14 pending + 2 confirmed + 5 cross-referenced)'과 §9.3의 PD-51 NO-DEFAULT 서술도 동일하게 스테일. 배너-본문 이중 상태는 리버설 편집 시 어느 쪽이 정본인지 판별 불가.

### [C-105] MAJOR — 스펙 §3.6이 'HUB-5/HUB-6/HUB-7은 이 페이지에 적용 안 됨'이라 선언하는데, [G-7]은 모든 화면에 검색 포함 허브를 요구하고 스펙 스스로도 어드민이 검색 입력을 반드시 탑재해야 한다(WF-NEW-A, QA-CMT-07)고 요구해, 탑재될 검색 UI의 3개 캐노니컬 문자열이 계약에서 이탈한다.

- `tracking-missing.md`: "This page builds no search pane, so HUB-5 / HUB-6 / HUB-7 do not apply here."
- `_global-rules.md`: "Every screen carries the top-right Comments hub: `[@ Mentions]` + `[★ Saved]` + full-text search across **all** comments (entity no. / author / text), newest first, click opens the entity."
- `_global-rules.md`: "A page may not introduce a local variant of any of the seven."
- `tracking-missing.md`: "The dropdown markup on this page is missing that input (`WF-NEW-A`). The admin must ship it; the query is persisted `[DC-23]`."
- `tracking-missing.md`: "Then a full-text search input is present, And searching `10323100841207` returns matching comments across **all** entity types, newest first `[G-7]`"

주: '검색 페인 없음'은 현재 와이어프레임의 결함 상태(WF-NEW-A) 서술로만 참이고, 어드민 계약으로는 거짓이다. 이대로면 어드민이 검색을 탑재할 때 결과 헤더(HUB-5)·빈 상태(HUB-6)·플레이스홀더(HUB-7) 문자열이 무규정 — [G-7]이 M3a D7을 닫으려고 만든 byte-exact 계약이 이 페이지에서 다시 갈라진다. QA-CMT-07도 세 문자열을 어서트하지 않는다.

### [C-106] MINOR — §3.3의 [G-5] 델타 논거가 자기모순: 풀 셀 델타는 '[G-5] 소비자 목록에 이 페이지가 없다'로 정당화하면서, 같은 표에서 M1 Channel 셀은 '[G-5] in full'의 지배를 받는다고 서술 — 동일 소비자 목록에 대한 상호배타적 두 독법이다.

- `tracking-missing.md`: "**Why the delta.** `[G-5]`'s consumer list is *View Orders badges, Inventory, Order Detail* — this page is not on it, and the pool cell does not render a badge at all."
- `tracking-missing.md`: "`[G-5]` in full: colorless **bold black**, never a coloured pill. Asserted by QA-M1-10"
- `_global-rules.md`: "All route labels render as **colorless black bold text**, never colored pills. Route origin = Inbound Request; consumers = View Orders badges, Inventory, Order Detail."

주: 델타 자체는 날짜·근거·리버설 임팩트가 명기된 선언 델타(v1.2에서 m1 D-1 BLOCKER 해소분)라 결함으로 보지 않되, 소비자 목록으로 풀 셀만 면제하고 M1은 구속된다는 논리는 성립 불가 — 목록이 페이지를 제외하면 M1도 자발적 채택일 뿐이다. 부수 효과: 풀 셀에서 OTHER 루트는 비볼드 회색으로 렌더되는데 [G-5]의 PD-80은 'black bold OTHER (channel)'을 규정한다.

### [C-107] MINOR — 스펙이 전역규칙 버전을 v1.0으로 핀(헤더·읽기 계약 item 1)하고 item 7은 §3.6 허브 문자열을 '아직 전역규칙에 올라가지 않은 후보 개정'으로 유지하는데, 실제 전역규칙은 v1.2이고 HUB 문자열은 이미 [G-7]에 게재됐다 — item 7 자신의 규칙대로면 해당 항목은 삭제됐어야 한다.

- `tracking-missing.md`: "Every `[G-n]` is a citation to `_global-rules.md` v1.0."
- `tracking-missing.md`: "Three page-level readings in this document are **candidate global amendments that have not yet been raised into `_global-rules.md`** and are therefore stated locally on purpose"
- `tracking-missing.md`: "the four strings above are `[G-7]` HUB-1 / HUB-2 / HUB-3 / HUB-4, and `[G-7]` is now the source; this table quotes it rather than owning it."
- `_global-rules.md`: "Version 1.2 · 2026-08-03 · Applies to all 8 screen specs."
- `tracking-missing.md`: "If the global rule is later amended, the global text supersedes and the page statement is deleted, not edited."

주: §3.6 본문은 이미 '[G-7]이 소스'라고 스스로 교정했으므로 행동 차이는 없다. 남은 것은 헤더의 'Global rules: _global-rules.md v1.0' 핀과 item 7의 3건 목록 중 §3.6 항목(문자열은 동일하므로 위험은 낮음). [BR-44]와 §5.1 이벤트명 노트 2건은 여전히 전역 미게재라 item 7 잔류가 정당하다.

### [C-108] MINOR — §5.1이 '전역규칙이 고정한 캐노니컬 크로스페이지 이벤트명은 10개'라고 서술하지만 전역규칙의 목록은 11개 개별 이름(쌍을 1개로 묶어도 9개)이라 어느 셈법으로도 10이 나오지 않는다.

- `tracking-missing.md`: "The ten canonical cross-page names fixed by `_global-rules.md` are used byte-identically here"
- `_global-rules.md`: "`comment.posted` · `comment.mention_notified` · `comment.starred` / `comment.unstarred` · `comment.read` / `comment.mark_all_read` · `comment.auto_posted` (`source=system`) · `product.barcode_registered` · `order.status_changed` · `order.outbounded` · `print.job_result`."

주: 개별 이름 기준 11개(comment 계열 7 + product/order/print 계열 4), 쌍 묶음 기준 9개. 스펙이 실제 사용하는 이름 자체는 전역 목록과 byte-identical해 실행 영향은 없음 — 서술 수치만 오귀속.

### [C-109] MINOR — §6.1 서두 '페이로드 필드는 전역규칙 라우팅 테이블 그대로이며 전 행 CONFIRMED 2026-08-03'는 4행(에이징 다이제스트)에 대해 거짓이다 — 전역 라우팅 테이블에 해당 행이 없고, 그 행은 스펙 스스로 PD-61 OWNER-PENDING으로 태깅했다.

- `tracking-missing.md`: "Payload fields are verbatim from the routing table in `_global-rules.md` (all rows CONFIRMED 2026-08-03)."
- `tracking-missing.md`: "| 4 | Daily aging digest — pool items open > 24 h `[PD-61 · OWNER-PENDING]` | **`#unrecognized-tracking`** | as-of time, item count, and per item: tracking no., product, registrant, age | none (channel-level, no @mention) | `[DC-18]` → `[DC-19]` |"
- `_global-rules.md`: "## Slack routing (all confirmed 2026-08-03 unless noted)"

주: 전역 라우팅 테이블 6행(unrecognized 발송·모닝체크 2·comment mention·expected-qty·match confirm)을 전수 대조 — 에이징 다이제스트 행은 존재하지 않는다. 1~3행의 채널·페이로드는 전역 테이블과 일치(클린). 서두 문장을 '행 1~3'으로 한정하거나 4행의 출처를 분리 표기해야 함.

### [C-110] MINOR — [BR-9] 근거란이 "[G-8]'s 'why' requirement"를 인용하지만 [G-8] 본문에는 이유(why/reason) 요구가 없다 — G-8은 actor·timestamp·entity·old→new·quantity만 규정한다.

- `tracking-missing.md`: "`[G-2]` with `[GD-5]`, plus `[G-8]`'s "why" requirement and the `[G-11]` reason precedent."
- `_global-rules.md`: "Every operator-initiated action persists: actor, timestamp, entity, old value → new value, quantity."

주: 규범 셀이 아닌 rationale 셀이라 행동 영향은 없다. 이유(reason) 필수화의 실제 근거는 PD-60 오너 확정과 [G-11] 선례로 충분 — G-8 귀속만 제거하면 됨. 인용 오귀속(임무 축 3) 유형.

### [C-111] MINOR — [G-7] HUB-1/2의 캐노니컬화 이전 코퍼스 서술('majority 5/8 — OD·RTO·INV·OM·TM')이 스펙의 서술('four-page-majority strings', TM 와이어프레임은 발산해 WF-NEW-E로 교정)과 모순 — TM이 다수파에 있었는지에 대해 두 문서가 다르게 말한다.

- `_global-rules.md`: "**majority 5/8** (OD · RTO · INV · OM · TM)"
- `tracking-missing.md`: "The wireframe now ships the corpus-canonical four-page-majority strings, so the `[WF]` and `[ADMIN]` tiers assert the same values"
- `tracking-missing.md`: "**`WF-NEW-E` filed and fixed — Comments-hub pane headers diverged from the majority strings.**"

주: 양쪽 모두 이력(provenance) 서술 층위라 검토 규율상 경계선이나, 현재 텍스트끼리의 수치 모순(4 vs 5)이라 등재. 전역이 스펙 단언 기준으로 셌다면(TM의 구 [ADMIN] 티어는 캐노니컬을 단언) 5/8, 와이어프레임 기준이면 4/8 — 어느 기준인지 전역 표가 명시하지 않는다. 현행 캐노니컬 문자열 자체는 양쪽 일치.

**대조 후 이상 없음:** [G-1] 스캐너 프로토콜 — N/A 선언(§1.5, BR-30, §7.8)이 G-1의 적용 표면 목록(View Orders·Closing)과 정합; 델타로 3대 불변식을 건드리는 곳 없음 · [G-2] 리프레시 금지 — BR-34의 '이 페이지는 예외 없음' 네거티브 등재가 G-2의 유일 예외(RTO Bulk Outbound)와 정합; 토스트 색(녹/적, 409는 non-green) 정합. [BR-44] F5 독법은 읽기 계약 item 7이 후보 개정으로 명시 선언한 의도적 로컬 서술이라 결함 아님 · [G-3] 오디오 — outbound-class 버튼 부재 근거의 N/A 선언(§1.5, §5.3, §7.8)이 G-3a 스코프 목록과 정합 · [G-4] 즉시 인쇄 — N/A 선언(BR-31, §6.5)과 PD-68(Closing CSV-only) 성격 서술이 전역 본문과 정합(양쪽 모두 OWNER-PENDING 유지) · [G-6] 상품명 — 브랜드 볼드 양 컬럼 확장은 '표면 범위' 델타로 선언됐고, 한국어 문자열=데이터 원칙 인용 정확 · [G-9] 멱등성 — 키 시맨틱스(BR-23), 더블클릭 가드, 낙관적 버전 체크→409→non-green 토스트 실질 내용이 전역과 일치(BR-22의 재서술은 내용 동일, '다르게' 재서술 아님) · [G-10] 트래킹 네임스페이스 — [L-1] 1열·E-11·QA-VAL-04의 inbound/outbound 분리 모델이 전역과 정합; BR-19의 주문라인 유일성은 '페이지 확장'으로 명시 선언되고 독립 리버설 경로까지 기재 · [G-11] — 이유 enum·M6 원천 등 본문 재서술 없이 교차참조만(§7.8, §9.3) · [G-12] 딥링크 — §6.2 디렉토리 형식이 G-12 자신의 예시(../inbound-request/#reqlist)와 일치, BR-37 인용 정확 · [G-13]/[G-14] — §2.6 rows 5·9·10·11 N/A 선언과 §9.3 소유 스펙 지정 정합 · [G-15] 단일 롤 — BR-26, E-29, QA-VAL-12의 실질(전원 실행 가능+actor 기록)이 전역과 일치 · [G-7] HUB-1~4 문자열 — §3.6 인용 4종이 전역 캐노니컬과 byte-identical; 배지=미읽음 멘션 수 시맨틱스 일치; 풀 아이템의 1급 코멘터블 엔티티 지위·source=system 파이프라인 일치

## 전역규칙 준수 감사 — view-orders.md vs _global-rules.md (기준선 review-baseline-20260803): 재서술·모순·[G-n] 오인용·CONFIRMED 미반영 사냥

### [C-112] MAJOR — M6 사유 enum의 세 번째 옵션 문자열이 두 정본에서 다르다 — [G-11]은 "exact enum"으로 "Other (memo)"를 박아두었는데 스펙(BR-53, QA-S6-13)은 정확히 `Other`를 규범으로 선언하고 [G-11]의 문구를 재해석으로 무력화한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "Expected-quantity edits are allowed with a **mandatory reason** — exact enum: "Damaged/defective — cannot accept" / "Supplier qty change" / "Other (memo)"."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "M6's third reason option label is exactly `Other`. `[G-11]`'s "Other (memo)" phrasing names the memo obligation, not the option string."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "Then its `select` has exactly 3 options and the third option's text is exactly `Other` — not `Other (memo)` `[G-11]`"

주: 스펙은 _review.md C-11로 국지 판정했지만 G-11 본문은 v1.2까지 미수정 — "exact enum"이라는 전역규칙의 자기 선언과 정면 충돌. 계약상 바이트 정확 문자열은 전역규칙이 정본이어야 하므로(G-7 HUB 사례처럼) G-11 본문을 `Other`로 고치는 게 정합. QA-S6-13은 두 문서 중 어느 쪽을 읽느냐에 따라 다른 문자열을 단언하게 된다.

### [C-113] MAJOR — [G-10]이 CONFIRMED(owner, PD-8)로 확정한 내용(추적번호 시스템 전역 유일 + 인바운드/아웃바운드 별도 네임스페이스 + 인바운드 우선 해석)을 스펙 본문이 여전히 PD-82·PD-86 OWNER-PENDING에 걸어두고 있으며, 이 두 태그는 헤더의 supersede 면책 목록(PD-1~8, 51, 55, 66, 71, 74, 79)에 없어 면책되지 않는다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "An inbound tracking number is **unique system-wide** — registering one that already exists on another inbound request is blocked. Inbound (supplier→warehouse) and outbound (warehouse→customer) tracking numbers are separate namespaces and may coincide; View Orders resolution precedence puts inbound-request tracking first (State 6). **CONFIRMED 2026-08-03 (owner, PD-8).**"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "when a scanned number exists in both, inbound-request tracking wins `[PD-8 · OWNER-PENDING]` `[PD-86 · OWNER-PENDING]` `[E-8]`"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "Prevented upstream at Inbound Request save `[PD-82 · OWNER-PENDING]`; if it ever occurs, this page's resolution is non-deterministic"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "PD-1 through PD-8, 51, 55, 66, 71, 74, 79 are now **OWNER-DECIDED** (PD-6 confirmed 2026-08-03 — the owner decision round is fully closed); any inline `[PD-{these} · OWNER-PENDING]` or `[PD-{these} · NO-DEFAULT]` tags below are superseded"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "A tracking number is unique across inbound requests; a duplicate is blocked at Inbound Request save | `[E-64]` `[PD-82 · OWNER-PENDING]` | provisional"

주: PD-86/PD-82가 레지스터에서 PD-8의 세부 별건일 가능성은 있으나, 두 산출물만 대조하면 동일 문장이 한쪽은 CONFIRMED, 한쪽은 owner-pending·provisional — 구현자가 확정 규칙을 가역으로 오판할 수 있는 상태 모순.

### [C-114] MAJOR — [G-4]는 "우리가 디자인하는 것은 내부 인보이스(PACKING)뿐"이라고 확정(CONFIRMED, owner)했는데, 스펙 M4는 우리가 내용을 구성하는 별도의 공급사 반품 라벨(운송사명+한글 상품명+사이즈+수량, 생략 규칙, 라이브 프리뷰)을 규범으로 정의하고 그 물리 레이아웃을 Phase 3-1로 넘긴다 — 그러나 §9.1의 Phase 3-1 범위(DELEO A4·YUN 4×6·샘플 듀얼뷰)에도 M4 라벨은 없다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "no custom carrier-label layout exists or will be built, for YUN, DELEO, or any carrier added later (e.g. FedEx). Only the internal invoice ("PACKING") is ours to design — see `specs/shipping-label.md`. **CONFIRMED 2026-08-03 (owner).**"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "Printing puts carrier name + product name (KR) + size + qty on the label — size/qty omitted if empty; attach it to the return box."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "**Out of scope:** the label's physical layout — that is Phase 3-1 (§9.1)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "**Label and invoice layout content** — what is physically on the DELEO A4 picking sheet and the YUN 4×6 carrier label, including the sample dual view | **Phase 3-1** (separate owner session, after Phase 3)"

주: G-4의 해당 절이 '고객 출고용 캐리어 라벨' 한정이라는 화해적 독해는 가능하나, "Only …" 배타 문장의 자면과 M4의 자체 디자인 라벨은 양립 불가. Phase 3-1 계획에서 M4 반품 라벨 템플릿이 누락될 실무 리스크가 있어 G-4 문장의 범위 한정(또는 M4 명시 편입)이 필요.

### [C-115] MINOR — [L-S1-6]은 [G-5]가 order-facing 배지를 "exactly 4"라고 말한다고 인용부호까지 붙여 주장하지만 G-5 본문에 그 표현은 없고("Order-facing badges (4)"), G-5는 이미 자체적으로 OTHER의 다운스트림 렌더링을 규정하고 있어 '전역규칙과 어긋나는 다섯 번째 값'이라는 델타 프레이밍 자체가 과장이다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "**Order-facing badges (4):** SMART BUY · JIT (purchase channel in parentheses: Coupang / Naver / Other retail) · WHOLESALE · PARTNERSHIP."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "OTHER renders downstream as black bold `OTHER (channel)` `[PD-80 · OWNER-PENDING]`."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "`[G-5]` states the order-facing badge set as "exactly 4"; this page renders a fifth **display** value"

주: 실체적 충돌(어느 표면이 OTHER를 렌더하는가)은 CP-3로 자가 신고돼 있음 — 신규 발견은 존재하지 않는 문구를 G-5에 귀속시킨 오인용 부분.

### [C-116] MINOR — PARTIAL 배지의 분수 의미가 상충한다 — [G-11]은 "PARTIAL (n/m remaining)"이라 하는데 스펙은 일관되게 {received}/{expected}(예: 620/800, 620=수령분)를 렌더한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "`REQUESTED → PARTIAL (n/m remaining, amber) → INBOUNDED`."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "Status renders `REQUESTED` (amber) or `PARTIAL {received}/{expected}` (amber, `.row-part` tint)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "the request becomes `PARTIAL 620/800`; State 0's Expected Inbound table shows the amber `PARTIAL 620/800` row"

주: 620/800에서 remaining은 180이므로 G-11의 "remaining" 자면과 불일치. G-11이 'n of m, 잔여 있음'의 축약이었을 개연성이 높으나 자면 그대로 구현하면 다른 숫자가 나온다 — G-11 괄호 문구 정정 권고.

### [C-117] MINOR — [G-2](CONFIRMED, PD-5)는 파괴적 액션에 확인 다이얼로그를 요구하고 스펙 자신도 "이 페이지의 파괴적 액션은 항상 confirm step을 거친다"고 단언하는데, Cancel Outbound([L-S3-2])는 클릭 즉시 상태를 롤백하며 어떤 확인 단계도 서술되지 않는다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "**Every removal/deletion-class (destructive) action takes a confirm dialog, plus a reason where the flow already carries a reason field, plus the toast.** **CONFIRMED 2026-08-03 (owner, PD-5).**"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "Destructive actions on this page always carry a confirm step and a stated confirmation `[PD-5 · OWNER-PENDING]` `[G-2]`."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "**Trigger:** clicking `Cancel Outbound` (`.btn-red-line`) on an outbounded order.
- **Behavior:** rolls the order status back **`prepare shipment` → `processing`**."

주: 쟁점은 Cancel Outbound가 removal/deletion-class인가의 분류 — Cancel Inbound는 M1 다이얼로그를 받는데 같은 cancel 계열인 Cancel Outbound만 무확인이라 어느 쪽이든 경계 선언이 필요. 부수: §10.1은 G-2의 "a reason where the flow already carries a reason field"를 "a reason where an enum exists"로 다르게 재서술.

### [C-118] MINOR — 스펙 헤더가 전역규칙을 "v1.0"으로 핀해 인용하지만 실제 _global-rules.md는 v1.2이고, 스펙 본문 자체가 v1.2에서만 존재하는 내용([G-7] HUB-1…HUB-7)에 의존한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "**Global rules:** `_global-rules.md` v1.0 — cited as `[G-n]`; this document states **page deltas only** and never restates a rule body."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "Version 1.2 · 2026-08-03 · Applies to all 8 screen specs."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "`[G-7]` v1.2 (2026-08-03) publishes them as **HUB-1…HUB-7**"

### [C-119] MINOR — 정본 이벤트명 개수가 세 군데서 다르다 — 전역규칙 목록은 9개 그룹(슬래시쌍 포함 11개 리터럴), 스펙 §5는 "9 groups covering 11 literal names", §9.5 CP-7은 "The 10 canonical names"라고 셈해 어느 집계와도 맞지 않는다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "`comment.posted` · `comment.mention_notified` · `comment.starred` / `comment.unstarred` · `comment.read` / `comment.mark_all_read` · `comment.auto_posted` (`source=system`) · `product.barcode_registered` · `order.status_changed` · `order.outbounded` · `print.job_result`."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "The canonical cross-page names — **9 groups covering 11 literal names** — must be byte-identical wherever they appear"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "The 10 **canonical** names are byte-identical everywhere; this is the tier below them."

### [C-120] MINOR — BR-44와 BR-45는 [G-9]·[G-10]의 규칙 본문을 [G-n] 인용 없이 사실상 그대로 재서술한다 — "델타만 서술, 본문 재서술 금지" 계약 위반이며, 같은 감사가 BR-33~36은 이미 정리했다고 기록한 것과 대비된다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "**Concurrent edits** by two operators resolve by optimistic version check → 409 → reload the row + non-green toast; counting flows (State 6 receive, closing scans) merge server-side instead."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "Concurrency: order-level edits use an optimistic version check → 409 → reload the row + non-green toast. **State 6 counting merges server-side** instead, because the value is a running total. | Last-write-wins would destroy counted units; merge is correct only where the value accumulates. | 2026-08-03 `[PD-7 · OWNER-PENDING]`"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "An inbound tracking number is unique system-wide. Inbound and outbound tracking numbers are **separate namespaces** and may coincide; when they do, inbound-request tracking wins the resolution."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "the `[G-*]`-restating rows `BR-33`…`BR-36` reduced to page deltas"

주: 내용 자체는 G-9/G-10과 일치하므로 행위 모순은 아님 — 계약(재서술 금지) 위반 및 인용 누락. BR-44는 G-9의 "concurrent edits"를 "order-level edits"로 좁혀 재서술한 점도 미세 차이.

### [C-121] MINOR — 전역규칙이 "오너 결정 라운드 완전 종료, PD-1~8 등 확정"이라 선언했는데 스펙 §9.2는 PD-1~8을 여전히 '제공적 디폴트(provisional default) 33개'에 포함시키고 PD-66만 결정됐다고 단서 달며, §10.1 상태열도 PD-1/3/4/5/6/7/8 행을 "provisional"로 남겨둔다 — 헤더 면책은 '인라인 태그'만 supersede하므로 이 산문·상태열은 미커버.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "PD-1 through PD-8, 51, 55, 66, 71, 74, 79 were owner-decided on 2026-08-03 — their register entries carry the ruling. The owner decision round is fully closed"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "Owner questions that **do** have a provisional default are **not** repeated here — they live in the PD register and are tagged inline in §3/§4/§5/§7 where the behavior appears. This page rests on **33** of them: `PD-1, 2, 3, 4, 5, 6, 7, 8, 9, 10,"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "| 2026-08-03 | Comments are **append-only** | `[BR-33]` `[PD-3 · OWNER-PENDING]` | provisional |"

### [C-122] MINOR — [G-1] 불변식 1은 "이전 값이 선택된 채(previous value selected)" 포커스 복귀를 요구하고 델타가 불변식을 제거하는 것을 금지하는데, [L-S6b-2]는 입력을 비우는(emptied) 동작을 [G-1]을 인용하며 서술한다 — 자면상 불변식 1의 절반을 제거하는 델타인데 [L-S1-12]의 페이지 내부 예외로만 선언돼 있다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "after every action, focus returns there with the previous value selected (so the next scan overwrites it)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "Page deltas may add local behavior (e.g. Closing disables the input before the count is entered), never remove the three invariants above."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "on completion the search input is re-focused and **emptied** (its placeholder becomes `Scan a tracking barcode — continue with the next one`), ready for the next tracking scan `[G-1]`"

주: 기능적 취지(다음 스캔이 무타건으로 덮어씀)는 보존됨 — 빈 입력도 덮어쓰기와 등가. 다만 G-1 자면과의 어긋남을 [G-1] 델타로 명시 선언하는 편이 정합.

### [C-123] MINOR — BR-36은 KR 상품명 열에도 굵은 EN 브랜드가 붙는다는 것을 "Page delta on [G-6]"·"two-column repetition is page-specific"이라고 주장하지만, 그 내용은 [G-6]이 이미 전역으로 규정한 본문이라 델타가 아니라 재서술이다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "Korean product names also carry the EN brand in bold (e.g. **Dr.Jart+** 포어레미디 리뉴잉 폼 클렌저)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "**Page delta on `[G-6]`:** the brand-in-bold prefix applies to **both** the `Product Name` and `Product Name KR` columns of this page's tables `[L-S1-18]`, and to the product lists inside M2, M2b and M4."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "The two-column repetition is page-specific: pickers read whichever column their eye lands on first, so the brand must anchor both."

주: 모달 상품 리스트(M2/M2b/M4)로의 확장만이 진짜 페이지 고유분 — 그 부분으로 델타 서술을 좁히면 해소.

### [C-124] MINOR — QA-M2-11은 #unrecognized-tracking 채널 알림 문구 검증에 [G-7]을 키로 달았지만, [G-7]은 코멘트 시스템(#fulfillment-admin-comments 멘션 알림)에 관한 규칙이고 미인식 풀 Slack 라우트는 전역규칙의 별도 Slack routing 표 소관이라 오귀속이다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "**QA-M2-11 [WF]** `[L-M2b]` `[G-7]`
Given `#m-unrec2` is open, Then its note is exactly `On send, the #unrecognized-tracking channel gets an "Unrecognized product added" alert"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "`@mention` notifies the mentioned person through Slack: **#fulfillment-admin-comments** (`C0BMGEWM5QA`)"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "| Unrecognized barcode sent to the Missing Tracking List | `#unrecognized-tracking` | tracking no., product, qty, memo, registrant, suspected orders |"

### [C-125] MINOR — 딥링크 경로 형식이 두 문서에서 다르다 — [G-12]는 `../inbound-request/#reqlist` 형식을 쓰고 스펙·QA는 `../inbound-request/index.html#reqlist`만을 이 페이지의 유일 허용 형식으로 규정한다 (스펙이 CP-8로 자가 신고했고 수정을 G-12에 배정했으나 G-12 본문은 기준선 시점 미통일).

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "e.g. View Orders State 6 banner → `../inbound-request/#reqlist` opens the Request List tab."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md`: "`[G-12]`'s illustrative directory form (`../inbound-request/#reqlist`) is a cross-page inconsistency, not a second permitted form on this page (§9.5 CP-8)."

주: 신규 발견 아님(자가 신고 CP-8) — 기준선에서 미해소 상태임을 확인하는 기록.

**대조 후 이상 없음:** [G-7] 허브 정본 문자열 HUB-1…HUB-7 — 스펙 [L-S1-3]·§2.4 WF-VO-1·QA-C-03/05/06/07/10/11/18의 인용을 전건 바이트 대조, 전부 일치. reading rule 2(entity여도 'order' 유지)도 QA-C-10에 정확 반영 · [G-3] 오디오 — 발신음 3개 컨트롤 스코프가 G-3a의 View Orders 열거(Outbound·Inbound+Outbound·bulk)와 일치, State 6 경고음=G-3c 일치, TTS는 Closing 전용(G-3b) 준수(§6.5) · [G-2] 리프레시 — RTO 단독 예외와 이 페이지 제로 예외 델타(BR-31) 정합; BR-51 ✓ Saved 칩은 위치 델타로 자가 선언·일자 기록(CP-9로 경계 문제 별도 신고됨) · [G-8] — 뷰=이벤트 투영 독트린, NON-event 선언(§5.9), ⓒ 마킹 9그룹의 이벤트명 바이트 대조 전부 일치; 페이지 스코프 5개 이름의 비정본 선언(CP-7)도 명시적 · [G-9] — 더블클릭 멱등(E-13/DC-13/BR-34), 버전체크 vs State 6 머지 분리 내용 일치(BR-44는 재서술 형식 문제만) · [G-10] 다중 추적번호 매칭·부분 도착 누적(BR-17, [L-S6-1], QA-S6-38) — 행위 내용 일치(PD 상태 표기 문제만 별도 등재) · [G-11] 라이프사이클 3단계, 기대수량 편집의 M6 단독 기원, 자동 코멘트+요청자 Slack 알림 — 일치(enum 문자열·PARTIAL 표기만 등재) · [G-12] 링크 실링크화·프로덕션 필터 딥링크 서술 — 일치(경로 형식 CP-8만 등재) · [G-13] — 이 페이지에 샘플 컨트롤 없음·Order Management 소유 명시(§9.1), 듀얼뷰 언급도 G-13 v1.2 내용과 부합 · [G-14] — 1:1 위치 규칙의 PD-46 provisional 상태가 양 문서 동일([L-S6-7]·[L-M1]·BR-21·E-6/E-82) · [G-15] — 단일 admin 롤·행위자 기록(§1.2, BR-35, QA-NG-11) 일치 · Slack routing 표 4개 라우트 — 채널·채널ID(C0BMGEWM5QA)·페이로드·멘션 대상 전부 일치, '이 페이지에서 라우팅 안 하는 것' 목록도 전역 표와 무충돌, PD-4 재시도 시맨틱(BR-42/E-40) 일치

## 전역규칙 준수 감사 — inbound-request.md vs _global-rules.md (기준선 review-baseline-20260803, 모순 사냥)

### [C-126] MAJOR — 오너 확정(PD-79)된 CANCELLED 터미널 상태·편집/취소 알림이 _global-rules에 미반영 — [G-11] 라이프사이클, [G-7] 시스템 자동코멘트 열거, Slack 라우팅 표가 스펙과 모순된다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "`REQUESTED → PARTIAL (n/m remaining, amber) → INBOUNDED`."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "The **receive pipeline has exactly three stages** — `REQUESTED` → `PARTIAL (n/m)` → `INBOUNDED` — plus one **terminal branch**: `REQUESTED → CANCELLED` (2026-08-03)."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "System auto-comments (expected-qty edit, unrecognized match-confirm) use the same pipeline with `source=system`."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "`trigger` ∈ `memo_materialization\|expected_qty_edit\|unrecognized_match_confirmed\|request_edited\|request_cancelled`"

주: grep 확인: _global-rules.md에 'CANCELLED' 0건. 스펙 §6.1 rows 7–8(Request edited/cancelled → #fulfillment-admin-comments @requester, 'Owner decision 2026-08-03 (PD-79 resolved)')에 대응하는 행이 전역 Slack 라우팅 표(6행)에 없다 — 유사 성격의 expected-qty edit 자동코멘트는 전역 표에 자체 행이 있으므로 단순 생략으로 보기 어렵다. PD-79는 전역규칙 헤더가 오너 확정으로 명시한 항목이므로 수정 방향은 _global-rules([G-11] CANCELLED 분기 추가 + Slack 표 2행 + [G-7] 트리거 열거 갱신) 쪽.

### [C-127] MAJOR — M1 동시 저장을 서버측 merge로 규정한 스펙이 [G-9](CONFIRMED, PD-7)의 동시성 모델과 모순 — G-9는 merge를 'counting flows (State 6 receive, closing scans)'에만 허용하고 그 외 동시 편집은 409인데, 스펙은 델타 선언 없이 [PD-7] 인용 하에 트래킹번호 세트 merge를 규정한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "**Concurrent edits** by two operators resolve by optimistic version check → 409 → reload the row + non-green toast; counting flows (State 6 receive, closing scans) merge server-side instead. **CONFIRMED 2026-08-03 (owner, PD-7).**"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "**Concurrency.** Two operators saving different sets for the same request resolve by **server-side merge of the number set** (numbers are additive, not a replaced field), with a version check on the request itself; a genuine conflict returns 409"

주: M1 트래킹번호 저장은 counting flow가 아니다. 같은 시나리오(두 오퍼레이터가 서로 다른 번호 세트 저장)에서 G-9 문자 구현=후발 409, 스펙(QA-D-14 'the server merges the sets … no number is lost')=merge — 구현이 갈린다. 스펙은 G-11 델타들과 달리 이를 델타로 선언하지 않고 [PD-7 · OWNER-PENDING] 인용으로 처리했다. 참고: 레지스터 PD-7의 Pages에 'IR E-39'가 올라 있어 코퍼스 의도는 merge 승인일 수 있으나, 레지스터 rationale('merge is correct only where the value is a running total')과도 상충 — [G-9] 문구를 additive-set까지 넓히거나 스펙에 델타 선언이 필요.

### [C-128] MAJOR — 스펙이 [G-11]의 두 문자를 오기로 선언하고 '정정 예정'이라 했으나 _global-rules v1.2에 정정이 반영되지 않아 PARTIAL 표기(n/m remaining vs received/expected)와 M6 사유 enum 3번째 옵션(Other (memo) vs Other)이 두 문서에서 모순 상태로 남아 있다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "a request expecting 180 with 120 received renders `PARTIAL 120/180`, never `PARTIAL 60/180`. `[G-11]`'s parenthetical is a wording slip in the rule, not a different behavior"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "exact enum: "Damaged/defective — cannot accept" / "Supplier qty change" / "Other (memo)""
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "**the option label is `Other`**, the memo is a separate mandatory field when that option is chosen, and the persisted `DC-8` value stays `reason=other`. `[G-11]`'s enum text is to be corrected to match"

주: 둘 다 스펙이 §3.3.5에서 'Declared [G-11] delta'로 선언한 항목(리뷰 판결 C-11, View Orders BR-53과 정렬). 그러나 [G-11]은 'exact enum'을 표방하는 규칙이고, _global-rules는 같은 날 v1.1→v1.2로 두 차례 개정되면서도 이 정정을 싣지 않았다. 마감 전 [G-11] 본문 정정('PARTIAL ({received}/{expected}, amber)' + enum 3번째 'Other') 필요 — 스펙 측 변경은 불필요(스펙 자체 명시).

### [C-129] MAJOR — PD-66이 오너 확정(전역규칙 헤더 명시)됐는데 스펙 §9.2 OQ-2는 여전히 'No behavior is specified on either side / Owner decision required'로 미결 상태를 규범 서술한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "PD-1 through PD-8, 51, 55, 66, 71, 74, 79 were owner-decided on 2026-08-03 — their register entries carry the ruling. The owner decision round is fully closed"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "*No behavior is specified on either side.* **Owner decision required.**"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_plans/_provisional-decisions.md`: "**OWNER-DECIDED 2026-08-03**: The case does not exist — either a tracking number or an order number is always present. The current registration contract (an identifier is required) stands."

주: 같은 확정 목록의 PD-79는 OQ-1이 'RESOLVED 2026-08-03 (owner)'로 재작성됐는데 OQ-2(PD-66)만 미갱신 — 비대칭이 누락을 방증. 스펙 3행의 일괄 supersede 선언은 '[PD-{these} · OWNER-PENDING]/[PD-{these} · NO-DEFAULT] 태그'만 커버하며, OQ-2의 본문 서술('Owner decision required')과 §9.2 섹션 배치(NO-DEFAULT open questions)는 태그가 아니라 커버되지 않는다. 오너 결정(케이스 부존재)이 BR-19 회복 루프의 전제를 확정하므로 OQ-2를 RESOLVED로 재작성해야 한다.

### [C-130] MAJOR — 스펙 §9.1이 Comments-hub 캐노니컬을 아직 미발행 상태('follows [G-7] once the six shared strings are canonicalised')로 서술하나, [G-7] v1.2는 일곱 개 문자열(HUB-1…HUB-7)을 이미 확정 계약으로 발행했고 스펙 자신의 §3.1.13도 적용 완료를 기록한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "This page ships its wireframe's strings and follows `[G-7]` once the six shared strings are canonicalised (§3.1.13, QA-F-11)"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "**[G-7] publishes the seven canonical hub strings** (HUB-1…HUB-7) as byte-exact cross-page contract, closing cross-page defect M3a D7."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "`[G-7]` v1.2 published HUB-1…HUB-7 and **`[IR-WFX-1]` was applied**; the wireframe and QA-F-02 / QA-F-03 moved with it in the same commit"

주: §9.1 out-of-scope 표의 잔존 stale 행. 문자열 개수도 틀림(six vs seven — HUB-7 검색 플레이스홀더 포함 7종). 현재형 조건문이라 이력 서술로 볼 수 없고, 구현자가 이 행만 읽으면 캐노니컬이 아직 비구속이라 오독할 수 있다. 행을 '캐노니컬 발행·적용 완료(2026-08-03)' 상태로 재작성 필요.

### [C-131] MINOR — View Orders 해석 우선순위(inbound-request 우선)가 [G-10]에선 PD-8로 CONFIRMED인데 스펙은 같은 규칙을 [PD-86 · OWNER-PENDING]로 태깅해(§3.3.7·BR-16·[E-22]·QA-E-08·§6.3) 확정/미결 상태가 두 문서에서 충돌한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "Inbound (supplier→warehouse) and outbound (warehouse→customer) tracking numbers are separate namespaces and may coincide; View Orders resolution precedence puts inbound-request tracking first (State 6). **CONFIRMED 2026-08-03 (owner, PD-8).**"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "View Orders resolution precedence puts inbound-request tracking first (State 6) `[PD-86 · OWNER-PENDING]` (`[E-22]`)"

주: 행동 서술 자체는 양쪽 동일(우선순위 = inbound 우선)하나 결정 상태가 상충. PD-86은 스펙 헤더의 일괄 supersede 목록(PD-1~8, 51, 55, 66, 71, 74, 79)에 없어 선언으로 커버되지 않는다. 근본 원인은 레지스터 중복으로 보임: PD-8 OWNER-DECIDED 본문이 'View Orders resolution keeps inbound-request precedence'까지 포함하는 반면 PD-86 항목은 OWNER-DECIDED 줄 없이 provisional로 남아 있다. 마감 시 유령 미결 항목이 되므로 태그 정리(또는 레지스터 PD-86에 PD-8 흡수 명기) 권장.

### [C-132] MINOR — §3.3.7(및 BR-9)이 [G-10] 규칙 본문을 다른 표현으로 재서술하고 스스로 'primary home of [G-10]'을 자처해, '스펙은 인용만 하고 본문을 재서술하지 않는다'는 전역규칙 헤더 계약을 위반한다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "Screen specs cite these by ID (`[G-n]`) and describe **page deltas only** — they never restate a rule body."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "**Behavior.** One inbound request may hold **any number** of tracking numbers, because one purchase frequently ships as several parcels. Every registered number is an independent View Orders match/scan target, and partial arrivals accumulate against the same request until it is fully received [G-10]."
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "One inbound request may register several tracking numbers (split shipments). **Every** registered number matches in View Orders and enters the internal-inbound screen (State 6); partial arrivals accumulate against the same request until fully received. **CONFIRMED 2026-08-03.**"

주: 내용은 의미상 동일('several'→'any number'로 미세 강화)해 행동 리스크는 낮으나, 같은 스펙의 결정 로그가 '[G-7]'s rule body no longer restated in §3.1.13 (citation + delta only)'라며 재서술을 결함 클래스로 제거한 전력과 비일관. 또한 [G-13]처럼 전역규칙이 primary home을 지정한 사례와 달리 [G-10]은 primary home을 지정하지 않는데 스펙이 자처한다. 재서술부를 인용+델타로 압축하거나 [G-10]에 primary home 지정을 명기하는 정리 권장.

### [C-133] MINOR — §2.4 관찰 3이 Saved 페인 헤더를 '과반 없음'(split 5/1/2)으로 서술하나 [G-7] HUB-2 표는 같은 항목을 'majority 5/8'로 기록해 캐노니컬 산정 근거 서술이 모순된다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "Of those four, two had a corpus majority (mentions header `Comments mentioning me · Click to open the order`, 5 pages; read-all `Mark all read`, 6 pages) and two did not — the saved header split 5 / 1 / 2"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "| **HUB-2** | `★ Saved` pane header | `Saved comments · Click to open the order` | **majority 5/8** (same five) |"

주: 5/1/2 분포는 산술적으로 5/8 과반 존재 — '과반 없음'은 [G-7] 표와도, 분포 자체와도 안 맞는다. 과반 부재로 표준영어 근거 해소된 것은 unstar 힌트(HUB-3, 3/2/2/1)뿐. 규범 문자열 주장(HUB-2 값)은 양쪽 byte 일치라 행동 영향 없음 — 근거 서사만 정정하면 됨.

### [C-134] MINOR — §5 전문의 '전역 캐노니컬 목록이 ten names를 커버한다'는 수치가 틀렸다 — 실제 목록은 그룹 9개 / 개별 이벤트명 11개로 어느 셈법으로도 10이 아니다.

- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/inbound-request.md`: "because `_global-rules`' canonical list covers ten names and does not yet cover these"
- `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_global-rules.md`: "`comment.posted` · `comment.mention_notified` · `comment.starred` / `comment.unstarred` · `comment.read` / `comment.mark_all_read` · `comment.auto_posted` (`source=system`) · `product.barcode_registered` · `order.status_changed` · `order.outbounded` · `print.job_result`."

주: · 구분 그룹 9개(starred/unstarred, read/mark_all_read를 쌍으로 셈) 또는 개별 11개. DC-23/DC-15 네이밍 caveat 자체(선언된 로컬명, 캐노니컬 승격 시 rename-only)는 문제 없음 — 수치만 정정 대상.

**대조 후 이상 없음:** [G-1] N/A 선언 + Enter 규율 델타 (§1.5, §3.1.5, BR-24) — 스캔 표면 부재 선언과 G-1 적용 범위(View Orders·Closing) 일치, 델타는 3대 불변식을 제거하지 않음 · [G-2] no-refresh·확정 토스트 적용 (BR-28, §3.1.7 step 5, [L-F1], M1/M2 토스트, QA-A-18/D-04/C-26) — 유일 예외(RTO Bulk Outbound) 서술 일치, M2 취소=확인 다이얼로그+사유+토스트로 파괴적 액션 계약 충족 · [G-3]·[G-4] N/A 선언 (§1.5, §6.5, QA-G-10) — 전역 print surfaces 목록(View Orders·RTO·Order Detail)과 일치, 오디오·프린트 부재 어서션 정합 · [G-5] origin form 4루트(SMART BUY/WHOLESALE/PARTNERSHIP/OTHER)·JIT 비요청 루트·colorless black bold·OTHER({channel}) 렌더 [PD-80 pending 유지] (BR-2, §3.1.2, §3.1.9, §3.3.3, QA-A-02/C-07) — 전역과 정합 · [G-6] 브랜드 볼드 EN명·한국어 공급사명 데이터 보존 (§3.1.12, QA-B-03, QA-C-16) — 피킹 아티팩트 한국어명 조항의 N/A 스코핑도 정확 · [G-7] 캐노니컬 HUB-1…HUB-7 문자열 자체 — §3.1.13·QA-F-02/F-03/F-11의 7개 문자열 전건 byte 대조 일치, 엔티티 라벨(Inbound No.)만 페이지 델타로 선언됨(전역 reading rule과 일치), 채널 ID C0BMGEWM5QA 전 인용 일치 · [G-8] 데이터 캡처 독트린 (§5 전반, §5.4) — NON-events 목록이 G-8 예시 클래스(cancelled edits 포함)와 정합, 편집/취소 이벤트(DC-24/25)에 actor·old→new 디프 포함 · [G-9] 등록·M1·M2의 멱등성(디바운스+키, DC-23) 및 stale-conflict 409 처리(DC-22) — M1 merge 스코프 건 제외하고 정합 · [G-10] 인용부의 행동 내용(다중 트래킹·부분 누적·전건 매칭·유일성·네임스페이스 분리) — 재서술·PD-86 태그 건 제외하고 전역과 동일 · [G-11] 수량 편집(M6 단일 기원·필수 사유·자동코멘트·요청자 알림·이 페이지는 이력 표시만), 미매칭 도착의 unrecognized pool 라우팅(BR-19) — 선언된 두 문자 델타 건 제외하고 정합 · [G-12] deep link (#reqlist/#s3, 프로덕션 필터드 엔티티 해석) — [L-F5], §6.2, QA-C-01/G-07 전역 예시와 일치 · [G-13]·[G-14] N/A rows (§1.5, §9.1) — 샘플·로케이션·감사모드 조항의 명시적 N/A 스코핑 정확
