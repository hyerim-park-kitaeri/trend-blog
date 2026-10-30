# Higgsfield 연동 (`scripts/higgsfield.py`)

Higgsfield API로 포스트용 이미지를 생성해 `posts/<날짜>/` 아래에 저장하는 모듈입니다.
표준 라이브러리만 쓰므로 추가 설치가 필요 없습니다. 기존 Pillow 카드 생성
(`make_cards.py`)은 그대로 두고, 사진·일러스트 형태의 이미지만 Higgsfield로 받습니다.

## 1. 키 발급과 환경변수

1. https://cloud.higgsfield.ai 에서 API 키를 만듭니다. 시크릿은 생성 직후 한 번만
   보이므로 바로 저장해야 합니다.
2. 환경변수를 설정합니다. 공식 SDK와 같은 규칙을 씁니다.

```bash
export HF_KEY="키아이디:시크릿"
# 또는
export HF_API_KEY="키아이디"
export HF_API_SECRET="시크릿"
```

키를 저장소에 커밋하지 마세요. `.env`는 `.gitignore`에 포함돼 있습니다.

## 2. 사용법

```bash
# 요청 내용만 확인 (API 호출·과금 없음)
python3 scripts/higgsfield.py --prompt "test" --out /tmp/a.jpg --dry-run

# 포스트 폴더에 바로 저장 → posts/2026-10-30/<슬러그>-hero.jpg
python3 scripts/higgsfield.py \
  --prompt "Korean supermarket aisle with discount tags, shoppers browsing" \
  --date 2026-10-30 --slug K세일페스타2026-11월쇼핑할인총정리

# 모델별 추가 인자 전달
python3 scripts/higgsfield.py --prompt "..." --out hero.jpg \
  --model bytedance/seedream/v4/text-to-image \
  --param aspect_ratio=16:9 --param resolution=2K
```

생성 스크립트(`gen_YYYYMMDD.py`) 안에서 쓸 때:

```python
from higgsfield import generate_image, post_image_path

generate_image(
    "Korean supermarket aisle with discount tags, shoppers browsing",
    post_image_path("2026-10-30", "K세일페스타2026-11월쇼핑할인총정리"),
)
```

주요 옵션

| 옵션 | 설명 |
| --- | --- |
| `--style` | 프롬프트 뒤에 붙는 스타일 프리셋. `editorial`(기본), `illust`, `none` |
| `--suffix` | 파일명 접미사. 기본 `hero` → `<슬러그>-hero.jpg` |
| `--param k=v` | 모델별 인자. 값은 JSON으로 먼저 파싱하고 실패하면 문자열로 전달 |
| `--all` | 응답에 함께 오는 축소본까지 모두 저장 (기본은 원본 1장) |
| `--save-json` | 완료 응답 JSON 저장. 새 모델의 응답 구조를 확인할 때 사용 |
| `--webhook` | 완료 시 호출할 webhook URL |
| `--poll`, `--timeout` | 상태 폴링 간격(기본 3초), 최대 대기(기본 600초) |

## 3. 동작 방식

1. `POST https://api.higgsfield.ai/<모델ID>` — 헤더 `Authorization: Key <키아이디>:<시크릿>`,
   본문은 `{"prompt": ...}` + 추가 인자. 응답으로 `request_id`와 `status_url`을 받습니다.
2. `GET <status_url>`을 `completed`가 될 때까지 폴링합니다. 상태값은
   `queued` / `in_progress` / `completed` / `failed` / `nsfw` / `canceled`이고,
   `completed`가 아닌 종료 상태는 오류로 처리합니다.
3. 완료 응답에서 이미지 URL을 찾아 내려받습니다. 모델에 따라 URL 위치가
   `results.raw.url`, `images[].url` 등으로 달라서 키 이름(`url`, `image_url`, `signed_url`)
   기준으로 재귀 탐색합니다.
4. 429/5xx와 네트워크 오류는 2·4·8·16초 간격으로 최대 4회 재시도합니다. 생성 요청에는
   `Idempotency-Key`를 붙여 재시도 때 같은 요청이 중복 과금되지 않게 합니다.

## 4. 확인한 것과 확인하지 못한 것

- 인증 헤더 형식, 베이스 URL, 상태값, 상태 조회 경로는 공식 Python SDK
  `higgsfield-client` 0.2.0 소스에서 확인했습니다.
- 기본 모델 ID `higgsfield-ai/soul/v2/standard`는 공식 퀵스타트의 엔드포인트 경로를
  따른 값입니다. 모델별로 받는 인자와 응답 구조는 실제 호출로 검증하지 않았습니다.
  새 모델을 쓸 때는 `--save-json`으로 응답을 한 번 받아 확인하세요.
- 전체 흐름(요청 → 폴링 → 이미지 저장, 인증 누락·실패·NSFW·타임아웃 처리)은 로컬
  스텁 서버로 검증했습니다. 실제 Higgsfield 계정으로는 호출하지 않았습니다.

## 5. 과금과 네트워크

- API는 선불 잔액에서 이미지 1장 단위로 과금됩니다. 테스트는 `--dry-run`으로
  요청 내용을 먼저 확인하는 편이 안전합니다.
- 생성 결과물은 서버에서 일정 기간 뒤 삭제됩니다(응답의 `expires_at` 참고).
  저장소에 필요한 이미지는 받은 즉시 커밋해 두세요.
- Claude Code 클라우드 세션에서 실행하려면 환경 네트워크 설정에서
  `api.higgsfield.ai` 허용이 필요합니다. 현재 세션에서는 차단돼 있습니다.

## 6. 참고: MCP 커넥터로 쓰는 방법

코드가 아니라 대화에서 바로 Higgsfield를 쓰려면 claude.ai → Settings → Connectors →
Add custom connector에 `https://mcp.higgsfield.ai/mcp`를 추가하고 Higgsfield 계정으로
로그인하면 됩니다. 유료 플랜이 필요하고, 이 저장소의 자동 생성 파이프라인과는
별개입니다.
