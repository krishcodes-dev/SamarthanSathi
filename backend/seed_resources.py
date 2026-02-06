
import asyncio
import sys
import os
import uuid
from sqlalchemy import select, text

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import AsyncSessionLocal as async_session_maker
from app.models.crisis import Resource, ResourceType, AvailabilityStatus

# Demo Data - Mumbai Resources (Merged)
RESOURCES = [
    # =====================
    # 🏥 MEDICAL
    # =====================
    {
        "provider_name": "Lilavati Hospital Ambulance Service",
        "resource_type": ResourceType.MEDICAL,
        "quantity_available": 5,
        "latitude": 19.0504,
        "longitude": 72.8291,
        "location_name": "Bandra West, Mumbai",
    },
    {
        "provider_name": "Cooper Hospital Trauma Center",
        "resource_type": ResourceType.MEDICAL,
        "quantity_available": 8,
        "latitude": 19.1075,
        "longitude": 72.8362,
        "location_name": "Juhu, Mumbai",
    },
    {
        "provider_name": "Sion Hospital ER Unit",
        "resource_type": ResourceType.MEDICAL,
        "quantity_available": 12,
        "latitude": 19.0357,
        "longitude": 72.8611,
        "location_name": "Sion Hospital, Mumbai",
    },
    {
        "provider_name": "Bombay Hospital Rapid Response",
        "resource_type": ResourceType.MEDICAL,
        "quantity_available": 4,
        "latitude": 18.9405,
        "longitude": 72.8282,
        "location_name": "Marine Lines, Mumbai",
    },
    {
        "provider_name": "Kokilaben Hospital Ambulance",
        "resource_type": ResourceType.MEDICAL,
        "quantity_available": 6,
        "latitude": 19.1316,
        "longitude": 72.8252,
        "location_name": "Andheri West, Mumbai",
    },
    {
        "provider_name": "Fortis Hospital Mulund Unit",
        "resource_type": ResourceType.MEDICAL,
        "quantity_available": 7,
        "latitude": 19.1623,
        "longitude": 72.9417,
        "location_name": "Mulund Goregaon Link Rd, Mumbai",
    },
    {
        "resource_type": ResourceType.MEDICAL,
        "provider_name": "K. B. Bhabha Municipal General Hospital",
        "quantity_available": 100,
        "latitude": 19.0630,
        "longitude": 72.8290,
        "location_name": "Bandra West",
    },
    {
        "resource_type": ResourceType.MEDICAL,
        "provider_name": "Hiranandani Hospital",
        "quantity_available": 50,
        "latitude": 19.1150,
        "longitude": 72.9050,
        "location_name": "Powai",
    },
    {
        "resource_type": ResourceType.MEDICAL,
        "provider_name": "Municipal Ambulance Service (Mumbai)",
        "quantity_available": 10,
        "latitude": 18.9400,
        "longitude": 72.8350,
        "location_name": "CST",
    },

    # =====================
    # 🚒 RESCUE
    # =====================
    {
        "provider_name": "Mumbai Fire Brigade - Andheri Station",
        "resource_type": ResourceType.RESCUE,
        "quantity_available": 3,
        "latitude": 19.1155,
        "longitude": 72.8447,
        "location_name": "Andheri East Fire Station",
    },
    {
        "provider_name": "Mumbai Fire Brigade - Byculla HQ",
        "resource_type": ResourceType.RESCUE,
        "quantity_available": 10,
        "latitude": 18.9723,
        "longitude": 72.8335,
        "location_name": "Byculla, Mumbai",
    },
    {
        "provider_name": "NDRF Unit 5 - Ghatkopar Base",
        "resource_type": ResourceType.RESCUE,
        "quantity_available": 40,
        "latitude": 19.0860,
        "longitude": 72.9090,
        "location_name": "Ghatkopar, Mumbai",
    },
    {
        "provider_name": "Juhu Beach Lifeguard Station",
        "resource_type": ResourceType.RESCUE,
        "quantity_available": 6,
        "latitude": 19.0984,
        "longitude": 72.8265,
        "location_name": "Juhu Beach, Mumbai",
    },
    {
        "provider_name": "Civil Defence Corps - Dadar",
        "resource_type": ResourceType.RESCUE,
        "quantity_available": 25,
        "latitude": 19.0178,
        "longitude": 72.8478,
        "location_name": "Dadar West, Mumbai",
    },
    {
        "provider_name": "Thane Disaster Response Force",
        "resource_type": ResourceType.RESCUE,
        "quantity_available": 15,
        "latitude": 19.2183,
        "longitude": 72.9781,
        "location_name": "Teen Hath Naka, Thane",
    },
    {
        "resource_type": ResourceType.RESCUE,
        "provider_name": "Fire Station Malad",
        "quantity_available": 4,
        "latitude": 19.1750,
        "longitude": 72.8500,
        "location_name": "Malad",
    },
    {
        "resource_type": ResourceType.RESCUE,
        "provider_name": "Municipal Rescue Cell Kurla",
        "quantity_available": 2,
        "latitude": 19.0700,
        "longitude": 72.8900,
        "location_name": "Kurla",
    },
    {
        "resource_type": ResourceType.RESCUE,
        "provider_name": "Police Disaster Response Unit – Andheri",
        "quantity_available": 3,
        "latitude": 19.1150,
        "longitude": 72.8400,
        "location_name": "Andheri",
    },

    # =====================
    # 🏕️ SHELTER
    # =====================
    {
        "provider_name": "St. Xavier's College Hall",
        "resource_type": ResourceType.SHELTER,
        "quantity_available": 200,
        "latitude": 18.9427,
        "longitude": 72.8315,
        "location_name": "Dhobi Talao, Mumbai",
    },
    {
        "provider_name": "Andheri Sports Complex",
        "resource_type": ResourceType.SHELTER,
        "quantity_available": 500,
        "latitude": 19.1245,
        "longitude": 72.8360,
        "location_name": "Andheri West, Mumbai",
    },
    {
        "provider_name": "Don Bosco School Matunga",
        "resource_type": ResourceType.SHELTER,
        "quantity_available": 150,
        "latitude": 19.0253,
        "longitude": 72.8580,
        "location_name": "Matunga, Mumbai",
    },
    {
        "provider_name": "NESCO Center Goregaon",
        "resource_type": ResourceType.SHELTER,
        "quantity_available": 1000,
        "latitude": 19.1550,
        "longitude": 72.8533,
        "location_name": "Goregaon East, Mumbai",
    },
    {
        "resource_type": ResourceType.SHELTER,
        "provider_name": "School Relief Camp – Parel",
        "quantity_available": 250,
        "latitude": 19.0150,
        "longitude": 72.8400,
        "location_name": "Parel",
    },
    {
        "resource_type": ResourceType.SHELTER,
        "provider_name": "IIT Powai Hostel (Temporary)",
        "quantity_available": 200,
        "latitude": 19.1300,
        "longitude": 72.9100,
        "location_name": "Powai",
    },

    # =====================
    # 🚰 FOOD/WATER
    # =====================
    {
        "provider_name": "Akshaya Patra Mumbai",
        "resource_type": ResourceType.FOOD,
        "quantity_available": 5000,
        "latitude": 19.0435,
        "longitude": 72.8227,
        "location_name": "Worli, Mumbai",
    },
    {
        "provider_name": "Roti Bank Foundation",
        "resource_type": ResourceType.FOOD,
        "quantity_available": 200,
        "latitude": 19.0166,
        "longitude": 72.8304,
        "location_name": "Lower Parel, Mumbai",
    },
    {
        "provider_name": "Mumbai Dabbawala Association",
        "resource_type": ResourceType.FOOD,
        "quantity_available": 1000,
        "latitude": 19.0600,
        "longitude": 72.8500,
        "location_name": "Bandra East, Mumbai",
    },
    {
        "provider_name": "Khalsa Aid Mumbai Team",
        "resource_type": ResourceType.WATER,
        "quantity_available": 1000,
        "latitude": 19.0805,
        "longitude": 72.8950,
        "location_name": "Vidyavihar, Mumbai",
    },
    {
        "provider_name": "Reliance Foundation Relief",
        "resource_type": ResourceType.FOOD,
        "quantity_available": 2000,
        "latitude": 19.0760,
        "longitude": 72.8777,
        "location_name": "BKC, Mumbai",
    },
    {
        "provider_name": "Zomato Feeding India",
        "resource_type": ResourceType.FOOD,
        "quantity_available": 500,
        "latitude": 19.1136,
        "longitude": 72.8697,
        "location_name": "Marol, Andheri East",
    },
    {
        "resource_type": ResourceType.WATER,
        "provider_name": "Municipal Water Tanker – Powai",
        "quantity_available": 8000,
        "latitude": 19.1150,
        "longitude": 72.9050,
        "location_name": "Powai",
    },
    {
        "resource_type": ResourceType.FOOD,
        "provider_name": "Food Distribution Center Dharavi",
        "quantity_available": 1500,
        "latitude": 19.0300,
        "longitude": 72.8500,
        "location_name": "Dharavi",
    },
    {
        "resource_type": ResourceType.WATER,
        "provider_name": "Municipal Tanker Goregaon",
        "quantity_available": 6000,
        "latitude": 19.1600,
        "longitude": 72.8600,
        "location_name": "Goregaon",
    },
]

async def seed_resources():
    print("🌱 Starting Resource Seeding...")
    async with async_session_maker() as session:
        inserted = 0
        skipped = 0

        for r_data in RESOURCES:
            # Check if exists by provider name
            stmt = select(Resource).where(Resource.provider_name == r_data["provider_name"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                skipped += 1
                continue

            # Create new resource
            resource = Resource(
                id=uuid.uuid4(),
                provider_name=r_data["provider_name"],
                resource_type=r_data["resource_type"],
                quantity_available=r_data["quantity_available"],
                latitude=r_data["latitude"],
                longitude=r_data["longitude"],
                location_name=r_data["location_name"],
                availability_status=AvailabilityStatus.AVAILABLE
            )
            session.add(resource)
            inserted += 1
        
        await session.commit()
        
        print(f"✅ Seeding complete!")
        print(f"   Injected: {inserted}")
        print(f"   Skipped:  {skipped}")
        
        # Verify total count
        count_result = await session.execute(text("SELECT COUNT(*) FROM resources"))
        count = count_result.scalar()
        print(f"📊 Total resource count: {count}")

if __name__ == "__main__":
    try:
        asyncio.run(seed_resources())
    except Exception as e:
        print(f"❌ Error seeding resources: {e}")
        sys.exit(1)
