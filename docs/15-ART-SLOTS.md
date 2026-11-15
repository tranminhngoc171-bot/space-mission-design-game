# Khe ảnh tay: cách thay tranh trong game

Tài liệu này cho agent của Ngọc (hoặc bất kỳ ai vẽ tay) biết cách thay
một tấm tranh trong game mà không cần sửa một dòng code nào.

## Quy tắc vàng

**Bỏ file vào đúng thư mục, đúng tên gốc, xong.**

Không cần sửa `art.js`, không cần đổi đuôi file, không cần báo trước.
Game tự nhận.

## Thư mục và tên

```
src/assets/art/
```

Mỗi khe có một tên gốc, ví dụ `bg-storm-wide`. Đặt file của bạn theo
đúng tên gốc đó, đuôi tự chọn:

```
bg-storm-wide.webp     (ưu tiên, nhẹ nhất)
bg-storm-wide.jpg      (được)
bg-storm-wide.png      (được)
bg-storm-wide.avif     (được)
```

Game mặc định nạp webp. Nếu file webp không tồn tại, nó tự thử jpg,
rồi png, rồi avif, theo thứ tự đó. Nhờ vậy bạn lưu ra định dạng nào
cũng chạy, và không cần đợi ai chuyển đổi giúp.

## Danh sách khe hiện có

### Màn mở đầu, 8 khung cảnh điện ảnh

| Tên gốc | Cảnh | Ảnh hiện tại |
|---|---|---|
| `bg-storm-wide` | Toàn cảnh bão cát, tường bụi cao ngất | AI gen |
| `bg-crew-running` | Đội chạy cúi rạp trong bão | AI gen |
| `bg-running-pov` | Góc nhìn thứ nhất, chạy, thấy đồng đội leo lên tàu | AI gen |
| `bg-face-closeup` | Cận mặt trong mũ, kính phản chiếu bão | AI gen |
| `bg-fall-buried` | Người té, cát đỏ phủ dần | AI gen |
| `bg-mars-orbit` | Toàn cảnh Sao Hỏa từ xa, tàu nhỏ bay ra | AI gen |
| `bg-waking-eyes` | Góc nhìn nằm ngửa, trần khoang mờ dần rõ | AI gen |
| `bg-entering-hab` | Góc nhìn thứ nhất đi vào cửa khoang | AI gen |

### Cảnh cũ màn kể chuyện

| Tên gốc | Cảnh |
|---|---|
| `mars-surface` | Đồng bằng đỏ Acidalia Planitia |
| `storm-coming` | Tường bão đang tới |
| `storm-impact` | Trong bão, mảnh ăng-ten văng |
| `departure` | Tàu rời bệ phóng trong quầng lửa |
| `awake` | Bên trong khoang, 5 giá đồ trống |

### Màn căn cứ

| Tên gốc | Cảnh |
|---|---|
| `bg-hab` | Mặt cắt khoang Hab ban ngày |
| `bg-farm` | Khu vườn kính |
| `bg-workbench` | Bàn kỹ thuật |
| `bg-radio` | Trạm radio |
| `bg-airlock` | Cửa khoang khí |

### Hồi tưởng gia đình (mở từ túi đồ)

| Tên gốc | Cảnh |
|---|---|
| `bg-houston-kitchen` | Bếp Houston đêm trước khi đi |
| `bg-moving-boxes` | Đóng thùng đồ |
| `bg-farewell-door` | Chia tay ở cửa |

## Kích thước và định dạng khuyến nghị

- Tỉ lệ 16:9, khuyến nghị 1600 x 900 hoặc 1920 x 1080
- Lưu webp chất lượng 80 tới 85 nếu có thể, mỗi file dưới 200 KB
- Nếu vẽ tay rồi chụp hoặc scan, xuất jpg chất lượng 85 cũng ổn
- Không cần nền trong suốt cho ảnh cảnh, đây là tranh phủ kín khung

## Icon thì khác

Icon vật phẩm (các file `icon-*.webp`) là ảnh nhỏ 128x128 cần nền
trong suốt, quy trình khác. Xem `scripts/gen-icon-sprite.py` để biết
đặc tả. Nếu muốn thay icon bằng tay, vẫn đặt đúng tên gốc vào
`src/assets/art/`, game tự nhận luôn.

## Sau khi thay

1. Đặt file vào `src/assets/art/` đúng tên gốc
2. Commit và push lên nhánh của bạn, mở PR
3. Sau khi merge vào main, tối đa 15 phút web sẽ có tranh mới
4. Nếu muốn xem ngay, mở tab Actions của repo `bersious/bersious-web`
   và bấm chạy tay workflow "Đồng bộ game từ repo chung"

## Nếu ảnh không hiện

Kiểm tra ba thứ theo thứ tự:

1. Tên file có đúng tên gốc không (chữ thường, gạch ngang, không dấu)
2. File có nằm trong `src/assets/art/` không
3. Mở trang web, bấm F12, xem tab Network: file của bạn trả về 200
   hay 404. Nếu 404 thì tên sai. Nếu 200 nhưng không hiện thì ảnh
   hỏng, thử mở file bằng trình xem ảnh.
