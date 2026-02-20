#!/usr/bin/env python3
"""
Test the scoring system to verify it matches iOS behavior
"""

import sys
from datetime import datetime, timedelta

# Import the scoring function from main.py
sys.path.insert(0, '.')
from main import calculate_island_score

def test_scenario(name: str, context: dict, device_info: dict):
    """Test a specific scenario and show scores"""
    print(f"\n{'='*60}")
    print(f"Scenario: {name}")
    print(f"Time: {context['current_hour']}:00")
    print(f"Meetings today: {context['meetings_today']}")
    print(f"Next meeting in: {context['next_meeting_minutes']} min" if context['next_meeting_minutes'] else "Next meeting: None")
    print(f"Unread emails: {context['unread_count']}")
    print(f"{'='*60}")
    
    island_types = ["dashboard", "meeting_prep", "meeting_marathon", "sunrise", "focus_mode", "breaking_news"]
    scores = []
    
    for island_type in island_types:
        score, reason = calculate_island_score(island_type, context, device_info)
        scores.append({
            "type": island_type,
            "score": score,
            "reason": reason
        })
    
    # Sort by score
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    print("\nScores:")
    for i, s in enumerate(scores):
        emoji = "🏆" if i == 0 else "  "
        print(f"{emoji} {i+1}. {s['type']:20s} {int(s['score']):3d} - {s['reason']}")
    
    winner = scores[0]
    print(f"\n✅ Winner: {winner['type']} (score: {int(winner['score'])})")
    return winner['type']

# Test scenarios
print("🧪 Testing Island Scoring System")
print("="*60)

# Scenario 1: Morning (7 AM)
winner1 = test_scenario(
    "Morning - 7 AM",
    {
        "current_hour": 7,
        "meetings_today": 2,
        "next_meeting_minutes": 120,  # 2 hours away
        "unread_count": 5
    },
    {"last_island_type": None, "last_island_shown_time": None}
)

# Scenario 2: Meeting in 10 minutes
winner2 = test_scenario(
    "Meeting Prep - 10 min before meeting",
    {
        "current_hour": 10,
        "meetings_today": 3,
        "next_meeting_minutes": 10,
        "unread_count": 15
    },
    {"last_island_type": None, "last_island_shown_time": None}
)

# Scenario 3: Busy day (5 meetings)
winner3 = test_scenario(
    "Meeting Marathon - 5 meetings today",
    {
        "current_hour": 14,
        "meetings_today": 5,
        "next_meeting_minutes": 60,
        "unread_count": 20
    },
    {"last_island_type": None, "last_island_shown_time": None}
)

# Scenario 4: Night time (10 PM)
winner4 = test_scenario(
    "Night - 10 PM",
    {
        "current_hour": 22,
        "meetings_today": 3,
        "next_meeting_minutes": None,  # No more meetings today
        "unread_count": 12
    },
    {"last_island_type": None, "last_island_shown_time": None}
)

# Scenario 5: Work hours, normal day
winner5 = test_scenario(
    "Work Hours - Normal day",
    {
        "current_hour": 14,
        "meetings_today": 2,
        "next_meeting_minutes": 180,
        "unread_count": 8
    },
    {"last_island_type": None, "last_island_shown_time": None}
)

# Scenario 6: Anti-repetition test
print("\n" + "="*60)
print("Testing Anti-Repetition")
print("="*60)

# First show
context = {
    "current_hour": 14,
    "meetings_today": 2,
    "next_meeting_minutes": 180,
    "unread_count": 8
}
device_info = {"last_island_type": None, "last_island_shown_time": None}

winner_first = test_scenario("First rotation", context, device_info)

# Immediately after (should penalize the winner)
device_info = {
    "last_island_type": winner_first,
    "last_island_shown_time": datetime.now().isoformat()
}

winner_second = test_scenario("Second rotation (immediately after)", context, device_info)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Morning (7 AM):              {winner1}")
print(f"Meeting in 10 min:           {winner2}")
print(f"5 meetings today:            {winner3}")
print(f"Night (10 PM):               {winner4}")
print(f"Work hours (normal):         {winner5}")
print(f"Anti-repetition test:        {winner_first} → {winner_second}")
print("="*60)

# Expected results
print("\n" + "="*60)
print("EXPECTED vs ACTUAL")
print("="*60)

expectations = [
    ("Morning (7 AM)", "sunrise", winner1),
    ("Meeting in 10 min", "meeting_prep", winner2),
    ("5 meetings today", "meeting_marathon", winner3),
    ("Night (10 PM)", "breaking_news or focus_mode or dashboard", winner4),
    ("Work hours", "dashboard or breaking_news", winner5),
    ("Anti-repetition", f"NOT {winner_first}", winner_second)
]

all_pass = True
for scenario, expected, actual in expectations:
    if "or" in expected:
        options = [opt.strip() for opt in expected.split("or")]
        passed = actual in options
    elif expected.startswith("NOT"):
        not_expected = expected.replace("NOT ", "")
        passed = actual != not_expected
    else:
        passed = actual == expected
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {scenario:25s} Expected: {expected:30s} Got: {actual}")
    if not passed:
        all_pass = False

print("="*60)
if all_pass:
    print("✅ ALL TESTS PASSED - Scoring system working as expected!")
else:
    print("❌ SOME TESTS FAILED - Review the scoring logic")
print("="*60)
