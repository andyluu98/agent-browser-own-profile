# 02. Chọn hồ sơ Chrome: Chrome riêng hay Chrome chính

Hồ sơ (profile) là một "người dùng" trong Chrome: chứa cookie, phiên đăng nhập, lịch sử truy cập.

| | Chrome riêng (mặc định) | Chrome chính (`--main`) |
|---|---|---|
| Thư mục | `%LOCALAPPDATA%\agent-browser-own-profile\chrome` | Hồ sơ Chrome dùng hằng ngày |
| Đăng nhập | Một lần bằng `login --site <trang>` | Đã có sẵn |
| Hỏi "Allow remote debugging?" | Không | Mỗi lần kết nối, người dùng bấm Allow |
| Tài khoản khác (Gmail, ngân hàng) | Không có trong hồ sơ này | Có, vì vậy Chrome bắt buộc hỏi Allow |
| Mức tin cậy của trang | Thấp hơn (hồ sơ mới) | Cao hơn (hồ sơ dùng lâu năm) |

Khuyến nghị: bắt đầu bằng Chrome riêng. Chỉ dùng `--main` khi trang chặn hồ sơ mới, ví dụ khung bình luận TikTok.

## Dùng lại hồ sơ của browser-own-profile

Đã đăng nhập sẵn bằng `browser-own-profile` thì không cần đăng nhập lại:

```bat
set ABOP_PROFILE=%LOCALAPPDATA%\browser-own-profile\chrome
run.bat check --site facebook
```

Hai công cụ không được dùng chung một hồ sơ cùng lúc: chạy `run.bat ab close` trước khi chuyển sang công cụ cũ.

## Bật cho phép với Chrome chính

Mở `chrome://inspect/#remote-debugging` trong Chrome và bật cho phép một lần. Từ Chrome 144, mỗi lần kết nối vào hồ sơ chính đều phải bấm Allow; không có cài đặt nào tắt được và bộ công cụ không lách bước này.
