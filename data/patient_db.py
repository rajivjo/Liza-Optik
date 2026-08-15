import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'optik.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            telefon TEXT NOT NULL,
            umur INTEGER,
            tarikh_daftar TEXT,
            catatan TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            tarikh TEXT,
            sph_r REAL, cyl_r REAL, axis_r INTEGER,
            sph_l REAL, cyl_l REAL, axis_l INTEGER,
            add_power REAL, pd REAL,
            jenis_lens TEXT,
            coating TEXT,
            status TEXT DEFAULT 'Dalam Proses',
            tarikh_siap TEXT,
            catatan TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    conn.commit()
    conn.close()

def tambah_customer(nama, telefon, umur=None, catatan=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    tarikh = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('''
        INSERT INTO customers (nama, telefon, umur, tarikh_daftar, catatan)
        VALUES (?, ?, ?, ?, ?)
    ''', (nama, telefon, umur, tarikh, catatan))
    customer_id = c.lastrowid
    conn.commit()
    conn.close()
    return customer_id

def cari_customer(nama="", telefon=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM customers
        WHERE nama LIKE ? OR telefon LIKE ?
        ORDER BY tarikh_daftar DESC
    ''', (f'%{nama}%', f'%{telefon}%'))
    results = c.fetchall()
    conn.close()
    return results

def semua_customer():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM customers ORDER BY tarikh_daftar DESC')
    results = c.fetchall()
    conn.close()
    return results

def simpan_prescription(customer_id, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    tarikh = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('''
        INSERT INTO prescriptions
        (customer_id, tarikh, sph_r, cyl_r, axis_r, sph_l, cyl_l, axis_l,
         add_power, pd, jenis_lens, coating, status, catatan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        customer_id, tarikh,
        data.get('sph_r'), data.get('cyl_r'), data.get('axis_r'),
        data.get('sph_l'), data.get('cyl_l'), data.get('axis_l'),
        data.get('add'), data.get('pd'),
        data.get('jenis_lens'), data.get('coating'),
        'Dalam Proses', data.get('catatan')
    ))
    rx_id = c.lastrowid
    conn.commit()
    conn.close()
    return rx_id

def kemaskini_status(rx_id, status, tarikh_siap=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if tarikh_siap:
        c.execute('UPDATE prescriptions SET status=?, tarikh_siap=? WHERE id=?',
                  (status, tarikh_siap, rx_id))
    else:
        c.execute('UPDATE prescriptions SET status=? WHERE id=?', (status, rx_id))
    conn.commit()
    conn.close()

def history_customer(customer_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM prescriptions
        WHERE customer_id=?
        ORDER BY tarikh DESC
    ''', (customer_id,))
    results = c.fetchall()
    conn.close()
    return results

def order_aktif():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT p.*, c.nama, c.telefon
        FROM prescriptions p
        JOIN customers c ON p.customer_id = c.id
        WHERE p.status = 'Dalam Proses'
        ORDER BY p.tarikh DESC
    ''')
    results = c.fetchall()
    conn.close()
    return results
