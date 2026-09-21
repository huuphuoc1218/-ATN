# API Reference - Badminton Court Booking

Tài liệu này liệt kê các API chính của hệ thống theo dạng LaTeX để bạn chèn trực tiếp vào báo cáo.

## API Xác thực (Auth API)

\subsubsection{API Xác thực}
\begin{enumerate}
\item \texttt{\textbf{POST /api/auth/register}} — Đăng ký tài khoản mới
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{email, password, full_name, phone_number?, role}|
\item \textit{Response:} \texttt{200 OK} hoặc \texttt{201 Created} kèm JWT token và thông tin người dùng
\item \textit{Ghi chú:} role hợp lệ gồm \texttt{user}, \texttt{owner}, \texttt{enterprise}
\end{itemize}

\item \texttt{\textbf{POST /api/auth/login}} — Đăng nhập tài khoản
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{email, password}|
\item \textit{Response:} JWT token và thông tin người dùng
\end{itemize}

\item \texttt{\textbf{POST /api/auth/google}} — Đăng nhập / đăng ký bằng Google
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{credential, role?}|
\item \textit{Ghi chú:} Hỗ trợ \texttt{user}, \texttt{owner}, \texttt{enterprise}; nếu là đăng ký mới bằng Google thì bắt buộc chọn role trước khi gửi
\item \textit{Response:} JWT token và thông tin người dùng
\end{itemize}
\end{enumerate}

## API Người dùng (User API)

\subsubsection{API Người dùng}
\begin{enumerate}
\item \texttt{\textbf{GET /api/users/me}} — Lấy thông tin tài khoản đang đăng nhập
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Thông tin cá nhân, vai trò, thông tin ngân hàng (nếu có)
\end{itemize}

\item \texttt{\textbf{PUT /api/users/me}} — Cập nhật hồ sơ cá nhân
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{email?, full_name?, phone_number?, avatar_url?, password?, bank_account_number?, bank_account_name?, bank_name?, bank_code?}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} \texttt{200 OK} khi cập nhật thành công
\end{itemize}

\item \texttt{\textbf{POST /api/users/me/avatar}} — Tải ảnh đại diện lên hệ thống
\begin{itemize}[label=$\circ$]
\item \textit{Form Data:} \verb|avatar (file)|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} URL ảnh đại diện mới
\end{itemize}

\item \texttt{\textbf{GET /api/users/}} — Lấy danh sách người dùng
\begin{itemize}[label=$\circ$]
\item \textit{Query:} \texttt{skip?, limit?}
\item \textit{Response:} Danh sách user không bao gồm admin
\end{itemize}

\item \texttt{\textbf{GET /api/users/\{user extunderscore id\}}} — Lấy thông tin người dùng theo ID
\begin{itemize}[label=$\circ$]
\item \textit{Response:} Thông tin người dùng theo ID
\end{itemize}

\item \texttt{\textbf{PUT /api/users/\{user extunderscore id\}}} — Cập nhật thông tin người dùng
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{email?, full_name?, phone_number?, avatar_url?, password?, bank_account_number?, bank_account_name?, bank_name?, bank_code?}|
\item \textit{Response:} \texttt{200 OK} khi cập nhật thành công
\end{itemize}

\item \texttt{\textbf{DELETE /api/users/\{user extunderscore id\}}} — Xóa tài khoản người dùng
\begin{itemize}[label=$\circ$]
\item \textit{Response:} Xóa thành công hoặc lỗi nếu không tồn tại
\end{itemize}

\item \texttt{\textbf{GET /api/users/admin/recent-activity}} — Lấy hoạt động gần đây của admin
\begin{itemize}[label=$\circ$]
\item \textit{Query:} \texttt{limit?}
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách hoạt động của user, yêu cầu sân và quảng cáo
\end{itemize}
\end{enumerate}

## API Quản lý sân (Court API)

