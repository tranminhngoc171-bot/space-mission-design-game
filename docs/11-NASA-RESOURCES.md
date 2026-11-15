# 11 - NASA Resources: Space Mission Design Game (NASA Space Apps Challenge 2026)

Tài liệu này ghi lại kết quả mở và đọc trực tiếp từng resource trên trang đề bài, không dựa vào mô tả tóm tắt trên trang danh sách. Mọi con số trong tài liệu đều trích từ trang gốc hoặc từ file PDF đã tải về và bóc text.

- Trang đề bài (tab Details): https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/
- Trang resource (tab Resources): https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/?tab=resources
- Ngày truy cập và trích xuất: 15/11/2026
- Phương pháp: mở bằng trình duyệt thật, đọc `document.body.innerText` của từng tab, bấm từng link, tải PDF về và chạy `pdftotext -layout` để đọc toàn văn. Với hai trang bị chặn khi mở bằng trình duyệt (Cloudflare với SourceForge, timeout với trang CSA), đã dùng `curl` kèm User-Agent để lấy HTML gốc và bóc text bằng Python.

---

## PHẦN 1 - MÔ TẢ ĐỀ BÀI ĐẦY ĐỦ

### 1.1 Thông tin chung của đề

| Trường | Giá trị |
|---|---|
| Tên đề | Space Mission Design Game |
| Sự kiện | 2026 NASA Space Apps Challenge |
| Thời gian hackathon | 14-15/11/2026 |
| Độ khó (Difficulty) | Intermediate, Beginner/Youth |
| Chủ đề (Subjects) | Games |
| Tab trên trang | Details, Resources, Teams |

### 1.2 Đoạn mô tả ngắn (challenge statement)

Thiết kế một sứ mệnh không gian đòi hỏi phải cân nhắc nhiều yêu cầu mâu thuẫn nhau, gồm mục tiêu khoa học, thiết kế tàu vũ trụ, thiết bị khoa học, phương tiện phóng, ngân sách, nguồn điện, khối lượng, liên lạc và các ràng buộc quỹ đạo. Với sinh viên, những đánh đổi này thường chỉ nằm trên giấy. Đề bài yêu cầu tạo ra một game tương tác, cho phép người chơi thiết kế, quản lý và mô phỏng một sứ mệnh không gian hoàn chỉnh, trong khi đưa ra các quyết định kỹ thuật, quản lý nguồn lực hữu hạn, và đánh giá được mỗi lựa chọn ảnh hưởng thế nào tới thành công của sứ mệnh.

### 1.3 Bối cảnh (Background), tóm đủ ý

Sứ mệnh không gian là hệ thống phức tạp, trong đó mục tiêu khoa học, yêu cầu kỹ thuật, nguồn lực sẵn có và ràng buộc vận hành phải khớp với nhau. Thiết kế sứ mệnh bao gồm quyết định về tàu, thiết bị khoa học, phương tiện phóng, quỹ đạo, nguồn điện, khối lượng, liên lạc, ngân sách và thời gian sống của sứ mệnh. Một quyết định cải thiện mặt này có thể tạo giới hạn ở mặt khác. Ví dụ được nêu nguyên văn: thêm một thiết bị mạnh hơn có thể tăng giá trị khoa học nhưng đồng thời tăng khối lượng, công suất tiêu thụ, khối lượng dữ liệu và chi phí.

Vấn đề giáo dục được nêu rõ: học thiết kế sứ mệnh hiện nay thường bị giới hạn ở bài tập lý thuyết, vì người học hiếm khi có môi trường để thử nghiệm cả một sứ mệnh từ khái niệm tới vận hành. Các công cụ hiện có thường chỉ tập trung vào một mảng riêng như cơ học quỹ đạo, thiết kế tàu, hoặc phóng tên lửa, mà không cho thấy các mảng đó tương tác ra sao trong một hệ thống hoàn chỉnh. Game tương tác được đề xuất như cách lấp khoảng trống đó: cho phép thử, ra quyết định, gặp ràng buộc, và học từ cả sứ mệnh thành công lẫn thất bại.

Người chơi có thể thiết kế cá nhân hoặc cộng tác theo nhóm tối đa bốn người, mỗi người đóng góp vào chiến lược chung. Các hướng tiếp cận được gợi ý: lập kế hoạch sứ mệnh, cấu hình tàu, chọn thiết bị, quản lý nguồn lực, chọn quỹ đạo, lập kế hoạch phóng, liên lạc, và mô phỏng sứ mệnh.

### 1.4 Mục tiêu (Objectives), nguyên văn rút gọn

Tạo một Space Mission Design Game tương tác, cho người chơi trải nghiệm quá trình thiết kế và quản lý một sứ mệnh không gian hoàn chỉnh. Có thể cho người chơi tham gia cá nhân hoặc cộng tác với nhóm tối đa bốn người, cùng ra quyết định chiến lược và đạt hiệu suất sứ mệnh cao nhất có thể.

Game có thể cho phép người chơi: định nghĩa mục tiêu sứ mệnh, thiết lập yêu cầu sứ mệnh, thiết kế tàu vũ trụ, chọn thiết bị khoa học, chọn phương tiện phóng và quỹ đạo, và quản lý các ràng buộc then chốt gồm ngân sách, khối lượng, nguồn điện, liên lạc, dữ liệu và thời gian sống của sứ mệnh.

### 1.5 Sản phẩm mà một giải pháp mạnh nên có

Đề bài dùng câu điều kiện "A strong solution might include", nghĩa là đây là kỳ vọng chứ không phải danh sách bắt buộc cứng. Nội dung gồm:

1. Một game hoặc mô phỏng tương tác, chạy được, có giao diện người dùng rõ ràng.
2. Hệ thống cấu hình sứ mệnh (mission configuration system).
3. Cơ chế quản lý nguồn lực (resource management mechanisms).
4. Chức năng cộng tác hoặc nhiều người chơi cho tối đa bốn người.
5. Hệ thống mô phỏng và đánh giá sứ mệnh.

Game có thể đưa ra phản hồi về hiệu suất sứ mệnh và thưởng cho các quyết định kỹ thuật hiệu quả, quản lý nguồn lực tiết kiệm, cộng tác thành công và đạt được mục tiêu sứ mệnh. Người dự thi được khuyến khích sáng tạo cơ chế game, trực quan hóa, hệ thống tính điểm và kịch bản sứ mệnh.

### 1.6 Các cân nhắc tiềm năng (Potential Considerations), liệt kê đầy đủ

Phần này mở đầu bằng câu "You may (but are not required to) consider the following", tức là hoàn toàn tùy chọn.

**Thiết kế game và trải nghiệm**
- Game có thể tiếp cận được với người chơi ở nhiều mức hiểu biết khác nhau về khoa học và kỹ thuật không gian.
- Game có thể hỗ trợ cả chơi đơn và chơi nhóm, cho tối đa bốn người cùng làm một sứ mệnh.
- Thành viên nhóm có thể có trách nhiệm khác nhau: lập kế hoạch sứ mệnh, thiết kế tàu, khoa học, liên lạc, hoặc quản lý nguồn lực.
- Mục tiêu rõ ràng và phản hồi rõ ràng giúp người chơi hiểu vì sao sứ mệnh thành công hay thất bại.
- Nên cho game tương tác, để người chơi sửa thiết kế và mô phỏng lại nhiều lần.
- Hệ thống tính điểm có thể thưởng cho thành công sứ mệnh, giá trị khoa học, hiệu quả dùng nguồn lực, và ra quyết định tốt.
- Game có thể có nhiều mức độ khó, nhiều loại sứ mệnh, hoặc nhiều kịch bản khác nhau.

**Thiết kế sứ mệnh**
- Người chơi có thể bắt đầu bằng việc định nghĩa mục tiêu sứ mệnh trước khi ra các quyết định về tàu và kỹ thuật.
- Nên cho mỗi quyết định thiết kế lớn đều có hệ quả. Ví dụ được nêu: tăng số thiết bị làm tăng năng lực khoa học nhưng cũng tăng khối lượng, công suất, chi phí và lượng dữ liệu sinh ra.
- Nên thể hiện rằng hiếm khi có một nghiệm hoàn hảo duy nhất. Các tổ hợp tàu, thiết bị, quỹ đạo và phương tiện phóng khác nhau có thể cùng đạt một mục tiêu.
- Nên có các ràng buộc thực tế như ngân sách hữu hạn, khối lượng tàu, công suất khả dụng, dung lượng liên lạc và thời gian sống của sứ mệnh.

**Tàu vũ trụ và payload**
- Tàu có thể gồm các thành phần: kết cấu (structure), hệ nguồn điện (power systems), pin (batteries), liên lạc (communications), máy tính trên tàu (onboard computers), điều khiển tư thế (attitude control), và thiết bị khoa học.
- Thiết bị khoa học có thể có các đặc tính khác nhau: khối lượng, công suất tiêu thụ, chi phí, lượng dữ liệu sinh ra, và giá trị khoa học.
- Nên cho người chơi chọn giữa linh kiện đơn giản và linh kiện tiên tiến tùy theo độ khó.

**Quỹ đạo và phóng**
- Game có thể cung cấp nhiều lựa chọn quỹ đạo và giải thích đặc điểm cơ bản của từng loại.
- Người chơi có thể xét quỹ đạo ảnh hưởng thế nào tới vùng phủ (coverage), cơ hội quan sát, liên lạc, thời gian sống và các yêu cầu khác.
- Phương tiện phóng có thể khác nhau về sức chở payload, chi phí và khả năng đạt quỹ đạo.
- Nên có bước kiểm tra rằng khối lượng tàu và quỹ đạo đã chọn tương thích với phương tiện phóng.

**Quản lý nguồn lực**
Game nên hiển thị rõ các nguồn lực chính. Các nguồn lực quan trọng được nêu nguyên văn:
- Mass: tổng khối lượng tàu và payload.
- Power: năng lượng khả dụng để vận hành hệ thống tàu và thiết bị.
- Budget: nguồn tiền để phát triển và vận hành sứ mệnh.
- Data: lượng thông tin do thiết bị khoa học sinh ra.
- Communications: khả năng truyền dữ liệu về trạm mặt đất.
- Time: thời gian phát triển và thời gian vận hành dự kiến của sứ mệnh.

Có thể xác định nguồn lực nào là then chốt nhất cho từng sứ mệnh cụ thể.

**Cộng tác**
- Ở chế độ nhóm, tối đa bốn người cùng làm một sứ mệnh.
- Nên cho mỗi thành viên vai trò riêng nhưng vẫn phải quyết định tập thể.
- Game có thể có tình huống buộc các thành viên thương lượng giữa các ưu tiên xung đột.
- Kết quả cuối cùng có thể phụ thuộc vào mức độ phối hợp của nhóm.

**Giá trị giáo dục**
- Khái niệm khoa học và kỹ thuật nên được giải thích bằng từ ngữ đơn giản, không giả định người chơi có kiến thức nâng cao.
- Các khái niệm phức tạp như độ cao quỹ đạo, sức chở payload, công suất tiêu thụ, tốc độ dữ liệu và liên lạc nên được giới thiệu ngay trong game.
- Nên có giải thích ngắn, hướng dẫn, chỉ báo trực quan, hoặc tài liệu học tập tùy chọn.
- Nên dạy vì sao một quyết định ảnh hưởng tới hiệu suất sứ mệnh, chứ không chỉ báo đúng hay sai.

