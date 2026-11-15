# 13 - Ghi chú khoa học cho màn viễn thông Giai đoạn 1

Tài liệu này giải thích bằng lời thường cho người đọc không chuyên vì sao ba bước của màn mở đầu lại được dựng đúng như vậy. Mọi con số ở đây đều lấy từ `src/data/nasa/mars_comms_protocol.json`. Nếu một con số không có trong file đó thì nó không có trong tài liệu này.

---

## 1. Vì sao không phát thẳng từ mặt đất Sao Hỏa về Trái Đất

Trực giác đầu tiên của hầu hết người chơi là "có ăng-ten thì phát thẳng lên Trái Đất". Cách đó không dùng được, và lý do là ba khó khăn cộng dồn chứ không phải một.

**Khó khăn thứ nhất là công suất.** Một máy phát trên rover hay trên trạm Hab chỉ có vài chục oát điện. Tín hiệu vô tuyến yếu đi theo bình phương khoảng cách, nên qua 225 triệu km nó loãng tới mức gần như không còn. Để bù lại thì phải có ăng-ten thật lớn hoặc máy phát thật mạnh, mà cả hai đều không mang lên Sao Hỏa được.

**Khó khăn thứ hai là băng thông.** Vệ tinh MRO mang một ăng-ten độ lợi cao ba mét và một bộ khuếch đại 100 W. Nhờ vậy nó đẩy được 500 kbps về chảo DSN 34 m và 2,6 Mbps về chảo 70 m khi Sao Hỏa ở xa nhất, và tới 5,2 Mbps khi gần hơn. Một đường phát thẳng từ mặt đất yếu hơn con số đó hàng nghìn lần. Nói cách khác, vệ tinh không chỉ khoẻ hơn, nó khoẻ hơn theo cấp số nhân.

**Khó khăn thứ ba là khí quyển và bụi.** Băng UHF quanh 400 MHz xuyên qua bụi lơ lửng và khí quyển mỏng của Sao Hỏa tốt hơn băng X nhiều. Trong một đợt bụi dày, đây là khác biệt giữa "gói tin tới nơi" và "gói tin biến mất".

Ghép ba điều lại thì ra thiết kế hai chặng: thiết bị mặt đất phát UHF lên vệ tinh, vệ tinh phát X-band xuống Trái Đất. Chặng thứ nhất chịu được bụi và không cần ăng-ten lớn. Chặng thứ hai có ăng-ten lớn và nguồn điện dồi dào nên băng thông rộng. Không chặng nào làm được việc của chặng kia.

## 2. Vì sao là 850 W

Đây là con số của nhóm làm game, không phải số của NASA, và file dữ liệu ghi rõ như vậy. Mốc thật để so sánh là bộ phát UHF Electra trên MRO: nó chỉ ra 5 W sóng vô tuyến nhưng cần tới 71 W điện một chiều. Tầng khuếch đại công suất là phần hao điện nhất, và một trạm mặt đất còn phải nuôi thêm mô-tơ chĩa ăng-ten cùng sưởi ấm đế ăng-ten để nó không kẹt trong giá lạnh. 850 W là con số gộp cả ba thứ đó.

Bài toán điện được dựng như sau. Giàn pin danh định 5.200 W, nhưng bão bụi chỉ cho qua 35 phần trăm, tức còn 1.820 W khả dụng. Bật tất cả tám thiết bị trong trạm là 1.620 W, vẫn lọt. Nhưng bật thêm bộ phát 850 W thì tổng lên 2.470 W, vượt xa ngân sách.

Trong tám thiết bị, hai cái là thiết yếu: bơm oxy 260 W và sưởi chính 360 W, cộng 620 W. Tắt một trong hai là phi hành gia chết trong vài phút hoặc vài giờ. Sáu thiết bị còn lại cộng 1.000 W và đều tắt được. Để có 850 W cho bộ phát, tải không thiết yếu phải hạ xuống không quá 350 W, nghĩa là phải cắt ít nhất 650 W. Có nhiều cách cắt thoả điều kiện đó, từ việc chỉ giữ lại tủ lạnh mẫu 120 W cho tới tắt sạch cả sáu.

