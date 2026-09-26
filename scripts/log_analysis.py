import json
import os
import re
from collections import Counter

# --- Setup Paths and Configurations ---
LOG_DIR = "logs"
log_files = {
    "access.log": "json",
    "application.log": "json",
    "error.log": "nginx_text"
}

# Regex pattern for NGINX error log timestamps (e.g., 2026/08/20 11:05:02)
nginx_pattern = re.compile(r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})')

# Global storage for analysis
file_stats = {}
valid_access_records = []
valid_application_records = []
valid_error_records = []


# ==========================================
# PASS 1: Parse all log files (Question 1)
# ==========================================
for filename, ftype in log_files.items():
    filepath = os.path.join(LOG_DIR, filename)
    if not os.path.exists(filepath):
        print(f"=== {filepath} ===")
        print("File not found.\n")
        continue
        
    valid_lines = 0
    malformed_lines = 0
    timestamps = []
    seen_lines = set()
    duplicates = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            raw_line = line.strip()
            if not raw_line:
                continue
            
            # Check for exact duplicate lines
            if raw_line in seen_lines:
                duplicates += 1
                # print(f"  Duplicate line  : {raw_line}")
                continue
            else:
                seen_lines.add(raw_line)
            
            # Parse based on file type
            if ftype == "json":
                try:
                    data = json.loads(raw_line)
                    valid_lines += 1
                    if 'timestamp' in data:
                        timestamps.append(data['timestamp'])

                    # Store valid access records for subsequent questions
                    if filename == "access.log":
                        valid_access_records.append(data)

                    if filename == "application.log":
                        valid_application_records.append(data)

                except json.JSONDecodeError:
                    malformed_lines += 1
                    # print(f"  Malformed line  : {raw_line}")
                    
            elif ftype == "nginx_text" and filename == "error.log":
                # Matches: Timestamp, Log Level (error/notice), and the rest of the message body
                match = re.match(r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)$', raw_line)
                
                if match:
                    valid_lines += 1
                    raw_ts, level, body = match.groups()
                    
                    # Normalize timestamp to ISO format for chronological sorting
                    iso_timestamp = raw_ts.replace("/", "-").replace(" ", "T", 1) + ".000Z"
                    timestamps.append(iso_timestamp)
                    
                    # Safely check if a request_id is embedded anywhere in the message body
                    req_id_match = re.search(r'request_id=([\w-]+)', body)
                    req_id = req_id_match.group(1) if req_id_match else "SYSTEM"
                    
                    valid_error_records.append({
                        "timestamp": iso_timestamp,
                        "level": level,
                        "message": body.strip(),
                        "request_id": req_id
                    })
                else:
                    malformed_lines += 1
                    # print(f"  Malformed line  : {raw_line}")



    timestamps.sort()
    file_stats[filename] = {
        "start_time": timestamps[0] if timestamps else "N/A",
        "end_time": timestamps[-1] if timestamps else "N/A",
        "valid": valid_lines,
        "malformed": malformed_lines,
        "duplicates": duplicates
    }

# ==========================================
# PRINT QUESTION 1 RESULTS
# ==========================================
print("=== QUESTION 1: File Stats & UTC Intervals ===")
for filename, stats in file_stats.items():
    print(f"=== {LOG_DIR}/{filename} ===")
    print(f"  UTC Interval          : {stats['start_time']} to {stats['end_time']}")
    print(f"  Valid lines (unique)  : {stats['valid']}")
    print(f"  Malformed             : {stats['malformed']}")
    print(f"  Duplicates            : {stats['duplicates']}\n")

# ==========================================
# QUESTION 2: Distinct Client Requests & Retries
# ==========================================
print("=== QUESTION 2: Distinct Client Requests ===")
unique_request_ids = set()
retried_requests_count = 0

for record in valid_access_records:
    req_id = record.get("request_id")
    if req_id:
        unique_request_ids.add(req_id)
    if "," in record.get("upstream", ""):
        retried_requests_count += 1

print(f"Distinct client requests (unique request_ids): {len(unique_request_ids)}")
print(f"Requests with upstream retries: {retried_requests_count}\n")

# ==========================================
# QUESTION 3: Final Client Status & Error Rate
# ==========================================
print("=== QUESTION 3: Status Counts & Error Rate ===")
status_counts = Counter()
total_requests_denom = len(valid_access_records)

for record in valid_access_records:
    status = record.get("status")
    if status:
        status_counts[status] += 1

error_statuses = sum(count for status, count in status_counts.items() if status >= 400)
error_rate = (error_statuses / total_requests_denom * 100) if total_requests_denom > 0 else 0

