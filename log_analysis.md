# Log analysis

Use all three supplied logs. Answer every question with commands/scripts and actual output.

1. What UTC interval is covered? How many valid, malformed and duplicate lines are in each file?
2. How many distinct client requests occurred? How did you deduplicate and avoid counting retries twice?
3. What are the final client status counts and error rate? State your denominator.
4. Which paths, time windows and backends account for the failures?
5. What are the median and p95 client latencies? State the percentile method and units.
6. Which requests retried upstream? How many succeeded after retrying?
7. Build an incident timeline using evidence from access, error AND application logs.
8. Show one correlated failed request and one successful request. Include IDs and timestamps.
9. Which errors appear to be proxy/connectivity issues versus dependency/application issues? What proves it?
10. What do the logs not prove? What would you check next in a running environment?

## Commands / scripts
## Results
## Timeline and correlated examples
## Conclusions and limits


## Commands / scripts
* scripts/log_analysis.py 

## Results
- Q1)
    ```
    === QUESTION 1: File Stats & UTC Intervals ===
    === logs/access.log ===
    UTC Interval          : 2026-08-20T11:00:00.015Z to 2026-08-20T11:29:57.578Z
    Valid lines (unique)  : 720
    Malformed             : 1
    Duplicates            : 5

    === logs/application.log ===
    UTC Interval          : 2026-08-20T11:00:00.015Z to 2026-08-20T11:29:57.578Z
    Valid lines (unique)  : 727
    Malformed             : 1
    Duplicates            : 2

    === logs/error.log ===
    UTC Interval          : 2026/08/20 11:05:02 to 2026/08/20 11:30:00
    Valid lines (unique)  : 68
    Malformed             : 0
  Duplicates            : 0
    ```
- Q2)
    ```
    === QUESTION 2: Distinct Client Requests ===
    Distinct client requests (unique request_ids): 720
    Requests with upstream retries: 19
    ```
    - How did you deduplicate and avoid counting retries twice?
      - Deduplication: Identical raw lines were tracked and skipped using a set.
      - Retries: NGINX logs retries in a single line using comma-separated upstreams. Counting unique request_id values ensures each transaction is counted exactly once without double-counting retries
- Q3)
    ```
    === QUESTION 3: Status Counts & Error Rate ===
    Status Counts: {404: 10, 200: 615, 502: 40, 503: 47, 504: 8}
    Denominator (Total valid access records): 720
    Error Rate (Status >= 400): 14.58%
    ```
- Q4)
    ```
    === QUESTION 4: Failure Breakdown ===
    Failed Paths: [('/records', 26), ('/counter', 26), ('/ready', 23), ('/missing', 10), ('/health', 10), ('/', 10)]
    Failed Upstreams/Backends: [('172.23.0.12:8080', 73), ('172.23.0.11:8080', 32)]
    Failure Time Windows:
    2026-08-20T11:06        : 9 errors
    2026-08-20T11:09        : 9 errors
    2026-08-20T11:05        : 8 errors
    2026-08-20T11:07        : 8 errors
    2026-08-20T11:08        : 8 errors
    2026-08-20T11:12        : 8 errors
    2026-08-20T11:13        : 8 errors
    2026-08-20T11:14        : 8 errors
    2026-08-20T11:15        : 8 errors
    2026-08-20T11:20        : 8 errors
    2026-08-20T11:21        : 8 errors
    2026-08-20T11:26        : 5 errors
    2026-08-20T11:25        : 4 errors
    2026-08-20T11:00        : 1 errors
    2026-08-20T11:03        : 1 errors
    2026-08-20T11:16        : 1 errors
    2026-08-20T11:19        : 1 errors
    2026-08-20T11:23        : 1 errors
    2026-08-20T11:29        : 1 errors
    ```
- Q5)
    ```
    === QUESTION 5: Client Latencies ===
    Median Latency: 0.054 seconds
    P95 Latency: 2.001 seconds
    ```

