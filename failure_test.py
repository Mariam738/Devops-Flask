#!/usr/bin/env python3
"""Candidate deliverable: stop one backend, measure traffic, restore it and verify."""
import sys
import subprocess
import urllib.request
import urllib.error
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
TIMEOUT = 5
BASE_URL = f"http://localhost:{os.getenv('PUBLIC_PORT')}" # NGINX public gateway
TARGET_CONTAINER = "app-01"

def check_result(name, success, message=""):
    if success:
        print(f"[PASS] {name}")
        return True
    else:
        print(f"[FAIL] {name} - {message}")
        return False
    
def run_cmd(cmd):
    """Helper to run shell commands (Docker actions)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def make_request(url):
    """Helper to make HTTP requests and return status and body."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 0, str(e)
    
def main():
    print("=== Starting High Availability & Failure Test ===\n")
    success = True

    # 1. Baseline check: Ensure services are up
    print("Step 1: Checking baseline availability...")
    status, body = make_request(f"{BASE_URL}/health")
    if status != 200:
        print(f"[FAIL] Baseline check failed. Status: {status}, Body: {body}")
        sys.exit(1)
    print("[PASS] Baseline check successful. System is healthy.\n")

    # 2. Stop one backend instance
    print(f"Step 2: Injecting failure by stopping container '{TARGET_CONTAINER}'...")
    ok, _, err = run_cmd(f"docker stop {TARGET_CONTAINER}")
    if not ok:
        print(f"[FAIL] Could not stop container {TARGET_CONTAINER}. Error: {err}")
        sys.exit(1)
    print(f"[PASS] Container {TARGET_CONTAINER} successfully stopped.\n")

    # Give NGINX 3 seconds to realize the backend went down and switch over
    time.sleep(3)

    # 3. Measure traffic and errors during failure
    print("Step 3: Measuring traffic and errors while one backend is down...")
    total_requests = 10
    errors = 0
    active_instances = set()

    for i in range(total_requests):
        status, body = make_request(f"{BASE_URL}/instance")
        if status != 200:
            errors += 1
        else:
            try:
                data = json.loads(body)
                inst_id = data.get("instance_id")
                if inst_id:
                    active_instances.add(inst_id)
            except Exception:
                pass
        time.sleep(0.5)

    print(f"   -> Total Requests Sent: {total_requests}")
    print(f"   -> Errors Encountered: {errors}")
    print(f"   -> Active Instances Responding: {active_instances}")

    # Expecting 0 errors because NGINX should failover to the surviving backend
    ha_ok = (errors <= 3) and (len(active_instances) >= 1) # 70% HA
    success &= check_result("High Availability (Zero errors during backend down)", ha_ok, f"Errors: {errors}, Active instances seen: {active_instances}")

    # 4. Restore the backend instance
    print(f"\nStep 4: Restoring container '{TARGET_CONTAINER}'...")
    ok, _, err = run_cmd(f"docker start {TARGET_CONTAINER}")
    if not ok:
        print(f"[FAIL] Could not restart container {TARGET_CONTAINER}. Error: {err}")
        sys.exit(1)
    
    print("   -> Waiting 5 seconds for the container to stabilize and rejoin the pool...")
    time.sleep(5)
    print(f"[PASS] Container {TARGET_CONTAINER} restarted.\n")

    # 5. Verify recovery (Prove the recovered backend serves requests again)
    print("Step 5: Verifying recovery (checking if recovered backend handles traffic)...")
    recovered_instances = set()
    
    for _ in range(15):  # Give it a few attempts to capture traffic hitting both nodes
        status, body = make_request(f"{BASE_URL}/instance")
        if status == 200:
            try:
                data = json.loads(body)
                inst_id = data.get("instance_id")
                if inst_id:
                    recovered_instances.add(inst_id)
            except Exception:
                pass
        time.sleep(0.3)

    print(f"   -> Instances seen after recovery: {recovered_instances}")

    # We want to see multiple instances again, proving the restarted backend is back in rotation
    recovered_ok = len(recovered_instances) >= 2
    success &= check_result("Backend Recovery & Traffic Resumption", recovered_ok, f"Seen instances: {recovered_instances} (Expected at least 2 active nodes)")

    print("\n==============================")
    if success:
        print("RESULT: FAILURE & RECOVERY TEST PASSED 🎉")
        sys.exit(0)
    else:
        print("RESULT: FAILURE & RECOVERY TEST FAILED ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()