**Danh sách tính năng có thể thêm (nguyên văn)**
- Nhiều kịch bản sứ mệnh với mục tiêu khác nhau.
- Sự kiện ngẫu nhiên hoặc ràng buộc bất ngờ.
- Nhiều mức độ khó.
- Mô hình tàu thực tế hoặc đơn giản hóa.
- Trực quan hóa tàu vũ trụ tương tác.
- Bảng điều khiển sứ mệnh hiển thị mức tiêu thụ nguồn lực theo thời gian thực.
- Bảng xếp hạng hoặc xếp hạng sứ mệnh.
- Báo cáo sứ mệnh tạo ra cuối mỗi lần mô phỏng.
- Khả năng lưu, chia sẻ và so sánh thiết kế sứ mệnh.
- Sứ mệnh hợp tác cho nhóm tối đa bốn người.
- Kịch bản cạnh tranh, nơi các nhóm khác nhau thiết kế cho cùng một mục tiêu.
- Chế độ sandbox cho phép thử nghiệm không bị ràng buộc định trước.
- Phân tích sau sứ mệnh (post-mission analysis) giải thích vì sao thành công hoặc thất bại.

Câu kết của đề: "For data and resources related to this challenge, refer to the Resources tab at the top of the page. More resources may be added before the hackathon begins."

### 1.7 Yêu cầu nộp bài (lấy từ Project Submission Guide, áp dụng chung cho mọi đề)

Đây là phần quan trọng nhất về mặt thủ tục, và không nằm trên trang đề bài mà nằm ở resource toàn cục. Nguồn: https://www.spaceappschallenge.org/resources/project-submission-guide/

- Cổng nộp bài mở Thứ Bảy 14/11/2026 lúc 9:00 sáng theo múi giờ của Local Event, đóng Chủ nhật 15/11/2026 lúc 11:59 tối cùng múi giờ. Nộp muộn không được chấm.
- Phải bấm nút "Submit for Judging". Chỉ bản lưu cuối cùng được chấm.
- Trang nộp bài cho phép ảnh JPG, PNG, GIF tối đa 10MB. Không cho tải video hay tài liệu lên. Video và tài liệu phải để ở dịch vụ ngoài (YouTube, Google Drive, GitHub, OneDrive, Dropbox) với link công khai, không cần đăng nhập.
- Các trường bắt buộc trên form: Project Name; High-Level Project Summary; Link to Project Demo; Link to Final Project; Detailed Project Description; Use of Super Intelligence; NASA Data; Space Agency Partner Data and Other References.
- Trường "NASA Data" ghi rõ: để đủ điều kiện xét Global Award, phải dùng ít nhất một dữ liệu hoặc resource của NASA.
- Demo bắt buộc: video tối đa 30 giây, hoặc slide deck tối đa 7 slide tính cả slide tiêu đề và giới thiệu. Vượt giới hạn thì không đủ điều kiện vào Global Judging.
- Toàn bộ nội dung trên trang nộp bài và tài liệu đính kèm phải bằng tiếng Anh. Nếu làm video thì được nói ngôn ngữ khác nhưng bắt buộc có phụ đề tiếng Anh. Slide deck phải bằng tiếng Anh.
- Nhóm Local Event cần ít nhất 1 người, nhóm Universal Event cần ít nhất 2 người, tối đa 6 thành viên. Mọi thành viên phải đăng ký cùng một Local Event.
- Phải khai báo mọi tài nguyên bên ngoài đã dùng (code, văn bản, hình ảnh) trong mục References, kể cả open source.
- Quy định về Super Intelligence (SI): được phép dùng, nhưng phải ghi rõ dùng ở đâu và thế nào. Hình ảnh và video do SI tạo phải có watermark nhìn thấy được. Âm thanh, code và dữ liệu do SI tạo phải ghi chú trong mô tả và metadata. Nội dung do SI tạo không được chứa hoặc chỉnh sửa các yếu tố thương hiệu NASA như logo, cờ, hoặc mission identifier.

---

## PHẦN 2 - TIÊU CHÍ CHẤM ĐIỂM

Trang đề bài "Space Mission Design Game" không có mục judging criteria. Tiêu chí chấm điểm nằm trong Judging & Awards Guide của sự kiện. Nguồn: https://www.spaceappschallenge.org/resources/judging-awards-guide/

### 2.1 Thang điểm

Mọi cấp chấm, từ Local và Universal Event tới Executive Judging, đều chấm theo thang 1 tới 5 trên năm tiêu chí. Điểm 5 là mức cao nhất và mỗi tiêu chí có mô tả riêng cho mức 5.

### 2.2 Năm tiêu chí, nguyên văn và diễn giải

**Impact (Tác động)**
Mô tả: dự án tạo tác động bằng cách giải quyết một vấn đề nhỏ hoặc lớn, ảnh hưởng tới chất lượng và số lượng của hiệu ứng tổng thể. Mức độ truyền cảm hứng hoặc giúp ích cho người khác thay đổi từ phạm vi rất rộng tới một nhóm nhỏ.
Mức 5: dự án thể hiện tác động đặc biệt, giải quyết một vấn đề có ý nghĩa bằng giải pháp đề xuất. Phạm vi rộng, truyền cảm hứng, mang lại lợi ích cho nhiều người, hoặc có thể thay đổi thế giới. Chất lượng và hiệu quả vượt xa kỳ vọng.

**Creativity (Sáng tạo)**
Mô tả: dự án thể hiện tính nguyên bản và đổi mới, giới thiệu một khái niệm chưa từng có, hoặc cải tiến có ý nghĩa trên ý tưởng đã có. Dự án nổi bật nhờ mức sáng tạo, góc nhìn mới hoặc cách thực thi độc đáo.
Mức 5: cách tiếp cận đột phá chưa từng được thử, thách thức phương pháp thông thường, giải pháp nguyên bản và nổi bật trong lĩnh vực.

**Validity (Tính hợp lệ, tính khả thi)**
Mô tả: giải pháp dựa trên nguyên lý khoa học và chứng minh được tính khả thi về kỹ thuật, chức năng hoặc logic. Được thiết kế để đạt mục đích và có tiềm năng hoạt động trong ứng dụng thực tế. Mức độ hoàn thiện có thể khác nhau, có thể đã phát triển đầy đủ hoặc còn cần tinh chỉnh nhiều. Tính dễ dùng và thân thiện với người dùng cũng ảnh hưởng tới tính thực tiễn.
Mức 5: giải pháp hợp lý về khoa học và khả thi về kỹ thuật, gắn chặt với các nguyên lý đã được thiết lập. Phát triển đầy đủ, sẵn sàng cho triển khai thực tế, rất dễ dùng.

**Relevance (Mức liên quan, mức dùng dữ liệu NASA)**
Mô tả: dự án giải quyết đầy đủ và trực tiếp đề bài đã chọn, gắn chặt với mục tiêu dự kiến. Tích hợp dữ liệu NASA một cách có ý nghĩa, dùng dữ liệu như thành phần cốt lõi chứ không phải phần thêm bề mặt. Độ sâu của việc dùng dữ liệu làm tăng độ tin cậy và hiệu quả của dự án.
Mức 5: dự án gắn sâu với đề bài, dữ liệu NASA là phần thiết yếu tạo nên thành công của dự án, việc dùng dữ liệu được thực hiện tốt.

**Presentation (Trình bày)**
Mô tả: nhóm truyền đạt dự án hiệu quả, làm rõ đề bài, giải pháp đề xuất và ý nghĩa của nó. Cách kể chuyện hấp dẫn và có cấu trúc, giúp người nghe hiểu mục đích và tác động. Độ rõ ràng, tổ chức và cách trình bày đóng vai trò then chốt. Giám khảo chấm điểm này dựa trên cả demo và toàn bộ dự án.
Mức 5: trình bày có cấu trúc tốt và thuyết phục, trình bày chỉn chu, hiệu quả cao trong việc truyền đạt ý tưởng.

Guide có một ghi chú quan trọng: nhiều nhóm chăm chút bốn tiêu chí đầu mà bỏ qua tiêu chí thứ năm, nên dành thời gian và nguồn lực xây dựng bài pitch và câu chuyện quanh dự án.

### 2.3 Các mốc thời gian chấm và công bố

- Global Nominees công bố 03/12/2026. Đây là các dự án được chọn từ vòng Local và Universal.
- Global Finalists và Honorable Mentions công bố 17/12/2026.
- Global Winners công bố 26/01/2027. Có 10 hạng mục Global Award, gồm: Best Use of Science, Best Use of Data, Best Use of Technology, Galactic Impact, Best Mission Concept, Most Inspirational, Best Storytelling, Global Connection, Art & Technology, Local Impact.
- Hạng mục gần với đề game nhất là "Best Mission Concept", mô tả là dự án có khái niệm và thiết kế hợp lý nhất.
Nguồn hạng mục: https://www.spaceappschallenge.org/awards/

### 2.4 Yêu cầu tối thiểu để được vào Global Judging

- Trả lời một đề chính thức của NASA Space Apps.
- Mọi thành viên đã đăng ký, cùng một Local Event, có tên trên tab Members của trang Team.
- Hoàn tất mọi trường bắt buộc trên trang nộp bài.
- Có demo dạng slide tối đa 7 slide hoặc video tối đa 30 giây.
- Dùng tiếng Anh trên trang nộp bài và mọi tài liệu liên kết.
- Nộp trước hạn.
- Tick hai ô xác nhận: đã đọc yêu cầu nộp bài và đồng ý Terms & Conditions; xác nhận sản phẩm là công trình gốc và mọi tài nguyên bên ngoài đã được liệt kê trong References.
- Chịu rà soát theo chính sách hạn chế tài trợ của NASA với Trung Quốc.

---

## PHẦN 3 - BẢNG LIỆT KÊ TOÀN BỘ RESOURCE

Tab Resources có đúng 8 mục dưới tiêu đề "NASA DATA & RESOURCES" và 1 mục dưới tiêu đề "SPACE AGENCY PARTNER RESOURCES". Mỗi mục có một link ra ngoài. Tổng cộng 9 link resource chính thức.

