# Command to display the last login information
# Usage: last

import auth
import json
import os

def run(args, fs):
    sessions_file = os.path.join("fs", "var", "sessions.json")

    if not os.path.exists(sessions_file):
        print("No login records found.")
        return
    
    with open(sessions_file, 'r') as file:
        sessions = json.load(file)
    
    print("Recent logins:")
    
    all_sessions = []
    for username, user_sessions in sessions.items():
        for session in user_sessions:
            all_sessions.append({
                "username": username,
                "action": session["action"],
                "timestamp": session["timestamp"]
            })

    all_sessions.sort(key=lambda x: x["timestamp"], reverse=True)

    for session in all_sessions[:10]:
        print(f"{session['username']:12} {session['action']:15} {session['timestamp']}")
