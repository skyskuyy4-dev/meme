import re
import time
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "kunci_rahasia_simm_unpam_muhammadsyafitra"

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
        print(f"Gagal inisialisasi database: {e}")

def get_db_connection():
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error Database I/O: {e}")
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
# 4. API ENDPOINTS (PROSES AJAX & VALIDASI REGEX)
# =========================================================================

@app.route('/api/mahasiswa', methods=['GET'])
def api_get_mahasiswa():
    daftar_obj = fetch_all_mahasiswa_objects()
    
    search_type = request.args.get('search_type')
    keyword = request.args.get('keyword')
    sort_by = request.args.get('sort_by')
    
    start_time = time.time()
    complexity_info = "O(1)"
    
    if keyword:
        if search_type == "nim":
            daftar_obj = binary_search_nim(daftar_obj, keyword)
            complexity_info = "O(log n) [Binary Search]"
        else:
            daftar_obj = linear_search_nama(daftar_obj, keyword)
            complexity_info = "O(n) [Linear Search]"
            
    if sort_by == "ipk_desc":
        daftar_obj = bubble_sort_ipk(daftar_obj, "desc")
        complexity_info += " + O(n^2) [Bubble Sort]"
    elif sort_by == "ipk_asc":
        daftar_obj = bubble_sort_ipk(daftar_obj, "asc")
        complexity_info += " + O(n^2) [Bubble Sort]"
    elif sort_by == "nim_asc":
        daftar_obj = merge_sort_nim(daftar_obj)
        complexity_info += " + O(n log n) [Merge Sort]"

    execution_time = (time.time() - start_time) * 1000
    
    total = len(daftar_obj)
    aktif = sum(1 for mhs in daftar_obj if mhs.status.lower() == "aktif")
    avg_ipk = sum(mhs.ipk for mhs in daftar_obj) / total if total > 0 else 0
    max_ipk = max((mhs.ipk for mhs in daftar_obj), default=0.0)
    
    return jsonify({
        "data": [mhs.to_dict() for mhs in daftar_obj],
        "stats": {
            "total": total,
            "aktif": aktif,
            "avg_ipk": round(avg_ipk, 2),
            "max_ipk": round(max_ipk, 2)
        },
        "performance": {
            "time_ms": round(execution_time, 4),
            "complexity": complexity_info
        }
    })

@app.route('/api/mahasiswa/tambah', methods=['POST'])
def api_tambah_mahasiswa():
    try:
        data = request.json
        nim = data.get('nim', '').strip()
        nama = data.get('nama', '').strip()
        prodi = data.get('prodi', '').strip()
        ipk = data.get('ipk', '').strip()
        status = data.get('status', 'Aktif')

        # VALIDASI REGEX
        if not re.match(r"^\d{10,12}\$", nim):
            return jsonify({"status": "error", "message": "Regex Fail: NIM harus berupa angka 10-12 digit!"}), 400
        if not re.match(r"^[a-zA-Z\s\.]{3,50}\$", nama):
            return jsonify({"status": "error", "message": "Regex Fail: Nama hanya boleh huruf, minimal 3 karakter!"}), 400
        if not re.match(r"^(0(\.\d{1,2})?|[1-3](\.\d{1,2})?|4(\.0{1,2})?)\$", str(ipk)):
            return jsonify({"status": "error", "message": "Regex Fail: IPK harus angka desimal antara 0.00 - 4.00!"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mahasiswa (nim, nama, prodi, ipk, status) VALUES (?, ?, ?, ?, ?)",
                       (nim, nama, prodi, float(ipk), status))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Data berhasil disimpan!"})
        
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "NIM sudah terdaftar di sistem!"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Terjadi kesalahan sistem: {str(e)}"}), 500

@app.route('/api/mahasiswa/generate', methods=['POST'])
def api_generate_contoh():
    sample_data = [
        ("2010114001", "Muhammad Fitra", "Teknik Informatika", 3.85, "Aktif"),
        ("2010114005", "Siti Aminah", "Sistem Informasi", 3.40, "Aktif"),
        ("2010114002", "Andi Wijaya", "Teknik Informatika", 2.90, "Cuti"),
        ("2010114012", "Riska Amelia", "Manajemen", 4.00, "Aktif"),
        ("2010114009", "Budi Santoso", "Akuntansi", 3.15, "Pasif")
    ]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO mahasiswa (nim, nama, prodi, ipk, status) VALUES (?, ?, ?, ?, ?)", sample_data)
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "5 Data simulasi berhasil digenerate!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/mahasiswa/hapus/<nim>', methods=['DELETE'])
def api_hapus_mahasiswa(nim):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mahasiswa WHERE nim = ?", (nim,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Data mahasiswa berhasil dihapus!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# =========================================================================
# 5. INTERNAL ROUTING HALAMAN HTML
# =========================================================================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "fitra" and password == "12345":
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            error_msg = "Username atau Password salah!"
            
    return render_template('login.html', error=error_msg)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# =========================================================================
# 6. BLOK EKSEKUSI UTAMA (RUNNER & ERROR HANDLING GLOBAL)
# =========================================================================

if __name__ == '__main__':
    try:
        print("="*60)
        print(" SIMM UNPAM - APLIKASI DATA MAHASISWA BERBASIS PYTHON")
        print(" UAS - MUHAMMADSYAFITRA")
        print(" STATUS SERVER: AKTIF")
        print("="*60)
        
        init_db()
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as server_error:
        print(f" Gagal menyalakan server Flask: {str(server_error)}")
