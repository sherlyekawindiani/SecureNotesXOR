import customtkinter as ctk
import mysql.connector
import base64
from tkinter import Listbox
from xor_crypto import xor_encrypt, xor_decrypt

# ============================================
# FUNGSI KONEKSI DATABASE
# ============================================
def get_connection():
    # Ini fungsi buat bikin koneksi Python MySQL.
    # host="localhost" = karena MySQL ada di laptop 
    # user="root" = user default admin MySQL
    # password="root123" = password MySQL 
    # database="kripto_notes" = nama database 
    # port=3306 = port default MySQL
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="kripto_notes",
        port=3306
    )

# ============================================
# Placeholder handling di textbox
# ============================================
def clear_placeholder(event):
    # Fungsi ini buat hapus teks placeholder otomatis saat textbox pertama kali diklik/focus.
    # event = trigger dari UI, gak kita pakai isinya  cuma buat jalanin fungsi
    if text_content.get("1.0", "end-1c") == "Tulis isi catatan di sini...":

        # Kalau textbox isinya MASIH placeholder bawaan hapus
        text_content.delete("1.0", "end")

def restore_placeholder(event):
    # Fungsi ini buat balikin placeholder kalau user keluar dari textbox dan ternyata kosong.
    # Biar UI tetap kasih clue harus ketik apa.
        if text_content.get("1.0", "end-1c").strip() == "":
            text_content.insert("1.0", "Tulis isi catatan di sini...")

# ============================================
# FUNGSI CREATE NOTE
# ============================================
def create_note():
    # Ambil input judul dan isi dari form UI
    judul = entry_title.get().strip()
    isi = text_content.get("1.0", "end-1c").strip()

    # Validasi input biar gak kosong
    if not judul or not isi or isi == "Tulis isi catatan di sini...":
        # Isi == placeholder juga kita anggap belum isi yang valid
        label_status.configure(text="Judul dan isi wajib diisi!", text_color="red")
        return

    # Encrypt isi pakai XOR → hasil bytes → dibungkus Base64
    enc = xor_encrypt(isi)

    # Simpan ke database
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes(title, content) VALUES (%s, %s)", (judul, enc))
    conn.commit()
    conn.close()

    # Refresh list di UI supaya data langsung muncul
    label_status.configure(text="CREATE berhasil ✅ (terenkripsi XOR Base64 & tersimpan)", text_color="green")
    read_notes()

    # Kosongkan form UI setelah create biar enak input note baru
    entry_title.delete(0, "end")
    text_content.delete("1.0", "end")

# ============================================
# FUNGSI READ NOTES
# ============================================
def read_notes():
    # Kosongin dulu listbox biar gak numpuk dobel
    list_notes.delete(0, "end")

    # Ambil semua data dari tabel notes di DB
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content FROM notes")
    semua_data = cur.fetchall()
    conn.close()

    # Looping hasil query buat dimasukin ke listbox
    for d in semua_data:
        enc = d[2]

        # Amankan padding Base64 kalau kepotong/hilang, biar gak error incorrect padding
        kurang = len(enc) % 4
        if kurang:
            enc += "=" * (4 - kurang)

        # Decrypt XOR, kalau error → jangan crash UI
        try:
            dec = xor_decrypt(enc)
        except:
            dec = "[gagal decrypt/decode]"  # tanda kalau datanya corrupt

        # Tampilin di listbox dalam format:
        # id | judul| isi plaintext
        # (di list cuma kita nampilin hasil decrypt biar manusia bisa baca)
        list_notes.insert("end", f"{d[0]} | {d[1]} → {dec}")

# ============================================
# LOAD NOTE KE FORM SAAT DIKLIK DARI LISTBOX
# ============================================
def load_selected_to_form(event):
    # Kalau gak ada yang kepilih  return
    if not list_notes.curselection():
        return

    # Ambil teks dari listbox yang dipilih
    pilih = list_notes.get(list_notes.curselection())
    bagian = pilih.split("|")
    idpilih = bagian[0].strip()

    note_id.set(idpilih)

    # Ambil judul dari list, masukkan ke entry
    judul_list = bagian[1].split("→")[0].strip()
    entry_title.delete(0, "end")
    entry_title.insert(0, judul_list)

    # Ambil ciphertext asli dari DB, decrypt, masukkan ke textbox form
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT content FROM notes WHERE id=%s", (idpilih,))
    row = cur.fetchone()
    conn.close()

    if row:
        enc_db = row[0]
        kurang = len(enc_db) % 4
        if kurang:
            enc_db += "=" * (4 - kurang)

        dec = xor_decrypt(enc_db)
        text_content.delete("1.0", "end")
        text_content.insert("1.0", dec)

