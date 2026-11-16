"""
Blender Bridge Server for Antigravity AI Modding
Enables live interactive control of Blender from the AI assistant.
Runs a lightweight local socket server and executes commands via Blender's main-thread timer.

Usage inside Blender:
1. Open Blender.
2. Go to the 'Scripting' tab.
3. Open or paste this file and click 'Run Script' (Alt+P).
4. The server will start listening on 127.0.0.1:9876.
"""

import bpy
import socket
import threading
import json
import io
import sys
import traceback
import queue

PORT = 9876
HOST = '127.0.0.1'

task_queue = queue.Queue()
running = True
server_socket = None

def execute_on_main_thread():
    """Timer callback running on Blender's main thread to execute tasks safely."""
    global running
    if not running:
        return None  # Unregister timer
    
    while not task_queue.empty():
        task = task_queue.get()
        cmd = task.get("command")
        client_sock = task.get("client")
        
        response = {"status": "error", "output": "", "error": None}
        
        try:
            if cmd == "ping":
                response = {
                    "status": "ok",
                    "output": f"Blender {bpy.app.version_string} connected. File: {bpy.data.filepath or 'Untitled'}"
                }
            elif cmd == "get_scene_info":
                objects = [obj.name for obj in bpy.data.objects]
                collections = [col.name for col in bpy.data.collections]
                active_obj = bpy.context.active_object.name if bpy.context.active_object else None
                response = {
                    "status": "ok",
                    "output": json.dumps({
                        "filepath": bpy.data.filepath,
                        "active_object": active_obj,
                        "objects": objects,
                        "collections": collections
                    })
                }
            elif cmd == "execute":
                code = task.get("code", "")
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                redirected_out = io.StringIO()
                redirected_err = io.StringIO()
                sys.stdout = redirected_out
                sys.stderr = redirected_err
                
                exec_globals = {
                    "bpy": bpy,
                    "__name__": "__main__"
                }
                
                try:
                    exec(code, exec_globals)
                    response["status"] = "ok"
                    response["output"] = redirected_out.getvalue()
                except Exception as e:
                    response["status"] = "error"
                    response["error"] = traceback.format_exc()
                    response["output"] = redirected_out.getvalue()
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
            else:
                response["error"] = f"Unknown command: {cmd}"
        except Exception as e:
            response["status"] = "error"
            response["error"] = str(e)
            
        try:
            payload = json.dumps(response).encode('utf-8')
            # Prefix with 8-byte length header
            client_sock.sendall(len(payload).to_bytes(8, byteorder='big') + payload)
            client_sock.close()
        except Exception:
            pass
            
    return 0.05  # Run every 50ms

def socket_listener():
    global server_socket, running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[Blender Bridge] Server listening on {HOST}:{PORT}")
    except Exception as e:
        print(f"[Blender Bridge] Failed to bind to {HOST}:{PORT}: {e}")
        return

    while running:
        try:
            client, addr = server_socket.accept()
            # Read 8-byte length header
            raw_len = client.recv(8)
            if not raw_len or len(raw_len) < 8:
                client.close()
                continue
            length = int.from_bytes(raw_len, byteorder='big')
            data = b""
            while len(data) < length:
                chunk = client.recv(min(4096, length - len(data)))
                if not chunk:
                    break
                data += chunk
                
            task_data = json.loads(data.decode('utf-8'))
            task_data["client"] = client
            task_queue.put(task_data)
        except Exception as e:
            if running:
                print(f"[Blender Bridge] Connection error: {e}")
            break

def start_server():
    global running
    running = True
    thread = threading.Thread(target=socket_listener, daemon=True)
    thread.start()
    if not bpy.app.timers.is_registered(execute_on_main_thread):
        bpy.app.timers.register(execute_on_main_thread)
    print(f"[Blender Bridge] Started successfully on port {PORT}.")

if __name__ == "__main__":
    start_server()