- Q6)
    ```
    === QUESTION 6: Upstream Retries and Recovery ===
    Total Requests that Retried : 19
    Succeeded After Retry       : 19
    Failed Permanently          : 0

    --- Retried Request IDs ---
    ID: lab-000124 | Path: /ready | Flow: 502, 200
    ID: lab-000130 | Path: /instance | Flow: 502, 200
    ID: lab-000136 | Path: /ready | Flow: 502, 200
    ID: lab-000142 | Path: /instance | Flow: 502, 200
    ID: lab-000148 | Path: /ready | Flow: 502, 200
    ID: lab-000154 | Path: /instance | Flow: 502, 200
    ID: lab-000160 | Path: /ready | Flow: 502, 200
    ID: lab-000166 | Path: /instance | Flow: 502, 200
    ID: lab-000172 | Path: /ready | Flow: 502, 200
    ID: lab-000178 | Path: /instance | Flow: 502, 200
    ID: lab-000184 | Path: /ready | Flow: 502, 200
    ID: lab-000190 | Path: /instance | Flow: 502, 200
    ID: lab-000196 | Path: /ready | Flow: 502, 200
    ID: lab-000202 | Path: /instance | Flow: 502, 200
    ID: lab-000208 | Path: /ready | Flow: 502, 200
    ID: lab-000214 | Path: /instance | Flow: 502, 200
    ID: lab-000220 | Path: /ready | Flow: 502, 200
    ID: lab-000226 | Path: /instance | Flow: 502, 200
    ID: lab-000232 | Path: /ready | Flow: 502, 200

    --- Retries Grouped by Path ---
    /ready          : 10 retries
    /instance       : 9 retries
    ```
- Q7)
    ```
    === QUESTION 7: Unified Incident Timeline ===
    Total Incident Timeline Events Recorded: 302

    First 15 Incidents: 
    TIMESTAMP                 | SOURCE       | REQUEST_ID   | DETAILS
    -----------------------------------------------------------------------------------------------
    2026-08-20T11:05:02.000Z  | NGINX_ERROR  | lab-000122   | [ERROR] 31#31: *122 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000122, request: "GET /health HTTP/1.1", upstream: "http://172.23.0.12:8080/health"
    2026-08-20T11:05:02.503Z  | ACCESS       | lab-000122   | [GET] /health | Status: 502 | Upstream Status: 502 | Latency: 0.003s
    2026-08-20T11:05:07.000Z  | NGINX_ERROR  | lab-000124   | [ERROR] 31#31: *124 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000124, request: "GET /ready HTTP/1.1", upstream: "http://172.23.0.12:8080/ready"
    2026-08-20T11:05:07.620Z  | APPLICATION  | lab-000124   | [INFO] [GET] /ready | Status: 200 | Duration: 120.0ms | Event: http_request
    2026-08-20T11:05:07.620Z  | ACCESS       | lab-000124   | [GET] /ready | Status: 200 | Upstream Status: 502, 200 | Latency: 0.12s
    2026-08-20T11:05:12.000Z  | NGINX_ERROR  | lab-000126   | [ERROR] 31#31: *126 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000126, request: "GET /records HTTP/1.1", upstream: "http://172.23.0.12:8080/records"
    2026-08-20T11:05:12.503Z  | ACCESS       | lab-000126   | [GET] /records | Status: 502 | Upstream Status: 502 | Latency: 0.003s
    2026-08-20T11:05:17.000Z  | NGINX_ERROR  | lab-000128   | [ERROR] 31#31: *128 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000128, request: "GET /counter HTTP/1.1", upstream: "http://172.23.0.12:8080/counter"
    2026-08-20T11:05:17.503Z  | ACCESS       | lab-000128   | [GET] /counter | Status: 502 | Upstream Status: 502 | Latency: 0.003s
    2026-08-20T11:05:22.000Z  | NGINX_ERROR  | lab-000130   | [ERROR] 31#31: *130 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000130, request: "GET /instance HTTP/1.1", upstream: "http://172.23.0.12:8080/instance"
    2026-08-20T11:05:22.620Z  | APPLICATION  | lab-000130   | [INFO] [GET] /instance | Status: 200 | Duration: 120.0ms | Event: http_request
    2026-08-20T11:05:22.620Z  | ACCESS       | lab-000130   | [GET] /instance | Status: 200 | Upstream Status: 502, 200 | Latency: 0.12s
    2026-08-20T11:05:27.000Z  | NGINX_ERROR  | lab-000132   | [ERROR] 31#31: *132 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000132, request: "GET / HTTP/1.1", upstream: "http://172.23.0.12:8080/"
    2026-08-20T11:05:27.503Z  | ACCESS       | lab-000132   | [GET] / | Status: 502 | Upstream Status: 502 | Latency: 0.003s
    2026-08-20T11:05:32.000Z  | NGINX_ERROR  | lab-000134   | [ERROR] 31#31: *134 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000134, request: "GET /health HTTP/1.1", upstream: "http://172.23.0.12:8080/health"
    ```
