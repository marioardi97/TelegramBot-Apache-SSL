# Telegram Bot untuk Konfigurasi Apache, SSL, Database dan FTP

Bot ini untuk yang malas eh memudahkan menambahkan Config Domain dan Instalasi SSL xixixi

Bot ini memungkinkan pengguna untuk menambahkan konfigurasi Apache dan menginstal sertifikat SSL menggunakan `acme.sh`. Bot ini aman dari akses ilegal karena melakukan validasi pada `chat_ids` yang terdaftar.
kemudian secara otomatis membuatkan Database serta user ftp.



![pengenturu](https://github.com/user-attachments/assets/d8bbd7b7-3d25-45d3-b4fd-494c0abd34c8)



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
dan
/ssl <domain> untuk menginstal ssl


## License

[MIT](https://choosealicense.com/licenses/mit/)
