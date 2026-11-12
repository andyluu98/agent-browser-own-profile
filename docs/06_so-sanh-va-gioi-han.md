# 06. So sánh với browser-own-profile và các giới hạn đã biết

Số đo ngày 12/11/2026 trên Windows 11 Pro, Chrome 157, cùng một hồ sơ đã đăng nhập. Thời gian tính từ lúc gọi lệnh tới lúc lệnh kết thúc.

## Tốc độ

| Việc | browser-own-profile | agent-browser-own-profile |
|---|---|---|
| `check --site facebook`, Chrome chưa mở | 9,1 đến 10,7 giây | 10,3 đến 10,4 giây |
| `check --site facebook`, Chrome đang giữ mở | Không áp dụng (mỗi lệnh mở Chrome mới) | 9,5 giây |
| `check --site tiktok-studio`, Chrome đang giữ mở | Chưa đo | 4,6 giây |
| Đọc cấu trúc một trang | Chưa đo riêng | 0,03 giây |

Kết luận: với lệnh chạy một lần, hai bản gần như ngang nhau, vì thời gian chủ yếu nằm ở việc mở Chrome và chờ trang tải (Facebook tải chậm). Bản mới chỉ nhanh hơn rõ khi chạy nhiều lệnh liên tiếp trong 5 phút, hoặc khi thăm dò từng bước bằng `ab`.

## Token

| Cách dùng | Lượng chữ trả về cho AI |
|---|---|
| Lệnh viết sẵn, ví dụ `check --site facebook` | Khoảng 530 ký tự |
| `ab snapshot -i` trên trang Facebook | Khoảng 3.100 ký tự mỗi lần đọc |
| `ab snapshot -i` trên trang blog aithetech.com | Khoảng 7.800 ký tự mỗi lần đọc |

Lệnh viết sẵn tiết kiệm token hơn nhiều so với để AI tự bấm từng bước. Đây là lý do bản mới giữ nguyên toàn bộ lệnh viết sẵn của bản cũ.

## Cài đặt và bảo trì

| Tiêu chí | browser-own-profile | agent-browser-own-profile |
|---|---|---|
| Phải cài | Python 3.11+, môi trường riêng 34 MB, browser-harness 0.1.13 qua pip | Python 3.11+, một file 19 MB tự tải và kiểm tra SHA-256 |
| Phần điều khiển Chrome tự viết | worker.py 592 dòng, client.py 164 dòng | engine.py dưới 200 dòng |
| Bên bảo trì phần điều khiển | Tự bảo trì | Vercel Labs (bản 0.42.0 phát hành 10/11/2026) |

## Giới hạn đã biết

- **Vẫn cần Python.** Bỏ hẳn Python đòi hỏi viết lại toàn bộ lệnh và bộ tách dữ liệu bằng ngôn ngữ khác.
- **`tiktok-post` và `instagram-post` chưa vận hành thử** trên bản này. `facebook-post` đã chạy tới bước xác nhận, chưa đăng thật.
- **`tiktok-comments` chưa vận hành thử**; khung bình luận trống với hồ sơ mới là do TikTok, không phụ thuộc công cụ.
- **macOS chưa vận hành thử** trên máy thật.
- **Hai công cụ không dùng chung hồ sơ cùng lúc.** Chrome của bản mới giữ mở 5 phút; cần `ab close` trước khi dùng bản cũ hoặc lệnh `login`.
- **agent-browser đang ở phiên bản 0.x**, giao diện lệnh có thể thay đổi giữa các bản. Repo cố định bản 0.42.0; nâng cấp phải cập nhật mã SHA-256 và chạy lại test.
