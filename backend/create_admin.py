
from sqlalchemy.orm import Session
from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import sys

def create_admin_accounts():
    """Tạo 2 tài khoản admin"""
    
    # Tạo tables nếu chưa tồn tại
    Base.metadata.create_all(bind=engine)
    
    # Tạo session
    db: Session = SessionLocal()
    
    try:
        # Danh sách admin cần tạo
        admins = [
            {
                "email": "admin1@sportclub.com",
                "password": "Admin@123",
                "full_name": "Admin Hệ Thống 1",
                "phone_number": "0901234567",
                "role": "admin"
            },
            {
                "email": "admin2@sportclub.com", 
                "password": "Admin@456",
                "full_name": "Admin Hệ Thống 2",
                "phone_number": "0909876543",
                "role": "admin"
            }
        ]
        
        print("🔧 Đang tạo tài khoản Admin...\n")
        
        for admin_data in admins:
            # Kiểm tra xem email đã tồn tại chưa
            existing_user = db.query(User).filter(User.email == admin_data["email"]).first()
            
            if existing_user:
                print(f"⚠️  Email {admin_data['email']} đã tồn tại!")
                print("   Bỏ qua tạo tài khoản này.\n")
                continue
            
            # Tạo user mới
            new_admin = User(
                email=admin_data["email"],
                hashed_password=get_password_hash(admin_data["password"]),
                full_name=admin_data["full_name"],
                phone_number=admin_data["phone_number"],
                role=admin_data["role"],
                is_active=True
            )
            
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            
            print(f"✅ Đã tạo Admin: {admin_data['full_name']}")
            print(f"   📧 Email: {admin_data['email']}")
            print(f"   🔑 Password: {admin_data['password']}")
            print(f"   👤 Role: {admin_data['role']}")
            print(f"   📱 Phone: {admin_data['phone_number']}\n")
        
        print("=" * 60)
        print("🎉 HOÀN THÀNH!")
        print("=" * 60)
        print("\n📝 THÔNG TIN ĐĂNG NHẬP ADMIN:\n")
        print("Admin 1:")
        print("  Email: admin1@sportclub.com")
        print("  Password: Admin@123\n")
        print("Admin 2:")
        print("  Email: admin2@sportclub.com")
        print("  Password: Admin@456\n")
        print("🔗 Đăng nhập tại: http://localhost:5173/admin/login")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo admin: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_accounts()
