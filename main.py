import base64
import csv
import json
import os
import random
import re
import sys
import time
from datetime import date, datetime
from io import BytesIO
from html import unescape
from pathlib import Path
from typing import Any, Dict, List

import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from loguru import logger
from PIL import Image


BASE_URL = "https://120.35.29.78:443"
SEARCH_URL = f"{BASE_URL}/eap/credit.searchMsg"
LIST_URL = f"{BASE_URL}/eap/credit.showProjectInfo"
CAPTCHA_URL = f"{BASE_URL}/eap/credit.vcodecheck"
DETAIL_URL = f"{BASE_URL}/eap/credit.publicShow"
AREA_TREE_URL = (
    f"{BASE_URL}/tzxm/command/ajax/"
    "com.hrt.tzxm.areaclassify.cmd.AreaClassifyQueryCmd/getAreaClassifyTree"
)


HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Origin": BASE_URL,
    "Pragma": "no-cache",
    "Referer": SEARCH_URL,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Not;A=Brand";v="24", "Chromium";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

CSV_FIELDNAMES = [
    "page",
    "list_project_name",
    "list_project_code",
    "list_report_code",
    "list_apply_time",
    "list_area",
    "list_project_type",
    "detail_project_code",
    "detail_project_name",
    "detail_project_type",
    "company_name",
    "detail_report_code",
]


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def load_config() -> Dict[str, Any]:
    config_path = Path(os.getenv("CONFIG_FILE", app_dir() / "config.json"))
    if not config_path.exists():
        logger.warning("未找到配置文件：{}，使用代码默认配置", config_path)
        return {}
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    if not isinstance(config, dict):
        raise ValueError(f"配置文件格式错误，根节点必须是对象：{config_path}")
    logger.info("已读取配置文件：{}", config_path)
    return config


def config_value(config: Dict[str, Any], key: str, env_key: str, default: str) -> str:
    value = os.getenv(env_key)
    if value is not None:
        return value
    value = config.get(key, default)
    if value is None:
        return ""
    return str(value)


def validate_date_value(value: str, field_name: str, *, default_today: bool = False) -> str:
    value = str(value or "").strip()
    if not value and default_today:
        return date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"{field_name} 日期格式错误：{value!r}，正确格式是 YYYY-MM-DD，例如 2026-07-24")
    datetime.strptime(value, "%Y-%m-%d")
    return value


def safe_filename_part(value: str) -> str:
    value = clean_text(value)
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    value = value.strip(" ._")
    return value or "未命名"


def default_output_csv(front_time: str, area_name: str) -> str:
    area = area_name.strip() or "福建省"
    return f"{safe_filename_part(front_time)}_{safe_filename_part(area)}.csv"


def generate_timestamp() -> str:
    first_12 = str(int(time.time() * 1000))[:12]
    check_digit = sum(int(i) for i in first_12) % 10
    return f"{first_12}{check_digit}"


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = False
    session.trust_env = False
    return session


def parse_json_response(text: str) -> Dict[str, Any]:
    text = text.strip()
    if not text:
        raise ValueError("empty response")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = json.loads(unescape(text))
    if isinstance(data, str):
        data = json.loads(data)
    if not isinstance(data, dict):
        raise ValueError(f"unexpected json type: {type(data).__name__}")
    return data


def iter_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for item in value:
            yield from iter_dicts(item)


def pick(data: Dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in data and data[name] not in (None, ""):
            return data[name]
    nested = data.get("data")
    if isinstance(nested, dict):
        return pick(nested, *names, default=default)
    return default


def normalize_public_key(public_key: str) -> str:
    public_key = public_key.strip()
    if "BEGIN PUBLIC KEY" in public_key:
        return public_key
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        + "\n".join(re.findall(r".{1,64}", public_key))
        + "\n-----END PUBLIC KEY-----"
    )


def encrypt_long(text: str, public_key: str) -> str:
    key = RSA.import_key(normalize_public_key(public_key))
    cipher = PKCS1_v1_5.new(key)
    chunks = []
    for i in range(0, len(text), 245):
        encrypted = cipher.encrypt(text[i : i + 245].encode("utf-8"))
        chunks.append(base64.b64encode(encrypted).decode("ascii"))
    return "|".join(chunks)


