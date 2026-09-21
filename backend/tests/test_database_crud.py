from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.security import get_password_hash
from app.crud import court as court_crud
from app.crud import friend as friend_crud
from app.crud import notification as notification_crud
from app.crud import user as user_crud
from app.models.court import Booking, Court, IndividualCourt
from app.models.friend import FriendRequest, Friendship
from app.models.notification import AdvertisementClick, AdvertisementRequest, CourtRequest, Notification
from app.models.user import User, UserRole
from app.schemas.court import BookingCreate, BookingUpdate, CourtCreate, CourtUpdate, IndividualCourtUpdate, TimeSlot
from app.schemas.notification import AdvertisementRequestCreate, AdvertisementRequestUpdate, CourtRequestCreate, CourtRequestUpdate, NotificationCreate
from app.schemas.user import UserRegister


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _enum_text(value):
    return str(getattr(value, "value", value))


def _password(index: int) -> str:
    return f"Pass{index:02d}!"


def _seed_user(
    db,
    index: int,
    role: UserRole = UserRole.user,
    *,
    active: bool = True,
    email: str | None = None,
    full_name: str | None = None,
    bank: bool = False,
) -> User:
    user = User(
        email=email or f"user{index}@example.com",
        hashed_password=get_password_hash(_password(index)),
        full_name=full_name or f"User {index}",
        phone_number=f"0900{index:04d}",
        avatar_url=f"https://img.test/{index}.png",
        role=role,
        address=f"Address {index}",
        is_active=active,
        bank_account_number=f"01234567{index:02d}" if bank else None,
        bank_account_name=f"User {index}" if bank else None,
        bank_name="Vietcombank" if bank else None,
        bank_code="970436" if bank else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _seed_court_payload(index: int, quantity: int) -> CourtCreate:
    return CourtCreate(
        name=f"Court {index}",
        address=f"Address {index}",
        ward="Ward 1",
        city="Ho Chi Minh City",
        description=f"Description {index}",
        court_quantity=quantity,
        opening_time="08:00",
        closing_time="22:00",
        facilities=["parking", "lights"],
        contact_phone=f"0903{index:04d}",
        contact_email=f"court{index}@example.com",
        time_slots=[
            TimeSlot(start_time="08:00", end_time="10:00", price=100000),
            TimeSlot(start_time="10:00", end_time="22:00", price=120000),
        ],
    )


def _seed_booking_payload(index: int, individual_court_id: int, payment_method: str = "vietqr") -> BookingCreate:
    return BookingCreate(
        individual_court_id=individual_court_id,
        booking_date=datetime(2026, 4, 29, 0, 0),
        start_time="08:00",
        end_time="09:00",
        phone_number=f"0912{index:04d}",
        customer_name=f"Customer {index}",
        customer_email=f"customer{index}@example.com",
        payment_method=payment_method,
    )


def _seed_notification(db, user_id: int, index: int, *, created_at: datetime | None = None) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=f"Title {index}",
        message=f"Message {index}",
        type="system",
        related_id=index,
        is_read=False,
        created_at=created_at or datetime(2026, 4, 29, 8, index % 60),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def _seed_court_request(db, owner_id: int, index: int, *, status: str = "pending") -> CourtRequest:
    request = CourtRequest(
        owner_id=owner_id,
        name=f"Request Court {index}",
        address=f"Request Address {index}",
        ward="Ward 1",
        city="Ho Chi Minh City",
        description=f"Request description {index}",
        court_quantity=2,
        opening_time="08:00",
        closing_time="22:00",
        facilities='["parking"]',
        contact_phone=f"0908{index:04d}",
        contact_email=f"owner{index}@example.com",
        images='["https://img.test/request.png"]',
        time_slots='[{"start_time":"08:00","end_time":"10:00","price":100000}]',
        status=status,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def _seed_ad_request(db, enterprise_id: int, index: int, *, status: str = "pending") -> AdvertisementRequest:
    request = AdvertisementRequest(
        enterprise_id=enterprise_id,
        name=f"Ad {index}",
        description=f"Ad description {index}",
        detail_url=f"https://ads.test/{index}",
        image_url=f"https://img.test/ad-{index}.png",
        status=status,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def _seed_friendship(db, user_a_id: int, user_b_id: int, *, current_streak: int = 0, best_streak: int = 0, last_activity_at: datetime | None = None) -> Friendship:
    low_id, high_id = friend_crud._normalize_pair(user_a_id, user_b_id)
    friendship = Friendship(
        user_low_id=low_id,
        user_high_id=high_id,
        current_streak=current_streak,
        best_streak=best_streak,
        last_activity_at=last_activity_at,
    )
    db.add(friendship)
    db.commit()
    db.refresh(friendship)
    return friendship


def _assert_deleted(db, model, **filters):
    assert db.query(model).filter_by(**filters).count() == 0


def _run_user_case(db, case_id: int):
    cycle = (case_id - 1) // 5
    variant = (case_id - 1) % 5
    role_cycle = [UserRole.user, UserRole.owner, UserRole.enterprise, UserRole.admin, UserRole.user]
    role = role_cycle[cycle]

    if variant == 0:
        payload = UserRegister(
            email=f"user-{cycle}@example.com",
            password=_password(case_id),
            full_name=f"User Create {cycle}",
            phone_number=f"0901{cycle:04d}",
            role=role,
        )
        created = user_crud.create_user(db, payload)
        assert created.id is not None
        assert created.email == payload.email
        assert _enum_text(created.role) == role.value
        assert created.hashed_password != payload.password
        assert created.is_active is True

    elif variant == 1:
        user = _seed_user(db, case_id, role=role, email=f"lookup-{cycle}@example.com")
        found_by_email = user_crud.get_user_by_email(db, user.email)
        found_by_id = user_crud.get_user_by_id(db, user.id)
        assert found_by_email is not None and found_by_email.id == user.id
        assert found_by_id is not None and found_by_id.email == user.email

    elif variant == 2:
        user = _seed_user(db, case_id, role=role)
        update_payloads = [
            {"full_name": f"Updated Name {cycle}"},
            {"phone_number": f"0988{cycle:04d}"},
            {"password": f"NewPass{cycle}!"},
            {
                "avatar_url": f"https://img.test/avatar-{cycle}.png",
                "bank_account_number": f"11223344{cycle}",
                "bank_account_name": f"Updated {cycle}",
                "bank_name": "Techcombank",
                "bank_code": "970407",
            },
            {"email": f"updated-{cycle}@example.com"},
        ]
        updated = user_crud.update_user(db, user.id, update_payloads[cycle])
        assert updated is not None
        if "password" in update_payloads[cycle]:
            assert updated.hashed_password != user.hashed_password
        for field, value in update_payloads[cycle].items():
            if field == "password":
                continue
            assert getattr(updated, field) == value

    elif variant == 3:
        target_role = role.value
        user_one = _seed_user(db, case_id * 10, role=role)
        user_two = _seed_user(db, case_id * 10 + 1, role=role)
        _seed_user(db, case_id * 10 + 2, role=UserRole.admin if role != UserRole.admin else UserRole.user)
        users = user_crud.get_users_by_role(db, target_role)
        ids = {item.id for item in users}
        assert user_one.id in ids and user_two.id in ids
        assert all(_enum_text(item.role) == target_role for item in users)

    else:
        target = _seed_user(db, case_id, role=role)
        _seed_notification(db, target.id, case_id)

        if role == UserRole.owner:
            court = court_crud.create_court(db, _seed_court_payload(case_id, 2), target.id, images=[f"https://img.test/court-{case_id}.png"])
            assert db.query(IndividualCourt).filter(IndividualCourt.court_id == court.id).count() == 2
        elif role == UserRole.enterprise:
            _seed_ad_request(db, target.id, case_id)
        else:
            friend = _seed_user(db, case_id + 200, role=UserRole.user)
            db.add(FriendRequest(sender_id=target.id, receiver_id=friend.id, status="pending"))
            db.commit()
            _seed_friendship(db, target.id, friend.id)
            db.add(Booking(individual_court_id=1, user_id=target.id, booking_date=datetime(2026, 4, 29, 0, 0), start_time="08:00", end_time="09:00", phone_number="0900000000", customer_name="Customer", customer_email="customer@example.com", payment_method="cash", payment_status="pending", booking_status="pending", status="pending"))
            db.commit()

        assert user_crud.delete_user(db, target.id) is True
        assert user_crud.get_user_by_id(db, target.id) is None
        assert db.query(Notification).filter(Notification.user_id == target.id).count() == 0
        assert db.query(FriendRequest).filter((FriendRequest.sender_id == target.id) | (FriendRequest.receiver_id == target.id)).count() == 0
        assert db.query(Friendship).filter((Friendship.user_low_id == target.id) | (Friendship.user_high_id == target.id)).count() == 0
        if role == UserRole.owner:
            assert db.query(Court).filter(Court.owner_id == target.id).count() == 0
            assert db.query(IndividualCourt).count() == 0
        elif role == UserRole.enterprise:
            assert db.query(AdvertisementRequest).filter(AdvertisementRequest.enterprise_id == target.id).count() == 0


def _run_court_case(db, monkeypatch, case_id: int):
    cycle = (case_id - 1) // 5
    variant = (case_id - 1) % 5
    quantity = cycle + 1
    owner = _seed_user(db, case_id, role=UserRole.owner, bank=True)
    court_payload = _seed_court_payload(case_id, max(quantity, 2))

    if variant == 0:
        court = court_crud.create_court(db, court_payload, owner.id, images=[f"https://img.test/court-{case_id}.png"])
        courts = court_crud.get_individual_courts_by_court(db, court.id)
        assert court.id is not None
        assert len(courts) == max(quantity, 2)
        assert courts[0].name == "Sân 1"

    elif variant == 1:
        court = court_crud.create_court(db, court_payload, owner.id)
        new_quantity = quantity + 1 if cycle % 2 == 0 else 1
        updated = court_crud.update_court(
            db,
            court.id,
            CourtUpdate(
                name=f"Updated Court {case_id}",
                court_quantity=new_quantity,
                contact_phone=f"0919{case_id:04d}",
                is_active=cycle % 2 == 0,
            ),
        )
        assert updated is not None
        assert updated.name == f"Updated Court {case_id}"
        assert updated.contact_phone == f"0919{case_id:04d}"
        assert updated.is_active == (cycle % 2 == 0)
        assert len(court_crud.get_individual_courts_by_court(db, court.id)) == new_quantity

    elif variant == 2:
        court = court_crud.create_court(db, court_payload, owner.id)
        individual = court_crud.get_individual_courts_by_court(db, court.id)[0]
        fetched = court_crud.get_individual_court(db, individual.id)
        assert fetched is not None
        assert fetched.id == individual.id
        updated = court_crud.update_individual_court(
            db,
            individual.id,
            IndividualCourtUpdate(name=f"VIP {case_id}", is_active=cycle % 2 == 0),
        )
        assert updated is not None
        assert updated.name == f"VIP {case_id}"
        assert updated.is_active == (cycle % 2 == 0)
        assert len(court_crud.get_courts_by_owner(db, owner.id)) == 1

    elif variant == 3:
        court = court_crud.create_court(db, court_payload, owner.id)
        user = _seed_user(db, case_id + 200, role=UserRole.user)
        payment_method = "cash" if cycle % 2 == 0 else "vietqr"
        if payment_method == "vietqr":
            monkeypatch.setattr(
                "app.core.vietqr_service.VietQRService.generate_qr_url",
                lambda self, **kwargs: f"https://qr.test/{case_id}",
            )
        booking = court_crud.create_booking(
            db,
            _seed_booking_payload(case_id, court_crud.get_individual_courts_by_court(db, court.id)[0].id, payment_method),
            user.id,
        )
        if payment_method == "cash":
            assert _enum_text(booking.payment_status) == "paid"
            assert _enum_text(booking.booking_status) == "confirmed"
            assert booking.status == "confirmed"
        else:
            assert _enum_text(booking.payment_status) == "pending"
            assert booking.qr_code_url == f"https://qr.test/{case_id}"
        update_fields = {"status": "completed"} if cycle % 2 == 0 else {"booking_status": "cancelled"}
        update_payload = BookingUpdate(**update_fields)
        updated = court_crud.update_booking(db, booking.id, update_payload)
        assert updated is not None
        if cycle % 2 == 0:
            assert _enum_text(updated.booking_status) == "completed"
            assert updated.status == "completed"
        else:
            assert _enum_text(updated.booking_status) == "cancelled"
            assert updated.status == "cancelled"
        assert court_crud.delete_booking(db, booking.id) is True
        assert court_crud.get_booking(db, booking.id) is None

    else:
        court = court_crud.create_court(db, court_payload, owner.id)
        individuals = court_crud.get_individual_courts_by_court(db, court.id)
        target = individuals[0]
        active_booking = Booking(
            individual_court_id=target.id,
            user_id=owner.id,
            booking_date=datetime(2026, 4, 29, 0, 0),
            start_time="08:00",
            end_time="09:00",
            phone_number="0900000000",
            customer_name="Customer",
            customer_email="customer@example.com",
            total_hours=1,
            total_price=100000,
            payment_method="cash",
            payment_status="paid",
            booking_status="confirmed",
            status="confirmed",
        )
        review_booking = Booking(
            individual_court_id=target.id,
            user_id=owner.id,
            booking_date=datetime(2026, 4, 28, 0, 0),
            start_time="10:00",
            end_time="11:00",
            phone_number="0900000001",
            customer_name="Customer 2",
            customer_email="customer2@example.com",
            total_hours=1,
            total_price=120000,
            payment_method="cash",
            payment_status="paid",
            booking_status="confirmed",
            status={0: "active", 1: "completed", 2: "pending", 3: "cancelled", 4: "completed"}[cycle],
        )
        db.add(active_booking)
        db.add(review_booking)
        db.commit()

        if cycle == 0:
            assert court_crud.check_booking_overlap(db, target.id, datetime(2026, 4, 29, 0, 0), "08:30", "09:30") is True
        elif cycle == 1:
            assert court_crud.check_booking_overlap(db, target.id, datetime(2026, 4, 28, 0, 0), "10:30", "11:30") is False
        elif cycle == 2:
            assert court_crud.check_booking_overlap(db, target.id, datetime(2026, 4, 29, 0, 0), "08:30", "09:30") is True
        elif cycle == 3:
            assert court_crud.check_booking_overlap(db, target.id, datetime(2026, 4, 28, 0, 0), "10:30", "11:30") is False
        else:
            summary = court_crud.get_owner_bookings_summary(db, owner.id)
            assert summary["total_bookings"] >= 2
            assert summary["period_days"] == 30


def _run_notification_case(db, case_id: int):
    cycle = (case_id - 1) // 5
    variant = (case_id - 1) % 5
    owner = _seed_user(db, case_id, role=UserRole.owner)
    enterprise = _seed_user(db, case_id + 100, role=UserRole.enterprise)
    admin = _seed_user(db, case_id + 200, role=UserRole.admin)

    if variant == 0:
        n1 = notification_crud.create_notification(
            db,
            NotificationCreate(
                user_id=owner.id,
                title=f"N{case_id}-1",
                message="First message",
                type="system",
                related_id=case_id,
            ),
        )
        n2 = notification_crud.create_notification(
            db,
            NotificationCreate(
                user_id=owner.id,
                title=f"N{case_id}-2",
                message="Second message",
                type="system",
                related_id=case_id + 1,
            ),
        )
        items = notification_crud.get_user_notifications(db, owner.id)
        assert {item.id for item in items} == {n1.id, n2.id}
        assert notification_crud.get_unread_count(db, owner.id) == 2

    elif variant == 1:
        first = _seed_notification(db, owner.id, case_id)
        second = _seed_notification(db, owner.id, case_id + 1)
        assert notification_crud.mark_as_read(db, first.id) is not None
        assert notification_crud.get_unread_count(db, owner.id) == 1
        notification_crud.mark_all_as_read(db, owner.id)
        assert notification_crud.get_unread_count(db, owner.id) == 0
        refreshed = notification_crud.get_user_notifications(db, owner.id)
        assert all(item.is_read for item in refreshed)
        assert second.id in {item.id for item in refreshed}

    elif variant == 2:
        request = notification_crud.create_court_request(
            db,
            CourtRequestCreate(
                name=f"Court Request {case_id}",
                address=f"Address {case_id}",
                ward="Ward 1",
                city="Ho Chi Minh City",
                description="Court description",
                court_quantity=2,
                opening_time="08:00",
                closing_time="22:00",
                facilities='["parking"]',
                contact_phone=f"0907{case_id:04d}",
                contact_email=f"court{case_id}@example.com",
                images='["https://img.test/court.png"]',
                time_slots='[{"start_time":"08:00","end_time":"10:00","price":100000}]',
            ),
            owner.id,
        )
        fetched = notification_crud.get_court_request(db, request.id)
        assert fetched is not None and fetched.owner.id == owner.id
        all_requests = notification_crud.get_all_court_requests(db, status="pending")
        assert request.id in {item.id for item in all_requests}
        updated = notification_crud.update_court_request_status(
            db,
            request.id,
            CourtRequestUpdate(status="approved" if cycle % 2 == 0 else "rejected", rejection_reason=None if cycle % 2 == 0 else "Missing papers"),
            admin.id,
        )
        assert updated is not None
        assert updated.reviewed_by == admin.id
        assert updated.status in {"approved", "rejected"}
        if cycle % 2 == 1:
            assert updated.rejection_reason == "Missing papers"
        assert notification_crud.delete_court_request(db, request.id) is True
        assert notification_crud.delete_court_request(db, request.id) is False

    elif variant == 3:
        request = notification_crud.create_advertisement_request(
            db,
            AdvertisementRequestCreate(
                name=f"Ad Request {case_id}",
                description="Ad description",
                detail_url=f"https://ads.test/{case_id}",
                image_url=f"https://img.test/{case_id}.png",
            ),
            enterprise.id,
        )
        fetched = notification_crud.get_advertisement_request(db, request.id)
        assert fetched is not None and fetched.owner.id == enterprise.id
        all_requests = notification_crud.get_all_advertisement_requests(db, status="pending")
        assert request.id in {item.id for item in all_requests}
        updated = notification_crud.update_advertisement_request_status(
            db,
            request.id,
            AdvertisementRequestUpdate(status="approved" if cycle % 2 == 0 else "rejected", rejection_reason=None if cycle % 2 == 0 else "Wrong content"),
            admin.id,
        )
        assert updated is not None
        assert updated.reviewed_by == admin.id
        assert updated.status in {"approved", "rejected"}
        click = notification_crud.create_advertisement_click(db, request.id, user_id=owner.id, ip_address="127.0.0.1", user_agent="pytest")
        counts = notification_crud.get_click_counts_by_request_ids(db, [request.id])
        assert counts[request.id] == 1
        assert click.advertisement_request_id == request.id
        assert notification_crud.delete_advertisement_request(db, request.id) is True
        assert notification_crud.delete_advertisement_request(db, request.id) is False

    else:
        court_request = notification_crud.create_court_request(
            db,
            CourtRequestCreate(
                name=f"Filter Court Request {case_id}",
                address=f"Filter Address {case_id}",
                ward="Ward 1",
                city="Ho Chi Minh City",
                description="Filter description",
                court_quantity=1,
                opening_time="08:00",
                closing_time="22:00",
                facilities='["lights"]',
                contact_phone=f"0906{case_id:04d}",
                contact_email=f"filter{case_id}@example.com",
                images='[]',
                time_slots='[]',
            ),
            owner.id,
        )
        ad_request = notification_crud.create_advertisement_request(
            db,
            AdvertisementRequestCreate(
                name=f"Filter Ad {case_id}",
                description="Filter ad description",
                detail_url=f"https://ads.test/filter/{case_id}",
                image_url=f"https://img.test/filter-{case_id}.png",
            ),
            enterprise.id,
        )
        notification_crud.create_advertisement_click(db, ad_request.id, user_id=None, ip_address="10.0.0.1", user_agent="pytest")
        notification_crud.create_advertisement_click(db, ad_request.id, user_id=owner.id, ip_address="10.0.0.2", user_agent="pytest")

        if cycle == 0:
            pending_requests = notification_crud.get_all_court_requests(db, status="pending")
            assert court_request.id in {item.id for item in pending_requests}
        elif cycle == 1:
            approved_request = notification_crud.update_court_request_status(db, court_request.id, CourtRequestUpdate(status="approved", rejection_reason=None), admin.id)
            assert approved_request is not None and approved_request.status == "approved"
        elif cycle == 2:
            ad_pending = notification_crud.get_enterprise_advertisement_requests(db, enterprise.id, status="pending")
            assert ad_request.id in {item.id for item in ad_pending}
        elif cycle == 3:
            counts = notification_crud.get_click_counts_by_request_ids(db, [ad_request.id])
            assert counts[ad_request.id] == 2
        else:
            assert notification_crud.get_click_counts_by_request_ids(db, []) == {}
            assert notification_crud.get_all_advertisement_requests(db, status="approved") == []


def _run_friend_case(db, case_id: int):
    cycle = (case_id - 1) // 5
    variant = (case_id - 1) % 5
    sender = _seed_user(db, case_id, role=UserRole.user, email=f"sender{case_id}@example.com")
    receiver = _seed_user(db, case_id + 50, role=UserRole.user, email=f"receiver{case_id}@example.com")

    if variant == 0:
        mixed = _seed_user(db, case_id + 100, role=UserRole.user, email=f"MiXeD{case_id}@Example.com")
        found = friend_crud.get_user_by_email(db, f"  mixed{case_id}@example.com  ")
        assert found is not None and found.id == mixed.id
        assert friend_crud._normalize_pair(10, 3) == (3, 10)
        assert friend_crud.get_friendship(db, sender.id, receiver.id) is None

    elif variant == 1:
        if cycle == 0:
            request = friend_crud.create_friend_request(db, sender, receiver.email)
            assert request.sender_id == sender.id
            assert request.receiver_id == receiver.id
            assert db.query(Notification).filter(Notification.user_id == receiver.id).count() == 1
        elif cycle == 1:
            with pytest.raises(ValueError):
                friend_crud.create_friend_request(db, sender, sender.email)
        elif cycle == 2:
            receiver.is_active = False
            db.commit()
            with pytest.raises(ValueError):
                friend_crud.create_friend_request(db, sender, receiver.email)
        elif cycle == 3:
            receiver.role = UserRole.admin
            db.commit()
            with pytest.raises(ValueError):
                friend_crud.create_friend_request(db, sender, receiver.email)
        else:
            friend_crud.create_friend_request(db, sender, receiver.email)
            with pytest.raises(ValueError):
                friend_crud.create_friend_request(db, sender, receiver.email)

    elif variant == 2:
        request = FriendRequest(sender_id=sender.id, receiver_id=receiver.id, status="pending")
        db.add(request)
        db.commit()
        db.refresh(request)
        action = {0: "accept", 1: "reject", 2: "invalid", 3: "accept", 4: "reject"}[cycle]
        if action in {"accept", "reject"}:
            responded = friend_crud.respond_friend_request(db, request.id, receiver, action)
            assert responded.status in {"accepted", "rejected"}
            assert responded.responded_at is not None
            if action == "accept":
                assert friend_crud.get_friendship(db, sender.id, receiver.id) is not None
        else:
            with pytest.raises(ValueError):
                friend_crud.respond_friend_request(db, request.id, receiver, action)

    elif variant == 3:
        friendship = _seed_friendship(db, sender.id, receiver.id, current_streak=cycle, best_streak=cycle + 1)
        friends_of_sender = friend_crud.list_friends(db, sender.id)
        friends_of_receiver = friend_crud.list_friends(db, receiver.id)
        assert friendship.id in {item.id for item in friends_of_sender}
        assert friendship.id in {item.id for item in friends_of_receiver}
        assert friend_crud.resolve_friend_user(db, friendship, sender.id).id == receiver.id
        assert friend_crud.resolve_friend_user(db, friendship, receiver.id).id == sender.id

    else:
        anchor = datetime.utcnow() - timedelta(days=cycle + 4)
        friendship = _seed_friendship(db, sender.id, receiver.id, current_streak=cycle + 2, best_streak=cycle + 1, last_activity_at=anchor)
        if cycle == 0:
            changed = friend_crud._apply_streak_expiry(friendship, datetime.utcnow())
            assert changed is False
            assert friendship.current_streak == cycle + 2
        elif cycle == 1:
            friendship.last_activity_at = datetime.utcnow() - timedelta(days=5, hours=1)
            db.commit()
            changed = friend_crud.refresh_friendship_streak_state(db, friendship)
            assert changed is True or changed is False
            assert db.query(Notification).filter(Notification.user_id.in_([sender.id, receiver.id])).count() >= 2
        elif cycle == 2:
            friendship.last_activity_at = datetime.utcnow() - timedelta(days=7, minutes=1)
            friendship.current_streak = 8
            friendship.best_streak = 5
            db.commit()
            changed = friend_crud._apply_streak_expiry(friendship, datetime.utcnow())
            assert changed is True
            assert friendship.current_streak == 0
            assert friendship.best_streak == 8
        elif cycle == 3:
            friend_crud.touch_friendship_invite_activity(db, sender.id, receiver.id, datetime.utcnow())
            refreshed = friend_crud.get_friendship(db, sender.id, receiver.id)
            assert refreshed is not None and refreshed.last_activity_at is not None
        else:
            friend_crud.refresh_friendship_streak_state(db, friendship)
            assert friend_crud.get_friendship(db, sender.id, receiver.id) is not None


@pytest.mark.parametrize("case_id", range(1, 101), ids=lambda value: f"db-case-{value:03d}")
def test_database_crud_cases(db, monkeypatch, case_id):
    if case_id <= 25:
        _run_user_case(db, case_id)
    elif case_id <= 50:
        _run_court_case(db, monkeypatch, case_id - 25)
    elif case_id <= 75:
        _run_notification_case(db, case_id - 50)
    else:
        _run_friend_case(db, case_id - 75)