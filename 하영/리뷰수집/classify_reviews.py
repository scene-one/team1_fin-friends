#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼핀 리뷰 페인포인트 분류 — 라벨 병합 · 집계 스크립트
=======================================================

SeSAC AI Native PM 2차 역기획 프로젝트 · 새싹프렌즈 1팀 · 박하영

하는 일
-------
puffin_reviews_raw.csv(원본 921건) + classification_labels.json(전수 판독 결과)
→ puffin_reviews_classified.csv, pain_point_summary.csv 생성

판정 자체는 이 스크립트가 하지 않는다. 리뷰 921건을 사람이(=분석자가) 전문 판독해
classification_labels.json 에 idx 목록으로 기록했고, 이 스크립트는 그 라벨을
원본에 병합하고 숫자를 세기만 한다. 키워드 자동 분류가 아니다.

실행
----
    python classify_reviews.py

의존성: 파이썬 기본 라이브러리만 사용 (csv, json)
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

RAW = "puffin_reviews_raw.csv"
LABELS = "classification_labels.json"
OUT_CLASSIFIED = "puffin_reviews_classified.csv"
OUT_SUMMARY = "pain_point_summary.csv"

# 분류 컬럼 — 요청받은 6개 + 참고 1개
COLS = [
    "아이_학습후_성장경험_부족",
    "부모_체계적_금융학습_확인_부족",
    "돈이_학습행동의_동기가_된_경험",
    "돈보상의_아쉬움_또는_부작용",
    "아이의_학습_지속_흥미_이용의욕",
    "부모의_금전적_보상부담",
    "참고_학습효과_긍정_언급",
]

# 대표 페인포인트 결정 우선순위 (위에서부터)
PRIORITY = [
    "아이_학습후_성장경험_부족",
    "부모_체계적_금융학습_확인_부족",
    "돈보상의_아쉬움_또는_부작용",
    "부모의_금전적_보상부담",
    "돈이_학습행동의_동기가_된_경험",
    "아이의_학습_지속_흥미_이용의욕",
]

# A·C 항목의 근거 원문을 자를 때 쓰는 기준어 (원문에서 그대로 잘라낸다 — 요약·수정 없음)
ANCHORS_A = ["퀴즈", "문제", "학습", "퀘스트", "미션", "공부", "경제"]
ANCHORS_C = ["재미", "재밌", "재민", "좋아해", "좋아라", "흥미", "열심", "매일", "꾸준",
             "스스로", "빠짐없이", "푹 빠", "푹빠", "즐거", "의지", "앞으로도", "잘쓸", "안 쓰게", "쏠쏠"]


def _stdout_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def excerpt(text, anchors, width=90):
    """원문에서 기준어가 포함된 구간을 그대로 잘라낸다. 문자열을 바꾸지 않는다."""
    text = text.strip()
    if len(text) <= width:
        return text
    for a in anchors:
        pos = text.find(a)
        if pos != -1:
            start = max(0, pos - 30)
            end = min(len(text), start + width)
            piece = text[start:end]
            return ("…" if start > 0 else "") + piece + ("…" if end < len(text) else "")
    return text[:width] + "…"