def build_drag_path(start_x: int, end_x: int) -> List[Dict[str, Any]]:
    path = []
    current = start_x
    now = int(time.time() * 1000)
    elapsed = 0
    while current < end_x:
        step = random.randint(3, 9)
        current = min(end_x, current + step)
        elapsed += random.randint(12, 35)
        path.append(
            {
                "x": current,
                "time": now + elapsed,
                "timeDiff": elapsed if len(path) == 0 else random.randint(12, 35),
                "positionDiff": step,
            }
        )
    for _ in range(random.randint(2, 4)):
        elapsed += random.randint(35, 90)
        jitter = random.choice([-1, 0, 1])
        path.append(
            {
                "x": end_x + jitter,
                "time": now + elapsed,
                "timeDiff": random.randint(35, 90),
                "positionDiff": abs(jitter),
            }
        )
    return path


def calc_slider_end_x(gap_x: float, gap_width: float = 50, track_width: float = 340) -> float:
    # Mirrors page JS:
    # progress = (sliderValue - 20) / (trackRect.width - 30)
    # puzzleX = progress * (380 - gapWidth - 20)
    return 20 + float(gap_x) * (track_width - 30) / (380 - gap_width - 20)


def decode_data_image(data_url: str) -> np.ndarray:
    raw = data_url.split(",", 1)[1] if "," in data_url else data_url
    image = Image.open(BytesIO(base64.b64decode(raw))).convert("RGBA")
    return np.array(image)


def save_data_image(data_url: str, path: Path) -> None:
    raw = data_url.split(",", 1)[1] if "," in data_url else data_url
    path.write_bytes(base64.b64decode(raw))


