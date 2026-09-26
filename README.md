<img src="assets/barq-logo.svg" alt="BARQ Systems" width="180">

## 📋 Prerequisites
- Docker & Docker Compose 
- Python 3 (for running test scripts).

## 🚀 1. Setup
- Create your local environment configuration file:
    ```bash
    mkdir -p config
    cat << EOF > config/app.env
    POSTGRES_USER=user
    POSTGRES_PASSWORD=change_me_to_a_secure_password
    POSTGRES_DB=db

    DATABASE_URL=postgresql://user:change_me_to_a_secure_password@postgres:5432/dn
    REDIS_URL=redis://redis:6379/0
    EOF
    ```
## 🏗️ 2. Build
```bash
docker compose build --no-cache
```
## 🟢 3. Start & Stop
- Start the stack (in the background):
    ```bash
    docker compose up -d
    ```
- Stop and clean containers:
    ```bash
    docker compose down
    ```
## 🧪 4. Test (Health Checks)
```bash
python validate.py
```
## 💥 5. Failure & Recovery Testing
```bash
python failure_test.py
```
## 💾 6. Backup & Restore Testing (PostgreSQL) 
```
docker compose up -d
curl -H 'Content-Type: application/json' -d '{"title":"Backup Restore Proof"}' http://127.0.0.1:8080/records
./backup.sh
docker compose down -v
docker compose up -d
./restore.sh
curl http://127.0.0.1:8080/records # find Backup Restore Proof
```
## 🧹 7. Cleanup
- ⚠️To completely clean up containers, networks, and volumes:
    ```Bash
    docker compose down -v --rmi all
    ```

## Architecure
<!-- <img src="architectrure.svg" alt="Architecture"> -->

