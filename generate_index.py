#!/usr/bin/env python3
"""
GARAMwiki — index.html 자동 생성기
====================================
사용법: python generate_index.py
새 HTML 파일을 추가한 뒤 이 스크립트를 실행하면 index.html이 자동으로 갱신됩니다.

파일명 → 카드 정보 변환 규칙:
  - 파일명에서 날짜(YYYY-MM) 자동 추출
  - 폴더명으로 카테고리 자동 분류
  - ARTICLE_META 딕셔너리에 제목/태그를 수동으로 추가하면 더 풍부한 카드가 만들어집니다.
"""

import os, re
from pathlib import Path
from datetime import date

# ───────────────────────────────────────────────
# 1. 아티클 메타데이터 (파일명 → 제목 / 태그)
#    새 파일 추가 시 여기에 한 줄 추가하세요.
# ───────────────────────────────────────────────
ARTICLE_META = {
    # 비즈니스 인텔리전스
    "2026-05_Korea_AI_DataCenter_Business_Strategy.html": {
        "title": "대한민국 AI 데이터센터 사업 환경 분석<br>및 수행 전략 2026 — PESTLE·SWOT·법적 환경",
        "tags":  ["AI 데이터센터", "AIDC 특별법", "AI 기본법", "비수도권 특구", "GPUaaS"],
    },
    "2026-02_FDE_Definitive_Guide_Vinoo_Ganesh.html": {
        "title": "The Definitive Guide to Forward Deployed Engineering<br>— Vinoo Ganesh (Next Play Newsletter)",
        "tags":  ["FDE", "Palantir", "Project Frontline", "Customer Outcomes", "Enterprise AI Deployment"],
    },
    "2025-12_Sapphire_2026_AI_10예측.html": {
        "title": "Sapphire Ventures — 2026 AI<br>10대 예측: 엔터프라이즈·인프라·혁신",
        "tags":  ["$1T IPO", "$50B M&A", "에너지 제약", "오픈소스 모델", "로보틱스"],
    },
    "2026-05_아모데이_제본스역설_화이트칼라.html": {
        "title": "AI가 화이트칼라를 대체할까,<br>아니면 10배 생산성을 줄까?",
        "tags":  ["Jevons Paradox", "Amdahl's Law", "Dario Amodei", "화이트칼라", "Fortune"],
    },
    "2026-05_다리오아모데이_SaaS붕괴경고.html": {
        "title": "Dario Amodei: SaaS 소프트웨어<br>복잡성은 더 이상 해자가 아니다",
        "tags":  ["SaaS 붕괴", "해자 소멸", "Anthropic", "Yahoo Finance", "Jamie Dimon"],
    },
    "2026-05_YC_RFS_Summer2026.html": {
        "title": "YC Requests for Startups<br>— Summer 2026 16개 테마",
        "tags":  ["YCombinator", "Company Brain", "SaaS 도전자", "Agent용 SW", "반도체 공급망"],
    },
    "2026-05_삼성구글_AI글라스.html": {
        "title": "베일 벗은 삼성·구글 'AI 글라스'<br>— 스마트폰 없이 길 안내·번역 척척",
        "tags":  ["Samsung", "Google", "Android XR", "Gemini", "웨어러블"],
    },
    "2026-05_오픈AI앤트로픽_SI영토확장.html": {
        "title": "OpenAI·Anthropic의 SI 영토 확장<br>— 파운데이션 모델에서 구현 레이어로",
        "tags":  ["OpenAI", "Anthropic", "SI", "FDE", "Lock-in"],
    },
    "2026-03_YC_로보틱스_스타트업.html": {
        "title": "YC 로보틱스 스타트업 98개<br>— 10개 카테고리 전체 지도",
        "tags":  ["YCombinator", "로보틱스", "휴머노이드", "방위드론", "데이터인프라"],
    },
    "2026-07_MIT_TR_Korea_Vol27_AI에이전트_NextWorker.html": {
        "title": "MIT Technology Review Korea Vol.27 — AI 에이전트 The Next Worker<br>챗봇 이후의 AI · 피지컬 AI · 멀티에이전트 위험 · 10대 키워드 (2026 7·8월호)",
        "tags":  ["MIT TR Korea", "AI 에이전트", "The Next Worker", "피지컬 AI", "멀티에이전트", "AI 거버넌스"],
    },
    "2026-07_AI_Frontier_EP102_샌프란시스코교훈_사람들이다미쳐요.html": {
        "title": "AI Frontier EP102 — 샌프란시스코의 교훈: \"사람들이 다 미쳐요\"<br>노정석 현장 르포 · HumanX $3,995 · AX 조건 · VIZCOM \"Mission Is the Moat\" · McKinsey 6% 성과율",
        "tags":  ["AI Frontier", "노정석", "Chester Roh", "샌프란시스코", "실리콘밸리", "AI 과열", "VIZCOM", "Mission Is the Moat", "AX 조건", "McKinsey", "Snowflake Summit", "한국 창업자", "AI Psychosis", "HumanX", "GTC 2026"],
    },
    "2026-07_AI_Frontier_EP103_이해가_병목이_될_때.html": {
        "title": "AI Frontier EP103 — 이해가 병목이 될 때<br>노정석·최승준·박종현 · Fable 쿼터 폭발 · 서브에이전트 모델 선택 · 인지 부채 · LMArena vs Artificial Analysis (2026-07-12)",
        "tags":  ["AI Frontier", "노정석", "최승준", "박종현", "Fable", "인지 부채", "Cognitive Debt", "서브에이전트", "이해 병목", "Thariq Shihipar", "지도와 영토", "Korzybski", "Artificial Analysis", "LMArena", "Jagged Intelligence", "Llama 4", "경계 설계", "퀴즈 학습", "세대 단층", "평가 깃발"],
    },
    "2026-07_Geoffrey_Litt_이해가_병목_Understanding_Bottleneck_인사이트.html": {
        "title": "Geoffrey Litt — 이해가 새로운 병목이다: Verify가 아닌 Participate를 위해<br>Notion 디자인 엔지니어 · /explain-diff · 퀴즈 속도조절기 · 마이크로 월드 · 인지 부채 · Alan Kay 증강 비전 (AI Engineer 2026-07-02)",
        "tags":  ["Geoffrey Litt", "이해 병목", "Understanding Bottleneck", "Verify vs Participate", "인지 부채", "Cognitive Debt", "Margaret Storey", "explain-diff", "마이크로 월드", "Micro-world", "퀴즈 속도조절기", "Seymour Papert", "Mathland", "Alan Kay", "Andy Matuschak", "Quantum Country", "Simon Willison", "Notion", "AI Engineer", "Peter Naur", "공유 멘탈 모델", "증강 vs 자동화"],
    },
    "2024-09_EO_Decoupling_Harvard_MBA_Teixeira.html": {
        "title": "하버드 MBA가 가장 먼저 가르치는 전략 — 디커플링(Decoupling)으로 시장을 훔쳐라<br>Thales Teixeira · 고객 가치 사슬 3유형 · 5단계 고객 훔치기 · AI 디커플링 가속 · EO Korea (2024-09)",
        "tags":  ["디커플링", "Thales Teixeira", "고객 가치 사슬", "Customer Value Chain", "EO Korea", "하버드 MBA", "비즈니스 모델", "디지털 파괴", "Uber", "Airbnb", "Netflix", "AI 디커플링", "스타트업 전략", "Counter-Decouple", "Unlocking the Customer Value Chain"],
    },
    "2026-06_a16z_Cycles_Different_But_Same_Bits_to_Atoms.html": {
        "title": "a16z Charts of the Week — 사이클은 같고 다르다: Bits → Atoms 대순환<br>Moses Sternstein · 로보틱스 $16B 역대 최고 · AI 네이티브 매핑 문제 · Accenture 30×→6× · 솔로프레너 2× (2026-06-26)",
        "tags":  ["Moses Sternstein", "a16z", "Bits to Atoms", "로보틱스 Physical AI", "AI 네이티브", "Accenture FCF", "솔로프레너", "그로서리 생산성 역설", "YC 배치", "Stripe Economics", "섹터 순환", "사이클 분석"],
    },
    # 나의 인사이트
    "2026-05_AI_Native_vs_Agent_Native_전략_분석.html": {
        "title": "AI-Native vs Agent-Native — 개념 정의·전략·실행 플랜<br>Garambada 심층 분석 보고서",
        "tags":  ["AI-Native", "Agent-Native", "Owned Intelligence", "Agent Manager", "소로프레너"],
    },
    "2026-05_AI_Frontier_EP98_의도가_남는_시대_김서준_Hashed.html": {
        "title": "AI Frontier EP98 — AI가 실행하는 시대, 인간에게 남는 건 '의도'<br>(Hashed 김서준 대표 × 노정석)",
        "tags":  ["AI Frontier", "김서준", "Hashed", "의도", "바이브 코딩", "VC 위기"],
    },
    "2026-05_Hermes_Agent_분석_NousResearch.html": {
        "title": "Hermes Agent — The Agent That Grows With You<br>Nous Research 오픈소스 자율 AI 에이전트 분석",
        "tags":  ["Hermes Agent", "Nous Research", "SKILL.md", "Closed Learning Loop", "오픈소스 에이전트"],
    },
    "2026-02_Venture_Studio_Asset_Class_Mandalore.html": {
        "title": "벤처 스튜디오, 새로운 자산 클래스로의 진화<br>— Mandalore Partners 2026 자산 기반 모델 분석",
        "tags":  ["벤처스튜디오", "자산 클래스", "Dual-Layer", "자산 기반 모델", "기관투자"],
    },
    "2026-05_AI_Frontier_EP97_AI_Psychosis_인사이트.html": {
        "title": "AI Frontier EP97 — AI Psychosis 시대<br>슈퍼 앱·Only One·T_brain 인사이트",
        "tags":  ["AI Psychosis", "T_brain", "Only One", "AI Native", "노정석·최승준"],
    },
    "2026-05_xAI_가스터빈_규제루프홀_인사이트.html": {
        "title": "xAI 가스터빈 46기 — AI 인프라 경쟁의<br>숨겨진 규제 루프홀과 사업 리스크",
        "tags":  ["xAI", "규제 루프홀", "ESG 리스크", "에너지 조달", "NAACP 소송"],
    },
    "2026-05_Anthropic_SMB_인사이트.html": {
        "title": "Anthropic이 SMB를 공략하는<br>진짜 이유 — 나의 인사이트",
        "tags":  ["Claude for SMB", "유통 채널 전쟁", "버티컬 AI", "GTM", "신뢰 설계"],
    },
    "2026-06_MattPocock_grillme_AI에이전트정렬기법_인사이트.html": {
        "title": "grill-me — AI 에이전트 정렬의 기술<br>Matt Pocock Skills 135k★ · 3문장이 바꾸는 워크플로",
        "tags":  ["grill-me", "Matt Pocock", "AI 에이전트 정렬", "Claude Code Skills", "공유 언어", "숙의 프로세스"],
    },
    "2026-07_AI_부메랑_재고용_AI_Boomerang.html": {
        "title": "AI 부메랑(AI Boomerang) — AI 때문에 해고했던 직원을 다시 채용하는 이유<br>고용주 55% 후회 · 32% 재고용 · 제도적 지식의 반격",
        "tags":  ["AI 부메랑", "재고용", "Robert Half", "Forrester", "Gartner", "제도적 지식", "AI ROI", "인력 전략"],
    },
    # 트렌드 인텔리전스
    "2026-02_HBR_Google_Cloud_Agentic_AI_Blueprint.html": {
        "title": "HBR × Google Cloud — 전사 에이전틱 AI 전환 블루프린트<br>3가지 치명적 실수와 첫 번째 행동",
        "tags":  ["HBR", "Google Cloud", "Agentic AI", "Agent Sprawl", "멀티에이전트"],
    },
    "2026-05_MS_Work_Trend_Index_2026_에이전트_인간_주체성.html": {
        "title": "Microsoft 2026 Work Trend Index<br>— 에이전트 시대, 인간 주체성의 재정의",
        "tags":  ["Microsoft WTI", "Frontier Firm", "Transformation Paradox", "Learning System", "AI Agency"],
    },
    "2026-07_Stanford_HAI_AI_Index_2026_연례보고서.html": {
        "title": "Stanford HAI 2026 AI Index Report<br>— $581.7B 투자·SWE-bench 100%·개발자 -20%·미중 2.7% 격차 · 기술-거버넌스 비대칭 심화",
        "tags":  ["Stanford HAI", "AI Index 2026", "AI 현황 보고서", "AI 투자", "미중 AI 경쟁", "AI 노동시장", "SWE-bench", "AI 거버넌스", "생성AI 보급", "환경비용"],
    },
    "트렌드_레이더_2026-05.html": {
        "title": "GARAMwiki AI 트렌드 레이더 2026<br>🔴 16 긴급 주목 · 🟡 13 주목 관찰 · DSpark×YMTC·Stanford HAI·패트릭 드닌 수록 · 2026-07-05 업데이트",
        "tags":  ["트렌드 레이더", "AI 시장 동향", "C레벨 인텔리전스", "AI 전략", "즉각 행동", "DSpark", "YMTC", "CXMT", "Stanford HAI", "패트릭 드닌", "수출통제", "Enterprise Agentic"],
    },
    "2026-05_KPMG_Venture_Pulse_Q1_2026_Global.html": {
        "title": "KPMG Venture Pulse Q1 2026<br>— 글로벌 VC 투자 역대 최고 $3,309억, AI 메가딜 집중",
        "tags":  ["KPMG Venture Pulse", "글로벌 VC", "OpenAI $122B", "AI 메가딜", "방산 테크"],
    },
    "2026-05_Google_Gemini_AI레이스역전.html": {
        "title": "Google Gemini, AI 레이스 역전<br>— 9억 사용자, 유일한 흑자 AI",
        "tags":  ["Google I/O 2026", "Gemini 3.5", "Gemini Spark", "월드모델"],
    },
    "2026-05_DeepSeek_V4.html": {
        "title": "DeepSeek V4 — 오픈소스가<br>프론티어를 추월하다",
        "tags":  ["DeepSeek V4", "수학·코딩 1위", "$0.28/1M", "오픈소스"],
    },
    "2026-05_LLM_Inference_TokenEconomics.html": {
        "title": "LLM 추론 인프라 &amp;<br>토큰 이코노믹스",
        "tags":  ["추론 인프라", "토큰 경제학", "GPU 클러스터"],
    },
    "2026-05_Boris_Cherny_Coding_Solved.html": {
        "title": "Boris Cherny — Why Coding<br>Is Solved (Sequoia AI Ascent)",
        "tags":  ["AI 코딩", "Sequoia", "소프트웨어 미래"],
    },
    "2026-05_Karpathy_VibeCoding_to_AgenticEngineering.html": {
        "title": "Karpathy — Vibe Coding에서<br>Agentic Engineering으로",
        "tags":  ["Karpathy", "에이전틱 엔지니어링", "Sequoia"],
    },
    "2026-05_Demis_Hassabis_AGI_75percent.html": {
        "title": "Demis Hassabis — AGI까지<br>75% 완료 (Sequoia)",
        "tags":  ["AGI", "DeepMind", "Sequoia", "AlphaFold"],
    },
    "2026-05_Jim_Fan_Robotics_EndGame.html": {
        "title": "Jim Fan — Robotics Endgame<br>물리 AI의 최종 목표",
        "tags":  ["로보틱스", "NVIDIA", "물리 AI", "Sequoia"],
    },
    "2026-05_Dolgov_Waymo_Full_Autonomy.html": {
        "title": "Dmitri Dolgov — Waymo<br>Full Autonomy 로드맵",
        "tags":  ["Waymo", "자율주행", "파운데이션 모델"],
    },
    "2026-05_Brockman_Human_Attention_Bottleneck.html": {
        "title": "Greg Brockman — Human Attention<br>is the Bottleneck",
        "tags":  ["Greg Brockman", "OpenAI", "인간 주의력", "Sequoia"],
    },
    "2026-05_Sequoia_This_is_AGI.html": {
        "title": "Sequoia Capital —<br>This Is AGI",
        "tags":  ["AGI", "Sequoia", "AI Ascent 2026"],
    },
    "2018-03_POSTECH_AI_수학적한계분석.html": {
        "title": "POSTECH — AI의<br>수학적 한계 분석",
        "tags":  ["POSTECH", "수학적 한계", "AI 이론", "아카이브"],
    },
    # 나의 인사이트
    "2026-05_월드모델_파운데이션모델_그리고AI.html": {
        "title": "월드모델, 파운데이션 모델<br>그리고 AI — 보이지 않는 것들",
        "tags":  ["월드모델", "LLM 한계", "F=ma → E=mc²", "디지털 트윈"],
    },
    "2026-04_AI능력한계_시스템관점.html": {
        "title": "AI 능력·한계 재고찰<br>— 시스템 관점에서",
        "tags":  ["AI 한계", "시스템 사고", "C-레벨 인사이트"],
    },
    # 모델 트래커
    "2026-06_Claude_Opus48_Fable5_AI경쟁_EP99_AI_Frontier.html": {
        "title": "Claude Opus 4.8 · Fable 5 · AI 경쟁 2026<br>EP99: 모델보다 운용 구조가 경쟁을 결정한다 (AI Frontier)",
        "tags":  ["Claude Opus 4.8", "Fable 5", "Mythos 5", "Dynamic Workflows", "AI 경쟁"],
    },
    "2026-05_Google_IO2026_풀스택AI_에이전트시대.html": {
        "title": "Google I/O 2026 — 풀스택 AI에서<br>에이전트 시대로 (DH Shin 심층 보고서)",
        "tags":  ["Google I/O 2026", "Gemini 3.5", "Antigravity 2.0", "Gemini Spark", "TPU 8세대"],
    },
    "2026-03_AI_10x레버리지_AX실행론_심층분석_인사이트.html": {
        "title": "AI 10x Leverage 두 방향성과<br>AX 실행론 심층 분석 (노정석·BFACTORY)",
        "tags":  ["AI 10x", "AX 실행론", "1/10x", "임계점 이론", "Pilot Purgatory"],
    },
    "2026-05_Gavin_Baker_Watts_Wafers_Orbital_Compute_인사이트.html": {
        "title": "Gavin Baker — Watts &amp; Wafers:<br>Orbital Compute·TSMC·Frontier Models 인사이트",
        "tags":  ["Watts & Wafers", "Orbital Compute", "TSMC", "Blackwell", "SaaS Death Trap"],
    },
    "경량문명_나의인사이트.html": {
        "title": "경량문명의 도래와 기업의 미래<br>— 초개인화 AI 시대 대응 전략",
        "tags":  ["경량문명", "AX", "거래비용이론", "1인기업", "솔로프리너"],
    },
    # 비즈니스 인텔리전스
    "공공기관_AX_Company_Builder_Wiki.html": {
        "title": "공공기관 AX × AI-Native<br>Company Builder 전략 보고서",
        "tags":  ["공공기관", "AX", "철도공단", "항만공사", "Company Builder"],
    },
    # 사업 현안
    "2026-04_AI도입_AI성숙도사다리_섹시하지않은진실_TuringPost.html": {
        "title": "AI 도입의 섹시하지 않은 진실 — AI 성숙도 사다리 L0~L5<br>조직 재설계와 '지루한 기초 공사'의 중요성 (Turing Post Korea)",
        "tags":  ["AI 성숙도", "Maturity Ladder", "가독화", "데이터 신뢰", "조직 재설계"],
    },
    "2026-05_KRNA_설계도면_AI_검증_프로젝트_미팅보고.html": {
        "title": "KRNA 설계도면 수량·공사비 산출 AI 검증 프로젝트<br>5/27 미팅 보고 및 심층 대응 전략 — WISE42",
        "tags":  ["KRNA", "WISE42", "설계도면 AI", "3-Layer Architecture", "Living System"],
    },
    "2026-05_OctaPulse_수산양식_AI로보틱스_투자검토.html": {
        "title": "OctaPulse — 수산양식 AI 비전·로보틱스<br>투자 검토 보고서 (YC W26)",
        "tags":  ["Aquaculture", "YC W26", "Computer Vision", "Hatchery QA", "투자검토"],
    },
    "2026-05_레거시산업_AI혁신_FoundersStudio_컴퍼니빌더.html": {
        "title": "레거시 산업 AI 혁신 — AI-Native Solopreneur<br>기반 Founders Studio 컴퍼니 빌더 전략",
        "tags":  ["경량문명", "Founders Studio", "AI Growth Buyout", "Solopreneur", "LaaS"],
    },
    "2026-05_에너지인프라_AX_전환전략_PoC_PRD.html": {
        "title": "에너지 인프라 AX 전환전략 — AI 설계 기술 검증<br>용역 종합 기획서 PoC PRD (국가철도공단)",
        "tags":  ["GraphRAG", "PINN", "온톨로지", "SCADA", "전철전력 AX"],
    },
    "2026-05_Enterprise_AX_사업운영전략_FS_WISE42.html": {
        "title": "Enterprise AX 사업 운영 전략<br>Founders Studio × WISE42 — FDE 네트워크",
        "tags":  ["FDE", "Palantir 모델", "크로스 도메인 플랫폼", "Micro Unit", "WISE42"],
    },
    "2026-06_AI_Governance_Platform_린_Wise42_사업전략_v03.html": {
        "title": "AI Governance Platform 사업 진출 전략 v03 — 법무법인 린 × Wise42<br>공공·중견기업 AX 시장 기반 신사업 · AI 기본법 · 3~5조 TAM · 공공기관 AX 심층 분석",
        "tags":  ["AI Governance", "법무법인 린", "Wise42", "AI 기본법", "공공 AX", "TrustLayer"],
    },
    "2026-07_AI_Consulting_AX_전략_Wise42_FoundersStudio.html": {
        "title": "AI 컨설팅은 왜 실패하는가 — Wise42 × Founders Studio의 제대로 된 AX 전략<br>Discovery-First FDE · 글로벌 실패 원인 5가지 · 한국 시장 분석 · 4-레이어 서비스 모델 · 12개월 로드맵",
        "tags":  ["AI 컨설팅", "AX 전략", "FDE", "Wise42", "Founders Studio", "Discovery Sprint", "Outcome-Based", "Accenture FCF", "McKinsey 80%", "AI 기본법", "PoC 수집가", "Company Builder"],
    },
    "2026-06_AI_Governance_Platform_린Wise42_사업현안_v05.html": {
        "title": "AI Governance Platform 사업 진출 전략 v05 — 법무법인 린 × Wise42<br>보안×컴플라이언스 통합 관문 · 업스테이지 Solar LLM · AIM Intelligence · AI TRiSM · TOP 7 즉각 실행",
        "tags":  ["AI Governance", "법무법인 린", "Wise42", "보안×컴플라이언스 통합 관문", "N2SF", "ISMS-P", "AI TRiSM", "업스테이지", "AIM Intelligence", "Module 6", "Module 7", "국정원 15위협", "공공 AX", "v05"],
    },
    # 모델 트래커 (EP100)
    "2026-06_Claude_Fable5_Mythos5_수출통제_EP100_AI_Frontier.html": {
        "title": "Claude Fable 5 · Mythos 5 · 수출통제 D+3<br>EP100: 출시 3일 만에 美수출통제 — 다음 국면은? (AI Frontier)",
        "tags":  ["Claude Fable 5", "Mythos 5", "수출통제", "Project Glasswing", "SWE-Bench Pro 80.3%"],
    },
    "2026-06_Sakana_Fugu_오케스트레이션모델_모델트래커.html": {
        "title": "🐡 Sakana Fugu / Fugu Ultra — One Model to Command Them All<br>오케스트레이션 모델 · AI 주권 · 프런티어급 성능 · 단일 API",
        "tags":  ["Sakana AI", "Fugu Ultra", "오케스트레이션 모델", "AI 주권", "멀티에이전트", "ICLR 2026"],
    },
    "2026-06_OpenAI_GPT56_Sol_Terra_Luna_모델트래커.html": {
        "title": "GPT-5.6 Sol · Terra · Luna — OpenAI 차세대 모델 패밀리 전격 해부<br>ultra 멀티에이전트 모드 · 정부 검열 · 3-티어 가격 전략 · Cerebras 750tok/s",
        "tags":  ["GPT-5.6", "Sol", "Terra", "Luna", "OpenAI", "멀티에이전트", "ultra mode", "사이버보안 AI", "Cerebras"],
    },
    "2026-07_DeepSeek_DSpark_중국AI미래지도_HBM해자_메모리반도체.html": {
        "title": "DSpark × YMTC × CXMT — 중국AI미래지도: HBM 해자를 뚫는 소프트웨어 기병<br>DSpark 661% 처리량 · YMTC NAND 4위 · CXMT DRAM 4위 · 한국 1000조 투자 리스크 · GLM-5.2 1/8 비용",
        "tags":  ["DeepSeek DSpark", "Speculative Decoding", "YMTC", "CXMT", "HBM", "중국 메모리반도체", "GLM-5.2", "한국 메모리", "골드만삭스 리스크", "Apple CXMT", "DeepSpec", "Lineshine HPC", "중국AI미래지도", "화웨이 Ascend"],
    },
    # 담론 등등
    "2025-06_이병한_뉴노멀탐문_3부작_피터틸_기술공화국.html": {
        "title": "이병한 뉴노멀탐문 3부작 — 피터 틸·기술공화국·퍼스트코리아<br>아메리카·테크노차이나·대한민국 문명 탐문",
        "tags":  ["이병한", "피터 틸", "기술공화국", "알렉스 카프", "퍼스트코리아", "J.D. 밴스"],
    },
    "2026-05_미중_첨단기술질서_백서인_중앙일보.html": {
        "title": "미국과 중국이 은밀하게 논의하는<br>첨단기술 질서 — 백서인 (중앙일보)",
        "tags":  ["미·중 정상회담", "AI 거버넌스 NPT", "기술주권", "리커플링", "바이오보안법"],
    },
    "2026-07_패트릭드닌_포스트리버럴_자유주의실패_아사히_담론.html": {
        "title": "미국 사상의 지각변동 — 패트릭 드닌 × 아사히신문 인터뷰<br>포스트 리버럴 · 자유주의 실패의 역설 · 기묘한 연합 · 가톨릭 부상 · 밴스의 사상적 지주",
        "tags":  ["패트릭 드닌", "포스트 리버럴", "자유주의 실패", "J.D. 밴스", "트럼프 현상", "기묘한 연합", "가톨릭 부상", "레오 14세", "공동선", "복음주의 해체", "테크 우파", "아사히신문", "미국 보수 사상"],
    },
    "2026-07_FS_창업자_반성문_AI시대_5년비전_약속철학.html": {
        "title": "FS 창업자 반성문 — 적게 약속하고 더 많이 이루는 회사<br>60대 창업 · AI 사이클 12년→5년 · Under-promise Over-deliver · 영업이익·배당·이익분배 (2026-07)",
        "tags":  ["FS", "창업 철학", "반성문", "Under-promise Over-deliver", "60대 창업", "AI 사이클", "5년 비전", "영업이익", "배당", "이익 분배", "코스닥", "지속 가능한 회사", "이해관계자 자본주의", "LP", "펀드"],
    },
    "2026-05_스타벅스_탱크데이_규범윤리_정치철학_분석.html": {
        "title": "스타벅스 '탱크데이' 사건의<br>규범윤리학·정치철학적 분석",
        "tags":  ["5·18", "칸트·밀·샌델", "시장의 도덕적 한계", "상품화", "공동체주의"],
    },
    "2026-06_하버마스_이성의수호_어두워지는시대_NewYorker.html": {
        "title": "위르겐 하버마스 — 이성의 수호, 어두워지는 시대<br>공론장·커뮤니케이티브 이성·AI와 민주주의 (The New Yorker · Alex Ross)",
        "tags":  ["하버마스", "공론장", "커뮤니케이티브 이성", "생활세계", "숙의 민주주의", "AI와 민주주의"],
    },
    "2026-06_구글Debug_모기코드로잡는다_오즈지식토킹.html": {
        "title": "세계에서 가장 많이 사람을 죽이는 동물을, 코드로 잡는다<br>구글 Debug · 볼바키아 · 스케일 엔지니어링 (오즈의 지식토킹 · 안광섭)",
        "tags":  ["구글 Debug", "볼바키아", "공중보건 AI", "스케일 엔지니어링", "기술 적정화", "오즈의 지식토킹"],
    },
    # 심화 기술
    "2026-05_Paperclip_AI_Agent_Orchestration_Platform.html": {
        "title": "📎 Paperclip — AI 에이전트 오케스트레이션 플랫폼<br>Zero-Human Company 구현 심층 분석",
        "tags":  ["Paperclip", "에이전트 오케스트레이션", "Zero-Human Company", "BYOA", "오픈소스"],
    },
    "ontology-vs-genai-wiki.html": {
        "title": "온톨로지 기반 AI vs 생성형 LLM<br>— 판단하는 AI의 아키텍처 해부",
        "tags":  ["Ontology", "Knowledge Graph", "Neuro-Symbolic", "Palantir-class", "Sovereign AI"],
    },
    "2026-07_DSpark_Confidence_Scheduled_Speculative_Decoding_심화기술.html": {
        "title": "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation<br>반자기회귀 드래프트 · 신뢰도 스케줄링 · V4-Flash 60~85% 가속 · DeepSpec MIT 오픈소스",
        "tags":  ["DSpark", "Speculative Decoding", "Semi-Autoregressive Generation", "Confidence Scheduling", "Markov Head", "DFlash", "EAGLE-3", "DeepSpec", "LLM 추론 최적화", "Hardware-Aware Scheduler", "DeepSeek V4", "HBM 병목", "ICML 2026"],
    },
    "2026-07_DSPy_BitterLesson_Engineering_AI_Systems_WF26.html": {
        "title": "DSPy &amp; The Bitter Lesson — AI 시스템을 제대로 엔지니어링하는 법<br>Omar Khattab @ WF26 · 프롬프트는 끔찍한 추상화 · 선언형 시그니처 · DSPy 컴파일러 · Machine Studying",
        "tags":  ["DSPy", "Omar Khattab", "Bitter Lesson", "Rich Sutton", "Declarative Signatures", "Separation of Concerns", "WF26", "AI Engineer World's Fair 2026", "Databricks", "MIT EECS", "Machine Studying", "LLM 시스템 엔지니어링", "조기 최적화", "컴파일러", "관심사의 분리"],
    },
}

