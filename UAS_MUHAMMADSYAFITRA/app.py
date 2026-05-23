import re
import time
import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime

# =========================================================================
# 1. KONSEP OOP (CLASS, ENKAPSULASI, PEWARISAN, POLIMORFISME)
# =========================================================================
class Orang:
    def __init__(self, nama):
        self._nama = nama  # Protected attribute

    def tampilkan_identitas(self):
        return f"Nama: {self._nama}"

class Mahasiswa(Orang):
    def __init__(self, nim, nama, prodi, ipk, status):
        super().__init__(nama)
        self.__nim = nim          # Private attribute
        self.__prodi = prodi      # Private attribute
        self.__ipk = float(ipk)   # Private attribute
        self.__status = status    # Private attribute

    @property
    def nim(self): return self.__nim
    @property
    def nama(self): return self._nama
    @property
    def prodi(self): return self.__prodi
    @property
    def ipk(self): return self.__ipk
    @property
    def status(self): return self.__status

    def to_dict(self):
        return {
            "nim": self.nim,
            "nama": self.nama,
            "prodi": self.prodi,
            "ipk": self.ipk,
            "status": self.status
        }

# =========================================================================
# 2. FILE I/O UTILITY & REPOSITORY (SQLITE DATABASE)
# =========================================================================
def init_db():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mahasiswa (
                nim TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                prodi TEXT NOT NULL,
                ipk REAL NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Gagal inisialisasi database: {e}")

def get_db_connection():
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error Database I/O: {e}")
        return None

def fetch_all_mahasiswa_objects():
    conn = get_db_connection()
    if not conn: return []
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mahasiswa")
    rows = cursor.fetchall()
    conn.close()
    
    daftar_mhs = []
    for row in rows:
        mhs = Mahasiswa(row['nim'], row['nama'], row['prodi'], row['ipk'], row['status'])
        daftar_mhs.append(mhs)
    return daftar_mhs

# =========================================================================
# 3. IMPLEMENTASI ALGORITMA SORTING & SEARCHING
# =========================================================================

# --- ALGORITMA SORTING ---
def bubble_sort_ipk(arr, urutan="desc"):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            kondisi = arr[j].ipk < arr[j+1].ipk if urutan == "desc" else arr[j].ipk > arr[j+1].ipk
            if kondisi:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def merge_sort_nim(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_nim(arr[:mid])
    right = merge_sort_nim(arr[mid:])
    
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i].nim < right[j].nim:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# --- ALGORITMA SEARCHING ---
def linear_search_nama(arr, keyword):
    hasil = []
    for mhs in arr:
        if keyword.lower() in mhs.nama.lower():
            hasil.append(mhs)
    return hasil

def binary_search_nim(arr, target_nim):
    arr_sorted = merge_sort_nim(arr)
    low = 0
    high = len(arr_sorted) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if arr_sorted[mid].nim == target_nim:
            return [arr_sorted[mid]]
        elif arr_sorted[mid].nim < target_nim:
            low = mid + 1
        else:
            high = mid - 1
    return []

# =========================================================================
# 4. FUNGSI UTAMA APLIKASI STREAMLIT
# =========================================================================

def show_login():
    """Halaman Login"""
    st.markdown("""
        <h1 style='text-align: center; color: #2c3e50;'>📚 SIMM UNPAM</h1>
        <h3 style='text-align: center; color: #555;'>Sistem Informasi Manajemen Mahasiswa</h3>
        <p style='text-align: center; color: #777;'>UAS - MUHAMMAD SYAFITRA</p>
        <hr>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Login Aplikasi")
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if username == "fitra" and password == "12345":
                st.session_state['user'] = username
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Username atau Password salah!")
        
        st.markdown("---")
        st.caption("💡 *Demo Login: username 'fitra', password '12345'*")

def show_dashboard():
    """Halaman Dashboard Utama"""
    st.markdown("""
        <h1 style='text-align: center; color: #2c3e50;'>📊 SIMM UNPAM</h1>
        <p style='text-align: center; color: #555;'>Sistem Informasi Manajemen Mahasiswa</p>
        <hr>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/graduation-cap.png", width=80)
        st.markdown(f"### 👋 Selamat Datang, **{st.session_state['user']}**!")
        st.markdown("---")
        
        menu = st.radio(
            "📌 **Menu Navigasi**",
            ["🏠 Dashboard", "📋 Data Mahasiswa", "➕ Tambah Data", "🔍 Cari Data", "📈 Statistik", "⚙️ Generate Data", "🚪 Logout"]
        )
        
        st.markdown("---")
        st.caption(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Routing Menu
    if menu == "🏠 Dashboard":
        show_dashboard_home()
    elif menu == "📋 Data Mahasiswa":
        show_data_mahasiswa()
    elif menu == "➕ Tambah Data":
        show_tambah_data()
    elif menu == "🔍 Cari Data":
        show_cari_data()
    elif menu == "📈 Statistik":
        show_statistik()
    elif menu == "⚙️ Generate Data":
        show_generate_data()
    elif menu == "🚪 Logout":
        st.session_state.clear()
        st.rerun()

def show_dashboard_home():
    """Halaman Home Dashboard"""
    st.markdown("## 🏠 Dashboard Overview")
    
    daftar_mhs = fetch_all_mahasiswa_objects()
    
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(daftar_mhs)
    aktif = sum(1 for mhs in daftar_mhs if mhs.status.lower() == "aktif")
    avg_ipk = sum(mhs.ipk for mhs in daftar_mhs) / total if total > 0 else 0
    max_ipk = max((mhs.ipk for mhs in daftar_mhs), default=0.0)
    
    with col1:
        st.metric("📊 Total Mahasiswa", total)
    with col2:
        st.metric("✅ Mahasiswa Aktif", aktif)
    with col3:
        st.metric("⭐ Rata-rata IPK", f"{avg_ipk:.2f}")
    with col4:
        st.metric("🏆 IPK Tertinggi", f"{max_ipk:.2f}")
    
    st.markdown("---")
    st.markdown("### 📌 Informasi Aplikasi")
    st.info("""
    **SIMM UNPAM** adalah aplikasi manajemen data mahasiswa yang dibangun dengan:
    - 🐍 Python & Streamlit
    - 🗄️ SQLite Database
    - 📊 Implementasi Algoritma Sorting & Searching
    - 🧬 Konsep OOP (Enkapsulasi, Pewarisan, Polimorfisme)
    """)
    
    if total > 0:
        st.markdown("### 📋 5 Data Terbaru")
        df = pd.DataFrame([mhs.to_dict() for mhs in daftar_mhs[:5]])
        st.dataframe(df, use_container_width=True, hide_index=True)

def show_data_mahasiswa():
    """Menampilkan data mahasiswa dengan fitur sorting"""
    st.markdown("## 📋 Data Mahasiswa")
    
    daftar_mhs = fetch_all_mahasiswa_objects()
    
    if not daftar_mhs:
        st.warning("⚠️ Belum ada data mahasiswa. Silakan tambah data atau generate data contoh!")
        return
    
    # Sorting options
    col1, col2 = st.columns([1, 2])
    with col1:
        sort_option = st.selectbox(
            "Urutkan berdasarkan:",
            ["Tanpa Urutan", "IPK Tertinggi", "IPK Terendah", "NIM A-Z"]
        )
    
    start_time = time.time()
    complexity_info = "O(1)"
    
    if sort_option == "IPK Tertinggi":
        daftar_mhs = bubble_sort_ipk(daftar_mhs.copy(), "desc")
        complexity_info = "O(n²) - Bubble Sort (Descending IPK)"
    elif sort_option == "IPK Terendah":
        daftar_mhs = bubble_sort_ipk(daftar_mhs.copy(), "asc")
        complexity_info = "O(n²) - Bubble Sort (Ascending IPK)"
    elif sort_option == "NIM A-Z":
        daftar_mhs = merge_sort_nim(daftar_mhs.copy())
        complexity_info = "O(n log n) - Merge Sort"
    
    execution_time = (time.time() - start_time) * 1000
    
    # Display data
    df = pd.DataFrame([mhs.to_dict() for mhs in daftar_mhs])
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Performance info
    with st.expander("⚡ Informasi Performa"):
        st.info(f"""
        - ⏱️ Waktu Eksekusi: `{execution_time:.4f} ms`
        - 📊 Kompleksitas: `{complexity_info}`
        - 📦 Jumlah Data: `{len(daftar_mhs)}`
        """)
    
    # Delete functionality
    st.markdown("### 🗑️ Hapus Data")
    col1, col2 = st.columns([2, 1])
    with col1:
        nim_to_delete = st.selectbox("Pilih NIM untuk dihapus:", [""] + [mhs.nim for mhs in daftar_mhs])
    with col2:
        if st.button("Hapus Data", type="secondary"):
            if nim_to_delete:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM mahasiswa WHERE nim = ?", (nim_to_delete,))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Data dengan NIM {nim_to_delete} berhasil dihapus!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal menghapus: {e}")
            else:
                st.warning("⚠️ Pilih NIM terlebih dahulu!")

def show_tambah_data():
    """Form untuk menambah data mahasiswa"""
    st.markdown("## ➕ Tambah Data Mahasiswa")
    
    with st.form("form_tambah_data", clear_on_submit=True):
        nim = st.text_input("NIM *", placeholder="Contoh: 2020114001 (10-12 digit angka)")
        nama = st.text_input("Nama Lengkap *", placeholder="Contoh: Muhammad Syafitra")
        prodi = st.selectbox("Program Studi *", ["Teknik Informatika", "Sistem Informasi", "Manajemen", "Akuntansi", "Teknik Komputer"])
        ipk = st.number_input("IPK *", min_value=0.0, max_value=4.0, step=0.01, format="%.2f")
        status = st.selectbox("Status", ["Aktif", "Cuti", "Pasif", "Lulus"])
        
        submitted = st.form_submit_button("💾 Simpan Data", type="primary", use_container_width=True)
        
        if submitted:
            # Validasi Regex
            errors = []
            if not re.match(r"^\d{10,12}$", nim):
                errors.append("NIM harus berupa angka 10-12 digit!")
            if not re.match(r"^[a-zA-Z\s\.]{3,50}$", nama):
                errors.append("Nama hanya boleh huruf dan spasi, minimal 3 karakter!")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO mahasiswa (nim, nama, prodi, ipk, status) VALUES (?, ?, ?, ?, ?)",
                        (nim, nama, prodi, float(ipk), status)
                    )
                    conn.commit()
                    conn.close()
                    st.success("✅ Data mahasiswa berhasil disimpan!")
                    st.balloons()
                except sqlite3.IntegrityError:
                    st.error("❌ NIM sudah terdaftar di sistem!")

def show_cari_data():
    """Fitur pencarian data mahasiswa"""
    st.markdown("## 🔍 Cari Data Mahasiswa")
    
    daftar_mhs = fetch_all_mahasiswa_objects()
    
    if not daftar_mhs:
        st.warning("⚠️ Belum ada data mahasiswa.")
        return
    
    search_type = st.radio("Tipe Pencarian:", ["Nama", "NIM"], horizontal=True)
    keyword = st.text_input("Masukkan kata kunci:", placeholder="Ketik di sini...")
    
    if keyword:
        start_time = time.time()
        
        if search_type == "Nama":
            hasil = linear_search_nama(daftar_mhs, keyword)
            complexity = "O(n) - Linear Search"
            st.info(f"🔍 Mencari nama mengandung: **{keyword}**")
        else:
            if re.match(r"^\d+$", keyword):
                hasil = binary_search_nim(daftar_mhs, keyword)
                complexity = "O(log n) - Binary Search"
                st.info(f"🔍 Mencari NIM: **{keyword}**")
            else:
                hasil = []
                st.warning("⚠️ NIM harus berupa angka!")
        
        execution_time = (time.time() - start_time) * 1000
        
        if hasil:
            st.success(f"✅ Ditemukan {len(hasil)} data")
            df = pd.DataFrame([mhs.to_dict() for mhs in hasil])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            with st.expander("⚡ Informasi Performa"):
                st.info(f"""
                - ⏱️ Waktu Pencarian: `{execution_time:.4f} ms`
                - 📊 Kompleksitas Algoritma: `{complexity}`
                - 🎯 Data Ditemukan: `{len(hasil)}`
                """)
        else:
            st.warning("😔 Data tidak ditemukan!")

def show_statistik():
    """Menampilkan statistik data"""
    st.markdown("## 📈 Statistik Mahasiswa")
    
    daftar_mhs = fetch_all_mahasiswa_objects()
    
    if not daftar_mhs:
        st.warning("⚠️ Belum ada data mahasiswa.")
        return
    
    # Konversi ke DataFrame
    df = pd.DataFrame([mhs.to_dict() for mhs in daftar_mhs])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Distribusi Program Studi")
        prodi_counts = df['prodi'].value_counts()
        st.bar_chart(prodi_counts)
        
    with col2:
        st.markdown("### 📊 Distribusi Status")
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts)
    
    st.markdown("---")
    st.markdown("### 📋 Ringkasan Statistik")
    
    stats = {
        "Total Mahasiswa": len(df),
        "Mahasiswa Aktif": len(df[df['status'] == 'Aktif']),
        "Rata-rata IPK": f"{df['ipk'].mean():.2f}",
        "Median IPK": f"{df['ipk'].median():.2f}",
        "IPK Tertinggi": f"{df['ipk'].max():.2f}",
        "IPK Terendah": f"{df['ipk'].min():.2f}",
        "Std Dev IPK": f"{df['ipk'].std():.2f}"
    }
    
    stats_df = pd.DataFrame([stats]).T
    stats_df.columns = ["Nilai"]
    st.dataframe(stats_df, use_container_width=True)
    
    # Histogram IPK
    st.markdown("### 📊 Distribusi IPK")
    st.bar_chart(df['ipk'].value_counts().sort_index())

