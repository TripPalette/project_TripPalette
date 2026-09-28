"""Server-side Unsplash lookup and short-lived in-memory cache."""

from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import current_app


UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
CACHE_SECONDS = 60 * 60 * 6

# Reviewed photos use Unsplash's hotlinked CDN URLs and retain attribution.
PREFERRED_PHOTOS = {
    "창원 진해": {
        "id": "_1qQSgLoYKg",
        "image_url": (
            "https://images.unsplash.com/photo-1617413758222-c1703dfdc9bc"
        ),
        "alt": "벚꽃 터널 아래를 산책하는 사람들",
        "photographer": "Minseok Kwak",
        "photographer_url": "https://unsplash.com/@te_rua",
        "photo_url": (
            "https://unsplash.com/photos/"
            "people-walking-on-sidewalk-with-cherry-blossom-trees-"
            "during-daytime-_1qQSgLoYKg"
        ),
    },
}

# Stable English searches produce more predictable results than transliterated input.
DESTINATION_SEARCH_TERMS = {
    "창원 진해": "South Korea cherry blossoms",
    "삼척": "Samcheok coast South Korea travel",
    "여수": "Yeosu coast South Korea travel",
    "구례": "Gurye Jirisan South Korea travel",
    "속초": "Sokcho coast Seoraksan South Korea travel",
    "무주": "Muju Deogyusan South Korea travel",
    "태백": "Taebaek mountain South Korea travel",
    "보령": "Boryeong beach South Korea travel",
    "정읍": "Jeongeup Naejangsan South Korea travel",
    "담양": "Damyang bamboo forest South Korea travel",
    "안동": "Andong Hahoe village South Korea travel",
    "순천": "Suncheon bay South Korea travel",
    "평창": "Pyeongchang mountain South Korea travel",
    "인제": "Inje mountain South Korea travel",
    "강릉": "Gangneung beach South Korea travel",
    "정선": "Jeongseon mountain South Korea travel",
    "제주": "Jeju Island South Korea travel",
    "경주": "Gyeongju South Korea travel",
    "부산": "Busan coast South Korea travel",
    "가평": "Gapyeong South Korea nature travel",
    "포천": "Pocheon South Korea nature travel",
    "양평": "Yangpyeong South Korea nature travel",
    "홍천": "Hongcheon South Korea nature travel",
    "양양": "Yangyang beach South Korea travel",
    "제천": "Jecheon lake South Korea travel",
    "단양": "Danyang South Korea travel",
    "충주": "Chungju lake South Korea travel",
    "태안": "Taean beach South Korea travel",
    "부여": "Buyeo South Korea historical travel",
    "포항": "Pohang coast South Korea travel",
    "문경": "Mungyeong South Korea travel",
    "청송": "Cheongsong Juwangsan South Korea travel",
    "거제": "Geoje Island South Korea travel",
    "통영": "Tongyeong coast South Korea travel",
    "남해": "Namhae South Korea coast travel",
    "군산": "Gunsan South Korea travel",
    "부안": "Buan Byeonsan South Korea travel",
    "완주": "Wanju South Korea nature travel",
    "신안": "Shinan islands South Korea travel",
    "제주 조천": "Jocheon Jeju Island South Korea",
    "제주 애월": "Aewol Jeju Island South Korea",
    "서귀포": "Seogwipo Jeju Island South Korea",
    # Geochang is used by the home-page hero even when it is not in seed data.
    "거창": "Geochang South Korea mountain travel",
}

_photo_cache: dict[str, tuple[float, dict | None]] = {}


def has_search_term(destination_name: str) -> bool:
    return destination_name in DESTINATION_SEARCH_TERMS


def _with_utm(url: str | None, app_name: str) -> str | None:
    if not url:
        return None
    separator = "&" if "?" in url else "?"
    tracking = urlencode({"utm_source": app_name, "utm_medium": "referral"})
    return f"{url}{separator}{tracking}"


def _request_photo(destination_name: str) -> dict | None:
    access_key = current_app.config.get("UNSPLASH_ACCESS_KEY")
    query = DESTINATION_SEARCH_TERMS.get(destination_name)
    if not access_key or not query:
        return None

    params = urlencode(
        {
            "query": query,
            "orientation": "landscape",
            "content_filter": "high",
            "order_by": "relevant",
            "per_page": 1,
        }
    )
    request_url = f"{UNSPLASH_API_URL}?{params}"

    request = Request(
        request_url,
        headers={
            "Authorization": f"Client-ID {access_key}",
            "Accept-Version": "v1",
            "User-Agent": "TripPalette/1.0",
        },
    )

    try:
        with urlopen(request, timeout=5) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
        current_app.logger.warning(
            "Unsplash photo lookup failed (%s): %s", destination_name, error
        )
        return None

    results = payload.get("results") or []
    if not results:
        return None
    photo = results[0]
    user = photo.get("user") or {}
    user_links = user.get("links") or {}
    photo_links = photo.get("links") or {}
    urls = photo.get("urls") or {}
    app_name = current_app.config.get("UNSPLASH_APP_NAME", "trippalette")
    if not urls.get("regular") and not urls.get("small"):
        return None

    return {
        "id": photo.get("id"),
        "urls": {
            "small": urls.get("small") or urls.get("regular"),
            "regular": urls.get("regular") or urls.get("small"),
        },
        "alt": photo.get("alt_description")
        or photo.get("description")
        or f"{destination_name} 여행 풍경",
        "photographer": user.get("name") or "Unsplash photographer",
        "photographer_url": _with_utm(user_links.get("html"), app_name),
        "photo_url": _with_utm(photo_links.get("html"), app_name),
        "unsplash_url": _with_utm("https://unsplash.com", app_name),
    }


def get_destination_photo(destination_name: str) -> dict | None:
    """Return a destination photo from cache or Unsplash."""
    preferred = PREFERRED_PHOTOS.get(destination_name)
    if preferred:
        app_name = current_app.config.get("UNSPLASH_APP_NAME", "trippalette")
        image_url = preferred["image_url"]
        return {
            "id": preferred["id"],
            "urls": {
                "small": f"{image_url}?auto=format&fit=crop&w=640&q=80",
                "regular": f"{image_url}?auto=format&fit=crop&w=1080&q=82",
            },
            "alt": preferred["alt"],
            "photographer": preferred["photographer"],
            "photographer_url": _with_utm(
                preferred["photographer_url"], app_name
            ),
            "photo_url": _with_utm(preferred["photo_url"], app_name),
            "unsplash_url": _with_utm("https://unsplash.com", app_name),
        }

    if not current_app.config.get("UNSPLASH_ACCESS_KEY"):
        return None

    now = time.monotonic()
    cached = _photo_cache.get(destination_name)
    if cached and now - cached[0] < CACHE_SECONDS:
        return cached[1]

    photo = _request_photo(destination_name)
    if photo is not None:
        _photo_cache[destination_name] = (now, photo)
    else:
        # Do not hold authentication, network, or empty-result failures for hours.
        _photo_cache.pop(destination_name, None)
    return photo


def clear_photo_cache() -> None:
    _photo_cache.clear()