print(f"Status Counts: {dict(status_counts)}")
print(f"Denominator (Total valid access records): {total_requests_denom}")
print(f"Error Rate (Status >= 400): {error_rate:.2f}%\n")

# ==========================================
# QUESTION 4: Paths, Time Windows, and Backends for Failures
# ==========================================
print("\n=== QUESTION 4: Failure Breakdown ===")
failed_paths = Counter()
failed_time_windows = Counter()
failed_upstreams = Counter()

for record in valid_access_records:
    if record.get("status", 0) >= 400:
        # 1. Path breakdown
        failed_paths[record.get("path")] += 1
        
        # 2. Backend (upstream) breakdown
        failed_upstreams[record.get("upstream")] += 1
        
        # 3. Time window breakdown (grouping by minute: YYYY-MM-DDTHH:MM)
        ts = record.get("timestamp", "")
        if len(ts) >= 16:
            minute_window = ts[:16] 
            failed_time_windows[minute_window] += 1

print("Failed Paths:", failed_paths.most_common())
print("Failed Upstreams/Backends:", failed_upstreams.most_common())
print("Failure Time Windows:")
for window, count in sorted(failed_time_windows.items()):
    print(f"  {window}        : {count} errors")

# ==========================================
# QUESTION 5: Median and p95 Client Latencies
# ==========================================
print("\n=== QUESTION 5: Client Latencies ===")
latencies = [r.get("request_time") for r in valid_access_records if isinstance(r.get("request_time"), (int, float))]
latencies.sort()

