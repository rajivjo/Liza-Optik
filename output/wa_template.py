from datetime import datetime

KEDAI = "Session Optical Giant Bukit Tinggi"
WAKTU = "Isnin - Sabtu: 10 pagi - 10 malam"

def wa_siap(nama, telefon, tarikh_siap=None):
    if not tarikh_siap:
        tarikh_siap = datetime.now().strftime("%d %B %Y")
    mesej = f"""✅ Cermin mata SIAP untuk diambil!

Nama   : {nama}
Tarikh : {tarikh_siap}

Sila datang pada waktu operasi:
{WAKTU}

Terima kasih kerana memilih {KEDAI}! 👓"""
    return telefon.strip(), mesej

def wa_reminder(nama, telefon):
    mesej = f"""👓 Peringatan dari {KEDAI}

Hai {nama}! Sudah lebih dari 2 tahun sejak pemeriksaan mata anda yang terakhir.

Masa untuk check mata sekali lagi! 😊

Hubungi kami atau singgah ke kedai pada waktu operasi:
{WAKTU}

Terima kasih! 🙏"""
    return telefon.strip(), mesej

def wa_order_diterima(nama, telefon):
    mesej = f"""📋 Pesanan Diterima!

Hai {nama}! Pesanan cermin mata anda telah kami terima.

Kami akan maklumkan apabila siap.

Waktu operasi: {WAKTU}

Terima kasih kerana memilih {KEDAI}! 👓"""
    return telefon.strip(), mesej