Điểm sư phạm nằm ở chỗ không có dòng "tổng công suất" nào hiện sẵn. Người chơi phải tự làm phép trừ, và phải nhận ra rằng 35 phần trăm không phải hiệu suất tấm pin mà là phần công suất còn lại sau khi bụi che trời.

## 3. Vì sao là 401,5 MHz

Băng UHF được định nghĩa là 300 MHz tới 3 GHz, nhưng trong thực tế liên lạc Sao Hỏa, "UHF" gần như luôn có nghĩa là dải hẹp 390 tới 450 MHz. Bộ phát Electra trên MRO hoạt động đúng trong dải này, và tần số đường về tiêu chuẩn dùng cho trung chuyển là 401,6 MHz.

Con số 401,5 MHz trong game lệch 0,1 MHz so với số thật. Đây là lựa chọn có chủ ý: nó nằm trong cùng băng, giữ được tính chân thực, nhưng tránh việc người chơi tra cứu thấy một số khác rồi tưởng game làm sai. File dữ liệu ghi rõ cả hai con số và ghi rõ cái nào là của NASA.

Vì sao dải này lại hợp với Sao Hỏa? Bước sóng ở 400 MHz là khoảng 75 cm. Ở bước sóng đó, hạt bụi cỡ vài mic-rô-mét gần như trong suốt với sóng, nên bụi không chặn được đường truyền. Ăng-ten cũng không cần lớn: một ăng-ten xoắn ốc cỡ chục xen-ti-mét là đủ. Đó là lý do rover và tàu đổ bộ đều dùng UHF để nói chuyện với vệ tinh, còn vệ tinh dùng X-band để nói chuyện với Trái Đất.

Thanh trượt tần số trong game chạy từ 399 tới 404 MHz, đỉnh ở 401,5. Lệch 2 MHz về phía nào cũng mất tín hiệu, và mô hình phạt theo bình phương sai lệch nên sai càng xa càng tệ nhanh.

## 4. Vì sao căn góc lại khó

Vệ tinh MRO bay ở quỹ đạo gần cực, độ cao 255 km ở cận điểm và 320 km ở viễn điểm, chu kỳ khoảng 112 phút. Nó chỉ ở trên đường chân trời của trạm Hab trong một cửa sổ ngắn, và trong game cửa sổ đó là 90 giây.

90 giây là con số của kịch bản, không phải của NASA: một lượt bay ngang thật kéo dài vài phút tới hơn mười phút tuỳ góc ngắm. Nhưng 90 giây tạo ra áp lực đúng ý đồ thiết kế, vì người chơi phải vừa nhìn đồng hồ vừa chỉnh hai thanh trượt.

Mô hình SNR trong game là một công thức đơn giản hoá, và file dữ liệu nói thẳng như vậy. Nó không phải link budget đầy đủ. Một link budget thật phải tính công suất phát, độ lợi hai ăng-ten, suy hao không gian tự do, tạp âm hệ thống, nhiệt độ tạp âm bầu trời và mặt đất. Ở đây chỉ giữ hai biến mà người chơi điều khiển được: góc ngắm và tần số.

Công thức: SNR bằng 24,0 dB trừ 0,35 nhân bình phương sai lệch góc tính bằng độ, trừ 2,60 nhân bình phương sai lệch tần số tính bằng MHz. Ngưỡng đạt là 15 dB. Vùng đạt vì thế là một hình elip: sai 5,1 độ về góc vẫn qua, và sai 1,86 MHz về tần số cũng vẫn qua, nhưng sai đồng thời cả hai thì trượt.

