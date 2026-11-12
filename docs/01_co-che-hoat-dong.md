# 01. Cơ chế hoạt động

## Ba cách để máy đọc một trang web

| Cách | Máy nhận được gì | Ưu điểm | Nhược điểm |
|---|---|---|---|
| Chụp màn hình | Một tấm ảnh, AI ước đoán vị trí nút | Dùng được với mọi phần mềm | Tốn token, chậm, có thể bấm lệch |
| **Đọc cấu trúc trang** (bộ công cụ này) | Danh sách ngắn dạng `e3 nút "Đăng"` | Ít token, nhanh, bấm đúng phần tử | Không nhận ra nút chỉ có biểu tượng mà không có tên |
| Kết hợp | Đọc cấu trúc, khi cần mới chụp ảnh | Linh hoạt | Phức tạp hơn |

Có thể hình dung trang web như một tòa nhà: chụp ảnh là đứng ngoài quan sát, đọc cấu trúc là cầm bản vẽ, biết chính xác cửa nào ở đâu và cửa nào đang khóa.

## Ba lớp của bộ công cụ

| Lớp | File | Vai trò |
|---|---|---|
| Lệnh viết sẵn | `abkit/recipes.py`, `abkit/parse.py` | Các bước cố định cho TikTok, Facebook, Shopee, Instagram; tách dữ liệu thành bảng |
| Chốt an toàn | `abkit/guard.py` | Dừng khi gặp captcha, hỏi trước nút rủi ro, giới hạn khối lượng, ghi nhật ký |
| Điều khiển Chrome | `abkit/engine.py`, `abkit/snapshot.js` | Gọi agent-browser để mở trang, đọc, bấm, điền, tải file |

## Các bước của một lệnh

1. **Khởi động.** Lệnh đầu tiên gọi agent-browser kèm hồ sơ Chrome riêng. agent-browser mở Chrome và giữ một tiến trình nền; các lệnh sau trong 5 phút dùng lại Chrome đó.
2. **Đọc trang.** `snapshot.js` chạy trong trang, gắn mã `e1`, `e2`... cho nút và ô nhập, trả về tối đa 150 phần tử và 4.000 ký tự chữ. Mật khẩu, số thẻ, mã OTP, token không bao giờ có trong kết quả.
3. **Chọn.** Lệnh viết sẵn (hoặc AI) chỉ được chọn một mã trong danh sách, không tự viết JavaScript chạy trong trang.
4. **Đối chiếu trước khi bấm.** Công cụ đọc lại tên nút ngay trước khi bấm. Nếu trang vừa đổi "Tiếp" thành "Đăng", công cụ từ chối bấm.
5. **Bấm.** agent-browser cuộn tới phần tử và bấm như người dùng; nếu phần tử bị che hoặc bị khóa, lệnh báo lỗi thay vì báo thành công giả.

## Vì sao vẫn giữ lệnh viết sẵn

agent-browser cho phép AI tự bấm từng bước, nhưng mỗi lần đọc trang tốn vài nghìn ký tự. Một lệnh viết sẵn như `tiktok-post` chỉ trả về vài dòng kết quả. Cách làm khuyến nghị: dùng `ab` để thăm dò trang mới, sau đó chuyển các bước tìm được thành lệnh cố định.
