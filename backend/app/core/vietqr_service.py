"""
VietQR Service - Generate QR codes for bank transfers
Documentation: https://www.vietqr.io/
"""

from typing import Dict, Optional
import urllib.parse


class VietQRService:
    """Service to generate VietQR payment QR codes"""
    
    def __init__(self):
        self.api_base = "https://img.vietqr.io/image"
        
    def generate_qr_url(
        self,
        bank_code: str,
        account_number: str,
        amount: int,
        description: str,
        account_name: Optional[str] = None,
        template: str = "compact2"
    ) -> str:
        """
        Generate VietQR payment URL
        
        Args:
            bank_code: Bank BIN code (e.g., "970436" for Vietcombank)
            account_number: Bank account number
            amount: Payment amount in VND
            description: Payment description/note
            account_name: Account holder name (optional)
            template: QR template style (compact, compact2, qr_only, print)
            
        Returns:
            str: VietQR image URL
            
        Example:
            >>> service = VietQRService()
            >>> qr_url = service.generate_qr_url(
            ...     bank_code="970436",
            ...     account_number="0123456789",
            ...     amount=500000,
            ...     description="Thanh toan dat san #123"
            ... )
        """
        
        # Build QR URL
        qr_url = f"{self.api_base}/{bank_code}-{account_number}-{template}.jpg"
        
        # Add query parameters
        params = {
            "amount": amount,
            "addInfo": description,
        }
        
        if account_name:
            params["accountName"] = account_name
        
        # Encode parameters
        query_string = urllib.parse.urlencode(params)
        full_url = f"{qr_url}?{query_string}"
        
        return full_url
    
    def generate_payment_info(
        self,
        bank_code: str,
        account_number: str,
        account_name: str,
        bank_name: str,
        amount: int,
        description: str
    ) -> Dict:
        """
        Generate complete payment information including QR code
        
        Returns:
            Dict with QR URL and payment details
        """
        
        qr_url = self.generate_qr_url(
            bank_code=bank_code,
            account_number=account_number,
            amount=amount,
            description=description,
            account_name=account_name
        )
        
        return {
            "qr_url": qr_url,
            "bank_code": bank_code,
            "bank_name": bank_name,
            "account_number": account_number,
            "account_name": account_name,
            "amount": amount,
            "description": description,
            "payment_method": "vietqr"
        }


# Dictionary of major Vietnamese banks
VIETNAM_BANKS = {
    "970405": "Agribank",
    "970422": "MB Bank (Military Bank)",
    "970407": "Techcombank",
    "970415": "Vietinbank",
    "970436": "Vietcombank",
    "970418": "BIDV",
    "970432": "VPBank",
    "970423": "TPBank",
    "970403": "Sacombank",
    "970448": "OCB", 
    "970441": "VIB",
    "970454": "VietCapital Bank",
    "970419": "NCB (Nam A Bank)",
    "970438": "BaoViet Bank",
    "970414": "Oceanbank",
    "970439": "Public Bank Vietnam",
    "970443": "SHB",
    "970437": "HDBank",
    "970433": "VietBank",
    "970431": "Eximbank",
    "970426": "Maritime Bank (MSB)",
    "970430": "PG Bank",
    "970440": "SeABank",
    "970434": "IndovinaBank",
    "970458": "UOB Vietnam",
    "970425": "ABBank",
    "970406": "DongA Bank",
    "970408": "GPBank",
    "970427": "VietA Bank",
    "970429": "SCB",
    "970428": "Nam A Bank",
    "970409": "Bac A Bank",
    "970449": "LienVietPostBank",
    "970424": "Shinhan Bank",
    "970412": "PVcomBank",
    "970446": "Cake by VPBank"
}


# Singleton instance
vietqr_service = VietQRService()