- Q8)
    ```
    === QUESTION 8: Correlated Request Examples (Full Trace) ===

    --- Successful Request Example (Request ID: lab-000002) ---
    [APPLICATION] Timestamp: 2026-08-20T11:00:02.532Z | [INFO] [GET] /health | Duration: 32.0ms | Event: http_request
    [ACCESS]      Timestamp: 2026-08-20T11:00:02.532Z | [GET] /health | Status: 200 | Upstream Status: 200 | Latency: 0.032s

    --- Failed Request Example (Request ID: lab-000122) ---
    [NGINX_ERROR] Timestamp: 2026-08-20T11:05:02.000Z | [ERROR] | Message: 31#31: *122 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000122, request: "GET /health HTTP/1.1", upstream: "http://172.23.0.12:8080/health"
    [ACCESS]      Timestamp: 2026-08-20T11:05:02.503Z | [GET] /health | Status: 502 | Upstream Status: 502 | Latency: 0.003s

- Q9)
  - Proxy/connectivity Issues ➡️ status codes: **502**
    - Proof: in `error.log` **connect() failed (111: Connection refused)** 
    - acess.log: {"timestamp":"2026-08-20T11:05:02.503Z",**"request_id":"lab-000122"**,"method":"GET","path":"/health",**"status":502**,"upstream":"172.23.0.12:8080","upstream_status":"502","request_time":0.003,"client":"192.0.2.24"}
    - **error.log**: 2026/08/20 11:05:02 [error] 31#31: *122 **connect() failed (111: Connection refused)** while connecting to upstream, **request_id=lab-000122**, request: "GET /health HTTP/1.1", upstream: "http://172.23.0.12:8080/health"
        
    
  - Dependency/application issues ➡️ status codes: **503, 504**
    - 503: 
        - Proof: in `application.log` **"event": "dependency_error", "dependency": "redis", "error_type": "TimeoutError"** 
            - acess.log: {"timestamp":"2026-08-20T11:12:09.525Z",**"request_id":"lab-000292"**,"method":"GET","path":"/ready",**"status":503,**"upstream":"172.23.0.12:8080","upstream_status":"503","request_time":2.025,"client":"192.0.2.24"}
            - **application.log**: 
            {"timestamp": "2026-08-20T11:12:09.524Z", "level": "ERROR", **"event": "dependency_error", "request_id": "lab-000292"**, "instance_id": "app-02", **"dependency": "redis", "error_type": "TimeoutError"**}
    - 504:
        - Proof: in `error.log` **upstream timed out**
        - acess.log: {"timestamp":"2026-08-20T11:25:14.501Z",**"request_id":"lab-000606"**,"method":"GET","path":"/records",**"status":504**,"upstream":"172.23.0.12:8080","upstream_status":"504","request_time":2.001,"client":"192.0.2.24"}
        - **error.log:** 2026/08/20 11:25:14 [error] 31#31: *606 **upstream timed out** (110: Operation timed out) while reading response header from upstream, **request_id=lab-000606**, request: "GET /records HTTP/1.1", upstream: "http://172.23.0.12:8080/records"
- Q10)
    - What the logs do not prove: 
        - Root cause of failures (e.g., TimeoutError Redis error was crashed or was overloaded).
        - System resource usage (CPU and memory usage, network bottlenecks)
    - What to check next:
        - Containers Health: Check if application containers crashed or restarted (docker ps, OOMKilled status).
        - Resource Metrics (CPU and memory usage)
        - Dependencies Status (Redis and Postgres metrics and logs)

## Timeline and correlated examples
- Successful Response logs
    - acess.log: {"timestamp":"2026-08-20T11:00:02.532Z",**"request_id":"lab-000002"**,"method":"GET","path":"/health","status":200,"upstream":"172.23.0.12:8080","upstream_status":"200","request_time":0.032,"client":"192.0.2.24"}
    - application.log {"timestamp": "2026-08-20T11:00:02.532Z", "level": "INFO", "event": "http_request", **"request_id": "lab-000002"**, "instance_id": "app-02", "method": "GET", "path": "/health", "status": 200, "duration_ms": 32.0}

- Bad Gatway 502 Error Without Retry
    ```
    TIMESTAMP                 | SOURCE       | REQUEST_ID   | DETAILS
    -----------------------------------------------------------------------------------------------
    2026-08-20T11:05:02.000Z  | NGINX_ERROR  | lab-000122   | [ERROR] 31#31: *122 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000122, request: "GET /health HTTP/1.1", upstream: "http://172.23.0.12:8080/health"
    2026-08-20T11:05:02.503Z  | ACCESS       | lab-000122   | [GET] /health | Status: 502 | Upstream Status: 502 | Latency: 0.003s
    ```
- Bad Gatway 502 Error With Successful Retry
     ```
    TIMESTAMP                 | SOURCE       | REQUEST_ID   | DETAILS
    -----------------------------------------------------------------------------------------------
    2026-08-20T11:05:07.000Z  | NGINX_ERROR  | lab-000124   | [ERROR] 31#31: *124 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000124, request: "GET /ready HTTP/1.1", upstream: "http://172.23.0.12:8080/ready"
    2026-08-20T11:05:07.620Z  | APPLICATION  | lab-000124   | [INFO] [GET] /ready | Status: 200 | Duration: 120.0ms | Event: http_request
    2026-08-20T11:05:07.620Z  | ACCESS       | lab-000124   | [GET] /ready | Status: 200 | Upstream Status: 502, 200 | Latency: 0.12s
    ``