def save_captcha_debug(
    captcha: Dict[str, Any],
    *,
    prefix: str,
    gap_x: Any = None,
    gap_y: Any = None,
    gap_width: Any = None,
    slider_end_x: Any = None,
    verify_result: Any = None,
) -> None:
    debug_dir = Path("captcha_images")
    debug_dir.mkdir(exist_ok=True)
    image_token = pick(captcha, "imageToken", "tokenId", "captchaId", default="unknown")
    safe_token = re.sub(r"[^0-9A-Za-z_.-]+", "_", str(image_token))
    stem = f"{int(time.time() * 1000)}_{prefix}_{safe_token}"

    for key in ["image", "gapImage", "puzzleImage"]:
        value = captcha.get(key)
        if isinstance(value, str) and value:
            save_data_image(value, debug_dir / f"{stem}_{key}.png")

    meta = {
        "imageToken": image_token,
        "captcha_keys": list(captcha.keys()),
        "gap_x": gap_x,
        "gap_y": gap_y,
        "gap_width": gap_width,
        "slider_end_x": slider_end_x,
        "verify_result": verify_result,
    }
    (debug_dir / f"{stem}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def opaque_bbox(image: np.ndarray) -> tuple[int, int, int, int]:
    alpha = image[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0 or len(ys) == 0:
        return 0, 0, image.shape[1], image.shape[0]
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def solve_gap_from_gap_image(captcha: Dict[str, Any]) -> tuple[float, float, float]:
    image_data = pick(captcha, "image", "backgroundImage")
    gap_image_data = pick(captcha, "gapImage")
    if not image_data or not gap_image_data:
        raise RuntimeError("captcha image/gapImage fields missing")

    image = decode_data_image(image_data)
    gap_image = decode_data_image(gap_image_data)
    if image.shape[:2] != gap_image.shape[:2]:
        raise RuntimeError(f"captcha image size mismatch: {image.shape} != {gap_image.shape}")

    image_gray = cv2.cvtColor(image[:, :, :3], cv2.COLOR_RGB2GRAY)
    gap_gray = cv2.cvtColor(gap_image[:, :, :3], cv2.COLOR_RGB2GRAY)
    diff = cv2.absdiff(image_gray, gap_gray)
    diff = cv2.GaussianBlur(diff, (3, 3), 0)
    _, mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        if 25 <= w <= 90 and 35 <= h <= 110 and area > 400:
            candidates.append((area, x, y, w, h))
    if not candidates:
        raise RuntimeError("gapImage diff did not find gap")

    _, x, y, w, h = max(candidates, key=lambda item: item[0])
    return float(x), float(y), float(w)


def solve_gap_from_images(captcha: Dict[str, Any]) -> tuple[float, float, float]:
    if pick(captcha, "gapImage"):
        try:
            return solve_gap_from_gap_image(captcha)
        except RuntimeError:
            pass

    background_data = pick(captcha, "image", "backgroundImage")
    puzzle_data = pick(captcha, "puzzleImage")
    if not background_data or not puzzle_data:
        raise RuntimeError("captcha image fields missing")

    background = decode_data_image(background_data)
    puzzle = decode_data_image(puzzle_data)
    x0, y0, x1, y1 = opaque_bbox(puzzle)
    puzzle = puzzle[y0:y1, x0:x1]

    bg_gray = cv2.cvtColor(background[:, :, :3], cv2.COLOR_RGB2GRAY)
    tpl_gray = cv2.cvtColor(puzzle[:, :, :3], cv2.COLOR_RGB2GRAY)
    mask = puzzle[:, :, 3]
    if np.count_nonzero(mask) < mask.size * 0.2:
        mask = None

    methods = []
    try:
        methods.append(cv2.matchTemplate(bg_gray, tpl_gray, cv2.TM_CCOEFF_NORMED, mask=mask))
    except cv2.error:
        methods.append(cv2.matchTemplate(bg_gray, tpl_gray, cv2.TM_CCOEFF_NORMED))

    bg_edge = cv2.Canny(bg_gray, 80, 180)
    tpl_edge = cv2.Canny(tpl_gray, 80, 180)
    methods.append(cv2.matchTemplate(bg_edge, tpl_edge, cv2.TM_CCOEFF_NORMED))

    best = None
    for result in methods:
        _, score, _, loc = cv2.minMaxLoc(result)
        if best is None or score > best[0]:
            best = (score, loc)
    if best is None:
        raise RuntimeError("captcha image matching failed")

    score, (gap_x, gap_y) = best
    if score < 0.15:
        raise RuntimeError(f"captcha image matching score too low: {score:.4f}")
    return float(gap_x), float(gap_y), float(puzzle.shape[1])


def warmup(session: requests.Session) -> None:
    session.get(SEARCH_URL, timeout=20)
    session.get(f"{LIST_URL}?timestamp={generate_timestamp()}", timeout=20)


def fetch_area_tree(session: requests.Session, super_code: str = "350000") -> Dict[str, Any]:
    payload = {
        "params": {
            "javaClass": "ParameterSet",
            "map": {"superCode": super_code},
            "length": 1,
        },
        "context": {
            "javaClass": "HashMap",
            "map": {},
            "length": 0,
        },
    }
    response = session.post(
        AREA_TREE_URL,
        json=payload,
        headers={
            **HEADERS,
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Referer": f"{BASE_URL}/tzxm/jsp/tzxm/areaclassify/queryAreaClassify.jsp",
        },
        timeout=20,
    )
    response.raise_for_status()
    data = json.loads(response.text.strip())
    if isinstance(data, str):
        data = json.loads(data)
    if isinstance(data, list):
        return {"data": data}
    if isinstance(data, dict):
        return data
    raise ValueError(f"unexpected area tree response type: {type(data).__name__}")


def extract_area_nodes(tree: Dict[str, Any]) -> List[Dict[str, str]]:
    name_keys = ["name", "text", "label", "areaName", "AreaName", "cantName", "CANTNAME", "CANT_NAME", "SHORT_NAME"]
    code_keys = ["code", "id", "value", "areaCode", "AreaCode", "cantCode", "CANTCODE", "CANT_CODE"]
    nodes = []
    seen = set()
    for item in iter_dicts(tree):
        name = next((item.get(key) for key in name_keys if item.get(key)), None)
        code = next((item.get(key) for key in code_keys if item.get(key)), None)
        if name is None or code is None:
            continue
        name = clean_text(str(name))
        code = clean_text(str(code))
        if not name or not code:
            continue
        key = (name, code)
        if key in seen:
            continue
        seen.add(key)
        nodes.append(
            {
                "name": name,
                "code": code,
                "short_name": clean_text(str(item.get("SHORT_NAME") or name)),
                "super_code": clean_text(str(item.get("SUPER_CODE") or "")),
                "type": clean_text(str(item.get("CANT_TYPE") or "")),
                "count": item.get("COUNT"),
            }
        )
    return nodes


def download_area_codes(session: requests.Session, output_path: str = "area_codes.json") -> List[Dict[str, Any]]:
    cities = extract_area_nodes(fetch_area_tree(session, "350000"))
    result = []
    logger.info("开始下载福建省市/区编码：市级数量 {}", len(cities))

    for city in cities:
        city_code = city["code"]
        districts = extract_area_nodes(fetch_area_tree(session, city_code))
        logger.info("地区编码：{}({}) -> 区县 {} 个", city["name"], city_code, len(districts))
        result.append(
            {
                "city_name": city["name"],
                "city_short_name": city.get("short_name", ""),
                "city_code": city_code,
                "districts": [
                    {
                        "area_name": district["name"],
                        "area_short_name": district.get("short_name", ""),
                        "area_code": district["code"],
                        "super_code": district.get("super_code", city_code),
                    }
                    for district in districts
                ],
            }
        )
        time.sleep(random.uniform(0.1, 0.3))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("地区编码下载完成：{}，共 {} 个市", output_path, len(result))
    return result


def resolve_area_code_from_file(area_name: str, path: str = "area_codes.json") -> str:
    area_name = clean_text(area_name)
    area_path = Path(path)
    if not area_name or not area_path.exists():
        return ""
    data = json.loads(area_path.read_text(encoding="utf-8"))
    candidates = []
    for city in data:
        candidates.append((city.get("city_name", ""), city.get("city_code", "")))
        candidates.append((city.get("city_short_name", ""), city.get("city_code", "")))
        for district in city.get("districts", []):
            candidates.append((district.get("area_name", ""), district.get("area_code", "")))
            candidates.append((district.get("area_short_name", ""), district.get("area_code", "")))
    for name, code in candidates:
        if clean_text(str(name)) == area_name and code:
            logger.info("从本地地区编码文件匹配：{} -> {}", area_name, code)
            return str(code)
    for name, code in candidates:
        name = clean_text(str(name))
        if code and name and (area_name in name or name in area_name):
            logger.warning("从本地地区编码文件模糊匹配：{} -> {}({})", area_name, name, code)
            return str(code)
    return ""


def resolve_area_code(session: requests.Session, area_name: str, default_super_code: str = "350000") -> str:
    area_name = clean_text(area_name)
    if not area_name:
        return ""

    file_code = resolve_area_code_from_file(area_name)
    if file_code:
        return file_code

    visited = set()
    queue = [default_super_code]
    fuzzy_match = ""

    while queue:
        super_code = queue.pop(0)
        if super_code in visited:
            continue
        visited.add(super_code)

        tree = fetch_area_tree(session, super_code)
        nodes = extract_area_nodes(tree)
        logger.info("正在查询地区编码：上级编码={}，返回 {} 个地区", super_code, len(nodes))

        for node in nodes:
            if node["name"] == area_name:
                logger.info("已匹配地区：{} -> {}", node["name"], node["code"])
                return node["code"]
            if not fuzzy_match and (area_name in node["name"] or node["name"] in area_name):
                fuzzy_match = node["code"]

        for node in nodes:
            code = node["code"]
            if code.isdigit() and len(code) >= 6 and code not in visited:
                queue.append(code)

    if fuzzy_match:
        logger.warning("未找到完全匹配地区：{}，使用模糊匹配编码：{}", area_name, fuzzy_match)
        return fuzzy_match
    raise RuntimeError(f"未能通过地区树接口找到 area_code：{area_name}")


def get_slide_captcha(session: requests.Session) -> Dict[str, Any]:
    response = session.post(
        CAPTCHA_URL,
        params={"type": "getSlideCaptcha"},
        headers={**HEADERS, "Referer": LIST_URL},
        timeout=20,
    )
    response.raise_for_status()
    return parse_json_response(response.text)


def solve_slide_captcha_once(session: requests.Session, *, save_debug: bool = False) -> str:
    captcha = get_slide_captcha(session)
    image_token = pick(captcha, "imageToken", "tokenId", "captchaId", "captcha_")
    public_key = pick(captcha, "publicKey", "rsaPublicKey", "key")
    gap_x = pick(captcha, "gapX", "x", "offsetX")
    gap_y = pick(captcha, "gapY", "y", "offsetY", default=80)
    gap_width = pick(captcha, "gapWidth", "width", default=50)

    if image_token is None or public_key is None:
        safe_keys = {k: ("<image>" if "image" in k.lower() else v) for k, v in captcha.items()}
        raise RuntimeError(f"captcha response missing token/publicKey: {safe_keys}")
    if gap_x is None:
        gap_x, gap_y, gap_width = solve_gap_from_images(captcha)

    start_x = 20
    end_x = int(round(calc_slider_end_x(float(gap_x), float(gap_width))))
    if save_debug or os.getenv("SAVE_CAPTCHA", "0") == "1":
        save_captcha_debug(
            captcha,
            prefix="request",
            gap_x=gap_x,
            gap_y=gap_y,
            gap_width=gap_width,
            slider_end_x=end_x,
        )
    drag_path = build_drag_path(start_x, end_x)
    drag_duration = drag_path[-1]["time"] - drag_path[0]["time"] + random.randint(80, 180)

    trajectory = {
        "startX": drag_path[0]["x"],
        "endX": drag_path[-1]["x"],
        "dragDuration": drag_duration,
        "dragPath": drag_path,
        "puzzleX": float(gap_x),
        "gapX": float(gap_x),
        "gapY": float(gap_y),
        "imageToken": image_token,
        "timestamp": int(time.time() * 1000),
        "nonce": "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for _ in range(16)),
    }
    encrypted = encrypt_long(json.dumps(trajectory, ensure_ascii=False, separators=(",", ":")), public_key)

    response = session.post(
        CAPTCHA_URL,
        params={"type": "slideValid", "imageToken": image_token},
        data={"trajectoryData": encrypted},
        headers={**HEADERS, "Referer": LIST_URL},
        timeout=20,
    )
    response.raise_for_status()
    result = parse_json_response(response.text)
    if not result.get("success"):
        save_captcha_debug(
            captcha,
            prefix="failed",
            gap_x=gap_x,
            gap_y=gap_y,
            gap_width=gap_width,
            slider_end_x=end_x,
            verify_result=result,
        )
        raise RuntimeError(f"slide captcha failed: {result}")
    token = pick(result, "token", "captchaToken")
    if not token:
        raise RuntimeError(f"captcha token missing: {result}")
    return token


def solve_slide_captcha(session: requests.Session, max_retries: int = 3) -> str:
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return solve_slide_captcha_once(session, save_debug=(attempt == 1))
        except RuntimeError as exc:
            last_error = exc
            logger.warning("第 {} 次滑块验证失败，准备重试：{}", attempt, exc)
            time.sleep(random.uniform(0.3, 0.8))
    raise RuntimeError(f"slide captcha failed after {max_retries} attempts: {last_error}")


def query_projects(
    session: requests.Session,
    captcha_token: str,
    *,
    page: int = 1,
    project_name: str = "光伏",
    project_code: str = "",
    front_time: str = "2025-01-01",
    behind_time: str = "",
    project_type: str = "",
    area_name: str = "",
    area_code: str = "",
    is_in: str = "",
    enterprise_name: str = "",
) -> str:
    data = {
        "page": str(page),
        "project_name": project_name,
        "project_code": project_code,
        "front_time": front_time,
        "behind_time": behind_time or date.today().isoformat(),
        "project_type": project_type,
        "AreaName": area_name,
        "AreaCode": area_code,
        "is_in": is_in,
        "enterprise_name": enterprise_name,
        "captchaToken": captcha_token,
    }
    response = session.post(
        LIST_URL,
        data=data,
        headers={**HEADERS, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Referer": LIST_URL},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def looks_like_captcha_required(html: str) -> bool:
    if "class=\"project\"" in html or "class='project'" in html:
        return False
    needles = ["验证码已过期", "免验证次数已用完", "查询需验证", "安全验证", "slideVerifyModal"]
    return any(needle in html for needle in needles)


def query_projects_with_captcha(session: requests.Session, page: int, query: Dict[str, str]) -> tuple[str, str]:
    token = solve_slide_captcha(session)
    html = query_projects(session, token, page=page, **query)
    if looks_like_captcha_required(html):
        token = solve_slide_captcha(session)
        html = query_projects(session, token, page=page, **query)
    return html, token


def extract_rows(html: str) -> List[List[str]]:
    rows = []
    for tr in re.findall(r"<tr[^>]*class=[\"']project[\"'][\s\S]*?</tr>", html, flags=re.I):
        cells = []
        for td in re.findall(r"<td[^>]*>([\s\S]*?)</td>", tr, flags=re.I):
            text = re.sub(r"<[^>]+>", "", td)
            cells.append(unescape(re.sub(r"\s+", " ", text)).strip())
        if cells:
            rows.append(cells)
    return rows


def extract_list_items(html: str) -> List[Dict[str, Any]]:
    items = []
    for tr in re.findall(r"<tr[^>]*class=[\"']project[\"'][\s\S]*?</tr>", html, flags=re.I):
        m = re.search(r"applyproject\('([^']+)'\s*,\s*'([^']+)'\)", tr)
        cells = []
        for td in re.findall(r"<td[^>]*>([\s\S]*?)</td>", tr, flags=re.I):
            text = re.sub(r"<[^>]+>", "", td)
            cells.append(unescape(re.sub(r"\s+", " ", text)).strip())
        if not cells:
            continue
        item = {
            "project_name": cells[0] if len(cells) > 0 else "",
            "project_code": cells[1] if len(cells) > 1 else "",
            "report_code": cells[2] if len(cells) > 2 else "",
            "apply_time": cells[3] if len(cells) > 3 else "",
            "area": cells[4] if len(cells) > 4 else "",
            "project_type": cells[5] if len(cells) > 5 else "",
            "detail_project_code": m.group(1) if m else cells[1] if len(cells) > 1 else "",
            "biaoji": m.group(2) if m else "0",
        }
        items.append(item)
    return items


def fetch_detail(session: requests.Session, project_code: str, biaoji: str = "0") -> str:
    response = session.get(
        DETAIL_URL,
        params={"projectcode": project_code, "biaoji": biaoji},
        headers={**HEADERS, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Referer": LIST_URL},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def clean_text(value: str) -> str:
    return unescape(re.sub(r"\s+", " ", value)).strip()


def parse_detail(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = clean_text(soup.get_text(" "))
    detail: Dict[str, Any] = {
        "company_name": "",
        "project_code": "",
        "project_name": "",
        "project_type": "",
        "report_code": "",
    }

    patterns = {
        "company_name": r"当前位置：项目信息\s+(.+?)\s+申报项目基本信息",
        "project_code": r"项目代码\s+([0-9A-Z-]+)",
        "project_name": r"项目名称\s+(.+?)\s+项目类型",
        "project_type": r"项目类型\s+(.+?)\s+项目（法人）单位",
        "report_code": r"报建编号\s+([0-9A-Z-]+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            detail[key] = clean_text(match.group(1))

    return detail


def collect_pages(
    session: requests.Session,
    *,
    start_page: int = 1,
    max_pages: int = 0,
    with_detail: bool = True,
    output_csv: str = "results.csv",
    **query: str,
) -> int:
    total = 0
    page = start_page
    end_page = None if max_pages <= 0 else start_page + max_pages - 1
    while end_page is None or page <= end_page:
        html, token = query_projects_with_captcha(session, page, query)
        items = extract_list_items(html)
        logger.info("正在爬取第 {} 页，本页解析到 {} 条数据，当前累计 {} 条", page, len(items), total)
        if not items:
            logger.info("第 {} 页没有数据，停止翻页", page)
            break
        for item in items:
            item["page"] = page
            if with_detail:
                detail_html = fetch_detail(session, item["detail_project_code"], item["biaoji"])
                item["detail"] = parse_detail(detail_html)
                time.sleep(random.uniform(0.15, 0.4))
            row = flatten_item_for_csv(item)
            append_csv_row(row, output_csv)
            total += 1
            logger.info(
                "已写入第 {} 条：第 {} 页 | {} | {} | {}",
                total,
                row["page"],
                row["list_project_code"],
                row["list_project_name"],
                row["company_name"],
            )
        time.sleep(random.uniform(0.3, 0.8))
        page += 1
    return total


def flatten_item_for_csv(item: Dict[str, Any]) -> Dict[str, Any]:
    detail = item.get("detail") or {}
    return {
        "page": item.get("page", ""),
        "list_project_name": item.get("project_name", ""),
        "list_project_code": item.get("project_code", ""),
        "list_report_code": item.get("report_code", ""),
        "list_apply_time": item.get("apply_time", ""),
        "list_area": item.get("area", ""),
        "list_project_type": item.get("project_type", ""),
        "detail_project_code": detail.get("project_code", item.get("detail_project_code", "")),
        "detail_project_name": detail.get("project_name", ""),
        "detail_project_type": detail.get("project_type", ""),
        "company_name": detail.get("company_name", ""),
        "detail_report_code": detail.get("report_code", ""),
    }


def append_csv_row(row: Dict[str, Any], path: str) -> None:
    csv_path = Path(path)
    need_header = not csv_path.exists() or csv_path.stat().st_size == 0
    with csv_path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES, extrasaction="ignore")
        if need_header:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in CSV_FIELDNAMES})


def clear_captcha_images() -> None:
    debug_dir = Path("captcha_images")
    if not debug_dir.exists():
        return
    deleted = 0
    for path in debug_dir.iterdir():
        if path.is_file():
            path.unlink()
            deleted += 1
    logger.info("已清空验证码图片目录：{}，删除 {} 个文件", debug_dir, deleted)


def pause_when_frozen() -> None:
    if getattr(sys, "frozen", False):
        try:
            input("程序运行结束，按回车键退出...")
        except EOFError:
            pass


def main() -> None:
    session = make_session()
    if os.getenv("DOWNLOAD_AREAS", "0") == "1":
        download_area_codes(session, os.getenv("AREA_CODES_JSON", "area_codes.json"))
        return

    warmup(session)
    config = load_config()

    front_time = validate_date_value(
        config_value(config, "front_time", "FRONT_TIME", "2025-01-01"),
        "front_time",
    )
    behind_time = validate_date_value(
        config_value(config, "behind_time", "BEHIND_TIME", ""),
        "behind_time",
        default_today=True,
    )

    query = {
        "project_name": os.getenv("PROJECT_NAME", "光伏"),
        "project_code": os.getenv("PROJECT_CODE", ""),
        "front_time": front_time,
        "behind_time": behind_time,
        "project_type": os.getenv("PROJECT_TYPE", ""),
        "area_name": config_value(config, "area_name", "AREA_NAME", ""),
        "area_code": config_value(config, "area_code", "AREA_CODE", ""),
        "is_in": os.getenv("IS_IN", ""),
        "enterprise_name": os.getenv("ENTERPRISE_NAME", ""),
    }
    if query["area_name"] and not query["area_code"]:
        query["area_code"] = resolve_area_code(session, query["area_name"])
    # MAX_PAGES=0 means keep turning pages until an empty page is returned.
    max_pages = int(os.getenv("MAX_PAGES", "0"))
    start_page = int(os.getenv("START_PAGE", "1"))
    with_detail = os.getenv("WITH_DETAIL", "1") != "0"
    output_csv = os.getenv("OUTPUT_CSV", default_output_csv(front_time, query["area_name"]))

    logger.info(
        "开始采集：起始页={}，最大页数={}，是否请求详情={}，输出文件={}，查询条件={}",
        start_page,
        "自动翻页" if max_pages <= 0 else max_pages,
        with_detail,
        output_csv,
        query,
    )
    total = collect_pages(
        session,
        start_page=start_page,
        max_pages=max_pages,
        with_detail=with_detail,
        output_csv=output_csv,
        **query,
    )
    logger.info("采集完成：一共爬取 {} 条数据，已追加写入 {}", total, output_csv)


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    try:
        main()
    finally:
        clear_captcha_images()
        pause_when_frozen()
