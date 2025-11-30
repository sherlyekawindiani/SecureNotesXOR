import base64

KEY = "xorkunci"  # Key untuk XOR, wajib sama saat encrypt & decrypt

def xor_encrypt(text: str) -> str:
    # Enkripsi pakai XOR → hasilnya bytes acak → diubah ke Base64 biar terbaca di UI
    result_bytes = bytearray()
    for i in range(len(text)):
        xor_char = ord(text[i]) ^ ord(KEY[i % len(KEY)])  # XOR plaintext sama key
        result_bytes.append(xor_char)

    # Encode hasil XOR (bytes) ke Base64, lalu jadi string
    encoded_b64 = base64.b64encode(result_bytes).decode("utf-8")
    return encoded_b64


def xor_decrypt(cipher_b64: str) -> str:
    # Buka bungkus Base64 dapat bytes asli XOR XOR ulang sama key kembali ke plaintext
    cipher_bytes = base64.b64decode(cipher_b64)
    decrypted_text = ""
    for i in range(len(cipher_bytes)):
        plain_char = cipher_bytes[i] ^ ord(KEY[i % len(KEY)])  # XOR ulang buat balikin
        decrypted_text += chr(plain_char)

    return decrypted_text
