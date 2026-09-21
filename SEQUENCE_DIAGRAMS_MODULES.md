## Sequence Diagram - Dang nhap

```plantuml
@startuml
hide footbox
skinparam shadowing false
skinparam sequence {
  ArrowColor #1f2937
  LifeLineBorderColor #334155
  LifeLineBackgroundColor #f8fafc
  ParticipantBorderColor #334155
  ParticipantBackgroundColor #eef2ff
}

title Sequence Diagram - Dang nhap

actor User
participant Frontend
participant "Auth API" as AuthAPI
participant "User Service" as UserService
database DB
participant "Security Service" as Security

User -> Frontend: Nhap email + password\nNhan Dang nhap
Frontend -> AuthAPI: POST /api/auth/login
AuthAPI -> UserService: get_user_by_email(email)
UserService -> DB: SELECT * FROM users WHERE email = ?
DB --> UserService: user / null
UserService --> AuthAPI: ket qua user

alt User khong ton tai
  AuthAPI --> Frontend: 401 Email khong ton tai
  Frontend --> User: Hien thi thong bao loi
else User ton tai
  AuthAPI -> Security: verify_password(plain, hashed)
  Security --> AuthAPI: true / false
  alt Mat khau sai
    AuthAPI --> Frontend: 401 Mat khau khong chinh xac
    Frontend --> User: Hien thi thong bao loi
  else Mat khau dung
    AuthAPI -> Security: create_access_token(sub=email)
    Security --> AuthAPI: JWT token
    AuthAPI --> Frontend: 200 token + user info
    Frontend -> Frontend: Luu localStorage (token, user)
    Frontend --> User: Redirect theo role
  end
end
@enduml
```

---

## Sequence Diagram - Dang tai san moi cua owner

```plantuml
@startuml
hide footbox
skinparam shadowing false
skinparam sequence {
  ArrowColor #1f2937
  LifeLineBorderColor #334155
  LifeLineBackgroundColor #f8fafc
  ParticipantBorderColor #334155
  ParticipantBackgroundColor #ecfeff
}

title Sequence Diagram - Dang tai san moi cua owner

actor Owner
participant Frontend
participant "Auth Middleware" as AuthMW
participant "Court Request API" as RequestAPI
participant "Upload Service" as UploadSvc
database DB
participant "Notification Service" as NotiSvc

Owner -> Frontend: Nhap thong tin san + anh + khung gio\nNhan Gui yeu cau
Frontend -> RequestAPI: POST /api/court-requests (multipart/json)
RequestAPI -> AuthMW: Verify JWT + role owner
AuthMW --> RequestAPI: owner hop le / tu choi

alt Khong dung role owner
  RequestAPI --> Frontend: 403 Forbidden
  Frontend --> Owner: Hien thi loi phan quyen
else Hop le
  loop Moi file anh
    RequestAPI -> UploadSvc: upload(image)
    UploadSvc --> RequestAPI: image_url
  end
  RequestAPI -> DB: INSERT court_requests(status=pending,...)
  DB --> RequestAPI: request_id
  RequestAPI -> NotiSvc: notify admins(request_created)
  NotiSvc -> DB: INSERT notifications
  DB --> NotiSvc: ok
  RequestAPI --> Frontend: 201 request detail
  Frontend --> Owner: Thong bao gui yeu cau thanh cong
end
@enduml
```

---

## Sequence Diagram - Tim kiem san