- Service Unaviable 503
    ```
    TIMESTAMP                 | SOURCE       | REQUEST_ID   | DETAILS
    ----------------------------------------------------------------------------------------------- 
    2026-08-20T11:12:09.525Z  | ACCESS       | lab-000292   | [GET] /ready | Status: 503 | Upstream Status: 503 | Latency: 2.025s
    2026-08-20T11:12:12.024Z  | APPLICATION  | lab-000293   | [ERROR] Event: dependency_error | Dependency: redis | Error Type: TimeoutError
    ```
- Gateway Timeout
    ```
    TIMESTAMP                 | SOURCE       | REQUEST_ID   | DETAILS
    ----------------------------------------------------------------------------------------------- 
    2026-08-20T11:25:14.501Z  | ACCESS       | lab-000606   | [GET] /records | Status: 504 | Upstream Status: 504 | Latency: 2.001s
    2026-08-20T11:25:15.200Z  | APPLICATION  | lab-000606   | [INFO] [GET] /records | Status: 200 | Duration: 2700.0ms | Event: http_request
    ```

## Conclusions and Limits
### Summary of Incidents:
- Mixed results: 
    - Some requests succeeded (or recovered on retry, like status 200)
    - Others failed due to proxy connectivity (502) and dependency/timeout issues (503, 504)
- The failure time window distribution shows that errors were sustained across multiple minutes (peaking between 11:05 and 11:21), indicating a prolonged period of backend instability rather than a single isolated spike
### Limitations of Log Data:
- Unknown Root Cause: Logs show that a request failed (e.g., status 502), but not why the underlying server or container failed at that moment
- No Infrastructure Metrics: Logs lack real-time data on CPU, memory, or network resource limits