if latencies:
    n = len(latencies)
    median = latencies[n // 2]
    p95 = latencies[int(n * 0.95)]
    print(f"Median Latency: {median} seconds")
    print(f"P95 Latency: {p95} seconds")
else:
    print("No latency data found.")

# ==========================================
# QUESTION 6: Upstream Retries and Recovery
# ==========================================
print("\n=== QUESTION 6: Upstream Retries and Recovery ===")

retried_requests = []
succeeded_after_retry = 0
retry_paths = Counter()

for record in valid_access_records:
    upstream_status_str = str(record.get("upstream_status", ""))
    
    # A comma indicates a retry occurred (e.g., "502, 200")
    if "," in upstream_status_str:
        req_id = record.get("request_id")
        path = record.get("path")
        
        # Split and clean the upstream statuses to check the final retry attempt
        statuses = [s.strip() for s in upstream_status_str.split(",")]
        try:
            final_upstream_code = int(statuses[-1])
        except ValueError:
            # Fallback to the main request status if parsing fails
            final_upstream_code = record.get("status", 500)
        
        retried_requests.append({
            "request_id": req_id,
            "path": path,
            "upstream_status": upstream_status_str,
            "final_upstream_code": final_upstream_code
        })
        
        retry_paths[path] += 1
        
        # Check if the final retry attempt succeeded (< 400)
        if final_upstream_code < 400:
            succeeded_after_retry += 1

total_retries = len(retried_requests)
failed_permanently = total_retries - succeeded_after_retry

print(f"Total Requests that Retried : {total_retries}")
print(f"Succeeded After Retry       : {succeeded_after_retry}")
print(f"Failed Permanently          : {failed_permanently}")

print("\n--- Retried Request IDs ---")
for item in retried_requests:  
    print(f"  ID: {item['request_id']} | Path: {item['path']} | Flow: {item['upstream_status']}")

print("\n--- Retries Grouped by Path ---")
for path, count in retry_paths.most_common():
    print(f"  {path:<15} : {count} retries")


# ==========================================
# QUESTION 7: Incident Timeline Reconstruction
# ==========================================
print("\n=== QUESTION 7: Unified Incident Timeline ===")

master_timeline = []

# 1. Add Access Log events (focusing on errors or retries for a clean timeline)
for r in valid_access_records:
    # Optional: Filter for failures or retries to keep timeline focused, or include all
    if r.get("status", 200) >= 500 or "," in str(r.get("upstream_status", "")):
        master_timeline.append({
            "timestamp": r.get("timestamp"),
            "source": "ACCESS",
            "summary": f"[{r.get('method')}] {r.get('path')} | Status: {r.get('status')} | Upstream Status: {r.get('upstream_status')} | Latency: {r.get('request_time')}s",
            "request_id": r.get("request_id")
        })

# 2. Add Error Log events (NGINX errors - filtering out routine notices)
for e in valid_error_records:
    level = e.get("level", "error").upper()
    
    # Skip routine notices/info to keep the timeline focused purely on incident events
    if level in ["NOTICE", "INFO"]:
        continue

    master_timeline.append({
        "timestamp": e.get("timestamp"),
        "source": "NGINX_ERROR",
        "summary": f"[{level}] {e.get('message')}",
        "request_id": e.get("request_id", "SYSTEM")
    })

# Extract request IDs from our access logs so we can correlate app logs
incident_request_ids = sorted(list({item["request_id"] for item in master_timeline if item["request_id"] != "SYSTEM"}))

# 3. Add Application Log events
for a in valid_application_records:
    level = a.get("level", "INFO")
    event_type = a.get("event", "unknown")
    req_id = a.get("request_id", "N/A")
    app_status = int(a.get("status", 200))
    duration = float(a.get("duration_ms", 0))

    # Filter conditions: errors, slow requests (>100ms), or tied to an incident request ID
    is_app_error = level == "ERROR" or app_status >= 500
    is_slow = duration > 100
    is_correlated = req_id in incident_request_ids

    if is_app_error or is_slow or is_correlated:
        # Format summary based on whether it's a dependency error or an HTTP request log
        if "dependency" in a:
            summary = f"[{level}] Event: {event_type} | Dependency: {a.get('dependency')} | Error Type: {a.get('error_type')}"
        else:
            method = a.get("method", "INFO")
            path = a.get("path", "N/A")
            summary = f"[{level}] [{method}] {path} | Status: {app_status} | Duration: {duration}ms | Event: {event_type}"

        master_timeline.append({
            "timestamp": a.get("timestamp"),
            "source": "APPLICATION",
            "summary": summary,
            "request_id": req_id
        })

# Sort primarily by timestamp, and secondarily by source priority:
# NGINX_ERROR (1) -> APPLICATION (2) -> ACCESS (3) to mirror the request lifecycle
master_timeline.sort(key=lambda x: (x["timestamp"], 1 if x["source"] == "NGINX_ERROR" else (2 if x["source"] == "APPLICATION" else 3)))
# # Print the chronological incident flow
print(f"Total Incident Timeline Events Recorded: {len(master_timeline)}\n")

print("First 15 Incidents: ")
print(f"{'TIMESTAMP':<25} | {'SOURCE':<12} | {'REQUEST_ID':<12} | {'DETAILS'}")
print("-" * 95)
for event in master_timeline[:15]:  # Print first 15 key events as a sample
    print(f"{event['timestamp']:<25} | {event['source']:<12} | {event['request_id']:<12} | {event['summary']}")


# ==========================================
# QUESTION 8: Correlated Request Examples
# ==========================================
print("\n=== QUESTION 8: Correlated Request Examples (Full Trace) ===")

def print_request_trace(target_req_id, label):
    print(f"\n--- {label} (Request ID: {target_req_id}) ---")
    found = False

    # Check Error Logs
    for e in valid_error_records:
        if e.get("request_id") == target_req_id:
            level = e.get("level", "error").upper()
            print(f"  [NGINX_ERROR] Timestamp: {e.get('timestamp')} | [{level}] | Message: {e.get('message')}")
            found = True

    # Check Application Logs
    for a in valid_application_records:
        if a.get("request_id") == target_req_id:
            if "dependency" in a:
                    print(f"  [APPLICATION] Timestamp: {a.get('timestamp')} | [{a.get('level')}] | Event: {a.get('event')} | Dependency: {a.get('dependency')} | Error Type: {a.get('error_type')}")
            else:
                print(f"  [APPLICATION] Timestamp: {a.get('timestamp')} | [{a.get('level')}] [{a.get('method')}] {a.get('path')} | Duration: {a.get('duration_ms')}ms | Event: {a.get('event')}")

            found = True

    # Check Access Logs
    for r in valid_access_records:
        if r.get("request_id") == target_req_id:
            print(f"  [ACCESS]      Timestamp: {r.get('timestamp')} | [{r.get('method')}] {r.get('path')} | Status: {r.get('status')} | Upstream Status: {r.get('upstream_status')} | Latency: {r.get('request_time')}s")
            found = True
        
            
    if not found:
        print(f"  No logs found for {target_req_id}")

# Automatically pick one successful ID and one failed ID from your parsed data
success_id = next((r.get("request_id") for r in valid_access_records if r.get("status") == 200), None)
# Try to find a 5xx server error first; if none exist, fall back to any error status >= 400
failed_id = next((r.get("request_id") for r in valid_access_records if r.get("status", 200) >= 500 or "," in str(r.get("upstream_status", ""))) , None)
if not failed_id:
    failed_id = next((r.get("request_id") for r in valid_access_records if r.get("status", 200) >= 400), None)

if success_id:
    print_request_trace(success_id, "Successful Request Example")

if failed_id:
    print_request_trace(failed_id, "Failed Request Example")