```plantuml
@startuml
hide footbox
skinparam shadowing false
skinparam sequence {
  ArrowColor #1f2937
  LifeLineBorderColor #334155
  LifeLineBackgroundColor #f8fafc
  ParticipantBorderColor #334155
  ParticipantBackgroundColor #fefce8
}

title Sequence Diagram - Tim kiem san

actor User
participant Frontend
participant "Court API" as CourtAPI
participant "Court Service" as CourtSvc
database DB

User -> Frontend: Nhap ngay, gio bat dau, gio ket thuc\nNhan Tim kiem
Frontend -> CourtAPI: GET /api/courts?booking_date&start_time&end_time
CourtAPI -> CourtSvc: validate_filters(...)

alt Filter khong hop le
  CourtSvc --> CourtAPI: invalid
  CourtAPI --> Frontend: 400 Bad Request
  Frontend --> User: Hien thi loi bo loc
else Filter hop le
  CourtSvc -> DB: SELECT courts + individual_courts
  DB --> CourtSvc: danh sach courts
  CourtSvc -> DB: SELECT bookings trung khung gio
  DB --> CourtSvc: bookings overlap
  CourtSvc -> CourtSvc: Loc san kha dung
  CourtSvc --> CourtAPI: available courts
  CourtAPI --> Frontend: 200 list courts
  Frontend --> User: Hien thi ket qua tim kiem
end
@enduml
```

---

## Sequence Diagram - Dat san va thanh toan

```plantuml
@startuml
hide footbox
skinparam shadowing false
skinparam sequence {
  ArrowColor #1f2937
  LifeLineBorderColor #334155
  LifeLineBackgroundColor #f8fafc
  ParticipantBorderColor #334155
  ParticipantBackgroundColor #f0fdf4
}

title Sequence Diagram - Dat san va thanh toan

actor User
participant Frontend
participant "Booking API" as BookingAPI
participant "Booking Service" as BookingSvc
participant "VietQR Service" as VietQR
database DB
participant "Email Service" as EmailSvc

User -> Frontend: Chon san + khung gio\nNhan Dat san
Frontend -> BookingAPI: POST /api/bookings/payment-preview
BookingAPI -> BookingSvc: check_availability + calc_price
BookingSvc -> DB: Query bookings overlap
DB --> BookingSvc: ket qua overlap

alt Het cho
  BookingSvc --> BookingAPI: conflict
  BookingAPI --> Frontend: 409 slot da duoc dat
  Frontend --> User: Hien thi loi va goi y khung gio khac
else Con cho
  BookingSvc -> VietQR: generate_qr(amount, content)
  VietQR --> BookingSvc: qr_url
  BookingSvc --> BookingAPI: preview data
  BookingAPI --> Frontend: 200 payment preview
  Frontend --> User: Hien thi QR thanh toan

  User -> Frontend: Xac nhan dat san
  Frontend -> BookingAPI: POST /api/bookings
  BookingAPI -> BookingSvc: create_booking(...)
  BookingSvc -> DB: INSERT bookings(status=pending/confirmed)
  DB --> BookingSvc: booking_id
  BookingSvc --> BookingAPI: booking + payment info
  BookingAPI --> Frontend: 201 created

  opt Owner xac nhan da nhan tien
    Frontend -> BookingAPI: POST /api/bookings/{id}/confirm-payment
    BookingAPI -> BookingSvc: mark_paid_and_active
    BookingSvc -> DB: UPDATE booking status
    DB --> BookingSvc: ok
    BookingSvc -> EmailSvc: send_booking_qr_email
    EmailSvc --> BookingSvc: sent
    BookingSvc --> BookingAPI: updated booking
    BookingAPI --> Frontend: 200 success
  end

  Frontend --> User: Hien thi dat san thanh cong
end
@enduml
```

---

## Sequence Diagram - Thong ke doanh thu

```plantuml
@startuml
hide footbox
skinparam shadowing false
skinparam sequence {
  ArrowColor #1f2937
  LifeLineBorderColor #334155
  LifeLineBackgroundColor #f8fafc
  ParticipantBorderColor #334155
  ParticipantBackgroundColor #dcfce7
}

title Sequence Diagram - Thong ke doanh thu

actor Owner
participant Frontend
participant "Booking Stats API" as StatsAPI
participant "Booking Service" as BookingSvc
database DB

Owner -> Frontend: Chon khoang thoi gian, san, trang thai
Frontend -> StatsAPI: GET /api/courts/owner/bookings
Frontend -> StatsAPI: GET /api/courts/owner/bookings/summary

StatsAPI -> BookingSvc: verify_owner_access
BookingSvc -> DB: Query bookings by owner + filters
DB --> BookingSvc: booking rows
BookingSvc -> BookingSvc: Tinh tong doanh thu/KPI
BookingSvc --> StatsAPI: detail + summary
StatsAPI --> Frontend: 200 thong ke

Frontend -> Frontend: Map data cho KPI + chart + table
Frontend --> Owner: Hien thi dashboard doanh thu
@enduml
```