# ───────────────────────────────────────────────
# 2. 폴더 → 카테고리 매핑
# ───────────────────────────────────────────────
FOLDER_CAT = {
    "03_비즈니스_인텔리전스": ("비즈니스", "📊 비즈니스 인텔리전스", "biz"),
    "04_트렌드_인텔리전스":   ("트렌드",   "📡 트렌드 인텔리전스",   "trend"),
    "06_나의_인사이트":        ("인사이트", "💡 나의 인사이트",       "insight"),
    "02_모델_트래커":          ("모델",     "🔬 모델 트래커",          "model"),
    "05_심화_기술":            ("기술",     "🔩 심화 기술",            "tech"),
    "07_사업_현안":            ("사업현안", "🏢 사업 현안",             "issue"),
    "08_담론_등등":            ("담론",     "💬 담론 등등",             "discourse"),
}

# ───────────────────────────────────────────────
# 3. HTML 파일 스캔
# ───────────────────────────────────────────────
BASE = Path(__file__).parent

def scan_articles():
    articles = []
    for folder_key, (cat_id, cat_label, cat_class) in FOLDER_CAT.items():
        folder = BASE / folder_key
        if not folder.exists():
            continue
        for html in sorted(folder.rglob("*.html"), reverse=True):
            rel = html.relative_to(BASE)
            fname = html.name
            meta = ARTICLE_META.get(fname, {})
            date_match = re.match(r"(\d{4}-\d{2}(?:-\d{2})?)", fname)
            date_str = date_match.group(1) if date_match else "—"
            title = meta.get("title") or fname.replace(".html","").replace("_"," ")
            tags  = meta.get("tags", [])
            articles.append({
                "rel":       str(rel).replace("\\", "/"),
                "fname":     fname,
                "cat_id":    cat_id,
                "cat_label": cat_label,
                "cat_class": cat_class,
                "date":      date_str,
                "title":     title,
                "tags":      tags,
            })
    return articles