| # | Tên resource | URL đầy đủ | Loại | Nội dung tóm tắt |
|---|---|---|---|---|
| 1 | Design and Develop Science Missions | https://www.nasa.gov/wp-content/uploads/2025/04/250323-design-and-develop-science-mission.pdf?emrc=a454cf | PDF, 25 trang slide | Slide webinar của NASA Small Satellite Institute, ngày 26/03/2025, tác giả Julie Levri. Trình bày quy trình systems engineering để phát triển một sứ mệnh khoa học: bốn segment (launch, space, ground, user), chuỗi bước Identify Need & Goals, Define Concept, Define Requirements, Design, Build & Verify, Implement. Có ví dụ xuyên suốt là sứ mệnh BioNutrients-2 trên ISS, đi từ nhu cầu tới yêu cầu định lượng và kiểm chứng. |
| 2 | General Mission Analysis Tool (GMAT) | https://software.nasa.gov/software/GSC-19468-1 | Công cụ phần mềm, open source | Phần mềm mã nguồn mở duy nhất ở mức enterprise cho thiết kế, tối ưu và dẫn đường sứ mệnh không gian. Hỗ trợ từ LEO tới Mặt Trăng, điểm libration và không gian sâu. Dùng để lan truyền quỹ đạo, tối ưu quỹ đạo, xác định quỹ đạo, mô phỏng dữ liệu dẫn đường, phân tích cửa sổ phóng, lập kế hoạch maneuver. |
| 3 | Concept Maturity Levels (CMLs) | https://dataverse.jpl.nasa.gov/dataset.xhtml?persistentId=hdl:2014/44299 | Bài báo PDF, 72 trang | Bài hội nghị AIAA SPACE 2013 của JPL (Wessen, Borden, Ziemer, Kwok), CL#13-3547. Định nghĩa thang CML 1 tới 7 để đo độ chín của một khái niệm sứ mệnh, kèm CML Matrix 7 cột x 24 dòng chia thành Science, Technical, Management, Cost, Other, và bộ checklist cho CML 2 tới 6. |
| 4 | Mission Design Lab (MDL) | https://etd.gsfc.nasa.gov/capabilities/integrated-design-center/mission-design-lab/ | Trang web, mô tả cơ sở | Phòng thiết kế sứ mệnh của NASA Goddard. Mô tả bốn mức study: Office Hours khoảng 1 giờ, Concept Development vài buổi nửa ngày, Tailored Trade Study thời lượng thay đổi, Point Design Study 6 ngày. Liệt kê 16 chuyên ngành kỹ thuật tham gia và các sản phẩm đầu ra. |
| 5 | NASA Mission Viz | https://nasa.github.io/mission-viz/ | Trang web, cổng công cụ và tutorial | Trang chỉ mục của repo Web-based Space Mission Visualization. Tập hợp bốn web app orrery 3D và bảy tutorial, gồm orrery ontology, bảng tham số quỹ đạo hành tinh, mô hình 3D Trái Đất tới Mặt Trăng, và hướng dẫn dựng quỹ đạo ellipse 3D bằng R. |
| 6 | A Learning Game About Telescopes (Build It Yourself) | https://science.nasa.gov/mission/webb/game-build-it-yourself/ | Game web chơi được | Game giáo dục của NASA về thiết kế kính viễn vọng không gian. Người chơi chọn mục tiêu khoa học, rồi bước sóng, thiết bị, hệ quang học, với các lựa chọn bị khóa nếu không tương thích. Có ba mức độ. Sau khi phóng, game cho xem cấu hình vệ tinh và chỉ ra sứ mệnh NASA thật có dữ liệu tương tự. Đây là tham chiếu thiết kế gần nhất với đề bài. |
| 7 | Cubesat 101 - Basic Concepts and Processes for First-Time CubeSat Developers | https://www3.nasa.gov/sites/default/files/atoms/files/nasa_csli_cubesat_101_508.pdf | PDF, hơn 70 trang | Hướng dẫn của NASA CubeSat Launch Initiative, bản Revision tháng 10/2017, do Cal Poly biên soạn. Bao phủ toàn bộ vòng đời CubeSat: chuẩn kích thước, dispenser, phương tiện phóng, quy trình phát triển theo tháng, cấp phép tần số, trạm mặt đất, kiểm thử môi trường, và bộ checklist. Đây là nguồn số liệu cứng tốt nhất trong cả trang. |
| 8 | Visualize a Space Mission Using Virtual Reality | https://www.spaceappschallenge.org/2023/challenges/visualize-a-space-mission-using-virtual-reality/ | Trang đề bài cũ, 2023 | Đề bài năm 2023 về dựng ứng dụng VR trong trình duyệt để trực quan hóa khái niệm sứ mệnh, quỹ đạo và timeline. Có ba mức Beginner, Intermediate, Advanced với hướng dẫn cụ thể, kèm danh sách resource riêng (NASA Eyes, Web WorldWind, GMAT, pykep, orrery). |
| 9 | Digital Games and Activities (CSA) | https://www.asc-csa.gc.ca/eng/youth-educators/digital-games-and-activities.asp | Trang web, danh mục game | Trang tập hợp game, sách điện tử và hoạt động của Cơ quan Vũ trụ Canada. Có bốn game chơi được: Mission: Astronaut, RADARSAT Constellation Mission, OSIRIS-REx, và Tomatosphere Adventure trên Minecraft Education. Ngoài ra có quiz, mô hình 3D để in, puzzle. |

---

## PHẦN 4 - CHI TIẾT TỪNG RESOURCE

### 4.1 Design and Develop Science Missions

- Tên đầy đủ: Design and Develop Science Missions, Access to Space for All, Systems Engineering Webinar Series
- URL: https://www.nasa.gov/wp-content/uploads/2025/04/250323-design-and-develop-science-mission.pdf?emrc=a454cf
- Loại: PDF, 25 trang, file 2.6 MB, ngày trên slide 26/03/2025
- Tác giả: Julie Levri, Flight Systems Engineer, NASA
- Nguồn gốc: www.nasa.gov/smallsat-institute
- Trạng thái: tải về thành công, đọc toàn văn bằng pdftotext

**Nội dung thật, theo trình tự slide**

Trang 2 liệt kê bảy tài liệu tham chiếu nền tảng, đây là các chuẩn mà mọi thiết kế sứ mệnh của NASA phải tuân theo:
1. NASA Systems Engineering Handbook, NASA SP-2016-6105 Rev 2, tại https://www.nasa.gov/reference/systems-engineering-handbook/
2. NASA Systems Engineering Processes and Requirements, NPR 7123.1 Rev D, tại https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_7123_001D_&page_name=main
3. NASA Space Flight Program and Project Management Requirements, NPR 7120.5 Rev F
4. NASA Research and Technology Program and Project Management Requirements, NPR 7120.8 Rev A
5. Risk Classification for NASA Payloads, NPR 8705.4 Rev B
6. NASA Science Mission Directorate, https://science.nasa.gov/learn/
7. System Engineering Curriculum Intro, NTRS 20210021839

Trang 4 tới 6 định nghĩa sứ mệnh khoa học: với NASA, một sứ mệnh khoa học do Science Mission Directorate quản lý là sứ mệnh không gian tập trung chủ yếu vào nghiên cứu và thám hiểm khoa học, bao gồm bốn lĩnh vực: Earth science, Heliophysics, Planetary science, Astrophysics. Sứ mệnh khoa học thường được dẫn dắt bởi các kế hoạch chiến lược của SMD, khác với sứ mệnh thám hiểm do các directorate khác chỉ đạo.

Trang 8 định nghĩa bốn segment, đây là khung phân rã mà game nên dùng:
- Launch segment: phương tiện phóng và các dịch vụ đi kèm để đưa tàu vào không gian.
- Space segment: tàu vũ trụ và các thành phần như orbiter, lander, rover, thiết bị khoa học dùng để thu dữ liệu.
- Ground segment: trạm mặt đất và trung tâm điều khiển, liên lạc với tàu, nhận dữ liệu, quản lý sứ mệnh.
- User segment: các nhà khoa học và công chúng dùng dữ liệu cho nghiên cứu và giáo dục.

Trang 10 là chuỗi sáu bước lớn, đây là xương sống của vòng chơi trong game: Identify Need & Goals, Define Concept, Define Requirements, Design, Build & Verify, Implement.

Trang 12 tới 23 là ví dụ xuyên suốt BioNutrients-2, minh họa cách một yêu cầu khoa học biến thành con số kỹ thuật:
- Nhu cầu: cho phép tạo dinh dưỡng tại chỗ nhanh, an toàn, đáng tin cậy với khối lượng, công suất và thể tích tối thiểu cho sứ mệnh dài ngày.
- Ba mục tiêu: cho nấm men phát triển; tạo beta carotene trên ISS; giảm khối lượng và thể tích so với payload BioNutrients-1.
- Yêu cầu định lượng cụ thể: 12 mẫu lặp lại; 30 mL thể tích mỗi mẫu; 3 microgam beta carotene trên mL mẫu thu hồi; 1 mg khối lượng tế bào khô mỗi mẫu; không nhiễm khuẩn.
- Yêu cầu tài nguyên: container mẫu nhỏ hơn 250 g; tổng thể tích chiếm chỗ nhỏ hơn 300 mL.
- Điểm phương pháp quan trọng: khi xác định yêu cầu phải đồng thời lập kế hoạch kiểm chứng (verification) trước khi triển khai. Ví dụ "container nhỏ hơn 250 g" được kiểm chứng bằng cách cân container rỗng.

Trang 24 liệt kê sáu ví dụ sứ mệnh khoa học thật, dùng được làm cảm hứng kịch bản game:
- PUNCH: bốn vệ tinh nhỏ ở LEO tạo quan sát 3D toàn cầu của vành nhật hoa, tìm hiểu cách khối lượng và năng lượng từ vành nhật hoa trở thành gió mặt trời. https://science.nasa.gov/mission/punch/
- PILOT: 34 vệ tinh trên hai quỹ đạo khác nhau, đo dòng plasma lạnh, đậm đặc vào và ra khỏi từ quyển Trái Đất. https://advancedspace.com/pilot-magnetosphere-science-mission-design/
- Dawn: tàu đầu tiên quay quanh hai thiên thể nhỏ, tiểu hành tinh Vesta và hành tinh lùn Ceres.
- Mars Moon Sampler: lander lên Phobos hoặc Deimos, thuộc lớp New Frontiers, mục tiêu xác định nguồn gốc hai mặt trăng của Sao Hỏa bằng cách mang mẫu về Trái Đất.
- Space Launch System: phương tiện phóng hạng nặng, giảm thời gian sứ mệnh, tăng biên khối lượng, tăng thể tích payload.
- Artemis: chuỗi sứ mệnh đưa hàng hóa lên bề mặt Mặt Trăng và cho phép lưu trú dài hạn.

**Giá trị cho game:** đây là tài liệu chuẩn để dựng màn hình "mission concept" và chuỗi bước chơi. Bốn segment cho bốn nhóm thẻ trong game. Chuỗi sáu bước cho sáu pha. Ví dụ BioNutrients-2 cho thấy một mục tiêu khoa học phải được dịch thành con số khối lượng, thể tích, số mẫu, và mỗi con số phải có cách kiểm chứng. Đây chính là cơ chế "requirement → design → verification" mà game có thể dạy.

### 4.2 General Mission Analysis Tool (GMAT)

- Tên đầy đủ trên trang: General Mission Analysis Tool (GMAT) Version R2025a
- Mã tham chiếu NASA: GSC-19468-1
- Trang giới thiệu: https://software.nasa.gov/software/GSC-19468-1
- Link tải: https://sourceforge.net/projects/gmat/
- Loại: phần mềm, category Design and Integration Tools, Release Type Open Source
- Hệ điều hành: Windows, Linux, Mac OS
- Liên hệ: hq-dl-t2-ops-center@mail.nasa.gov
- Trạng thái: trang giới thiệu mở thành công. Link tải SourceForge bị Cloudflare chặn khi truy cập tự động, xem mục 5 về resource không truy cập được.

**Nội dung thật trên trang NASA Software Catalog**

GMAT được mô tả là hệ phần mềm mã nguồn mở duy nhất trên thế giới ở mức enterprise, đa sứ mệnh, dùng cho thiết kế, tối ưu hóa và dẫn đường sứ mệnh không gian. Hệ thống hỗ trợ các chế độ bay từ quỹ đạo Trái Đất thấp tới Mặt Trăng, điểm libration và sứ mệnh không gian sâu. GMAT được phát triển bởi một nhóm gồm NASA, doanh nghiệp tư nhân, tổ chức công và tư nhân đóng góp. Nó được dùng cho hỗ trợ sứ mệnh thật, nghiên cứu kỹ thuật, làm công cụ giáo dục và tiếp cận công chúng.

**Chức năng cụ thể (input và output)**

Theo mô tả trên tab Resources và trang phần mềm, GMAT cho phép:
- Mô hình hóa tàu vũ trụ, hệ đẩy, quỹ đạo, maneuver và các thành phần sứ mệnh khác bằng mô hình vật lý độ trung thực cao.
- Lan truyền quỹ đạo (orbit propagation).
- Tối ưu hóa quỹ đạo (trajectory optimization).
- Xác định quỹ đạo (orbit determination).
- Mô phỏng dữ liệu dẫn đường (navigation-data simulation).
- Phân tích cửa sổ phóng (launch-window analysis).
- Lập kế hoạch maneuver (maneuver planning).
- Đánh giá các kịch bản sứ mệnh và đánh đổi kỹ thuật khác nhau.
- Trực quan hóa tham số sứ mệnh, phân tích kết quả qua plot, report và output phân tích khác.

