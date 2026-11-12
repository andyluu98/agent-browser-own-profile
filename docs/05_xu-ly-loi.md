# 05. Xử lý lỗi

| Thông báo | Nguyên nhân | Cách xử lý |
|---|---|---|
| "CHƯA CÓ PYTHON 3.11+" | Máy chưa có Python hoặc chưa thêm vào PATH | Cài từ python.org, chọn "Add python.exe to PATH" |
| "file tải về không khớp mã kiểm tra SHA-256" | Tải dở hoặc file bị thay đổi trên đường truyền | Chạy lại `setup`; vẫn lỗi thì báo người hướng dẫn |
| "Trang yêu cầu đăng nhập" | Hồ sơ chưa đăng nhập trang đó, hoặc phiên đã hết hạn | `ab close`, rồi `login --site <trang>` |
| "DỪNG: Trang đang hỏi xác minh" | Trang nghi ngờ là máy | Xem [docs/03](03_vi-sao-bi-chan.md); thử `--main` |
| "nút đã đổi tên ..., không bấm" | Trang thay đổi giữa lúc đọc và lúc bấm | Chạy lại lệnh; nếu lặp lại, trang đã đổi bố cục |
| Lệnh `login` mở Chrome nhưng báo hồ sơ đang dùng | Chrome của công cụ còn giữ mở | `ab close` rồi chạy lại `login` |
| "Không tách được dòng nào", có file `-raw.txt` | Trang đổi bố cục | Đọc file raw, sửa mốc nhận diện trong `abkit/parse.py`, thêm mẫu vào test |
| Khung bình luận TikTok trống | TikTok không tải bình luận cho hồ sơ mới | Dùng `--main` |

## Kết quả vận hành thử (12/11/2026, Windows 11, Chrome 157)

| Lệnh | Kết quả |
|---|---|
| `setup` | Tải và kiểm tra agent-browser 0.42.0 trong 2 giây |
| `check --site facebook` | Đọc được 59 đến 64 nút và ô bằng hồ sơ đã đăng nhập |
| `check --site tiktok-studio` | Đọc được trang tải video |
| `facebook-post` (không `--yes`) | Mở khung soạn bài, điền nội dung, tìm thấy nút Post đã bật, dừng và đóng Chrome |
| `shopee` | Báo "Trang yêu cầu đăng nhập" do phiên Shopee trong hồ sơ thử đã hết hạn (bản cũ báo giống hệt) |
| `tiktok-post` | Chưa vận hành thử trên bản này |

Lần đầu dùng `tiktok-post`: chạy không có `--yes` để kiểm tra các bước trước nút Post, đúng hết mới chạy lại với `--yes`.
