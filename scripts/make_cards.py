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
    base1 = "posts/2026-09-14"
    os.makedirs(base1, exist_ok=True)

    # ---- Post 1: 청년미래적금 ----
    make_cover(
        f"{base1}/청년미래적금-cover.png",
        "정부정책",
        ["청년미래적금", "9월 추가 신청 검토"],
        "234만명 몰린 이유부터 일반형·우대형 조건, 만기 수령액까지 한번에 정리합니다.",
        pal_key="blue",
    )
    make_summary_card(
        f"{base1}/청년미래적금-핵심요약.png",
        "핵심요약",
        "청년미래적금 9월 추가모집, 이것만은 확인하세요",
        [
            "대상: 만 19~34세 청년, 3년 만기 자유적립식 저축상품",
            "1차 결과: 신청 234만명 중 실제 가입 138만명 수준",
            "추가모집: 9월 중 검토 중, 정확한 일정은 미정",
            "혜택: 기본금리 연 5%+우대금리, 정부기여금 일반형 6%·우대형 12%, 이자소득 비과세",
        ],
        pal_key="blue",
    )
    make_table_card(
        f"{base1}/청년미래적금-조건비교표.png",
        "조건 비교",
        "청년미래적금 일반형 · 우대형 조건표",
        [
            ("가입 대상", "만 19~34세 청년"),
            ("일반형 개인소득", "6,000만원 이하 또는 소상공인 연매출 3억원 이하"),
            ("우대형 개인소득", "3,600만원 이하 또는 소상공인 연매출 1억원 이하"),
            ("일반형 가구소득", "중위소득 200% 이하(맞벌이 250%)"),
            ("우대형 가구소득", "중위소득 150% 이하(맞벌이 200%)"),
            ("일반형 정부기여금", "월 납입액의 6%"),
            ("우대형 정부기여금", "월 납입액의 12%"),
            ("월 50만원 납입시 기여금", "일반형 108만원 / 우대형 216만원(3년)"),
            ("종합 수익률 효과", "일반형 연 13.2~14.4% / 우대형 연 18.2~19.4%"),
        ],
        pal_key="blue",
    )

    # ---- Post 2: 넷플릭스 스캔들 ----
    make_cover(
        f"{base1}/넷플릭스스캔들-cover.png",
        "OTT 신작",
        ["넷플릭스 스캔들", "9월18일 공개"],
        "손예진 지창욱 나나가 펼치는 위험한 사랑 내기, 줄거리와 출연진을 정리합니다.",
        pal_key="rose",
    )
    make_summary_card(
        f"{base1}/넷플릭스스캔들-핵심요약.png",
        "핵심요약",
        "넷플릭스 스캔들, 시청 전 이것만은 확인하세요",
        [
            "공개일: 9월 18일 오후 5시, 8부작 전편 동시 공개",
            "원작: 1782년 소설 「위험한 관계」를 조선시대로 각색, 2003년 영화의 시리즈 리메이크",
            "주연: 손예진(조씨부인)·지창욱(조원)·나나(희연), 연출 정지우 감독",
            "관전포인트: 위험한 사랑 내기를 둘러싼 심리극과 국악 요소, 파격적인 로맨스 수위",
        ],
        pal_key="rose",
    )
    make_table_card(
        f"{base1}/넷플릭스스캔들-캐릭터표.png",
        "캐릭터 정보",
        "넷플릭스 스캔들 캐릭터 · 기본 정보표",
        [
            ("조씨부인 (손예진)", "재능을 감춘 채 살아야 했던 사대부가 규수"),
            ("조원 (지창욱)", "조선 최고의 연애꾼으로 불리는 인물"),
            ("희연 (나나)", "위험한 사랑 내기에 얽혀드는 순수한 여인"),
            ("연출", "정지우 감독"),
            ("원작", "「위험한 관계」(1782년 프랑스 소설)"),
            ("공개 정보", "9월 18일 오후 5시, 8부작 동시 공개"),
            ("전작 비교", "2003년 영화 「스캔들」, 관객 350만명"),
        ],
        pal_key="rose",
    )
