import pymysql

# Sesuai dengan config Aiven lo
db_config = {
    "host": "mysql-f0fb579-warunggelap.a.aivencloud.com",
    "user": "avnadmin",
    "password": "AVNS_zBSkHwPh5HwgJipez9a", # <-- GANTI PAKE PASSWORD AIVEN LO!
    "database": "defaultdb",
    "port": 13745,
    "ssl": {'ssl': {}}
}

try:
    print("Menghubungkan ke Cloud Database Aiven...")
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 1. Bikin Tabel Pesanan
    print("Membuat tabel 'pesanan'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pesanan (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama_pelanggan VARCHAR(100) NOT NULL,
            no_meja VARCHAR(10) NOT NULL,
            metode_bayar VARCHAR(50) NOT NULL,
            total_bayar INT NOT NULL,
            status VARCHAR(20) DEFAULT 'Antri',
            catatan TEXT,
            waktu_pesan TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # 2. Bikin Tabel Detail Pesanan
    print("Membuat tabel 'detail_pesanan'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detail_pesanan (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_pesanan INT NOT NULL,
            nama_menu VARCHAR(100) NOT NULL,
            harga INT NOT NULL,
            FOREIGN KEY (id_pesanan) REFERENCES pesanan(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    conn.commit()
    print("\n🔥 BOOM! Semua tabel sukses dibuat di Cloud Aiven! 🔥")
    
    cursor.close()
    conn.close()

except Exception as e:
    print("\nGagal membuat tabel:", str(e))