# Hướng dẫn tạo tài khoản Admin

## Cách 1: Chạy script Python

1. Mở terminal và di chuyển vào thư mục backend:

```bash
cd backend
```

2. Chạy script tạo admin:

```bash
python create_admin.py
```

## Thông tin tài khoản Admin

### Admin 1

- **Email**: admin1@sportclub.com
- **Password**: Admin@123
- **Họ tên**: Admin Hệ Thống 1
- **SĐT**: 0901234567

### Admin 2

- **Email**: admin2@sportclub.com
- **Password**: Admin@456
- **Họ tên**: Admin Hệ Thống 2
- **SĐT**: 0909876543

## Đăng nhập Admin

1. Truy cập: http://localhost:5173/admin/login
2. Nhập email và password của admin
3. Hệ thống sẽ redirect đến `/admin/dashboard` sau khi đăng nhập thành công

## Lưu ý

- Role "admin" đã được thêm vào enum UserRole
- Script sẽ kiểm tra và không tạo lại admin nếu email đã tồn tại
- Mật khẩu được hash bằng bcrypt trước khi lưu vào database
- Admin có quyền truy cập cao nhất trong hệ thống
