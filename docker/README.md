

# docker usage

```
git clone https://github.com/mqu/gdpr-registry-app.git gdpr-registry
cd gdpr-registry/docker
mkdir -p data data/backup data/stamps/ ; touch data/db.sqlite3

docker-compose build
docker-compose up -d

# add an admin user
docker-compose exec app /app/gdpr.sh create-admin

# backup
docker-compose exec app /app/gdpr.sh backup

# restart
docker-compose down ; docker-compose up -d ; docker-compose logs -ft
```
