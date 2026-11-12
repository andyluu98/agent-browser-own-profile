# agent-browser-own-profile

Bộ công cụ điều khiển **Chrome đã đăng nhập của chính bạn** bằng Claude Code: đọc sản phẩm bán chạy trên Shopee, đọc bình luận một video TikTok, đăng video lên TikTok Studio, đăng bài Facebook kèm ảnh. Phần điều khiển trình duyệt dùng [agent-browser](https://github.com/vercel-labs/agent-browser) (Rust, Vercel Labs, giấy phép Apache-2.0); phần quy trình, chốt an toàn và tài liệu tiếng Việt kế thừa từ `browser-own-profile`.

Bộ công cụ **không lách** cơ chế chống bot. Bộ công cụ hoạt động được vì dùng hồ sơ Chrome đã đăng nhập và thao tác với khối lượng nhỏ như người dùng thật. Khi trang hiển thị captcha, bộ công cụ dừng lại và thông báo, không giải hộ. Xem [docs/03](docs/03_vi-sao-bi-chan.md).

## Điểm khác so với browser-own-profile

| Tiêu chí | browser-own-profile | agent-browser-own-profile |
|---|---|---|
| Cần cài | Python 3.11+, môi trường riêng 34 MB, thư viện browser-harness | Python 3.11+ (chỉ thư viện chuẩn) và một file agent-browser 19 MB tự tải lần đầu |
| Mã nguồn tự bảo trì cho phần điều khiển Chrome | Khoảng 760 dòng (worker.py, client.py) | Dưới 200 dòng (engine.py) |
| Chrome giữa các lệnh | Mở mới mỗi lệnh | Giữ mở 5 phút, lệnh sau nhanh hơn |
| Kiểm tra file tải về | Không áp dụng | Đối chiếu SHA-256 với bản phát hành chính thức |
| Thăm dò trang mới | Không có | Lệnh `ab` gọi trực tiếp agent-browser trên cùng hồ sơ |

Số đo cụ thể và các giới hạn đã biết: [docs/06](docs/06_so-sanh-va-gioi-han.md).

## Cài đặt làm plugin Claude Code

```
/plugin marketplace add andyluu98/agent-browser-own-profile
/plugin install agent-browser-own-profile@agent-browser-own-profile
```

Khởi động lại Claude Code, sau đó yêu cầu bằng lời ở bất kỳ phiên làm việc nào, ví dụ:

> Dùng agent-browser-own-profile tìm 10 bàn phím cơ bán chạy khoảng 1 triệu đồng trên Shopee.

Lần chạy đầu, công cụ tự tải agent-browser vào `%LOCALAPPDATA%\agent-browser-own-profile\` (macOS: `~/Library/Application Support/agent-browser-own-profile/`). Thư mục này giữ hồ sơ Chrome, kết quả và nhật ký; cập nhật plugin không làm mất dữ liệu.

Repo đang ở chế độ riêng tư: học viên cần được mời vào repo trên GitHub thì lệnh cài đặt mới tải được.

## Yêu cầu máy

- Windows 10/11 x64 hoặc macOS (bản macOS chưa được vận hành thử trên máy thật).
- Google Chrome.
- Python 3.11 trở lên, khi cài trên Windows chọn "Add python.exe to PATH". Không cần cài thêm thư viện.

## Các lệnh

Gọi qua `run.bat` (Windows) hoặc `run.sh` (macOS). Thông thường Claude Code tự chạy các lệnh này.

| Lệnh | Chức năng |
|---|---|
| `setup` | Tải agent-browser bản cố định, kiểm tra mã SHA-256, in "SẴN SÀNG" |
| `doctor` | Kiểm tra Python, Chrome, agent-browser, hồ sơ Chrome |
| `login --site <trang> --no-wait` | Mở Chrome riêng để người dùng tự đăng nhập |
| `check --site <trang>` | Mở trang, liệt kê các nút và ô nhập công cụ nhận diện được |
| `shopee --keyword ... --min ... --max ... --limit 10` | Sản phẩm bán chạy, tối đa 20 |
| `tiktok-comments --url <link> --limit 30 [--an-ten]` | Bình luận một video, tối đa 50 |
| `tiktok-post --video <file.mp4> --caption "..."` | Đăng video qua TikTok Studio, **hỏi trước khi bấm Post** |
| `facebook-post --text "..." [--image <ảnh>]` | Đăng bài Facebook, **hỏi trước khi bấm Đăng** |
| `instagram-post --media <file> --caption "..."` | Đăng Instagram, **hỏi trước khi bấm Chia sẻ** |
| `ab <lệnh agent-browser>` | Thăm dò một trang mới từng bước trên cùng hồ sơ, ví dụ `ab snapshot -i` |

Các trang có sẵn: `tiktok`, `tiktok-studio`, `facebook`, `instagram`, `threads`, `shopee`, `google` (khai báo trong `abkit/sites.json`).

Mặc định công cụ tự mở Chrome riêng với hồ sơ đã đăng nhập: **không cần bật remote debugging, không cần bấm Allow**. Máy đã có hồ sơ của `browser-own-profile` thì công cụ tự dùng lại hồ sơ đó. Tùy chọn `--headless` chạy ngầm không hiện cửa sổ. Tùy chọn `--main` (Chrome chính) chỉ dùng khi thật cần, xem [docs/02](docs/02_chon-profile.md).

## Kết quả và nhật ký

- Bảng kết quả lưu tại `output\NN_ten.csv`, mở được bằng Excel.
- Mỗi lần chạy ghi một file trong `logs\`: mở trang nào, bấm nút nào, đọc bao nhiêu ký tự. Nội dung đã điền không được ghi lại.

## Tài liệu

1. [Cơ chế hoạt động](docs/01_co-che-hoat-dong.md)
2. [Chọn hồ sơ Chrome](docs/02_chon-profile.md)
3. [Vì sao bị chặn](docs/03_vi-sao-bi-chan.md)
4. [An toàn](docs/04_an-toan.md)
5. [Xử lý lỗi](docs/05_xu-ly-loi.md)
6. [So sánh với bản cũ và giới hạn đã biết](docs/06_so-sanh-va-gioi-han.md)

## Kiểm thử

```bat
cd /d <thư mục repo>
set PYTHONPATH=%CD%
python -m unittest discover -s tests
```

18 test: 14 test chốt an toàn và bộ tách dữ liệu, 4 test chạy Chrome ẩn trên các trang mẫu trong máy (không truy cập mạng).
