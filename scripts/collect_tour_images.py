"""한국관광공사 Open API에서 여행지·숙소 이미지를 수집한다.

인증키는 프로젝트 루트의 .env에 TOUR_API_KEY로 저장한다.
기본 실행은 JSON을 변경하지 않는 미리보기이며, --write를 지정해야 반영한다.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
DESTINATIONS_PATH = ROOT / "app" / "data" / "destinations.json"
ACCOMMODATIONS_PATH = ROOT / "app" / "data" / "accommodations.json"
DEFAULT_REPORT_PATH = ROOT / "app" / "data" / "tour-image-report.json"

PHOTO_API_URL = (
    "https://apis.data.go.kr/B551011/PhotoGalleryService1/gallerySearchList1"
)
TOUR_SEARCH_URL = (
    "https://apis.data.go.kr/B551011/KorService2/searchKeyword2"
)
TOUR_IMAGE_URL = "https://apis.data.go.kr/B551011/KorService2/detailImage2"

COMMON_PARAMS = {
    "MobileOS": "ETC",
    "MobileApp": "TripPalette",
    "_type": "json",
}

LICENSE_NAMES = {
    "Type1": "공공누리 제1유형",
    "Type3": "공공누리 제3유형",
}


class ApiError(RuntimeError):
    """공공 API 호출 또는 응답 형식 오류."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="TourAPI 이미지 URL을 수집해 seed JSON에 연결합니다."
    )
    parser.add_argument(
        "--target",
        choices=("all", "destinations", "accommodations"),
        default="all",
        help="수집 대상(기본값: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="테스트할 항목 수. 지정하지 않으면 전체 항목을 처리합니다.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="검증된 결과를 JSON에 반영합니다. 생략하면 미리보기만 합니다.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="이미 images가 있는 항목도 다시 조회합니다.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="수집 결과 보고서 경로",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.08,
        help="API 요청 사이 대기 시간(초)",
    )
    return parser.parse_args()


def load_json(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path}의 최상위 값은 배열이어야 합니다.")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    temporary_path.replace(path)


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(re.sub(r"<[^>]+>", "", value))
    return re.sub(r"[^0-9A-Za-z가-힣]", "", value).lower()


def api_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        header = payload["response"]["header"]
        if header.get("resultCode") != "0000":
            raise ApiError(header.get("resultMsg", "API 응답 오류"))
        items = payload["response"]["body"].get("items", {})
    except (KeyError, TypeError) as error:
        top_level_keys = list(payload) if isinstance(payload, dict) else []
        response = payload.get("response") if isinstance(payload, dict) else None
        response_keys = list(response) if isinstance(response, dict) else []
        gateway_code = payload.get("resultCode") if isinstance(payload, dict) else None
        gateway_message = payload.get("resultMsg") if isinstance(payload, dict) else None
        raise ApiError(
            "예상하지 못한 API 응답 형식입니다. "
            f"resultCode={gateway_code!r}, resultMsg={gateway_message!r}, "
            f"top_level_keys={top_level_keys}, response_keys={response_keys}"
        ) from error

    if not items:
        return []
    result = items.get("item", [])
    if isinstance(result, dict):
        return [result]
    return result


def request_items(
    url: str,
    service_key: str,
    params: dict[str, Any],
    delay: float,
) -> list[dict[str, Any]]:
    query = urlencode({"serviceKey": service_key, **COMMON_PARAMS, **params})
    request = Request(
        f"{url}?{query}",
        headers={"User-Agent": "TripPalette-seed-image-collector/1.0"},
    )
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        response_text = error.read().decode("utf-8", errors="replace")
        response_text = response_text.replace(service_key, "[REDACTED]")
        response_text = re.sub(r"\s+", " ", response_text).strip()[:300]
        detail = f" - {response_text}" if response_text else ""
        raise ApiError(f"HTTP {error.code}: {url}{detail}") from error
    except (URLError, TimeoutError) as error:
        raise ApiError(f"API 연결 실패: {error}") from error
    except json.JSONDecodeError as error:
        raise ApiError("API가 JSON이 아닌 응답을 반환했습니다.") from error
    finally:
        if delay > 0:
            time.sleep(delay)
    return api_items(payload)


