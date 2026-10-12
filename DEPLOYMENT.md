# Triển khai production

Kiến trúc phù hợp với repository hiện tại:

```text
Vue 3 + Vite (frontend) -> Vercel
FastAPI (backend)       -> Render Web Service
PostgreSQL               -> Supabase Database
Ảnh tải lên              -> Cloudinary
```

> Supabase là nền tảng backend/database, không phải nơi deploy trực tiếp
> frontend Vue. Frontend nên deploy trên Vercel (hoặc Render Static Site).

## 1. Chuẩn bị bảo mật

- Không commit `.env`, mật khẩu PostgreSQL, SMTP password, Cloudinary API secret
  hoặc JWT secret.
- Các credential từng xuất hiện trong mã nguồn/lịch sử Git phải được đổi hoặc
  thu hồi trước khi đưa hệ thống lên production.
- Tạo JWT secret mới đủ dài, riêng cho production.

## 2. Tạo PostgreSQL trên Supabase

1. Tạo project tại [Supabase](https://supabase.com).
2. Vào **Project Settings > Database > Connect** và chọn thông tin kết nối
   dạng **Session pooler** hoặc **Direct connection**.
3. Lưu các giá trị `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USER` và
   `DB_PASSWORD`. Không dùng `service_role` key cho kết nối PostgreSQL.
4. Di chuyển schema/dữ liệu từ PostgreSQL local bằng pgAdmin hoặc
   `pg_dump`/`pg_restore`.
5. Kiểm tra bảng và quyền truy cập bằng SQL Editor/pgAdmin.

Backend hiện tạo các bảng còn thiếu khi khởi động bằng
`Base.metadata.create_all`; dữ liệu production nên được backup trước mỗi lần
thay đổi schema.

## 3. Deploy backend FastAPI trên Render

Tạo **New > Web Service**, kết nối GitHub repository và đặt:

- **Root Directory:** `backend`
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Thêm các Environment Variables sau trong Render:

```text
DB_HOST=...
DB_PORT=5432
DB_DATABASE=postgres
DB_USER=postgres.<project-ref>
DB_PASSWORD=...
PGSSLMODE=require
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
GOOGLE_CLIENT_ID=...
BACKEND_PUBLIC_BASE_URL=https://<render-service>.onrender.com
BACKEND_CORS_ORIGINS=http://localhost:5173
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
CLOUDINARY_FOLDER=pickleball
```

For email on Render, use Resend over HTTPS instead of Gmail SMTP:

```text
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=onboarding@resend.dev
```

The `onboarding@resend.dev` sender is suitable for initial testing. For
production delivery to arbitrary recipients, verify a domain in Resend and use
an address from that verified domain. `RESEND_API_KEY` must only be configured
on Render; never expose it in the frontend.

`BACKEND_CORS_ORIGINS` có thể là danh sách phân tách bằng dấu phẩy. Sau khi có
domain Vercel, cập nhật thành:

```text
BACKEND_CORS_ORIGINS=https://<vercel-project>.vercel.app
```

Không nên lưu ảnh trên filesystem của Render vì filesystem ephemeral. Dự án
đã hỗ trợ Cloudinary và sẽ lưu URL ảnh trong PostgreSQL.

Kiểm tra sau khi deploy:

- `https://<render-service>.onrender.com/health` trả về `{"status":"healthy"}`
- `https://<render-service>.onrender.com/docs` mở được Swagger UI

## 4. Deploy frontend Vue/Vite trên Vercel

1. Chọn **Add New > Project**, import cùng GitHub repository.
2. Đặt **Root Directory** là `frontend`.
3. Đặt:
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Thêm Environment Variables:

```text
VITE_API_BASE_URL=https://<render-service>.onrender.com/api
VITE_GOOGLE_CLIENT_ID=<google-client-id>
```

5. Deploy lại sau khi thay đổi environment variables.

`frontend/vercel.json` đã có rewrite về `index.html`, nên các route của
Vue Router khi refresh không bị 404.

## 5. Đồng bộ CORS và OAuth

Sau khi Vercel cấp domain chính thức:

1. Đặt `BACKEND_CORS_ORIGINS` trên Render là domain Vercel chính xác, không
   thêm dấu `/` cuối URL.
2. Nếu dùng domain custom, thêm domain đó vào cùng biến, phân tách bằng dấu
   phẩy.
3. Cập nhật **Authorized JavaScript origins** và **Authorized redirect URIs**
   trong Google Cloud Console nếu dùng Google Sign-In.
4. Redeploy backend sau khi đổi CORS và redeploy frontend sau khi đổi Vite env.

## 6. Kiểm tra production

```text
GET /health
GET /docs
Đăng ký/đăng nhập
Google Sign-In
Tạo sân và tải ảnh
Đặt sân, thanh toán/QR và email (nếu bật SMTP)
Refresh trực tiếp các route frontend
```

Nếu frontend vẫn gọi `localhost`, kiểm tra `VITE_API_BASE_URL` trên Vercel và
build deployment mới. Nếu gặp CORS, kiểm tra origin trên trình duyệt và giá
trị `BACKEND_CORS_ORIGINS` trên Render.
