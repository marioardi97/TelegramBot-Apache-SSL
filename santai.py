import os
import subprocess
import random
import string
import nest_asyncio
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Aktifkan nest_asyncio
nest_asyncio.apply()

# Ganti dengan token bot Anda & ID Chat anda
BOT_TOKEN = '1111'
ALLOWED_CHAT_IDS = [111, 111]

# Fungsi untuk menghasilkan password kuat
def generate_strong_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation  # Tambahkan karakter khusus
    return ''.join(random.choice(characters) for _ in range(length))

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

    ftp_user = domain.replace('.', '_')
    ftp_password = generate_strong_password()  # Password FTP
    db_user = ftp_user
    db_password = generate_strong_password()    # Password Database

    try:
        # Buat konfigurasi Apache untuk domain
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

        # Tambahkan user FTP tanpa /sbin/nologin
        subprocess.run(['useradd', '-d', f"/var/www/{domain}", ftp_user], check=True)

        # Escape password untuk menghindari masalah sintaksis
        escaped_ftp_password = ftp_password.replace('$', '\\$').replace('`', '\\`').replace('"', '\\"')

        # Mengatur password pengguna FTP dengan aman
        subprocess.run(['bash', '-c', f'echo "{ftp_user}:{escaped_ftp_password}" | chpasswd'], check=True)

        # Set folder permissions untuk user FTP
        subprocess.run(['chown', '-R', f"{ftp_user}:{ftp_user}", f"/var/www/{domain}"], check=True)

        # Buat database dan user database dengan hak akses penuh
        subprocess.run(['mysql', '-u', 'root', '-e', f"CREATE USER '{db_user}'@'%' IDENTIFIED BY '{db_password}';"], check=True)  # Izinkan remote
        subprocess.run(['mysql', '-u', 'root', '-e', f"CREATE DATABASE {db_user};"], check=True)
        subprocess.run(['mysql', '-u', 'root', '-e', f"GRANT ALL PRIVILEGES ON {db_user}.* TO '{db_user}'@'%';"], check=True)  # Izinkan remote
        subprocess.run(['mysql', '-u', 'root', '-e', "FLUSH PRIVILEGES;"], check=True)

        # Kirim pesan dengan detail konfigurasi
        await update.message.reply_text(
            f"Konfigurasi untuk {domain} berhasil ditambahkan.\n\n"
            f"**Detail Konfigurasi:**\n\n"
            f"Domain: {domain}\n"
            f"Docroot: \var\www\{domain}\n"
            f"FTP User: {ftp_user}\n"
            f"FTP Password: {ftp_password}\n\n"
            f"Database User: {db_user}\n"
            f"Database Name: {db_user}\n"
            f"Database Password: {db_password}\n"
            f"Gunakan port 22 untuk SFTP dan port 21 untuk FTP.\n\n"
            f"Untuk mengakses database secara remote, gunakan:\n"
            f"Port 3306 dan IP server sebagai Hostnya\n"
            f"Jalankan /ssl {domain} 10-15 menit kedepan untuk menginstall SSL (menunggu domain terpropagasi)\n\n"
        )

    except Exception as e:
        await update.message.reply_text(f"Terjadi kesalahan: {str(e)}")

# Fungsi untuk menginstal SSL
async def install_ssl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return

    domain = ' '.join(context.args)
    if not domain:
        await update.message.reply_text("Format salah. Gunakan /ssl <domain>")
        return

    ssl_command_issue = f"/root/.acme.sh/acme.sh --issue -d {domain} --apache"
    ssl_command_install = f"/root/.acme.sh/acme.sh --install-cert -d {domain} " \
                          f"--key-file /etc/ssl/private/{domain}.key " \
                          f"--fullchain-file /etc/ssl/certs/{domain}.crt " \
                          f"--reloadcmd 'systemctl reload apache2'"

    try:
        # Mengeluarkan sertifikat SSL
        subprocess.run(ssl_command_issue, shell=True, check=True)
        # Menginstal sertifikat SSL
        subprocess.run(ssl_command_install, shell=True, check=True)

        await update.message.reply_text(f"SSL untuk {domain} telah berhasil diinstal.")
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
    loop = asyncio.get_event_loop()  # Gunakan loop yang sudah ada
    loop.run_until_complete(main())