# ───────────────────────────────────────────────
# 4. 카드 HTML 생성
# ───────────────────────────────────────────────
def card_html(a):
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in a["tags"])
    return f'''
      <a class="card" data-cat="{a["cat_id"]}"
         href="./{a["rel"]}">
        <div class="card-meta">
          <span class="cat-badge {a["cat_class"]}">{a["cat_id"]}</span>
          <span class="card-date">{a["date"]}</span>
        </div>
        <div class="card-title">{a["title"]}</div>
        <div class="card-tags">{tags_html}</div>
        <span class="card-arrow">→</span>
      </a>'''

# ───────────────────────────────────────────────
# 5. 섹션 HTML 생성
# ───────────────────────────────────────────────
def sections_html(articles):
    from collections import defaultdict
    grouped = defaultdict(list)
    for a in articles:
        grouped[(a["cat_id"], a["cat_label"], a["cat_class"])].append(a)

    dot_colors = {"비즈니스":"var(--biz)","트렌드":"var(--trend)",
                  "인사이트":"var(--insight)","모델":"var(--model)",
                  "기술":"var(--tech)","사업현안":"var(--issue)",
                  "담론":"var(--discourse)"}

    html = ""
    for (cat_id, cat_label, cat_class), items in grouped.items():
        color = dot_colors.get(cat_id, "var(--accent)")
        cards = "\n".join(card_html(a) for a in items)
        html += f'''
  <section class="section" id="sec-{cat_id}" data-cat="{cat_id}">
    <div class="section-header">
      <div class="section-dot" style="background:{color}"></div>
      <span class="section-title">{cat_label}</span>
      <span class="section-count">{len(items)}개</span>
    </div>
    <div class="cards-grid">{cards}
    </div>
  </section>
'''
    return html

