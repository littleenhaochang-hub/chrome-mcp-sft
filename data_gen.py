import json
import time
import os
import urllib.request
import urllib.error
import subprocess
import argparse

# Configuration
SYSTEM_PROMPT = """You are an autonomous web browser agent. 
You will be given a minified DOM (Accessibility Tree) and a Task.
Output ONLY a JSON object representing your next action. 
Valid actions:
{"method": "click", "params": {"selector": "<css_selector>"}}
{"method": "type", "params": {"selector": "<css_selector>", "text": "<text>"}}
{"method": "scroll", "params": {"direction": "down"}}
{"method": "done", "params": {"result": "<final_answer>"}}
"""

def run_cmd(cmd: str) -> str:
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[Error] Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()

def get_dom_snapshot() -> str:
    """Get the current accessibility tree/text snapshot from OpenClaw Chrome MCP."""
    print("[Browser] Capturing DOM snapshot...")
    # Using the local Chrome session via OpenClaw
    return run_cmd('openclaw browser --browser-profile user snapshot --format text')

def execute_action(action_json: dict):
    """Execute the parsed JSON action via OpenClaw Chrome MCP."""
    method = action_json.get("method")
    params = action_json.get("params", {})
    
    print(f"[Browser] Executing: {method} {params}")
    
    # Note: These are conceptual mappings to the OpenClaw CLI.
    # In a real environment, you'd use the raw MCP JSON-RPC payload or exact CLI flags.
    if method == "click":
        # Pseudo-command, assumes openclaw browser click <selector>
        pass 
    elif method == "type":
        # Pseudo-command
        pass
    elif method == "scroll":
        # Pseudo-command
        pass
    
    time.sleep(2) # Wait for network/rendering

def ask_oracle(task: str, minified_dom: str) -> dict:
    """Ask Gemini 3.1 Pro via urllib for the next action."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY environment variable not set.")
        return {"method": "error", "params": {"msg": "No API key"}}
        
    prompt = f"{SYSTEM_PROMPT}\n\nTASK: {task}\n\nCURRENT DOM:\n{minified_dom}\n\nNEXT ACTION (JSON ONLY):"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.0}
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    
    print("[Oracle] Thinking...")
    try:
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            response = res_data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Clean markdown formatting if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
                
            return json.loads(response)
    except urllib.error.HTTPError as e:
        print(f"[Error] API request failed with status: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
        return {"method": "error", "params": {"msg": "Oracle request failed"}}
    except Exception as e:
        print(f"[Error] Failed to ask Oracle or parse JSON: {e}")
        return {"method": "error", "params": {"msg": "Oracle request failed"}}

def run_trajectory(task: str, url: str):
    print(f"=== Starting Oracle Trajectory ===")
    print(f"Task: {task}\nURL: {url}")
    
    # 1. Open URL
    run_cmd(f'openclaw browser --browser-profile user open "{url}"')
    time.sleep(3) # Wait for initial load
    
    dataset = []
    max_steps = 15 # Allow enough steps to complete the flight search flow
    
    for step in range(max_steps):
        print(f"\n--- Step {step + 1} ---")
        
        # 2. Get DOM & Minify
        raw_dom = get_dom_snapshot()
        # Truncate strictly to simulate the 4K token edge limit
        minified_dom = raw_dom[:4000] 
        
        # 3. Get Oracle Action
        action = ask_oracle(task, minified_dom)
        
        # 4. Record State-Action Pair
        record = {
            "instruction": task,
            "input_state": minified_dom,
            "output_action": action
        }
        dataset.append(record)
        
        # Append to JSONL immediately to prevent data loss
        with open("flight_search_dataset.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
        # 5. Execute Action
        if action.get("method") == "done":
            print(f"[Success] Task completed. Result: {action.get('params', {}).get('result')}")
            break
        elif action.get("method") == "error":
            print("[Abort] Oracle error.")
            break
            
        execute_action(action)
        
    print("=== Trajectory Complete ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect Flight Search data via Chrome MCP")
    parser.add_argument("--task", type=str, default="Find the cheapest one-way flight from TPE to NRT on April 15th.", help="The natural language task")
    parser.add_argument("--url", type=str, default="https://www.google.com/flights", help="Starting URL")
    args = parser.parse_args()
    
    run_trajectory(args.task, args.url)
", help="The natural language task")
    parser.add_argument("--url", type=str, default="https://www.google.com/flights", help="Starting URL")
    args = parser.parse_args()
    
    run_trajectory(args.task, args.url)
