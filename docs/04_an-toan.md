# 04. An toàn: các chốt bộ công cụ tự áp dụng

| Chốt | Vị trí | Cơ chế |
|---|---|---|
| Dừng khi gặp captcha hoặc yêu cầu đăng nhập | `guard.check_page` | Mỗi lần đọc trang đều kiểm tra; thấy "Drag the slider", đường dẫn `/verify/`... thì dừng |
| Hỏi trước nút rủi ro | `guard.Kit.click` | Nút có chữ Post, Đăng, Like, Gửi, Mua, Xóa, Follow phải được xác nhận; chỉ "có" mới được tính là đồng ý |
| Đối chiếu tên nút lúc bấm | `engine.Browser.click` | Tên nút khác lúc đọc trang thì từ chối bấm |
| Giới hạn khối lượng | `guard.LIMITS` | Tối đa 20 sản phẩm, 50 bình luận, 4 vòng cuộn, 1 bài mỗi lần chạy |
| Ẩn dữ liệu nhạy cảm | `snapshot.js` | Mật khẩu, số thẻ, OTP, token không có trong dữ liệu đọc ra |
| Chỉ mở https | `engine.Browser.open` | Từ chối http, javascript:, ftp |
| Không để lại bài nháp | `guard.Kit.__exit__` | Lệnh bị dừng hoặc bị từ chối thì đóng hẳn Chrome |
| Bản agent-browser cố định | `install.py` | Tải đúng bản 0.42.0, đối chiếu SHA-256 với bản phát hành chính thức, sai thì bỏ |
| Tự đóng Chrome | `engine.KEEP_OPEN_MS` | Chrome giữ mở tối đa 5 phút không hoạt động rồi tự đóng |

## Lệnh `ab` không có các chốt trên

`ab` gọi thẳng agent-browser để thăm dò. Claude Code phải hỏi người dùng trước khi bấm nút đăng, gửi, mua, xóa qua đường này (quy định trong `CLAUDE.md` và `SKILL.md`).

## Người dùng cần tự bảo vệ

- **Không chia sẻ thư mục hồ sơ Chrome**: ai có thư mục này là có phiên đăng nhập của bạn.
- **Không đưa thư mục `output\`** lên GitHub công khai nếu có dữ liệu của người khác.
- Muốn nới giới hạn trong `LIMITS` thì đọc rủi ro ở [docs/03](03_vi-sao-bi-chan.md) trước.
