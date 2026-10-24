#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate cover / summary / table card PNGs for the 2026-10-24 kimjang price post."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from make_cards import make_cover, make_summary_card, make_table_card

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "posts", "2026-10-24")
os.makedirs(BASE, exist_ok=True)

make_cover(
    os.path.join(BASE, "김장철물가-cover.png"),
    "생활경제",
    ["배추값은 내리고", "새우젓값은 뛰었다"],
    "2026년 김장철을 앞두고 배추·무·양념채소는 내렸지만 새우젓은 32% 급등한 물가 상황을 정리합니다.",
    pal_key="amber",
)

make_summary_card(
    os.path.join(BASE, "김장철물가-핵심요약.png"),
    "핵심요약",
    "2026년 김장철 물가, 이것만은 확인하세요",
    [
        "배추 소매가 포기당 5,557원으로 작년보다 10.3% 낮고, 무도 개당 2,262원으로 7.1% 낮음(aT, 10월 16일 기준)",
        "대파·생강·깐마늘 등 양념채소도 작년보다 10~17%대 낮음, 출하량 증가가 배경",
        "새우젓은 1kg 20,269원으로 작년보다 32.5% 급등, 생산량 감소가 원인으로 알려짐",
        "정부는 11월부터 배추 등 재료 공급 확대와 할인 지원을 시행할 계획으로 알려짐",
    ],
    pal_key="amber",
)

make_table_card(
    os.path.join(BASE, "김장철물가-재료별가격표.png"),
    "재료별 가격",
    "2026년 김장철 주요 재료별 가격 총정리",
    [
        ("배추(포기당)", "5,557원, 작년보다 10.3% 하락"),
        ("무(1개)", "2,262원, 작년보다 7.1% 하락"),
        ("대파(1kg)", "2,774원, 작년보다 17.4% 하락"),
        ("생강(1kg)", "12,555원, 작년보다 16.2% 하락"),
        ("깐마늘(1kg)", "10,150원, 작년보다 10.5% 하락"),
        ("양파(1kg)", "작년보다 3.6% 하락"),
        ("국산 고춧가루(1kg)", "작년보다 3.5% 하락"),
        ("새우젓(1kg)", "20,269원, 작년보다 32.5% 급등"),
        ("멸치액젓(1kg)", "6,268원, 작년보다 3.0% 상승"),
    ],
    pal_key="amber",
)
