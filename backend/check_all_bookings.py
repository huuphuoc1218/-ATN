from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Ensure imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text
from app.core.database import SessionLocal

def check_all_bookings():
    db = SessionLocal()
    try:
        # First, check all courts
        print("\n" + "="*100)
        print("ALL COURTS")
        print("="*100)
        
        query = text("""
            SELECT id, name, owner_id, address, city, ward, is_active
            FROM courts
            ORDER BY id
        """)
        
        courts = db.execute(query).fetchall()
        for row in courts:
            print(f"Court {row[0]}: {row[1]} | Owner: {row[2]} | {row[4]} | Ward: {row[5]} | Active: {row[6]}")
        
        # Check all individual courts
        print("\n" + "="*100)
        print("ALL INDIVIDUAL COURTS")
        print("="*100)
        
        query = text("""
            SELECT id, court_id, name, is_active
            FROM individual_courts
            ORDER BY court_id, id
        """)
        
        ind_courts = db.execute(query).fetchall()
        for row in ind_courts:
            print(f"IndCourt {row[0]}: {row[2]} (Court: {row[1]}) | Active: {row[3]}")
        
        # Check all bookings
        print("\n" + "="*100)
        print("ALL BOOKINGS")
        print("="*100)
        
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
                CAST(b.total_price AS VARCHAR) as total_price
            FROM bookings b
            LEFT JOIN individual_courts ic ON b.individual_court_id = ic.id
            ORDER BY b.booking_date DESC, b.start_time DESC
            LIMIT 20
        """)
        
        results = db.execute(query).fetchall()
        
        if not results:
            print("❌ No bookings found in database")
        else:
            print(f"\n✅ Found {len(results)} booking(s):\n")
            
            # Use Vietnam timezone (UTC+7)
            vn_tz = timezone(timedelta(hours=7))
            now_vn = datetime.now(vn_tz)
            today = now_vn.strftime("%Y-%m-%d")
            current_time = now_vn.strftime("%H:%M")
            print(f"Today: {today} | Current Time: {current_time} (Vietnam Time UTC+7)\n")
            
            for idx, row in enumerate(results, 1):
                print(f"{idx}. Booking #{row[0]}")
                print(f"   Court: {row[2]} (ID: {row[1]})")
                print(f"   Status: {row[3]} | Booking Status: {row[4]}")
                print(f"   Time: {row[5]} - {row[6]}")
                print(f"   Date: {row[7]}")
                print(f"   Customer: {row[8]}")
                print(f"   Price: {row[9]} VND")
                
                booking_date = row[7]
                if isinstance(booking_date, str):
                    booking_date = booking_date.split('T')[0]
                else:
                    booking_date = booking_date.strftime("%Y-%m-%d")
                
                is_today = booking_date == today
                start_time = row[5]
                end_time = row[6]
                
                if is_today:
                    is_in_progress = start_time <= current_time < end_time
                    print(f"   🎯 In Progress: {'✅ YES' if is_in_progress else '❌ No'}")
                else:
                    print(f"   ❌ Not today (Date: {booking_date})")
                print()
        
        print("="*100 + "\n")
        
    except Exception as exc:
        print(f"❌ Error: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    check_all_bookings()