Vì sao góc cao lại tốt? Vì đường truyền xuyên qua ít khí quyển hơn. Ở góc 10 độ, tín hiệu phải đi qua một quãng khí quyển dài gấp gần sáu lần so với ở thiên đỉnh. Với khí quyển Sao Hỏa mỏng thì khác biệt này nhỏ, nhưng với bụi thì không nhỏ chút nào, và đó là lý do đỉnh của thanh trượt nằm ở 68 độ chứ không phải 90.

## 5. Vì sao chỉ có 16 byte

Đây là con số của kịch bản, không phải chuẩn NASA, và nó được chọn để dạy một bài học cụ thể: khi đường truyền là tài nguyên khan hiếm, bạn phải chọn cái gì đáng gửi.

Sáu gói tin trong game có tổng 29 byte, chia thành các cỡ 8, 7, 6, 3, 3 và 2 byte. Chọn ba gói mà tổng không quá 16 byte, và có đúng 14 tổ hợp thoả điều kiện trên 20 tổ hợp có thể. Con số 14 quan trọng: nó có nghĩa là không có một đáp án đúng duy nhất, nên người chơi buộc phải nghĩ về hậu quả chứ không thể thử cho tới khi qua.

Ba gói đắt nhất là toạ độ 8 byte, nhật ký bão 7 byte và sinh hiệu 6 byte. Tổng 21 byte, vượt trần, nên tổ hợp đó bất khả thi. Đây là bài học rõ nhất: ba gói giá trị cao nhất không thể đi cùng nhau. Chọn toạ độ thì phải bỏ hoặc nhật ký bão hoặc sinh hiệu, và cả hai đều đau theo cách khác nhau.

Ba gói rẻ nhất là dữ liệu đất 2 byte, lượng oxy 3 byte và áp suất 3 byte, tổng 8 byte. Rẻ, nhưng không có toạ độ thì đội cứu hộ chỉ biết bạn ở đâu đó trong một vùng rộng hàng trăm ki-lô-mét. Đây là cái bẫy ngược của bài toán: tiết kiệm dung lượng không phải mục tiêu, gửi đúng thứ mới là mục tiêu.

Chỉ có ba tổ hợp chạm đúng trần 16 byte, và mỗi tổ hợp trong số đó là một chiến lược khác nhau: toạ độ cộng sinh hiệu cộng dữ liệu đất (cứu người, bỏ khoa học), sinh hiệu cộng lượng oxy cộng nhật ký bão (cứu người, bỏ vị trí), và sinh hiệu cộng áp suất cộng nhật ký bão (chẩn đoán trạm, bỏ vị trí). Cả ba đều hợp lệ và cả ba đều có giá.

## 6. Vì sao cần ba trạm DSN cách nhau 120 độ

Deep Space Network có ba cơ sở: Goldstone ở California, Madrid ở Tây Ban Nha và Canberra ở Úc. Mỗi nơi có một chảo 70 m, và cả ba do JPL quản lý.

Ý tưởng đằng sau cách bố trí rất đơn giản: Trái Đất quay. Một ăng-ten ở California sẽ mất dấu Sao Hỏa khi Trái Đất quay đủ để Sao Hỏa lặn xuống dưới đường chân trời. Nếu chỉ có một trạm thì mỗi ngày sẽ có nhiều giờ không liên lạc được. Đặt ba trạm rải quanh vòng kinh tuyến thì lúc nào cũng có ít nhất một trạm nhìn thấy mục tiêu.

Ba kinh độ thật là 116,78 độ tây, 4,25 độ tây và 148,98 độ đông. Khoảng cách giữa chúng lần lượt là 112,5 độ, 153,2 độ và 95,0 độ, không đúng chính xác 120 độ như cách nói quen thuộc, nhưng đủ để luôn có trạm trực.

Một chi tiết dễ nhầm cần nói rõ: chảo 70 m của Madrid là **DSS-63**, không phải DSS-43. DSS-43 là chảo 70 m của Canberra, và nó là ăng-ten duy nhất còn liên lạc được với Voyager 2 vì tàu đó nằm xa dưới mặt phẳng hoàng đạo, chỉ thấy được từ Nam Bán Cầu. DSS-14 là chảo 70 m của Goldstone, khai trương năm 1966 và mở rộng lên 70 m năm 1988.

