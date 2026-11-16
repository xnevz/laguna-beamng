"""
Blender Bridge Client for Antigravity AI Modding
Connects to a running Blender instance via the bridge server (Mode B - Live),
or falls back to headless Blender execution (Mode A - Background).
"""

import socket
import json
import sys
import os
import subprocess
import argparse

PORT = 9876
HOST = '127.0.0.1'
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe"

def send_command(command, data=None, timeout=120):
    """Attempt to send a command to the live Blender instance."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((HOST, PORT))
    except (ConnectionRefusedError, socket.timeout):
        return None
    
    payload = {"command": command}
    if data:
        payload.update(data)
    
    encoded = json.dumps(payload).encode('utf-8')
    s.sendall(len(encoded).to_bytes(8, byteorder='big') + encoded)
    
    try:
        raw_len = s.recv(8)
        if not raw_len or len(raw_len) < 8:
            s.close()
            return {"status": "error", "error": "Empty response from Blender"}
        length = int.from_bytes(raw_len, byteorder='big')
        
        response_data = b""
        while len(response_data) < length:
            chunk = s.recv(min(4096, length - len(response_data)))
            if not chunk:
                break
            response_data += chunk
        s.close()
        return json.loads(response_data.decode('utf-8'))
    except socket.timeout:
        s.close()
        return {"status": "error", "error": "Socket timed out waiting for response"}

def execute_live(code, timeout=120):
    return send_command("execute", {"code": code}, timeout=timeout)

def ping():
    return send_command("ping", timeout=5)

def execute_headless(script_path, blend_path=None):
    """Execute a script headlessly in Blender background mode."""
    cmd = [BLENDER_PATH, "-b"]
    if blend_path and os.path.exists(blend_path):
        cmd.append(blend_path)
    cmd.extend(["-P", script_path])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "ok" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr if result.returncode != 0 else None
    }

def run_script(script_path, blend_path=None, force_headless=False, timeout=120):
    """Run script either live (if Blender is open) or headless."""
    if not force_headless:
        p = ping()
        if p and p.get("status") == "ok":
            print(f"[Bridge] Live Blender session detected: {p.get('output')}")
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            res = execute_live(code, timeout=timeout)
            return res
            
    print("[Bridge] Live Blender session not found or headless requested. Running in background...")
    return execute_headless(script_path, blend_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blender Bridge Client")
    parser.add_argument("script", nargs="?", help="Python script to execute in Blender")
    parser.add_argument("--blend", help="Path to .blend file (for headless mode)")
    parser.add_argument("--ping", action="store_true", help="Ping live Blender session")
    parser.add_argument("--headless", action="store_true", help="Force headless execution")
    parser.add_argument("--eval", help="Direct Python code string to execute")
    parser.add_argument("--timeout", type=int, default=120, help="Socket timeout in seconds")
    
    args = parser.parse_args()
    
    if args.ping:
        res = ping()
        if res:
            print("Response:", res)
        else:
            print("Blender live bridge is not currently running.")
    elif args.eval:
        p = ping()
        if p and p.get("status") == "ok" and not args.headless:
            print(f"[Bridge] Executing on live Blender: {p.get('output')}")
            print(execute_live(args.eval, timeout=args.timeout))
        else:
            print("[Bridge] Running eval in background Blender...")
            temp_script = os.path.join(os.path.dirname(__file__), "_temp_eval.py")
            with open(temp_script, "w", encoding="utf-8") as f:
                f.write(args.eval)
            print(execute_headless(temp_script, args.blend))
            if os.path.exists(temp_script):
                os.remove(temp_script)
    elif args.script:
        res = run_script(args.script, args.blend, args.headless, timeout=args.timeout)
        print(json.dumps(res, indent=2))
    else:
        parser.print_help()
