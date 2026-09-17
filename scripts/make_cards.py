#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate cover / summary / table card PNGs for trend-blog posts using Pillow."""
import textwrap
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/usr/share/fonts/opentype/noto"
SANS_REG = f"{FONT_DIR}/NotoSansCJK-Regular.ttc"
SANS_BOLD = f"{FONT_DIR}/NotoSansCJK-Bold.ttc"

W = 900

# ---------- palette per post ----------
PALETTES = {
    "blue": {"bg": "#FFFFFF", "accent": "#2F5DFF", "accent_dark": "#1A3FCC", "text": "#1B1F2B", "sub": "#5B6472", "line": "#E4E8F0", "badge_bg": "#2F5DFF", "badge_fg": "#FFFFFF"},
    "rose": {"bg": "#FFFFFF", "accent": "#D6336C", "accent_dark": "#A61E4D", "text": "#1B1F2B", "sub": "#5B6472", "line": "#F2E1E8", "badge_bg": "#D6336C", "badge_fg": "#FFFFFF"},
    "teal": {"bg": "#FFFFFF", "accent": "#0E9384", "accent_dark": "#0A6E63", "text": "#1B1F2B", "sub": "#5B6472", "line": "#DFF1EE", "badge_bg": "#0E9384", "badge_fg": "#FFFFFF"},
    "amber": {"bg": "#FFFFFF", "accent": "#C2760C", "accent_dark": "#8F5608", "text": "#1B1F2B", "sub": "#5B6472", "line": "#F5E6D0", "badge_bg": "#C2760C", "badge_fg": "#FFFFFF"},
}

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap_text(draw, text, f, max_width):
    lines = []
    for para in text.split("\n"):
        if para == "":
            lines.append("")
            continue
        cur = ""
        for ch in para:
            test = cur + ch
            if draw.textlength(test, font=f) > max_width and cur:
                lines.append(cur)
                cur = ch
            else:
                cur = test
        lines.append(cur)
    return lines

def draw_badge(draw, xy, text, pal, f):
    x, y = xy
    pad_x, pad_y = 22, 12
    tw = draw.textlength(text, font=f)
    w = tw + pad_x * 2
    h = f.size + pad_y * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=pal["badge_bg"])
    draw.text((x + pad_x, y + pad_y - 2), text, font=f, fill=pal["badge_fg"])
    return h

def make_cover(path, badge, title_lines, subtitle, pal_key="blue"):
    pal = PALETTES[pal_key]
    H = 900
    img = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(img)

    # top accent bar
    d.rectangle([0, 0, W, 14], fill=pal["accent"])

    f_badge = font(SANS_BOLD, 26)
    f_title = font(SANS_BOLD, 58)
    f_sub = font(SANS_REG, 30)

    bx, by = 60, 90
    bh = draw_badge(d, (bx, by), badge, pal, f_badge)

    ty = by + bh + 50
    for line in title_lines:
        d.text((60, ty), line, font=f_title, fill=pal["text"])
        ty += 74

    # divider
    ty += 20
    d.line([(60, ty), (W - 60, ty)], fill=pal["line"], width=3)
    ty += 40

    sub_lines = wrap_text(d, subtitle, f_sub, W - 120)
    for line in sub_lines[:6]:
        d.text((60, ty), line, font=f_sub, fill=pal["sub"])
        ty += 44

    # bottom accent block
    d.rectangle([0, H - 90, W, H], fill=pal["accent"])
    f_foot = font(SANS_BOLD, 30)
    foot = "TREND BLOG · 오늘의 이슈 총정리"
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, H - 90 + (90 - 34) / 2), foot, font=f_foot, fill="#FFFFFF")

    img.save(path)
    print("saved", path)