Input điển hình: script GMAT (ngôn ngữ kịch bản riêng) khai báo spacecraft, lực tác dụng, propagator, burn, targeter. Output điển hình: chuỗi thời gian tọa độ Descartes, report, plot.

**Giá trị cho game:** GMAT là công cụ có thể dùng để sinh dữ liệu quỹ đạo thật cho game nếu cần độ chính xác cao. Nhưng với game web, không cần chạy GMAT runtime. Điều đáng lấy là mô hình khái niệm của nó: spacecraft + propagator + maneuver + targeter, tương ứng với ba bảng dữ liệu trong game là tàu, quỹ đạo, và burn.

### 4.3 Concept Maturity Levels (CMLs)

- Tên bài: Space mission concept development using concept maturity levels
- URL dataset: https://dataverse.jpl.nasa.gov/dataset.xhtml?persistentId=hdl:2014/44299
- URL file PDF trực tiếp: https://dataverse.jpl.nasa.gov/api/access/datafile/50237
- Persistent identifier: hdl:2014/44299
- Loại: bài hội nghị, PDF 72 trang, 1.4 MB
- Tác giả: Randii R. Wessen, Chester Borden, John Ziemer, Johnny Kwok, Jet Propulsion Laboratory, California Institute of Technology
- Năm: 2013, hội nghị AIAA SPACE 2013, San Diego, 10 tới 12/09/2013
- JPL Clearance Number: CL#13-3547
- Giấy phép: CC0 1.0, dùng tự do
- Trạng thái: trang dataset mở thành công, PDF tải và đọc toàn văn thành công

**Nội dung thật**

Bài báo công bố lần đầu bộ CML Matrix ra ngoài cộng đồng JPL. CML là hệ phân loại đo mức độ chín của một khái niệm sứ mệnh trong giai đoạn Pre-Phase A, tức trước khi dự án vào Phase A/B chính thức. JPL phát triển phương pháp này từ năm 2008.

Định nghĩa bảy mức, trích nguyên văn:
- CML 1, Cocktail Napkin: câu hỏi khoa học đã được phát biểu rõ, loại quan sát cần thiết đã được đề xuất, phác thảo sơ lược về khái niệm sứ mệnh và mục tiêu cấp cao đã có. Cái làm ý tưởng trở nên độc đáo và có ý nghĩa đã được nắm bắt.
- CML 2, Initial Feasibility: ý tưởng được mở rộng và chất vấn về tính khả thi từ góc độ khoa học, kỹ thuật và chương trình. Mục tiêu cấp thấp hơn đã được xác định, các tham số hiệu năng then chốt đã được định lượng, và các tính toán cơ bản đã được thực hiện. Các tính toán này, ở mức bậc một, xác định tính khả thi của khái niệm.
- CML 3, Trade Space: đã khảo sát không gian đánh đổi quanh mục tiêu khoa học và kiến trúc, giữa hệ tàu, hệ mặt đất và thiết kế sứ mệnh, để hiểu quan hệ giữa lợi ích khoa học, chi phí và rủi ro.
- CML 4, Point Design: một thiết kế và chi phí cụ thể đã được chọn trong không gian đánh đổi, định nghĩa xuống mức các phân hệ chính với biên và dự phòng chấp nhận được. Đã thực hiện đánh đổi ở mức phân hệ.
- CML 5, Baseline Concept: cách triển khai đã được định nghĩa gồm đối tác, hình thức hợp đồng, cách tích hợp và kiểm thử, chi phí và tiến độ. Đây là mức cần để viết đề xuất NASA Step 1 hoặc tổ chức Mission Concept Review.
- CML 6, Integrated Concept: chi tiết mở rộng về kỹ thuật, quản lý, chi phí và các yếu tố khác, có phân tích, biên và dự phòng đã chứng minh, có prototyping và phát triển công nghệ.
- CML 7 trở lên: đã nằm trong Phase A của dự án, phải tuân theo NPR 7120.5E, không còn cần hướng dẫn CML.

Cấu trúc CML Matrix: 7 cột cho CML 1 tới 7, 24 dòng, chia thành 2 dòng Science, 13 dòng Technical, 5 dòng Management, 1 dòng Cost, 3 dòng Other. Cách chia này khớp với cách NASA đánh giá khái niệm sứ mệnh: đầu tiên là science review, sau đó là TMCO Review (Technical, Management, Cost, Other).

Quy tắc đánh giá: mỗi ô trong cột trạng thái được tô màu xanh (hoàn thành), vàng (đang làm), đỏ (chưa bắt đầu). Một khái niệm được coi là đạt một mức CML nếu 80% thuộc tính trong cột đó đã xanh. Bài báo ghi rõ 80% không phải ngưỡng thiêng liêng, và cảnh báo không nên để nhóm tự đánh giá vì tự đánh giá thường lạc quan quá mức.

Ba hạn chế của công cụ checklist được nêu rõ: công cụ chỉ đo mức hoàn thành chứ không đo chất lượng; không có trọng số giữa các thuộc tính; và rất nguy hiểm nếu để nhóm tự chấm.

**Giá trị cho game:** CML cho một hệ thống cấp bậc rất tốt để thiết kế progression trong game. Người chơi bắt đầu ở CML 1 với một mục tiêu khoa học, rồi phải hoàn thành các bước để lên CML 2, 3, 4. Ngưỡng 80% là một cơ chế tính điểm sẵn có: người chơi chỉ được "duyệt" một giai đoạn khi đã hoàn thành 80% checklist của giai đoạn đó. Đây là cơ chế có nguồn NASA thật, dễ giải thích với giám khảo.

### 4.4 Mission Design Lab (MDL)

- URL: https://etd.gsfc.nasa.gov/capabilities/integrated-design-center/mission-design-lab/
- Loại: trang web mô tả cơ sở của NASA Goddard Engineering and Technology Directorate
- Trạng thái: mở và đọc toàn văn thành công. Trang có banner thông báo website không được cập nhật do gián đoạn ngân sách liên bang.

**Nội dung thật**

MDL là môi trường cộng tác để phát triển thiết kế không gian và khái niệm kiến trúc. Bốn thành phần then chốt được nêu: con người, quy trình, công cụ và cơ sở vật chất.

Bốn mức study, đây là phần có số liệu cứng:
- Office Hours: khoảng 1 giờ, không cần chuẩn bị hoặc chuẩn bị rất ít, mục đích brainstorm, xác định các "tall pole" và trade study then chốt, đề xuất bước tiếp theo và đầu mối hỗ trợ kỹ thuật sớm.
- Concept Development: vài buổi nửa ngày. Sản phẩm có thể là đánh giá tính khả thi khái niệm và đánh giá rủi ro.
- Tailored Trade Study: thời lượng thay đổi. Sản phẩm có thể gồm concept, ConOps, bảng tổng hợp nguồn lực (Resources Summary), trade tree, và chi phí ước lượng bậc độ lớn (ROM cost).
- Point Design Study: 6 ngày. Sản phẩm gồm CAD, MEL (Master Equipment List), mô hình kỹ thuật, chi phí CEMA. Điều kiện vào: phải "pass" checklist CML.

Năng lực kỹ thuật: thiết kế quỹ đạo LEO, GEO, libration, retrograde, drift away, Mặt Trăng và không gian sâu; sứ mệnh một tàu, chùm vệ tinh, bay theo đội hình hoặc hệ phân tán; phát triển khái niệm hệ mặt đất gồm dịch vụ và sản phẩm; thích ứng phương tiện phóng; cân nhắc kết thúc sứ mệnh gồm de-orbit có kiểm soát và không kiểm soát, trinh sát và hạ cánh, thu hồi mẫu.

Mười sáu chuyên ngành tham gia trong một study: Attitude Control, Mission Cost, Propulsion, Avionics, Mechanical Designer, Reliability, Flight Dynamics, Flight Software, Mechanical Systems, Orbital Debris, Radiation Environment, Structural, Communications, Mission Operations, Power Systems, Thermal.

Mỗi phân hệ chuẩn bị tài liệu về: yêu cầu, thiết kế cơ sở, thiết kế thay thế và trade study, sơ đồ chức năng, giao diện, ước lượng chi tiết khối lượng, công suất và tốc độ dữ liệu, đánh giá rủi ro kỹ thuật, vấn đề và khuyến nghị, mô hình, chi phí tham số và grassroots.

Sản phẩm mẫu của MDL: sơ đồ khối hệ thống tàu, phân tích quỹ đạo, phân tích liên lạc và hệ mặt đất, thích ứng hệ phóng, Master Equipment List, mô hình CAD đóng gói cơ khí, mô hình 3D khái niệm đài quan sát.

**Giá trị cho game:** đây là bản thiết kế của một "phiên họp nhóm" thật. Ba con số dùng được ngay: Office Hours 1 giờ, Concept Development vài buổi nửa ngày, Point Design 6 ngày. Danh sách 16 chuyên ngành cho 4 vai trò trong chế độ 4 người chơi: có thể gộp thành Power/Thermal, Structures/Mechanisms, Communications/Flight Dynamics, Cost/Operations. Bộ sản phẩm (MEL, sơ đồ khối, ước lượng mass/power/data rate) chính là những gì màn hình tổng kết cuối game nên in ra.

### 4.5 NASA Mission Viz

- URL gốc: https://nasa.github.io/mission-viz/
- Repo: https://github.com/nasa/mission-viz
- Loại: trang chỉ mục của bộ web app và tutorial
- Trạng thái: mở thành công, và đã mở thêm ba trang con bên dưới

**Nội dung thật trên trang chính**

Trang là chỉ mục của repo Web-based Space Mission Visualization (WSMV), gồm các web app orrery minh họa và tutorial dựng quỹ đạo.

Bốn web app:
- Ontology-based Orrery: trang HTML nhúng mô hình 3D hệ Mặt Trời, tham số quỹ đạo Kepler biểu diễn dưới dạng lớp orbit từ Space Situational Awareness Ontology. Dựng bằng thư viện X3DOM. URL: https://nasa.github.io/mission-viz/OntologyDrivenOrrery/An_Orrery_in_ThreeJS.html
- Orrery and orbital parameters table: trang HTML sinh từ mã R, nhúng mô hình 3D hệ Mặt Trời kèm bảng tham số quỹ đạo hành tinh. URL: https://nasa.github.io/mission-viz/RMarkdown/ontology_based_orrery_generated_from_R_code.html
- Orrery with Potentially Hazardous Asteroids: mô hình 3D động của các hành tinh phía trong và 50 tiểu hành tinh nguy hiểm tiềm tàng. Bộ lan truyền quỹ đạo viết bằng JavaScript gốc, theo sách "Orbital Mechanics, Theory and Applications" của Tom Logsdon. URL: https://nasa.github.io/mission-viz/X3Dom/InnerSolarSystem.html
- Earth Moon Mission Visualization: mô hình 3D động của một tàu đi từ quỹ đạo Trái Đất tới quỹ đạo Mặt Trăng. URL: https://nasa.github.io/mission-viz/X3Dom/20160129_Earth_MoonMission_X3D.html

Bảy tutorial, gồm ba tài liệu đáng chú ý:
- How to design a 3D elliptical orbit: https://nasa.github.io/mission-viz/RMarkdown/Elliptical_Orbit_Design.html
- Web-based Space Mission Visualization Tutorial Series: https://nasa.github.io/mission-viz/X3Dom/WebMissionVisualizationTutorialSeries.html
- A vision for a community developed web-based orrery: https://nasa.github.io/mission-viz/X3Dom/20150611_WebBasedMissionVisualizationSystem.pdf

