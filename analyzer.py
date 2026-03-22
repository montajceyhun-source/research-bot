"""
analyzer.py — Gemini ilə araşdırma məlumatını strukturlaşdırma
"""
import google.generativeai as genai
import json
import config

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def _clean_json(raw: str) -> dict | list:
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("[") if raw.find("[") < raw.find("{") and raw.find("[") != -1 else raw.find("{")
        if raw.find("[") != -1 and (raw.find("{") == -1 or raw.find("[") < raw.find("{")):
            end = raw.rfind("]") + 1
        else:
            end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
        raise


def build_presentation_structure(research: dict) -> dict:
    """
    Toplanan məlumatdan 10-15 slaydlıq təqdimat strukturu qur.
    """
    sources_summary = "\n".join(
        f"- [{s['index']}] {s['title']}: {s['snippet'][:200]}"
        for s in research["sources"]
    )

    prompt = f"""
Sən peşəkar tədqiqatçı və təqdimat mütəxəssisisən.
Aşağıdakı mövzu üzrə toplanmış internet məlumatlarını analiz et və
10-15 slaydlıq peşəkar təqdimat strukturu yarat.

MÖVZU: {research['topic']}

TOPLANMIŞ MƏLUMATLAR:
{research['raw_content'][:6000]}

MƏNBƏLƏR:
{sources_summary}

Azərbaycan dilində JSON formatında cavab ver (yalnız JSON, heç bir əlavə mətn yox):
{{
  "title": "Təqdimatın başlığı",
  "subtitle": "Alt başlıq",
  "key_message": "Əsas mesaj (1 cümlə)",
  "slides": [
    {{
      "number": 1,
      "type": "title",
      "title": "Slayd başlığı",
      "content": ["Məqam 1", "Məqam 2"],
      "speaker_note": "Təqdimatçı üçün qeyd"
    }}
  ],
  "sources": [
    {{"index": 1, "title": "Mənbə adı", "url": "https://..."}}
  ],
  "summary": "3-5 cümlə ilə ümumi xülasə"
}}

Slayd növləri (type): title, overview, problem, data, analysis, comparison, timeline, insight, recommendation, conclusion, sources

Hər slaydda content massivindəki məqamlar qısa (max 10 söz) olsun.
Mütləq real məlumat, statistika və istinadlar daxil et.
"""

    raw = model.generate_content(prompt).text
    return _clean_json(raw)


def generate_telegram_report(structure: dict, topic: str) -> str:
    """
    Telegram üçün oxunaqlı mətn hesabatı yarat.
    """
    prompt = f"""
Aşağıdakı təqdimat strukturuna əsasən Telegram üçün ətraflı araşdırma hesabatı yaz.

MÖVZU: {topic}
STRUKTUR: {json.dumps(structure, ensure_ascii=False)}

Azərbaycan dilində Telegram Markdown formatında yaz:
- *qalın* mətn üçün ulduz
- Hər bölmə üçün emoji
- Əsas statistika və faktları vurgula
- Mənbələri sonda göstər
- 600-900 söz həcmində olsun

Format:
🔍 *[Başlıq]*

📌 *Xülasə*
...

📊 *Əsas Tapıntılar*
...

💡 *Tövsiyələr*
...

📚 *Mənbələr*
...
"""
    return model.generate_content(prompt).text.strip()
