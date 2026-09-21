import smtplib
from email.message import EmailMessage
from html import escape
from typing import Tuple

from app.core.config import settings


def is_email_configured() -> bool:
    return bool(
        settings.SMTP_HOST
        and settings.SMTP_PORT
        and settings.SMTP_USERNAME
        and settings.SMTP_PASSWORD
        and settings.SMTP_FROM_EMAIL
    )


def send_booking_qr_email(
    to_email: str,
    customer_name: str,
    booking_id: int,
    qr_image_url: str,
    booking_info_url: str,
    court_name: str,
    individual_court_name: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    total_price: str,
    smtp_timeout: float = 10.0,
  ) -> Tuple[bool, str]:
    """Send booking confirmation email with QR code image to customer."""
    if not is_email_configured():
        return False, "SMTP is not fully configured"

    subject = f"[NP SPORTCLUB] Payment confirmed for booking #{booking_id}"

    html_body = f"""
    <!doctype html>
    <html>
      <body style="margin:0;padding:0;background:#f3f6fb;font-family:Segoe UI,Arial,sans-serif;color:#1f2937;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f6fb;padding:24px 12px;">
          <tr>
            <td align="center">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:680px;background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e5e7eb;">
                <tr>
                  <td style="background:linear-gradient(135deg,#0f766e 0%,#115e59 100%);padding:24px 28px;color:#ffffff;">
                    <div style="font-size:12px;letter-spacing:1px;opacity:.9;text-transform:uppercase;">Pickleball NP SPORTCLUB</div>
                    <h1 style="margin:8px 0 4px 0;font-size:24px;line-height:1.3;">Payment Confirmed</h1>
                    <p style="margin:0;font-size:14px;opacity:.95;">Booking #{booking_id}</p>
                  </td>
                </tr>
                <tr>
                  <td style="padding:24px 28px 10px 28px;">
                    <p style="margin:0 0 12px 0;font-size:15px;line-height:1.6;">Hi <strong>{escape(customer_name)}</strong>, the court owner has confirmed your payment.</p>
                    <p style="margin:0 0 20px 0;font-size:14px;color:#4b5563;line-height:1.6;">Scan the QR code below to view your complete booking details anytime.</p>
                  </td>
                </tr>
                <tr>
                  <td style="padding:0 28px 20px 28px;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:12px;">
                      <tr>
                        <td style="padding:14px 16px;border-bottom:1px solid #e5e7eb;"><span style="color:#6b7280;font-size:13px;">Court</span><br /><strong style="font-size:15px;">{escape(court_name)} - {escape(individual_court_name)}</strong></td>
                      </tr>
                      <tr>
                        <td style="padding:14px 16px;border-bottom:1px solid #e5e7eb;"><span style="color:#6b7280;font-size:13px;">Booking date</span><br /><strong style="font-size:15px;">{escape(booking_date)}</strong></td>
                      </tr>
                      <tr>
                        <td style="padding:14px 16px;border-bottom:1px solid #e5e7eb;"><span style="color:#6b7280;font-size:13px;">Time slot</span><br /><strong style="font-size:15px;">{escape(start_time)} - {escape(end_time)}</strong></td>
                      </tr>
                      <tr>
                        <td style="padding:14px 16px;"><span style="color:#6b7280;font-size:13px;">Total amount</span><br /><strong style="font-size:18px;color:#0f766e;">{escape(total_price)} VND</strong></td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td align="center" style="padding:4px 28px 12px 28px;">
                    <img src="{escape(qr_image_url)}" alt="Booking QR" width="260" height="260" style="display:block;border:1px solid #d1d5db;border-radius:12px;background:#ffffff;padding:8px;" />
                    <p style="margin:10px 0 0 0;font-size:13px;color:#6b7280;">Scan this QR code to view booking details</p>
                  </td>
                </tr>
                <tr>
                  <td align="center" style="padding:10px 28px 24px 28px;">
                    <a href="{escape(booking_info_url)}" target="_blank" style="display:inline-block;background:#0f766e;color:#ffffff;text-decoration:none;padding:12px 22px;border-radius:10px;font-size:14px;font-weight:600;">View booking details</a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """.strip()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email
    msg.set_content(
        "\n".join(
            [
                f"Payment for booking #{booking_id} has been confirmed.",
                f"Court: {court_name} - {individual_court_name}",
                f"Booking date: {booking_date}",
                f"Time slot: {start_time} - {end_time}",
                f"Total amount: {total_price} VND",
                f"View details: {booking_info_url}",
            ]
        )
    )
    msg.add_alternative(html_body, subtype="html")

    try:
        if settings.SMTP_USE_TLS:
          with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=smtp_timeout) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
          with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=smtp_timeout) as server:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
        return True, "Email sent successfully"
    except Exception as exc:
        return False, f"Email sending failed: {exc}"
