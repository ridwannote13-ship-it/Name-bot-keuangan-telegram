from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ===== GOOGLE AUTH =====
google_json = os.getenv("GOOGLE_JSON")
creds_dict = json.loads(google_json)

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)


# ===== GET SHEET PER USER (MULTI USER)
def get_user_sheet(user_id):

    try:
        ws = client.open("Laporan Keuangan Bot").worksheet(str(user_id))
    except:
        ws = client.open("Laporan Keuangan Bot").add_worksheet(
            title=str(user_id), rows="1000", cols="10")
        ws.append_row(["Tanggal","Jenis","Nominal","Keterangan"])

    return ws


# ===== PARSE NOMINAL
def parse_nominal(n):
    return int(n.replace(".", "").replace(",", ""))


# ===== MASUK
async def masuk(update, context):
    try:
        nominal = parse_nominal(context.args[0])
        ket = " ".join(context.args[1:])
    except:
        await update.message.reply_text("Format salah.\n/masuk 10000 gaji")
        return

    sheet = get_user_sheet(update.effective_user.id)
    tanggal = datetime.now().strftime("%d-%m-%Y")

    sheet.append_row([tanggal,"Masuk",nominal,ket])

    await update.message.reply_text("✅ Pemasukan tersimpan")


# ===== KELUAR
async def keluar(update, context):
    try:
        nominal = parse_nominal(context.args[0])
        ket = " ".join(context.args[1:])
    except:
        await update.message.reply_text("Format salah.\n/keluar 5000 makan")
        return

    sheet = get_user_sheet(update.effective_user.id)
    tanggal = datetime.now().strftime("%d-%m-%Y")

    sheet.append_row([tanggal,"Keluar",nominal,ket])

    await update.message.reply_text("✅ Pengeluaran tersimpan")


# ===== SALDO
async def saldo(update, context):
    sheet = get_user_sheet(update.effective_user.id)
    data = sheet.get_all_records()

    df = pd.DataFrame(data)

    if len(df)==0:
        await update.message.reply_text("Belum ada data.")
        return

    df["Nominal"] = df["Nominal"].astype(int)

    masuk = df[df["Jenis"]=="Masuk"]["Nominal"].sum()
    keluar = df[df["Jenis"]=="Keluar"]["Nominal"].sum()

    saldo = masuk - keluar

    await update.message.reply_text(f"💰 Saldo: Rp {saldo}")


# ===== GRAFIK
async def grafik(update, context):
    sheet = get_user_sheet(update.effective_user.id)
    data = sheet.get_all_records()

    df = pd.DataFrame(data)

    if len(df)==0:
        await update.message.reply_text("Belum ada data.")
        return

    df["Nominal"] = df["Nominal"].astype(int)

    masuk = df[df["Jenis"]=="Masuk"]["Nominal"].sum()
    keluar = df[df["Jenis"]=="Keluar"]["Nominal"].sum()

    plt.figure()
    plt.pie([masuk,keluar], labels=["Masuk","Keluar"], autopct='%1.1f%%')
    plt.title("Perbandingan Keuangan")

    plt.savefig("/tmp/grafik.png")
    plt.close()

    await update.message.reply_photo(photo=open("/tmp/grafik.png","rb"))


# ===== PDF
async def pdf(update, context):
    sheet = get_user_sheet(update.effective_user.id)
    data = sheet.get_all_values()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    for row in data:
        pdf.cell(200,8,txt=" | ".join(row),ln=True)

    pdf.output("/tmp/laporan.pdf")

    await update.message.reply_document(
        document=open("/tmp/laporan.pdf","rb"))


# ===== DASHBOARD LINK
async def dashboard(update, context):
    user_id = update.effective_user.id
    link = f"https://financebot.streamlit.app/?user={user_id}"

    await update.message.reply_text(f"📊 Dashboard kamu:\n{link}")


# ===== TEXT HANDLER
async def text_handler(update, context):
    text = update.message.text.lower().split()

    if len(text)<2:
        return

    sheet = get_user_sheet(update.effective_user.id)

    if text[0]=="masuk":
        nominal = parse_nominal(text[1])
        ket = " ".join(text[2:])
        tanggal = datetime.now().strftime("%d-%m-%Y")

        sheet.append_row([tanggal,"Masuk",nominal,ket])
        await update.message.reply_text("✅ Pemasukan tersimpan")

    elif text[0]=="keluar":
        nominal = parse_nominal(text[1])
        ket = " ".join(text[2:])
        tanggal = datetime.now().strftime("%d-%m-%Y")

        sheet.append_row([tanggal,"Keluar",nominal,ket])
        await update.message.reply_text("✅ Pengeluaran tersimpan")


# ===== TOKEN
TOKEN = os.getenv("TELEGRAM_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("masuk", masuk))
app.add_handler(CommandHandler("keluar", keluar))
app.add_handler(CommandHandler("saldo", saldo))
app.add_handler(CommandHandler("grafik", grafik))
app.add_handler(CommandHandler("pdf", pdf))
app.add_handler(CommandHandler("dashboard", dashboard))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
