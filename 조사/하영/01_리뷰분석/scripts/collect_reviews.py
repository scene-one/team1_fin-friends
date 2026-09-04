#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼핀(Puffin) Google Play 한국어 리뷰 수집 스크립트
====================================================

SeSAC AI Native PM 2차 역기획 프로젝트 · 새싹프렌즈 1팀 · 박하영

목적
----
1차 프로젝트에서 분석한 약 918건의 리뷰 원본이 남아있지 않아,
동일한 기준(한국어 / 최신순)으로 리뷰 원문을 다시 확보하고
재분석 가능한 형태(CSV·JSON)로 저장한다.

이 스크립트는 **수집만** 한다. 페인포인트 분류·요약·감성분석은 하지 않는다.
리뷰 원문(review_text)은 어떤 경우에도 가공하지 않는다.

설치
----
    python -m pip install google-play-scraper

실행
----
    python collect_reviews.py                    # 기본값으로 전체 수집
    python collect_reviews.py --max 300          # 300건만 (테스트용)
    python collect_reviews.py --out ./data       # 출력 폴더 지정

출력
----
    puffin_reviews_raw.csv    수집 원본 (UTF-8 BOM — 엑셀에서 바로 열림)
    puffin_reviews_raw.json   동일 데이터 JSON
    quality_report.json       데이터 품질 검사 결과
    collection_log.json       수집 실행 기록 (재현용 메타데이터)

개인정보
--------
작성자 닉네임(userName)은 저장하지 않는다.
대신 SHA-256 해시 앞 12자리를 reviewer_hash로 저장해,
동일인의 반복 리뷰는 식별하되 실명·닉네임은 남기지 않는다.
"""

import argparse
import csv
import hashlib
import json
import sys
import time
from collections import Counter
from datetime import datetime, date
from pathlib import Path

try:
    from google_play_scraper import Sort, app as gp_app, reviews as gp_reviews
except ImportError:
    sys.exit(
        "google-play-scraper 가 설치되어 있지 않습니다.\n"
        "  python -m pip install google-play-scraper\n"
        "를 먼저 실행하세요."
    )

# ---------------------------------------------------------------- 수집 설정

APP_ID = "family.firfin.app"          # 퍼핀 - 용돈관리, 금융교육, 청소년카드
APP_URL = f"https://play.google.com/store/apps/details?id={APP_ID}&hl=ko"
LANG = "ko"
COUNTRY = "kr"

BATCH_SIZE = 200        # 1회 요청당 리뷰 수 (구글이 사실상 허용하는 상한)
SLEEP_SEC = 1.0         # 요청 간 대기 — 차단 방지
MAX_RETRY = 3           # 요청 실패 시 재시도 횟수
DRY_STREAK_LIMIT = 3    # 새 리뷰가 0건인 페이지가 N회 연속이면 종료


def _stdout_utf8():
    """윈도우 cp949 콘솔에서 한글이 깨지지 않도록."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def anonymize(name):
    """작성자 닉네임 → 되돌릴 수 없는 짧은 해시."""
    if not name:
        return ""
    return hashlib.sha256(name.encode("utf-8")).hexdigest()[:12]


