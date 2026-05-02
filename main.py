"""
=============================================================
  BÀI TẬP LỚN SỐ 3 - HIỆN THỰC HỆ MÃ RSA BẰNG PYTHON
=============================================================
  Yêu cầu:
  - Tìm số nguyên tố lớn (>= 500 bits)
  - Tính ước số chung lớn nhất (GCD)
  - Tính khóa giải mã d
  - Tạo bộ khóa ngẫu nhiên
  - Mã hóa thông điệp
  - Giải mã thông điệp
=============================================================
"""

import random
import time
import json
import os
from pathlib import Path
from datetime import datetime


# ============================================================
# 0. SETUP DIRECTORIES & JSON UTILITIES
# ============================================================

# Tạo thư mục lưu trữ nếu chưa tồn tại
KEYS_DIR = Path("keys")
CIPHERS_DIR = Path("ciphers")
CONFIG_FILE = Path("rsa_session.json")

KEYS_DIR.mkdir(exist_ok=True)
CIPHERS_DIR.mkdir(exist_ok=True)


def int_to_str(num):
    """Chuyển số nguyên lớn thành chuỗi hex để lưu JSON."""
    return hex(num)


def str_to_int(hex_str):
    """Chuyển chuỗi hex thành số nguyên."""
    return int(hex_str, 16)


def save_config(config_dict):
    """Lưu cấu hình session vào file JSON."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_dict, f, indent=2)


def load_config():
    """Tải cấu hình session từ file JSON."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def get_current_config():
    """Lấy cấu hình hiện tại hoặc khởi tạo mặc định."""
    config = load_config()
    if 'current_key_pair' not in config:
        config['current_key_pair'] = None
    if 'current_cipher' not in config:
        config['current_cipher'] = None
    return config


# ============================================================
# 1. MODULAR EXPONENTIATION (tự cài đặt - không dùng pow(x,e,n))
# ============================================================

def mod_pow(base, exp, mod):
    """
    Tính base^exp mod n bằng thuật toán Square-and-Multiply (Fast Exponentiation).
    Không dùng hàm pow() 3 tham số có sẵn của Python.
    """
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:          # nếu bit thấp nhất là 1
            result = (result * base) % mod
        exp = exp >> 1             # dịch phải 1 bit (chia 2)
        base = (base * base) % mod
    return result


# ============================================================
# 2. MILLER-RABIN PRIMALITY TEST (kiểm tra số nguyên tố)
# ============================================================

def miller_rabin_test(n, a):
    """
    Thực hiện một vòng kiểm tra Miller-Rabin với nhân chứng a.
    Trả về True nếu n có thể là số nguyên tố, False nếu chắc chắn là hợp số.
    """
    # Viết n-1 = 2^r * d, với d lẻ
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    x = mod_pow(a, d, n)  # x = a^d mod n

    if x == 1 or x == n - 1:
        return True  # Có thể là nguyên tố

    for _ in range(r - 1):
        x = mod_pow(x, 2, n)  # x = x^2 mod n
        if x == n - 1:
            return True

    return False  # Chắc chắn là hợp số


