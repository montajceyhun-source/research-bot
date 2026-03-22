"""
bot.py — Araşdırma Telegram Botu
İstifadəsi: mövzu yazırsınız → araşdırır → mətn + .pptx göndərir
"""
import os
import asyncio
import tempfile
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import config
from searcher    import gather_research
from analyzer    import build_presentation_structure, generate_telegram_report
from pptx_builder import build_pptx

# ─── Yardımçı funksiyalar ─────────────────────────────────────────────────

async def _typing(update: Update):
    await update.message.chat.send_action("typing")


async def _send_long(update: Update, text: str):
    """4096 simvol limitini keçsə, bölüb göndər."""
    for i in range(0, len(text), 4000):
        await update.message.reply_text(
            text[i:i+4000], parse_mode="Markdown"
        )


# ─── Komandalar ───────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Araşdırma Botuna Xoş Gəldiniz!*\n\n"
        "İstənilən mövzunu yazın, mən:\n"
        "1️⃣ İnternetdə araşdırma aparacağam\n"
        "2️⃣ Mənbələri analiz edəcəyəm\n"
        "3️⃣ Telegram-da ətraflı hesabat göndərəcəyəm\n"
        "4️⃣ Hazır `.pptx` təqdimat faylı göndərəcəyəm\n\n"
        "📝 *Misal:* `Süni intellektin gələcəyi`\n"
        "📝 *Misal:* `Azərbaycan iqtisadiyyatı 2024`\n"
        "📝 *Misal:* `Yenilenən enerji mənbələri`",
        parse_mode="Markdown"
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *Necə istifadə etmək olar:*\n\n"
        "• Sadəcə istənilən mövzunu yazın\n"
        "• Bot 2-4 dəqiqə ərzində cavab verəcək\n"
        "• Həm mətn hesabatı, həm də .pptx faylı alacaqsınız\n\n"
        "⏳ Araşdırma müddəti mövzudan asılıdır (1-4 dəq)",
        parse_mode="Markdown"
    )


# ─── Əsas məntiq ──────────────────────────────────────────────────────────

async def handle_topic(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """İstifadəçi mövzu yazdıqda çağırılır."""
    topic = update.message.text.strip()

    if len(topic) < 3:
        await update.message.reply_text("⚠️ Zəhmət olmasa daha ətraflı mövzu yazın.")
        return

    # ── 1. Başlanğıc bildirişi ────────────────────────────────────────────
    status_msg = await update.message.reply_text(
        f"🔍 *\"{topic}\"* mövzusu araşdırılır...\n\n"
        "⏳ Bu 2-4 dəqiqə çəkəcək. Zəhmət olmasa gözləyin.",
        parse_mode="Markdown"
    )

    try:
        # ── 2. İnternet araşdırması ───────────────────────────────────────
        await status_msg.edit_text(
            f"🌐 *\"{topic}\"*\n\n"
            "📡 İnternetdə mənbələr axtarılır... (1/4)",
            parse_mode="Markdown"
        )
        research = await asyncio.get_event_loop().run_in_executor(
            None, gather_research, topic
        )

        # ── 3. AI analizi ─────────────────────────────────────────────────
        await status_msg.edit_text(
            f"🤖 *\"{topic}\"*\n\n"
            "🧠 Gemini AI məlumatları analiz edir... (2/4)",
            parse_mode="Markdown"
        )
        structure = await asyncio.get_event_loop().run_in_executor(
            None, build_presentation_structure, research
        )

        # ── 4. Telegram hesabatı ──────────────────────────────────────────
        await status_msg.edit_text(
            f"📝 *\"{topic}\"*\n\n"
            "✍️ Hesabat yazılır... (3/4)",
            parse_mode="Markdown"
        )
        report = await asyncio.get_event_loop().run_in_executor(
            None, generate_telegram_report, structure, topic
        )

        # ── 5. PPTX yaratma ───────────────────────────────────────────────
        await status_msg.edit_text(
            f"📊 *\"{topic}\"*\n\n"
            "🎨 PowerPoint faylı hazırlanır... (4/4)",
            parse_mode="Markdown"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            pptx_path = os.path.join(tmpdir, f"{topic[:40].replace(' ', '_')}.pptx")
            pptx_ok   = await asyncio.get_event_loop().run_in_executor(
                None, build_pptx, structure, pptx_path
            )

            # ── 6. Nəticələri göndər ─────────────────────────────────────
            await status_msg.delete()

            # Mətn hesabatı
            await _send_long(update, report)

            # PPTX faylı
            if pptx_ok and os.path.exists(pptx_path):
                slide_count = len(structure.get("slides", []))
                await update.message.reply_document(
                    document=open(pptx_path, "rb"),
                    filename=f"{topic[:40]}.pptx",
                    caption=(
                        f"📊 *{topic}*\n"
                        f"📑 {slide_count} slayd | "
                        f"🌐 {len(research['sources'])} mənbə\n\n"
                        f"💡 _{structure.get('key_message', '')}_"
                    ),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    "⚠️ PPTX faylı yaradılarkən problem yarandı. "
                    "Lakin yuxarıdakı mətn hesabatını istifadə edə bilərsiniz."
                )

    except Exception as e:
        await status_msg.edit_text(
            f"❌ *Xəta baş verdi:*\n`{str(e)[:200]}`\n\n"
            "Zəhmət olmasa yenidən cəhd edin.",
            parse_mode="Markdown"
        )
        print(f"[Bot xətası] {e}")
        raise


# ─── Botu başlat ──────────────────────────────────────────────────────────

def main():
    print("🚀 Araşdırma Botu başladılır...")
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic))

    print("✅ Bot aktiv — Telegram-da mövzu yazın!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
