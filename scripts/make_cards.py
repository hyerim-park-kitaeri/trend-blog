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
    base1 = "posts/2026-09-22"
    os.makedirs(base1, exist_ok=True)

    # ---- Post 1: 가계부채비율 착시 / 집값 양극화 (한은 금융안정보고서) ----
    make_cover(
        f"{base1}/가계부채비율착시-cover.png",
        "경제이슈",
        ["가계부채비율 70%대", "착시효과와 집값 양극화"],
        "한은 9월 금융안정보고서로 보는 가계부채비율 하락의 이면과 강남·중랑 집값 엇갈린 흐름을 정리합니다.",
        pal_key="blue",
    )
    make_summary_card(
        f"{base1}/가계부채비율착시-핵심요약.png",
        "핵심요약",
        "가계부채비율 착시효과, 이것만은 확인하세요",
        [
            "가계부채비율: 2025년 말 88.1% → 2026년 1분기 85.3% → 2분기 약 81%로 하락 추세",
            "착시 논란: 부채 감소가 아닌 명목 GDP 확대 효과, 연말엔 70%대 중후반 전망",
            "집값 양극화: 8월 대책 이후 강남·서초 하락, 중랑·성북·서대문은 3%대 상승",
            "취약고리: 자영업자 대출 1098조 5000억원, 취약 자영업자 연체율 12.71%",
        ],
        pal_key="blue",
    )
    make_table_card(
        f"{base1}/가계부채비율착시-핵심수치표.png",
        "핵심 수치",
        "한은 9월 금융안정보고서 핵심 수치 총정리",
        [
            ("가계부채비율(2025년 말)", "88.1%"),
            ("가계부채비율(2026년 1분기)", "85.3%"),
            ("가계부채비율(2026년 2분기, 추정)", "약 81%"),
            ("가계부채비율(2026년 연말 전망)", "70%대 중후반"),
            ("관리 임계치", "80~85%"),
            ("자영업자 대출 잔액(2분기 말)", "1098조 5000억원"),
            ("취약 자영업자 연체율", "12.71%"),
            ("전체 취약차주 비중", "6.8%(0.1%p 상승)"),
            ("강남구 아파트값(8월 대책 후)", "1.28% 하락"),
            ("서초구 아파트값(8월 대책 후)", "0.94% 하락"),
            ("중랑구 아파트값(8월 대책 후)", "3.46% 상승"),
            ("성북구 아파트값(8월 대책 후)", "3.36% 상승"),
            ("서대문구 아파트값(8월 대책 후)", "3.15% 상승"),
        ],
        pal_key="blue",
    )

    # ---- Post 2: 추석 보이스피싱·스미싱 주의보 ----
    make_cover(
        f"{base1}/추석보이스피싱주의보-cover.png",
        "생활안전",
        ["추석 택배·환전 사칭", "보이스피싱·스미싱 주의보"],
        "9월 24~27일 추석 연휴를 노린 스미싱 수법과 금융당국이 안내한 예방·대처법을 정리합니다.",
        pal_key="rose",
    )
    make_summary_card(
        f"{base1}/추석보이스피싱주의보-핵심요약.png",
        "핵심요약",
        "추석 보이스피싱·스미싱 주의보, 이것만은 확인하세요",
        [
            "발표: 금융위·금감원이 9월 20일, 9월 24~27일 추석 연휴 앞두고 공동 주의보",
            "주요 수법: '택배 주소지 오류·배송불가', '명절 지원금', '환전' 미끼 스미싱",
            "위험성: 악성 앱 설치 시 원격조종, 112·금감원 전화도 사기범에 강제 연결(콜포워딩)",
            "대처법: 공식 앱·대표번호로 직접 확인, 감염 시 즉시 비행기모드 후 통신사 방문 초기화",
        ],
        pal_key="rose",
    )
    make_table_card(
        f"{base1}/추석보이스피싱주의보-예방수칙표.png",
        "예방수칙",
        "추석 보이스피싱·스미싱 예방 수칙 총정리",
        [
            ("주의보 발표", "금융위원회·금융감독원, 9월 20일 공동 발표"),
            ("경계 기간", "추석 연휴 9월 24일~27일"),
            ("대표 수법 1", "택배 주소지 오류·배송불가 문자 + 악성 URL"),
            ("대표 수법 2", "지자체 사칭 명절 지원금 문자"),
            ("대표 수법 3", "해외여행 후 환전 미끼 정보 탈취"),
            ("감염 시 위험", "휴대폰 원격조종, 신고전화 콜포워딩 피해"),
            ("기본 예방수칙", "출처 불명 URL 클릭 금지, 공식 앱·대표번호로 확인"),
            ("의심 문자 확인", "카카오톡 '보호나라' 채널 스미싱 메뉴 조회"),
            ("안드로이드 설정", "'보안 위험 자동 차단' 기능 활성화"),
            ("감염 후 대처", "비행기모드 전환 또는 전원 차단 후 통신사 방문 초기화"),
            ("올해 1~7월 발생 건수", "7940건(전년 대비 46% 감소)"),
            ("올해 1~7월 피해액", "3614억원(전년 대비 53% 감소)"),
        ],
        pal_key="rose",
    )
