#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Higgsfield API 연동 - 블로그 포스트용 이미지 생성.

인증(공식 SDK와 동일한 환경변수 규칙):
    HF_KEY="<key-id>:<key-secret>"   또는   HF_API_KEY / HF_API_SECRET
키 발급: https://cloud.higgsfield.ai  (API 사용량은 선불 잔액에서 과금됨)

호출 흐름:
    POST https://api.higgsfield.ai/<model>  -> request_id, status_url, cancel_url
    GET  <status_url>                       -> queued / in_progress / completed / failed / nsfw / canceled
    completed 응답에서 이미지 URL 추출       -> 로컬 파일로 저장

표준 라이브러리만 사용하므로 별도 설치가 필요하지 않다.

사용 예:
    export HF_KEY="키아이디:시크릿"
    python3 scripts/higgsfield.py \
        --prompt "Korean supermarket aisle with discount tags, editorial photo" \
        --date 2026-10-30 --slug K세일페스타2026-11월쇼핑할인총정리

    # 요청 내용만 확인(과금 없음)
    python3 scripts/higgsfield.py --prompt "test" --out /tmp/a.jpg --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE_URL = os.environ.get("HF_BASE_URL", "https://api.higgsfield.ai").rstrip("/")
DEFAULT_MODEL = "higgsfield-ai/soul/v2/standard"
USER_AGENT = "trend-blog-higgsfield/1.0"

# 포스트 이미지 톤을 일정하게 유지하기 위한 프롬프트 접미사.
STYLE_PRESETS = {
    "none": "",
    "editorial": "editorial news photography, natural daylight, clean composition, no text, no watermark",
    "illust": "flat vector illustration, minimal, soft muted palette, no text, no watermark",
}

DONE = {"completed", "failed", "nsfw", "canceled"}


class HiggsfieldError(RuntimeError):
    pass


def credential_key() -> str:
    """HF_KEY 또는 HF_API_KEY+HF_API_SECRET에서 'id:secret' 형태의 키를 만든다."""
    key = os.environ.get("HF_KEY")
    if key:
        return key.strip()

    api_key = os.environ.get("HF_API_KEY")
    api_secret = os.environ.get("HF_API_SECRET")
    if api_key and api_secret:
        return f"{api_key.strip()}:{api_secret.strip()}"

    raise HiggsfieldError(
        "Higgsfield 인증 정보가 없습니다. HF_KEY 또는 HF_API_KEY/HF_API_SECRET을 설정하세요."
    )


def _request(method, url, *, key, body=None, headers=None, timeout=90.0, retries=4):
    """Higgsfield API 호출. 429/5xx는 지수 백오프로 재시도한다."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    base_headers = {
        "Authorization": f"Key {key}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    if data is not None:
        base_headers["Content-Type"] = "application/json"
    if headers:
        base_headers.update(headers)

    delay = 2.0
    last_error = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, data=data, headers=base_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            last_error = HiggsfieldError(f"{method} {url} -> HTTP {e.code}: {detail}")
            if e.code not in (408, 409, 425, 429, 500, 502, 503, 504) or attempt == retries:
                raise last_error from e
        except urllib.error.URLError as e:
            last_error = HiggsfieldError(f"{method} {url} -> 네트워크 오류: {e.reason}")
            if attempt == retries:
                raise last_error from e
        time.sleep(delay)
        delay *= 2
    raise last_error


def submit(model, arguments, *, key=None, webhook_url=None, timeout=90.0):
    """생성 요청을 넣고 request_id / status_url / cancel_url을 받는다."""
    key = key or credential_key()
    url = f"{BASE_URL}/{model.strip('/')}"
    if webhook_url:
        url += "?" + urllib.parse.urlencode({"hf_webhook": webhook_url})

    # 내부 재시도로 같은 요청이 두 번 과금되지 않도록 요청당 키를 하나만 쓴다.
    data = _request(
        "POST", url, key=key, body=arguments,
        headers={"Idempotency-Key": str(uuid.uuid4())}, timeout=timeout,
    )
    if "request_id" not in data:
        raise HiggsfieldError(f"예상과 다른 응답입니다: {json.dumps(data)[:500]}")
    request_id = data["request_id"]
    return {
        "request_id": request_id,
        "status_url": data.get("status_url") or f"{BASE_URL}/requests/{request_id}/status",
        "cancel_url": data.get("cancel_url") or f"{BASE_URL}/requests/{request_id}/cancel",
    }


def wait(status_url, *, key=None, poll=3.0, timeout=600.0, verbose=True):
    """completed까지 상태를 폴링하고 마지막 응답 전체를 돌려준다."""
    key = key or credential_key()
    deadline = time.time() + timeout
    last = None
    while True:
        data = _request("GET", status_url, key=key)
        status = str(data.get("status", "")).lower()
        if status != last and verbose:
            print(f"  status: {status or '(없음)'}", flush=True)
            last = status
        if status in DONE:
            if status != "completed":
                raise HiggsfieldError(f"생성 실패(status={status}): {json.dumps(data)[:500]}")
            return data
        if time.time() > deadline:
            raise HiggsfieldError(f"{timeout:.0f}초 안에 끝나지 않았습니다(마지막 status={status}).")
        time.sleep(poll)


def extract_image_urls(payload):
    """응답 JSON에서 이미지 URL을 순서대로 뽑는다.

    모델에 따라 results.raw.url, images[].url 등 위치가 달라 키 이름으로 재귀 탐색한다.
    """
    found = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str) and k in ("url", "image_url", "signed_url") and v.startswith("http"):
                    found.append(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    seen, ordered = set(), []
    for u in found:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    return ordered


def download(url, path, *, timeout=120.0):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(path, "wb") as f:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
    return path


def build_prompt(prompt, style="editorial"):
    suffix = STYLE_PRESETS.get(style, "")
    if not suffix:
        return prompt
    return f"{prompt}, {suffix}"


def generate_image(prompt, out_path, *, model=DEFAULT_MODEL, params=None, style="editorial",
                   key=None, webhook_url=None, poll=3.0, timeout=600.0, verbose=True,
                   save_json=None, save_all=False):
    """프롬프트로 이미지를 만들어 out_path에 저장하고 저장 경로 목록을 돌려준다."""
    key = key or credential_key()
    arguments = {"prompt": build_prompt(prompt, style)}
    if params:
        arguments.update(params)

    if verbose:
        print(f"[higgsfield] {model} 요청", flush=True)
    handle = submit(model, arguments, key=key, webhook_url=webhook_url)
    if verbose:
        print(f"  request_id: {handle['request_id']}", flush=True)

    payload = wait(handle["status_url"], key=key, poll=poll, timeout=timeout, verbose=verbose)
    if save_json:
        os.makedirs(os.path.dirname(os.path.abspath(save_json)) or ".", exist_ok=True)
        with open(save_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    urls = extract_image_urls(payload)
    if not urls:
        raise HiggsfieldError(f"응답에서 이미지 URL을 찾지 못했습니다: {json.dumps(payload)[:500]}")
    if not save_all:
        # 응답에는 원본과 축소본이 함께 오는 경우가 많아 기본값은 첫 번째(원본)만 저장한다.
        urls = urls[:1]

    root, ext = os.path.splitext(out_path)
    ext = ext or ".jpg"
    saved = []
    for i, url in enumerate(urls):
        path = f"{root}{ext}" if i == 0 else f"{root}-{i + 1}{ext}"
        download(url, path)
        saved.append(path)
        if verbose:
            print(f"  saved {path}", flush=True)
    return saved


def post_image_path(date, slug, suffix="hero", ext=".jpg"):
    """posts/<date>/<slug>-<suffix><ext> 경로를 만든다(기존 카드 이미지 작명 규칙과 동일)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "posts", date, f"{slug}-{suffix}{ext}")


