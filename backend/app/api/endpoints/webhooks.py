"""
Webhook endpoints for bank transaction notifications
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.core.database import get_db
from app.crud import court as court_crud
from app.models.court import PaymentStatus, BookingStatus

router = APIRouter()


@router.post("/bank-transaction")
async def handle_bank_transaction_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: Optional[str] = Header(None)
):
    """
    Webhook endpoint to receive bank transaction notifications
    
    Supports:
    - Sepay webhook notifications
    - Direct bank API webhooks
    
    This endpoint is called by the bank/payment service when a transaction occurs.
    It automatically verifies and confirms the booking payment.
    """
    try:
        payload = await request.json()
        
        # TODO: Verify webhook signature (specific to payment service)
        # For Sepay, signature = HMAC-SHA256(webhook_secret, body)
        # if x_signature:
        #     expected_signature = hmac.new(
        #         WEBHOOK_SECRET.encode(),
        #         body,
        #         hashlib.sha256
        #     ).hexdigest()
        #     
        #     if not hmac.compare_digest(x_signature, expected_signature):
        #         raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Extract transaction details
        transaction_id = payload.get("id") or payload.get("transaction_id")
        amount = float(payload.get("amount", 0))
        description = str(payload.get("description", "")).upper().strip()
        
        # Parse booking ID from description (format: "BOOKING123")
        booking_id = None
        if "BOOKING" in description:
            try:
                booking_id_str = description.split("BOOKING")[1].split()[0]
                booking_id = int(booking_id_str)
            except (IndexError, ValueError):
                return {
                    "status": "ignored",
                    "message": "Could not parse booking ID from description"
                }
        
        if not booking_id:
            return {
                "status": "ignored",
                "message": "No booking ID found in transaction"
            }
        
        # Get booking
        booking = court_crud.get_booking(db, booking_id)
        if not booking:
            return {
                "status": "error",
                "message": f"Booking {booking_id} not found"
            }
        
        # Check if already verified
        if booking.payment_status == PaymentStatus.PAID:
            return {
                "status": "already_verified",
                "booking_id": booking_id
            }
        
        # Verify amount matches
        if abs(amount - float(booking.total_price)) > 0.01:
            # Amount mismatch - mark as partial payment
            booking.payment_status = PaymentStatus.PARTIAL
            booking.bank_transaction_id = transaction_id
            booking.payment_note = f"Partial payment: {amount} VND (expected {booking.total_price} VND)"
            db.commit()
            
            return {
                "status": "partial_payment",
                "booking_id": booking_id,
                "expected": float(booking.total_price),
                "received": amount
            }
        
        # Verify payment
        from datetime import datetime
        booking.payment_status = PaymentStatus.PAID
        booking.booking_status = BookingStatus.CONFIRMED
        booking.status = "confirmed"  # Legacy field
        booking.bank_transaction_id = transaction_id
        booking.payment_verified_at = datetime.now()
        booking.payment_note = f"Auto-verified via webhook: {transaction_id}"
        
        db.commit()
        
        # TODO: Send notification to user and owner
        # - User: "Payment confirmed! Your booking is now confirmed."
        # - Owner: "New booking confirmed: Booking #{booking_id}"
        
        return {
            "status": "success",
            "booking_id": booking_id,
            "transaction_id": transaction_id,
            "amount": amount
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing webhook"
        )


@router.get("/bank-transaction/test")
async def test_webhook():
    """
    Test endpoint to verify webhook is accessible
    """
    return {
        "status": "ok",
        "message": "Webhook endpoint is working"
    }