Ontology: Space Situational Awareness Ontology của Robert Rovetto, file OWL trong repo; và NASA TM 20210000030, "An Ontology-Based Virtual Orrery", PDF tại https://ntrs.nasa.gov/api/citations/20210000030/downloads/NASA_TM_20210000030.pdf

**Trang con đã mở: bảng tham số quỹ đạo hành tinh**

URL: https://nasa.github.io/mission-viz/RMarkdown/ontology_based_orrery_generated_from_R_code.html
Đây là bảng số liệu thật, dùng trực tiếp được cho game. Cột gồm: label, eccentricity, inclination (độ), omega (độ), period (ngày), raan (độ), sma (AU), tau.

| Hành tinh | eccentricity | inclination | omega | period (ngày) | raan | sma (AU) | tau |
|---|---|---|---|---|---|---|---|
| Mercury | 0.20563 | 3.38 | 48.331 | 88.0 | 281.01 | 0.387098 | 29.124 |
| Venus | 0.006772 | 3.86 | 76.68 | 224.701 | 272.76 | 0.723332 | 54.884 |
| Earth | 0.016708 | 7.155 | -11.26064 | 365.25638 | 23.439281 | 1.0 | 114.20783 |
| Mars | 0.0934 | 5.65 | 49.558 | 686.971 | 317.68143 | 1.523679 | 286.502 |
| Jupiter | 0.0489 | 6.09 | 100.464 | 4332.59 | 268.057 | 5.2044 | 273.867 |
| Saturn | 0.0565 | 5.51 | 113.665 | 10759.22 | 40.589 | 9.5826 | 339.392 |
| Uranus | 0.046381 | 6.48 | 74.006 | 30688.5 | 257.311 | 19.2184 | 96.998856 |
| Neptune | 0.009456 | 6.43 | 131.784 | 60182.0 | 299.3 | 30.110388 | 276.336 |
| Pluto | 0.2488 | 11.88 | 110.299 | 90560.0 | 132.993 | 39.48 | 113.834 |

**Trang con đã mở: Elliptical Orbit Design**

URL: https://nasa.github.io/mission-viz/RMarkdown/Elliptical_Orbit_Design.html
Tác giả Daniel A. O'Neil, 14/04/2017. Trang dạy cách dựng quỹ đạo 3D từ hình ellipse 2D rồi áp ba phép quay. Công thức cụ thể có trong trang:
- b = a * sqrt(1 - e^2), bán trục nhỏ
- c = e * a, khoảng cách từ tâm tới tiêu điểm
- x = a * cos(u) - e, y = a * sqrt(1 - e^2) * sin(u), với u chạy từ -pi tới pi
- Ba phép quay: inclination là pitch (quay quanh trục Y), omega là yaw (quay quanh trục Z), RAAN là roll (quay quanh trục X)

Trang cũng đưa thuật toán giải phương trình Kepler bằng chuỗi Taylor bậc ba của Marc Murison, gồm các hàm KeplerStart3, eps1, eps2, eps3, KeplerSolve với dung sai 1e-14, và hàm propagate tính vị trí theo thời gian:
- M = n * (clock - tau), với n = 2*pi/T
- r = a * (1 - e * cos(E))
- s.x = r * ((cos(E) - e) / (1 - e * cos(E)))
- s.y = r * ((sqrt(1 - e^2) * sin(E)) / (1 - e * cos(E)))

Đây là công thức đầy đủ để vẽ quỹ đạo trong game bằng JavaScript mà không cần thư viện ngoài.

**Trang con đã mở: Tutorial Series và dữ liệu Molniya**

URL: https://nasa.github.io/mission-viz/X3Dom/WebMissionVisualizationTutorialSeries.html
Ba PDF tutorial:
- Part 1: https://nasa.github.io/mission-viz/X3Dom/20150918_WebVisualization_of_a_GMAT_GeneratedTrajectory_Part1.pdf
- Part 2: https://nasa.github.io/mission-viz/X3Dom/20150923_WebVisualization_of_a_GMAT_generatedTrajectory_Part2.pdf
- Part 3: https://nasa.github.io/mission-viz/X3Dom/20151102_WebVisualization_of_a_GMAT_generatedTrajectory_Part3.pdf

Part 1 đã tải và đọc (622 dòng text). Nội dung: quy trình export một quỹ đạo đơn giản từ GMAT, xử lý dữ liệu thành đối tượng JavaScript, và dựng trang web nhúng trực quan hóa tương tác. Năm mục tiêu học: cài GMAT; xem tutorial GMAT trên YouTube; thêm report generator vào script GMAT; dùng Excel để chuyển file dữ liệu sang JSON; viết trực quan hóa quỹ đạo bằng JavaScript và WebGL với X3Dom. Tutorial dùng GMAT-R2014a.

Có hai file dữ liệu mẫu thật, tải được:
- https://nasa.github.io/mission-viz/X3Dom/MolniyaOrbit.txt , 156 dòng, cột Sat.UTCGregorian, Sat.EarthMJ2000Eq.X, Y, Z, đơn vị km, bước thời gian không đều từ 60 giây tới hàng chục phút, khoảng 22 tới 23/07/2014
- https://nasa.github.io/mission-viz/X3Dom/MolniyaOrbit.json , cùng dữ liệu dạng JSON

Dòng đầu của file: `22 Jul 2014 11:29:10.811   137380   -75679.6   21487.6`, tức vị trí X khoảng 137.380 km. Dòng cuối: `23 Jul 2014 23:13:05.305   9890.4   -39514.5   -1334.18`. Đây là quỹ đạo Molniya thật, dùng làm dữ liệu demo cho màn hình "trajectory" trong game.

**Giá trị cho game:** đây là resource có giá trị thực dụng cao nhất cho phần hình ảnh. Bảng tham số quỹ đạo 9 hành tinh dùng được ngay cho màn hình orrery. Công thức quỹ đạo ellipse và thuật toán Kepler dùng được ngay để vẽ quỹ đạo bằng canvas hoặc SVG. File Molniya dùng được làm dữ liệu mẫu cho "xem lại hành trình".

### 4.6 A Learning Game About Telescopes (Build It Yourself)

- Tên trên trang: A Learning Game About Telescopes / Build It Yourself
- URL: https://science.nasa.gov/mission/webb/game-build-it-yourself/
- Game chạy trong iframe tại: https://webb.nasa.gov/content/features/educational/buildItYourself/game/index.html
- Transcript đầy đủ (PDF 8 trang): https://science.nasa.gov/wp-content/uploads/2024/03/gametext.pdf
- Loại: game web giáo dục, chơi được, do NASA Goddard phát triển cho Webb
- Trạng thái: trang và PDF transcript tải và đọc thành công

**Nội dung thật trên trang**

Mô tả chính thức: game dạy người chơi rằng yêu cầu khoa học dẫn dắt thiết kế và kỹ thuật của sứ mệnh kính viễn vọng. Người chơi chọn khoa học mà vệ tinh sẽ nghiên cứu, rồi quyết định bước sóng, thiết bị và hệ quang học nào giúp hiểu rõ nhất về khoa học đã chọn. Sau khi phóng, người chơi thấy vệ tinh trông thế nào và biết sứ mệnh thật nào có dữ liệu tương tự.

Gợi ý chơi (nguyên văn rút gọn): số lựa chọn được phép có giới hạn, nên phải chọn tốt nhất theo tham số của màn đang chơi. Có những lựa chọn bị làm xám và không chọn được, vì chúng không khả thi về khoa học hoặc kỹ thuật. Có thể đổi lựa chọn bất cứ lúc nào trước khi phóng. Nếu ghép quá nhiều thứ không bổ trợ nhau, vệ tinh sẽ thành một mớ hỗn độn.

Yêu cầu kỹ thuật của game: kích thước màn hình tối thiểu 1024 x 768. Thiết kế cho tablet, laptop, desktop. Không tương thích tốt với điện thoại, trừ điện thoại màn hình lớn ở chế độ ngang và phải cuộn. Game không có accessibility tích hợp nhưng có transcript đầy đủ. Game được NASA Education phê duyệt năm 2013. Phản hồi gửi về GSFC-NASAWebb@mail.nasa.gov.

**Nội dung thật trong transcript 8 trang**

Cấu trúc màn hình: màn chính nền xanh đậm, có ba nút Level 1, Level 2 (ghi nhầm thành "Level 3" lần đầu trong transcript), Level 3, và nút "Need a hint" ở góc dưới phải.

Trình tự chơi mỗi màn:
1. Màn Science: chọn mục tiêu khoa học. Năm lựa chọn: Black Holes, Star Formation, Early Universe, Galaxies, Exoplanets. Rê chuột vào biểu tượng để đọc giải thích ở nửa trái màn hình.
2. Màn Wavelength: chọn bước sóng phù hợp với mục tiêu đã chọn. Ví dụ Black Holes cho phép chọn X-ray hoặc Gamma ray, mỗi lựa chọn có giải thích riêng về vật lý và về cái người chơi có thể học được.
3. Màn Instrument: chọn thiết bị.
4. Màn Optics: chọn cấu hình quang học.
5. Màn Launch: chuỗi hoạt cảnh phóng.
6. Màn kết quả: hiển thị cấu hình vệ tinh đã tạo, kết quả khoa học thu được, và nêu tên sứ mệnh NASA thật có đặc điểm và mục tiêu khoa học tương tự.

Cơ chế then chốt: các lựa chọn bị khóa khi không tương thích về khoa học hoặc kỹ thuật với mục tiêu đã chọn. Số lượng lựa chọn bị giới hạn theo màn. Lên màn cao hơn thì được chọn nhiều mục tiêu khoa học cùng lúc, kéo theo nhiều bước sóng, thiết bị và cấu hình quang học hơn.

**Giá trị cho game:** đây là mẫu tham chiếu gần nhất về cấu trúc. Chuỗi Science, Wavelength, Instrument, Optics tương ứng với chuỗi Objective, Measurement, Instrument, Configuration trong game của nhóm. Cơ chế "greyed out khi không tương thích" là cách thể hiện ràng buộc dễ hiểu nhất với người chơi phổ thông, và nên copy. Cơ chế "sau khi phóng thì chỉ ra sứ mệnh thật tương tự" là một điểm cộng giáo dục rất rẻ để làm: chỉ cần một bảng ánh xạ cấu hình sang tên sứ mệnh thật.

### 4.7 Cubesat 101 - Basic Concepts and Processes for First-Time CubeSat Developers

- Tên đầy đủ: CubeSat 101: Basic Concepts and Processes for First-Time CubeSat Developers
- URL: https://www3.nasa.gov/sites/default/files/atoms/files/nasa_csli_cubesat_101_508.pdf
- Loại: PDF, hơn 70 trang, 4.4 MB, Revision tháng 10/2017
- Đơn vị: NASA CubeSat Launch Initiative, biên soạn theo hợp đồng bởi California Polytechnic State University, San Luis Obispo, CubeSat Systems Engineer Lab
- Trạng thái: tải và đọc toàn văn thành công (4014 dòng text)

**Số liệu kỹ thuật cứng trích được**

Kích thước và khối lượng chuẩn:
- 1U: kích thước 10 cm x 10 cm x 11 cm, khối lượng xấp xỉ 1 tới 1,33 kg
- 3U: kích thước 10 cm x 10 cm x 34 cm
- 6U: về cơ bản là hai 3U đặt cạnh nhau, tức rộng gấp đôi
- Các cỡ khác đã phổ biến: 1.5U, 2U, 6U, 12U
- CDS cho phép phần nhô ra khỏi thân tối đa 6,5 mm tính từ bề mặt

