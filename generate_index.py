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
    # 나의 인사이트
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
    # 트렌드 인텔리전스
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
}

# ───────────────────────────────────────────────
# 2. 폴더 → 카테고리 매핑
# ───────────────────────────────────────────────
FOLDER_CAT = {
    "03_비즈니스_인텔리전스": ("비즈니스", "📊 비즈니스 인텔리전스", "biz"),
    "04_트렌드_인텔리전스":   ("트렌드",   "📡 트렌드 인텔리전스",   "trend"),
    "06_나의_인사이트":        ("인사이트", "💡 나의 인사이트",       "insight"),
    "02_모델_트래커":          ("모델",     "🔬 모델 트래커",          "model"),
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
                  "인사이트":"var(--insight)","모델":"var(--model)"}

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
  .card:hover {{ transform:translateY(-2px); border-color:rgba(88,166,255,0.3);
    box-shadow:0 8px 24px rgba(0,0,0,0.4); }}
  .card[data-cat="비즈니스"]:hover {{ border-color:rgba(245,158,11,0.3); }}
  .card[data-cat="트렌드"]:hover   {{ border-color:rgba(59,130,246,0.3); }}
  .card[data-cat="인사이트"]:hover {{ border-color:rgba(16,185,129,0.3); }}
  .card[data-cat="모델"]:hover     {{ border-color:rgba(167,139,250,0.3); }}
  .card-meta {{ display:flex; align-items:center; gap:8px; margin-bottom:10px; }}
  .cat-badge {{ font-size:0.7rem; font-weight:700; padding:2px 8px;
    border-radius:10px; letter-spacing:0.3px; }}
  .cat-badge.biz     {{ background:var(--biz-bg); color:var(--biz); }}
  .cat-badge.trend   {{ background:var(--trend-bg); color:var(--trend); }}
  .cat-badge.insight {{ background:var(--insight-bg); color:var(--insight); }}
  .cat-badge.model   {{ background:var(--model-bg); color:var(--model); }}
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
