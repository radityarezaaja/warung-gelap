from flask import Flask, render_template, request, jsonify, render_template_string
from flask_cors import CORS 
import pymysql # <-- Diubah agar lebih stabil dan menghindari error 2059
import os
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app) 

# --- KONFIGURASI DATABASE (FLEKSIBEL & AMAN DARI SENSOR GITHUB) ---
db_url = os.environ.get("DATABASE_URL")

if db_url:
    # JIKA BERJALAN DI SERVER CLOUD (VERCEL)
    url = urlparse(db_url)
    db_config = {
        "host": url.hostname,
        "user": url.username,
        "password": url.password,
        "database": url.path[1:], 
        "port": url.port or 3306,
        "ssl": {'ssl': {}}, # Wajib untuk cloud database Aiven
        "cursorclass": pymysql.cursors.DictCursor
    }
else:
    # JIKA BERJALAN DI LAPTOP (LOKAL)
    # Ubah password di bawah ini saat running lokal, lalu kembalikan menjadi "PASSWORD_DIAMANKAN" sebelum git push
    db_config = {
        "host": "mysql-f0fb579-warunggelap.a.aivencloud.com",
        "user": "avnadmin",
        "password": "PASSWORD_DIAMANKAN", 
        "database": "defaultdb",
        "port": 13745,
        "ssl": {'ssl': {}},
        "cursorclass": pymysql.cursors.DictCursor
    }

