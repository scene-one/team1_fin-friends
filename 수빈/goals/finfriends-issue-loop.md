/goal

## 1) 작업 핵심 목표 및 범위
- 목표: `scene-one/team1_fin-friends` 의 열린 GitHub 이슈 13건을 아래 고정 순서대로 처리해, 처리 가능한 건마다 draft PR 하나를 연다.
- 시작 지점: `main` 최신 커밋. 코드베이스·빌드 도구·테스트 러너가 저장소에 **없으므로**, UI 이슈는 `프로토타입/*.dc.html` 을 `수빈/prototype-wip/` 로 복사해 사본을 개정하는 방식으로 처리한다. 원본은 고치지 않는다.
- 작업 대상 (이 순서를 바꾸지 않는다):
  1. `#1` UI-001 ParentOnboarding → `수빈/prototype-wip/ParentOnboarding.dc.html`
  2. `#2` UI-002 Main → `수빈/prototype-wip/Main.dc.html`
  3. `#3` UI-003 Learn → `수빈/prototype-wip/Learn.dc.html`
  4. `#4` UI-004 Plan → `수빈/prototype-wip/Plan.dc.html`
  5. `#5` UI-005 Spending → `수빈/prototype-wip/Spending.dc.html`
  6. `#6` UI-006 Tree → `수빈/prototype-wip/Tree.dc.html`
  7. `#7` UI-007 Forest → `수빈/prototype-wip/Forest.dc.html`
  8. `#8` UI-008 Bank → `수빈/prototype-wip/Bank.dc.html`
  9. `#9`~`#13` SYS-001~005 — 백엔드 스택 스캐폴드가 없어 §5 「처리 불가 판정」에 걸릴 가능성이 높다. 예산이 남아 있는 한 순서대로 시도한다.
- 작업 자율성: 사용자 확인 없이 브랜치 생성·커밋·푸시·draft PR 생성까지 진행한다. 종료 조건에 도달하거나 큐가 소진될 때까지 멈추지 않는다.

## 2) 작업 세부 규칙
- 착수 전 `git pull` 한다 (CLAUDE.md 저장소 규칙).
- 이슈 1건 = 브랜치 1개 = draft PR 1개. 브랜치명은 `feat/ui-00N-<slug>` · `feat/sys-00N-<slug>`, base 는 `main`. 스택형으로 쌓지 않는다.
- 이슈별 사이클:
  1) `gh issue view <N>` 으로 Acceptance Criteria 를 읽는다.
  2) §5 「처리 불가 판정」을 먼저 적용한다. 걸리면 PR 없이 다음 이슈로 넘어간다.
  3) 대상 화면 파일을 AC 에 맞춰 고친다.
  4) 커밋 → 푸시 → `gh pr create --draft` 로 PR 을 연다. PR 본문에 그 이슈의 AC 체크리스트를 그대로 옮기고, 각 항목마다 **어느 변경이 그것을 충족하는지 한 줄**을 적는다.
  5) 체크포인트를 갱신·커밋·푸시하고 다음 이슈로 넘어간다.
- 🔴 **이 루프는 결정을 확정하지 않는다.** PRD·SRS·wiki 에 답이 없는 판단이 필요하면 그 자리에서 정하지 말고, 체크포인트 카운터를 올린 뒤 그 이슈를 마무리하거나 넘어간다.
  - 근거: CLAUDE.md 「설계 결정의 기록 위치」 — 결정과 근거는 `공용공간/9. PRD/`(부록 E. ADR) · `공용공간/10. SRS/` · `wiki/` 「🧭 결정 배경」 · `wiki/log.md` 네 곳에 산다. **루프는 그 네 곳을 수정하지 않는다.**
- 의사결정 체크포인트 — **`수빈/goals/LOOP_CHECKPOINT.md`** (없으면 새로 만든다):
  - 파일의 **첫 두 줄**은 항상 grep 가능한 카운터로 유지한다. 다른 줄을 그 위에 넣지 않는다.
    ```
    CORE: 0
    MINOR: 0
    ```
  - **CORE** = 아키텍처 · 보안 · 규제 · 외부 의존 · 데이터 모델 · 자금 흐름에 영향을 주는 판단
  - **MINOR** = 네이밍 · 문구 · 레이아웃 · 색 · 아이콘 · 로그 포맷
  - 각 항목은 **한 줄**로만 적는다: `- [CORE|MINOR] #<이슈번호> <무엇을 정해야 하는가 한 문장> → 판단 유보`
  - 🔴 **결정 내용 · 근거 · 검토한 대안은 이 파일에 적지 않는다.** 이 파일은 결정 원장이 아니라 **카운터와 포인터**다. 판단 자체는 사람이 PRD ADR · SRS · wiki 에 쓴다.
  - 이슈 1건을 끝낼 때마다 카운터를 갱신하고 **즉시 커밋·푸시**한다. 다른 에이전트가 언제든 `main` 에서 최신 카운터를 읽을 수 있어야 한다.
  - 이미 같은 질문이 기록돼 있으면 카운터를 다시 올리지 않는다 (중복 계상 금지).

