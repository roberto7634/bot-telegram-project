import os
import pandas as pd
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("TOKEN")
FILE = "database_project.xlsx"

# ================= INIT DATABASE =================
def init_db():
    if not os.path.exists(FILE):
        with pd.ExcelWriter(FILE) as writer:
            pd.DataFrame(columns=["ID","Nama","Nilai"]).to_excel(writer,"Projects",index=False)
            pd.DataFrame(columns=["Tanggal","ProjectID","Nama"]).to_excel(writer,"Absensi",index=False)
            pd.DataFrame(columns=["Tanggal","ProjectID","Jenis","Jumlah","Keterangan"]).to_excel(writer,"Keuangan",index=False)

# ================= MENU =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Tambah Project", callback_data="add_project")],
        [InlineKeyboardButton("📝 Absen", callback_data="absen")],
        [InlineKeyboardButton("💰 Keuangan", callback_data="keuangan")],
    ]
    await update.message.reply_text(
        "MENU UTAMA",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BUTTON =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_project":
        context.user_data["mode"] = "add_project"
        await query.message.reply_text("Ketik nama project:")

    elif query.data == "absen":
        context.user_data["mode"] = "absen"
        await query.message.reply_text("Ketik nama untuk absen:")

    elif query.data == "keuangan":
        context.user_data["mode"] = "keuangan"
        await query.message.reply_text("Format: masuk 100000 keterangan")

# ================= HANDLE TEXT =================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    text = update.message.text

    if mode == "add_project":
        df = pd.read_excel(FILE, sheet_name="Projects")
        new_id = len(df) + 1
        df.loc[len(df)] = [new_id, text, 0]
        df.to_excel(FILE, sheet_name="Projects", index=False)
        await update.message.reply_text("Project ditambahkan.")

    elif mode == "absen":
        df = pd.read_excel(FILE, sheet_name="Absensi")
        df.loc[len(df)] = [datetime.now(), 1, text]
        df.to_excel(FILE, sheet_name="Absensi", index=False)
        await update.message.reply_text("Absen tersimpan.")

    elif mode == "keuangan":
        data = text.split()
        df = pd.read_excel(FILE, sheet_name="Keuangan")
        df.loc[len(df)] = [datetime.now(), 1, data[0], int(data[1]), " ".join(data[2:])]
        df.to_excel(FILE, sheet_name="Keuangan", index=False)
        await update.message.reply_text("Keuangan tersimpan.")

    context.user_data["mode"] = None

# ================= MAIN =================
def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
