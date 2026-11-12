---
name: agent-browser-own-profile
description: Điều khiển Chrome đã đăng nhập của người dùng qua agent-browser (Rust) để đăng video TikTok Studio, đăng bài Facebook kèm ảnh, đăng Instagram, đọc sản phẩm bán chạy Shopee, đọc bình luận một video TikTok, hoặc thăm dò một trang mới từng bước. Dùng khi người dùng gọi "agent-browser-own-profile", "abop", hoặc muốn tự động làm việc trên TikTok, Facebook, Shopee bằng tài khoản của chính họ. Hỏi trước khi đăng, dừng khi gặp captcha, không like hay comment hàng loạt.
---

# agent-browser-own-profile

## Chạy lệnh

Thư mục plugin là hai cấp trên thư mục của skill này. Gọi:

- Windows: `"<thư mục plugin>\run.bat" <lệnh> <tham số>`
- macOS: `"<thư mục plugin>/run.sh" <lệnh> <tham số>`

Lần đầu: chạy `setup`, phải in "SẴN SÀNG". Báo "CHƯA CÓ PYTHON 3.11+" thì hướng dẫn người dùng cài Python (chọn "Add python.exe to PATH") rồi chạy lại.

Kết quả và nhật ký nằm ở `%LOCALAPPDATA%\agent-browser-own-profile\` (macOS: `~/Library/Application Support/agent-browser-own-profile/`).

## Bảng lệnh

| Người dùng muốn | Lệnh |
|---|---|
| Đăng video lên TikTok | `tiktok-post --video "<đường dẫn tuyệt đối .mp4>" --caption "..."` |
| Đăng bài Facebook | `facebook-post --text "..." [--image "<đường dẫn ảnh>"]` |
| Đăng Instagram | `instagram-post --media "<đường dẫn>" --caption "..."` |
| Sản phẩm bán chạy Shopee | `shopee --keyword "..." [--min 800000 --max 1200000] --limit 10` |
| Bình luận một video TikTok | `tiktok-comments --url "<link>" --limit 30 [--main] [--an-ten]` |
| Thử mở một trang | `check --site <tiktok, tiktok-studio, facebook, instagram, shopee, google>` |
| Đăng nhập một trang | `ab close`, rồi `login --site <trang> --no-wait` |
| Trang chưa có lệnh sẵn | `ab open <url>`, `ab snapshot -i`, `ab click @eN`, `ab fill @eN "..."` |

Đường dẫn file luôn là đường dẫn tuyệt đối. Khoảng giá mơ hồ ("tầm 1 triệu"): tự chọn khoảng hợp lý và nói rõ.

## Quy trình

1. **Đăng nhập khi cần.** Lệnh báo "Trang yêu cầu đăng nhập": chạy `ab close` rồi `login --site <trang> --no-wait`, nhờ người dùng đăng nhập trong cửa sổ Chrome vừa mở và **đóng hẳn cửa sổ đó**, chờ họ báo xong, chạy lại việc lúc nãy.
2. **Đăng bài luôn hỏi người dùng.** Lần chạy đầu không có `--yes`: lệnh đi tới nút Đăng, in "CẦN XÁC NHẬN" và không bấm. Hỏi người dùng trong chat, nêu rõ trang, nội dung, file. Họ đồng ý rõ ràng thì chạy lại **đúng lệnh đó** thêm `--yes`. Không tự thêm `--yes`, không dùng một lần đồng ý cho bài khác.
3. **Thăm dò bằng `ab` không có chốt an toàn tự động.** Trước khi bấm nút đăng, gửi, thích, theo dõi, mua, xóa: hỏi người dùng. Tìm ra đường đi rồi thì đề xuất viết thành lệnh cố định để lần sau không tốn token.
4. **Báo kết quả** thành bảng, kèm đường dẫn file CSV hoặc nhật ký (dòng "Nhật ký: ..." cuối lệnh). Có lỗi thì đọc nhật ký trước khi đoán.

## Chọn Chrome

- Mặc định: Chrome riêng của bộ công cụ, giữ mở 5 phút sau mỗi lệnh để lệnh sau nhanh hơn.
- Người dùng đã có hồ sơ của `browser-own-profile`: đặt `ABOP_PROFILE=%LOCALAPPDATA%\browser-own-profile\chrome` để dùng lại phiên đăng nhập.
- `--main`: Chrome chính đang mở; người dùng bật `chrome://inspect/#remote-debugging` một lần và bấm Allow mỗi lần chạy. Cần cho đọc bình luận TikTok. Chỉ dùng khi người dùng đồng ý.

## Ranh giới bắt buộc

- Lệnh báo **"DỪNG: Trang đang hỏi xác minh"**: dừng và báo người dùng. Không giải captcha, không chạy lại liên tục, không viết code để né.
- Không like hay comment hàng loạt, mỗi lần chạy một bài. Không tăng `LIMITS` trong `abkit/guard.py` khi chưa giải thích rủi ro.
- Không đọc, không gửi đi thư mục hồ sơ Chrome (chứa phiên đăng nhập).
- Không cài Playwright, Puppeteer hay thư viện điều khiển trình duyệt khác khi chưa hỏi.
