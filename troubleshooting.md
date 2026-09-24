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