def make_summary_card(path, badge, title, bullets, pal_key="blue"):
    pal = PALETTES[pal_key]
    f_badge = font(SANS_BOLD, 24)
    f_title = font(SANS_BOLD, 40)
    f_bullet = font(SANS_REG, 28)
    f_bullet_b = font(SANS_BOLD, 28)

    pad = 60
    content_w = W - pad * 2 - 40

    tmp = Image.new("RGB", (10, 10))
    dtmp = ImageDraw.Draw(tmp)

    title_lines = wrap_text(dtmp, title, f_title, content_w)

    bullet_blocks = []
    for b in bullets:
        wrapped = wrap_text(dtmp, b, f_bullet, content_w - 50)
        bullet_blocks.append(wrapped)

    H = 90 + 50 + 60 + len(title_lines) * 50 + 40
    for wrapped in bullet_blocks:
        H += 30 + len(wrapped) * 42
    H += 70

    img = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=pal["accent"])

    y = 60
    bh = draw_badge(d, (pad, y), badge, pal, f_badge)
    y += bh + 40

    for line in title_lines:
        d.text((pad, y), line, font=f_title, fill=pal["text"])
        y += 50
    y += 20

    d.line([(pad, y), (W - pad, y)], fill=pal["line"], width=3)
    y += 40

    for wrapped in bullet_blocks:
        bullet_x = pad
        d.ellipse([bullet_x, y + 12, bullet_x + 14, y + 26], fill=pal["accent"])
        for i, line in enumerate(wrapped):
            d.text((bullet_x + 34, y), line, font=f_bullet, fill=pal["text"])
            y += 42
        y += 22

    d.rectangle([0, H - 16, W, H], fill=pal["accent"])
    img.save(path)
    print("saved", path)

def make_table_card(path, badge, title, rows, pal_key="blue"):
    """rows: list of (label, value) or (label, value, extra) tuples"""
    pal = PALETTES[pal_key]
    f_badge = font(SANS_BOLD, 24)
    f_title = font(SANS_BOLD, 38)
    f_label = font(SANS_BOLD, 26)
    f_value = font(SANS_REG, 26)

    pad = 55
    content_w = W - pad * 2

    tmp = Image.new("RGB", (10, 10))
    dtmp = ImageDraw.Draw(tmp)
    title_lines = wrap_text(dtmp, title, f_title, content_w)

    row_blocks = []
    for row in rows:
        label = row[0]
        value = row[1]
        label_lines = wrap_text(dtmp, label, f_label, content_w * 0.40)
        value_lines = wrap_text(dtmp, value, f_value, content_w * 0.56)
        n = max(len(label_lines), len(value_lines))
        row_blocks.append((label_lines, value_lines, n))

    H = 60 + 50 + 40 + len(title_lines) * 46 + 30
    for _, _, n in row_blocks:
        H += n * 38 + 28
    H += 60

    img = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=pal["accent"])

    y = 60
    bh = draw_badge(d, (pad, y), badge, pal, f_badge)
    y += bh + 34

    for line in title_lines:
        d.text((pad, y), line, font=f_title, fill=pal["text"])
        y += 46
    y += 24

    d.line([(pad, y), (W - pad, y)], fill=pal["accent"], width=3)
    y += 26

    label_x = pad
    value_x = pad + int(content_w * 0.42)

    for label_lines, value_lines, n in row_blocks:
        row_top = y
        ly = y
        for line in label_lines:
            d.text((label_x, ly), line, font=f_label, fill=pal["accent_dark"])
            ly += 38
        vy = y
        for line in value_lines:
            d.text((value_x, vy), line, font=f_value, fill=pal["text"])
            vy += 38
        y = row_top + n * 38 + 28
        d.line([(pad, y - 14), (W - pad, y - 14)], fill=pal["line"], width=2)

    d.rectangle([0, H - 16, W, H], fill=pal["accent"])
    img.save(path)
    print("saved", path)


