# Steps to test backup.sh and restore.sh
```
docker compose up -d
curl -H 'Content-Type: application/json' -d '{"title":"Backup Restore Proof"}' http://127.0.0.1:8080/records
./backup.sh
docker compose down -v
docker compose up -d
./restore.sh
curl http://127.0.0.1:8080/records # find Backup Restore Proof
```