[![](https://mermaid.ink/img/pako:eNqdVGtvmzAU_SuWpVaJFBIwjwKaKnWN1E3aI0unfRjkg0M8ggo2MqZLl-a_75pHk0ZZW80fAPuee8651zZbnIgVwyFOJS3X6Ps0ljFHMM7O0HWeMa7QOZpJsXnoA-1q1AUn6CNXTHKmFsgwLh9nQirkm74Z-uYj-pJmfBM1TzRn90xWrCV7t5STy19SQC5fIcj-LeTdopc48PCB0VytddKSVUhwdJXn6BryaMaBrkdOKSsEHwymIrljsps2Il9lsmaVklQJORwiYwwmD0k7k8-JTsGuytJ6E4q8jprdvI6Zs1VWnegIKORZQlUGaXNRq4ynfbRttN4GHWBoQsFz6zyCBzKt530_R0sK_drvQLV4iYq05bVU5M1UB97fdxjYQM4SXcJThdpko9eeJ5qj5ii5jk10v6LBTFQqlez226dG-UhuuDggIi8QHbv6h65nXwTdHkSD5vVfqgc0J9pxC2eSpqxfqeplewu7dfRD5HXBnjL1mN2AiqEjVjQo25ZUxooquveiRyPZQ0k0kHp-hINC8AgufrbCoZI1G-GCyYLqKd5qSIzVmhUsxiF8AkO9MRKRCxnjmO8gtaT8pxBFny1Fna77SV2CGJtmFEraI0CSyWtRc4VD1_UaChxu8QaHlmePHdc3bcu-IDYhnjPCDzg0zLFJHMsKSGBZJPA937G93Qj_aYTNcUBs07EdiLiWa1vBCEOl0L_P7W-t-bvt_gIvO4-u?type=png)](https://mermaid.live/edit#pako:eNqdVF1vmzAU_SuWpVZECgkYSAFNlbpG6ibtI0unPQzy4BCXoIKNjNnSpfnvu-ajSaOsreYHwL7nnnPutc0WJ2LFcIhTScs1-j6NZcwRjLMzdJ1njCt0jmZSbB76QLsadcEx-sgVk5ypBTLNy8eZkAr5lm-FvvWIvqQZ30TNE83ZLyYr1pK9W8rx5Z0UkMtXCLJ_C3m_6CUOPHxgNFdrnbRkFRIcXeU5uoY8mnGg65FTygrBDWMqknsmu2kj8lUma1YpSZWQgwEyR2DykLQz-ZzoFOyqLO03ocjrqNnN65g5W2XViY6AQp4lVGWQNhe1ynjaR9tG623QAYbGFDy3ziN4IMt-3vdztKTQr_0OVIuXqEhbXktF3kx14P19h4EN5CzRJTxVqE02eu15ojlqjpLnOkT3KzJmolKpZLffPjXKR3KDxQEReYHo2NU_dCfORdDtQWQ0r_9SPaA50Y5bOJM0Zf1KVS_bW9itox8irwv2lKnH7AZUTB2xI6NsW1KZK6ro3osejWQPJZEh9fwIB4XgIVz8bIVDJWs2xAWTBdVTvNWQGKs1K1iMQ_gEhnpjJiIXMsYx30FqSflPIYo-W4o6XfeTugQxNs0olLRHgCST16LmCoee5zUUONziDQ7tiTNyPd9ybOeCOIRM3CF-wKFpjSzi2nZAAtsmgT_xXWeyG-I_jbA1CohjuY4LEc_2HDsYYqgU-ve5_a0lgt9lKd79BVAXkIg)

---
# DevOps Internship Task - Starter v2

**Due date:** ____________________

**Time window:** 4 calendar days from the invitation email date/time.

Read [the task](assessment/TASK.md), then [the API contract](assessment/APPLICATION.md).
Everyone receives this same release. The environment is intentionally broken.
Hidden issue types and count are not disclosed. Investigate this project; do not replace it.

## Included

- Flask API, PostgreSQL, Redis, Docker and NGINX starter files.
- Three historical logs, a question template and documentation templates.
- App-only tests and a recorded challenge script.
- Unimplemented validation, failure-test and backup/restore placeholders.

Use synthetic lab accounts/data only. Supplied values are for this disposable exercise,
never for real services. Keep the lab on your local machine; do not expose it publicly.

## Before you start

- Linux or WSL2, Python 3.12, Git and Docker with Compose.
- Docker Desktop must use Linux containers. Run shell scripts in Linux/WSL.
- Suggested capacity: 2 CPU cores, 4 GB free RAM and 3 GB free disk, plus Docker overhead.
- Internet for first downloads and GitHub. No cloud account or paid registry required.
- Use a machine where container names app-01, app-02, nginx, postgres and redis are unused.
  Do not delete someone else's containers to free those names.
- Intended public port: 8080 before the video, 8090 after the live change.
  If either is occupied, ask the organizer for a documented workstation exception.

## Start

Clone the supplied Git bundle/repository. Keep both release commits and the v2 baseline tag.
Set your own Git name/email before making changes.

From the repository root:

```bash
git status
git log -2 --oneline
cp .env.example .env
docker version
docker compose version
docker compose -p barq-assessment up --build -d
docker compose -p barq-assessment ps -a
docker compose -p barq-assessment logs --no-color
```

The initial environment is not expected to pass. Record what actually happens.
The intended URL is http://127.0.0.1:8080; do not assume the starter configuration is correct.

App-only checks use fake dependencies, not real SQL/Redis or Docker networking:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Your work

- Complete [assessment/TASK.md](assessment/TASK.md).
- Implement validate.py, failure_test.py, backup.sh and restore.sh, or documented equivalents.
  Placeholders deliberately exit 2; they are unfinished deliverables, not validation evidence.
- Create .github/workflows/ci.yml yourself.
- Complete the root report templates and docs/EVIDENCE_INDEX.md.
- Add architecture.png or architecture.pdf.
- Replace this README with copyable setup/build/run/test/failure/backup/restore/cleanup commands.
- Commit as you work. Do not commit real secrets, backups, virtual environments or challenge state.

## Recorded challenge

Use the supplied video_challenge.sh unchanged. Read its code if needed; do not run it early.
After repairing the environment, run it once, for the first time in the video working copy,
during the continuous 12-18 minute recording. The script requires healthy services, both
initial instances and the target network layout. Preflight failures make no runtime changes.

```bash
./video_challenge.sh
```

If you deliberately changed the project name, pass --project YOUR_PROJECT.
An organizer-approved alternate local URL can be passed with --url http://127.0.0.1:PORT.
The script touches only matching Compose-owned lab containers/networks.
Keep the receipt in .assessment/challenge.json for the evidence index. Do not delete the
one-run marker to retry. A local marker is not tamper-proof; ownership is judged from evidence.
Do not use docker compose down to reset the runtime challenge.

## Stop safely

Outside the recorded challenge, docker compose -p barq-assessment down stops this lab.
Do not use --volumes during persistence tests. Avoid global Docker prune/cleanup commands.
Back up anything you need before removing containers; investigate whether data actually persists.
