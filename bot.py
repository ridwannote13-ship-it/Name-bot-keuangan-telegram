from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ===== AMBIL GOOGLE JSON DARI RAILWAY ENV =====
google_json = os.getenv("GOOGLE_JSON")
creds_dict = json.loads(google_json)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict, scope)

client = gspread.authorize(creds)
sheet = client.open("Laporan Keuangan Bot").sheet1


async def masuk(update, context):
    nominal = context.args[0]
    ket = " ".join(context.args[1:])
    tanggal = datetime.now().strftime("%d-%m-%Y")

    sheet.append_row([tanggal, "Masuk", nominal, ket])
    await update.message.reply_text("✅ Pemasukan tersimpan")


async def keluar(update, context):
    nominal = context.args[0]
    ket = " ".join(context.args[1:])
    tanggal = datetime.now().strftime("%d-%m-%Y")

    sheet.append_row([tanggal, "Keluar", nominal, ket])
    await update.message.reply_text("✅ Pengeluaran tersimpan")


async def text_handler(update, context):
    text = update.message.text.lower().split()

    if len(text) == 0:
        return

    if text[0] == "masuk":
        nominal = text[1]
        ket = " ".join(text[2:])
        tanggal = datetime.now().strftime("%d-%m-%Y")

        sheet.append_row([tanggal, "Masuk", nominal, ket])
        await update.message.reply_text("✅ Pemasukan tersimpan")

    elif text[0] == "keluar":
        nominal = text[1]
        ket = " ".join(text[2:])
        tanggal = datetime.now().strftime("%d-%m-%Y")

        sheet.append_row([tanggal, "Keluar", nominal, ket])
        await update.message.reply_text("✅ Pengeluaran tersimpan")

    elif text[0] == "saldo":
        data = sheet.get_all_values()[1:]

        total_masuk = 0
        total_keluar = 0

        for row in data:
            if row[1] == "Masuk":
                total_masuk += int(row[2])
            elif row[1] == "Keluar":
                total_keluar += int(row[2])

        saldo = total_masuk - total_keluar

        await update.message.reply_text(f"💰 Saldo sekarang: Rp {saldo}")


# ===== TOKEN DARI RAILWAY =====
TOKEN = os.getenv("TELEGRAM_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("masuk", masuk))
app.add_handler(CommandHandler("keluar", keluar))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
