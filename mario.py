import os 
import subprocess
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Aktifkan nest_asyncio
nest_asyncio.apply()

# Ganti dengan token bot Anda
BOT_TOKEN = '11111'  # Ganti dengan token bot Anda
ALLOWED_CHAT_IDS = [111, 11111] # Ganti dengan Daftar ID Tele Anda

# Cek apakah user yang mengirimkan pesan diizinkan
async def is_authorized(update: Update) -> bool:
    chat_id = update.effective_chat.id
    if chat_id not in ALLOWED_CHAT_IDS:
        await update.message.reply_text("Akses dilarang!")
        return False
    return True

# Fungsi untuk menyapa pengguna
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    await update.message.reply_text(f"Selamat datang, @{username}!")

# Fungsi untuk menambahkan konfigurasi
async def add_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return

    domain = ' '.join(context.args)
    if not domain:
        await update.message.reply_text("Format salah. Gunakan /addconfig <domain>")
        return

    config_path = f"/etc/apache2/sites-available/{domain}.conf"
    if os.path.exists(config_path):
        await update.message.reply_text("Domain sudah ada. Silakan gunakan domain yang berbeda.")
        return

    config_content = f"""
<VirtualHost *:80>
    ServerName {domain}
    DocumentRoot /var/www/{domain}
    ErrorLog /var/log/apache2/{domain}-error.log
    CustomLog /var/log/apache2/{domain}-access.log combined
</VirtualHost>
    """

    try:
        with open(config_path, 'w') as file:
            file.write(config_content)

        # Buat folder untuk domain
        os.makedirs(f"/var/www/{domain}", exist_ok=True)

        # Buat index.html
        index_content = f"<html><body><h1>Welcome to {domain}</h1></body></html>"
        with open(f"/var/www/{domain}/index.html", 'w') as index_file:
            index_file.write(index_content)

        # Aktifkan dan reload Apache
        subprocess.run(['a2ensite', f"{domain}.conf"], check=True)
        subprocess.run(['systemctl', 'reload', 'apache2'], check=True)

        await update.message.reply_text(f"Konfigurasi untuk {domain} berhasil ditambahkan. Jalankan perintah /ssl {domain} dalam 10-15 menit kedepan untuk menginstall SSL ")
    except Exception as e:
        await update.message.reply_text(f"Terjadi kesalahan: {str(e)}")

# Fungsi untuk menginstal SSL menggunakan acme.sh
async def install_ssl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return

    domain = ' '.join(context.args)
    if not domain:
        await update.message.reply_text("Format salah. Gunakan /ssl <domain>")
        return

    # Jalankan perintah untuk membuat SSL dengan acme.sh
    try:
        # Buat SSL menggunakan acme.sh
        command = f"/root/.acme.sh/acme.sh --issue -d {domain} --apache"
        subprocess.run(command, shell=True, check=True)

        # Instal sertifikat
        command = f"/root/.acme.sh/acme.sh --install-cert -d {domain} --key-file /etc/ssl/private/{domain}.key --fullchain-file /etc/ssl/certs/{domain}.crt --reloadcmd 'systemctl reload apache2'"
        subprocess.run(command, shell=True, check=True)

        await update.message.reply_text(f"SSL untuk {domain} berhasil diinstal.")
    except Exception as e:
        await update.message.reply_text(f"Terjadi kesalahan saat menginstal SSL: {str(e)}")

# Fungsi utama untuk menjalankan bot
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addconfig", add_config))
    application.add_handler(CommandHandler("ssl", install_ssl))

    await application.run_polling()

# Menjalankan bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