# ============================================
# FUNGSI UPDATE NOTE
# ============================================
def update_note():
    # Pastikan note_id sudah ada (artinya user udah klik note di list)
    if not note_id.get():
        label_status.configure(text="Pilih note dulu dari list!", text_color="red")
        return

    # Ambil input terbaru dari form UI
    judul_new = entry_title.get().strip()
    isi_new = text_content.get("1.0", "end-1c").strip()

    # Encrypt ulang isi pakai XOR→Base64
    enc_new = xor_encrypt(isi_new)

    # Update di DB
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notes SET title=%s, content=%s WHERE id=%s", (judul_new, enc_new, note_id.get()))
    conn.commit()
    conn.close()

    # Refresh list dan kosongkan form UI biar UX sama kayak Create
    label_status.configure(text="UPDATE berhasil ✅", text_color="green")
    read_notes()
    note_id.set("")
    entry_title.delete(0, "end")
    text_content.delete("1.0", "end")

# ============================================
# FUNGSI DELETE NOTE
# ============================================
def delete_note():
    if not note_id.get():
        label_status.configure(text="Pilih note dulu!", text_color="red")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id=%s", (note_id.get(),))
    conn.commit()
    conn.close()

    label_status.configure(text="DELETE berhasil ✅", text_color="green")
    read_notes()
    note_id.set("")
    entry_title.delete(0, "end")
    text_content.delete("1.0", "end")

# ============================================
# BAGIAN GUI / FRONTEND-nya
# ============================================
ctk.set_appearance_mode("dark")  # Set mode gelap biar tampil modern
ctk.set_default_color_theme("blue")  # Tema warna, bukan key enkripsi ya!
app = ctk.CTk()
app.title("Secure Notes Manager XOR")
app.geometry("520x420")

note_id = ctk.StringVar(value="")  # Variabel untuk simpan ID note yang dipilih user

# Input judul note, ada placeholder biar user tau ini kolom buat apa
entry_title = ctk.CTkEntry(app, placeholder_text="Masukkan Judul", width=400)
entry_title.pack(pady=5)

# Textbox isi note, default dikasih teks placeholder
text_content = ctk.CTkTextbox(app, width=400, height=120)
text_content.pack(pady=5)
text_content.insert("1.0", "Tulis isi catatan di sini...")  # Placeholder ghost text
text_content.bind("<FocusIn>", clear_placeholder)  # Hapus placeholder saat ngeklik
text_content.bind("<FocusOut>", restore_placeholder)  # Balik placeholder kalau kosong

# Frame tempat tombol CRUD biar rapi kegrid
frame_btn = ctk.CTkFrame(app)
frame_btn.pack(pady=5)

# Tombol CRUD
btn_create = ctk.CTkButton(frame_btn, text="Create", command=create_note, width=90)
btn_create.grid(row=0, column=0, padx=5)

btn_update = ctk.CTkButton(frame_btn, text="Update", command=update_note, width=90)
btn_update.grid(row=0, column=1, padx=5)

btn_delete = ctk.CTkButton(frame_btn, text="Delete", command=delete_note, width=90)
btn_delete.grid(row=0, column=2, padx=5)

# Listbox = tempat nampilin plaintext note yang udah didekripsi dari DB
list_notes = Listbox(app, width=50, height=8)
list_notes.pack(pady=10)
list_notes.bind("<<ListboxSelect>>", load_selected_to_form)  # Event ketika pilih note

# Label status = buat kasih notif ke user hasil CRUD atau error koneksi
label_status = ctk.CTkLabel(app, text="")
label_status.pack()

# Coba read DB di awal supaya listbox langsung terisi
try:
    read_notes()
except Exception as e:
    label_status.configure(text=f"Error koneksi DB: {e}", text_color="red")

app.mainloop()
