import urllib.request
import urllib.error
import json
import time

scenarios = [
    {
        "name": "SCENARIO 1: GREEN (high confidence)",
        "payload": {
            "caller_text": "I'm near the big clock tower",
            "signals": [
                { "type": "GPS",  "data": "$GPGGA,092311,1304.96,N,08016.24,E,1,07,1.1,14.5,M" },
                { "type": "W3W",  "data": "///fills.snap.brave" },
                { "type": "ADDRESS", "data": "Anna Salai, Chennai" }
            ]
        }
    },
    {
        "name": "SCENARIO 2: YELLOW (conflict / indoor GPS)",
        "payload": {
            "caller_text": "I'm inside a shopping mall, ground floor",
            "signals": [
                { "type": "GPS",  "data": "$GPGGA,092311,1304.96,N,08016.24,E,1,03,7.8,14.5,M" },
                { "type": "CELL", "data": "{ \"tower_lat\": 13.071, \"tower_lon\": 80.258, \"signal_dbm\": -102 }" }
            ]
        }
    },
    {
        "name": "SCENARIO 3: RED (disaster / search zone)",
        "payload": {
            "caller_text": "There was an explosion, I can see a red building and a petrol station",
            "signals": [
                { "type": "CELL", "data": "{ \"tower_lat\": 13.060, \"tower_lon\": 80.248, \"signal_dbm\": -110 }" }
            ],
            "disaster_mode": True
        }
    }
]

url = 'http://localhost:8000/locate'
headers = {'Content-Type': 'application/json'}

def test_scenarios():
    results_md = "# Scenario Test Results\n\n"
    for scenario in scenarios:
        print(f"Running {scenario['name']}...")
        req = urllib.request.Request(url, data=json.dumps(scenario['payload']).encode('utf-8'), headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                results_md += f"## {scenario['name']}\n"
                results_md += f"**Input Signals**: {', '.join([s['type'] for s in scenario['payload']['signals']])}\n"
                if scenario['payload'].get('disaster_mode'):
                    results_md += "**Mode**: DISASTER\n"
                
                results_md += f"**Status**: `{result.get('dispatch_status')}`\n"
                results_md += f"**Confidence**: `{result.get('confidence_score')}`\n"
                results_md += f"**Uncertainty Radius**: `{result.get('uncertainty_radius_m')} m`\n"
                results_md += f"**Explanation**: _{result.get('explanation')}_\n"
                if result.get('followup_question'):
                    results_md += f"**Follow-up Question**: _{result.get('followup_question')}_\n"
                results_md += "\n"
                
        except urllib.error.URLError as e:
            results_md += f"## {scenario['name']}\n**Error**: {e}\n\n"
            print(f"Error: {e}")

    with open("C:/Users/tamoj/.gemini/antigravity/brain/8c003e20-b4eb-41a3-8a9d-363967726985/test_results.md", "w") as f:
        f.write(results_md)
    print("Done. Results written to test_results.md")

if __name__ == '__main__':
    # Wait for server to be fully up
    time.sleep(2)
    test_scenarios()