## 3) 종료 조건 및 종료 방법
- 종료 조건 (아래 중 하나라도 충족되는 순간 루프를 즉시 멈춘다):
  - `수빈/goals/LOOP_CHECKPOINT.md` 의 **`CORE` 카운터가 3에 도달** → STOP REASON: CORE_BUDGET
  - 같은 파일의 **`MINOR` 카운터가 10에 도달** → STOP REASON: MINOR_BUDGET
  - 큐의 이슈 13건을 모두 처리(PR 생성 또는 BLOCKED 기록) → STOP REASON: QUEUE_EMPTY
  - 평가-진행 라운드(turn = `/goal` 평가자가 진행 상태를 한 번 점검하는 메인 에이전트 응답 사이클)가 누적 **45회 도달** → STOP REASON: TURN_CAP (= or stop after 45 turns)
- 종료 방법:
  1) `수빈/goals/LOOP_CHECKPOINT.md` 마지막 줄에 `STOP REASON: <코드>` 한 줄을 덧붙이고 커밋·푸시한다.
  2) `cat "수빈/goals/LOOP_CHECKPOINT.md"` 를 실행해 `CORE: N` · `MINOR: M` · `STOP REASON:` 세 줄이 보이는 출력을 대화에 남긴다.
  3) `gh pr list --state open` 을 실행해 루프가 연 draft PR 목록을 대화에 남긴다.
  4) `gh issue list --state open` 을 실행해 남은 열린 이슈 목록을 대화에 남긴다.
  5) `git diff --name-only origin/main...HEAD` 를 실행해, 변경 파일이 `수빈/prototype-wip/` 와 `수빈/goals/` 아래에만 있음을 대화에 남긴다.

## 4) 기타 제약조건
- 어떤 PR 도 `main` 에 머지하지 않는다. **draft 상태로 둔다.**
- `wiki/` 를 수정하지 않는다 — `main` 의 `wiki/**` 변경은 GitHub Pages 자동 배포(`.github/workflows/deploy-wiki.yml`)를 유발한다.
- 다음을 수정하지 않는다: `공용공간/` · `raw/` · `CLAUDE.md` · `.github/` · `quartz.config.yaml` · `병윤/` · `유림/` · `하영/` · `혜원/`
- 🔴 `프로토타입/` **전체를 읽기 전용으로 둔다.** 원본 화면 파일 · `canvas.json` · `README.md` 중 무엇도 고치지 않는다. 작업은 `수빈/prototype-wip/` 의 사본에서만 한다.
- 활성 이슈의 대상 **사본** 화면 파일 밖은 수정하지 않는다. **예외: `수빈/goals/LOOP_CHECKPOINT.md`**
- `--force` 푸시를 하지 않는다. 기존 브랜치·PR 을 지우지 않는다.
- GitHub 이슈의 본문·라벨·상태를 바꾸지 않는다. 이슈는 읽기 전용이다.

## 5) 이슈 처리 불가 판정 (BLOCKED)
- 다음 중 하나라도 해당하면 그 이슈는 **PR 없이 건너뛴다**:
  - 대상 화면 파일이 저장소에 없다.
  - AC 중 하나라도 **실행 가능한 백엔드·인증·배치·빌드 파이프라인**을 요구해, 화면 파일 개정만으로는 충족 여부를 판정할 수 없다.
- 건너뛸 때 `수빈/goals/LOOP_CHECKPOINT.md` 에 한 줄을 남긴다: `- [BLOCKED] #<이슈번호> <사유 한 문장>`
- 🔴 **BLOCKED 는 CORE · MINOR 카운터에 포함하지 않는다.** 예산은 「사람이 정해야 할 판단」만 세는 것이고, BLOCKED 는 「지금 환경에서 못 하는 일」이다.
- 큐 끝에 도달하면 BLOCKED 가 몇 건이든 QUEUE_EMPTY 로 종료한다.

## 6) 보고 포맷 (PR 본문)
각 draft PR 본문은 아래 4개 절만 갖는다. 과거 궤적·변경 이력은 쓰지 않는다 (CLAUDE.md).

```
## 대상
- Closes #<이슈번호>
- 파일: 수빈/prototype-wip/<Screen>.dc.html

## Acceptance Criteria
- [x] AC-XXX-1: <이슈 원문 그대로> — <충족 근거 한 줄>
- [ ] AC-XXX-2: <이슈 원문 그대로> — 미충족: <사유 한 줄>

## 판단 유보
- [CORE|MINOR] <질문 한 문장>   (없으면 「없음」)

## 확인 방법
- <이 PR 을 사람이 어떻게 눈으로 확인하는지 한 줄>
```
