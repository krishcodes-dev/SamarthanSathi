import sys
import os
import asyncio
from typing import List

# Add current directory to path
sys.path.append(os.getcwd())

from sqlalchemy import select
from app.core.database import get_db, init_db, engine
from app.models.crisis import CrisisRequest, RequestStatus, Resource, ResourceType
from app.services.matching import match_resources

async def audit_async():
    print("\n" + "="*50)
    print("7. DATABASE INTEGRITY AUDIT")
    print("="*50)
    
    # 1. Check Enum
    try:
        # Just accessing the enum member to verify it exists
        status = RequestStatus.IN_PROGRESS
        print("✅ RequestStatus.IN_PROGRESS enum exists")
    except AttributeError:
        print("❌ RequestStatus.IN_PROGRESS enum MISSING (critical bug!)")
        return

    # 2. Check DB Access & Content
    # We need a session. get_db is a generator.
    async for db in get_db():
        try:
            # Check Requests
            result = await db.execute(select(CrisisRequest).limit(5))
            requests = result.scalars().all()
            print(f"✅ Database accessible, {len(requests)} requests found (Sample)")
            
            # Check Resources (Crucial for next step)
            result = await db.execute(select(Resource))
            resources = result.scalars().all()
            print(f"✅ {len(resources)} resources in registry")
            
            if not resources:
                print("⚠️  No resources found! Seeding recommended for matching test.")
                # We can't test matching effectively without resources
                # But we'll try with empty list or mock if needed.
                # The user's prompt said "Assume you have seeded resources".
                pass
            
            # --- 5. RESOURCE MATCHING AUDIT ---
            print("\n" + "="*50)
            print("5. RESOURCE MATCHING AUDIT")
            print("="*50)
            
            # Mock request logic from checkilst
            # Test matching logic
            test_request = {
                'need_type': 'medical',
                'location': {'lat': 19.1197, 'lng': 72.8464},  # Andheri
                'quantity': 5,
                'urgency_level': 'U1 - Critical'
            }
            
            print(f"Testing Match for: {test_request}")
            
            # match_resources expects args, not a dict
            # def match_resources(request_lat, request_lng, need_type, request_qty, urgency_score, urgency_level, available_resources, top_n)
            
            matches = match_resources(
                request_lat=test_request['location']['lat'],
                request_lng=test_request['location']['lng'],
                need_type=test_request['need_type'],
                request_qty=test_request['quantity'],
                urgency_score=80, # Derived from U1
                urgency_level=test_request['urgency_level'],
                available_resources=resources,
                top_n=3
            )
            
            print(f"Found {len(matches)} matches")
            for i, match in enumerate(matches[:3], 1):
                print(f"\n{i}. {match['provider_name']} ({match['resource_type']})")
                print(f"   Distance: {match['distance_km']}km")
                print(f"   Match score: {match['match_score']}")
                # print reasoning clean
                print(f"   Reasoning: {match['reasoning'][0]}") # Top reason
                
            # validations
            if len(matches) > 0:
                top = matches[0]
                if top['match_score'] > matches[-1]['match_score']:
                    print("✅ Sorting verified (Score desc)")
                else:
                    print(f"⚠️  Sorting check: Top {top['match_score']} vs Last {matches[-1]['match_score']}")
            else:
                print("⚠️  No matches found (Check resource DB)")
                
        except Exception as e:
            print(f"❌ Database/Matching Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # We are inside the context manager of get_db provided by async generator...
            # actually we looped over it. breaks loop.
            pass
        break 

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(audit_async())
