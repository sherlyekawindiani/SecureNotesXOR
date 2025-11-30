# Secure Notes Manager (XOR + Base64)

**Penjelasan singkat:**  
Aplikasi GUI untuk menyimpan catatan (CRUD). Isi catatan dienkripsi pakai operasi XOR lalu di-encode Base64 sebelum disimpan ke MySQL. Saat ditampilkan, aplikasi mendecode Base64 lalu mendekripsi XOR sehingga user melihat plaintext.

## Fitur
- **Create**: input catatan baru (terenkripsi)
- **Read**: menampilkan catatan dalam bentuk plaintext (hasil dekripsi)
- **Update**: edit catatan & simpan ulang terenkripsi
- **Delete**: hapus catatan dari database

## Isi project
- `app.py` — GUI + CRUD (CustomTkinter)
- `xor_crypto.py` — fungsi XOR encrypt/decrypt + Base64
- `dump_kripto_notes.sql` — dump database (struktur + data)
- `requirements.txt` — library yang diperlukan

## Cara install & run
1. (Opsional) Buat virtual env:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1

2. Install dependency:
   ```powershell
   pip install -r requirements.txt
   
3. Jalankan aplikasi:
   ```powershell
   python app.py
   

## Database
- Nama database: `kripto_notes`
- Tabel: `notes(id INT PK AI, title VARCHAR(255), content TEXT)`
- `content` menyimpan **ciphertext** (Base64 dari hasil XOR)

## Key
- KEY yang dipakai di `xor_crypto.py`: `xorkunci`