def show_generate_data():
    """Generate data contoh"""
    st.markdown("## ⚙️ Generate Data Contoh")
    
    st.warning("⚠️ Fungsi ini akan menambahkan 5 data contoh ke database (tanpa menghapus data yang sudah ada)")
    
    sample_data = [
        ("2020114001", "Muhammad Fitra", "Teknik Informatika", 3.85, "Aktif"),
        ("2020114005", "Siti Aminah", "Sistem Informasi", 3.40, "Aktif"),
        ("2020114002", "Andi Wijaya", "Teknik Informatika", 2.90, "Cuti"),
        ("2020114012", "Riska Amelia", "Manajemen", 4.00, "Aktif"),
        ("2020114009", "Budi Santoso", "Akuntansi", 3.15, "Pasif")
    ]
    
    if st.button("🎲 Generate Data Contoh", type="primary"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            inserted = 0
            for data in sample_data:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO mahasiswa (nim, nama, prodi, ipk, status) VALUES (?, ?, ?, ?, ?)",
                        data
                    )
                    if cursor.rowcount > 0:
                        inserted += 1
                except:
                    pass
            conn.commit()
            conn.close()
            st.success(f"✅ Berhasil menambahkan {inserted} data baru!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Gagal generate data: {e}")

# =========================================================================
# 5. MAIN APP
# =========================================================================

def main():
    # Konfigurasi halaman
    st.set_page_config(
        page_title="SIMM UNPAM - Sistem Informasi Mahasiswa",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f7fb;
        }
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
        }
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Inisialisasi database
    init_db()
    
    # Cek status login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if st.session_state['logged_in']:
        show_dashboard()
    else:
        show_login()

if __name__ == '__main__':
    main()
