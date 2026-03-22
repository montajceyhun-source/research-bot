"""
searcher.py — Çox mənbəli ağıllı axtarış sistemi

Prioritet sırası:
  1. Serper.dev   (aylıq 2,500 pulsuz — ən yaxşı keyfiyyət)
  2. Google CSE   (aylıq 100 pulsuz   — Google-un öz nəticələri)
  3. DuckDuckGo   (limitsiz ehtiyat   — API açarı lazım deyil)
"""

import requests
from bs4 import BeautifulSoup
import config


# ─── 1. Serper.dev ────────────────────────────────────────────────────────

def _search_serper(query: str, n: int) -> list[dict]:
    """
    Serper.dev — Google nəticələrini qaytarır.
    Aylıq 2,500 sorğu pulsuz. https://serper.dev
    """
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY"   : config.SERPER_API_KEY,
                "Content-Type": "application/json",
            },
            json={"q": query, "num": n, "gl": "az", "hl": "az"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()

        results = []
        for item in data.get("organic", [])[:n]:
            results.append({
                "title"  : item.get("title", ""),
                "url"    : item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source" : "serper",
            })

        # Knowledge Graph varsa əlavə et
        kg = data.get("knowledgeGraph", {})
        if kg.get("description"):
            results.insert(0, {
                "title"  : kg.get("title", query),
                "url"    : kg.get("descriptionUrl", ""),
                "snippet": kg.get("description", ""),
                "source" : "serper_kg",
            })

        return results
    except Exception as e:
        print(f"  [Serper xətası] {e}")
        return []


# ─── 2. Google Custom Search Engine ──────────────────────────────────────

def _search_google_cse(query: str, n: int) -> list[dict]:
    """
    Google Programmable Search Engine.
    Aylıq 100 sorğu pulsuz. https://programmablesearchengine.google.com
    """
    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": config.GOOGLE_CSE_API_KEY,
                "cx" : config.GOOGLE_CSE_ID,
                "q"  : query,
                "num": min(n, 10),
                "lr" : "lang_az",
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()

        return [
            {
                "title"  : item.get("title", ""),
                "url"    : item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source" : "google_cse",
            }
            for item in data.get("items", [])[:n]
        ]
    except Exception as e:
        print(f"  [Google CSE xətası] {e}")
        return []


# ─── 3. DuckDuckGo (ehtiyat) ─────────────────────────────────────────────

def _search_duckduckgo(query: str, n: int) -> list[dict]:
    """DuckDuckGo — API açarı lazım deyil, ehtiyat mənbə."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            return [
                {
                    "title"  : r.get("title", ""),
                    "url"    : r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source" : "duckduckgo",
                }
                for r in ddgs.text(query, max_results=n)
            ]
    except Exception as e:
        print(f"  [DuckDuckGo xətası] {e}")
        return []


# ─── Ağıllı axtarış orkestrasyonu ────────────────────────────────────────

def search_web(topic: str) -> list[dict]:
    """
    Mövcud API açarlarına görə ən yaxşı mənbəni avtomatik seçir.
    Hər mövzu üçün 2 fərqli sorğu (Azərbaycanca + İngiliscə) işlədir.
    """
    n = config.SEARCH_RESULTS_COUNT
    results = []

    # Hansı motor aktiv olduğunu müəyyən et
    has_serper = bool(config.SERPER_API_KEY)
    has_google = bool(config.GOOGLE_CSE_API_KEY and config.GOOGLE_CSE_ID)

    if has_serper:
        engine = "Serper.dev"
        fn     = _search_serper
    elif has_google:
        engine = "Google CSE"
        fn     = _search_google_cse
    else:
        engine = "DuckDuckGo"
        fn     = _search_duckduckgo

    print(f"  🔍 Axtarış motoru: {engine}")

    # Sorğu 1: mövzunun özü
    r1 = fn(f"{topic} araşdırma analiz statistika", n)
    results.extend(r1)

    # Sorğu 2: ingilis dilində daha geniş mənbə
    r2 = fn(f"{topic} research analysis overview facts", n // 2)
    results.extend(r2)

    # Serper varsa əlavə "latest" sorğusu da at
    if has_serper and len(results) < 6:
        r3 = _search_serper(f"{topic} latest trends 2024 2025", 4)
        results.extend(r3)

    # Dublikatları sil (eyni URL)
    seen   = set()
    unique = []
    for r in results:
        if r["url"] and r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    print(f"  📋 {len(unique)} unikal mənbə tapıldı")
    return unique


# ─── Səhifə məzmunu çəkmə ─────────────────────────────────────────────────

def fetch_page_content(url: str, max_chars: int = 4000) -> str:
    """URL-dən əsas məzmunu çəkir (reklamlar olmadan)."""
    if not url or not url.startswith("http"):
        return ""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        # Lazımsız tag-ları sil
        for tag in soup(["script", "style", "nav", "footer",
                         "header", "aside", "form", "iframe",
                         "noscript", "advertisement"]):
            tag.decompose()

        # Prioritet ilə əsas məzmunu axtar
        content = ""
        for selector in ["article", "main", '[role="main"]',
                         ".content", "#content", ".post-content",
                         ".entry-content", "div"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator=" ", strip=True)
                if len(text) > 300:
                    content = text
                    break

        if not content:
            content = soup.get_text(separator=" ", strip=True)

        # Artıq boşluqları təmizlə
        content = " ".join(content.split())
        return content[:max_chars]

    except Exception:
        return ""


# ─── Tam araşdırma toplama ────────────────────────────────────────────────

def gather_research(topic: str) -> dict:
    """
    Mövzu üzrə tam araşdırma məlumatı topla.
    """
    print(f"\n🔬 '{topic}' araşdırılır...")
    search_results = search_web(topic)

    sources      = []
    full_content = []

    for i, r in enumerate(search_results[:8]):
        if not r.get("url"):
            continue

        print(f"  📄 [{i+1}] {r['url'][:65]}...")
        page_text = fetch_page_content(r["url"])

        # Snippet-i də saxla — bəzən tam mətnə çıxış olmur
        combined = page_text or r.get("snippet", "")

        source = {
            "index"  : i + 1,
            "title"  : r["title"],
            "url"    : r["url"],
            "snippet": r.get("snippet", ""),
            "content": combined,
            "engine" : r.get("source", "unknown"),
        }
        sources.append(source)

        if combined:
            full_content.append(
                f"[Mənbə {i+1} | {r['title']}]\n{combined}\n"
            )

    total_chars = sum(len(s["content"]) for s in sources)
    print(f"  ✅ {len(sources)} mənbə, {total_chars:,} simvol məlumat toplandı")

    return {
        "topic"      : topic,
        "sources"    : sources,
        "raw_content": "\n\n".join(full_content),
    }