def unique_images(images: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for image in images:
        url = image.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        result.append(image)
        if len(result) == 3:
            break
    return result


def collect_destination_images(
    destination: dict[str, Any],
    service_key: str,
    delay: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    name = destination["name"]
    try:
        items = request_items(
            PHOTO_API_URL,
            service_key,
            {
                "keyword": name,
                "numOfRows": 20,
                "pageNo": 1,
                "arrange": "A",
            },
            delay,
        )
    except ApiError as error:
        if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" not in str(error):
            raise
        return collect_destination_tour_images(
            destination, service_key, delay, fallback_reason=str(error)
        )

    images = unique_images(
        [
            {
                "url": item.get("galWebImageUrl"),
                "thumbnail_url": item.get("galWebImageUrl"),
                "alt": item.get("galTitle") or f"{name} 대표 이미지",
                "source": "한국관광공사 관광사진 정보",
                "source_title": item.get("galTitle"),
                "photographer": item.get("galPhotographer"),
                "license": "공공누리 제1유형",
                "content_id": str(item.get("galContentId", "")),
            }
            for item in items
            if item.get("galWebImageUrl")
        ]
    )
    return images, {
        "query": name,
        "result_count": len(items),
        "source_api": "관광사진 정보",
    }


def collect_destination_tour_images(
    destination: dict[str, Any],
    service_key: str,
    delay: float,
    fallback_reason: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """관광사진 API 권한이 없을 때 국문 관광정보의 관광지 사진을 사용한다."""
    name = destination["name"]
    queries = [name]
    items = request_items(
        TOUR_SEARCH_URL,
        service_key,
        {
            "keyword": name,
            "contentTypeId": 12,
            "numOfRows": 30,
            "pageNo": 1,
            "arrange": "A",
        },
        delay,
    )
    name_tokens = [normalize_text(token) for token in name.split() if token]
    matched_items = []
    for item in items:
        searchable = normalize_text(
            f"{item.get('title', '')} {item.get('addr1', '')} {item.get('addr2', '')}"
        )
        if name_tokens and all(token in searchable for token in name_tokens):
            matched_items.append(item)

    if len(matched_items) < 3 and " " in name:
        shorter_keyword = name.split()[-1]
        queries.append(shorter_keyword)
        additional_items = request_items(
            TOUR_SEARCH_URL,
            service_key,
            {
                "keyword": shorter_keyword,
                "contentTypeId": 12,
                "numOfRows": 30,
                "pageNo": 1,
                "arrange": "A",
            },
            delay,
        )
        items.extend(additional_items)
        known_content_ids = {item.get("contentid") for item in matched_items}
        for item in additional_items:
            searchable = normalize_text(
                f"{item.get('title', '')} {item.get('addr1', '')} {item.get('addr2', '')}"
            )
            if (
                item.get("contentid") not in known_content_ids
                and name_tokens
                and all(token in searchable for token in name_tokens)
            ):
                matched_items.append(item)
                known_content_ids.add(item.get("contentid"))

    images = unique_images(
        [
            {
                "url": item.get("firstimage"),
                "thumbnail_url": item.get("firstimage2") or item.get("firstimage"),
                "alt": item.get("title") or f"{name} 대표 이미지",
                "source": "한국관광공사 국문 관광정보",
                "source_title": item.get("title"),
                "photographer": None,
                "license": LICENSE_NAMES.get(
                    item.get("cpyrhtDivCd"),
                    item.get("cpyrhtDivCd") or "출처 확인 필요",
                ),
                "content_id": str(item.get("contentid", "")),
            }
            for item in matched_items
            if item.get("firstimage")
        ]
    )
    return images, {
        "query": queries,
        "result_count": len(items),
        "location_match_count": len(matched_items),
        "source_api": "국문 관광정보 fallback",
        "fallback_reason": fallback_reason,
    }


def accommodation_match_score(
    accommodation: dict[str, Any], item: dict[str, Any]
) -> int:
    expected_name = normalize_text(accommodation.get("name"))
    result_name = normalize_text(item.get("title"))
    if not expected_name or not result_name:
        return 0

    if expected_name == result_name:
        score = 100
    elif expected_name in result_name or result_name in expected_name:
        score = 75
    else:
        return 0

    expected_address = normalize_text(accommodation.get("address"))
    result_address = normalize_text(
        f"{item.get('addr1', '')} {item.get('addr2', '')}"
    )
    if expected_address and result_address:
        address_tokens = re.findall(
            r"[가-힣]+(?:특별자치도|광역시|특별시|도|시|군|구|읍|면)",
            accommodation.get("address", ""),
        )
        matched_tokens = sum(
            normalize_text(token) in result_address for token in address_tokens
        )
        if address_tokens and matched_tokens == 0:
            return 0
        score += min(matched_tokens * 5, 20)
    return score


def image_from_tour_item(
    item: dict[str, Any], accommodation_name: str
) -> dict[str, Any] | None:
    url = item.get("originimgurl") or item.get("firstimage")
    if not url:
        return None
    copyright_code = item.get("cpyrhtDivCd")
    return {
        "url": url,
        "thumbnail_url": item.get("smallimageurl") or item.get("firstimage2") or url,
        "alt": item.get("imgname") or f"{accommodation_name} 이미지",
        "source": "한국관광공사 국문 관광정보",
        "source_title": item.get("title") or accommodation_name,
        "license": LICENSE_NAMES.get(copyright_code, copyright_code or "출처 확인 필요"),
        "content_id": str(item.get("contentid", "")),
    }


def collect_accommodation_images(
    accommodation: dict[str, Any],
    service_key: str,
    delay: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    name = accommodation["name"]
    search_items = request_items(
        TOUR_SEARCH_URL,
        service_key,
        {
            "keyword": name,
            "contentTypeId": 32,
            "numOfRows": 10,
            "pageNo": 1,
            "arrange": "A",
        },
        delay,
    )
    ranked = sorted(
        (
            (accommodation_match_score(accommodation, item), item)
            for item in search_items
        ),
        key=lambda pair: pair[0],
        reverse=True,
    )
    if not ranked or ranked[0][0] < 75:
        return [], {
            "query": name,
            "result_count": len(search_items),
            "reason": "정확한 이름의 숙소를 찾지 못했습니다.",
            "candidates": [item.get("title") for item in search_items[:3]],
        }

    score, matched = ranked[0]
    content_id = matched.get("contentid")
    detail_items = request_items(
        TOUR_IMAGE_URL,
        service_key,
        {
            "contentId": content_id,
            "imageYN": "Y",
            "numOfRows": 20,
            "pageNo": 1,
        },
        delay,
    )

    images = [
        image
        for item in detail_items
        if (image := image_from_tour_item(item, name)) is not None
    ]
    if not images:
        fallback = image_from_tour_item(matched, name)
        if fallback:
            images.append(fallback)

    return unique_images(images), {
        "query": name,
        "result_count": len(search_items),
        "matched_title": matched.get("title"),
        "matched_address": matched.get("addr1"),
        "match_score": score,
        "content_id": str(content_id or ""),
    }


def process_records(
    records: list[dict[str, Any]],
    kind: str,
    service_key: str,
    limit: int | None,
    overwrite: bool,
    delay: float,
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    processed = 0
    collector = (
        collect_destination_images
        if kind == "destination"
        else collect_accommodation_images
    )

    for record in records:
        if len(record.get("images", [])) == 3 and not overwrite:
            reports.append(
                {
                    "kind": kind,
                    "name": record["name"],
                    "status": "skipped",
                    "reason": "기존 이미지가 있습니다.",
                }
            )
            continue
        if limit is not None and processed >= limit:
            break
        processed += 1

        try:
            images, details = collector(record, service_key, delay)
        except ApiError as error:
            reports.append(
                {
                    "kind": kind,
                    "name": record["name"],
                    "status": "error",
                    "reason": str(error),
                }
            )
            continue

        record["images"] = images
        if images:
            primary_url = images[0]["url"]
            if len(primary_url) <= 255:
                record["image_url"] = primary_url
            else:
                details["primary_url_warning"] = (
                    "대표 URL이 255자를 넘어 image_url에는 저장하지 않았습니다."
                )

        if len(images) == 3:
            status = "matched"
        elif images:
            status = "partial"
        else:
            status = "review"

        reports.append(
            {
                "kind": kind,
                "name": record["name"],
                "status": status,
                "image_count": len(images),
                **details,
            }
        )
        print(
            f"[{kind}] {record['name']}: "
            f"{status} ({len(images)}/3)"
        )
    return reports


def main() -> int:
    args = parse_args()
    load_dotenv(ROOT / ".env")
    service_key = os.getenv("TOUR_API_KEY", "").strip()
    if not service_key or service_key == "change-me":
        print(
            "오류: 프로젝트 루트 .env에 TOUR_API_KEY를 설정하세요.",
            file=sys.stderr,
        )
        return 2

    # 공공데이터포털의 인코딩 키를 붙여 넣은 경우 이중 인코딩을 방지한다.
    if "%" in service_key:
        service_key = unquote(service_key)

    destinations = load_json(DESTINATIONS_PATH)
    accommodations = load_json(ACCOMMODATIONS_PATH)
    reports: list[dict[str, Any]] = []

    if args.target in {"all", "destinations"}:
        reports.extend(
            process_records(
                destinations,
                "destination",
                service_key,
                args.limit,
                args.overwrite,
                args.delay,
            )
        )
    if args.target in {"all", "accommodations"}:
        reports.extend(
            process_records(
                accommodations,
                "accommodation",
                service_key,
                args.limit,
                args.overwrite,
                args.delay,
            )
        )

    summary = {
        "mode": "write" if args.write else "preview",
        "target": args.target,
        "matched": sum(item["status"] == "matched" for item in reports),
        "partial": sum(item["status"] == "partial" for item in reports),
        "review": sum(item["status"] == "review" for item in reports),
        "errors": sum(item["status"] == "error" for item in reports),
        "skipped": sum(item["status"] == "skipped" for item in reports),
        "items": reports,
    }
    write_json(args.report.resolve(), summary)

    if args.write:
        if args.target in {"all", "destinations"}:
            write_json(DESTINATIONS_PATH, destinations)
        if args.target in {"all", "accommodations"}:
            write_json(ACCOMMODATIONS_PATH, accommodations)

    print(
        "완료: "
        f"matched={summary['matched']}, partial={summary['partial']}, "
        f"review={summary['review']}, "
        f"errors={summary['errors']}, skipped={summary['skipped']}"
    )
    print(f"보고서: {args.report.resolve()}")
    if not args.write:
        print("미리보기 모드이므로 seed JSON은 변경하지 않았습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