def main():
    _stdout_utf8()
    here = Path(__file__).parent

    rows = list(csv.DictReader(open(here / RAW, encoding="utf-8-sig")))
    labels = json.loads((here / LABELS).read_text(encoding="utf-8"))

    manual = labels["_수기근거"]
    p1 = set(labels["아이_학습후_성장경험_부족"])
    p2 = set(labels["부모_체계적_금융학습_확인_부족"])
    p2_direct = set(labels["부모_체계적_금융학습_확인_부족_직접근거"])
    a = set(labels["돈이_학습행동의_동기가_된_경험"])
    b = set(labels["돈보상의_아쉬움_또는_부작용"])
    c_pos = set(labels["아이의_학습_지속_흥미_이용의욕_긍정"])
    c_neg = set(labels["아이의_학습_지속_흥미_이용의욕_부정"])
    d = set(labels["부모의_금전적_보상부담"])
    ref = set(labels["참고_학습효과_긍정_언급"])

    out = []
    for i, r in enumerate(rows, 1):
        text = r["review_text"]
        flags = {
            "아이_학습후_성장경험_부족": int(i in p1),
            "부모_체계적_금융학습_확인_부족": int(i in p2),
            "돈이_학습행동의_동기가_된_경험": int(i in a),
            "돈보상의_아쉬움_또는_부작용": int(i in b),
            "아이의_학습_지속_흥미_이용의욕": int(i in c_pos or i in c_neg),
            "부모의_금전적_보상부담": int(i in d),
            "참고_학습효과_긍정_언급": int(i in ref),
        }

        대표 = ""
        for key in PRIORITY:
            if flags[key]:
                대표 = key
                break

        # 근거 원문 · 분류 이유
        if str(i) in manual:
            근거 = manual[str(i)]["quote"]
            이유 = manual[str(i)]["reason"]
        elif flags["돈이_학습행동의_동기가_된_경험"]:
            근거 = excerpt(text, ANCHORS_A)
            이유 = "퀴즈·문제풀이와 금전 보상을 연결지어 긍정적으로 서술 — 보상이 학습 행동의 이유로 제시됨."
        elif flags["아이의_학습_지속_흥미_이용의욕"]:
            근거 = excerpt(text, ANCHORS_C)
            이유 = ("아이의 학습(퀴즈·투자체험) 흥미·지속·의욕을 언급 (긍정)."
                    if i in c_pos else
                    "아이가 앱 이용을 줄이거나 중단한다는 언급 (부정).")
        elif flags["참고_학습효과_긍정_언급"]:
            근거 = excerpt(text, ["경제", "지식", "금융", "배우", "배웠", "익히", "습관", "관념", "공부"])
            이유 = "아이가 경제·금융 지식을 실제로 익혔다는 경험 기반 서술 (핵심 페인포인트에 대한 반증 자료)."
        else:
            근거 = ""
            이유 = "6개 항목 어디에도 해당하지 않음 (기능 요청·오류 신고·단순 만족 표현 등)."

        방향 = "긍정" if i in c_pos else ("부정" if i in c_neg else "")

        out.append({
            "idx": i,
            **{k: r[k] for k in ["review_id", "review_date", "rating", "review_text",
                                 "reviewer_hash", "app_version", "thumbs_up",
                                 "developer_reply", "reply_date"]},
            **flags,
            "학습흥미_방향": 방향,
            "P2_근거강도": ("직접" if i in p2_direct else ("간접" if i in p2 else "")),
            "대표_페인포인트": 대표,
            "근거가_되는_리뷰_원문": 근거,
            "분류_이유": 이유,
        })

    fields = list(out[0].keys())
    with open(here / OUT_CLASSIFIED, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(out)

    # ---------------- 요약표 ----------------
    total = len(out)
    labels_kr = {
        "아이_학습후_성장경험_부족": "아이: 학습 후 성장 경험 부족",
        "부모_체계적_금융학습_확인_부족": "부모: 체계적인 금융학습 확인 부족",
        "돈이_학습행동의_동기가_된_경험": "돈이 학습 행동의 동기가 된 경험",
        "돈보상의_아쉬움_또는_부작용": "돈 보상의 아쉬움 또는 부작용",
        "아이의_학습_지속_흥미_이용의욕": "아이의 학습 지속·흥미·이용 의욕",
        "부모의_금전적_보상부담": "부모의 금전적 보상 부담",
        "참고_학습효과_긍정_언급": "[참고] 학습효과를 긍정 언급",
    }
    # 각 항목 대표 리뷰 = 수기근거가 있으면 그것, 없으면 해당 항목 중 가장 긴 근거
    reps = {
        "아이_학습후_성장경험_부족": 715,
        "부모_체계적_금융학습_확인_부족": 809,
        "돈이_학습행동의_동기가_된_경험": 612,
        "돈보상의_아쉬움_또는_부작용": 338,
        "아이의_학습_지속_흥미_이용의욕": 769,
        "부모의_금전적_보상부담": 844,
        "참고_학습효과_긍정_언급": 837,
    }

    summary = []
    for col in COLS:
        n = sum(r[col] for r in out)
        rep_idx = reps[col]
        rep_row = out[rep_idx - 1]
        rep_text = rep_row["근거가_되는_리뷰_원문"] or rep_row["review_text"]
        summary.append({
            "구분": labels_kr[col],
            "리뷰 건수": n,
            "전체 대비 비율": f"{n / total * 100:.1f}%",
            "대표 리뷰": rep_text,
            "대표 리뷰 날짜": rep_row["review_date"],
            "대표 리뷰 평점": rep_row["rating"],
        })

    with open(here / OUT_SUMMARY, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()), quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(summary)

    # ---------------- 콘솔 출력 ----------------
    print("=" * 64)
    print(f"퍼핀 리뷰 페인포인트 분류 결과  (전체 {total}건 전수 판독)")
    print("=" * 64)
    for s in summary:
        print(f"{s['구분']:28s} {s['리뷰 건수']:4d}건  {s['전체 대비 비율']:>6s}")

    classified = sum(1 for r in out if r["대표_페인포인트"])
    print(f"\n1개 이상 항목에 해당한 리뷰   : {classified}건 ({classified/total*100:.1f}%)")
    print(f"어느 항목에도 해당 없음        : {total-classified}건 ({(total-classified)/total*100:.1f}%)")
    print(f"P2 직접근거 / 전체            : {len(p2_direct)}건 / {len(p2)}건")
    print(f"학습흥미 긍정 / 부정          : {len(c_pos)}건 / {len(c_neg)}건")

    # 평점 교차
    print("\n[핵심 2개 항목의 평점 분포]")
    for col in ["아이_학습후_성장경험_부족", "부모_체계적_금융학습_확인_부족"]:
        cnt = Counter(r["rating"] for r in out if r[col])
        dist = " ".join(f"{k}점 {v}건" for k, v in sorted(cnt.items()))
        print(f"  {labels_kr[col]:28s} {dist}")

    # 연도 교차
    print("\n[핵심 2개 항목의 연도 분포]")
    for col in ["아이_학습후_성장경험_부족", "부모_체계적_금융학습_확인_부족"]:
        cnt = Counter(r["review_date"][:4] for r in out if r[col])
        dist = " ".join(f"{k}년 {v}건" for k, v in sorted(cnt.items()))
        print(f"  {labels_kr[col]:28s} {dist}")

    # 겹침
    both = sum(1 for r in out if r["아이_학습후_성장경험_부족"] and r["부모_체계적_금융학습_확인_부족"])
    a_and_b = sum(1 for r in out if r["돈이_학습행동의_동기가_된_경험"] and r["돈보상의_아쉬움_또는_부작용"])
    print(f"\n아이·부모 페인포인트 동시 해당 : {both}건")
    print(f"A(동기)·B(부작용) 동시 해당     : {a_and_b}건")

    print(f"\n[저장] {OUT_CLASSIFIED}, {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
