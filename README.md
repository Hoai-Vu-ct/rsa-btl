# Bài tập RSA Cryptography

## Chạy chương trình:
```bash
python main.py
```

Chương trình sẽ tự động tạo các thư mục cần thiết:

- keys/ - Lưu trữ các cặp khóa RSA
- ciphers/ - Lưu trữ các thông điệp đã encrypt
- rsa_session.json - Theo dõi phiên làm việc hiện tại

## Quick Start

### Tạo và lưu cặp khóa
```
1. Chạy: python main.py
2. Chọn: [1] - Tạo khóa 1024-bit (số nguyên tố 512-bit)
3. Chọn: [y] - Lưu khóa
4. Nhập tên (hoặc để trống để tự động tạo)
```

### Encrypt một thông điệp
```
1. Chọn: [6] - Encrypt
2. Chọn: [1] - Encrypt từ CLI hoặc [2] - Encrypt từ file
3. Nhập thông điệp hoặc chọn file
4. Chọn: [y] - Lưu cipher
```

### Decrypt một thông điệp
```
1. Chọn: [7] - Decrypt
2. Tự động nhận diện:
   - Nếu từ file: Tạo "filename_decrypted.ext"
   - Nếu từ CLI: Hiển thị thông điệp trên màn hình và tạm dừng
```

## Hướng dẫn menu

[0] Thoát chương trình

### Quản lý khóa (Tùy chọn 1-5)
[1] Tạo khóa RSA 1024-bit (số nguyên tố 512-bit - Nhanh)
[2] Tạo khóa RSA 2048-bit (số nguyên tố 1024-bit - Chậm hơn nhưng mạnh hơn)
[3] Liệt kê tất cả các cặp khóa đã lưu
[4] Tải một cặp khóa từ file
[5] Xem chi tiết của một khóa cụ thể

### Encrypt & Decrypt (Tùy chọn 6-9)
[6] Encrypt một thông điệp hoặc file
    - Chọn giữa nhập từ CLI hoặc chọn file
    - Có thể lưu thông điệp đã encrypt
[7] Decrypt một thông điệp
    - Tự động lưu ra file hoặc in ra màn hình
    - Hiển thị kết quả với chế độ tạm dừng để tránh trôi màn hình
[8] Liệt kê tất cả các cipher đã lưu (hiển thị nguồn: file hoặc CLI)
[9] Tải một cipher và tự động tải khóa tương ứng

### Utilities (Options 10-13)
[10] Kiểm tra một số có phải số nguyên tố không
[11] Tính GCD của hai số
[12] Chạy demo hoàn chỉnh (tạo khóa, encrypt, decrypt)
[13] Xóa bộ nhớ phiên (khóa và cipher)


## File Structure

```
BTL/
├── main.py                   # File chương trình chính
├── README.md                 # File này
├── keys/                     # Lưu trữ cặp khóa RSA (JSON)
│   ├── rsa_key_20260502_143000.json
│   └── rsa_key_mykey.json
├── ciphers/                  # Lưu trữ thông điệp đã encrypt (JSON)
│   ├── msg_20260502_143015.json
│   └── msg_cli_test.json
├── rsa_session.json          # Trạng thái phiên hiện tại
└── test_message.txt          # File ví dụ để encrypt
```

## Ví dụ sử dụng

### Ví dụ 1: Encrypt thông điệp cơ bản

```
[Menu] Chọn: 1
→ Tạo khóa 1024-bit
→ Lưu thành: rsa_key_20260502_150000.json

[Menu] Chọn: 6 → 1
→ Nhập: "Hello, RSA!"
→ Lưu thành: msg_20260502_150015.json

[Menu] Chọn: 7
→ Hiển thị: "Hello, RSA!" với khung rõ ràng
→ Tự động tạm dừng để dễ nhìn
```

### Ví dụ 2: Encrypt/Decrypt file

```
[Menu] Chọn: 6 → 2
→ Liệt kê file trong thư mục hiện tại
→ Chọn: [1] test_message.txt
→ Encrypt file thành: msg_20260502_150030.json

[Menu] Chọn: 9
→ Chọn: [1] msg_20260502_150030.json
→ Tự động tải khóa đã dùng để encrypt

[Menu] Chọn: 7
→ Tạo: test_message_decrypted.txt
→ Nội dung file gốc được khôi phục!
```

### Ví dụ 3: Làm việc qua nhiều sessions

**Session 1:**
```
[Menu] Chọn: 1 → Tạo khóa → Lưu thành "my_key"
[Menu] Chọn: 6 → Encrypt thông điệp → Lưu lại
[Menu] Chọn: 0 → Thoát
```

**Session 2:**
```
[Menu] Chương trình khởi động
→ Tự động tải "my_key" (khôi phục phiên)
→ Cipher trước đó cũng được tải
[Menu] Chọn: 7 → Decrypt ngay!
```

## Storage Format

### Key Pair JSON Format
```json
{
  "name": "rsa_key_20260502_150000",
  "created": "2026-05-02T15:00:00.123456",
  "key_bits": 1024,
  "public_key": {
    "e": "0x10001",
    "n": "0xc3d..."  // Large hex number
  },
  "private_key": {
    "d": "0x8f2...",  // Large hex number
    "n": "0xc3d..."
  }
}
```

### Cipher JSON Format
```json
{
  "label": "msg_20260502_150015",
  "created": "2026-05-02T15:00:15.654321",
  "key_used": "rsa_key_20260502_150000",
  "blocks_count": 3,
  "source_filename": "document.pdf",  // null if from CLI
  "ciphertext": ["0x3a2b...", "0x9c1f...", "0x7d8e..."]
}
```

### Session Config JSON Format
```json
{
  "current_key_pair": "rsa_key_20260502_150000",
  "current_cipher": "msg_20260502_150015"
}
```


