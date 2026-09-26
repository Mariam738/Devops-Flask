# Technical decisions

Record at least 5 decisions. Include assumptions and limits.

## Decision
- Choice:
- Why:
- Alternative:
- Trade-off:
- Evidence / commit:
- Production improvement:

Cover your base image, health checks, networks, timeouts/retries, restart/resource settings,
storage and any other meaningful choices.

## Decision 1: Container Health Checks
- **Choice:** Python built-in urllib script querying GET /ready with 5s interval, 3s timeout, and 10s start period
- **Assumptions:** The /ready endpoint accurately evaluates PostgreSQL and Redis connectivity, responding with HTTP 200 when ready and 503 otherwise
- **Alternative:** Querying GET /health or installing curl
- **Trade-off:** Stricter dependency checks mean temporary backend degradation will mark the container unhealthy, causing restarts or load balancer drops
- **Limitations:** If PostgreSQL or Redis temporarily fails, the health check fails and triggers container restarts, which can worsen the outage by hammering the recovering databases with repeated boot sequences

## Decision 2: Alpine-based Images (Redis, PostgreSQL, Nginx)
- **Choice:** Use Alpine-based images (postgres:alpine, redis:alpine, nginx:alpine).
- **Assumptions:** Standard databases and web servers run smoothly and reliably on Alpine.
- **Alternative:** Using larger Debian-based images for everything.
- **Trade-off:** Much smaller download sizes and faster start times, but slightly different system libraries under the hood.
- **Limitations:** Alpine uses a different core system library (musl) than Debian, which can occasionally cause unexpected software compatibility issues.

## Decision 3: Network Segmentation and Isolation
- **Choice:** ent containers into isolated networks where Nginx is on frontend, databases (PostgreSQL, Redis) are on backend, and the App bridges both (frontend and backend)
- **Assumptions:** Network segregation provides a strict security boundary, preventing public or proxy access from directly reaching the internal databases.
- **Alternative:** Placing all services on a single shared Docker network
- **Trade-off:** High security and clear traffic boundaries in exchange for managing multiple network interfaces per container (complexity)
- **Limitations:** Containers attached to multiple networks can occasionally make network debugging or packet tracking slightly more complex.

## Decision 4: Data Persistence and Storage
- **Choice:** Use Docker named volumes (postgres-data, redis-data) for database storage, alongside Redis AOF persistence (--appendonly yes)
- **Assumptions: **Data must survive container restarts, updates, and accidental deletions without loss
- **Alternative:** Using temporary storage that deletes data when the container stops
- **Trade-off:** Data is safely saved, but you have to manage where and how those files are stored on your computer
- **Limitations:** Named volumes are tied to the Docker host machine, making multi-host volume replication or cloud storage migration more complex

## Decision 5: Resource Limits
- **Choice:** et explicit CPU and memory caps for all containers (App: 0.5 CPU / 512MB RAM; Postgres: 0.5 CPU / 512MB RAM; Redis: 0.25 CPU / 256MB RAM; Nginx: 0.25 CPU / 128MB RAM)
- **Assumptions:** These limits provide enough headroom for normal operations while matching the expected resource profile of each service
- **Alternative:** Allowing containers to consume unlimited host resources
- **Trade-off:** Stable system performance and fair resource sharing, but a risk of crashes if a service unexpectedly exceeds its cap
- **Limitations:** If traffic spikes beyond the allocated limits, containers will be throttled or killed rather than automatically scaling up