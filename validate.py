#!/usr/bin/env python3
"""Candidate deliverable: implement environment validation; this is not a solution."""
import sys
import socket
import urllib.request
import urllib.error
import json
import time

# Configuration
TIMEOUT = 5
BASE_URL = "http://localhost:8080" # NGINX public gateway

def check_result(name, success, message=""):
    if success:
        print(f"[PASS] {name}")
        return True
    else:
        print(f"[FAIL] {name} - {message}")
        return False
    
def make_request(url, method="GET", data=None, headers=None):
    """Helper to make HTTP requests and return status, headers, and body."""
    if headers is None:
        headers = {}
    
    body = json.dumps(data).encode('utf-8') if data else None
    if data:
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            res_body = response.read().decode('utf-8')
            return response.status, dict(response.headers), res_body
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode('utf-8')
    except Exception as e:
        return 0, {}, str(e)

def make_request_with_retry(url, method="GET", data=None, headers=None, max_retries=5, delay=2):
    """Bounded wait: retries the request if it fails or hits a timeout."""
    for attempt in range(max_retries):
        status, res_headers, body = make_request(url, method=method, data=data, headers=headers)
        # If we get a valid response (even a 400/404/200, meaning the server is UP), return it
        if status != 0:
            return status, res_headers, body
        print(f"Service not ready yet (Attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
        time.sleep(delay)
    return 0, {}, "Connection timed out after retries"
   
def test_endpoints():
    print("--- 1. Testing Core Endpoints & Routing ---")
    success = True

    # GET /
    status, _, body = make_request_with_retry(f"{BASE_URL}/")
    is_ok = (status == 200 and "message" in body and "instance_id" in body)
    success &= check_result("GET / (Root Welcome)", is_ok, f"Status: {status}, Body: {body}")

    # GET /health
    status, _, body = make_request_with_retry(f"{BASE_URL}/health")
    success &= check_result("GET /health (Liveness)", status == 200, f"Status: {status}, Body: {body}")

    # GET /ready (Postgres & Redis check)
    status, _, body = make_request_with_retry(f"{BASE_URL}/ready")
    success &= check_result("GET /ready (Readiness)", status == 200, f"Status: {status}, Body: {body} (Dependencies may be down)")

    # GET /instance & Header check
    status, headers, body = make_request_with_retry(f"{BASE_URL}/instance")
    has_instance_header = "X-Instance-ID" in headers
    success &= check_result("GET /instance (Get Instace)", status == 200 and has_instance_header and "instance_id" in body, f"Status: {status}, Body: {body} (Missing X-Instance-ID header)")

    return success

def test_database_and_cache():
    print("\n--- 2. Testing Database (Postgres) & Cache (Redis) Flows ---")
    success = True

    # POST /records (Write to Postgres)
    payload = {"title": "Video proof"}
    status, _, body = make_request_with_retry(f"{BASE_URL}/records", method="POST", data=payload)
    success &= check_result("POST /records (Write)", status == 201, f"Status: {status}, Body: {body}")

    # GET /records (Read from Postgres)
    status, _, body = make_request_with_retry(f"{BASE_URL}/records")
    has_record = status == 200 and "Video proof" in body
    success &= check_result("GET /records (List/Persistence)", has_record, f"Status: {status}, Body: {body}")

    # GET /counter (Redis Atomic Increment)
    status1, _, body1 = make_request_with_retry(f"{BASE_URL}/counter")
    status2, _, body2 = make_request_with_retry(f"{BASE_URL}/counter")
    # Verify counter increments properly
    try:
        val1 = json.loads(body1).get("counter", 0)
        val2 = json.loads(body2).get("counter", 0)
        counter_ok = (status1 == 200 and status2 == 200 and val2 == val1 + 1)
    except Exception:
        counter_ok = False

    success &= check_result("GET /counter (Redis Atomic Increment)", counter_ok, f"Responses: {body1} -> {body2}")

    return success

def test_network_isolation():
    print("\n--- 3. Testing Network Isolation ---")
    success = True
    # 1. Internal Services ARE NOT exposed to the host   
    restricted_ports = {
        "PostgreSQL (Port 5432)": 5432,
        "Redis (Port 6379)": 6379,
    }

    for name, port in restricted_ports.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex(("localhost", port))
            s.close()
            # result != 0 means connection refused (Isolated / Safe)
            is_isolated = (result != 0)
        except Exception:
            is_isolated = True

        success &= check_result(f"Host Isolation: {name} closed", is_isolated, f"Security risk! Internal service port {port} is exposed to the host.")

    return success

def test_multiple_backends():
    print("\n--- 4. Testing Multi-Backend Distribution ---")
    instances_seen = set()
    for _ in range(10):
        status, _, body = make_request_with_retry(f"{BASE_URL}/instance")
        if status == 200:
            try:
                data = json.loads(body)
                instances_seen.add(data.get("instance_id"))
            except Exception:
                pass
    
    # Expecting at least 2 different backend instances if scaled up
    has_multiple = len(instances_seen) >= 2
    return check_result("Multi-backend load balancing (Multiple instances detected)", has_speed := has_multiple, f"Seen instances: {instances_seen}")

def main():
    print("Starting Comprehensive Architecture Validation...\n")  

    # Give services a few seconds to stabilize if just started
    time.sleep(2)

    pass_endpoints = test_endpoints()
    pass_db_cache = test_database_and_cache()
    pass_isolation = test_network_isolation()
    pass_multiple_backends = test_multiple_backends()

    print("\n==============================")
    if pass_endpoints and pass_db_cache and pass_isolation and pass_multiple_backends:
        print("RESULT: ALL VALIDATIONS PASSED 🎉")
        sys.exit(0)
    else:
        print("RESULT: VALIDATION FAILED ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()