Trong màn chơi, người chơi chọn trạm nào đang có Sao Hỏa cao nhất trên trời. Với người chơi ở Việt Nam, Canberra thường là lựa chọn tốt vào nửa đầu buổi tối và Madrid vào nửa sau, còn Goldstone phục vụ nửa sau buổi tối giờ Thái Bình Dương.

## 7. Vì sao 12,5 phút là con số đáng sợ

Tín hiệu vô tuyến đi bằng tốc độ ánh sáng, 299.792,458 km mỗi giây. Không có cách nào nhanh hơn, không có công nghệ nào cải thiện được con số này. Đây là ràng buộc vật lý duy nhất trong cả màn chơi mà người chơi không thể vượt qua bằng cách chơi giỏi hơn.

Khoảng cách trung bình Trái Đất tới Sao Hỏa là khoảng 225 triệu km. Chia cho tốc độ ánh sáng ra 12,5 phút một chiều, 25,0 phút khứ hồi. Ở cấu hình gần nhất, khi hai hành tinh đối diện nhau, khoảng cách là 54,6 triệu km và trễ một chiều 3,0 phút. Ở cấu hình xa nhất, khi Sao Hỏa ở phía bên kia Mặt Trời, khoảng cách là 401 triệu km và trễ một chiều 22,3 phút.

Trong màn cầu cứu, con số 12,5 phút có nghĩa là sau khi bấm phát, người chơi phải chờ 12,5 phút mô phỏng mới biết gói tin có tới DSN hay không. Không có cách nào hỏi lại giữa chừng. Nếu gói tin sai, gói tin đã sai rồi, và lần thử tiếp theo phải chờ tới lượt bay ngang tiếp theo của vệ tinh, tức khoảng 112 phút nữa.

Đó là lý do ba bước của Giai đoạn 1 phải làm đúng ngay lần đầu: 850 W, 401,5 MHz, dưới 16 byte. Không phải vì game thích khó, mà vì ngoài đời thật cũng vậy.

## 8. Ba bước khoá vào nhau thế nào

Ba bước của Giai đoạn 1 không phải ba câu đố rời. Chúng chia sẻ một ràng buộc chung, và ràng buộc đó là lý do thứ tự lại quan trọng.

Bước một quyết định có điện hay không. Nếu người chơi tắt mất bơm oxy để dồn điện, họ qua được bước một nhưng thua cả màn, vì phi hành gia chết trước khi gói tin kịp tới Trái Đất. Đây là chỗ dễ sai nhất, vì về mặt số học thì tắt bơm oxy là cách nhanh nhất để có 850 W.

Bước hai quyết định gói tin có tới được vệ tinh hay không. Nếu SNR dưới 15 dB, không có gói tin nào đi tiếp, và bước ba trở nên vô nghĩa. Cửa sổ 90 giây cũng có nghĩa là người chơi không thể chỉnh chậm: chỉnh xong góc rồi mới chỉnh tần số là đã hết giờ.

Bước ba quyết định đội cứu hộ nhận được gì. Đây là bước duy nhất mà một lựa chọn tồi vẫn cho ra kết quả, chỉ là kết quả nghèo hơn. Chọn đúng dung lượng nhưng sai nội dung thì gói tin vẫn tới, vẫn được xác nhận, và vẫn không giúp được ai.

Xếp lại thì thứ tự ràng buộc là: điện trước, đường truyền sau, nội dung cuối. Sai ở bước trước thì bước sau không cứu được.

## 9. Ngân sách 16 byte dạy được gì mà lời giảng không dạy được

Một bài giảng về "tài nguyên hạn chế" thì ai cũng gật đầu. Nhưng khi người chơi thật sự phải bỏ gói toạ độ 8 byte để lấy hai gói nhỏ, họ cảm được cái giá.

