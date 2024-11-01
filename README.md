# Telegram Bot untuk Konfigurasi Apache dan SSL

Bot ini untuk yang malas eh memudahkan menambahkan Config Domain dan Instalasi SSL xixixi

Bot ini memungkinkan pengguna untuk menambahkan konfigurasi Apache dan menginstal sertifikat SSL menggunakan `acme.sh`. Bot ini aman dari akses ilegal karena melakukan validasi pada `chat_ids` yang terdaftar.



##Keamanan
Bot ini melakukan validasi pada chat_ids yang terdaftar, sehingga hanya pengguna yang terotorisasi yang dapat mengakses fitur bot. Pastikan untuk menambahkan chat_id Anda ke dalam daftar ALLOWED_CHAT_IDS dalam kode bot.

## Deployment

Ikuti Step berikut:


```bash
pip install python-telegram-bot nest_asyncio

```
```bash
curl https://get.acme.sh | sh

```
```bash
~/.acme.sh/acme.sh --register-account -m your_email@example.com


```

## Penggunaan
setelah instalasi selesai, update lah telegram bot token dan chat id pada scriptnya.

/addconfig <domain> untuk menambahkan domain baru
/ssl <domain> untuk menginstal ssl