# Data Menu Lengkap dengan Gambar (Tetap seperti aslinya)
MENU = {
    "makanan": [
        ("Nasi Goreng Sedih", 15000, "https://cdn-brilio-net.akamaized.net/real/2024/02/09/2207401/kreasi-nasi-goreng-nyeleneh.jpg"),
        ("Mie Biasa Aja", 12000, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSch_fnjsbALrjQUZedkFb4wbOMidGpxNHWPg&s"),
        ("Ayam Kampus Geprek?", 18000, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT6-p30zYc5-Kz2u_V-4g2zJ0H6r6a6S-Y-2Q&s"),
        ("Sate Gratis", 22000, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSMVQcOpt1AMgh9jXSsajQfuKmZ73iaU5s8xA&s"),
        ("Bakso Sapi", 15000, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWEJzsDDkqvppHd9aRERdDsaEYUgcaIFxLvQ&s")
    ],
    "minuman": [
        ("ES TEH MANIS!", 5000, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6q9hUpKk7FgChm014QYy1sKdZKkZK5OUruQ&s"),
        ("Kopi Hitam", 7000, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQYFuobkc99W3vA1AYRa4jE2wVwfv1asXGktQ&s"),
        ("Susu Aja", 10000, "https://encrypted-tbn0.gstatic.com/images?q=tbn:GcS-v0M9N9X_7zX3G0P0q8zZ7n8W0-9-5-6-7-8&s"),
        ("Soda Gak Gembira", 12000, "https://i.pinimg.com/474x/d6/5d/78/d65d78d36414874347513455c3ef3d92.jpg"),
        ("Air Mineral", 4000, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQeqxYo4dh8O-j-NJSVLs-aHmOyqFc26JWtUA&s")
    ],
    "paket": [
        ("Nasi Goreng & Mineral", 18000, "https://bosara.sultraprov.go.id/asset/foto_produk/product-dapur-afifah--20240129011529600.jpg"),
        ("Sate & Susu", 30000, "https://bosara.sultraprov.go.id/asset/foto_produk/product-dapur-afifah--20240129011529600.jpg"),
        ("2 Sate, 2 Bakso, 1 Mie", 85000, "https://bosara.sultraprov.go.id/asset/foto_produk/product-dapur-afifah--20240129011529600.jpg")
    ]
}

# --- TEMPLATE HTML UNTUK ADMIN ---
ADMIN_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin - Warung Gelap</title>
    <style>
        body { 
            font-family: sans-serif; 
            background: #111; 
            color: #eee; 
            padding: 20px; 
        }

        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px; 
        }

        th, td { 
            border: 1px solid #333; 
            padding: 12px; 
            text-align: left; 
        }

        th { 
            background: #e67e22; 
            color: white; 
        }

        tr:nth-child(even) { 
            background: #1a1a1a; 
        }

        h1 {
            color: #e67e22;
        }

        .status {
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
        }

        .antri {
            background: orange;
            color: black;
        }

        .dimasak {
            background: dodgerblue;
            color: white;
        }

        .selesai {
            background: limegreen;
            color: white;
        }

        .btn-status {
            padding: 8px 14px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
        }

        .btn-masak {
            background: orange;
            color: black;
        }

        .btn-selesai {
            background: limegreen;
            color: white;
        }
    </style>
</head>
<body>

    <h1>Daftar Pesanan Masuk (Dapur)</h1>

    <table>
        <tr>
            <th>Waktu</th>
            <th>Meja</th>
            <th>Pelanggan</th>
            <th>Pesanan</th>
            <th>Jumlah Item</th>
            <th>Total</th>
            <th>Status</th>
            <th>Aksi</th>
            <th>Catatan</th>
        </tr>

        {% for o in orders %}
        <tr>
            <td>{{ o.waktu_pesan }}</td>
            <td>{{ o.no_meja }}</td>
            <td>{{ o.nama_pelanggan }}</td>

            <td>{{ o.daftar_menu | join(', ') }}</td>

            <td>{{ o.jumlah_item }}</td>

            <td>Rp {{ "{:,}".format(o.total_bayar) }}</td>

            <td>
                {% if o.status == 'Antri' %}
                    <span class="status antri">ANTRI</span>

                {% elif o.status == 'Dimasak' %}
                    <span class="status dimasak">DIMASAK</span>

                {% else %}
                    <span class="status selesai">SELESAI</span>
                {% endif %}
            </td>

            <td>
                {% if o.status == 'Antri' %}

                    <a href="/update_status/{{ o.id }}/Dimasak"
                       class="btn-status btn-masak">
                       MASAK
                    </a>

                {% elif o.status == 'Dimasak' %}

                    <a href="/update_status/{{ o.id }}/Selesai"
                       class="btn-status btn-selesai">
                       SIAP
                    </a>

                {% else %}

                    <span class="status selesai">
                         SUDAH DIAMBIL
                    </span>

                {% endif %}
            </td>

            <td>{{ o.catatan }}</td>
        </tr>
        {% endfor %}

    </table>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template('index.html', menu=MENU)

@app.route('/simpan_pesanan', methods=['POST'])
def simpan_pesanan():

    data = request.json

    # =========================
    # VALIDASI
    # =========================
    if not data.get('nama'):
        return jsonify({
            "status": "error",
            "message": "Nama pelanggan kosong"
        }), 400

    if not data.get('meja'):
        return jsonify({
            "status": "error",
            "message": "Nomor meja kosong"
        }), 400

    if len(data.get('items', [])) == 0:
        return jsonify({
            "status": "error",
            "message": "Pesanan kosong"
        }), 400

    # =========================
    # DEBUG TERMINAL
    # =========================
    print("\n===== DATA PESANAN MASUK =====")
    print(data)
    print("==============================\n")

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # =========================
        # INSERT PESANAN
        # =========================
        query_pesanan = """
            INSERT INTO pesanan 
            (nama_pelanggan, no_meja, metode_bayar, total_bayar, catatan) 
            VALUES (%s, %s, %s, %s, %s)
        """

        val_pesanan = (
            data['nama'],
            data['meja'],
            data['metode'],
            data['total'],
            data['catatan']
        )

        cursor.execute(query_pesanan, val_pesanan)

        # =========================
        # AMBIL ID PESANAN
        # =========================
        id_pesanan_baru = cursor.lastrowid

        print(f"ID Pesanan Baru: {id_pesanan_baru}")

        # =========================
        # INSERT DETAIL PESANAN
        # =========================
        query_detail = """
            INSERT INTO detail_pesanan 
            (id_pesanan, nama_menu, harga) 
            VALUES (%s, %s, %s)
        """

        for item in data['items']:

            print(f"Menambahkan item: {item['name']}")

            cursor.execute(
                query_detail,
                (
                    id_pesanan_baru,
                    item['name'],
                    item['price']
                )
            )

        conn.commit()

        print("Pesanan berhasil disimpan!")

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Pesanan berhasil masuk dapur!"
        }), 200

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =========================
# UPDATE STATUS PESANAN
# =========================
@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        query = """
            UPDATE pesanan
            SET status = %s
            WHERE id = %s
        """

        cursor.execute(query, (status, id))

        conn.commit()

        cursor.close()
        conn.close()

        return f'''
        <script>
            alert("Status berhasil diupdate menjadi: {status}");
            window.location.href="/admin";
        </script>
        '''

    except Exception as e:
        return f"Gagal update status: {str(e)}"


@app.route('/admin')
def admin():

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM pesanan 
            ORDER BY waktu_pesan DESC
        """)

        orders = cursor.fetchall()

        # =========================
        # AMBIL DETAIL MENU
        # =========================
        for order in orders:

            cursor.execute("""
                SELECT nama_menu 
                FROM detail_pesanan 
                WHERE id_pesanan = %s
            """, (order['id'],))

            menu_list = [row['nama_menu'] for row in cursor.fetchall()]

            # FIX ERROR ITEMS
            order['daftar_menu'] = menu_list

            # JUMLAH ITEM
            order['jumlah_item'] = len(menu_list)

        cursor.close()
        conn.close()

        return render_template_string(
            ADMIN_HTML_TEMPLATE,
            orders=orders
        )

    except Exception as e:
        return f"Gagal memuat database: {str(e)}"

if __name__ == '__main__':
    # Otomatis menyesuaikan port dinamis dari Render/Vercel
    port = int(os.environ.get("PORT", 5000))
    # debug di-set False saat naik server, di lokal tetap aman karena mengikuti environment
    app.run(host='0.0.0.0', port=port, debug=os.environ.get("FLASK_ENV") == "development")