---

## Sequence Diagram - Quan li san cho admin

```plantuml
@startuml
hide footbox
skinparam shadowing false
skinparam sequence {
  ArrowColor #1f2937
  LifeLineBorderColor #334155
  LifeLineBackgroundColor #f8fafc
  ParticipantBorderColor #334155
  ParticipantBackgroundColor #fee2e2
}

title Sequence Diagram - Quan li san cho admin

actor Admin
participant Frontend
participant "Court Request API" as RequestAPI
participant "Court Service" as CourtSvc
participant "Notification Service" as NotiSvc
database DB

Admin -> Frontend: Mo danh sach yeu cau san
Frontend -> RequestAPI: GET /api/court-requests
RequestAPI -> DB: SELECT court_requests
DB --> RequestAPI: pending/approved/rejected
RequestAPI --> Frontend: 200 list requests

Admin -> Frontend: Chon phe duyet/tu choi request
Frontend -> RequestAPI: PUT /api/court-requests/{id} (status)
RequestAPI -> CourtSvc: review_request(request_id, status)
CourtSvc -> DB: SELECT request by id
DB --> CourtSvc: request data

alt Approve
  CourtSvc -> DB: INSERT/UPDATE courts + individual_courts
  DB --> CourtSvc: court_id
  CourtSvc -> DB: UPDATE request status=approved
  DB --> CourtSvc: ok
else Reject
  CourtSvc -> DB: UPDATE request status=rejected + reason
  DB --> CourtSvc: ok
end

CourtSvc -> NotiSvc: notify owner about result
NotiSvc -> DB: INSERT notifications
DB --> NotiSvc: ok
RequestAPI --> Frontend: 200 reviewed result
Frontend --> Admin: Cap nhat UI thanh cong
@enduml
```

---

## Sequence Diagram - Dang quang cao

```plantuml
@startuml
hide footbox
skinparam shadowing false
skinparam sequence {
  ArrowColor #1f2937
  LifeLineBorderColor #334155
  LifeLineBackgroundColor #f8fafc
  ParticipantBorderColor #334155
  ParticipantBackgroundColor #fae8ff
}

title Sequence Diagram - Dang quang cao

actor Enterprise
participant Frontend
participant "Advertisement API" as AdAPI
participant "Upload Service" as UploadSvc
participant "Admin Review API" as AdminAPI
participant "Notification Service" as NotiSvc
database DB

Enterprise -> Frontend: Nhap noi dung quang cao + image + detail URL
Frontend -> AdAPI: POST /api/admin/advertisement-requests
AdAPI -> UploadSvc: upload(image)
UploadSvc --> AdAPI: image_url
AdAPI -> DB: INSERT advertisement_requests(status=pending)
DB --> AdAPI: request_id
AdAPI --> Frontend: 201 created
Frontend --> Enterprise: Thong bao gui yeu cau thanh cong

== Admin review ==
actor Admin
Admin -> Frontend: Mo trang duyet quang cao
Frontend -> AdminAPI: GET /api/admin/advertisement-requests
AdminAPI -> DB: SELECT requests
DB --> AdminAPI: list requests
AdminAPI --> Frontend: 200 list

Admin -> Frontend: Phe duyet / Tu choi
Frontend -> AdminAPI: PUT /api/admin/advertisement-requests/{id}
AdminAPI -> DB: UPDATE request status
DB --> AdminAPI: ok

opt Neu approved
  AdminAPI -> DB: INSERT advertisements (published)
  DB --> AdminAPI: ad_id
end

AdminAPI -> NotiSvc: notify enterprise result
NotiSvc -> DB: INSERT notifications
DB --> NotiSvc: ok
AdminAPI --> Frontend: 200 reviewed
Frontend --> Admin: Cap nhat ket qua
@enduml
```