if __name__ == "__main__":
    import os
    base1 = "posts/2026-09-17"
    os.makedirs(base1, exist_ok=True)

    # ---- Post 1: 수시 원서접수 먹통 사태 ----
    make_cover(
        f"{base1}/수시원서접수먹통-cover.png",
        "입시이슈",
        ["수시 원서접수 먹통", "414건 구제 확정"],
        "9월11일 서버 장애부터 대학별 구제 현황, 경쟁률 취소 권고 3건까지 정리합니다.",
        pal_key="blue",
    )
    make_summary_card(
        f"{base1}/수시원서접수먹통-핵심요약.png",
        "핵심요약",
        "수시 원서접수 먹통 사태, 이것만은 확인하세요",
        [
            "사고 개요: 9월11일 오후 5시50분 유웨이어플라이 서버 장애로 마감 1시간 연장",
            "구제 심사 결과: 신청 1588건 중 414건 인정, 354건 최종 접수 완료로 구제 확정",
            "형평성 논란: 17개 대학 연장시간 경쟁률 공개, 이를 본 뒤 지원한 3건 취소 권고",
            "대학별 구제: 경북대 72건 최다, 경희대 51건·중앙대 48건·전남대 27건 순",
        ],
        pal_key="blue",
    )
    make_table_card(
        f"{base1}/수시원서접수먹통-구제현황표.png",
        "구제 현황",
        "수시 원서접수 먹통 사태 타임라인 · 구제 현황표",
        [
            ("장애 발생 시각", "9월11일 오후 5시50분, 유웨이어플라이 서버 장애"),
            ("서버 복구 시각", "같은 날 오후 6시20분경 정상화"),
            ("마감 연장", "기존 오후 6시에서 오후 7시로 1시간 연장"),
            ("구제 신청 건수", "총 1588건 접수"),
            ("구제 인정 건수", "414건"),
            ("최종 구제 확정", "354건 접수 완료"),
            ("구제 최다 대학", "경북대 72건, 경희대 51건, 중앙대 48건"),
            ("취소 권고 대상", "경쟁률 확인 후 지원한 3건"),
        ],
        pal_key="blue",
    )

    # ---- Post 2: GLP-1 비만약 오남용우려의약품 지정 ----
    make_cover(
        f"{base1}/GLP1비만약-cover.png",
        "건강트렌드",
        ["위고비 마운자로", "오남용우려의약품 지정 임박"],
        "이달 확정되는 규제 방향과 2026년 가격, 보험 적용, 부작용까지 정리합니다.",
        pal_key="teal",
    )
    make_summary_card(
        f"{base1}/GLP1비만약-핵심요약.png",
        "핵심요약",
        "위고비·마운자로, 처방 전 이것만은 확인하세요",
        [
            "규제 동향: 식약처, GLP-1 비만약 오·남용우려의약품 지정 자문 완료, 이달 확정 예정",
            "가격 현황: 위고비 월 21만~42만원대(평균 26만원), 마운자로 월 29만~60만원대",
            "보험 적용: 비만 치료 목적은 비급여, 당뇨병 치료 목적일 때만 급여 가능성",
            "국산 신약: 한미약품 에페글레나타이드 2026년 하반기 출시 목표로 일정 앞당김",
        ],
        pal_key="teal",
    )
    make_table_card(
        f"{base1}/GLP1비만약-가격비교표.png",
        "가격·규제 비교",
        "위고비 · 마운자로 가격과 보험·규제 현황표",
        [
            ("위고비 월 비용", "약 21만~42만원, 전국 평균 약 26만원"),
            ("마운자로 월 비용", "용량별 약 29만~60만원대"),
            ("건강보험 적용", "다이어트 목적 비급여, 당뇨병 치료 목적 급여 가능성"),
            ("비대면 처방", "2024년 12월2일부터 제한, 대면 진료 필수"),
            ("규제 동향", "식약처 오남용우려의약품 지정 자문 완료, 이달 확정 예정"),
            ("금기 대상", "갑상선수질암, 다발성내분비종양증 병력자 등"),
            ("국산 신약", "한미약품 에페글레나타이드, 2026년 하반기 출시 목표"),
            ("유한양행", "월 1회 투여 주사제 임상시험 진입 예정"),
        ],
        pal_key="teal",
    )
