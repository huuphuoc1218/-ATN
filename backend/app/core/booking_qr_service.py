from datetime import datetime, timedelta
from html import escape
from typing import Optional
from urllib.parse import quote_plus

from jose import JWTError, jwt

from app.core.config import settings


def generate_booking_access_token(booking_id: int, expires_hours: int = 72) -> str:
    """Create a signed short-lived token for public booking info page."""
    payload = {
        "sub": "booking_qr",
        "booking_id": booking_id,
        "exp": datetime.utcnow() + timedelta(hours=expires_hours),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_booking_access_token(token: str) -> Optional[int]:
    """Validate and decode booking QR token to booking id."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("sub") != "booking_qr":
            return None
        booking_id = payload.get("booking_id")
        if not isinstance(booking_id, int):
            return None
        return booking_id
    except JWTError:
        return None


def build_booking_info_url(token: str) -> str:
    """Public URL shown after scanning QR code."""
    base = settings.BACKEND_PUBLIC_BASE_URL.rstrip("/")
    return f"{base}/api/bookings/qr-booking/{token}"


def build_qr_image_url(content_url: str) -> str:
    """Generate QR image URL from booking info URL."""
    encoded = quote_plus(content_url)
    return f"https://quickchart.io/qr?text={encoded}&size=300"


def build_booking_info_html(
    booking_id: int,
    customer_name: str,
    customer_email: str,
    phone_number: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    total_price: str,
    court_name: str,
    individual_court_name: str,
    owner_name: str,
    owner_phone: str,
) -> str:
    """Render a modern HTML page for booking details opened from QR."""
    return f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Booking #{booking_id}</title>
    <style>
      :root {{
        --bg: #f3f7fb;
        --text: #0f172a;
        --muted: #64748b;
        --line: #e2e8f0;
        --brand: #0f766e;
        --brand-dark: #115e59;
      }}

      * {{ box-sizing: border-box; }}

      body {{
        margin: 0;
        background: radial-gradient(circle at top right, #e0f2fe, var(--bg) 45%);
        font-family: "Segoe UI", Tahoma, Arial, sans-serif;
        color: var(--text);
        padding: 24px 12px;
      }}

      .page {{ max-width: 860px; margin: 0 auto; }}

      .card {{
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 18px;
        box-shadow: 0 20px 44px rgba(15, 23, 42, 0.08);
        overflow: hidden;
      }}

      .hero {{
        background: linear-gradient(140deg, var(--brand) 0%, var(--brand-dark) 100%);
        color: #ffffff;
        padding: 24px;
      }}

      .brand {{
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.92;
        margin-bottom: 8px;
      }}

      .title {{ margin: 0; font-size: 28px; line-height: 1.2; }}
      .subtitle {{ margin: 8px 0 0; font-size: 14px; opacity: 0.92; }}

      .body {{ padding: 24px; }}

      .section-title {{
        margin: 0 0 12px;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--muted);
      }}

      .grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }}

      .item {{
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 12px 14px;
        background: #f8fafc;
      }}

      .label {{
        font-size: 12px;
        color: var(--muted);
        margin-bottom: 4px;
      }}

      .value {{
        font-size: 15px;
        font-weight: 700;
        word-break: break-word;
      }}

      .value.total {{ color: var(--brand-dark); font-size: 18px; }}

      .divider {{
        border: 0;
        border-top: 1px solid var(--line);
        margin: 20px 0;
      }}

      .footer-note {{
        margin-top: 16px;
        font-size: 12px;
        color: var(--muted);
      }}

      @media (max-width: 700px) {{
        .title {{ font-size: 24px; }}
        .body {{ padding: 16px; }}
        .grid {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <div class="page">
      <div class="card">
        <div class="hero">
          <div class="brand">Pickleball NP SPORTCLUB</div>
          <h1 class="title">Booking Details #{booking_id}</h1>
          <p class="subtitle">This page was opened by scanning your QR code from the confirmation email.</p>
        </div>

        <div class="body">
          <h2 class="section-title">Customer Information</h2>
          <div class="grid">
            <div class="item">
              <div class="label">Customer name</div>
              <div class="value">{escape(customer_name)}</div>
            </div>
            <div class="item">
              <div class="label">Email</div>
              <div class="value">{escape(customer_email)}</div>
            </div>
            <div class="item">
              <div class="label">Phone number</div>
              <div class="value">{escape(phone_number)}</div>
            </div>
            <div class="item">
              <div class="label">Booking date</div>
              <div class="value">{escape(booking_date)}</div>
            </div>
          </div>

          <hr class="divider" />

          <h2 class="section-title">Booking Information</h2>
          <div class="grid">
            <div class="item">
              <div class="label">Time slot</div>
              <div class="value">{escape(start_time)} - {escape(end_time)}</div>
            </div>
            <div class="item">
              <div class="label">Court</div>
              <div class="value">{escape(court_name)} - {escape(individual_court_name)}</div>
            </div>
            <div class="item">
              <div class="label">Total amount</div>
              <div class="value total">{escape(total_price)} VND</div>
            </div>
          </div>

          <hr class="divider" />

          <h2 class="section-title">Court Owner</h2>
          <div class="grid">
            <div class="item">
              <div class="label">Owner name</div>
              <div class="value">{escape(owner_name)}</div>
            </div>
            <div class="item">
              <div class="label">Contact</div>
              <div class="value">{escape(owner_phone)}</div>
            </div>
          </div>

          <p class="footer-note">If you need support, please contact the court owner using the details above.</p>
        </div>
      </div>
    </div>
  </body>
</html>
""".strip()
