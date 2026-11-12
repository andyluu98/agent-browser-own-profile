# 02. Hồ sơ Chrome: dùng Chrome riêng, không bật debug

Hồ sơ (profile) là một "người dùng" trong Chrome: chứa cookie, phiên đăng nhập, lịch sử truy cập.

## Mặc định: Chrome riêng, không phải bật gì

Công cụ tự mở một Chrome riêng với hồ sơ riêng. Người dùng **không cần bật remote debugging, không cần vào `chrome://inspect`, không cần bấm Allow**. Chrome chính dùng hằng ngày không bị đụng tới.

Công cụ chọn hồ sơ theo thứ tự:

1. Biến `ABOP_PROFILE` nếu có đặt.
2. Hồ sơ của chính công cụ (`%LOCALAPPDATA%\agent-browser-own-profile\chrome`) nếu đã từng dùng.
3. Hồ sơ đã đăng nhập của `browser-own-profile` (`%LOCALAPPDATA%\browser-own-profile\chrome`) nếu máy có. Người đã đăng nhập ở công cụ cũ không phải đăng nhập lại.
4. Không có hồ sơ nào: tạo hồ sơ mới, người dùng đăng nhập một lần bằng `login --site <trang>`.

Lệnh `doctor` in ra hồ sơ đang dùng.

## Vì sao không dùng thẳng hồ sơ Chrome chính

Từ Chrome 136, Chrome không cho công cụ điều khiển hồ sơ chính nếu người dùng chưa bật remote debugging và bấm Allow. Đây là quy tắc bảo mật của Chrome: hồ sơ chính chứa mọi tài khoản (Gmail, ngân hàng), nên Chrome bắt buộc người dùng xác nhận. Bộ công cụ không lách quy tắc này.

Cách chép hồ sơ chính ra một bản tạm (lệnh `--profile <tên>` của agent-browser) đã được thử ngày 12/11/2026: mất 29 giây để mở và bản chép không giữ được phiên đăng nhập Facebook. Vì vậy bộ công cụ không dùng cách này.

## `--main`: lựa chọn cuối

`--main` gắn vào Chrome chính đang mở. Chỉ dùng khi một trang chặn Chrome riêng (ví dụ khung bình luận TikTok trống) và người dùng chấp nhận:

1. Mở `chrome://inspect/#remote-debugging` trong Chrome chính, bật cho phép.
2. Mỗi lần chạy, bấm Allow khi Chrome hỏi.

## Lưu ý

- Hai công cụ không dùng chung một hồ sơ cùng lúc: chạy `run.bat ab close` trước khi dùng `browser-own-profile` hoặc lệnh `login`.
- Không chia sẻ thư mục hồ sơ: ai có thư mục này là có phiên đăng nhập của bạn.
