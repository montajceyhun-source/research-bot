"""
pptx_builder.py — Araşdırma strukturundan .pptx fayl yaratma
Node.js + pptxgenjs istifadə edir
"""
import json
import subprocess
import tempfile
import os


# Rəng palitrası — "Midnight Executive" mövzusu
COLORS = {
    "bg_dark"   : "1E2761",   # Tünd arxa fon (başlıq/nəticə)
    "bg_light"  : "F8F9FD",   # Açıq arxa fon (məzmun)
    "primary"   : "1E2761",   # Əsas rəng
    "accent"    : "4A90D9",   # Vurğu rəngi
    "text_dark" : "1A1A2E",   # Tünd mətn
    "text_light": "FFFFFF",   # Açıq mətn
    "text_muted": "6B7280",   # Solğun mətn
    "card_bg"   : "FFFFFF",   # Kart arxa fonu
}

TYPE_ICONS = {
    "title"         : "🎯",
    "overview"      : "📋",
    "problem"       : "⚠️",
    "data"          : "📊",
    "analysis"      : "🔬",
    "comparison"    : "⚖️",
    "timeline"      : "📅",
    "insight"       : "💡",
    "recommendation": "🚀",
    "conclusion"    : "✅",
    "sources"       : "📚",
}


def build_pptx(structure: dict, output_path: str) -> bool:
    """
    Struktur məlumatından .pptx fayl yarat.
    """
    js_code = _generate_js(structure, output_path)

    # Müvəqqəti JS faylı
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js",
                                     delete=False, encoding="utf-8") as f:
        f.write(js_code)
        js_path = f.name

    try:
        result = subprocess.run(
            ["node", js_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"[PPTX xətası] {result.stderr[:500]}")
            return False
        return True
    except Exception as e:
        print(f"[PPTX xətası] {e}")
        return False
    finally:
        os.unlink(js_path)


def _escape(text: str) -> str:
    """JS string üçün xüsusi simvolları qaç."""
    return (str(text)
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", ""))


def _generate_js(structure: dict, output_path: str) -> str:
    slides    = structure.get("slides", [])
    title     = _escape(structure.get("title", "Araşdırma"))
    subtitle  = _escape(structure.get("subtitle", ""))
    sources   = structure.get("sources", [])

    slide_blocks = []

    for i, slide in enumerate(slides):
        stype   = slide.get("type", "content")
        stitle  = _escape(slide.get("title", ""))
        content = slide.get("content", [])
        is_dark = stype in ("title", "conclusion", "sources")
        bg      = COLORS["bg_dark"] if is_dark else COLORS["bg_light"]
        txt_col = COLORS["text_light"] if is_dark else COLORS["text_dark"]
        icon    = TYPE_ICONS.get(stype, "📌")

        # Müxtəlif slayd növləri
        if stype == "title":
            block = _title_slide(title, subtitle, bg)
        elif stype == "sources":
            block = _sources_slide(sources, bg, txt_col)
        elif stype == "data" and content:
            block = _data_slide(stitle, content, bg, txt_col, icon)
        else:
            block = _content_slide(stitle, content, bg, txt_col, icon, is_dark)

        slide_blocks.append(block)

    slides_js = "\n".join(slide_blocks)
    out_escaped = _escape(output_path)

    return f"""
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.title  = "{title}";

{slides_js}

pres.writeFile({{ fileName: "{out_escaped}" }})
  .then(() => console.log("✅ PPTX yaradıldı: {out_escaped}"))
  .catch(e => {{ console.error("❌ Xəta:", e); process.exit(1); }});
"""


def _title_slide(title: str, subtitle: str, bg: str) -> str:
    return f"""
// ── Başlıq Slaydı ──────────────────────────────────────────
{{
  let s = pres.addSlide();
  s.background = {{ color: "{bg}" }};

  // Üst aksent zolağı
  s.addShape(pres.shapes.RECTANGLE, {{
    x: 0, y: 0, w: 10, h: 0.08,
    fill: {{ color: "{COLORS['accent']}" }}, line: {{ color: "{COLORS['accent']}" }}
  }});

  // Sol dekor zolaq
  s.addShape(pres.shapes.RECTANGLE, {{
    x: 0.7, y: 1.5, w: 0.07, h: 2.6,
    fill: {{ color: "{COLORS['accent']}" }}, line: {{ color: "{COLORS['accent']}" }}
  }});

  // Başlıq
  s.addText("{title}", {{
    x: 1.0, y: 1.5, w: 8.0, h: 1.4,
    fontSize: 38, bold: true, color: "{COLORS['text_light']}",
    fontFace: "Calibri", valign: "middle", margin: 0
  }});

  // Alt başlıq
  s.addText("{subtitle}", {{
    x: 1.0, y: 3.1, w: 8.0, h: 0.8,
    fontSize: 16, color: "CADCFC",
    fontFace: "Calibri", valign: "middle", margin: 0
  }});

  // Alt zolaq
  s.addShape(pres.shapes.RECTANGLE, {{
    x: 0, y: 5.1, w: 10, h: 0.525,
    fill: {{ color: "{COLORS['accent']}", transparency: 40 }},
    line: {{ color: "{COLORS['accent']}" }}
  }});
  s.addText("AI tərəfindən hazırlanmış araşdırma", {{
    x: 0.5, y: 5.15, w: 9, h: 0.4,
    fontSize: 11, color: "CADCFC", fontFace: "Calibri", margin: 0
  }});
}}
"""


def _content_slide(title: str, content: list, bg: str,
                   txt_col: str, icon: str, is_dark: bool) -> str:
    bullet_color = COLORS["text_light"] if is_dark else COLORS["text_dark"]
    header_bg    = COLORS["accent"] if is_dark else COLORS["primary"]

    items_js = ""
    for idx, item in enumerate(content[:8]):
        item_esc = _escape(str(item))
        br = "true" if idx < len(content) - 1 else "false"
        items_js += f'  {{ text: "{item_esc}", options: {{ bullet: true, breakLine: {br}, fontSize: 14, color: "{bullet_color}", paraSpaceAfter: 6 }} }},\n'

    return f"""
// ── Məzmun Slaydı: {title[:30]} ──
{{
  let s = pres.addSlide();
  s.background = {{ color: "{bg}" }};

  // Başlıq paneli
  s.addShape(pres.shapes.RECTANGLE, {{
    x: 0, y: 0, w: 10, h: 1.1,
    fill: {{ color: "{header_bg}" }}, line: {{ color: "{header_bg}" }}
  }});
  s.addText("{icon}  {title}", {{
    x: 0.4, y: 0, w: 9.2, h: 1.1,
    fontSize: 22, bold: true, color: "FFFFFF",
    fontFace: "Calibri", valign: "middle", margin: 0
  }});

  // Məzmun kartı
  s.addShape(pres.shapes.RECTANGLE, {{
    x: 0.4, y: 1.3, w: 9.2, h: 4.0,
    fill: {{ color: "{COLORS['card_bg']}" }},
    line: {{ color: "E2E8F0", width: 1 }},
    shadow: {{ type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.08 }}
  }});

  s.addText([
{items_js}
  ], {{
    x: 0.7, y: 1.5, w: 8.6, h: 3.6,
    fontFace: "Calibri", valign: "top"
  }});
}}
"""


def _data_slide(title: str, content: list, bg: str,
                txt_col: str, icon: str) -> str:
    """Statistika/data slaydı — böyük rəqəm kartları."""
    items = content[:4]
    card_w = 2.0
    spacing = (10 - 0.5 - len(items) * card_w) / (len(items) + 1)

    cards_js = ""
    for idx, item in enumerate(items):
        x = 0.5 + spacing + idx * (card_w + spacing)
        item_esc = _escape(str(item))
        # İlk söz böyük stat kimi, qalanı isə açıqlama
        parts = item_esc.split(" ", 2)
        stat  = parts[0] if parts else item_esc
        desc  = " ".join(parts[1:]) if len(parts) > 1 else ""

        cards_js += f"""
  s.addShape(pres.shapes.RECTANGLE, {{
    x: {x:.2f}, y: 1.5, w: {card_w}, h: 2.8,
    fill: {{ color: "{COLORS['card_bg']}" }},
    line: {{ color: "E2E8F0", width: 1 }},
    shadow: {{ type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.1 }}
  }});
  s.addShape(pres.shapes.RECTANGLE, {{
    x: {x:.2f}, y: 1.5, w: {card_w}, h: 0.07,
    fill: {{ color: "{COLORS['accent']}" }}, line: {{ color: "{COLORS['accent']}" }}
  }});
  s.addText("{stat}", {{
    x: {x:.2f}, y: 1.8, w: {card_w}, h: 1.2,
    fontSize: 30, bold: true, color: "{COLORS['primary']}",
    fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  }});
  s.addText("{desc}", {{
    x: {x + 0.1:.2f}, y: 3.1, w: {card_w - 0.2}, h: 1.0,
    fontSize: 12, color: "{COLORS['text_muted']}",
    fontFace: "Calibri", align: "center", valign: "top", margin: 0
  }});
"""

    return f"""
// ── Data Slaydı: {title[:30]} ──
{{
  let s = pres.addSlide();
  s.background = {{ color: "{bg}" }};
  s.addShape(pres.shapes.RECTANGLE, {{
    x: 0, y: 0, w: 10, h: 1.1,
    fill: {{ color: "{COLORS['primary']}" }}, line: {{ color: "{COLORS['primary']}" }}
  }});
  s.addText("{icon}  {title}", {{
    x: 0.4, y: 0, w: 9.2, h: 1.1,
    fontSize: 22, bold: true, color: "FFFFFF",
    fontFace: "Calibri", valign: "middle", margin: 0
  }});
  {cards_js}
}}
"""


def _sources_slide(sources: list, bg: str, txt_col: str) -> str:
    items_js = ""
    for idx, src in enumerate(sources[:10]):
        title_esc = _escape(src.get("title", "Mənbə"))
        url_esc   = _escape(src.get("url", ""))
        br = "true" if idx < len(sources) - 1 else "false"
        items_js += (
            f'  {{ text: "[{src.get("index", idx+1)}] {title_esc}", '
            f'options: {{ bullet: true, breakLine: {br}, fontSize: 13, '
            f'color: "CADCFC", paraSpaceAfter: 5 }} }},\n'
        )

    return f"""
// ── Mənbələr Slaydı ──
{{
  let s = pres.addSlide();
  s.background = {{ color: "{bg}" }};
  s.addShape(pres.shapes.RECTANGLE, {{
    x: 0, y: 0, w: 10, h: 1.1,
    fill: {{ color: "{COLORS['accent']}" }}, line: {{ color: "{COLORS['accent']}" }}
  }});
  s.addText("📚  İstifadə Edilən Mənbələr", {{
    x: 0.4, y: 0, w: 9.2, h: 1.1,
    fontSize: 22, bold: true, color: "FFFFFF",
    fontFace: "Calibri", valign: "middle", margin: 0
  }});
  s.addText([
{items_js}
  ], {{
    x: 0.6, y: 1.3, w: 8.8, h: 4.1,
    fontFace: "Calibri", valign: "top"
  }});
}}
"""
