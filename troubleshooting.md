# Troubleshooting journal

Keep chronological entries. Copy this block for each meaningful investigation.

## Entry / date / time
- **Symptom:**
- **Hypothesis:**
- **Command or test:**
- **Actual output:**
- **Failed attempt and what changed your thinking:**
- **Root cause:**
- **Fix:**
- **Retest evidence:**
- **Related commit:**
- **Remaining uncertainty:**

Do not fabricate a failed attempt just to fill the template. Record actual attempts.

## Entry 1
- **Symptom:** Containers `app-01` and `app-02` marked as `(unhealthy)`
- **Hypothesis:** Health check URL or instance configuration is misconfigured.
- **Command or test:** `docker compose -p barq-assessment ps -a` and `docker compose -p barq-assessment logs app-01 app-02`
- **Actual output:**
  - `docker compose ps -a`: `app-01 Up (unhealthy)`, `app-02 Up (unhealthy)`
  - `docker compose logs`: `{"path": "/healthz", "status": 404, ...}`
- **Failed attempt and what changed your thinking:** Initially checked for port conflicts, but the 404 error proved the server was running—just probed at the wrong path.
- **Root cause:** 
    1) Health check probed `/healthz` instead of `/health`. 
    2) `app-02` had `INSTANCE_ID` hardcoded to `"app-01"`
- **Fix:** Updated health check path to `/health` and corrected `app-02` instance ID to `"app-02"` in `docker-compose.yml`
- **Retest evidence:** `docker compose ps` shows both apps as `Up (healthy)`, and container logs confirm `/health` requests are now returning HTTP 200.
- **Related commit:** Fix: resolve app health checks and duplicate instance IDs
- **Remaining uncertainty:** `/ready` endpoint and dependency connections pending full integration

## Entry 2
- **Symptom:**
    1) The `/ready` endpoint returned `503 Service Unavailable`
    2) Postgres/Redis data was lost upon container restart.
- **Hypothesis:**
    1) App connections fail due to mismatched configuration
    2) Data is ephemeral because persistence is disabled
- **Command or test:**
    1. Test container readiness across replicas (via internal Python/urllib execution):
    ```bash
    docker compose exec app-01 python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/ready', timeout=2).read())"
    docker compose exec app-02 python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/ready', timeout=2).read())"
    ```
    2. Test endpoints, persistence, and restart survival internally:
    ```bash
    docker compose exec app-01 python -c "
    import urllib.request, json
    base = 'http://127.0.0.1:8080'
    # Store record & check counter
    req = urllib.request.Request(f'{base}/records', data=json.dumps({'title':'Persistence proof'}).encode(), headers={'Content-Type':'application/json'})
    print('POST /records:', urllib.request.urlopen(req).read())
    print('GET /counter:', urllib.request.urlopen(f'{base}/counter').read())

    # Test 404 on unknown route
    try:
        urllib.request.urlopen(f'{base}/unknown-route')
    except urllib.error.HTTPError as e:
        print('Unknown route status code:', e.code)
        
    # Test 400 on invalid title (empty string)
    try:
        bad_req = urllib.request.Request(f'{base}/records', data=json.dumps({'title':''}).encode(), headers={'Content-Type':'application/json'})
        urllib.request.urlopen(bad_req)
    except urllib.error.HTTPError as e:
        print('Invalid title status code:', e.code)

    # Test 400 on invalid title (exceeds 200 character limit)
    try:
        long_req = urllib.request.Request(f'{base}/records', data=json.dumps({'title': 'a' * 201}).encode(), headers={'Content-Type':'application/json'})
        urllib.request.urlopen(long_req)
    except urllib.error.HTTPError as e:
        print('Exceeded limit title status code:', e.code)
    "
    
    # Full teardown and recreation to rigorously test volume persistence
    docker compose down
    docker compose up -d

    # Verify data survived the full container recreation
    docker compose exec app-01 python -c "
    import urllib.request
    base = 'http://127.0.0.1:8080'
    print('GET /records (after down/up):', urllib.request.urlopen(f'{base}/records').read())
    print('GET /counter (after down/up):', urllib.request.urlopen(f'{base}/counter').read())
    "
    ```
- **Actual output:** urllib.error.HTTPError: HTTP Error 503: SERVICE UNAVAILABLE (initially)
- **Failed attempt and what changed your thinking:** Relied on container health checks before realizing they only test process liveness, not actual application readiness or database queries.
- **Root cause:**
    1) `app.env` had incorrect database ports
    2) PostgreSQL was incorrectly routed to volatile RAM storage (`tmpfs`) with its persistent volume mapped to the wrong path
    3) Redis lacked both AOF persistence and a data volume mount
- **Fix:**
    1) Corrected `DATABASE_URL` (port `5432` and password) and `REDIS_URL` (port `6379`) in app.env.
    2) Removed `tmpfs` from Postgres and mounted `postgres-data` to `/var/lib/postgresql/data`
    3) Enabled Redis AOF persistence (`--appendonly "yes"`) with a mapped data volume (`redis_data:/data`)
- **Retest evidence:** 
    - `/ready` returned HTTP 200 OK across both `app-01` and `app-02` (internal) and via internal `urllib` execution.
  - `POST /records` successfully stored the record `{"title":"Persistence proof"}`
  - `GET /records` successfully retrieved the persisted record list even after running `docker compose down`/`up`
  - `GET /counter` successfully incremented and retained its value across restarts
  - Every response successfully included a request ID header/field.
  - Unknown routes correctly returned HTTP 404.
  - Invalid record titles (empty or >200 chars) correctly returned HTTP 400.
- **Related commit:** Fix: readiness checks and postgres and redis persistence`
- **Remaining uncertainty:**
    - None for backend storage
    - Pending NGINX routing configuration

## Entry 3
- **Symptom:**
    1) Accessing `http://localhost:8080/instance` in the browser resulted in "This page isn’t working" (localhost didn’t send any data.)
    2) NGINX container lacked health monitoring in Docker.
- **Hypothesis:**
    1) Port mismatch between the Docker host mapping and NGINX's internal listen configuration
    2) Missing NGINX container health check 
- **Command or test:**
    1) Browser check: Attempted to load `http://localhost:8080/instance`.
    2) Infrastructure check:
       ```bash
       docker compose ps
       ```
- **Actual output:**
    1) Browser connection error (`This page isn’t working`)
    2) Nginx container status showing `Up` without a health check indicator 
- **Failed attempt and what changed your thinking:** None
- **Root cause:**
    1) `docker-compose.yml` mapped host traffic to container port `81`, while `nginx.conf` was configured to listen internally on port `80`
    2) The NGINX service definition lacked a native Docker health check to verify proper startup
- **Fix:**
    1) Corrected the Docker port mapping in `docker-compose.yml` to target port `80` (`ports: ["127.0.0.1:${PUBLIC_PORT:-8080}:80"]`)
    2) Added an explicit Docker health check block (`test: ["CMD", "nginx", "-t"]`) to the NGINX service.
- **Retest evidence:**
    - This page isn't working error cleared, and traffic successfully reached NGINX, resulting in a **502 Bad Gateway** response (paving the way for Entry 4's upstream investigation).
    - `docker compose ps` successfully reported NGINX as **Up (healthy)**.
- **Related commit:** Fix: NGINX port mapping and add container health check
- **Remaining uncertainty:** NGINX is now reachable, but upstream communication with the backend application containers needs resolution
