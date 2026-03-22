import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "BURAYA_YAZIN")
GEMINI_API_KEY     = os.environ.get("GEMINI_API_KEY",     "BURAYA_YAZIN")

# ── Axtarış API-ları (prioritet sırası ilə istifadə edilir) ──────────────
# 1. Serper.dev  — aylıq 2,500 pulsuz  → https://serper.dev
# 2. Google CSE  — aylıq 100 pulsuz    → https://programmablesearchengine.google.com
# 3. DuckDuckGo  — ehtiyat, həmişə aktiv (API açarı lazım deyil)
SERPER_API_KEY        = os.environ.get("SERPER_API_KEY",        "")
GOOGLE_CSE_API_KEY    = os.environ.get("GOOGLE_CSE_API_KEY",    "")
GOOGLE_CSE_ID         = os.environ.get("GOOGLE_CSE_ID",         "")

# Hər axtarışda neçə nəticə götürülsün
SEARCH_RESULTS_COUNT = 8

# Slayd sayı
MIN_SLIDES = 10
MAX_SLIDES = 15
