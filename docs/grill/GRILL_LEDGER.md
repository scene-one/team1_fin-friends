# 🔥 Grill Ledger — 핀프렌즈 서비스 계획 선명화

> 착수 전 미해소 **결정 토픽 원장**. 해소될 때마다 `wiki/` 해당 페이지 + 하네스(`CLAUDE.md`)에 반영하고 여기에 기록한다.
> 참조 범위: `wiki/` (지식베이스 35장) · 근거 원본 5종
> 세션 시작 2026-09-01

```
RESOLVED: 2 / TOTAL: 50
```

---

## S. 서비스 흐름 관점 (10)

- [x] S1 | CORE  | 아이 앱 홈의 기본 진입점 | status:RESOLVED | decision:**옷장/아바타 홈** — 아바타·펫·공간 키트가 첫 화면, 학습·실천은 하단 탭 | applied:`wiki/concepts/product/3층-구조.md` · `wiki/entities/services/핀프렌즈.md` · `CLAUDE.md`(원장 규칙 신설)
- [x] S2 | CORE  | 출석체크 ⭐ 지급 조건 | status:RESOLVED | decision:**접속만으로 ⭐1** — H2(저진도 아이)의 진입 문턱을 우선 | applied:`wiki/concepts/product/별-지급-엔진.md` · `wiki/concepts/product/WPA-북극성-지표.md`(제외 규칙 격상) · `wiki/index.md`(공백 #7 제거)
- [ ] S3 | CORE  | 「실천하기」 통합 화면의 4종 배치·미개통 칸(불리기) 처리 | depends:S1    | status:UNRESOLVED
- [ ] S4 | CORE  | 미션 사진 인증 플로우 확정 — v13이 PRD의 Out을 뒤집음 | depends:P1    | status:UNRESOLVED
- [ ] S5 | CORE  | 계획 카드 작성 상기 트리거 — 자동 발동이 사라진 자리를 무엇이 메우나 | depends:-     | status:UNRESOLVED
- [ ] S6 | CORE  | 업종 일치를 ⭐ 판정에 넣을지 (US-4 AC-E2 · 선결과제 ③) | depends:S5    | status:UNRESOLVED
- [ ] S7 | CORE  | F15 「가입 ⭐1」 판정 경로 — P-20과 충돌, 「선택 제출」로 사양 변경할지 | depends:P2    | status:UNRESOLVED
- [ ] S8 | MINOR | 나무 주기 초기화 · 월간 숲 스냅샷 확정 시점 (승인 지연 귀속) | depends:S2    | status:UNRESOLVED
- [ ] S9 | CORE  | 아이 전용 기기 부재(키즈워치·부모폰 공유) 시 아이 세션 진입 방식 | depends:S1    | status:UNRESOLVED
- [ ] S10 | MINOR | 예적금 완주 ⭐10의 중간 마디 — 12개월 뒤 보상 문제 | depends:S7   | status:UNRESOLVED

## C. 고객 관점 (10)

- [ ] C1 | CORE  | 1차 타깃 세그먼트 확정 — 「금융성장 증명형 29.3만」 유지 vs 재정의 | depends:-     | status:UNRESOLVED
- [ ] C2 | CORE  | 아이 연령 범위 확정 — 초1~3 vs 초1~6 (난이도 5단계와 정합) | depends:C1    | status:UNRESOLVED
- [ ] C3 | MINOR | 아동 화면의 `%` 표기 대체안 (30/70/100은 초6 과정) | depends:C2    | status:UNRESOLVED
- [ ] C4 | CORE  | 고객 인터뷰 0건 해소 계획 — 인원·시점·문항 | depends:C1    | status:UNRESOLVED
- [ ] C5 | CORE  | 부모 이자 지급 의향(검증과제 ③) 검증 방식 — 리뷰 「금전 부담」 7건 대치 | depends:C4    | status:UNRESOLVED
- [ ] C6 | MINOR | 부모 적금 이자 주기 — 주 단위 vs 월 단위 | depends:C5    | status:UNRESOLVED
- [ ] C7 | CORE  | 부모 적금 이율 — 연 20% 유지 vs 현실 정합(시중 최고 7.00%) | depends:C5    | status:UNRESOLVED
- [ ] C8 | CORE  | 아이 Pain 12건 → 부모 화면 신호 0건(R8) 해소 방식 | depends:C1    | status:UNRESOLVED
- [ ] C9 | CORE  | 난이도 5단계를 부모가 고를 수 있는가 — 부모 선택 vs 진단 배치 | depends:C2    | status:UNRESOLVED
- [ ] C10 | MINOR | 계획 초과(갈래 B) 회고 이탈 방지 설계 — 열람률 ≥70% 확보 수단 | depends:S6   | status:UNRESOLVED

## O. 운영 관점 (10)

- [ ] O1 | CORE  | 콘텐츠 제작량 연 7,300문항 대응 — 완화안·출시 순서 채택 여부 | depends:C2    | status:UNRESOLVED
- [ ] O2 | CORE  | 학습 콘텐츠 제작 주체·검수 프로세스 (누가 쓰고 누가 감수하나) | depends:O1    | status:UNRESOLVED
- [ ] O3 | CORE  | 미션 승인 병목 — 부모 미승인 시 SLA·리마인드·자동 만료 | depends:S2    | status:UNRESOLVED
- [ ] O4 | CORE  | 사진 인증 도입 시 운영 부담 — 보관 기간·삭제 주기·신고 대응 | depends:S4    | status:UNRESOLVED
- [ ] O5 | MINOR | 별 원장 정합성 온콜 체계 — 4인 팀에서 30분 SLA 실현 방법 | depends:-     | status:UNRESOLVED
- [ ] O6 | CORE  | 기술 스택 확정 — three.js 외 서버·DB·인증·분석이 전부 미정 | depends:-     | status:UNRESOLVED
- [ ] O7 | CORE  | β 클로즈드 8슬롯 모집 방법·기간·중도이탈 대체 | depends:C4    | status:UNRESOLVED
- [ ] O8 | CORE  | 선불업 제휴사 선정 프로세스·타임라인 (B안의 상대가 아직 없다) | depends:-     | status:UNRESOLVED
- [ ] O9 | MINOR | CS 채널 — 아동 직접 문의 허용 여부·부모 경유 원칙 | depends:O6    | status:UNRESOLVED
- [ ] O10 | MINOR | 주간 WPA 판정 운영 — 누가 언제 보고 무엇을 근거로 HOLD/FAIL 선언 | depends:O6   | status:UNRESOLVED

## R. 수익모델 관점 (10)

- [ ] R1 | CORE  | 수익 산출식 부재(R5) — 결제 수수료 + 제휴 2중 구조의 단가 가정 | depends:O8    | status:UNRESOLVED
- [ ] R2 | CORE  | 제휴사 수수료율·최소 물량 확보 (검증과제 ⑥) | depends:O8    | status:UNRESOLVED
- [ ] R3 | CORE  | 완전 무료 유지 확정인가 — 부분 유료화 가능성 검토 | depends:R1    | status:UNRESOLVED
- [ ] R4 | MINOR | 실물 카드 발급 유무·발급 비용 부담 주체 | depends:R2    | status:UNRESOLVED
- [ ] R5 | CORE  | 손익분기 사용자 수 — 29.3만 중 몇 %가 필요한가 | depends:R1    | status:UNRESOLVED
- [ ] R6 | CORE  | 금융사 제휴 수익 형태 — 계좌개설 CPA vs 잔액 연동 (P-20 충돌 검토) | depends:P2    | status:UNRESOLVED
- [ ] R7 | MINOR | 모집단 연 5~12% 감소(R6) 대응 — 진입 속도 목표치 | depends:C1    | status:UNRESOLVED
- [ ] R8 | CORE  | 졸업 설계 — 아이가 대상 연령을 벗어나면 무엇이 되나 (LTV) | depends:C2    | status:UNRESOLVED
- [ ] R9 | MINOR | 광고 모델 배제 확정 — 아동 대상 광고 규제 검토 포함 | depends:R1    | status:UNRESOLVED
- [ ] R10 | CORE | 수익 발생 시점 로드맵 — MVP 이후 언제 무엇으로 | depends:R1    | status:UNRESOLVED

## P. 규제 컴플라이언스 관점 (10)

- [ ] P1 | CORE  | 🔴 아동 이미지(미션 사진) 저장·보관 정책 — v13이 남긴 최대 공백 | depends:-     | status:UNRESOLVED
- [ ] P2 | CORE  | 🔴 P-20 「가입 연결」의 중개업 해당 여부 법률 검토 (검증과제 ⑤) | depends:-     | status:UNRESOLVED
- [ ] P3 | CORE  | 개인정보 보존기간·파기 정책 전반 (현재 미정의) | depends:P1    | status:UNRESOLVED
- [ ] P4 | CORE  | 법정대리인 동의 재확인 주기·철회 플로우 | depends:P3    | status:UNRESOLVED
- [ ] P5 | CORE  | 외부 SDK·국외이전 방침 (분석 도구·3D 에셋 CDN) | depends:O6    | status:UNRESOLVED
- [ ] P6 | MINOR | 선불충전금 별도관리 — 제휴사 종속이나 앱 내 표시 의무 범위 | depends:O8    | status:UNRESOLVED
- [ ] P7 | CORE  | 탈퇴·해지 플로우 — P-11 전액 환불과 별·나무·숲 데이터의 관계 | depends:P3    | status:UNRESOLVED
- [ ] P8 | MINOR | 아동 눈높이 고지 문구 검수 주체·주기 (개인정보보호법 §22의2③) | depends:P4    | status:UNRESOLVED
- [ ] P9 | CORE  | 🔴 부모 적금(앱 내 가상 이자)의 법적 성격 — 유사수신·선불 해당 여부 | depends:C7    | status:UNRESOLVED
- [ ] P10 | MINOR | 지오펜싱 서술 회수 완료 확인 — 대외 자료 정정 상태 | depends:-    | status:UNRESOLVED

---

## 해소 기록

### S1 — 아이 앱 홈의 기본 진입점 *(2026-09-01)*

**결정** 옷장/아바타 홈. 아이가 앱을 켜면 아바타·펫·공간 키트가 놓인 화면이 첫 화면이고, 학습·실천은 하단 탭.

**근거** 별(즉각 보상)은 「모은 것이 보이는 곳」이라 재접속 동기가 여기서 나온다. 3층 구조의 「양」 축을 진입점에 두고 「질」 축(나무·숲)은 부모 화면에 남긴다.

**받아들인 대가** 실천 동선이 한 단계 멀어져 WPA가 비용을 받는다. 홈에서 실천 미완을 알리는 수단이 필요 → **S3·S5로 이월**.

### S2 — 출석체크 ⭐ 지급 조건 *(2026-09-01)*

**결정** 접속만으로 ⭐1. 학습 완료를 조건으로 걸지 않는다.

**근거** 「학습 1개 이상」은 진도가 느린 아이(H2 유형)의 첫 성공 경험을 지연시키고, 그 집단이 학습→행동 전이 격차가 가장 큰 집단이다. 진입 문턱을 우선했다.

**받아들인 대가** H1의 우려(*"출석만 해도 주면 공부를 안 할 수도"*)는 해소되지 않았다. S1의 옷장 홈과 겹쳐 「켜기만 하면 옷 사는 앱」이 될 위험이 실재한다.

**의존하는 방어선 2개** ① WPA 분자에서 출석 ⭐ 제외 ② 나무 승급에 실천 횟수 필수. **①이 풀리면 이 결정도 철회 대상**이다.

**감시 지표** 출석률 × WPA 상관 r ≤ 0.3. 초과 시 주당 상한 도입 검토.
