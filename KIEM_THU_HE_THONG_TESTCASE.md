\section{Kiểm thử hệ thống}

\subsection{Đăng nhập người dùng}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Không nhập Email & Email: rỗng, Mật khẩu: bất kỳ & Thông báo lỗi "Please fill out this field" & Passed \\
\hline
2 & Không nhập Mật khẩu & Email: khoa@gmail.com, Mật khẩu: rỗng & Thông báo lỗi "Please fill out this field" & Passed \\
\hline
3 & Sai mật khẩu & Email: khoa@gmail.com, Mật khẩu: sai123 & Thông báo lỗi đăng nhập không thành công & Passed \\
\hline
4 & Sai tài khoản & Email: khongtontai@gmail.com, Mật khẩu: khoathi123 & Thông báo lỗi đăng nhập không thành công & Passed \\
\hline
5 & Email không hợp lệ & Email: khoakaiz.gmail.com, Mật khẩu: khoathi123 & Thông báo lỗi định dạng email không hợp lệ & Passed \\
\hline
6 & Đăng nhập thành công & Email: khoa@gmail.com, Mật khẩu: khoathi123 & Điều hướng đúng trang theo vai trò user & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Đăng nhập người dùng}
\end{table}

\subsection{Đăng ký tài khoản}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Bỏ trống họ tên & Full name: rỗng, Email hợp lệ, Mật khẩu hợp lệ & Hiển thị lỗi bắt buộc nhập họ tên & Passed \\
\hline
2 & Email đã tồn tại & Email: khoa@gmail.com, Mật khẩu: khoathi123 & Hiển thị thông báo email đã được sử dụng & Passed \\
\hline
3 & Mật khẩu quá ngắn & Mật khẩu: 12345 & Hiển thị lỗi không đạt điều kiện mật khẩu & Passed \\
\hline
4 & Xác nhận mật khẩu không khớp & Mật khẩu: khoathi123, Nhập lại: khoathi12 & Hiển thị lỗi xác nhận mật khẩu không khớp & Passed \\
\hline
5 & Đăng ký user thành công & Dữ liệu hợp lệ vai trò user & Tạo tài khoản và đăng nhập tự động hoặc điều hướng đăng nhập & Passed \\
\hline
6 & Đăng ký owner/enterprise từ query role & role=owner hoặc enterprise, dữ liệu hợp lệ & Tạo đúng tài khoản theo vai trò yêu cầu & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Đăng ký tài khoản}
\end{table}

\subsection{Xem danh sách sân và chi tiết sân}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Tải danh sách sân công khai & Truy cập trang /court & Danh sách sân hiển thị đầy đủ theo API /courts & Passed \\
\hline
2 & Tìm kiếm theo tên sân & Keyword: NP Sport & Danh sách được lọc đúng theo từ khóa & Passed \\
\hline
3 & Lọc theo địa điểm & Khu vực: TP.HCM & Chỉ hiển thị sân thuộc khu vực được chọn & Passed \\
\hline
4 & Xem chi tiết sân hợp lệ & court id tồn tại & Hiển thị thông tin sân, ảnh và khung giờ/sân con & Passed \\
\hline
5 & Xem chi tiết sân không tồn tại & court id: 999999 & Hiển thị lỗi không tìm thấy sân & Passed \\
\hline
6 & Dữ liệu ảnh sân bị thiếu & Court có ảnh rỗng & UI vẫn hiển thị placeholder, không vỡ layout & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Xem danh sách và chi tiết sân}
\end{table}

\subsection{Đặt sân và thanh toán}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Đặt sân khi chưa đăng nhập & Truy cập /booking/:id khi chưa có token & Bị chặn và điều hướng về trang đăng nhập & Passed \\
\hline
2 & Tạo payment preview hợp lệ & Chọn sân con + ngày + khung giờ hợp lệ & Trả về số tiền và thông tin chuyển khoản hợp lệ & Passed \\
\hline
3 & Trùng lịch đặt sân & Chọn sân con và time slot đã có booking & Thông báo lỗi trùng lịch, không tạo booking mới & Passed \\
\hline
4 & Xác nhận thanh toán thành công & booking id hợp lệ + giao dịch đúng nội dung & Cập nhật trạng thái booking thành đã thanh toán & Passed \\
\hline
5 & Verify thanh toán thất bại & booking id hợp lệ + không có giao dịch khớp & Trả về trạng thái chưa thanh toán và thông báo phù hợp & Passed \\
\hline
6 & Truy cập QR booking hợp lệ & token QR còn hiệu lực & Hiển thị trang xác nhận/check-in booking hợp lệ & Passed \\
\hline
7 & Cập nhật booking hợp lệ & booking id của chính user + khung giờ hợp lệ & Booking được cập nhật và trả dữ liệu mới & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Đặt sân và thanh toán}
\end{table}

