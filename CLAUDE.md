# CLAUDE.md: hướng dẫn cho Claude Code trong repo này

Người dùng repo này thường **không biết mở terminal**. Claude Code tự chạy mọi lệnh; người dùng chỉ đăng nhập trên Chrome và trả lời "có/không". Không bảo người dùng tự gõ lệnh, trừ khi Claude Code không chạy được lệnh đó.

Mọi lệnh chạy bằng `run.bat <lệnh>` trong thư mục repo (macOS: `./run.sh <lệnh>`). Kết quả nằm ở `%LOCALAPPDATA%\agent-browser-own-profile\output\`, nhật ký ở `...\logs\`. Có lỗi thì đọc nhật ký mới nhất trước khi đoán nguyên nhân.

## 1. Cài đặt

1. `run.bat setup` phải in "SẴN SÀNG".
2. Báo "CHƯA CÓ PYTHON 3.11+": hướng dẫn tải tại https://www.python.org/downloads/ (chọn "Add python.exe to PATH"), rồi chạy lại.
3. Thiếu Chrome: hướng dẫn cài Google Chrome.

Không cài Playwright, Puppeteer hay thư viện điều khiển trình duyệt nào khác khi chưa hỏi người dùng. Không đổi `VERSION` trong `abkit/install.py` khi chưa cập nhật mã SHA-256 tương ứng và chạy lại test.

## 2. Đăng nhập: chỉ trang nào việc cần

Chạy việc người dùng yêu cầu; nếu lệnh báo **"Trang yêu cầu đăng nhập"**:

1. `run.bat ab close` (đóng Chrome của công cụ nếu đang giữ mở), rồi `run.bat login --site <trang> --no-wait`.
2. Nói với người dùng: "Em đã mở Chrome trang <tên>. Anh/chị đăng nhập, xong thì **đóng hẳn cửa sổ Chrome đó** rồi báo em."
3. Người dùng báo xong thì chạy lại việc lúc nãy.

Công cụ tự mở Chrome riêng, **không bao giờ yêu cầu người dùng bật remote debugging hay bấm Allow** ở chế độ mặc định. Máy đã có hồ sơ đăng nhập của `browser-own-profile` thì công cụ tự dùng lại (lệnh `doctor` cho biết đang dùng hồ sơ nào). Hai công cụ không dùng chung một hồ sơ cùng lúc.

## 3. Yêu cầu thường gặp

| Người dùng nói | Lệnh |
|---|---|
| "Tìm 10 bàn phím bán chạy tầm 1 triệu trên Shopee" | `shopee --keyword "bàn phím" --min 800000 --max 1200000 --limit 10` |
| "Đọc bình luận video TikTok này <link>" | `tiktok-comments --url "<link>" --limit 30` (khung trống: báo người dùng; chỉ đề xuất `--main` khi họ chấp nhận bật remote debugging trên Chrome chính) |
| "Đăng video này lên TikTok, caption ..." | `tiktok-post --video "<đường dẫn tuyệt đối>" --caption "..."` |
| "Đăng bài Facebook: ..." | `facebook-post --text "..." [--image "<đường dẫn ảnh>"]` |
| "Mở thử trang X" | `check --site <trang>` |
| Trang chưa có lệnh viết sẵn | Thăm dò bằng `ab open <url>`, `ab snapshot -i`, `ab click @eN`; xem mục 4 |

**Đăng bài luôn cần người dùng đồng ý.** Lần chạy đầu không có `--yes`: lệnh đi tới nút Đăng, in "CẦN XÁC NHẬN" và không bấm. Hỏi người dùng trong chat, nêu rõ trang, nội dung, file. Người dùng đồng ý rõ ràng thì chạy lại **đúng lệnh đó** thêm `--yes`. Câu trả lời khác (im lặng, "để xem", "chắc vậy") là không. Không tự thêm `--yes`, không dùng một lần đồng ý cho bài khác.

## 4. Thăm dò trang mới bằng `ab`

`ab` gọi thẳng agent-browser trên cùng hồ sơ, không qua chốt an toàn của `abkit`. Vì vậy:

- Chỉ dùng để đọc và tìm đường đi. Trước khi bấm bất kỳ nút nào có nghĩa đăng, gửi, thích, theo dõi, mua, xóa: hỏi người dùng trong chat, nêu rõ nút và nội dung.
- Mỗi lần đọc trang tốn khoảng vài nghìn ký tự. Khi đã tìm ra các bước, đề xuất viết thành lệnh cố định trong `abkit/recipes.py` để lần sau không tốn token.
- Gặp captcha hoặc trang xác minh: dừng, báo người dùng.

## 5. Báo kết quả

- Trình bày thành bảng, kèm đường dẫn file CSV.
- Số "đã bán" của Shopee là nhãn làm tròn (8k+), không phải số chính xác.
- Có file `output\NN_...-raw.txt`: trang đã đổi bố cục; báo người dùng, sửa `abkit/parse.py` nếu được yêu cầu.

## 6. Ranh giới bắt buộc

- Lệnh báo **"DỪNG: Trang đang hỏi xác minh"**: dừng, báo người dùng. Không giải captcha, không chạy lại liên tục, không viết thêm code để né (giả chuột, giả dấu vân tay, đổi tài khoản).
- Không like hay comment hàng loạt; không tăng `LIMITS` trong `abkit/guard.py` khi chưa giải thích rủi ro.
- Không đọc, không gửi đi thư mục hồ sơ Chrome: nó chứa phiên đăng nhập.
- Không đưa thư mục `output\` lên GitHub công khai.

## 7. Kiểm thử sau khi sửa code

```bat
set PYTHONPATH=%CD%
python -m unittest discover -s tests
```

Phải đạt toàn bộ trước khi commit.
