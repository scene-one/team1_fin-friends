#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼핀 리뷰 페인포인트 근거 — 최종 검수 · 확정 스크립트
========================================================

SeSAC AI Native PM 2차 역기획 프로젝트 · 새싹프렌즈 1팀 · 박하영

하는 일
-------
2단계 분류 결과(classification_labels.json)를 원문과 재대조해 검수하고,
근거 강도(직접/간접)와 개발사 답변을 붙여 최종 근거 파일을 만든다.

    → pain_point_evidence_final.csv

검수 항목 (전부 통과해야 확정)
------------------------------
1. 수기 인용문이 원문에 글자 그대로 존재하는가
2. review_id 중복이 없는가
3. 라벨 목록 안에 중복 인덱스가 없는가
4. 직접근거가 전체 근거의 부분집합인가
5. 학습흥미 긍정/부정이 겹치지 않는가
6. 빈 본문이 분류되지 않았는가

실행: python finalize_evidence.py
의존성: 파이썬 기본 라이브러리만 사용
"""

import csv
import json
import sys
from pathlib import Path

RAW = "puffin_reviews_raw.csv"
LABELS = "classification_labels.json"
OUT = "pain_point_evidence_final.csv"

# 아이 페인포인트 근거 강도
#   직접 = 아이 본인이 성장 결핍을 진술한 것
#   간접 = 부모가 관찰한 학습 미형성(대충 풀기·해설 안 봄·난이도 과소)
아이_직접 = []              # 921건 중 0건
아이_간접 = [338, 382, 715]

# 개발사가 해당 리뷰에 답변한 내용 중 앱 기능 판단에 쓰이는 것만 요지로 기록
답변요지 = {
    "445": "2023-09-21 · '부모님도 어떤 문제를 풀었는지 보실 수 있는 기능은 향후 지원할 예정' → 당시 미지원 확인",
    "382": "2023-11-21 · '어떤 문제를 푸는지 부모님도 함께 보실 수 있게 준비 중' → 당시 미지원 확인",
    "666": "2024-10-21 · '아이가 푼 퀴즈의 내용을 부모님의 앱 > 교육 메뉴에서도 확인하실 수 있도록 업데이트 되었다' → 기능 출시 확인",
    "338": "2024-04-01 · '다소 의도와 다르게 작동하는 케이스', '틀린 경우 보상을 받지 못하도록 하는 안을 적극 검토' → 퍼핀이 문제를 인정",
    "715": "2023-06-04 · '레벨이 올라가면서 점점 난이도는 높아져요', '퍼핀월드 퀴즈를 통해 성취의 경험을 얻길 바라요' → 레벨 기반 난이도 진행 존재",
    "725": "2023-05-19 · 앱 대신 웹사이트·블로그 참고 안내 → 가입 전 교육 수준 확인 수단은 앱 밖에만 존재",
    "104": "2025-05-23 · '플러스 멤버십은 플러스 퀴즈 5개씩 풀이 가능, 1년 기준 결제 비용을 다 받아가실 수 있는 구조' → 멤버십 요금이 보상으로 환원되는 구조",
    "121": "2025-03-11 · '플러스 퀴즈 콘텐츠에 영어가 더 있었으면 하는 의견이시군요! 적극 반영' → 콘텐츠 확장 요구 접수",
    "817": "2023-04-22 · '퍼핀월드는 재밌고 자연스럽게 생활 경제와 금융을 익힐 수 있도록 구현', '순차적인 업데이트 예정'",
    "870": "2023-04-04 · '말씀주신 기능과 이벤트 준비를 더욱 빠르게' → 콘텐츠 확충 요구 접수",
    "735": "2023-05-03 · '제안주신 기능 중 일부는 이미 개발 진행 중' → 학습 확인 기능이 개발 중이었음",
}


def _stdout_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def verify(rows, lab):
    """검수 6항목. 실패하면 목록을 돌려준다."""
    fails = []

    for k, v in lab["_수기근거"].items():
        t = rows[int(k) - 1]["review_text"]
        for part in [p.strip() for p in v["quote"].split(" / ")]:
            if part not in t:
                fails.append(f"인용문 불일치 idx={k}: {part[:40]}")

    ids = [r["review_id"] for r in rows]
    if len(ids) != len(set(ids)):
        fails.append(f"review_id 중복 {len(ids)-len(set(ids))}건")

    keys = ["아이_학습후_성장경험_부족", "부모_체계적_금융학습_확인_부족",
            "돈이_학습행동의_동기가_된_경험", "돈보상의_아쉬움_또는_부작용",
            "아이의_학습_지속_흥미_이용의욕_긍정", "아이의_학습_지속_흥미_이용의욕_부정",
            "부모의_금전적_보상부담", "참고_학습효과_긍정_언급",
            "부모_체계적_금융학습_확인_부족_직접근거"]
    for k in keys:
        L = lab[k]
        if len(L) != len(set(L)):
            fails.append(f"{k} 목록 내 중복")
        out_of_range = [i for i in L if not (1 <= i <= len(rows))]
        if out_of_range:
            fails.append(f"{k} 범위 이탈 {out_of_range}")

    if not set(lab["부모_체계적_금융학습_확인_부족_직접근거"]) <= set(lab["부모_체계적_금융학습_확인_부족"]):
        fails.append("P2 직접근거가 전체 근거의 부분집합이 아님")

    if set(lab["아이의_학습_지속_흥미_이용의욕_긍정"]) & set(lab["아이의_학습_지속_흥미_이용의욕_부정"]):
        fails.append("학습흥미 긍정/부정 겹침")

    everything = set()
    for k in keys:
        everything |= set(lab[k])
    empty = [i for i in everything if not rows[i - 1]["review_text"].strip()]
    if empty:
        fails.append(f"빈 본문이 분류됨: {empty}")

    return fails


def main():
    _stdout_utf8()
    here = Path(__file__).parent

    rows = list(csv.DictReader(open(here / RAW, encoding="utf-8-sig")))
    lab = json.loads((here / LABELS).read_text(encoding="utf-8"))
    classified = list(csv.DictReader(open(here / "puffin_reviews_classified.csv", encoding="utf-8-sig")))

    print("=" * 62)
    print("최종 검수")
    print("=" * 62)
    fails = verify(rows, lab)
    if fails:
        print("🔴 검수 실패:")
        for f in fails:
            print("  ✗", f)
        return 1
    print("✅ 검수 6항목 전부 통과 — 인용문 불일치 0 / 중복 0 / 범위이탈 0 / 빈본문 0")

    p1 = set(lab["아이_학습후_성장경험_부족"])
    p2 = set(lab["부모_체계적_금융학습_확인_부족"])
    p2_d = set(lab["부모_체계적_금융학습_확인_부족_직접근거"])
    c_pos = set(lab["아이의_학습_지속_흥미_이용의욕_긍정"])
    c_neg = set(lab["아이의_학습_지속_흥미_이용의욕_부정"])

    out = []
    for i, (r, c) in enumerate(zip(rows, classified), 1):
        out.append({
            "idx": i,
            "review_id": r["review_id"],
            "review_date": r["review_date"],
            "rating": r["rating"],
            "review_text": r["review_text"],
            "아이_학습후_성장경험_부족": c["아이_학습후_성장경험_부족"],
            "아이_근거강도": ("직접" if i in 아이_직접 else ("간접" if i in 아이_간접 else "")),
            "부모_체계적_금융학습_확인_부족": c["부모_체계적_금융학습_확인_부족"],
            "부모_근거강도": ("직접" if i in p2_d else ("간접" if i in p2 else "")),
            "돈이_학습행동의_동기가_된_경험": c["돈이_학습행동의_동기가_된_경험"],
            "돈보상의_아쉬움_또는_부작용": c["돈보상의_아쉬움_또는_부작용"],
            "아이의_학습_지속_흥미_이용의욕": c["아이의_학습_지속_흥미_이용의욕"],
            "학습흥미_방향": ("긍정" if i in c_pos else ("부정" if i in c_neg else "")),
            "부모의_금전적_보상부담": c["부모의_금전적_보상부담"],
            "참고_학습효과_긍정_언급": c["참고_학습효과_긍정_언급"],
            "대표_페인포인트": c["대표_페인포인트"],
            "근거가_되는_리뷰_원문": c["근거가_되는_리뷰_원문"],
            "분류_이유": c["분류_이유"],
            "최종_근거보유": "Y" if c["대표_페인포인트"] else "N",
            "원문대조_검수": "완료",
            "개발사_답변_여부": "Y" if r["developer_reply"].strip() else "N",
            "개발사_답변_요지": 답변요지.get(str(i), ""),
            "developer_reply": r["developer_reply"],
            "reply_date": r["reply_date"],
        })

    with open(here / OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(out)

    # ---------------- 확정 수치 ----------------
    total = len(out)
    print("\n" + "=" * 62)
    print(f"최종 확정 수치  (모수 {total}건)")
    print("=" * 62)
    print(f"{'항목':32s} {'건수':>5s} {'비율':>7s} {'직접':>5s} {'간접':>5s}")
    print("-" * 62)
    표 = [
        ("아이 — 성장 경험 부족", "아이_학습후_성장경험_부족", len(아이_직접), len(아이_간접)),
        ("부모 — 체계적 금융학습 부족", "부모_체계적_금융학습_확인_부족", len(p2_d), len(p2) - len(p2_d)),
        ("돈이 학습 행동의 동기", "돈이_학습행동의_동기가_된_경험", None, None),
        ("돈 보상의 아쉬움·부작용", "돈보상의_아쉬움_또는_부작용", None, None),
        ("학습 지속·흥미", "아이의_학습_지속_흥미_이용의욕", None, None),
        ("부모의 금전적 보상 부담", "부모의_금전적_보상부담", None, None),
        ("[참고] 학습효과 긍정 언급", "참고_학습효과_긍정_언급", None, None),
    ]
    for 이름, col, 직, 간 in 표:
        n = sum(1 for r in out if r[col] == "1")
        d = str(직) if 직 is not None else "-"
        g = str(간) if 간 is not None else "-"
        print(f"{이름:32s} {n:5d} {n/total*100:6.1f}% {d:>5s} {g:>5s}")

    print(f"\n근거 보유 리뷰: {sum(1 for r in out if r['최종_근거보유']=='Y')}건 "
          f"/ 해당 없음 {sum(1 for r in out if r['최종_근거보유']=='N')}건")
    print(f"학습흥미 방향: 긍정 {len(c_pos)}건 / 부정 {len(c_neg)}건")
    print(f"\n[저장] {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