\subsubsection{API Quản lý sân}
\begin{enumerate}
\item \texttt{\textbf{POST /api/courts}} — Chủ sân tạo sân mới
\begin{itemize}[label=$\circ$]
\item \textit{Body/Form:} \verb|{court_data, images?}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} \texttt{201 Created}
\end{itemize}

\item \texttt{\textbf{GET /api/courts}} — Lấy danh sách sân công khai
\begin{itemize}[label=$\circ$]
\item \textit{Query:} \texttt{skip?, limit?, booking extunderscore date?, start extunderscore time?, end extunderscore time?}
\item \textit{Response:} Danh sách sân, có thể lọc theo thời gian trống
\end{itemize}

\item \texttt{\textbf{GET /api/courts/my}} — Lấy danh sách sân của chủ sân hiện tại
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách sân thuộc owner đang đăng nhập
\end{itemize}

\item \texttt{\textbf{GET /api/courts/\{court extunderscore id\}}} — Xem chi tiết sân
\begin{itemize}[label=$\circ$]
\item \textit{Response:} Thông tin sân và danh sách sân con
\end{itemize}

\item \texttt{\textbf{PUT /api/courts/\{court extunderscore id\}}} — Cập nhật sân
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|CourtUpdate|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} \texttt{200 OK}
\end{itemize}

\item \texttt{\textbf{DELETE /api/courts/\{court extunderscore id\}}} — Xóa sân
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} \texttt{204 No Content}
\end{itemize}

\item \texttt{\textbf{GET /api/courts/\{court extunderscore id\}/individual-courts}} — Lấy danh sách sân con
\begin{itemize}[label=$\circ$]
\item \textit{Response:} Danh sách sân con theo sân chính
\end{itemize}

\item \texttt{\textbf{PUT /api/individual-courts/\{individual extunderscore court extunderscore id\}}} — Cập nhật sân con
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{name?, is_active?}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} \texttt{200 OK}
\end{itemize}

\item \texttt{\textbf{POST /api/courts/bookings}} — Tạo booking thủ công cho owner
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|BookingCreate|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} \texttt{201 Created}
\end{itemize}

\item \texttt{\textbf{POST /api/upload-images}} — Upload ảnh sân
\begin{itemize}[label=$\circ$]
\item \textit{Form Data:} \verb|images (file[])|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách URL ảnh
\end{itemize}
\end{enumerate}

## API Đặt sân (Booking API)

\subsubsection{API Đặt sân}
\begin{enumerate}
\item \texttt{\textbf{POST /api/bookings/payment-preview}} — Xem trước thanh toán VietQR
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{court_id, booking_date, start_time, end_time}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} QR code, số tiền, thông tin ngân hàng
\end{itemize}

\item \texttt{\textbf{POST /api/bookings/}} — Tạo booking mới
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|BookingCreate|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} \texttt{201 Created} kèm thông tin thanh toán
\end{itemize}

\item \texttt{\textbf{GET /api/bookings/\{booking extunderscore id\}}} — Xem chi tiết booking
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Chi tiết booking
\end{itemize}

\item \texttt{\textbf{PUT /api/bookings/\{booking extunderscore id\}}} — Cập nhật booking
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{status?, booking_status?, payment_status?}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Booking được cập nhật
\end{itemize}

\item \texttt{\textbf{GET /api/bookings/user/my-bookings}} — Lấy booking hiện tại của user
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách booking của user
\end{itemize}

\item \texttt{\textbf{GET /api/bookings/user/my-bookings/history}} — Lịch sử đặt sân của user
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách lịch sử booking kèm sân và vị trí
\end{itemize}

\item \texttt{\textbf{GET /api/bookings/\{booking extunderscore id\}/payment-info}} — Lấy thông tin thanh toán booking
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} QR code, ngân hàng, số tài khoản, số tiền
\end{itemize}

\item \texttt{\textbf{POST /api/bookings/\{booking extunderscore id\}/verify-payment}} — Xác minh thanh toán tự động
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Booking đã xác minh hoặc thông báo lỗi
\end{itemize}