def _parse_params(items):
    params = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--param 형식은 key=value 입니다: {item}")
        k, v = item.split("=", 1)
        try:
            params[k] = json.loads(v)
        except json.JSONDecodeError:
            params[k] = v
    return params


def main(argv=None):
    ap = argparse.ArgumentParser(description="Higgsfield API로 포스트 이미지 생성")
    ap.add_argument("--prompt", required=True, help="이미지 프롬프트(영문 권장)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"모델 ID (기본: {DEFAULT_MODEL})")
    ap.add_argument("--style", default="editorial", choices=sorted(STYLE_PRESETS),
                    help="프롬프트에 붙일 스타일 프리셋")
    ap.add_argument("--out", help="저장 경로. 미지정 시 --date/--slug로 계산")
    ap.add_argument("--date", help="posts/<date> 폴더명 (예: 2026-10-30)")
    ap.add_argument("--slug", help="포스트 슬러그 (md 파일명과 동일)")
    ap.add_argument("--suffix", default="hero", help="파일명 접미사 (기본: hero)")
    ap.add_argument("--param", action="append", metavar="KEY=VALUE",
                    help="모델별 추가 인자 (예: --param aspect_ratio=16:9)")
    ap.add_argument("--webhook", help="완료 시 호출할 webhook URL")
    ap.add_argument("--poll", type=float, default=3.0, help="상태 폴링 간격(초)")
    ap.add_argument("--timeout", type=float, default=600.0, help="최대 대기 시간(초)")
    ap.add_argument("--save-json", help="완료 응답 JSON을 저장할 경로")
    ap.add_argument("--all", action="store_true", dest="save_all",
                    help="응답에 담긴 이미지 변형(축소본 등)까지 모두 저장")
    ap.add_argument("--dry-run", action="store_true", help="요청 내용만 출력하고 호출하지 않음")
    args = ap.parse_args(argv)

    if args.out:
        out_path = args.out
    elif args.date and args.slug:
        out_path = post_image_path(args.date, args.slug, args.suffix)
    else:
        raise SystemExit("--out 또는 --date와 --slug를 지정하세요.")

    params = _parse_params(args.param)
    arguments = {"prompt": build_prompt(args.prompt, args.style)}
    arguments.update(params)

    if args.dry_run:
        print(f"POST {BASE_URL}/{args.model.strip('/')}")
        print("Authorization: Key ****")
        print(json.dumps(arguments, ensure_ascii=False, indent=2))
        print(f"저장 경로: {out_path}")
        return 0

    try:
        generate_image(
            args.prompt, out_path, model=args.model, params=params, style=args.style,
            webhook_url=args.webhook, poll=args.poll, timeout=args.timeout,
            save_json=args.save_json, save_all=args.save_all,
        )
    except HiggsfieldError as e:
        print(f"[higgsfield] 오류: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