Chi phí và dịch vụ:
- Dưới CSLI, NASA chi trả toàn bộ chi phí phóng, tối đa 300.000 USD, thường đủ để đưa một 3U lên quỹ đạo Trái Đất thấp. Nhóm phát triển tự chịu mọi chi phí phát triển, vận hành, trạm mặt đất, kiểm thử và đi lại.
- Con số 300.000 USD cho một 3U lên LEO là mốc chi phí phóng rất tốt để dùng làm giá tham chiếu trong game.

Chuỗi thời gian phát triển, đây là bộ số liệu dùng trực tiếp cho thanh "Time" trong game:
- 2.1 Concept Development: 1 tới 6 tháng
- 2.2 Securing Funding: 1 tới 12 tháng
- 2.3 Merit and Feasibility Reviews: 1 tới 2 tháng
- 2.4 CubeSat Design: 1 tới 6 tháng
- 2.5 Proposal to CSLI Call: 3 tới 4 tháng
- 2.6 Selection and Manifesting: 1 tới 36 tháng
- 2.7 Mission Coordination: 9 tới 18 tháng
- 2.8 Regulatory Licensing: 4 tới 6 tháng
- 2.9 Flight-Specific Documentation Development and Submittal: 10 tới 12 tháng
- 2.10 Ground Station Design, Development, and Testing: 2 tới 12 tháng
- 2.11 CubeSat Hardware Fabrication and Testing: 2 tới 12 tháng
- 2.12 Mission Readiness Reviews: nửa ngày
- 2.13 CubeSat-to-Dispenser Integration and Testing: 2 ngày
- 2.14 Dispenser-to-Launch Vehicle Integration: 1 ngày
- 2.15 Launch: 1 ngày
- 2.16 Mission Operations: thay đổi, tối đa 20 năm

Danh sách phương tiện phóng của Mỹ đã dùng cho CubeSat (tính tới 2017): Super Strypi, Minotaur I, Minotaur IV, Taurus XL, Delta II, Antares, Falcon 9, Atlas V, Electron, Falcon 9 Heavy, LauncherOne, SLS. Con số chiều cao trong hình: Atlas V 58,3 m, Electron 17 m.

Hệ thống triển khai (dispenser):
- P-POD (Poly-Picosatellite Orbital Deployer) do Cal Poly phát triển, là dispenser đầu tiên, dùng cho 3U
- Dispenser 6U xuất hiện từ 2014, chứa được một 6U, sáu 1U, hoặc hai 3U
- CubeSat gắn vào dispenser qua thanh ray, đẩy ra bằng lò xo

Quy trình phóng theo ví dụ ELaNa II trong phụ lục:
- Phút thứ 30 sau khi tách: ăng ten triển khai
- Phút thứ 45: bật beacon UHF
- Vài pass đầu: trạm mặt đất thử liên lạc để kiểm tra tàu
- Khoảng 4 ngày sau phóng: bắt đầu kiểm thử payload, kéo dài ít nhất 1 năm
- Quy định cấm phát sóng trước phút thứ 45 sau khi tách, và cấm gửi lệnh mặt đất trước phút thứ 45

Vật liệu và linh kiện trong ví dụ: kết cấu hợp kim nhôm 6061-T6, linh kiện COTS, pin lithium-ion có mạch bảo vệ quá áp và quá dòng, pin phải có chứng nhận UL, radio tốc độ cao dùng ăng ten patch gốm, ăng ten triển khai kiểu monopole hướng xuống nadir.

Quy định kỹ thuật khác: CDS cấm dùng pyrotechnics. Cơ cấu giữ và nhả tấm pin mặt trời dùng burn wire (dây đốt bằng điện trở làm chảy dây cước), phải dùng hai dây độc lập để tránh nhả sớm khi rung. Không được thiết kế sát giới hạn bao hình của CDS: "nếu không vừa thì không bay".

Yêu cầu về tần số: phải xin giấy phép tần số, thường dùng băng tần nghiệp dư, có thể dùng 70 cm và S-band cho hai hệ liên lạc chính và phụ, phải đăng ký với IARU.

Yêu cầu về hồ sơ: báo cáo pin (battery report), xác nhận kích thước, báo cáo điện, phân tích thoát khí (venting analysis), quy trình kiểm thử gồm Day In The Life, rung và sốc, thermal vacuum bakeout. Hồ sơ đầu tiên thường đến hạn khoảng 10 tháng trước ngày giao tàu cho cơ sở tích hợp.

**Giá trị cho game:** đây là nguồn số liệu cứng tốt nhất trong cả trang resource. Dùng được ngay: 1U = 10x10x11 cm, 1 tới 1,33 kg; 3U = 10x10x34 cm; chi phí phóng 300.000 USD cho 3U lên LEO; 16 giai đoạn phát triển với số tháng cụ thể; mốc 30 phút triển khai ăng ten và 45 phút bật beacon; giới hạn nhô ra 6,5 mm; cấm pyrotechnics.

### 4.8 Visualize a Space Mission Using Virtual Reality (đề bài 2023)

- URL: https://www.spaceappschallenge.org/2023/challenges/visualize-a-space-mission-using-virtual-reality/
- Tab Details: https://www.spaceappschallenge.org/2023/challenges/visualize-a-space-mission-using-virtual-reality/?tab=details
- Tab Resources: https://www.spaceappschallenge.org/2023/challenges/visualize-a-space-mission-using-virtual-reality/?tab=resources
- Loại: trang đề bài cũ của NASA Space Apps 2023, có tab Details và Resources riêng
- Độ khó: Advanced, Intermediate, Beginner/Youth. Chủ đề: Games, Planets & Moons, Software, Space Exploration
- Trạng thái: mở và đọc toàn văn cả hai tab thành công

**Vì sao đề này được đưa vào resource:** đây là tiền lệ trực tiếp. Cùng chủ đề "game", cùng yêu cầu trực quan hóa sứ mệnh, và có sẵn danh sách công cụ đã được NASA tuyển chọn. Đọc nó cho biết ban tổ chức coi công cụ nào là chuẩn.

**Nội dung thật, tab Details**

Tóm tắt: tưởng tượng một vệ tinh quay quanh Trái Đất, hoặc sứ mệnh Trái Đất tới Mặt Trăng cần maneuver chuyển quỹ đạo, hoặc tàu trên quỹ đạo chu kỳ giữa Trái Đất và Sao Hỏa, hoặc tàu thăm dò không gian sâu băng qua vành đai tiểu hành tinh. Hiểu và trực quan hóa các sứ mệnh phức tạp không dễ. Đề yêu cầu tạo ứng dụng VR tương tác trong trình duyệt, cho phép người dùng trực quan hóa khái niệm sứ mệnh, quỹ đạo và timeline.

Ba mức được nêu rõ:
- Beginner: học dùng GMAT, hoặc tự dựng quỹ đạo ellipse 3D. Dùng tutorial ba phần để biết cách dùng GMAT sinh chuỗi tọa độ Descartes 3D và vẽ quỹ đạo bằng thư viện X3D.
- Intermediate, hướng 1: dùng digital globe và dựng quỹ đạo quanh Trái Đất. Resource có link tới Web WorldWind của NASA, có API để thêm hình khối vào layer.
- Intermediate, hướng 2: dựng orrery ảo và trực quan hóa Earth-Mars cycler. Cycler là tàu đi theo quỹ đạo chu kỳ quanh Trái Đất và Sao Hỏa, có thể có tàu thứ hai lệch pha 180 độ. Hình dung như hệ thống giao thông công cộng: phi hành đoàn rời quỹ đạo Trái Đất để gặp cycler, rồi rời cycler để hạ cánh Sao Hỏa.
- Advanced: orrery ảo có vành đai tiểu hành tinh, sứ mệnh không gian sâu có fly-by hành tinh, dùng slingshot để lấy thêm động lượng khi đi qua Sao Hỏa hoặc Sao Kim. Có thể có chức năng upload file dữ liệu chuỗi tọa độ Descartes.

Yêu cầu triển khai: nhúng ứng dụng vào một trang web và đưa lên dịch vụ host miễn phí để giám khảo NASA truy cập được.

**Nội dung thật, tab Resources**

Nhóm NASA Resources gồm sáu mục: NASA Eyes (được mô tả là ví dụ tốt về orrery), NASA Software Catalog, trang Web-based space mission visualization trong Software Catalog, GMAT bản 2018, trang Space Mission Design Tools (dặn tìm GMAT bản R2020a), và Web WorldWind.

Nhóm Other Resources gồm: Web-based Space Mission Visualization Index Page; Web-based Mission Visualization Software (trang ReadMe của repo, có link tới các demo 3D và tutorial); Web-based Space Mission Visualization (chuỗi tutorial ba phần); Elliptical Orbit Simulator; Tutorial for Web-based Space Mission Visualization; Ontology-driven Orrery (dùng Three.js, tương tác được, click và kéo để xoay); Interactive Orrery (viết bằng R); Web-Based Space Mission Visualization System (tầm nhìn về orrery ảo); Inner Solar System (orrery động có các tiểu hành tinh nguy hiểm tiềm tàng); và The Orbit Plotting Module trong tài liệu pykep của ESA, một thư viện Python để trực quan hóa quỹ đạo.

Nhóm CSA gồm bài về thí nghiệm VR Vection và tin về công ty Canada Felix and Paul Studios phát triển hệ camera VR cho thám hiểm không gian.

Trang còn đưa danh sách từ khóa để tự tìm thêm, phân theo mục đích: thư viện đồ họa 3D, game engine, digital globe, dịch vụ host miễn phí, kiến thức về quỹ đạo (ellipse, parabolic, hyperbolic), tối ưu hóa đa ngành (Hohmann transfer example, Dymos two-burn orbit raise, Dymos Python package), và VR.

**Giá trị cho game:** trang này xác nhận rằng với đề "game" thì việc dựng trực quan hóa bằng thư viện web là hướng được ban tổ chức chấp nhận và khuyến khích. Nó cũng cho một danh sách công cụ đã được sàng lọc. pykep là lựa chọn nếu cần tính toán quỹ đạo chính xác hơn.

### 4.9 Digital Games and Activities (CSA)

- URL: https://www.asc-csa.gc.ca/eng/youth-educators/digital-games-and-activities.asp
- Loại: trang danh mục game và hoạt động của Canadian Space Agency
- Ngày cập nhật trên trang: 26/11/2025
- Trạng thái: trình duyệt bị timeout, đã lấy HTML gốc bằng curl và bóc text thành công

**Nội dung thật**

Trang giới thiệu là tập hợp game kỹ thuật số, sách điện tử và hoạt động cho mọi lứa tuổi. Danh mục gồm 11 mục:
1. Tomatosphere Adventure: game trên Minecraft Education, hiểu quang hợp rồi trồng cà chua trên Sao Hỏa.
2. Game Mission: Astronaut.
3. Exploring Earth: khám phá hành tinh qua ảnh phi hành gia chụp từ không gian và ảnh vệ tinh.
4. Game RADARSAT Constellation Mission: giúp một nông dân, một thuyền trưởng và một nhân viên ứng cứu hoàn thành nhiệm vụ bằng ảnh RADARSAT.
5. Game OSIRIS-REx: giúp tàu OSIRIS-REx chọn địa điểm tốt nhất trên tiểu hành tinh Bennu để lấy mẫu mang về Trái Đất.
6. The Explorers Club e-books.
7. Quizzes.
8. Mô hình in 3D.
9. Astronaut cutouts.
10. Puzzle Canada from space, dùng ảnh mosaic từ RADARSAT-2.
11. Playlists.

**Trang con đã mở: Game Mission: Astronaut**