def to_iso(value):
    """datetime → ISO 문자열. None 이면 빈 문자열."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return ""


def to_day(value):
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    return ""


# ---------------------------------------------------------------- 수집 본체

def fetch_page(token, batch_size):
    """리뷰 한 페이지를 가져온다. 실패하면 백오프 후 재시도."""
    last_error = None
    for attempt in range(1, MAX_RETRY + 1):
        try:
            if token is None:
                return gp_reviews(
                    APP_ID,
                    lang=LANG,
                    country=COUNTRY,
                    sort=Sort.NEWEST,
                    count=batch_size,
                )
            # continuation_token 을 넘기면 나머지 인자는 토큰에 담긴 값이 쓰인다
            return gp_reviews(APP_ID, continuation_token=token)
        except Exception as exc:                       # 네트워크·차단·파싱 실패 전부
            last_error = exc
            wait = SLEEP_SEC * (2 ** attempt)
            print(f"  ! 요청 실패({attempt}/{MAX_RETRY}): {exc} — {wait:.0f}초 후 재시도")
            time.sleep(wait)
    raise RuntimeError(f"{MAX_RETRY}회 재시도 실패: {last_error}")


def collect(max_reviews=None, batch_size=BATCH_SIZE):
    """최신순으로 페이지를 넘기며 리뷰를 모은다. review_id 기준 중복 제거."""
    collected = {}          # review_id -> raw dict
    duplicates = 0
    pages = 0
    token = None
    dry_streak = 0
    stop_reason = "continuation_token 소진 (더 이상 페이지 없음)"

    while True:
        result, token = fetch_page(token, batch_size)
        pages += 1

        if not result:
            stop_reason = "빈 페이지 응답"
            break

        new_count = 0
        for raw in result:
            rid = raw.get("reviewId")
            if not rid:
                continue
            if rid in collected:
                duplicates += 1
                continue
            collected[rid] = raw
            new_count += 1

        print(f"  · {pages}페이지: 응답 {len(result)}건 / 신규 {new_count}건 / 누적 {len(collected)}건")

        if max_reviews and len(collected) >= max_reviews:
            stop_reason = f"--max {max_reviews} 도달"
            break
        if token is None:
            break
        if new_count == 0:
            dry_streak += 1
            if dry_streak >= DRY_STREAK_LIMIT:
                stop_reason = f"신규 0건 페이지 {DRY_STREAK_LIMIT}회 연속 — 더 받을 리뷰 없음"
                break
        else:
            dry_streak = 0

        time.sleep(SLEEP_SEC)

    rows = [normalize(r) for r in collected.values()]
    rows.sort(key=lambda r: r["review_datetime"], reverse=True)
    if max_reviews:
        rows = rows[:max_reviews]

    return rows, {
        "pages_fetched": pages,
        "duplicates_skipped": duplicates,
        "stop_reason": stop_reason,
    }


def normalize(raw):
    """google-play-scraper 응답 → 저장용 필드. 원문은 그대로 둔다."""
    return {
        "review_id": raw.get("reviewId", ""),
        "review_date": to_day(raw.get("at")),
        "review_datetime": to_iso(raw.get("at")),
        "rating": raw.get("score"),
        "review_text": raw.get("content") or "",       # 원문 무가공
        "reviewer_hash": anonymize(raw.get("userName")),
        "app_version": raw.get("reviewCreatedVersion") or "",
        "thumbs_up": raw.get("thumbsUpCount", 0),
        "developer_reply": raw.get("replyContent") or "",
        "reply_date": to_day(raw.get("repliedAt")),
        "reply_datetime": to_iso(raw.get("repliedAt")),
    }


FIELDS = [
    "review_id",
    "review_date",
    "review_datetime",
    "rating",
    "review_text",
    "reviewer_hash",
    "app_version",
    "thumbs_up",
    "developer_reply",
    "reply_date",
    "reply_datetime",
]


# ---------------------------------------------------------------- 품질 검사

def quality_check(rows, meta):
    """수집 결과를 검사한다. 분류·해석은 하지 않는다."""
    ids = [r["review_id"] for r in rows]
    dates = sorted(d for d in (r["review_date"] for r in rows) if d)
    empty_text = sum(1 for r in rows if not r["review_text"].strip())

    by_rating = Counter(r["rating"] for r in rows)
    by_day = Counter(r["review_date"] for r in rows if r["review_date"])
    by_month = Counter(d[:7] for d in dates)
    by_version = Counter(r["app_version"] for r in rows if r["app_version"])

    return {
        "총_리뷰_수": len(rows),
        "고유_review_id_수": len(set(ids)),
        "중복_리뷰_수": len(ids) - len(set(ids)),
        "수집중_스킵된_중복_응답": meta["duplicates_skipped"],
        "빈_리뷰_수(본문없음)": empty_text,
        "개발사_답변_있는_리뷰": sum(1 for r in rows if r["developer_reply"].strip()),
        "app_version_있는_리뷰": sum(1 for r in rows if r["app_version"]),
        "가장_오래된_리뷰": dates[0] if dates else None,
        "가장_최신_리뷰": dates[-1] if dates else None,
        "평점별_건수": {str(k): v for k, v in sorted(by_rating.items(), key=lambda x: (x[0] is None, x[0]))},
        "평균_평점": round(sum(r["rating"] for r in rows if r["rating"]) / len(rows), 3) if rows else None,
        "월별_건수": dict(sorted(by_month.items())),
        "날짜별_건수": dict(sorted(by_day.items())),
        "버전별_건수_상위20": dict(by_version.most_common(20)),
        "수집_페이지_수": meta["pages_fetched"],
        "수집_종료_사유": meta["stop_reason"],
    }


def print_report(q):
    print("\n" + "=" * 52)
    print("데이터 품질 검사")
    print("=" * 52)
    print(f"전체 리뷰 수        : {q['총_리뷰_수']}건")
    print(f"고유 review_id      : {q['고유_review_id_수']}개")
    print(f"중복 리뷰           : {q['중복_리뷰_수']}건 (수집 중 {q['수집중_스킵된_중복_응답']}건 스킵)")
    print(f"빈 리뷰(본문 없음)  : {q['빈_리뷰_수(본문없음)']}건")
    print(f"개발사 답변 있음    : {q['개발사_답변_있는_리뷰']}건")
    print(f"app_version 있음    : {q['app_version_있는_리뷰']}건")
    print(f"기간                : {q['가장_오래된_리뷰']} ~ {q['가장_최신_리뷰']}")
    print(f"평균 평점           : {q['평균_평점']}")

    print("\n[평점별 건수]")
    total = q["총_리뷰_수"] or 1
    for score in ["1", "2", "3", "4", "5"]:
        n = q["평점별_건수"].get(score, 0)
        bar = "█" * round(n / total * 40)
        print(f"  {score}점 {n:5d}건 ({n/total*100:5.1f}%) {bar}")

    print("\n[월별 건수]")
    for month, n in q["월별_건수"].items():
        print(f"  {month}  {n:4d}건  {'▪' * min(n, 60)}")


# ---------------------------------------------------------------- 저장

def save_csv(rows, path):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def save_json(rows, path, meta):
    payload = {
        "_meta": meta,
        "reviews": rows,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- main

def main():
    _stdout_utf8()

    parser = argparse.ArgumentParser(description="퍼핀 Google Play 한국어 리뷰 수집")
    parser.add_argument("--max", type=int, default=None, help="최대 수집 건수 (기본: 가능한 만큼 전부)")
    parser.add_argument("--batch", type=int, default=BATCH_SIZE, help=f"1회 요청 건수 (기본 {BATCH_SIZE})")
    parser.add_argument("--out", type=str, default=".", help="출력 폴더 (기본: 현재 폴더)")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    started = datetime.now()
    print(f"퍼핀 리뷰 수집 시작 — {started:%Y-%m-%d %H:%M:%S}")
    print(f"  앱      : {APP_ID}")
    print(f"  언어/국가: {LANG} / {COUNTRY}")
    print(f"  정렬     : 최신순(NEWEST)\n")

    # 앱 메타데이터 — 구글이 공개한 총 리뷰 수와 실제 수집량을 비교하기 위함
    app_meta = {}
    try:
        info = gp_app(APP_ID, lang=LANG, country=COUNTRY)
        app_meta = {
            "title": info.get("title"),
            "developer": info.get("developer"),
            "current_version": info.get("version"),
            "installs": info.get("installs"),
            "score": info.get("score"),
            "ratings_count": info.get("ratings"),      # 별점만 남긴 것 포함
            "reviews_count": info.get("reviews"),      # 글이 있는 리뷰 (구글 공개값)
            "released": info.get("released"),
            "last_updated": info.get("lastUpdatedOn"),
        }
        print(f"  구글 공개 리뷰 수: {app_meta['reviews_count']}건 (평점 {app_meta['ratings_count']}개)\n")
    except Exception as exc:
        print(f"  ! 앱 메타데이터 조회 실패: {exc}\n")

    rows, meta = collect(max_reviews=args.max, batch_size=args.batch)
    finished = datetime.now()

    if not rows:
        print("수집된 리뷰가 없습니다. 네트워크 또는 앱 ID를 확인하세요.")
        return 1

    quality = quality_check(rows, meta)

    log = {
        "collected_at": started.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": finished.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": round((finished - started).total_seconds(), 1),
        "app_id": APP_ID,
        "app_url": APP_URL,
        "lang": LANG,
        "country": COUNTRY,
        "sort": "NEWEST",
        "library": "google-play-scraper",
        "collected_count": len(rows),
        "google_reported_reviews": app_meta.get("reviews_count"),
        "coverage_pct": (
            round(len(rows) / app_meta["reviews_count"] * 100, 1)
            if app_meta.get("reviews_count") else None
        ),
        "app_meta": app_meta,
        **meta,
    }

    save_csv(rows, out_dir / "puffin_reviews_raw.csv")
    save_json(rows, out_dir / "puffin_reviews_raw.json", log)
    (out_dir / "quality_report.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "collection_log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print_report(quality)
    print("\n[저장 완료]")
    for name in ["puffin_reviews_raw.csv", "puffin_reviews_raw.json",
                 "quality_report.json", "collection_log.json"]:
        p = out_dir / name
        print(f"  {name:26s} {p.stat().st_size:>9,} bytes")

    if log["coverage_pct"] is not None:
        print(f"\n구글 공개 리뷰 수 대비 확보율: {log['coverage_pct']}% "
              f"({len(rows)} / {log['google_reported_reviews']})")
    print(f"수집 종료 사유: {meta['stop_reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