\item \texttt{\textbf{POST /api/bookings/\{booking extunderscore id\}/manual-verify}} — Chủ sân/admin xác minh thanh toán thủ công
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{transaction_id, note?}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Booking đã xác minh
\end{itemize}

\item \texttt{\textbf{POST /api/bookings/\{booking extunderscore id\}/confirm-payment}} — Chủ sân xác nhận đã nhận tiền
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Booking chuyển sang trạng thái active
\end{itemize}

\item \texttt{\textbf{GET /api/bookings/qr-booking/\{token\}}} — Xem booking từ mã QR
\begin{itemize}[label=$\circ$]
\item \textit{Response:} Trang HTML chi tiết booking
\end{itemize}

\item \texttt{\textbf{POST /api/bookings/\{booking extunderscore id\}/invite-codes}} — Tạo mã mời cho booking
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Mã mời, trạng thái và thời gian tạo
\end{itemize}

\item \texttt{\textbf{POST /api/bookings/invite-codes/preview}} — Xem trước mã mời
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{code}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Thông tin booking, sân, người mời
\end{itemize}

\item \texttt{\textbf{POST /api/bookings/invite-codes/respond}} — Chấp nhận/từ chối mã mời
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{code, action}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Trạng thái lời mời sau khi phản hồi
\end{itemize}

\item \texttt{\textbf{POST /api/bookings/invite-codes/send}} — Gửi mã mời cho bạn bè
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{code, friend_user_id}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Thông tin lời mời đã gửi
\end{itemize}

\item \texttt{\textbf{POST /api/bookings/invite-codes/\{invite extunderscore id\}/respond}} — Phản hồi lời mời từ thông báo
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{action}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Trạng thái và thời gian phản hồi
\end{itemize}

\item \texttt{\textbf{GET /api/bookings/invite-codes/\{invite extunderscore id\}/details}} — Xem chi tiết lời mời
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Chi tiết booking invite
\end{itemize}
\end{enumerate}

## API Thông báo và Quảng cáo (Notification / Advertisement API)

\subsubsection{API Thông báo và Quảng cáo}
\begin{enumerate}
\item \texttt{\textbf{GET /api/notifications}} — Lấy danh sách thông báo
\begin{itemize}[label=$\circ$]
\item \textit{Query:} \texttt{skip?, limit?}
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách thông báo của user
\end{itemize}

\item \texttt{\textbf{GET /api/notifications/unread-count}} — Đếm thông báo chưa đọc
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Số lượng thông báo chưa đọc
\end{itemize}

\item \texttt{\textbf{PUT /api/notifications/\{notification extunderscore id\}/read}} — Đánh dấu một thông báo đã đọc
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Thông báo đã đọc
\end{itemize}

\item \texttt{\textbf{POST /api/notifications/mark-all-read}} — Đánh dấu tất cả thông báo đã đọc
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Cập nhật toàn bộ thông báo
\end{itemize}

\item \texttt{\textbf{GET /api/advertisements/public}} — Lấy danh sách quảng cáo đã duyệt
\begin{itemize}[label=$\circ$]
\item \textit{Response:} Danh sách quảng cáo công khai
\end{itemize}

\item \texttt{\textbf{POST /api/advertisements/\{request extunderscore id\}/click}} — Ghi nhận lượt click quảng cáo
\begin{itemize}[label=$\circ$]
\item \textit{Response:} \texttt{200 OK} sau khi ghi nhận click
\end{itemize}

\item \texttt{\textbf{POST /api/enterprise/advertisements}} — Doanh nghiệp tạo yêu cầu quảng cáo
\begin{itemize}[label=$\circ$]
\item \textit{Form Data:} \verb|{name, description, detail_url, image}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Yêu cầu quảng cáo trạng thái pending
\end{itemize}