URL: https://www.asc-csa.gc.ca/eng/youth-educators/activities/game-mission-astronaut.asp
Game online miễn phí, dành cho học sinh lớp 3 tới lớp 6, chơi trên máy tính hoặc tablet. Người chơi chọn avatar và phụ kiện, rồi chọn sứ mệnh để kiếm sao hoặc chơi minigame. Có hàng chục hoạt động ngắn chia thành tám sứ mệnh theo chủ đề: huấn luyện phi hành gia, sống trong không gian, robot, khoa học, tàu vũ trụ, Mặt Trăng và sứ mệnh Mặt Trăng, thiên văn và kính Webb, sức khỏe trong không gian. Sao kiếm được dùng để mở thẻ sưu tập thuộc bảy bộ, có thể "xây hệ Mặt Trời". Có sáu minigame, ví dụ Lunar Rover là hoạt động coding dễ, lập trình rover di chuyển trên Mặt Trăng bằng khối lệnh.

**Trang con đã mở: Game RADARSAT và Game OSIRIS-REx**

URL: https://www.asc-csa.gc.ca/eng/satellites/radarsat/activities/game.asp và https://www.asc-csa.gc.ca/eng/satellites/osiris-rex/activities/game.asp
Cả hai trang chỉ là khung chứa iframe, nội dung game nằm ở:
- https://www.asc-csa.gc.ca/app/game/RADARSAT/index.html?lang=en
- https://www.asc-csa.gc.ca/app/game/OSIRIS-REx/index.html?lang=en
Tiêu đề iframe xác nhận nội dung: "Use the RCM satellites to help farmers, a first responder and a ship's captain" và "Help the OSIRIS-REx spacecraft select the best site". Hai file index.html chỉ có 1,2 KB và 1,1 KB, tức game được nạp hoàn toàn bằng JavaScript, không đọc được nội dung tĩnh. Ghi nhận là không trích xuất được nội dung chi tiết của hai game này.

**Giá trị cho game:** giá trị chủ yếu là tham chiếu thiết kế trải nghiệm, không phải số liệu. Ba mẫu đáng học: Mission: Astronaut dùng hệ sao và thẻ sưu tập để giữ người chơi; RADARSAT gắn mỗi màn với một nhân vật có nhu cầu thực tế (nông dân, thuyền trưởng, ứng cứu viên), đây là cách hay để biến "mục tiêu sứ mệnh" thành câu chuyện; OSIRIS-REx biến việc chọn địa điểm thành quyết định có đánh đổi rõ ràng.

### 4.10 Các resource toàn cục đã đọc thêm (ngoài tab Resources của đề)

Những trang này không nằm trong tab Resources của đề, nhưng cần thiết để hiểu luật chơi và tiêu chí chấm.

| Tên | URL | Nội dung chính |
|---|---|---|
| Participant FAQs | https://www.spaceappschallenge.org/resources/participant-faqs/ | Xác nhận thời gian 14-15/11/2026, chủ đề "The Next Frontier", mốc công bố challenge statement 28/10 và resource 13/11/2026, yêu cầu về tuổi dưới 18, quy trình đăng ký. |
| Judging & Awards Guide | https://www.spaceappschallenge.org/resources/judging-awards-guide/ | Toàn bộ tiêu chí chấm điểm đã ghi ở Phần 2. |
| Project Submission Guide | https://www.spaceappschallenge.org/resources/project-submission-guide/ | Toàn bộ yêu cầu nộp bài đã ghi ở mục 1.7, kèm hướng dẫn làm demo 30 giây với timeline từng giây. |
| Awards | https://www.spaceappschallenge.org/awards/ | Danh sách 10 Global Award và quy trình ba vòng chấm. |
| NASA Science Mission Directorate | https://science.nasa.gov/ | Trang chủ của SMD, đơn vị tài trợ và quản lý sứ mệnh khoa học. |
| Chapter 3: Gravity & Mechanics, Basics of Space Flight | https://science.nasa.gov/learn/basics-of-space-flight/chapter3-2 | Định nghĩa delta-v, phương trình tên lửa Tsiolkovsky, giải thích ve, m0, mf, ln, và định nghĩa specific impulse. Số liệu: ve cao nhất hiện nay khoảng 4,5 km/s cho động cơ lỏng, khoảng 2,5 km/s cho động cơ rắn, động cơ ion cao hơn một bậc độ lớn. |
| Mars: Facts | https://science.nasa.gov/mars/facts/ | Bán kính Sao Hỏa 3.390 km; khoảng cách trung bình tới Mặt Trời 142 triệu dặm tức 228 triệu km, bằng 1,5 AU; ánh sáng đi từ Mặt Trời tới Sao Hỏa 13 phút; một vòng quay 24,6 giờ; một năm 669,6 sol tức 687 ngày Trái Đất; nhiệt độ từ 20 độ C tới âm 153 độ C; không có từ trường toàn cầu; có hai mặt trăng Phobos và Deimos. |
| Hazard: Distance From Earth (NASA HRP) | https://www.nasa.gov/hrp/hazard-distance-from-earth | Sao Hỏa cách Trái Đất trung bình 140 triệu dặm. Trễ liên lạc một chiều tới 20 phút. Sứ mệnh Sao Hỏa có người kéo dài khoảng ba năm. |
| SLS paper (ví dụ sứ mệnh trong PDF Design and Develop) | https://ntrs.nasa.gov/api/citations/20130013034/downloads/20130013034.pdf | SLS cấu hình đầu nâng 70 tấn lên LEO, có thể tiến hóa lên 130 tấn hoặc hơn; cấu hình 70 tấn nâng hơn 154.000 pound. |

---

## PHẦN 5 - KẾT LUẬN: THÔNG SỐ DÙNG TRỰC TIẾP ĐƯỢC CHO GAME

### 5.1 Những gì trang resource cung cấp thật, và những gì không

Điều cần nói thẳng: tab Resources của đề này không có dataset, không có bảng thông số tàu, không có bảng delta-v. Nó là một danh sách tài liệu phương pháp luận và công cụ. Ba trong chín resource là tài liệu quy trình (systems engineering, CML, MDL), ba là công cụ hoặc game tham chiếu, hai là PDF kỹ thuật (CubeSat 101 và slide webinar), một là trang đề bài cũ.

Hệ quả: nếu muốn dùng số liệu NASA thật cho game thì nguồn chính là CubeSat 101 (kích thước, khối lượng, chi phí, tiến độ) và bảng quỹ đạo hành tinh trong NASA Mission Viz. Các con số về delta-v và trễ tín hiệu phải tự tính từ hằng số vật lý, và nên ghi rõ trong tài liệu dự án là "tính toán từ hằng số, không trích từ trang đề". Điều này hoàn toàn hợp lệ vì yêu cầu của giải chỉ là dùng ít nhất một dữ liệu hoặc resource của NASA.

### 5.2 Số liệu dùng trực tiếp được, có nguồn

**Nhóm A, hình học và khối lượng CubeSat (nguồn: CubeSat 101, mục 1.1)**
- 1U: 10 x 10 x 11 cm, 1 tới 1,33 kg. Lấy trung bình 1,2 kg mỗi U.
- 3U: 10 x 10 x 34 cm, suy ra khoảng 3 tới 4 kg
- 6U: hai 3U cạnh nhau, tức 20 x 10 x 34 cm
- Phần nhô ra cho phép: tối đa 6,5 mm
- Cấm pyrotechnics trong thiết kế CubeSat theo CDS

**Nhóm B, chi phí phóng (nguồn: CubeSat 101, mục 2.2)**
- 300.000 USD là mức NASA chi tối đa để phóng một 3U lên LEO dưới CSLI
- Suy ra khoảng 100.000 USD mỗi kg lên LEO cho khối lượng cỡ 3 kg. Đây là con số rất dễ dùng làm giá phóng cơ sở trong game.

**Nhóm C, tiến độ phát triển (nguồn: CubeSat 101, mục 2.1 tới 2.16)**
Mười sáu giai đoạn với số tháng cụ thể. Nếu cộng các mức tối thiểu của 11 giai đoạn phát triển chính thì ra khoảng 51 tháng, còn cộng các mức tối đa thì ra khoảng 126 tháng, trước khi tính tới 20 năm vận hành. Đây là thanh "Time" của game, và cũng là nguồn gốc của các sự kiện trễ. Lưu ý các giai đoạn chạy song song một phần trong thực tế, nên con số cộng dồn chỉ là biên trên và biên dưới, không phải đường găng.

**Nhóm D, tham số quỹ đạo hành tinh (nguồn: NASA Mission Viz, bảng ontology orrery)**
Bảng đầy đủ 9 hành tinh với eccentricity, inclination, omega, period, raan, sma, tau đã chép ở mục 4.5. Dùng trực tiếp để vẽ orrery hoặc để kiểm tra vị trí tương đối Trái Đất và Sao Hỏa ở mỗi thời điểm.

**Nhóm E, Sao Hỏa và trễ tín hiệu (nguồn: NASA Mars Facts và NASA HRP)**
- Bán kính Sao Hỏa: 3.390 km
- Khoảng cách trung bình tới Mặt Trời: 228 triệu km, tức 1,5237 AU theo bảng quỹ đạo
- Một năm Sao Hỏa: 687 ngày Trái Đất, tức 669,6 sol
- Một ngày Sao Hỏa: 24,6 giờ
- Khoảng cách Trái Đất tới Sao Hỏa trung bình: khoảng 140 triệu dặm, tức khoảng 225 triệu km
- Trễ liên lạc một chiều tối đa theo NASA HRP: 20 phút

Từ đó tính được bảng trễ tín hiệu, dùng tốc độ ánh sáng 299.792,458 km/s:

| Trường hợp | Khoảng cách | Trễ một chiều | Trễ khứ hồi |
|---|---|---|---|
| Gần nhất (xấp xỉ) | 54,6 triệu km | 3,0 phút | 6,1 phút |
| Trung bình | 225 triệu km | 12,5 phút | 25,0 phút |
| Xa nhất (xấp xỉ) | 401 triệu km | 22,3 phút | 44,6 phút |

Con số 20 phút một chiều trong tài liệu NASA HRP khớp với khoảng cách khoảng 360 triệu km, tức gần mức xa nhất. Đây là dải rất tốt để làm cơ chế "lệnh gửi đi rồi phải chờ": người chơi bấm một lệnh và phải chờ 3 tới 22 phút mô phỏng mới thấy kết quả.

**Nhóm F, phương trình tên lửa và delta-v (nguồn: NASA Basics of Space Flight chương 3, cộng tính toán)**
Định nghĩa nguyên văn từ NASA: delta-v là mức thay đổi vận tốc tối đa mà một phương tiện chạy bằng tên lửa có thể trải qua bằng cách phun bớt khối lượng, khi không có ngoại lực. Phương trình Tsiolkovsky: delta-v = ve * ln(m0/mf). ve cao nhất hiện nay khoảng 4,5 km/s cho động cơ lỏng, 2,5 km/s cho động cơ rắn. Specific impulse là tỷ số giữa lực đẩy và trọng lượng dòng nhiên liệu, đo bằng giây khi tính theo trọng lượng nhiên liệu.

Tính toán Hohmann transfer Trái Đất tới Sao Hỏa từ bán trục lớn 1,0 AU và 1,523679 AU:
- Vận tốc quỹ đạo Trái Đất: 29,785 km/s
- Vận tốc quỹ đạo Sao Hỏa: 24,129 km/s
- Vận tốc tại điểm cận nhật của quỹ đạo chuyển tiếp: 32,729 km/s
- Vận tốc tại điểm viễn nhật của quỹ đạo chuyển tiếp: 21,480 km/s
- Delta-v khởi hành (thay đổi vận tốc nhật tâm ở quỹ đạo Trái Đất): 2,945 km/s
- Delta-v tới nơi (thay đổi vận tốc nhật tâm ở quỹ đạo Sao Hỏa): 2,649 km/s
- Tổng delta-v nhật tâm: 5,594 km/s
- Thời gian bay: 258,9 ngày, tức 0,71 năm