Mười sáu byte là ngân sách của cả khung tin, và sáu gói tin trong game cộng lại chỉ 29 byte. So sánh cho dễ hình dung: một bức ảnh chụp từ điện thoại hiện nay nặng khoảng 3 triệu byte. Ngân sách của cả màn chơi nhỏ hơn một bức ảnh hàng trăm nghìn lần. Đó là mức độ khan hiếm mà kỹ sư viễn thông vũ trụ thật sự làm việc.

Bài học thứ hai là về ưu tiên. Toạ độ là gói đắt nhất và cũng là gói quyết định nhất, vì không có nó thì đội cứu hộ phải dò một vùng rộng hàng trăm ki-lô-mét bằng ảnh quỹ đạo, mất nhiều ngày. Nhưng nếu bỏ sinh hiệu, đội cứu hộ thậm chí không biết có nên phóng tàu hay không. Hai gói đó cộng lại đã 14 byte, chỉ còn 2 byte cho tất cả phần còn lại. Và 2 byte vừa đúng gói dữ liệu đất.

Đó là tổ hợp chạm trần: toạ độ, sinh hiệu, dữ liệu đất. Đúng 16 byte. Nó không phải đáp án duy nhất, nhưng nó là ví dụ rõ nhất cho việc ngân sách buộc phải có một logic, chứ không phải một danh sách mong muốn.

## 10. Điều gì trong màn này là thật và điều gì là của game

Cần phân biệt rõ để không ai nhầm một sản phẩm giải trí với một bản thiết kế sứ mệnh.

Thật, lấy từ NASA: MRO phóng năm 2005, quỹ đạo 255 tới 320 km, chu kỳ 112 phút, độ nghiêng 93 độ. Bộ phát Electra làm việc trong băng 390 tới 450 MHz, đường về tiêu chuẩn 401,6 MHz, ra 5 W sóng từ 71 W điện. Chặng X-band đạt 500 kbps tới chảo 34 m và 2,6 Mbps tới chảo 70 m. Ba trạm DSN ở Goldstone, Madrid và Canberra, với ba chảo 70 m là DSS-14, DSS-63 và DSS-43. Khoảng cách trung bình 225 triệu km và bảng trễ 3,0 / 12,5 / 22,3 phút.

Của game: 850 W cho bộ phát, giàn pin 5.200 W danh định, 35 phần trăm công suất còn lại, tau 1,4, nhiệt độ âm 25 độ C, gió 12 m/s, cửa sổ 90 giây, ngưỡng 15 dB, trần 16 byte, và công suất của tám thiết bị trong trạm.

Ranh giới này quan trọng vì nếu người chơi hỏi "số này ở đâu ra", câu trả lời phải có ngay trong file dữ liệu. Mỗi con số đều mang trường nguồn riêng, và trường đó nói thẳng đây là số của NASA hay số của nhóm làm game.

---

## Ghi chú về nguồn số liệu

Số thật của NASA trong tài liệu này: độ cao quỹ đạo MRO 255 tới 320 km, chu kỳ 112 phút, độ nghiêng 93 độ, phóng năm 2005, băng UHF 390 tới 450 MHz, tần số đường về 401,6 MHz, tốc độ xuống X-band 500 kbps tới 34 m và 2,6 Mbps tới 70 m, bộ phát Electra ra 5 W sóng và cần 71 W điện, ba trạm DSN cùng kinh độ và tên chảo 70 m, khoảng cách trung bình 225 triệu km, và bảng trễ 3,0 / 12,5 / 22,3 phút.

Số của kịch bản game: 850 W cho bộ phát, 35 phần trăm công suất pin, tau 1,4, cửa sổ 90 giây, ngưỡng SNR 15 dB, trần 16 byte, và toàn bộ công suất tiêu thụ của tám thiết bị trong trạm.
