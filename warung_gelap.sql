-- 1. Membuat Database Warung Gelap
CREATE DATABASE IF NOT EXISTS warung_gelap;
USE warung_gelap;

-- 2. Membuat Tabel Pesanan (Data Utama)
-- Tabel ini menyimpan siapa yang pesan, di meja mana, dan total bayarnya.
CREATE TABLE IF NOT EXISTS pesanan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_pelanggan VARCHAR(100) NOT NULL,
    no_meja INT NOT NULL,
    metode_bayar VARCHAR(50) NOT NULL,
    total_bayar INT NOT NULL,
    catatan TEXT,
    status ENUM('Antri', 'Dimasak', 'Selesai') DEFAULT 'Antri',
    waktu_pesan TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Membuat Tabel Detail Pesanan (Data Menu)
-- Tabel ini penting supaya pemilik resto tahu "item menu" apa saja yang dipesan.
-- Tabel ini terhubung ke tabel pesanan lewat kolom 'id_pesanan'.
CREATE TABLE IF NOT EXISTS detail_pesanan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_pesanan INT,
    nama_menu VARCHAR(100) NOT NULL,
    harga INT NOT NULL,
    FOREIGN KEY (id_pesanan) REFERENCES pesanan(id) ON DELETE CASCADE
);

-- 4. Opsional: Tambahkan data contoh untuk ngetes (Bisa dihapus nanti)
-- INSERT INTO pesanan (nama_pelanggan, no_meja, metode_bayar, total_bayar, catatan) 
-- VALUES ('Budi', 5, 'QRIS', 50000, 'Gak pake sambel');