Cộng thêm phần thoát khỏi giếng hấp dẫn Trái Đất, tính từ LEO 400 km với vận tốc vô cực 2,945 km/s: delta-v khởi hành khoảng 3,57 km/s, cộng với khoảng 9,4 km/s để đạt LEO.

Bắt vào quỹ đạo Sao Hỏa 400 km từ vận tốc vô cực 2,649 km/s: delta-v khoảng 2,08 km/s.

Bảng khối lượng nhiên liệu theo phương trình tên lửa, dùng để kiểm tra tính hợp lý của thiết kế:

| Isp (giây) | Delta-v 3,6 km/s | Delta-v 5,6 km/s |
|---|---|---|
| 300 | tỷ số khối lượng 3,40, nhiên liệu chiếm 70,6% | 6,71, nhiên liệu chiếm 85,1% |
| 320 | 3,15, nhiên liệu 68,3% | 5,96, nhiên liệu 83,2% |
| 450 | 2,26, nhiên liệu 55,8% | 3,56, nhiên liệu 71,9% |

Con số này rất hữu ích cho game: nếu người chơi chọn động cơ hóa học Isp 320 và cần 5,6 km/s, thì 83% khối lượng phải là nhiên liệu. Đó là một bài học đánh đổi rất mạnh và hoàn toàn có thật.

**Nhóm G, khối lượng payload của phương tiện phóng (nguồn: PDF SLS)**
SLS cấu hình đầu 70 tấn lên LEO, tiến hóa lên 130 tấn hoặc hơn. Đây là mốc tham chiếu cho hạng "heavy lift". Có thể dùng để kiểm tra dữ liệu launch_vehicles.json hiện tại của nhóm: Falcon Heavy 25.000 kg lên LEO là hợp lý, Ariane 6 với 12.000 kg cũng hợp lý, còn SLS 70.000 kg là mốc trên cùng nếu muốn thêm một lựa chọn cực đại.

### 5.3 Ba thông số quan trọng nhất có thể dùng ngay

1. **Kích thước và khối lượng CubeSat: 1U = 10 x 10 x 11 cm và 1 tới 1,33 kg, 3U = 10 x 10 x 34 cm, phần nhô ra tối đa 6,5 mm.** Nguồn: CubeSat 101 của NASA CSLI, mục 1.1. Đây là bộ số liệu chuẩn hóa duy nhất trong toàn bộ resource, dùng để dựng hệ thống "kiểm tra bao hình" (form factor check) cho khối payload: người chơi xếp thiết bị vào các khe 1U, nếu tổng vượt sức chở thì không phóng được. Cơ chế này vừa có nguồn NASA thật, vừa tạo đánh đổi trực quan.

2. **Bảng tham số quỹ đạo 9 hành tinh với eccentricity, inclination, omega, period, raan, sma, tau.** Nguồn: bảng trong orrery của NASA Mission Viz. Dùng trực tiếp để vẽ hệ Mặt Trời 2D hoặc 3D bằng canvas, và để tính khoảng cách Trái Đất tới Sao Hỏa theo thời gian, từ đó suy ra trễ tín hiệu. Đây là thứ biến game từ bảng số thành một thứ có cảm giác "không gian thật".

3. **Phương trình tên lửa delta-v = ve * ln(m0/mf) với ve tính từ Isp, cùng dải delta-v Trái Đất tới Sao Hỏa khoảng 5,6 km/s nhật tâm, tương đương khoảng 3,5 km/s từ LEO cho phần khởi hành.** Nguồn: định nghĩa delta-v và Isp từ NASA Basics of Space Flight chương 3; các con số transfer tính từ bán trục lớn 1,0 AU và 1,523679 AU trong bảng quỹ đạo của Mission Viz. Đây là công thức duy nhất cần cho cơ chế nhiên liệu, và nó cho ra một kết luận gây ấn tượng mạnh với người chơi: phần lớn khối lượng tàu liên hành tinh là nhiên liệu.

### 5.4 Gợi ý ánh xạ resource sang tính năng game

| Tính năng trong game | Resource làm nền |
|---|---|
| Màn hình chọn mục tiêu khoa học, rồi bước sóng, thiết bị, cấu hình | A Learning Game About Telescopes, chuỗi Science, Wavelength, Instrument, Optics |
| Bốn vai trò cho chế độ 4 người chơi | Mission Design Lab, 16 chuyên ngành gộp thành 4 nhóm |
| Cấp bậc tiến trình và ngưỡng "đủ chín để duyệt" | Concept Maturity Levels, ngưỡng 80% |
| Chuỗi pha chơi | Design and Develop Science Missions, sáu bước Identify Need tới Implement |
| Bốn nhóm thẻ thành phần sứ mệnh | Design and Develop Science Missions, bốn segment |
| Thanh Time với sự kiện trễ | CubeSat 101, mục 2.1 tới 2.16 |
| Kiểm tra khối lượng so với sức chở phương tiện phóng | CubeSat 101 (khối lượng 1U tới 12U) và PDF SLS (70 tấn lên LEO) |
| Kiểm tra bao hình payload | CubeSat 101, kích thước 1U, 3U, 6U, giới hạn nhô 6,5 mm |
| Cơ chế nhiên liệu và giới hạn delta-v | Basics of Space Flight chương 3, phương trình Tsiolkovsky |
| Màn hình bản đồ hệ Mặt Trời và vị trí tương đối | NASA Mission Viz, bảng quỹ đạo 9 hành tinh |
| Cơ chế trễ tín hiệu khi điều khiển tàu xa | NASA Mars Facts cộng NASA HRP (20 phút một chiều) |
| Màn "xem lại hành trình" bằng dữ liệu thật | File MolniyaOrbit.txt và .json từ repo mission-viz |
| Báo cáo cuối sứ mệnh | MDL, bộ sản phẩm gồm MEL, sơ đồ khối, ước lượng mass, power, data rate |
| Sự kiện ngẫu nhiên | CubeSat 101, các cột mốc 30 phút triển khai ăng ten và 45 phút bật beacon, cấm phát sóng trước 45 phút |

---

## PHẦN 6 - RESOURCE KHÔNG TRUY CẬP ĐƯỢC VÀ LÝ DO

| Resource | URL | Tình trạng | Lý do | Đã xử lý thế nào |
|---|---|---|---|---|
| GMAT download trên SourceForge | https://sourceforge.net/projects/gmat/ | Không tải được | Cloudflare chặn với thông báo "Sorry, you have been blocked", Ray ID a5ac50df1b836e49 | Không cần thiết cho mục tiêu tài liệu. Đã đọc đầy đủ trang mô tả GMAT trên software.nasa.gov, là nguồn chính thức về chức năng và nền tảng. |
| Trang CSA, truy cập bằng trình duyệt | https://www.asc-csa.gc.ca/eng/youth-educators/digital-games-and-activities.asp | Trình duyệt báo Page.navigate timed out sau 5 giây, trang trắng | Máy chủ CSA phản hồi chậm với trình duyệt tự động | Đã lấy HTML gốc bằng curl kèm User-Agent và bóc text thành công, nội dung đầy đủ đã ghi ở mục 4.9 |
| Hai game RADARSAT và OSIRIS-REx của CSA | https://www.asc-csa.gc.ca/app/game/RADARSAT/index.html và https://www.asc-csa.gc.ca/app/game/OSIRIS-REx/index.html | Mở được khung nhưng không có nội dung tĩnh | Trang index chỉ 1,1 tới 1,2 KB, toàn bộ game nạp bằng JavaScript phía client | Ghi nhận giới hạn. Đã đọc mô tả chính thức trên trang cha, đủ để mô tả mục đích của hai game. |
| Ảnh trong Figure 3 tới Figure 8c của bài CML | trong PDF cml.pdf | Text bóc được nhưng nội dung bảng nằm trong ảnh | CML Matrix và checklist là ảnh scan, không phải bảng text | Ghi nhận giới hạn. Đã đọc phần text mô tả cấu trúc 24 dòng, 7 cột và quy tắc 80%, đủ để áp dụng vào game. Nếu cần nội dung chi tiết từng ô thì phải mở PDF và xem ảnh. |
| Bảng tham số chi tiết trong các slide BioNutrients | trong design_develop.pdf | Một số slide có sơ đồ khối dạng ảnh, text chỉ còn nhãn | Slide là hình vẽ | Ghi nhận. Các con số định lượng chính đều là text và đã trích đủ. |

Không có resource nào trong chín mục chính của tab Resources bị chặn hoàn toàn. Tất cả chín đều đã mở và đọc được nội dung thật.

---

## PHỤ LỤC - ĐƯỜNG DẪN ĐẦY ĐỦ ĐÃ DÙNG

Toàn bộ URL đã truy cập trong quá trình trích xuất, để lần sau không phải tìm lại.

**Trang đề bài và luật chơi**
- https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/
- https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/?tab=details
- https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/?tab=resources
- https://www.spaceappschallenge.org/resources/participant-faqs/
- https://www.spaceappschallenge.org/resources/judging-awards-guide/
- https://www.spaceappschallenge.org/resources/project-submission-guide/
- https://www.spaceappschallenge.org/awards/
- https://www.spaceappschallenge.org/resources/

**PDF đã tải và đọc toàn văn**
- https://www.nasa.gov/wp-content/uploads/2025/04/250323-design-and-develop-science-mission.pdf?emrc=a454cf
- https://www3.nasa.gov/sites/default/files/atoms/files/nasa_csli_cubesat_101_508.pdf
- https://dataverse.jpl.nasa.gov/api/access/datafile/50237
- https://science.nasa.gov/wp-content/uploads/2024/03/gametext.pdf
- https://nasa.github.io/mission-viz/X3Dom/20150918_WebVisualization_of_a_GMAT_GeneratedTrajectory_Part1.pdf
- https://ntrs.nasa.gov/api/citations/20130013034/downloads/20130013034.pdf

**Trang web đã mở**
- https://software.nasa.gov/software/GSC-19468-1
- https://dataverse.jpl.nasa.gov/dataset.xhtml?persistentId=hdl:2014/44299
- https://etd.gsfc.nasa.gov/capabilities/integrated-design-center/mission-design-lab/
- https://nasa.github.io/mission-viz/
- https://nasa.github.io/mission-viz/RMarkdown/ontology_based_orrery_generated_from_R_code.html
- https://nasa.github.io/mission-viz/RMarkdown/Elliptical_Orbit_Design.html
- https://nasa.github.io/mission-viz/X3Dom/WebMissionVisualizationTutorialSeries.html
- https://science.nasa.gov/mission/webb/game-build-it-yourself/
- https://www.spaceappschallenge.org/2023/challenges/visualize-a-space-mission-using-virtual-reality/?tab=details
- https://www.spaceappschallenge.org/2023/challenges/visualize-a-space-mission-using-virtual-reality/?tab=resources
- https://www.asc-csa.gc.ca/eng/youth-educators/digital-games-and-activities.asp
- https://www.asc-csa.gc.ca/eng/youth-educators/activities/game-mission-astronaut.asp
- https://www.asc-csa.gc.ca/eng/satellites/radarsat/activities/game.asp
- https://www.asc-csa.gc.ca/eng/satellites/osiris-rex/activities/game.asp
- https://science.nasa.gov/mars/facts/
- https://www.nasa.gov/hrp/hazard-distance-from-earth
- https://science.nasa.gov/learn/basics-of-space-flight/chapter3-2

**Dữ liệu mẫu tải được**
- https://nasa.github.io/mission-viz/X3Dom/MolniyaOrbit.txt
- https://nasa.github.io/mission-viz/X3Dom/MolniyaOrbit.json
