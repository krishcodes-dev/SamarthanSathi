#!/usr/bin/env python3
"""
End-to-End Crisis Request Demo
Submit a crisis message and watch it flow through the system!
"""
import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def submit_crisis(message: str):
    """Submit a crisis request and return the ID"""
    print(f"\n📨 Submitting crisis request...")
    print(f"Message: '{message}'\n")
    
    response = requests.post(
        f"{API_BASE}/requests/submit",
        json={"raw_text": message}
    )
    
    # Check for both 200 and 201 (Created)
    if response.status_code in [200, 201]:
        data = response.json()
        request_id = data["id"]
        print(f"✅ Request submitted! ID: {request_id}\n")
        return request_id
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def get_request_details(request_id: str):
    """Get full details of a request"""
    response = requests.get(f"{API_BASE}/requests/{request_id}")
    if response.status_code == 200:
        return response.json()
    return None

def find_resources(request_id: str):
    """Find matching resources for a request"""
    response = requests.get(f"{API_BASE}/requests/{request_id}/matches")
    if response.status_code == 200:
        return response.json()
    return []

def dispatch_resource(request_id: str, resource_id: str, quantity: int = 1):
    """Dispatch a resource"""
    print(f"\n🚀 Dispatching resource {resource_id[:8]}...")
    response = requests.post(
        f"{API_BASE}/matches/{request_id}/dispatch/{resource_id}",
        json={"quantity": quantity}
    )
    
    if response.status_code == 200:
        print("✅ DISPATCH SUCCESSFUL!")
        data = response.json()
        print(f"   Status: {data.get('status', 'dispatched')}")
        print(f"   Remaining Capacity: {data.get('remaining_capacity')}")
        return True
    else:
        print(f"❌ Dispatch Failed: {response.status_code}")
        print(response.text)
        return False

def print_analysis(data: dict):
    """Pretty print the AI analysis"""
    print("=" * 60)
    print("🤖 AI ANALYSIS RESULTS")
    print("=" * 60)
    
    # Extraction
    extraction = data.get("extraction", {})
    print(f"\n📍 EXTRACTED INFORMATION:")
    print(f"  Location: {extraction.get('location', 'Unknown')}")
    
    if extraction.get('location_alternatives'):
         print(f"  ⚠️  AMBIGUITY DETECTED:")
         for alt in extraction['location_alternatives']:
             conf = float(alt.get('confidence', 0)) * 100
             print(f"     ○ {alt.get('value')} ({conf:.0f}%)")
             
    print(f"  Need Type: {extraction.get('need_type', 'Unknown')}")
    print(f"  Quantities: {extraction.get('quantities', [])}")
    print(f"  Contact Info: {extraction.get('contact_info', [])}")
    
    # Urgency
    urgency = data.get("urgency_analysis", {})
    if urgency:
        print(f"\n🚨 URGENCY ANALYSIS:")
        print(f"  Score: {urgency.get('score', 0)}/100")
        print(f"  Level: {urgency.get('level', 'Unknown')}")
        print(f"  Confidence: {urgency.get('confidence', 0)}%")
        print(f"\n  Reasoning:")
        for reason in urgency.get("reasoning", []):
            print(f"    • {reason}")
        
        flags = urgency.get("flags", [])
        if flags:
            print(f"\n  🚩 Flags: {', '.join(flags)}")
    
    print("\n" + "=" * 60)

def print_resources(resources: list):
    """Pretty print matched resources"""
    print("\n🎯 MATCHED RESOURCES:")
    print("=" * 60)
    
    if not resources:
        print("  No matching resources found")
    else:
        for i, res in enumerate(resources, 1):
            print(f"\n  #{i} {res.get('provider_name', 'Unknown')}")
            print(f"     Type: {res.get('resource_type')}")
            print(f"     Distance: {res.get('distance_km', 0):.2f} km")
            print(f"     Available: {res.get('quantity_available', 0)} units")
            print(f"     Match Score: {res.get('match_score', 0)}/100")
            if res.get('match_reasoning'):
                print(f"     Reasoning: {res['match_reasoning']}")
    
    print("=" * 60)

def main():
    print("🆘 SamarthanSathi - End-to-End Demo")
    print("=" * 60)
    
    # Example crisis messages you can try:
    print("\n💡 Example crisis messages you can send:")
    print("1. 'Emergency! 20 people trapped in building collapse at Dharavi. Need rescue team immediately!'")
    print("2. 'Urgent: Need 100 food packets at Andheri relief camp. 50 families without food.'")
    print("3. 'Fire at Kurla market! Need fire brigade and ambulances. Multiple injuries.'")
    print("4. 'Flood in Bandra. 30 people stuck on rooftop. Need boats urgently!'")
    print("5. 'Medical emergency: Need blood type O+ at Sion hospital. Patient critical.'")
    
    # Get user input
    print("\n" + "=" * 60)
    crisis_message = input("\n✍️  Enter your crisis message: ").strip()
    
    if not crisis_message:
        print("❌ No message provided. Exiting.")
        return
    
    # Submit request
    request_id = submit_crisis(crisis_message)
    if not request_id:
        return
    
    # Wait a moment for processing
    print("⏳ Processing... (waiting 1 second)")
    time.sleep(1)
    
    # Get details
    print("\n🔍 Fetching analysis...")
    details = get_request_details(request_id)
    
    if details:
        print_analysis(details)
    
    # Find resources
    print("\n🔍 Finding matching resources...")
    resources = find_resources(request_id)
    print_resources(resources)
    
    if resources:
        choice = input("\n🚀 Dispatch top resource? (y/n): ").strip().lower()
        if choice == 'y':
            top_res = resources[0]
            resource_id = top_res.get('resource_id')
            if resource_id:
                dispatch_resource(request_id, resource_id)
            else:
                print("❌ Error: Top match has no resource_id")
    
    # Instructions
    print("\n" + "=" * 60)
    print("📊 NEXT STEPS:")
    print("=" * 60)
    print(f"\n1. Open dashboard: http://localhost:5173")
    print(f"2. Your request should appear at the top (ID: {request_id[:8]}...)")
    print(f"3. Click 'Reasoning' to see the urgency analysis")
    print(f"4. Click 'Find Resources' to see matches")
    print(f"\n✨ Your request is now live in the system!")

if __name__ == "__main__":
    main()
