#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from make_cards import make_cover, make_summary_card, make_table_card

base = "posts/2026-09-23"
os.makedirs(base, exist_ok=True)

# ---- Post 1: 기초연금 하후상박 개편 ----
make_cover(
    f"{base}/기초연금하후상박개편-cover.png",
    "정부정책",
    ["기초연금 하후상박 개편", "2027년 4월 월 38만원"],
    "소득 하위 30% 이하는 월 38만원, 부부감액은 20%에서 10%로 줄어드는 기초연금 개편안을 정리합니다.",
    pal_key="teal",
)
make_summary_card(
    f"{base}/기초연금하후상박개편-핵심요약.png",
    "핵심요약",
    "기초연금 하후상박 개편, 이것만은 확인하세요",
    [
        "수급기준: 소득 하위 70% 유지, 2027년 4월 시행 목표로 연내 입법 추진",
        "차등지급: 하위 30% 이하 348만명 월 38만원, 30~45%는 35만9000원, 45~70%는 35만원 동결",
        "부부감액 축소: 하위 45% 이하 부부가구 감액률 20%→10%, 하위 30% 부부는 월 56만→68만4000원",
        "직역연금 수급자·배우자도 소득 하위 45% 이하면 신규로 기초연금 수급 가능(약 11만명)",
    ],
    pal_key="teal",
)
make_table_card(
    f"{base}/기초연금하후상박개편-지급액표.png",
    "지급액 비교",
    "2027년 기초연금 개편안 소득구간별 지급액 총정리",
    [
        ("소득 하위 30% 이하(348만명)", "월 38만원(올해 대비 3만원 인상)"),
        ("소득 하위 30%초과~45%이하(174만명)", "월 35만9000원(9000원 인상)"),
        ("소득 하위 45%초과~70%이하", "월 35만원(동결)"),
        ("부부감액 비율(하위 45% 이하, 234만명)", "20%→10%로 축소"),
        ("하위 30% 이하 부부가구 수령액", "올해 월 56만원→내년 월 68만4000원"),
        ("직역연금 수급자·배우자 포함 기준", "소득 하위 45% 이하(약 11만명 신규)"),
        ("2027년 기초연금 예산", "25조 7000억원(올해 대비 2조 6000억원, 11%↑)"),
        ("시행 목표 시점", "2027년 4월(연내 입법 완료 목표)"),
    ],
    pal_key="teal",
)

# ---- Post 2: LGD 720Hz 게이밍 OLED 모니터 ----
make_cover(
    f"{base}/LGD720Hz게이밍모니터-cover.png",
    "IT전자제품",
    ["세계 최초 720Hz", "게이밍 OLED 모니터 공개"],
    "LG디스플레이가 양산한 24.5인치 720Hz OLED 패널과 ASUS ROG Swift OLED PG259QWS Ace 스펙을 정리합니다.",
    pal_key="amber",
)
make_summary_card(
    f"{base}/LGD720Hz게이밍모니터-핵심요약.png",
    "핵심요약",
    "세계 최초 720Hz 게이밍 OLED, 이것만은 확인하세요",
    [
        "발표: LG디스플레이, 9월 21일 24.5인치 720Hz 게이밍 OLED 패널 세계 최초 양산 발표",
        "스펙: FHD(1920x1080) 네이티브 해상도에서 720Hz 구현, 응답속도 0.02ms",
        "첫 탑재 제품: ASUS ROG Swift OLED PG259QWS Ace, Tandem WOLED 패널·위치센서 내장",
        "PGL CS2 Major Singapore 2026 공식 모니터 선정, 2026년 4분기 초 출시·유럽가 1149유로",
    ],
    pal_key="amber",
)
make_table_card(
    f"{base}/LGD720Hz게이밍모니터-스펙표.png",
    "스펙 총정리",
    "ASUS ROG Swift OLED PG259QWS Ace 스펙 총정리",
    [
        ("패널 크기", "24.5인치"),
        ("해상도", "FHD 1920x1080(네이티브)"),
        ("최대 주사율", "720Hz"),
        ("응답속도", "0.02ms(GtG)"),
        ("패널 타입", "Tandem WOLED(TrueBlack Glossy)"),
        ("개발사", "LG디스플레이(패널)·ASUS(완제품)"),
        ("특징 기능", "위치센서(높이·기울기·스위블 기록)"),
        ("공식 대회 지정", "PGL CS2 Major Singapore 2026"),
        ("출시 시기", "2026년 4분기 초"),
        ("가격(유럽 기준)", "1149유로(MSRP)"),
    ],
    pal_key="amber",
)

print("all done")
