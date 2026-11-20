"""
KrishiMulya AI: Unified Application Launcher
Starts both the Flask API Backend (Port 5000) and React Frontend (Port 5173),
and automatically opens the portal in your browser.
"""

import os
import sys
import time
import subprocess
import webbrowser
import urllib.request
import urllib.error

def check_backend_health(url="http://127.0.0.1:5000/api/health", retries=25, delay=1.0):
    print("Waiting for Flask Backend to initialize...")
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    print("Flask Backend is live and healthy on http://127.0.0.1:5000!")
                    return True
        except Exception:
            time.sleep(delay)
    return False

def check_frontend_ready(url="http://localhost:5173", retries=25, delay=1.0):
    print("Waiting for Vite React Frontend...")
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    print("React Frontend is live on http://localhost:5173!")
                    return True
        except Exception:
            time.sleep(delay)
    return False

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")

    env = os.environ.copy()
    env["PYTHONPATH"] = root_dir
    env["PYTHONUNBUFFERED"] = "1"

    print("==================================================================")
    print("  KrishiMulya AI: Crop Price Prediction & Decision Support System")
    print("  MCA Final Year Project - Karnataka APMC Market Intelligence")
    print("==================================================================")

    # 1. Start Backend
    print("\n[1/3] Launching Flask REST Backend on port 5000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "backend.app"],
        cwd=root_dir,
        env=env
    )

    if not check_backend_health():
        print("Backend startup timed out. Check console logs.")
        backend_proc.terminate()
        sys.exit(1)

    # 2. Start Frontend
    print("\n[2/3] Launching React Vite Frontend on port 5173...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"],
        cwd=frontend_dir
    )

    check_frontend_ready()

    # 3. Open Browser
    portal_url = "http://localhost:5173"
    print(f"\n[3/3] Opening portal in your browser: {portal_url}")
    print("\n------------------------------------------------------------------")
    print("  Web Portal:      http://localhost:5173")
    print("  Backend API:     http://localhost:5000/api")
    print("  Health Endpoint: http://localhost:5000/api/health")
    print("")
    print("  Demo Logins:")
    print("    Farmer Account:  farmer@karnataka.gov  /  Farmer@123")
    print("    Admin Account:   admin@cropprice.ai    /  Admin@123")
    print("------------------------------------------------------------------")
    print("Press Ctrl+C to stop both servers.\n")

    try:
        webbrowser.open(portal_url)
    except Exception:
        pass

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down KrishiMulya AI servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Stopped successfully.")

if __name__ == "__main__":
    main()