\subsection{Lịch sử đặt sân người dùng}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Xem danh sách booking hiện tại & User: Nguyễn Văn An (user_id=25, email: an.nguyen@gmail.com), có 3 booking: BK1021, BK1033, BK1040; đăng nhập bằng token hợp lệ & Trả về danh sách booking của user hiện tại & Passed \\
\hline
2 & Xem lịch sử booking & User Nguyễn Văn An có lịch sử: BK0988 (12/04/2026 - completed), BK1002 (20/04/2026 - cancelled), BK1021 (27/04/2026 - confirmed) & Trả về lịch sử kèm trạng thái theo thời gian & Passed \\
\hline
3 & Không có booking nào & User mới: le.thuylinh.new@gmail.com (tạo ngày 29/04/2026), chưa phát sinh booking nào & API trả về mảng rỗng, UI hiển thị empty state & Passed \\
\hline
4 & Token không hợp lệ & Token của user Nguyễn Văn An đã hết hạn (exp < thời điểm request) & Trả về 401 Unauthorized & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Lịch sử đặt sân người dùng}
\end{table}

\subsection{Mời bạn vào trận bằng mã mời}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Tạo mã mời hợp lệ & POST /bookings/\{booking_id\}/invite-codes với booking thuộc user & Tạo mã mời thành công, trả mã và thời hạn & Passed \\
\hline
2 & Tạo mã mời cho booking không thuộc user & booking_id không phải chủ booking & Trả lỗi quyền truy cập (403/404) & Passed \\
\hline
3 & Preview mã mời hợp lệ & POST /bookings/invite-codes/preview với code còn hiệu lực & Trả về thông tin trận trước khi phản hồi & Passed \\
\hline
4 & Mã mời hết hạn & code đã hết hạn & Trả thông báo mã mời không hợp lệ hoặc hết hạn & Passed \\
\hline
5 & Chấp nhận lời mời & respond=accept trên mã hợp lệ & Cập nhật trạng thái lời mời thành accepted & Passed \\
\hline
6 & Từ chối lời mời & respond=reject trên mã hợp lệ & Cập nhật trạng thái lời mời thành rejected & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Mời bạn vào trận}
\end{table}

\subsection{Quản lý bạn bè}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Gửi lời mời kết bạn hợp lệ & POST /friends/requests với user đích tồn tại & Tạo lời mời kết bạn thành công & Passed \\
\hline
2 & Gửi lời mời cho chính mình & from_id = to_id & Trả lỗi validation, không tạo request & Passed \\
\hline
3 & Chấp nhận lời mời kết bạn & POST /friends/requests/\{id\}/respond với action=accept & Tạo quan hệ bạn bè hai chiều & Passed \\
\hline
4 & Từ chối lời mời kết bạn & action=reject & Cập nhật request sang rejected & Passed \\
\hline
5 & Lấy danh sách bạn bè của tôi & GET /friends/me & Trả về danh sách bạn bè + pending requests & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Quản lý bạn bè}
\end{table}

\subsection{Thông báo hệ thống}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Lấy danh sách thông báo & GET /notifications với token hợp lệ & Trả về danh sách thông báo theo user đăng nhập & Passed \\
\hline
2 & Đếm thông báo chưa đọc & GET /notifications/unread-count & Trả về số lượng chưa đọc chính xác & Passed \\
\hline
3 & Đánh dấu đã đọc 1 thông báo & PUT /notifications/\{id\}/read & Thông báo chuyển trạng thái read=true & Passed \\
\hline
4 & Đánh dấu tất cả đã đọc & POST /notifications/mark-all-read & Tất cả thông báo của user chuyển sang đã đọc & Passed \\
\hline
5 & Đánh dấu thông báo không thuộc user & notification_id của user khác & Trả lỗi quyền truy cập phù hợp & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Thông báo hệ thống}
\end{table}

\subsection{Owner quản lý sân}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Tạo sân mới hợp lệ & POST /courts với role owner, dữ liệu đầy đủ & Tạo sân thành công, trả về thông tin sân & Passed \\
\hline
2 & Tạo sân thiếu trường bắt buộc & Thiếu tên sân hoặc địa chỉ & Trả lỗi validation 422 & Passed \\
\hline
3 & Cập nhật sân của chính owner & PUT /courts/\{id\} với owner sở hữu sân & Cập nhật thông tin sân thành công & Passed \\
\hline
4 & Xóa sân của chính owner & DELETE /courts/\{id\} & Xóa thành công và không còn trong danh sách & Passed \\
\hline
5 & Owner truy cập sân của owner khác & PUT/DELETE court không thuộc quyền & Trả lỗi 403 Forbidden & Passed \\
\hline
6 & Cập nhật sân con (individual court) & PUT /individual-courts/\{id\} với dữ liệu hợp lệ & Thông tin sân con được cập nhật đúng & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Owner quản lý sân}
\end{table}

