# 07. Kịch bản chạy Shopee

Lệnh `shopee` đọc danh sách sản phẩm bán chạy theo từ khóa và khoảng giá, lưu thành bảng CSV mở được bằng Excel. Lệnh chỉ đọc, không thêm vào giỏ, không mua, không nhắn tin cho shop.

Trạng thái ngày 12/11/2026: lệnh và bộ tách dữ liệu đã có, 3 test dữ liệu Shopee đạt. Chưa chạy được trên trang thật bằng bản này vì phiên đăng nhập Shopee trong hồ sơ thử đã hết hạn.

## Bước 1. Đăng nhập một lần

Shopee bắt buộc đăng nhập mới hiện trang tìm kiếm.

```bat
run.bat ab close
run.bat login --site shopee --no-wait
```

Đăng nhập trong cửa sổ Chrome vừa mở (mật khẩu, mã OTP do người dùng tự nhập), sau đó **đóng hẳn cửa sổ Chrome đó**. Khi phiên hết hạn, lệnh sẽ báo "Trang yêu cầu đăng nhập" và chỉ cần làm lại bước này.

## Bước 2. Kiểm tra

```bat
run.bat check --site shopee
```

Kết quả đạt: in ra tiêu đề trang Shopee và danh sách nút, ô nhập. Báo "Trang yêu cầu đăng nhập" thì làm lại bước 1.

## Bước 3. Chạy lệnh

| Mục đích | Lệnh |
|---|---|
| 10 bàn phím cơ bán chạy từ 800.000 đến 1.200.000 đồng | `run.bat shopee --keyword "bàn phím cơ" --min 800000 --max 1200000 --limit 10` |
| 20 tai nghe bluetooth bán chạy, không giới hạn giá | `run.bat shopee --keyword "tai nghe bluetooth" --limit 20` |
| 10 bình giữ nhiệt dưới 300.000 đồng | `run.bat shopee --keyword "bình giữ nhiệt" --max 300000 --limit 10` |

- Giá ghi bằng đồng, không có dấu chấm.
- Tối đa 20 sản phẩm mỗi lần (giới hạn trong `abkit/guard.py`), sắp xếp theo lượng bán của Shopee.
- Giữa hai lần tìm nên cách nhau vài phút; tìm dồn dập dễ bị Shopee hỏi xác minh.

Dùng qua Claude Code thì chỉ cần nói, ví dụ:

> Dùng agent-browser-own-profile tìm 10 bàn phím cơ bán chạy khoảng 1 triệu đồng trên Shopee.

## Bước 4. Đọc kết quả

Màn hình in từng dòng: giá, lượng bán, điểm đánh giá, tên sản phẩm. File CSV lưu tại `%LOCALAPPDATA%\agent-browser-own-profile\output\NN_shopee-<từ-khóa>.csv` với các cột:

| Cột | Ý nghĩa |
|---|---|
| `title` | Tên sản phẩm |
| `price` | Giá đang bán (đồng) |
| `original_price` | Giá gốc trước giảm, để trống nếu không giảm |
| `rating` | Điểm đánh giá như Shopee hiển thị (ví dụ `4.9`), để trống nếu chưa có |
| `sold` | Nhãn lượng bán như Shopee hiển thị (ví dụ "Đã bán 2,1k") |
| `location` | Nơi gửi hàng |

Lượng bán là con số Shopee làm tròn trên thẻ sản phẩm, không phải số liệu chính xác của shop.

## Khi có lỗi

| Hiện tượng | Cách xử lý |
|---|---|
| "Trang yêu cầu đăng nhập" | Làm lại bước 1 |
| "DỪNG: Trang đang hỏi xác minh" | Dừng, không chạy lại liên tục. Mở Shopee bằng tay trong Chrome riêng (`login --site shopee`), tự xác minh, để một thời gian rồi mới thử lại |
| "Không tách được dòng nào", có file `-raw.txt` | Shopee đã đổi bố cục thẻ sản phẩm. Gửi file raw cho người hướng dẫn để sửa mốc nhận diện trong `abkit/parse.py` |
| Ít sản phẩm hơn số yêu cầu | Trang chỉ hiện một phần kết quả khi mới mở; ghi nhận số dòng thực tế, không tự cộng thêm |
