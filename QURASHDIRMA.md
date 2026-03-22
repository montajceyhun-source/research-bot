# 🔬 Araşdırma Botu — Quraşdırma Bələdçisi
## Railway.app ilə tamamilə pulsuz

---

## 💰 Xərc: 0 ₼

| Servis | Limit | Qiymət |
|--------|-------|--------|
| Serper.dev axtarış | Aylıq 2,500 | Pulsuz |
| Google CSE | Aylıq 100 (ehtiyat) | Pulsuz |
| DuckDuckGo | Limitsiz (ehtiyat) | Pulsuz |
| Gemini AI | Gündə 1,500 sorğu | Pulsuz |
| Telegram Bot | Limitsiz | Pulsuz |
| Railway.app | Aylıq 500 saat | Pulsuz |

---

## ADDIM 1 — API Açarlarını Alın

### 📱 Telegram Bot Token
1. Telegram-da **@BotFather**-a yazın
2. `/newbot` göndərin, ad və username yazın
3. Aldığınız token → `TELEGRAM_BOT_TOKEN`
4. **@userinfobot**-a yazın → chat ID → (lazım deyil bu bot üçün, bot hər kəsə cavab verir)

---

### 🤖 Gemini API (AI üçün)
1. **https://aistudio.google.com/app/apikey** açın
2. Google hesabınızla daxil olun
3. **"Create API Key"** basın
4. Açarı kopyalayın → `GEMINI_API_KEY`

---

### 🔍 Serper.dev (əsas axtarış — aylıq 2,500 pulsuz)
1. **https://serper.dev** açın
2. Google ilə qeydiyyat (1 dəqiqə)
3. Dashboard-da **API Key** görünəcək
4. Kopyalayın → `SERPER_API_KEY`

> ✅ Bu açar olsa sistem çox yaxşı işləyir.
> Aylıq 2,500 axtarış = gündə ~80 araşdırma.

---

### 🌐 Google CSE (ehtiyat — aylıq 100 pulsuz, könüllü)
Serper bitdikdə avtomatik Google-a keçir.

**API Key:**
1. **https://console.cloud.google.com** açın
2. Yeni proje → "Custom Search API" axtarın → Enable
3. Credentials → Create API Key → `GOOGLE_CSE_API_KEY`

**Search Engine ID:**
1. **https://programmablesearchengine.google.com** açın
2. "New search engine" → "Search the entire web" seçin
3. Search engine ID-ni kopyalayın → `GOOGLE_CSE_ID`

> ℹ️ Bu addım könüllüdür. Serper.dev bitdikdə ehtiyat kimi işləyir.

---

## ADDIM 2 — GitHub-a Yükləyin

```bash
git init
git add .
git commit -m "Araşdırma botu v2"
git remote add origin https://github.com/SizinAd/research-bot.git
git push -u origin main
```

---

## ADDIM 3 — Railway Quraşdırması

1. **https://railway.app** → GitHub ilə daxil olun
2. "New Project" → "Deploy from GitHub repo"
3. `research-bot` reponu seçin
4. **Variables** bölməsinə bu açarları əlavə edin:

```
TELEGRAM_BOT_TOKEN  = 1234567890:AAF...      ← mütləq
GEMINI_API_KEY      = AIzaSy...              ← mütləq
SERPER_API_KEY      = abc123...              ← tövsiyə edilir
GOOGLE_CSE_API_KEY  = AIzaSy...              ← könüllü
GOOGLE_CSE_ID       = 123456789...           ← könüllü
```

5. Deploy avtomatik başlayır — 2-3 dəqiqə gözləyin

---

## ADDIM 4 — Test Edin

Telegram-da botunuza yazın:
```
/start
```
Sonra mövzu yazın:
```
Süni intellektin gələcəyi
```

2-4 dəqiqədən sonra:
- 📝 Ətraflı mətn hesabatı
- 📊 10-15 slaydlı `.pptx` faylı

---

## Sistem Necə İşləyir

```
Siz mövzu yazırsınız
        ↓
Serper.dev → Google-dan real nəticələr (ən yaxşı)
        ↓  (Serper bitsə)
Google CSE → Google-un öz axtarışı (ehtiyat)
        ↓  (Google da bitsə)
DuckDuckGo → həmişə aktiv ehtiyat
        ↓
Hər mənbənin içi oxunur (tam mətn)
        ↓
Gemini AI analiz edib strukturlaşdırır
        ↓
Telegram: mətn hesabatı + .pptx fayl
```

---

## Aylıq Limit Hesablaması

| Ssenari | Gündəlik araşdırma |
|---------|-------------------|
| Yalnız Serper | ~80 araşdırma/gün |
| Serper + Google | ~83 araşdırma/gün |
| Hamısı bitdikdə | DuckDuckGo — limitsiz (keyfiyyət aşağı) |

Əksər istifadəçilər üçün **aylıq 2,500 Serper** sorğusu tamamilə kifayətdir.