\subsection{Owner theo dõi lịch đặt và doanh thu}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Xem danh sách booking của owner & GET /owner/bookings với token owner & Trả về booking thuộc các sân của owner & Passed \\
\hline
2 & Lọc booking theo ngày & Tham số ngày hợp lệ & Danh sách trả về đúng bộ lọc ngày & Passed \\
\hline
3 & Xem tổng quan booking & GET /owner/bookings/summary & Trả về thống kê tổng số trận, doanh thu, tỷ lệ lấp đầy & Passed \\
\hline
4 & User thường truy cập endpoint owner & role user gọi /owner/bookings & Trả lỗi 403 Forbidden & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Owner theo dõi lịch đặt và doanh thu}
\end{table}

\subsection{Enterprise quản lý quảng cáo}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Tạo yêu cầu quảng cáo hợp lệ & POST /enterprise/advertisements với ảnh + nội dung hợp lệ & Tạo yêu cầu quảng cáo ở trạng thái pending & Passed \\
\hline
2 & Upload ảnh quảng cáo sai định dạng & File .txt hoặc kích thước vượt giới hạn & Trả lỗi upload và không tạo quảng cáo & Passed \\
\hline
3 & Xem danh sách quảng cáo của enterprise & GET /enterprise/advertisements & Hiển thị đúng danh sách theo tài khoản hiện tại & Passed \\
\hline
4 & Xóa quảng cáo do chính enterprise tạo & DELETE /enterprise/advertisements/\{id\} & Xóa thành công khỏi hệ thống & Passed \\
\hline
5 & Người dùng public xem quảng cáo & GET /advertisements/public & Trả về danh sách quảng cáo đã được duyệt & Passed \\
\hline
6 & Ghi nhận lượt click quảng cáo & POST /advertisements/\{id\}/click & Tăng bộ đếm click cho quảng cáo tương ứng & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Enterprise quản lý quảng cáo}
\end{table}

\subsection{Admin quản trị hệ thống}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Admin đăng nhập thành công & Email: admin.system@courtgo.vn, Mật khẩu: Admin@123 & Điều hướng đến /admin/profile & Passed \\
\hline
2 & Lấy danh sách user & Admin ID 1; trang 1; kích thước 10; từ khóa nguyen; vai trò user & Trả về danh sách user phân trang/filter đúng & Passed \\
\hline
3 & Cập nhật thông tin user bất kỳ & User ID 27; họ tên Lê Minh Khoa; SĐT 0909123456; trạng thái active & User được cập nhật đúng thông tin & Passed \\
\hline
4 & Xóa user bất kỳ & User ID 44; không có booking active; không thuộc vai trò admin hoặc owner & User bị xóa hoặc soft-delete theo nghiệp vụ & Passed \\
\hline
5 & Duyệt yêu cầu sân & Yêu cầu sân ID 105 của owner nguyenthanhson.owner@gmail.com; trạng thái pending & Yêu cầu chuyển approved và phát sinh thông báo & Passed \\
\hline
6 & Từ chối yêu cầu sân & Yêu cầu sân ID 106; lý do: Thiếu giấy tờ chứng minh quyền khai thác sân & Yêu cầu chuyển rejected, lưu lý do từ chối & Passed \\
\hline
7 & Duyệt quảng cáo enterprise & Yêu cầu quảng cáo ID 58 của enterprise fitplus@brand.vn; nội dung hợp lệ; trạng thái pending & Quảng cáo được chuyển trạng thái approved & Passed \\
\hline
8 & User thường truy cập API admin & Tài khoản user thường khoa@gmail.com; đăng nhập hợp lệ nhưng truy cập chức năng quản trị & Trả lỗi 403 Forbidden & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Admin quản trị hệ thống}
\end{table}

\subsection{Phân quyền và điều hướng frontend}
\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{|C{1cm}|L{3cm}|L{3.5cm}|L{3.5cm}|X|}
\hline
ID & Test Case & Test Data & Kết quả mong muốn & Trạng thái \\ [0.5ex]
\hline
1 & Chưa đăng nhập vào route cần auth & Truy cập /booking/:id khi chưa có token & Bị redirect về /login & Passed \\
\hline
2 & Sai role vào route restricted & User role=user truy cập /admin/users & Bị chuyển về /user/home & Passed \\
\hline
3 & Đã đăng nhập truy cập /login & Token hợp lệ và user trong localStorage & Bị redirect về home theo role & Passed \\
\hline
4 & Admin đã đăng nhập truy cập /admin/login & Role admin hợp lệ & Bị redirect về /admin/profile & Passed \\
\hline
5 & Truy cập root khi đã đăng nhập & Truy cập / với token + user hợp lệ & Redirect đúng /\{role\}/home hoặc /admin/profile & Passed \\
\hline
\end{tabularx}
\caption{Test case cho chức năng Phân quyền và điều hướng frontend}
\end{table}