# ───────────────────────────────────────────────
# 6. filter-btn 생성
# ───────────────────────────────────────────────
def filter_buttons(articles):
    cats = list(dict.fromkeys(a["cat_id"] for a in articles))
    cat_labels = {a["cat_id"]: a["cat_label"] for a in articles}
    btns = '\n  <button class="filter-btn active" data-cat="전체" onclick="filterCat(this)">전체</button>'
    for c in cats:
        btns += f'\n  <button class="filter-btn" data-cat="{c}" onclick="filterCat(this)">{cat_labels[c]}</button>'
    return btns

# ───────────────────────────────────────────────
# 7. 전체 index.html 조립
# ───────────────────────────────────────────────
def build_index():
    articles = scan_articles()
    today    = date.today().isoformat()
    total    = len(articles)

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GARAMwiki — AI 지식 베이스</title>
<style>
  :root {{
    --bg: #0d1117; --surface: #161b22; --surface2: #21262d;
    --border: #30363d; --text: #e6edf3; --muted: #7d8590; --accent: #58a6ff;
    --biz: #f59e0b;   --biz-bg: rgba(245,158,11,0.08);
    --trend: #3b82f6; --trend-bg: rgba(59,130,246,0.08);
    --insight: #10b981; --insight-bg: rgba(16,185,129,0.08);
    --model: #a78bfa; --model-bg: rgba(167,139,250,0.08);
    --tech: #06b6d4;  --tech-bg: rgba(6,182,212,0.08);
    --issue: #f97316; --issue-bg: rgba(249,115,22,0.08);
    --discourse: #e879f9; --discourse-bg: rgba(232,121,249,0.08);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", sans-serif;
    min-height: 100vh; }}
  header {{ border-bottom: 1px solid var(--border); padding: 0 32px;
    position: sticky; top: 0; background: rgba(13,17,23,0.92);
    backdrop-filter: blur(12px); z-index: 100; }}
  .header-inner {{ max-width: 1200px; margin: 0 auto;
    display: flex; align-items: center; gap: 24px; height: 60px; }}
  .logo {{ font-size: 1.4rem; font-weight: 800; letter-spacing: -0.5px;
    background: linear-gradient(135deg,#58a6ff 0%,#a78bfa 50%,#10b981 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; white-space: nowrap; }}
  .logo span {{ font-weight:400; font-size:0.85rem; color:var(--muted);
    -webkit-text-fill-color:var(--muted); }}
  .search-wrap {{ flex:1; max-width:480px; position:relative; }}
  .search-wrap svg {{ position:absolute; left:12px; top:50%; transform:translateY(-50%); color:var(--muted); }}
  #searchInput {{ width:100%; padding:8px 12px 8px 36px; background:var(--surface2);
    border:1px solid var(--border); border-radius:8px; color:var(--text);
    font-size:0.9rem; outline:none; transition:border-color 0.2s; }}
  #searchInput:focus {{ border-color:var(--accent); }}
  #searchInput::placeholder {{ color:var(--muted); }}
  .header-stats {{ margin-left:auto; display:flex; gap:16px; }}
  .stat-chip {{ font-size:0.75rem; color:var(--muted); background:var(--surface2);
    border:1px solid var(--border); border-radius:20px; padding:4px 10px; white-space:nowrap; }}
  .stat-chip b {{ color:var(--text); }}
  .filter-bar {{ max-width:1200px; margin:0 auto; padding:20px 32px 0;
    display:flex; gap:8px; flex-wrap:wrap; align-items:center; }}
  .filter-label {{ font-size:0.8rem; color:var(--muted); margin-right:4px; }}
  .filter-btn {{ padding:5px 14px; border-radius:20px; border:1px solid var(--border);
    background:transparent; color:var(--muted); font-size:0.82rem; cursor:pointer; transition:all 0.15s; }}
  .filter-btn:hover {{ border-color:var(--accent); color:var(--text); }}
  .filter-btn.active {{ background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600; }}
  .filter-btn[data-cat="비즈니스"].active {{ background:var(--biz); border-color:var(--biz); }}
  .filter-btn[data-cat="트렌드"].active   {{ background:var(--trend); border-color:var(--trend); }}
  .filter-btn[data-cat="인사이트"].active {{ background:var(--insight); border-color:var(--insight); }}
  .filter-btn[data-cat="모델"].active     {{ background:var(--model); border-color:var(--model); }}
  .filter-btn[data-cat="기술"].active     {{ background:var(--tech); border-color:var(--tech); }}
  .filter-btn[data-cat="사업현안"].active {{ background:var(--issue); border-color:var(--issue); }}
  .filter-btn[data-cat="담론"].active     {{ background:var(--discourse); border-color:var(--discourse); }}
  main {{ max-width:1200px; margin:0 auto; padding:28px 32px 60px; }}
  .section {{ margin-bottom:40px; }}
  .section-header {{ display:flex; align-items:center; gap:12px; margin-bottom:16px;
    padding-bottom:10px; border-bottom:1px solid var(--border); }}
  .section-dot {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; }}
  .section-title {{ font-size:1rem; font-weight:700; letter-spacing:-0.2px; }}
  .section-count {{ font-size:0.8rem; color:var(--muted); margin-left:auto; }}
  .cards-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; }}
  .card {{ display:block; background:var(--surface); border:1px solid var(--border);
    border-radius:12px; padding:18px 20px; text-decoration:none; color:inherit;
    transition:transform 0.15s,border-color 0.15s,box-shadow 0.15s;
    position:relative; overflow:hidden; }}
  .card::before {{ content:''; position:absolute; top:0;left:0;right:0;
    height:3px; border-radius:12px 12px 0 0; }}
  .card[data-cat="비즈니스"]::before {{ background:var(--biz); }}
  .card[data-cat="트렌드"]::before   {{ background:var(--trend); }}
  .card[data-cat="인사이트"]::before {{ background:var(--insight); }}
  .card[data-cat="모델"]::before     {{ background:var(--model); }}
  .card[data-cat="기술"]::before     {{ background:var(--tech); }}
  .card[data-cat="사업현안"]::before {{ background:var(--issue); }}
  .card[data-cat="담론"]::before      {{ background:var(--discourse); }}
  .card:hover {{ transform:translateY(-2px); border-color:rgba(88,166,255,0.3);
    box-shadow:0 8px 24px rgba(0,0,0,0.4); }}
  .card[data-cat="비즈니스"]:hover {{ border-color:rgba(245,158,11,0.3); }}
  .card[data-cat="트렌드"]:hover   {{ border-color:rgba(59,130,246,0.3); }}
  .card[data-cat="인사이트"]:hover {{ border-color:rgba(16,185,129,0.3); }}
  .card[data-cat="모델"]:hover     {{ border-color:rgba(167,139,250,0.3); }}
  .card[data-cat="기술"]:hover     {{ border-color:rgba(6,182,212,0.3); }}
  .card[data-cat="사업현안"]:hover {{ border-color:rgba(249,115,22,0.3); }}
  .card[data-cat="담론"]:hover     {{ border-color:rgba(232,121,249,0.3); }}
  .card-meta {{ display:flex; align-items:center; gap:8px; margin-bottom:10px; }}
  .cat-badge {{ font-size:0.7rem; font-weight:700; padding:2px 8px;
    border-radius:10px; letter-spacing:0.3px; }}
  .cat-badge.biz     {{ background:var(--biz-bg); color:var(--biz); }}
  .cat-badge.trend   {{ background:var(--trend-bg); color:var(--trend); }}
  .cat-badge.insight {{ background:var(--insight-bg); color:var(--insight); }}
  .cat-badge.model   {{ background:var(--model-bg); color:var(--model); }}
  .cat-badge.tech    {{ background:var(--tech-bg); color:var(--tech); }}
  .cat-badge.issue      {{ background:var(--issue-bg); color:var(--issue); }}
  .cat-badge.discourse  {{ background:var(--discourse-bg); color:var(--discourse); }}
  .card-date {{ font-size:0.72rem; color:var(--muted); margin-left:auto; }}
  .card-title {{ font-size:0.95rem; font-weight:600; line-height:1.45;
    margin-bottom:8px; color:var(--text); }}
  .card-tags {{ display:flex; flex-wrap:wrap; gap:5px; }}
  .tag {{ font-size:0.68rem; padding:2px 7px; border-radius:6px;
    background:var(--surface2); color:var(--muted); border:1px solid var(--border); }}
  .card-arrow {{ position:absolute; bottom:16px; right:18px; font-size:0.85rem;
    color:var(--muted); opacity:0; transition:opacity 0.15s,right 0.15s; }}
  .card:hover .card-arrow {{ opacity:1; right:14px; }}
  .empty-state {{ text-align:center; padding:60px 20px; color:var(--muted); display:none; }}
  .empty-state.visible {{ display:block; }}
  .empty-state h3 {{ font-size:1.1rem; margin-bottom:8px; color:var(--text); }}
  .card.hidden, .section.hidden {{ display:none; }}
  footer {{ border-top:1px solid var(--border); text-align:center;
    padding:20px; font-size:0.78rem; color:var(--muted); }}
  footer a {{ color:var(--accent); text-decoration:none; }}
  @media (max-width:700px) {{
    header, main, .filter-bar {{ padding-left:16px; padding-right:16px; }}
    .header-stats {{ display:none; }}
    .cards-grid {{ grid-template-columns:1fr; }}
  }}
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="logo">GARAMwiki <span>/ AI 지식 베이스</span></div>
    <div class="search-wrap">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input id="searchInput" type="text" placeholder="제목, 태그로 검색…" autocomplete="off">
    </div>
    <div class="header-stats">
      <span class="stat-chip"><b id="totalCount">{total}</b> 아티클</span>
      <span class="stat-chip">업데이트 <b>{today}</b></span>
    </div>
  </div>
