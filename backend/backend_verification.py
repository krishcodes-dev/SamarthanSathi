# backend_verification.py
from app.services.extraction import extract_entities
from app.services.urgency import calculate_urgency

print("="*70)
print("TARGETED FIX VERIFICATION")
print("="*70)

test_cases = [
    # (message, expected_need, expected_urgency_level)
    ("Building collapse Kurla", "rescue", "U1"),
    ("fire bandra", "rescue", "U1"),
    ("help flood area powai", "rescue", "U1"),
    ("3 children unconscious", "medical", "U1"),
    ("50 blankets needed near Malad", "blankets", "U3"),
    ("looking for water tanker info", None, "U5"),
]

passed = 0
failed = 0

for text, expected_need, expected_level in test_cases:
    print(f"\n📝 {text}")
    
    extraction = extract_entities(text)
    urgency = calculate_urgency(text, extraction)
    
    need_ok = extraction.need_type == expected_need
    level_ok = expected_level in urgency.level
    
    if need_ok and level_ok:
        print(f"   ✅ PASS")
        passed += 1
    else:
        print(f"   ❌ FAIL")
        failed += 1
    
    print(f"      Need: {extraction.need_type} (expected: {expected_need}) {'✅' if need_ok else '❌'}")
    print(f"      Urgency: {urgency.level} (expected: {expected_level}) {'✅' if level_ok else '❌'}")
    print(f"      Score: {urgency.score}")
    print(f"      Top reason: {urgency.reasoning[0][:70]}...")

print("\n" + "="*70)
print(f"RESULTS: {passed} passed, {failed} failed")
if failed == 0:
    print("✅ ALL TESTS PASSED - READY FOR DEMO")
else:
    print(f"⚠️  {failed} tests failed - review fixes")
print("="*70)
