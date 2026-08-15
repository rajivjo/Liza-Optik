import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import extra_streamlit_components as stx
from datetime import datetime, timedelta

from core.auth import admin_exists, create_admin, login, tambah_user, semua_users, padam_user
from core.calculator import (transposition, sphere_equivalent, bvd_compensation,
                              near_power, near_pd, add_estimator, prism_prentice)
from core.validator import validate_prescription
from core.ai_engine import analyze_prescription, detect_vision_type
from data.patient_db import (init_db, tambah_customer, cari_customer,
                              semua_customer, simpan_prescription,
                              kemaskini_status, history_customer, order_aktif)
from output.wa_template import wa_siap, wa_reminder, wa_order_diterima
from output.edger_job import generate_work_order

# ─── Init ───────────────────────────────────────
init_db()
st.set_page_config(
    page_title="Session Optical Giant",
    page_icon="👓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Cookie Manager ─────────────────────────────
@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()

cookie_manager = get_cookie_manager()

# ─── CSS ────────────────────────────────────────
st.markdown("""
<style>
* { box-sizing: border-box; }
.stApp { background-color: #0d1117; }
#MainMenu, footer, header { visibility: hidden; }

.main-header {
    background: linear-gradient(135deg, #10203F 0%, #1a2f5a 100%);
    border: 1px solid #B08D43;
    color: #e6edf3;
    padding: 1rem 1.2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    text-align: center;
}
.main-header h2 { font-size: 1.3rem; margin: 0 0 0.2rem 0; color: #B08D43; }
.main-header p  { font-size: 0.82rem; margin: 0; opacity: 0.75; }

.result-box {
    background: #161b22; border: 1px solid #B08D43;
    border-left: 3px solid #B08D43; border-radius: 10px;
    padding: 0.85rem; margin: 0.4rem 0;
    font-size: 0.9rem; line-height: 1.6; color: #e6edf3;
}
.warning-box {
    background: #1c1a0a; border: 1px solid #d4a017;
    border-left: 3px solid #d4a017; border-radius: 10px;
    padding: 0.85rem; margin: 0.4rem 0;
    font-size: 0.9rem; color: #f0d060;
}
.danger-box {
    background: #1a0a0a; border: 1px solid #ef5350;
    border-left: 3px solid #ef5350; border-radius: 10px;
    padding: 0.85rem; margin: 0.4rem 0;
    font-size: 0.9rem; color: #ff8a80;
}
.success-box {
    background: #0a1a0e; border: 1px solid #2ea043;
    border-left: 3px solid #2ea043; border-radius: 10px;
    padding: 0.85rem; margin: 0.4rem 0;
    font-size: 0.9rem; color: #56d364;
}
.stButton > button {
    border-radius: 8px; font-weight: 500;
    background-color: #10203F;
    border: 1px solid #B08D43; color: #B08D43;
}
.stButton > button:hover {
    background-color: #B08D43; color: #10203F; border-color: #B08D43;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    border-radius: 8px; font-size: 1rem;
    background-color: #161b22; border-color: #30363d; color: #e6edf3;
}
.stTabs [data-baseweb="tab"] { font-size: 0.85rem; padding: 0.4rem 0.7rem; }
.stTabs [aria-selected="true"] { color: #B08D43 !important; border-bottom-color: #B08D43 !important; }
section[data-testid="stSidebar"] {
    background: #10203F !important;
    min-width: 220px !important; max-width: 260px !important;
    border-right: 1px solid #B08D43;
}
section[data-testid="stSidebar"] * { color: #e6edf3 !important; }
hr { border-color: #30363d !important; }

/* Mobile */
.bottom-nav { display: none; }
@media (max-width: 768px) {
    .main-header h2 { font-size: 1.1rem; }
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="column"] { min-width: 100% !important; flex: 100% !important; }
    .stButton > button { min-height: 48px; font-size: 1rem; width: 100%; }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input { font-size: 16px !important; min-height: 44px; }
    pre { font-size: 0.78rem !important; }
    .bottom-nav {
        display: flex !important;
        position: fixed; bottom: 0; left: 0; right: 0;
        background: #10203F;
        border-top: 2px solid #B08D43;
        justify-content: space-around;
        align-items: center;
        padding: 0.4rem 0 0.8rem 0;
        z-index: 9999;
    }
    .bnav-btn {
        color: #B08D43; font-size: 0.6rem;
        text-align: center; display: flex;
        flex-direction: column; align-items: center;
        gap: 1px; background: none; border: none;
        cursor: pointer; padding: 0.3rem 0.5rem;
    }
    .bnav-btn .icon { font-size: 1.3rem; display: block; }
    .bnav-btn.active { color: #ffffff; }
    .main .block-container { padding-bottom: 90px !important; }
}
@media (max-width: 900px) {
    .main-header h2 { font-size: 1.2rem; }
}
.stCode { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── Cookie Auth Helper ──────────────────────────
def get_cookie(key):
    try:
        return cookie_manager.get(key)
    except:
        return None

def set_cookie(key, value, days=30):
    try:
        expires = datetime.now() + timedelta(days=days)
        cookie_manager.set(key, value, expires_at=expires)
    except:
        pass

def delete_cookie(key):
    try:
        cookie_manager.delete(key)
    except:
        pass

# ─── Restore session dari cookies ───────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'menu' not in st.session_state:
    st.session_state.menu = '🏠 Dashboard'

# Cuba restore dari cookie
if not st.session_state.logged_in:
    cookie_user = get_cookie('optik_user')
    cookie_role = get_cookie('optik_role')
    cookie_nama = get_cookie('optik_nama')
    if cookie_user and cookie_role and cookie_nama:
        st.session_state.logged_in = True
        st.session_state.user = {
            'username': cookie_user,
            'role': cookie_role,
            'nama_penuh': cookie_nama
        }

# ════════════════════════════════════════════════
# SETUP ADMIN (First Run)
# ════════════════════════════════════════════════
if not admin_exists():
    st.markdown("""
    <div class="main-header">
        <h2>👓 Session Optical Giant Bukit Tinggi</h2>
        <p>Sistem Pengurusan Optik</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("🔧 **Persediaan Pertama** — Cipta akaun Admin.")
    with st.form("setup_form"):
        st.subheader("⚙️ Setup Admin")
        nama_penuh = st.text_input("Nama Penuh", placeholder="Liza Binti Ahmad")
        username   = st.text_input("Username",   placeholder="liza")
        password   = st.text_input("Password",   type="password")
        password2  = st.text_input("Ulang Password", type="password")
        if st.form_submit_button("✅ Cipta Akaun Admin", use_container_width=True):
            if not nama_penuh or not username or not password:
                st.error("Sila isi semua medan.")
            elif password != password2:
                st.error("Password tidak sepadan.")
            elif len(password) < 6:
                st.error("Password mesti sekurang-kurangnya 6 aksara.")
            else:
                create_admin(username, password, nama_penuh)
                st.success("✅ Akaun admin berjaya dicipta! Sila log masuk.")
                st.rerun()
    st.stop()

# ════════════════════════════════════════════════
# LOGIN
# ════════════════════════════════════════════════
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        st.markdown("""
        <div class="main-header">
            <h2>👓 Session Optical Giant</h2>
            <p>Bukit Tinggi — Sistem Pengurusan Optik</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            st.subheader("🔐 Log Masuk")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            ingat    = st.checkbox("Ingat saya", value=True)
            if st.form_submit_button("Log Masuk", use_container_width=True):
                ok, user_data = login(username, password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    if ingat:
                        set_cookie('optik_user', user_data['username'], days=30)
                        set_cookie('optik_role', user_data['role'],     days=30)
                        set_cookie('optik_nama', user_data['nama_penuh'], days=30)
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah.")
    st.stop()

# ════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════
user = st.session_state.user

# ── Sidebar ──────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👓 Session Optical")
    st.markdown(f"**{user['nama_penuh']}**")
    st.caption(f"Role: {user['role'].upper()}")
    st.divider()
    menu = st.radio("", [
        "🏠 Dashboard",
        "🔬 Analisis RX",
        "🧮 Kalkulator",
        "👥 Customer",
        "📋 Order Aktif",
        "📱 WhatsApp",
        "⚙️ Tetapan"
    ], key="menu", label_visibility="collapsed")
    st.divider()
    if st.button("🚪 Log Keluar", use_container_width=True):
        delete_cookie('optik_user')
        delete_cookie('optik_role')
        delete_cookie('optik_nama')
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# ── Mobile bottom nav (guna st.session_state.menu) ─
menu_icons = {
    "🏠 Dashboard":  ("🏠", "Dashboard"),
    "🔬 Analisis RX":("🔬", "Analisis"),
    "🧮 Kalkulator": ("🧮", "Kalkulator"),
    "👥 Customer":   ("👥", "Customer"),
    "📋 Order Aktif":("📋", "Order"),
    "📱 WhatsApp":   ("📱", "WA"),
    "⚙️ Tetapan":   ("⚙️", "Tetapan"),
}
current = st.session_state.menu

# Bottom nav — 5 item utama
nav_items = [
    "🏠 Dashboard", "🔬 Analisis RX",
    "🧮 Kalkulator", "👥 Customer", "📱 WhatsApp"
]

nav_cols = st.columns(len(nav_items))
# Inject bottom nav via HTML + JS (guna st.session_state untuk navigate)
bottom_nav_html = '<div class="bottom-nav">'
for key in nav_items:
    icon, label = menu_icons[key]
    active_cls = "active" if current == key else ""
    bottom_nav_html += f'''
    <form action="" method="get" style="display:inline">
    <button class="bnav-btn {active_cls}" type="submit"
        onclick="window.parent.postMessage({{type:'streamlit:setComponentValue', value:'{key}'}}, '*'); return false;">
        <span class="icon">{icon}</span>{label}
    </button>
    </form>'''
bottom_nav_html += '</div>'

# Gunakan button biasa tapi hidden untuk mobile nav
# Cara terbaik: render button invisible, trigger via JS
st.markdown(f"""
<div class="main-header">
    <h2>👓 Session Optical Giant Bukit Tinggi</h2>
    <p>AI Optician Assistant</p>
</div>
""", unsafe_allow_html=True)

# Mobile nav buttons (real streamlit buttons, styled as bottom nav)
with st.container():
    st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)
    b_cols = st.columns(5)
    nav_map = {
        0: "🏠 Dashboard",
        1: "🔬 Analisis RX",
        2: "🧮 Kalkulator",
        3: "👥 Customer",
        4: "📱 WhatsApp"
    }
    for i, col in enumerate(b_cols):
        key = nav_map[i]
        icon, label = menu_icons[key]
        with col:
            if st.button(f"{icon}\n{label}", key=f"bnav_{i}",
                         use_container_width=True):
                st.session_state.menu = key
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Sync menu dari sidebar
menu = st.session_state.get('menu', '🏠 Dashboard')

# ════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════
if menu == "🏠 Dashboard":
    customers = semua_customer()
    orders    = order_aktif()
    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Customer",    len(customers))
    c2.metric("📋 Order Aktif", len(orders))
    c3.metric("📅 Tarikh",      datetime.now().strftime("%d %b %Y"))
    st.divider()
    st.subheader("📋 Order Dalam Proses")
    if orders:
        for o in orders[:10]:
            with st.expander(f"🔵 {o[16]} — {o[17]}"):
                st.write(f"**Tarikh:** {o[2]}")
                st.write(f"**RX Kanan:** {o[3]:+.2f}/{o[4]:+.2f}×{o[5]}")
                st.write(f"**RX Kiri:**  {o[6]:+.2f}/{o[7]:+.2f}×{o[8]}")
                st.write(f"**Lens:** {o[11]} | **Status:** {o[13]}")
    else:
        st.info("🎉 Tiada order aktif.")

# ════════════════════════════════════════════════
# ANALISIS RX
# ════════════════════════════════════════════════
elif menu == "🔬 Analisis RX":
    st.subheader("🔬 Analisis Prescription")
    with st.form("rx_form"):
        st.markdown("##### 👁️ Mata Kanan (OD)")
        c1, c2, c3 = st.columns(3)
        sph_r  = c1.number_input("SPH",  min_value=-20.0, max_value=20.0, step=0.25, value=0.0, format="%.2f", key="sph_r")
        cyl_r  = c2.number_input("CYL",  min_value=-10.0, max_value=10.0, step=0.25, value=0.0, format="%.2f", key="cyl_r")
        axis_r = c3.number_input("AXIS", min_value=0,     max_value=180,  step=1,    value=0,              key="axis_r")

        st.markdown("##### 👁️ Mata Kiri (OS)")
        c4, c5, c6 = st.columns(3)
        sph_l  = c4.number_input("SPH",  min_value=-20.0, max_value=20.0, step=0.25, value=0.0, format="%.2f", key="sph_l")
        cyl_l  = c5.number_input("CYL",  min_value=-10.0, max_value=10.0, step=0.25, value=0.0, format="%.2f", key="cyl_l")
        axis_l = c6.number_input("AXIS", min_value=0,     max_value=180,  step=1,    value=0,              key="axis_l")

        st.markdown("##### 📐 Maklumat Tambahan")
        c7, c8, c9 = st.columns(3)
        add  = c7.number_input("ADD",     min_value=0.0, max_value=4.0,  step=0.25, value=0.0, format="%.2f")
        pd   = c8.number_input("PD (mm)", min_value=50.0,max_value=80.0, step=0.5,  value=64.0,format="%.1f")
        age  = c9.number_input("Umur",    min_value=5,   max_value=100,  step=1,    value=35)
        lifestyle = st.text_input("Gaya Hidup / Simptom",
                                  placeholder="komputer, outdoor, memandu, penglihatan berganda...")
        submit = st.form_submit_button("🔍 Analisis", use_container_width=True)

    if submit:
        errors = validate_prescription(sph_r, cyl_r, axis_r, add, pd) + \
                 validate_prescription(sph_l, cyl_l, axis_l, add, pd)
        if errors:
            for e in errors: st.error(f"❌ {e}")
        else:
            st.success("✅ Prescription sah")
            col_r, col_l = st.columns(2)
            with col_r:
                se_r = sphere_equivalent(sph_r, cyl_r)
                ts_r, tc_r, ta_r = transposition(sph_r, cyl_r, axis_r)
                st.markdown(f"""<div class="result-box">
                <b>👁️ Kanan</b><br>SE: <b>{se_r:+.2f}D</b><br>
                Trans: <b>{ts_r:+.2f}/{tc_r:+.2f}×{ta_r}°</b><br>
                BVD: <b>{bvd_compensation(se_r):+.2f}D</b>
                </div>""", unsafe_allow_html=True)
            with col_l:
                se_l = sphere_equivalent(sph_l, cyl_l)
                ts_l, tc_l, ta_l = transposition(sph_l, cyl_l, axis_l)
                st.markdown(f"""<div class="result-box">
                <b>👁️ Kiri</b><br>SE: <b>{se_l:+.2f}D</b><br>
                Trans: <b>{ts_l:+.2f}/{tc_l:+.2f}×{ta_l}°</b><br>
                BVD: <b>{bvd_compensation(se_l):+.2f}D</b>
                </div>""", unsafe_allow_html=True)
            if add > 0:
                st.markdown(f"""<div class="result-box">
                <b>📖 Power Baca:</b> R {near_power(sph_r,add):+.2f}D | L {near_power(sph_l,add):+.2f}D &nbsp;|&nbsp;
                <b>Near PD:</b> {near_pd(pd):.1f}mm</div>""", unsafe_allow_html=True)

            st.markdown("#### 🤖 AI Recommendation")
            vtype, vrec = detect_vision_type(add if add > 0 else None, age)
            st.info(f"**{vtype}** — {vrec}")
            recs, warnings, _ = analyze_prescription(
                sph_r, cyl_r, sph_l, cyl_l, add if add > 0 else None, age, lifestyle)
            for r in recs:
                st.markdown(f'<div class="result-box">{r}</div>', unsafe_allow_html=True)
            for w in warnings:
                box = "danger-box" if "🚨" in w else "warning-box"
                st.markdown(f'<div class="{box}">{w}</div>', unsafe_allow_html=True)

            st.markdown("#### 🔧 Work Order — Nidek LE-9000")
            rx_data = {'sph_r':sph_r,'cyl_r':cyl_r,'axis_r':axis_r,
                       'sph_l':sph_l,'cyl_l':cyl_l,'axis_l':axis_l,
                       'add':add,'pd':pd,'jenis_lens':vrec,'coating':'-'}
            st.code(generate_work_order("—", rx_data), language=None)

# ════════════════════════════════════════════════
# KALKULATOR
# ════════════════════════════════════════════════
elif menu == "🧮 Kalkulator":
    st.subheader("🧮 Kalkulator Optik")
    tab1,tab2,tab3,tab4,tab5 = st.tabs(["Transposition","Sph Eq","BVD","ADD","Prism"])
    with tab1:
        c1,c2,c3 = st.columns(3)
        ts=c1.number_input("SPH",step=0.25,value=0.0,format="%.2f",key="t1")
        tc=c2.number_input("CYL",step=0.25,value=0.0,format="%.2f",key="t2")
        ta=c3.number_input("AXIS",min_value=0,max_value=180,step=1,value=90,key="t3")
        if st.button("Kira",use_container_width=True,key="bt"):
            ns,nc,na=transposition(ts,tc,ta)
            st.markdown(f'<div class="success-box">Hasil: <b>{ns:+.2f}/{nc:+.2f}×{na}°</b></div>',unsafe_allow_html=True)
    with tab2:
        c1,c2=st.columns(2)
        ss=c1.number_input("SPH",step=0.25,value=0.0,format="%.2f",key="s1")
        sc=c2.number_input("CYL",step=0.25,value=0.0,format="%.2f",key="s2")
        if st.button("Kira",use_container_width=True,key="bs"):
            st.markdown(f'<div class="success-box">SE: <b>{sphere_equivalent(ss,sc):+.2f}D</b></div>',unsafe_allow_html=True)
    with tab3:
        c1,c2=st.columns(2)
        bp=c1.number_input("Power (D)",step=0.25,value=0.0,format="%.2f",key="b1")
        bd=c2.number_input("BVD (mm)",step=0.5,value=12.0,format="%.1f",key="b2")
        if st.button("Kira",use_container_width=True,key="bb"):
            st.markdown(f'<div class="success-box">BVD Adj: <b>{bvd_compensation(bp,bd):+.2f}D</b></div>',unsafe_allow_html=True)
    with tab4:
        ea=st.slider("Umur",35,80,45)
        st.markdown(f'<div class="result-box">Umur <b>{ea}</b> — ADD: <b>+{add_estimator(ea):.2f}D</b></div>',unsafe_allow_html=True)
    with tab5:
        c1,c2=st.columns(2)
        pp=c1.number_input("Power (D)",step=0.25,value=2.0,format="%.2f",key="p1")
        pd2=c2.number_input("Decentration (mm)",step=0.5,value=5.0,format="%.1f",key="p2")
        if st.button("Kira",use_container_width=True,key="bp"):
            st.markdown(f'<div class="success-box">Prism: <b>{prism_prentice(pp,pd2):.2f}Δ</b></div>',unsafe_allow_html=True)

# ════════════════════════════════════════════════
# CUSTOMER
# ════════════════════════════════════════════════
elif menu == "👥 Customer":
    st.subheader("👥 Rekod Customer")
    tab1,tab2=st.tabs(["➕ Daftar Baru","🔍 Cari"])
    with tab1:
        with st.form("fc"):
            nama=st.text_input("Nama Penuh *")
            telefon=st.text_input("No. Telefon *",placeholder="011-2345678")
            c1,c2=st.columns(2)
            umur=c1.number_input("Umur",1,120,30)
            catatan=c2.text_input("Catatan")
            if st.form_submit_button("💾 Simpan",use_container_width=True):
                if nama and telefon:
                    cid=tambah_customer(nama,telefon,umur,catatan)
                    st.success(f"✅ **{nama}** berjaya didaftarkan!")
                else:
                    st.error("Nama dan telefon wajib diisi.")
    with tab2:
        cari=st.text_input("🔍 Cari nama atau nombor...")
        if cari:
            results=cari_customer(nama=cari,telefon=cari)
            if results:
                for r in results:
                    with st.expander(f"👤 {r[1]} — {r[2]}"):
                        st.write(f"**Umur:** {r[3]} | **Daftar:** {r[4]}")
                        hist=history_customer(r[0])
                        if hist:
                            st.markdown("**History:**")
                            for h in hist:
                                st.caption(f"{h[2]} R:{h[3]:+.2f}/{h[4]:+.2f}×{h[5]} L:{h[6]:+.2f}/{h[7]:+.2f}×{h[8]} [{h[13]}]")
            else:
                st.info("Tiada rekod dijumpai.")
        else:
            all_c=semua_customer()
            st.caption(f"Jumlah: {len(all_c)} customer")
            for r in all_c[:30]:
                st.write(f"👤 **{r[1]}** — {r[2]}")

# ════════════════════════════════════════════════
# ORDER AKTIF
# ════════════════════════════════════════════════
elif menu == "📋 Order Aktif":
    st.subheader("📋 Order Aktif")
    orders=order_aktif()
    if not orders:
        st.success("🎉 Tiada order dalam proses!")
    else:
        for o in orders:
            with st.expander(f"🔵 {o[16]} ({o[17]})"):
                st.write(f"**Tarikh:** {o[2]}")
                st.write(f"**R:** {o[3]:+.2f}/{o[4]:+.2f}×{o[5]} | **L:** {o[6]:+.2f}/{o[7]:+.2f}×{o[8]}")
                st.write(f"**Lens:** {o[11]} | **Coating:** {o[12]}")
                ns=st.selectbox("Status",["Dalam Proses","Siap","Diambil"],key=f"s{o[0]}")
                if st.button("✅ Kemaskini",key=f"k{o[0]}",use_container_width=True):
                    ts=datetime.now().strftime("%Y-%m-%d") if ns=="Siap" else None
                    kemaskini_status(o[0],ns,ts)
                    st.success(f"Status: **{ns}**")
                    st.rerun()

# ════════════════════════════════════════════════
# WHATSAPP
# ════════════════════════════════════════════════
elif menu == "📱 WhatsApp":
    st.subheader("📱 WhatsApp Template")
    tab1,tab2,tab3=st.tabs(["✅ Spek Siap","🔔 Reminder","📋 Order Diterima"])
    configs=[(tab1,wa_siap,"siap",True),(tab2,wa_reminder,"remind",False),(tab3,wa_order_diterima,"order",False)]
    for tab,func,key,need_date in configs:
        with tab:
            nw=st.text_input("Nama Customer",key=f"n{key}")
            tw=st.text_input("No. Telefon",key=f"t{key}",placeholder="011-2345678")
            td=None
            if need_date:
                td=st.date_input("Tarikh Siap",key=f"d{key}")
            if st.button("Generate",key=f"g{key}",use_container_width=True):
                if nw and tw:
                    tel,mesej=func(nw,tw,td.strftime("%d %B %Y")) if need_date else func(nw,tw)
                    st.markdown("**📞 Nombor Telefon:**")
                    st.code(tel,language=None)
                    st.markdown("**💬 Mesej WhatsApp:**")
                    st.code(mesej,language=None)
                else:
                    st.error("Sila isi nama dan nombor.")

# ════════════════════════════════════════════════
# TETAPAN
# ════════════════════════════════════════════════
elif menu == "⚙️ Tetapan":
    st.subheader("⚙️ Tetapan")
    if user['role']=='admin':
        tab1,tab2=st.tabs(["👤 Pengguna","ℹ️ Sistem"])
        with tab1:
            st.markdown("#### Tambah Pengguna")
            with st.form("fu"):
                un=st.text_input("Nama Penuh")
                c1,c2=st.columns(2)
                uu=c1.text_input("Username")
                ur=c2.selectbox("Role",["staff","admin"])
                up=st.text_input("Password",type="password")
                if st.form_submit_button("Tambah",use_container_width=True):
                    if un and uu and up:
                        ok,msg=tambah_user(uu,up,un,ur)
                        st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                    else:
                        st.error("Sila isi semua medan.")
            st.divider()
            for u2 in semua_users():
                c1,c2,c3=st.columns([4,2,1])
                c1.write(f"👤 **{u2['nama_penuh']}** @{u2['username']}")
                c2.caption(u2['role'].upper())
                if u2['username']!=user['username']:
                    if c3.button("🗑️",key=f"d{u2['username']}"):
                        padam_user(u2['username']); st.rerun()
        with tab2:
            st.markdown(f"""
            **Kedai:** Session Optical Giant Bukit Tinggi
            **Waktu:** Isnin–Sabtu 10pg–10mlm
            **Versi:** 1.0.0
            **Log masuk:** {user['nama_penuh']} ({user['role']})
            """)
    else:
        st.info(f"Log masuk sebagai: **{user['nama_penuh']}** ({user['role']})")