</header>

<div class="filter-bar">
  <span class="filter-label">필터</span>
  {filter_buttons(articles)}
</div>

<main>
{sections_html(articles)}
  <div class="empty-state" id="emptyState">
    <h3>검색 결과가 없습니다</h3>
    <p>다른 키워드나 태그로 검색해 보세요.</p>
  </div>
</main>

<footer>
  GARAMwiki · 개인 AI 지식 베이스 · 마지막 갱신 <b>{today}</b>
  &nbsp;|&nbsp; 새 파일 추가 후 <code>python generate_index.py</code> 또는 Claude에게 "랜딩 페이지 업데이트해줘"
</footer>

<script>
  const searchInput = document.getElementById("searchInput");
  searchInput.addEventListener("input", applyFilters);
  let activeCat = "전체";
  function filterCat(btn) {{
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    activeCat = btn.dataset.cat;
    applyFilters();
  }}
  function applyFilters() {{
    const q = searchInput.value.toLowerCase().trim();
    let n = 0;
    document.querySelectorAll(".card").forEach(card => {{
      const catMatch = activeCat === "전체" || card.dataset.cat === activeCat;
      const searchMatch = !q || card.innerText.toLowerCase().includes(q);
      card.classList.toggle("hidden", !(catMatch && searchMatch));
      if (catMatch && searchMatch) n++;
    }});
    document.querySelectorAll(".section").forEach(sec => {{
      sec.classList.toggle("hidden", sec.querySelectorAll(".card:not(.hidden)").length === 0);
    }});
    document.getElementById("emptyState").classList.toggle("visible", n === 0);
    document.getElementById("totalCount").textContent = n;
  }}
  document.addEventListener("keydown", e => {{
    if (e.key === "/" && document.activeElement !== searchInput) {{
      e.preventDefault(); searchInput.focus();
    }}
  }});
</script>
</body>
</html>'''

    out = BASE / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"✅ index.html 생성 완료 — {total}개 아티클 ({today})")
    print(f"   경로: {out}")

if __name__ == "__main__":
    build_index()