\item \texttt{\textbf{GET /api/enterprise/advertisements}} — Xem quảng cáo đã duyệt của doanh nghiệp
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách quảng cáo approved
\end{itemize}

\item \texttt{\textbf{GET /api/enterprise/advertisement-requests}} — Xem danh sách yêu cầu quảng cáo của doanh nghiệp
\begin{itemize}[label=$\circ$]
\item \textit{Query:} \texttt{status extunderscore filter?}
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách yêu cầu quảng cáo của enterprise
\end{itemize}

\item \texttt{\textbf{DELETE /api/enterprise/advertisements/\{request extunderscore id\}}} — Xóa yêu cầu/quảng cáo của doanh nghiệp
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} \texttt{204 No Content}
\end{itemize}

\item \texttt{\textbf{GET /api/admin/advertisement-requests}} — Admin xem danh sách yêu cầu quảng cáo
\begin{itemize}[label=$\circ$]
\item \textit{Query:} \texttt{status extunderscore filter?}
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách request theo trạng thái
\end{itemize}

\item \texttt{\textbf{PUT /api/admin/advertisement-requests/\{request extunderscore id\}}} — Admin duyệt hoặc từ chối quảng cáo
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{status, rejection_reason?}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Yêu cầu quảng cáo được cập nhật trạng thái
\end{itemize}

\item \texttt{\textbf{DELETE /api/admin/advertisement-requests/\{request extunderscore id\}}} — Admin xóa yêu cầu quảng cáo
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} \texttt{204 No Content}
\end{itemize}

\item \texttt{\textbf{POST /api/courts/bookings}} — Endpoint booking legacy cho owner
\begin{itemize}[label=$\circ$]
\item \textit{Ghi chú:} Đây là endpoint cũ được giữ để tương thích
\end{itemize}
\end{enumerate}

## API Bạn bè (Friend API)

\subsubsection{API Bạn bè}
\begin{enumerate}
\item \texttt{\textbf{POST /api/friends/requests}} — Gửi lời mời kết bạn
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{email}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Tạo request kết bạn thành công
\end{itemize}

\item \texttt{\textbf{POST /api/friends/requests/\{request extunderscore id\}/respond}} — Phản hồi lời mời kết bạn
\begin{itemize}[label=$\circ$]
\item \textit{Body:} \verb|{action}|
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Trạng thái accepted/rejected
\end{itemize}

\item \texttt{\textbf{GET /api/friends/me}} — Lấy danh sách bạn bè
\begin{itemize}[label=$\circ$]
\item \textit{Header:} \texttt{Authorization: Bearer Token}
\item \textit{Response:} Danh sách bạn bè và trạng thái streak
\end{itemize}
\end{enumerate}

## API Webhook

\subsubsection{API Webhook}
\begin{enumerate}
\item \texttt{\textbf{POST /webhooks/bank-transaction}} — Nhận webhook giao dịch ngân hàng
\begin{itemize}[label=$\circ$]
\item \textit{Body:} JSON giao dịch ngân hàng
\item \textit{Header:} \texttt{x-signature?}
\item \textit{Response:} Trạng thái xử lý giao dịch
\end{itemize}

\item \texttt{\textbf{GET /webhooks/bank-transaction/test}} — Kiểm tra webhook hoạt động
\begin{itemize}[label=$\circ$]
\item \textit{Response:} \texttt{\{status: ok\}}
\end{itemize}
\end{enumerate}

## Ghi chú chung

\begin{itemize}
\item Tất cả API trong nhóm \texttt{/api/...} đều được gắn prefix gốc \texttt{/api} trong FastAPI.
\item Các API yêu cầu xác thực cần gửi \texttt{Authorization: Bearer Token}.
\item Một số endpoint quản trị chỉ cho phép vai trò \texttt{admin}.
\item Một số endpoint chỉ cho phép \texttt{owner} hoặc \texttt{enterprise} tùy nghiệp vụ.
\end{itemize}
