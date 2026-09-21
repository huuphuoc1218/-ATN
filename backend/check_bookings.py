from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime

# Ensure imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text
from app.core.database import SessionLocal

def check_bookings_for_courts():
    db = SessionLocal()
    try:
        # Get bookings for individual courts 1 and 2
        query = text("""
            SELECT 
                b.id,
                b.individual_court_id,
                ic.name as court_name,
                b.status,
                b.booking_status,
                b.start_time,
                b.end_time,
                b.booking_date,
                b.customer_name,
                b.customer_email,
                b.created_at
            FROM bookings b
            JOIN individual_courts ic ON b.individual_court_id = ic.id
            WHERE b.individual_court_id IN (1, 2)
            ORDER BY b.booking_date DESC, b.start_time DESC
            LIMIT 10
        """)
        
        results = db.execute(query).fetchall()
        
        print("\n" + "="*100)
        print("BOOKING DATA FOR COURTS 1 & 2")
        print("="*100)
        
        if not results:
            print("❌ No bookings found for courts 1 and 2")
        else:
            print(f"\n✅ Found {len(results)} booking(s):\n")
            
            for idx, row in enumerate(results, 1):
                print(f"\n{idx}. Booking ID: {row[0]}")
                print(f"   Court: {row[2]} (ID: {row[1]})")
                print(f"   Status: {row[3]}")
                print(f"   Booking Status: {row[4]}")
                print(f"   Start Time: {row[5]}")
                print(f"   End Time: {row[6]}")
                print(f"   Booking Date: {row[7]}")
                print(f"   Customer: {row[8]} ({row[9]})")
                print(f"   Created At: {row[10]}")
                
                # Check if booking is in progress
                booking_date = row[7]
                if isinstance(booking_date, str):
                    booking_date = booking_date.split('T')[0]
                else:
                    booking_date = booking_date.strftime("%Y-%m-%d")
                
                today = datetime.utcnow().strftime("%Y-%m-%d")
                current_time = datetime.utcnow().strftime("%H:%M")
                
                is_today = booking_date == today
                start_time = row[5]
                end_time = row[6]
                
                if is_today:
                    is_in_progress = start_time <= current_time < end_time
                    print(f"   Is Today: ✅ Yes")
                    print(f"   Current Time: {current_time}")
                    print(f"   In Progress: {'✅ YES' if is_in_progress else '❌ No (not yet or already passed)'}")
                else:
                    print(f"   Is Today: ❌ No ({booking_date})")
        
        print("\n" + "="*100 + "\n")
        
        # Also check individual courts info
        print("="*100)
        print("INDIVIDUAL COURTS INFO")
        print("="*100)
        
        query2 = text("""
            SELECT id, court_id, name, is_active, created_at
            FROM individual_courts
            WHERE id IN (1, 2)
        """)
        
        results2 = db.execute(query2).fetchall()
        
        for row in results2:
            print(f"\nCourt ID: {row[0]}, Name: {row[2]}, Active: {row[3]}")
        
        print("\n" + "="*100 + "\n")
        
    except Exception as exc:
        print(f"❌ Error: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    check_bookings_for_courts()