def is_prime(n, k=20):
    """
    Kiểm tra n có phải số nguyên tố không bằng thuật toán Miller-Rabin.
    k: số vòng kiểm tra (càng lớn càng chính xác).
    Với k=20, xác suất sai < (1/4)^20 ≈ 10^-12.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Kiểm tra chia hết cho các số nguyên tố nhỏ để nhanh hơn
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # Chạy k vòng Miller-Rabin với các nhân chứng ngẫu nhiên
    for _ in range(k):
        a = random.randrange(2, n - 1)
        if not miller_rabin_test(n, a):
            return False
    return True


# ============================================================
# 3. TÌM SỐ NGUYÊN TỐ LỚN (>= num_bits bits)
# ============================================================

def generate_large_prime(num_bits):
    """
    Tìm số nguyên tố lớn có đúng num_bits bit.
    - Sinh số ngẫu nhiên num_bits bit (bit cao nhất và bit thấp nhất = 1)
    - Kiểm tra nguyên tố bằng Miller-Rabin
    """
    print(f"  Đang tìm số nguyên tố {num_bits} bits...", end="", flush=True)
    count = 0
    while True:
        # Sinh số ngẫu nhiên num_bits bit
        # Bit cao nhất = 1 (đảm bảo đủ num_bits bit)
        # Bit thấp nhất = 1 (đảm bảo số lẻ)
        candidate = random.getrandbits(num_bits)
        candidate |= (1 << (num_bits - 1))  # đặt bit cao nhất = 1
        candidate |= 1                        # đặt bit thấp nhất = 1 (số lẻ)

        count += 1
        if is_prime(candidate):
            print(f" Tìm được sau {count} lần thử!")
            return candidate


# ============================================================
# 4. THUẬT TOÁN EUCLID MỞ RỘNG (Extended GCD)
# ============================================================

def gcd(a, b):
    """
    Tính ước số chung lớn nhất của a và b bằng thuật toán Euclid.
    Tự cài đặt, không dùng math.gcd().
    """
    while b != 0:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Thuật toán Euclid mở rộng.
    Trả về (gcd, x, y) sao cho: a*x + b*y = gcd(a, b)
    """
    if b == 0:
        return a, 1, 0
    g, x, y = extended_gcd(b, a % b)
    return g, y, x - (a // b) * y


def mod_inverse(e, phi):
    """
    Tính nghịch đảo modular của e theo phi: d * e ≡ 1 (mod phi).
    Sử dụng thuật toán Euclid mở rộng.
    Trả về d nếu tồn tại, ngược lại raise ValueError.
    """
    g, x, _ = extended_gcd(e, phi)
    if g != 1:
        raise ValueError(f"Nghịch đảo không tồn tại! gcd({e}, {phi}) = {g} ≠ 1")
    return x % phi


# ============================================================
# 5. CHỌN SỐ e HỢP LỆ
# ============================================================

def choose_public_exponent(phi_n):
    """
    Chọn số e hợp lệ: 1 < e < phi(n) và gcd(e, phi(n)) = 1.
    Ưu tiên dùng e = 65537 (số Fermat F4, phổ biến nhất trong RSA thực tế).
    Nếu không được thì tìm số khác.
    """
    e = 65537  # 2^16 + 1, số nguyên tố, được dùng rộng rãi
    if gcd(e, phi_n) == 1:
        return e
    # Nếu 65537 không hợp lệ, tìm e khác
    for e in range(3, phi_n, 2):
        if gcd(e, phi_n) == 1:
            return e
    raise ValueError("Không tìm được e hợp lệ!")


# ============================================================
# 6. TẠO BỘ KHÓA RSA NGẪU nhiên
# ============================================================

def generate_rsa_keypair(num_bits=512):
    """
    Tạo bộ khóa RSA ngẫu nhiên.

    Tham số:
        num_bits: số bit của mỗi số nguyên tố p, q (mặc định 512 bit → n ~ 1024 bit)

    Trả về:
        public_key  = (e, n)
        private_key = (d, n)
    """
    print(f"\n{'='*55}")
    print(f"  SINH BỘ KHÓA RSA ({num_bits*2} bits)")
    print(f"{'='*55}")

    # Bước 1: Chọn 2 số nguyên tố lớn p, q
    print("\n[Bước 1] Tạo hai số nguyên tố lớn p và q:")
    p = generate_large_prime(num_bits)
    q = generate_large_prime(num_bits)
    while p == q:
        q = generate_large_prime(num_bits)

    # Bước 2: Tính n = p * q
    n = p * q
    print(f"\n[Bước 2] n = p × q ({n.bit_length()} bits)")

    # Bước 3: Tính phi(n) = (p-1)(q-1)
    phi_n = (p - 1) * (q - 1)
    print(f"[Bước 3] φ(n) = (p-1)(q-1)")

    # Bước 4: Chọn e
    e = choose_public_exponent(phi_n)
    print(f"[Bước 4] e = {e}")

    # Bước 5: Tính d = e^(-1) mod phi(n)
    d = mod_inverse(e, phi_n)
    print(f"[Bước 5] d = e⁻¹ mod φ(n) (tính bằng Extended Euclid)")

    # Kiểm tra: e*d mod phi(n) == 1
    assert (e * d) % phi_n == 1, "Lỗi: e*d mod phi(n) ≠ 1!"
    print(f"\n✓ Kiểm tra: (e × d) mod φ(n) = {(e * d) % phi_n}")

    public_key  = (e, n)
    private_key = (d, n)
    return public_key, private_key


# ============================================================
# 7. MÃ HÓA VÀ GIẢI MÃ (số nguyên)
# ============================================================

def rsa_encrypt_int(m, public_key):
    """
    Mã hóa số nguyên m: c = m^e mod n
    m phải thỏa 0 <= m < n
    """
    e, n = public_key
    if m < 0 or m >= n:
        raise ValueError(f"Thông điệp m={m} phải nằm trong [0, n-1]")
    return mod_pow(m, e, n)


def rsa_decrypt_int(c, private_key):
    """
    Giải mã số nguyên c: m = c^d mod n
    """
    d, n = private_key
    return mod_pow(c, d, n)


# ============================================================
# 8. MÃ HÓA VÀ GIẢI MÃ CHUỖI VĂN BẢN
# ============================================================

def text_to_int(text):
    """Chuyển chuỗi văn bản → số nguyên (dùng UTF-8)."""
    return int.from_bytes(text.encode('utf-8'), byteorder='big')


def int_to_text(number):
    """Chuyển số nguyên → chuỗi văn bản."""
    byte_length = (number.bit_length() + 7) // 8
    return number.to_bytes(byte_length, byteorder='big').decode('utf-8')


def rsa_encrypt_text(plaintext, public_key):
    """
    Mã hóa chuỗi văn bản bằng RSA.
    Nếu thông điệp quá dài (>= n), tự động chia thành nhiều khối.

    Trả về: list các số nguyên mã hóa (ciphertext blocks)
    """
    e, n = public_key
    # Tính kích thước khối tối đa (bytes) để m < n
    block_size = (n.bit_length() // 8) - 1  # để đảm bảo m < n

    plaintext_bytes = plaintext.encode('utf-8')
    ciphertext_blocks = []

    # Chia thành từng khối và mã hóa
    for i in range(0, len(plaintext_bytes), block_size):
        block = plaintext_bytes[i:i + block_size]
        m = int.from_bytes(block, byteorder='big')
        c = rsa_encrypt_int(m, public_key)
        ciphertext_blocks.append(c)

    return ciphertext_blocks


def rsa_decrypt_text(ciphertext_blocks, private_key, block_size_bytes=None):
    """
    Giải mã list các số nguyên → chuỗi văn bản.
    """
    d, n = private_key
    if block_size_bytes is None:
        block_size_bytes = (n.bit_length() // 8) - 1

    plaintext_bytes = b""
    for c in ciphertext_blocks:
        m = rsa_decrypt_int(c, private_key)
        # Chuyển m về bytes với độ dài cố định
        byte_len = (m.bit_length() + 7) // 8
        plaintext_bytes += m.to_bytes(byte_len, byteorder='big')

    return plaintext_bytes.decode('utf-8')


# ============================================================
# 9. KEY MANAGEMENT (LƯU/TẢI KHÓA)
# ============================================================

def save_keypair(public_key, private_key, key_name=None):
    """
    Lưu bộ khóa RSA vào file JSON.
    
    Tham số:
        public_key: tuple (e, n)
        private_key: tuple (d, n)
        key_name: tên file (mặc định: dấu thời gian)
    
    Trả về: tên file được lưu
    """
    if key_name is None:
        key_name = f"rsa_key_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    e, n = public_key
    d, _ = private_key
    
    key_data = {
        "name": key_name,
        "created": datetime.now().isoformat(),
        "key_bits": n.bit_length(),
        "public_key": {
            "e": int_to_str(e),
            "n": int_to_str(n)
        },
        "private_key": {
            "d": int_to_str(d),
            "n": int_to_str(n)
        }
    }
    
    file_path = KEYS_DIR / f"{key_name}.json"
    with open(file_path, 'w') as f:
        json.dump(key_data, f, indent=2)
    
    print(f"✓ Đã lưu khóa: {file_path}")
    return key_name


def load_keypair(key_name):
    """
    Tải bộ khóa RSA từ file JSON.
    
    Tham số:
        key_name: tên file (có hoặc không có .json)
    
    Trả về: (public_key, private_key)
    """
    if not key_name.endswith('.json'):
        key_name = f"{key_name}.json"
    
    file_path = KEYS_DIR / key_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file khóa: {file_path}")
    
    with open(file_path, 'r') as f:
        key_data = json.load(f)
    
    e = str_to_int(key_data["public_key"]["e"])
    n = str_to_int(key_data["public_key"]["n"])
    d = str_to_int(key_data["private_key"]["d"])
    
    public_key = (e, n)
    private_key = (d, n)
    
    print(f"✓ Đã tải khóa: {file_path}")
    return public_key, private_key


def list_keypairs():
    """Liệt kê tất cả bộ khóa được lưu."""
    key_files = sorted(KEYS_DIR.glob("*.json"))
    
    if not key_files:
        print("  Không có bộ khóa nào được lưu.")
        return []
    
    print(f"\n  Danh sách bộ khóa ({len(key_files)}):")
    print(f"  {'─'*60}")
    
    keys_info = []
    for idx, file_path in enumerate(key_files, 1):
        with open(file_path, 'r') as f:
            key_data = json.load(f)
        
        name = key_data.get("name", file_path.stem)
        created = key_data.get("created", "N/A")
        bits = key_data.get("key_bits", "?")
        
        print(f"  [{idx}] {name}")
        print(f"      Bit: {bits} | Tạo: {created}")
        keys_info.append((idx, name, file_path.stem))
    
    print(f"  {'─'*60}\n")
    return keys_info


def view_key_details(key_name):
    """Xem chi tiết của một bộ khóa."""
    if not key_name.endswith('.json'):
        key_name = f"{key_name}.json"
    
    file_path = KEYS_DIR / key_name
    
    if not file_path.exists():
        print(f"Không tìm thấy file: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        key_data = json.load(f)
    
    print(f"\n{'─'*60}")
    print(f"  CHI TIẾT BỘ KHÓA: {key_data['name']}")
    print(f"{'─'*60}")
    print(f"  Ngày tạo: {key_data['created']}")
    print(f"  Độ dài key: {key_data['key_bits']} bits")
    print(f"\n  Khóa công khai (e, n):")
    e_hex = key_data["public_key"]["e"]
    n_hex = key_data["public_key"]["n"]
    print(f"    e = {e_hex}")
    print(f"    n = {n_hex}")
    print(f"\n  Khóa bí mật (d, n): [ẨNMẶC]")
    print(f"{'─'*60}\n")


# ============================================================
# 10. CIPHER MANAGEMENT (LƯU/TẢI BẢN MÃ)
# ============================================================

def save_cipher(ciphertext_blocks, key_name, message_label=None, source_filename=None):
    """
    Lưu bản mã vào file JSON với metadata.
    
    Tham số:
        ciphertext_blocks: list các số nguyên mã hóa
        key_name: tên bộ khóa được dùng
        message_label: nhãn tin nhắn (mặc định: dấu thời gian)
        source_filename: tên file gốc nếu mã hóa từ file (mặc định: None - CLI input)
    
    Trả về: tên file được lưu
    """
    if message_label is None:
        message_label = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    cipher_data = {
        "label": message_label,
        "created": datetime.now().isoformat(),
        "key_used": key_name,
        "blocks_count": len(ciphertext_blocks),
        "source_filename": source_filename,  # None nếu từ CLI, string nếu từ file
        "ciphertext": [int_to_str(c) for c in ciphertext_blocks]
    }
    
    file_path = CIPHERS_DIR / f"{message_label}.json"
    with open(file_path, 'w') as f:
        json.dump(cipher_data, f, indent=2)
    
    print(f"✓ Đã lưu bản mã: {file_path}")
    return message_label


def load_cipher(cipher_name):
    """
    Tải bản mã từ file JSON.
    
    Tham số:
        cipher_name: tên file (có hoặc không có .json)
    
    Trả về: (ciphertext_blocks, key_name_used, label, source_filename)
    """
    if not cipher_name.endswith('.json'):
        cipher_name = f"{cipher_name}.json"
    
    file_path = CIPHERS_DIR / cipher_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file bản mã: {file_path}")
    
    with open(file_path, 'r') as f:
        cipher_data = json.load(f)
    
    ciphertext_blocks = [str_to_int(c) for c in cipher_data["ciphertext"]]
    key_name = cipher_data["key_used"]
    label = cipher_data["label"]
    source_filename = cipher_data.get("source_filename", None)  # Backward compatibility
    
    print(f"✓ Đã tải bản mã: {file_path}")
    return ciphertext_blocks, key_name, label, source_filename


def list_ciphers():
    """Liệt kê tất cả bản mã được lưu."""
    cipher_files = sorted(CIPHERS_DIR.glob("*.json"))
    
    if not cipher_files:
        print("  Không có bản mã nào được lưu.")
        return []
    
    print(f"\n  Danh sách bản mã ({len(cipher_files)}):")
    print(f"  {'─'*80}")
    
    ciphers_info = []
    for idx, file_path in enumerate(cipher_files, 1):
        with open(file_path, 'r') as f:
            cipher_data = json.load(f)
        
        label = cipher_data.get("label", file_path.stem)
        key_used = cipher_data.get("key_used", "?")
        created = cipher_data.get("created", "N/A")
        blocks = cipher_data.get("blocks_count", "?")
        source = cipher_data.get("source_filename", None)
        
        source_info = f"File: {source}" if source else "CLI: [nhập tay]"
        
        print(f"  [{idx}] {label}")
        print(f"      Khóa: {key_used} | Khối: {blocks} | Nguồn: {source_info}")
        ciphers_info.append((idx, label, file_path.stem))
    
    print(f"  {'─'*80}\n")
    return ciphers_info


def list_files_in_current_dir(max_results=20):
    """Liệt kê các file trong thư mục hiện tại (không phải thư mục con)."""
    try:
        files = [f for f in Path(".").iterdir() if f.is_file() and not f.name.startswith('.')]
        files.sort()
        
        if not files:
            print("  Không có file nào trong thư mục hiện tại.")
            return []
        
        print(f"\n  Danh sách file ({len(files)}):")
        print(f"  {'─'*70}")
        
        files_info = []
        for idx, file_path in enumerate(files[:max_results], 1):
            size_kb = file_path.stat().st_size / 1024
            print(f"  [{idx:2d}] {file_path.name:<45} ({size_kb:>8.1f} KB)")
            files_info.append((idx, file_path.name, str(file_path)))
        
        if len(files) > max_results:
            print(f"  ... và {len(files) - max_results} file khác")
        
        print(f"  {'─'*70}\n")
        return files_info
    except Exception as e:
        print(f"  ✗ Lỗi khi liệt kê file: {e}")
        return []


def encrypt_file(file_path, public_key, current_key_name):
    """
    Mã hóa nội dung file.
    
    Tham số:
        file_path: đường dẫn đến file
        public_key: khóa công khai (e, n)
        current_key_name: tên bộ khóa được dùng
    
    Trả về: (ciphertext_blocks, filename_only, cipher_name)
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File không tồn tại: {file_path}")
        
        # Đọc file dưới dạng byte
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        file_size_kb = len(file_content) / 1024
        print(f"  Đang mã hóa file: {file_path.name} ({file_size_kb:.1f} KB)")
        
        # Chuyển bytes thành số nguyên rồi mã hóa
        e, n = public_key
        block_size = (n.bit_length() // 8) - 1
        
        ciphertext_blocks = []
        for i in range(0, len(file_content), block_size):
            block = file_content[i:i + block_size]
            m = int.from_bytes(block, byteorder='big')
            c = rsa_encrypt_int(m, public_key)
            ciphertext_blocks.append(c)
        
        print(f"  ✓ Mã hóa thành công! Số khối: {len(ciphertext_blocks)}")
        
        # Lưu bản mã với source_filename
        cipher_name = save_cipher(ciphertext_blocks, current_key_name, 
                                 source_filename=file_path.name)
        
        return ciphertext_blocks, file_path.name, cipher_name
    
    except Exception as e:
        print(f"  ✗ Lỗi mã hóa file: {e}")
        raise


def decrypt_to_file(ciphertext_blocks, private_key, source_filename):
    """
    Giải mã và lưu vào file mới.
    
    Tham số:
        ciphertext_blocks: list các khối mã hóa
        private_key: khóa bí mật (d, n)
        source_filename: tên file gốc (để tạo tên file decrypt)
    
    Trả về: đường dẫn file mới được tạo
    """
    try:
        # Giải mã tất cả các khối
        d, n = private_key
        block_size_bytes = (n.bit_length() // 8) - 1
        
        decrypted_bytes = b""
        for c in ciphertext_blocks:
            m = rsa_decrypt_int(c, private_key)
            byte_len = (m.bit_length() + 7) // 8
            decrypted_bytes += m.to_bytes(byte_len, byteorder='big')
        
        # Tạo tên file mới: filename_decrypted.ext
        source_path = Path(source_filename)
        stem = source_path.stem
        suffix = source_path.suffix
        new_filename = f"{stem}_decrypted{suffix}"
        
        # Lưu file
        with open(new_filename, 'wb') as f:
            f.write(decrypted_bytes)
        
        file_size_kb = len(decrypted_bytes) / 1024
        print(f"\n{'─'*70}")
        print(f"✓ GIẢI MÃ THÀNH CÔNG!")
        print(f"{'─'*70}")
        print(f"File được lưu: {new_filename} ({file_size_kb:.1f} KB)")
        print(f"{'─'*70}\n")
        
        return new_filename
    
    except Exception as e:
        print(f"✗ Lỗi giải mã file: {e}")
        raise


# ============================================================
# 11. DEMO CHẠY THỬ
# ============================================================

def demo_rsa(num_bits=512):
    """
    Demo hoàn chỉnh: sinh khóa → mã hóa → giải mã.
    num_bits: số bit mỗi số nguyên tố (512 → n ~ 1024 bit)
    """
    print("\n" + "="*60)
    print("   DEMO HỆ MÃ RSA - BÀI TẬP LỚN SỐ 3")
    print("="*60)

    start = time.time()

    # ---- Sinh khóa ----
    public_key, private_key = generate_rsa_keypair(num_bits)
    e, n = public_key
    d, _ = private_key

    print(f"\n{'─'*55}")
    print("  THÔNG TIN KHÓA")
    print(f"{'─'*55}")
    print(f"  Khóa công khai  (e, n):")
    print(f"    e = {e}")
    print(f"    n = {str(n)}  ({n.bit_length()} bits)")
    print(f"  Khóa bí mật  (d, n):")
    print(f"    d = {str(d)}  ({d.bit_length()} bits)")

    # ---- Test 1: Mã hóa số nguyên ----
    print(f"\n{'─'*55}")
    print("  TEST 1: Mã hóa / Giải mã số nguyên")
    print(f"{'─'*55}")
    m = 123456789
    c = rsa_encrypt_int(m, public_key)
    m_dec = rsa_decrypt_int(c, private_key)
    print(f"  Thông điệp gốc  : {m}")
    print(f"  Bản mã          : {str(c)}")
    print(f"  Giải mã ra      : {m_dec}")
    print(f"  Kết quả         : {'✓ ĐÚNG' if m == m_dec else '✗ SAI'}")

    # ---- Test 2: Mã hóa chuỗi văn bản ----
    print(f"\n{'─'*55}")
    print("  TEST 2: Mã hóa / Giải mã chuỗi văn bản")
    print(f"{'─'*55}")
    plaintext = "Xin chào! Đây là bài tập lớn số 3 - RSA Implementation."
    print(f"  Thông điệp gốc  : {plaintext}")

    cipher_blocks = rsa_encrypt_text(plaintext, public_key)
    print(f"  Số khối mã hóa  : {len(cipher_blocks)}")
    print(f"  Khối đầu tiên   : {str(cipher_blocks[0])}")

    decrypted = rsa_decrypt_text(cipher_blocks, private_key)
    print(f"  Giải mã ra      : {decrypted}")
    print(f"  Kết quả         : {'✓ ĐÚNG' if plaintext == decrypted else '✗ SAI'}")

    elapsed = time.time() - start
    print(f"\n{'─'*55}")
    print(f"  Tổng thời gian  : {elapsed:.2f} giây")
    print(f"{'─'*55}\n")


# ============================================================
# 12. GIAO DIỆN TƯƠNG TÁC 
# ============================================================

def interactive_menu():
    """Menu tương tác để test từng chức năng."""
    print("\n" + "="*70)
    print("   HỆ MÃ RSA - MENU TƯƠNG TÁC (LƯU/TẢI KHÓA VÀ BẢN MÃ)")
    print("="*70)
    
    public_key_global  = None
    private_key_global = None
    cipher_global      = None
    current_key_name   = None
    current_cipher_name = None
    
    # Tải cấu hình session
    config = get_current_config()
    if config['current_key_pair']:
        try:
            public_key_global, private_key_global = load_keypair(config['current_key_pair'])
            current_key_name = config['current_key_pair']
            print(f"\n✓ Đã khôi phục khóa: {current_key_name}")
        except:
            pass
            print("\n" + "="*70)
        print("  MENU CHÍNH")
        print("="*70)
        if current_key_name:
            print(f"  [Khóa hiện tại: {current_key_name}]")
        if current_cipher_name:
            print(f"  [Bản mã hiện tại: {current_cipher_name}]")
    print("="*70)
    print("  ┌─ SINH VÀ QUẢN LÝ KHÓA")
    print("  │  1. Sinh bộ khóa RSA mới (512-bit → 1024-bit)")
    print("  │  2. Sinh bộ khóa RSA mới (1024-bit → 2048-bit)")
    print("  │  3. Liệt kê bộ khóa được lưu")
    print("  │  4. Tải bộ khóa từ file")
    print("  │  5. Xem chi tiết khóa")
    print("  ├─ MÃ HÓA VÀ GIẢI MÃ")
    print("  │  6. Mã hóa thông điệp mới")
    print("  │  7. Giải mã bản mã")
    print("  │  8. Liệt kê bản mã được lưu")
    print("  │  9. Tải bản mã từ file")
    print("  ├─ TIỆN ÍCH")
    print("  │  10. Kiểm tra một số có nguyên tố không")
    print("  │  11. Tính GCD của hai số")
    print("  │  12. Chạy Demo đầy đủ")
    print("  │  13. Xóa bộ nhớ session")
    print("  └─")
    print("  0. Thoát")
    print("="*70)
    while True:

        try:
            choice = input("\nChọn chức năng (0-13): ").strip()

            if choice == "0":
                print("Thoát chương trình.")
                break

            elif choice == "1":
                print("\n  Sinh bộ khóa 1024-bit (512-bit primes)...")
                public_key_global, private_key_global = generate_rsa_keypair(512)
                e, n = public_key_global
                d, _ = private_key_global
                print(f"\n  ✓ Sinh khóa thành công!")
                print(f"  e = {e}")
                print(f"  n  = {str(n)[:100]}... ({n.bit_length()} bits)")
                
                save_choice = input("\n  Lưu khóa này? (y/n, mặc định: y): ").strip().lower()
                if save_choice != 'n':
                    key_label = input("  Nhập tên khóa (mặc định: auto): ").strip()
                    current_key_name = save_keypair(public_key_global, private_key_global, key_label if key_label else None)
                    config['current_key_pair'] = current_key_name
                    save_config(config)

            elif choice == "2":
                print("\n  Sinh bộ khóa 2048-bit (1024-bit primes - CÓ THỂ MẤT THỜI GIAN)...")
                public_key_global, private_key_global = generate_rsa_keypair(1024)
                e, n = public_key_global
                d, _ = private_key_global
                print(f"\n  ✓ Sinh khóa 2048-bit thành công!")
                print(f"  e = {e}")
                print(f"  n  = {str(n)[:100]}... ({n.bit_length()} bits)")
                
                save_choice = input("\n  Lưu khóa này? (y/n, mặc định: y): ").strip().lower()
                if save_choice != 'n':
                    key_label = input("  Nhập tên khóa (mặc định: auto): ").strip()
                    current_key_name = save_keypair(public_key_global, private_key_global, key_label if key_label else None)
                    config['current_key_pair'] = current_key_name
                    save_config(config)

            elif choice == "3":
                keys_info = list_keypairs()
                if keys_info:
                    idx_str = input("  Chọn khóa để xem chi tiết (số thứ tự, hoặc bỏ qua): ").strip()
                    if idx_str.isdigit():
                        idx = int(idx_str) - 1
                        if 0 <= idx < len(keys_info):
                            _, _, key_file = keys_info[idx]
                            view_key_details(key_file)

            elif choice == "4":
                keys_info = list_keypairs()
                if keys_info:
                    idx_str = input("  Chọn khóa để tải (số thứ tự): ").strip()
                    if idx_str.isdigit():
                        idx = int(idx_str) - 1
                        if 0 <= idx < len(keys_info):
                            _, _, key_file = keys_info[idx]
                            try:
                                public_key_global, private_key_global = load_keypair(key_file)
                                current_key_name = key_file
                                config['current_key_pair'] = current_key_name
                                save_config(config)
                                print(f"\n  ✓ Đã đặt khóa hiện tại: {current_key_name}")
                            except Exception as e:
                                print(f"  ✗ Lỗi: {e}")

            elif choice == "5":
                keys_info = list_keypairs()
                if keys_info:
                    idx_str = input("  Chọn khóa để xem (số thứ tự): ").strip()
                    if idx_str.isdigit():
                        idx = int(idx_str) - 1
                        if 0 <= idx < len(keys_info):
                            _, _, key_file = keys_info[idx]
                            view_key_details(key_file)

            elif choice == "6":
                if public_key_global is None:
                    print("  ✗ Chưa có khóa! Vui lòng sinh hoặc tải khóa trước.")
                    continue
                
                encrypt_mode = input("\n  Chọn chế độ mã hóa:\n    [1] Nhập thông điệp từ CLI\n    [2] Mã hóa từ file\n  Lựa chọn (1 hoặc 2): ").strip()
                
                if encrypt_mode == "1":
                    # Mã hóa từ CLI
                    msg = input("  Nhập thông điệp cần mã hóa: ")
                    cipher_global = rsa_encrypt_text(msg, public_key_global)
                    print(f"  ✓ Mã hóa thành công! Số khối: {len(cipher_global)}")
                    print(f"  Khối đầu tiên: {str(cipher_global[0])[:80]}...")
                    
                    save_choice = input("\n  Lưu bản mã này? (y/n, mặc định: y): ").strip().lower()
                    if save_choice != 'n':
                        msg_label = input("  Nhập tên bản mã (mặc định: auto): ").strip()
                        # Lưu với source_filename=None (vì từ CLI)
                        current_cipher_name = save_cipher(cipher_global, current_key_name, 
                                                         msg_label if msg_label else None, 
                                                         source_filename=None)
                        config['current_cipher'] = current_cipher_name
                        save_config(config)
                
                elif encrypt_mode == "2":
                    # Mã hóa từ file
                    files_info = list_files_in_current_dir()
                    if files_info:
                        idx_str = input("  Chọn file để mã hóa (số thứ tự): ").strip()
                        if idx_str.isdigit():
                            idx = int(idx_str) - 1
                            if 0 <= idx < len(files_info):
                                _, filename, filepath = files_info[idx]
                                try:
                                    cipher_global, original_name, cipher_name = encrypt_file(
                                        filepath, public_key_global, current_key_name
                                    )
                                    current_cipher_name = cipher_name
                                    config['current_cipher'] = current_cipher_name
                                    save_config(config)
                                except Exception as e:
                                    print(f"  ✗ Lỗi: {e}")
                else:
                    print("  Lựa chọn không hợp lệ.")


            elif choice == "7":
                if private_key_global is None:
                    print("  ✗ Chưa có khóa bí mật! Vui lòng tải khóa trước.")
                    continue
                if cipher_global is None:
                    print("  ✗ Chưa có bản mã! Vui lòng tải hoặc mã hóa trước.")
                    continue
                
                # Cần lấy source_filename từ current_cipher_name
                source_filename = None
                if current_cipher_name:
                    cipher_file_path = CIPHERS_DIR / f"{current_cipher_name}.json"
                    if cipher_file_path.exists():
                        with open(cipher_file_path, 'r') as f:
                            cipher_data = json.load(f)
                            source_filename = cipher_data.get("source_filename", None)
                
                try:
                    if source_filename:
                        # Mã hóa từ file -> lưu vào file mới
                        decrypt_to_file(cipher_global, private_key_global, source_filename)
                    else:
                        # Mã hóa từ CLI -> in ra CLI
                        result = rsa_decrypt_text(cipher_global, private_key_global)
                        print(f"\n{'─'*70}")
                        print(f"✓ GIẢI MÃ THÀNH CÔNG!")
                        print(f"{'─'*70}")
                        print(f"  Thông điệp:\n{result}")
                        print(f"{'─'*70}")
                        input("\n  Nhấn Enter để tiếp tục...")
                except Exception as e:
                    print(f"  ✗ Lỗi giải mã: {e}")


            elif choice == "8":
                ciphers_info = list_ciphers()

            elif choice == "9":
                ciphers_info = list_ciphers()
                if ciphers_info:
                    idx_str = input("  Chọn bản mã để tải (số thứ tự): ").strip()
                    if idx_str.isdigit():
                        idx = int(idx_str) - 1
                        if 0 <= idx < len(ciphers_info):
                            _, _, cipher_file = ciphers_info[idx]
                            try:
                                cipher_global, key_name, label, source_filename = load_cipher(cipher_file)
                                current_cipher_name = cipher_file
                                config['current_cipher'] = current_cipher_name
                                save_config(config)
                                source_info = f"File: {source_filename}" if source_filename else "CLI: [nhập tay]"
                                print(f"\n  ✓ Đã đặt bản mã hiện tại: {current_cipher_name}")
                                print(f"  (Mã hóa bằng: {key_name}, Nguồn: {source_info})")
                                
                                # Tự động tải khóa được dùng
                                load_choice = input("\n  Tải khóa được dùng? (y/n, mặc định: y): ").strip().lower()
                                if load_choice != 'n':
                                    try:
                                        public_key_global, private_key_global = load_keypair(key_name)
                                        current_key_name = key_name
                                        config['current_key_pair'] = current_key_name
                                        save_config(config)
                                        print(f"  ✓ Đã tải khóa: {key_name}")
                                    except Exception as e:
                                        print(f"  ✗ Lỗi tải khóa: {e}")
                            except Exception as e:
                                print(f"  ✗ Lỗi: {e}")

            elif choice == "10":
                num_str = input("  Nhập số cần kiểm tra: ").strip()
                num = int(num_str)
                result = is_prime(num)
                print(f"  → {num} {'LÀ số nguyên tố ✓' if result else 'KHÔNG phải số nguyên tố ✗'}")

            elif choice == "11":
                a = int(input("  Nhập số a: ").strip())
                b = int(input("  Nhập số b: ").strip())
                g = gcd(a, b)
                print(f"  → GCD({a}, {b}) = {g}")

            elif choice == "12":
                demo_rsa(512)

            elif choice == "13":
                confirm = input("  Xóa bộ nhớ session? (y/n): ").strip().lower()
                if confirm == 'y':
                    public_key_global = None
                    private_key_global = None
                    cipher_global = None
                    current_key_name = None
                    current_cipher_name = None
                    config['current_key_pair'] = None
                    config['current_cipher'] = None
                    save_config(config)
                    print("  ✓ Đã xóa bộ nhớ session")

            else:
                print("  Lựa chọn không hợp lệ. Vui lòng nhập 0-13.")

        except ValueError as ve:
            print(f"  ✗ Lỗi giá trị: {ve}")
        except KeyboardInterrupt:
            print("\n  Đã dừng.")
            break
        except Exception as e:
            print(f"  ✗ Lỗi: {e}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --- Chạy Demo tự động ---
    # demo_rsa(num_bits=512)

    interactive_menu()