"""
Bank Transaction Verification Service
Supports multiple Vietnamese banks for automatic payment verification
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.court import Booking, PaymentStatus, BookingStatus

class BankVerificationService:
    """
    Service to verify bank transactions for payment confirmation
    
    Supports:
    - Sepay API (transaction monitoring service)
    - Direct bank APIs (MB Bank, VCB, etc.)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize bank verification service
        
        Args:
            api_key: API key for bank transaction monitoring service (e.g., Sepay)
        """
        self.api_key = api_key
        self.base_url = "https://my.sepay.vn/userapi"  # Sepay API endpoint
        
    async def verify_transaction(
        self,
        bank_code: str,
        account_number: str,
        amount: float,
        description: str,
        time_window_minutes: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Verify if a transaction matching criteria exists
        
        Args:
            bank_code: Bank BIN code (e.g., "970422" for MB Bank)
            account_number: Recipient account number
            amount: Expected transaction amount
            description: Payment description/note to match
            time_window_minutes: Time window to search for transaction
            
        Returns:
            Transaction info dict if found, None otherwise
        """
        if not self.api_key:
            # Manual verification mode - admin must confirm
            return None
            
        try:
            # Get recent transactions from Sepay
            transactions = await self._get_recent_transactions(
                bank_code, 
                account_number,
                time_window_minutes
            )
            
            # Find matching transaction
            for trans in transactions:
                if self._match_transaction(trans, amount, description):
                    return {
                        "transaction_id": trans.get("id"),
                        "amount": trans.get("amount"),
                        "description": trans.get("description"),
                        "transaction_time": trans.get("transaction_date"),
                        "bank_code": bank_code,
                        "account_number": account_number
                    }
                    
            return None
            
        except Exception as e:
            print(f"Error verifying transaction: {str(e)}")
            return None
    
    async def _get_recent_transactions(
        self,
        bank_code: str,
        account_number: str,
        time_window_minutes: int
    ) -> List[Dict[str, Any]]:
        """
        Get recent transactions from bank via Sepay API
        
        Args:
            bank_code: Bank BIN code
            account_number: Account number
            time_window_minutes: Time window in minutes
            
        Returns:
            List of transaction dicts
        """
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/transactions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    params={
                        "account_number": account_number,
                        "limit": 50  # Get last 50 transactions
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    transactions = data.get("transactions", [])
                    
                    # Filter by time window
                    cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
                    recent_trans = [
                        t for t in transactions
                        if datetime.fromisoformat(t.get("transaction_date", "")) >= cutoff_time
                    ]
                    
                    return recent_trans
                else:
                    print(f"Sepay API error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            print(f"Error fetching transactions: {str(e)}")
            return []
    
    def _match_transaction(
        self,
        transaction: Dict[str, Any],
        expected_amount: float,
        expected_description: str
    ) -> bool:
        """
        Check if transaction matches expected payment
        
        Args:
            transaction: Transaction data from bank
            expected_amount: Expected payment amount
            expected_description: Expected payment description
            
        Returns:
            True if transaction matches, False otherwise
        """
        trans_amount = float(transaction.get("amount", 0))
        trans_desc = str(transaction.get("description", "")).upper().strip()
        
        # Normalize expected description (remove spaces, uppercase)
        normalized_expected = expected_description.upper().replace(" ", "")
        normalized_trans = trans_desc.replace(" ", "")
        
        # Check amount match (exact)
        amount_match = abs(trans_amount - expected_amount) < 0.01
        
        # Check description contains expected pattern
        # Expected format: "BOOKING{booking_id}" or custom note
        description_match = normalized_expected in normalized_trans
        
        return amount_match and description_match
    
    async def auto_verify_booking(
        self,
        db: Session,
        booking: Booking,
        owner_bank_code: str,
        owner_account_number: str
    ) -> bool:
        """
        Automatically verify booking payment
        
        Args:
            db: Database session
            booking: Booking instance to verify
            owner_bank_code: Owner's bank code
            owner_account_number: Owner's bank account number
            
        Returns:
            True if payment verified and booking updated, False otherwise
        """
        if booking.payment_status == PaymentStatus.PAID:
            return True  # Already verified
            
        # Generate expected description
        expected_desc = f"BOOKING{booking.id}"
        
        # Search for matching transaction
        transaction = await self.verify_transaction(
            bank_code=owner_bank_code,
            account_number=owner_account_number,
            amount=float(booking.total_price),
            description=expected_desc,
            time_window_minutes=30
        )
        
        if transaction:
            # Update booking payment status
            booking.payment_status = PaymentStatus.PAID
            booking.booking_status = BookingStatus.CONFIRMED
            booking.bank_transaction_id = transaction["transaction_id"]
            booking.payment_verified_at = datetime.now()
            booking.payment_note = f"Auto-verified: {transaction['description']}"
            
            db.commit()
            db.refresh(booking)
            
            return True
            
        return False
    
    def manual_verify_booking(
        self,
        db: Session,
        booking: Booking,
        transaction_id: str,
        note: Optional[str] = None
    ) -> Booking:
        """
        Manually verify booking payment by admin/owner
        
        Args:
            db: Database session
            booking: Booking instance to verify
            transaction_id: Bank transaction ID
            note: Optional verification note
            
        Returns:
            Updated booking instance
        """
        booking.payment_status = PaymentStatus.PAID
        booking.booking_status = BookingStatus.CONFIRMED
        booking.bank_transaction_id = transaction_id
        booking.payment_verified_at = datetime.now()
        booking.payment_note = note or "Manually verified"
        
        db.commit()
        db.refresh(booking)
        
        return booking


# Singleton instance
bank_verification_service = BankVerificationService()


def get_bank_verification_service(api_key: Optional[str] = None) -> BankVerificationService:
    """Get bank verification service instance"""
    if api_key:
        return BankVerificationService(api_key=api_key)
    return bank_verification_service
