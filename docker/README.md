

# run

```
git clone https://github.com/mqu/gdpr-registry-app.git gdpr-registry
cd gdpr-registry
git checkout -b docker
cd docker
mkdir -p data data/backup data/stamps/ ; touch data/db.sqlite3

docker-compose build
docker-compose up -d

```
