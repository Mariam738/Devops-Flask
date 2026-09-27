# Diagram notes

Create architecture.png or architecture.pdf at the repository root.
Show the final three-instance system on port 8090.

Label client, NGINX, Flask instances, PostgreSQL, Redis, ports, frontend/backend networks,
storage, request flow and health/readiness relationships. Explain remaining single points of failure.
This note is not a replacement for the required diagram.

## Architecure
<!-- <img src="architectrure.svg" alt="Architecture"> -->

[![](https://mermaid.ink/img/pako:eNqdVGtvmzAU_SuWpVaJFBIwjwKaKnWN1E3aI0unfRjkg0M8ggo2MqZLl-a_75pHk0ZZW80fAPuee8651zZbnIgVwyFOJS3X6Ps0ljFHMM7O0HWeMa7QOZpJsXnoA-1q1AUn6CNXTHKmFsgwLh9nQirkm74Z-uYj-pJmfBM1TzRn90xWrCV7t5STy19SQC5fIcj-LeTdopc48PCB0VytddKSVUhwdJXn6BryaMaBrkdOKSsEHwymIrljsps2Il9lsmaVklQJORwiYwwmD0k7k8-JTsGuytJ6E4q8jprdvI6Zs1VWnegIKORZQlUGaXNRq4ynfbRttN4GHWBoQsFz6zyCBzKt530_R0sK_drvQLV4iYq05bVU5M1UB97fdxjYQM4SXcJThdpko9eeJ5qj5ii5jk10v6LBTFQqlez226dG-UhuuDggIi8QHbv6h65nXwTdHkSD5vVfqgc0J9pxC2eSpqxfqeplewu7dfRD5HXBnjL1mN2AiqEjVjQo25ZUxooquveiRyPZQ0k0kHp-hINC8AgufrbCoZI1G-GCyYLqKd5qSIzVmhUsxiF8AkO9MRKRCxnjmO8gtaT8pxBFny1Fna77SV2CGJtmFEraI0CSyWtRc4VD1_UaChxu8QaHlmePHdc3bcu-IDYhnjPCDzg0zLFJHMsKSGBZJPA937G93Qj_aYTNcUBs07EdiLiWa1vBCEOl0L_P7W-t-bvt_gIvO4-u?type=png)](https://mermaid.live/edit#pako:eNqdVF1vmzAU_SuWpVZECgkYSAFNlbpG6ibtI0unPQzy4BCXoIKNjNnSpfnvu-ajSaOsreYHwL7nnnPutc0WJ2LFcIhTScs1-j6NZcwRjLMzdJ1njCt0jmZSbB76QLsadcEx-sgVk5ypBTLNy8eZkAr5lm-FvvWIvqQZ30TNE83ZLyYr1pK9W8rx5Z0UkMtXCLJ_C3m_6CUOPHxgNFdrnbRkFRIcXeU5uoY8mnGg65FTygrBDWMqknsmu2kj8lUma1YpSZWQgwEyR2DykLQz-ZzoFOyqLO03ocjrqNnN65g5W2XViY6AQp4lVGWQNhe1ynjaR9tG623QAYbGFDy3ziN4IMt-3vdztKTQr_0OVIuXqEhbXktF3kx14P19h4EN5CzRJTxVqE02eu15ojlqjpLnOkT3KzJmolKpZLffPjXKR3KDxQEReYHo2NU_dCfORdDtQWQ0r_9SPaA50Y5bOJM0Zf1KVS_bW9itox8irwv2lKnH7AZUTB2xI6NsW1KZK6ro3osejWQPJZEh9fwIB4XgIVz8bIVDJWs2xAWTBdVTvNWQGKs1K1iMQ_gEhnpjJiIXMsYx30FqSflPIYo-W4o6XfeTugQxNs0olLRHgCST16LmCoee5zUUONziDQ7tiTNyPd9ybOeCOIRM3CF-wKFpjSzi2nZAAtsmgT_xXWeyG-I_jbA1CohjuY4LEc_2HDsYYqgU-ve5_a0lgt9lKd79BVAXkIg)

## Readiness Order (Startup)
- Step 1: **postgres & redis** start (must report healthy)
- Step 2: **app-01 & app-02** start
- Step 3: **nginx** starts last

## Single Points of Failure (SPOF)
- **Nginx:** If it crashes, all external traffic stops
- **Postgres / Redis:** If either fails, the apps lose database access and caching/queues
- **Apps (app-01/app-02):** Not a SPOF individually (load-balanced), but failing both takes the app offline
- How would you fix them in production ❓
  - **Nginx:** Use a cloud load balancer or redundant instances with failover
  - **Postgres & Redis:** Use managed high-availability services or primary-replica replication with auto-failover
  - **Apps:** Scale to 3+ instances across multiple availability zones

## How Request Flows ❓
- **Client:** Sends request
- **Nginx:** Receives request and load-balances it
- **App Instances (app-01/app-02):** Process the request, querying Postgres for data and Redis for cache/session
- **Response:** Flows back through Nginx to the client

## Why these ports ❓
- Port 8080 or 8090 (Apps, Nginx): Commonly used as custom/alternative HTTP ports for Nginx or apps during testing
- Port 5432 (Postgres): The official IANA-assigned standard port for PostgreSQL
- Port 6379 (Redis): The official default port 
 
## Why these networks ❓
- Nginx (Frontend Network): Faces the public internet to handle client traffic safely and route it internally
- Apps (Frontend & Backend): Act as the bridge, they accept traffic from Nginx and talk to the internal databases
- DB & Redis (Backend Network): Isolated completely from the public internet for security, accessible only by the app containers