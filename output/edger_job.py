from datetime import datetime

def generate_work_order(customer_nama, rx_data, frame_data=None):
    tarikh = datetime.now().strftime("%d/%m/%Y %H:%M")
    wo = f"""
╔══════════════════════════════════════╗
║         WORK ORDER — NIDEK LE-9000       ║
╚══════════════════════════════════════╝

Tarikh  : {tarikh}
Customer: {customer_nama}

━━━━━━━━━━━━━━ PRESCRIPTION ━━━━━━━━━━━━━━

        SPH      CYL     AXIS    ADD
KANAN : {rx_data.get('sph_r', 0):+.2f}   {rx_data.get('cyl_r', 0):+.2f}   {rx_data.get('axis_r', 0):>3}°   {rx_data.get('add', 0) or 0:+.2f}
KIRI  : {rx_data.get('sph_l', 0):+.2f}   {rx_data.get('cyl_l', 0):+.2f}   {rx_data.get('axis_l', 0):>3}°   {rx_data.get('add', 0) or 0:+.2f}

PD    : {rx_data.get('pd', 0):.1f} mm

━━━━━━━━━━━━━━ SPESIFIKASI ━━━━━━━━━━━━━━

Jenis Lens : {rx_data.get('jenis_lens', '-')}
Coating    : {rx_data.get('coating', '-')}
Material   : {frame_data.get('material', '-') if frame_data else '-'}
Frame      : {frame_data.get('nama_frame', '-') if frame_data else '-'}
Warna      : {frame_data.get('warna', '-') if frame_data else '-'}

━━━━━━━━━━━━━━ CATATAN ━━━━━━━━━━━━━━

{rx_data.get('catatan', 'Tiada catatan')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Disediakan oleh: Session Optical Giant Bukit Tinggi
"""
    return wo
