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

# ===== GOOGLE AUTH =====
google_json = os.getenv("GOOGLE_JSON")
creds_dict = json.loads(google_json)

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# PAKSA KE SHEET DATA (PROFESSIONAL)
sheet = client.open("Laporan Keuangan Bot").worksheet("Data")


# ===== PARSE NOMINAL (BISA 14.000 / 14,000 / 14000)
def parse_nominal(n):
    return int(n.replace(".", "").replace(",", ""))


# ===== COMMAND MASUK
async def masuk(update, context):
    try:
        nominal = parse_nominal(context.args[0])
        ket = " ".join(context.args[1:])
    except:
        await update.message.reply_text("Format salah. Contoh:\n/masuk 10000 gaji")
        return

    tanggal = datetime.now().strftime("%d-%m-%Y")
    sheet.append_row([tanggal, "Masuk", nominal, ket])

    await update.message.reply_text("✅ Pemasukan tersimpan")


# ===== COMMAND KELUAR
async def keluar(update, context):
    try:
        nominal = parse_nominal(context.args[0])
        ket = " ".join(context.args[1:])
    except:
        await update.message.reply_text("Format salah. Contoh:\n/keluar 5000 makan")
        return

    tanggal = datetime.now().strftime("%d-%m-%Y")
    sheet.append_row([tanggal, "Keluar", nominal, ket])

    await update.message.reply_text("✅ Pengeluaran tersimpan")


# ===== CEK SALDO
async def saldo(update, context):
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


# ===== LAPORAN BULAN INI
async def laporan(update, context):
    data = sheet.get_all_values()[1:]
    bulan_ini = datetime.now().strftime("%m-%Y")

    total_masuk = 0
    total_keluar = 0

    for row in data:
        if bulan_ini in row[0]:
            if row[1] == "Masuk":
                total_masuk += int(row[2])
            elif row[1] == "Keluar":
                total_keluar += int(row[2])

    saldo = total_masuk - total_keluar

    await update.message.reply_text(
        f"📊 Laporan Bulan Ini\n"
        f"💰 Masuk : Rp {total_masuk}\n"
        f"💸 Keluar : Rp {total_keluar}\n"
        f"📈 Saldo : Rp {saldo}"
    )


# ===== FREE TEXT HANDLER
async def text_handler(update, context):
    text = update.message.text.lower().split()

    if len(text) < 2:
        return

    if text[0] == "masuk":
        nominal = parse_nominal(text[1])
        ket = " ".join(text[2:])
        tanggal = datetime.now().strftime("%d-%m-%Y")

        sheet.append_row([tanggal, "Masuk", nominal, ket])
        await update.message.reply_text("✅ Pemasukan tersimpan")

    elif text[0] == "keluar":
        nominal = parse_nominal(text[1])
        ket = " ".join(text[2:])
        tanggal = datetime.now().strftime("%d-%m-%Y")

        sheet.append_row([tanggal, "Keluar", nominal, ket])
        await update.message.reply_text("✅ Pengeluaran tersimpan")


# ===== TOKEN
TOKEN = os.getenv("TELEGRAM_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("masuk", masuk))
app.add_handler(CommandHandler("keluar", keluar))
app.add_handler(CommandHandler("saldo", saldo))
app.add_handler(CommandHandler("laporan", laporan))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
