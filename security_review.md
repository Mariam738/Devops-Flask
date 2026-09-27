# Security and production-readiness review

Record at least 8 concrete risks or improvements relevant to your final solution.
This is a review requirement, not the number of hidden faults.

For each finding:
- Risk and evidence:
- Impact:
- Implemented fix / commit:
- Production follow-up:
- How to verify:

Cover secrets, ports, container user, image selection, networks, persistence/backup,
logging/monitoring and availability. Separate completed work from planned improvements.

## 1 Secrets Management
- **Risk and evidence:** Storing database passwords inside the docker compose or in plain text  (./config/app.env)
- **Impact:** Anyone with read access to the repository or server filesystem can view sensitive credentials
- **Implemented fix / commit:**
  - Moved environment variables to an external .env file excluded from version control via .gitignore
  - Used github action secrets
- **Production follow-up:** Migrate to a dedicated secrets manager (like Docker Secrets, AWS Secrets Manager, or HashiCorp Vault)
- **How to verify:** Check that .env files are absent from the git repository and inspect container environment variables securely

## 2 Network Segmentation
- **Risk and evidence:** Nginx having access to backend service
- **Impact:** 
- **Implemented fix / commit:**
  - Ensured nginx have access to frontend network only and 
  - Ensure only the app container bridging both (frontend, backend networks)
- **Production follow-up:** Implement explicit firewall rules or Docker network policies to restrict cross-container traffic further
- **How to verify:** spect networks using docker network inspect

## 3 Data Persistence and Backup
- **Risk and evidence:** Storing critical application data inside ephemeral container layers.
- **Impact:** 
All database records and cache data are permanently lost if the container is removed or recreated
- **Implemented fix / commit:**
ttached Docker named volumes (postgres-data, redis-data) and enabled Redis AOF persistence (--appendonly yes)
- **Production follow-up:** Implement automated daily database snapshots and off-site cloud backups
- **How to verify:** Run docker volume ls to verify named volumes exist, and restart containers to confirm data persists

## 4 Non-Root Container User
- **Risk and evidence:** Containers running processes as the default root user
- **Impact:** A remote code execution vulnerability could allow an attacker to gain full administrative control of the host container
- **Implemented fix / commit:** Created and switched to a dedicated non-root user (USER app with UID/GID 10001) in the application Dockerfile
- **Production follow-up:** Apply similar non-root restrictions to any custom companion service images if applicable
- **How to verify:** Run docker exec <app_container> whoami to ensure it returns app instead of root

## 5 Nginx Availability and Health Monitoring
- **Risk and evidence:** Running the Nginx reverse proxy without an automated health check, meaning orchestrators or load balancers cannot detect if Nginx stops responding
- **Impact:** Traffic could continue routing to a frozen or dead web server, causing complete service downtime for users
- **Implemented fix / commit:** Added a dedicated health check to Nginx
- **Production follow-up:** Integrate Nginx status metrics with an external monitoring system like Prometheus or Datadog
- **How to verify:** Run docker inspect --format='{{json .State.Health}}' nginx

## 6 Container Port Exposure
- **Risk and evidence:** Exposing database and redis ports directly to the host machine (e.g., `ports: ["127.0.0.1:15432:5432"]`), risking accidental binding to public interfaces if local network configurations change
- **Impact:** External network scanners or unauthorized users could find and exploit database ports if misconfigured.
- **Implemented fix / commit:** Bound database and redis strictly to the internal Docker bridge network (`backend`) without publishing host ports, or restricted bindings exclusively to localhost (`127.0.0.1`).
- **Production follow-up:** Ensure only the reverse proxy (Nginx) exposes public HTTP/HTTPS ports to the outside world.
- **How to verify:** Run `docker port <container_id>` or check `docker-compose.yml` to confirm database ports are safe.

## 7 Logging and Monitoring
- **Risk and evidence:** Relying purely on default container stdout logs without centralized tracking
- **Impact:** Hard to trace errors, debug production crashes, or audit security events across multiple containers
- **Implemented fix / commit:** Configured containers to stream logs cleanly to `stdout`/`stderr`, allowing quick inspection using `docker logs` combined with `grep`
- **Production follow-up:** Forward container logs to a centralized monitoring system (like Prometheus, Grafana Loki, or Datadog)
- **How to verify:** Run `docker logs <container_id> | grep "ERROR"` to confirm logs are captured and searchable

## 8 Resource Limits and Denial of Service (DoS)
- **Risk and evidence:** Running containers without explicit CPU and memory caps, allowing any single container to consume 100% of the host machine's resources
- **Impact:** A memory leak or a high traffic spike in one service (like the Python app or Postgres) could exhaust host resources, crashing all other services on the server
- **Implemented fix / commit:** Defined explicit CPU and memory caps for all containers in `docker-compose.yml` (e.g., App: 0.5 CPU / 512MB RAM, Redis: 0.25 CPU / 256MB RAM)
- **Production follow-up:** Monitor actual container resource utilization via  Prometheus to fine-tune limits based on real production loads
- **How to verify:** Run `docker stats` under load to confirm containers stay within their designated memory and CPU boundaries

## 9 Database Backup and Disaster Recovery Strategy
- **Risk and evidence:** Relying exclusively on local Docker volumes (postgres-data, redis-data) without an automated, tested off-site backup routine
- **Impact:** A host disk failure, ransomware attack, or accidental data corruption could permanently destroy production data despite local volume persistence
- **Implemented fix / commit:**   
  - created sripts (backup.sh and restore.sh) and tested them
- **Production follow-up:** Regularly run automated staging environment restoration drills to verify that backup integrity is sound
- **How to verify:** Run bash script in readme in 6. Backup & Restore Testing (PostgreSQL) 

## 10 Nginx Reverse Proxy Configuration and Availability
- **Risk and evidence:** Running Nginx wrong proxy configurations, which can lead to drop of requests 
- **Impact:** Drops between users and the Python application and no high availability
- **Implemented fix / commit:**   
  - ensured upstream servers are correctly configured in nginx.config
  -  changed max_fails to 1  and fail_timeout to 10s to ensure HA be
- **Production follow-up:** Set up basic HTTP error monitoring (like tracking 502/504 gateway errors) to catch unexpected app downtimes quickly
- **How to verify:** Run python failure_test.py
