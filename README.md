# Journey of application deployment on GCP

## Test

```bash
curl http://localhost:8000
curl http://localhost:8001/chain
```

## 01 Coding

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py

deactivate
```

## 02 Docker

```bash
docker build -t python-fastapi .
docker run -d -p 8000:8000 --name fastapi python-fastapi

docker rm -f fastapi

docker run -d -p 8003:8000 --name app-c python-fastapi
docker run -d -p 8002:8000 --name app-b python-fastapi
docker run -d -p 8001:8000 --name app-a --link app-b:app-b --link app-c:app-c python-fastapi

docker rm -f app-a app-b app-c
```

## 03 Docker Compose

```bash
docker compose up --build

docker compose down
```

## 04 Cloud Run

```bash
gcloud run deploy --source . --region asia-southeast1 --port 8000 app-a --allow-unauthenticated --quiet
```

* [Cloud Storage](https://console.cloud.google.com/storage/browser)
* [Cloud Build](https://console.cloud.google.com/cloud-build/builds)
* [Artifact Registry](https://console.cloud.google.com/artifacts)
* [Cloud Run](https://console.cloud.google.com/run)
* [Cloud Run with Custom Domain](https://console.cloud.google.com/run/domains)

## 05 Update Code on Cloud Run

```bash
gcloud run deploy --source . --region asia-southeast1 --port 8000 app-a --allow-unauthenticated
```

## 06 Cloud Code on VSCode

* Open Duet AI
  * `explain this code to me`
* Edit `main.py` and put the following comment
  * `# Function to plus number by get endpoint /plus/i/j to plus i and j number together`

## 07 Unit Test

* Open Duet AI
  * `Please write unittest with pytest on test_main.py file`
    * Fix by put `from fastapi.testclient import TestClient` and use `TestClient(app)` on response accordingly

```bash
source ../01/.venv/bin/activate
pip install -r requirements-dev.txt
pytest
# Remove failed test

deactivate
```

## 08 Deploy from source code

```bash
gcloud source repos create python-fastapi

# Go to SET UP CONTINUOUS DEPLOYMENT in Cloud Run

# Change Code to v3
git remote add google ssh://[YOUR EMAIL]@source.developers.google.com:2022/p/{YOUR GCP PROJECT}/r/python-fastapi
git push --all google
```

* [Cloud Source Repositories](https://source.cloud.google.com)

## 09 CI/CD with Cloud Build

* [Cloud Build Repositories 2ND GEN](https://console.cloud.google.com/cloud-build/repositories/2nd-gen)
* [Cloud Build Trigger](https://console.cloud.google.com/cloud-build/triggers)
* Change to `v4` and git push

## 10 Dev and Production

```bash
gcloud deploy apply --file clouddeploy.yaml --region asia-southeast1
# Edit Cloud Build trigger from 10 directory 
# Change to v5

gcloud beta run domain-mappings --region asia-southeast1 create \
  --service=app-a-dev --domain=app-a.dev.demo.opsta.dev
gcloud beta run domain-mappings --region asia-southeast1 create \
  --service=app-b-dev --domain=app-b.dev.demo.opsta.dev
gcloud beta run domain-mappings --region asia-southeast1 create \
  --service=app-c-dev --domain=app-c.dev.demo.opsta.dev
gcloud beta run domain-mappings --region asia-southeast1 create \
  --service=app-a-prd --domain=app-a.demo.opsta.dev
gcloud beta run domain-mappings --region asia-southeast1 create \
  --service=app-b-prd --domain=app-b.demo.opsta.dev
gcloud beta run domain-mappings --region asia-southeast1 create \
  --service=app-c-prd --domain=app-c.demo.opsta.dev

# gcloud deploy releases create fastapi-release-$(date +"%Y%m%d%H%M") \
#   --delivery-pipeline fastapi --skaffold-file skaffold.yaml --region asia-southeast1 \
#   --images 'fastapi=asia-southeast1-docker.pkg.dev/{YOUR GCP PROJECT}/devfest/fastapi@sha256:87ded8770178d25b286ef74f332fb2574300ab83a97bf672940bbede3dae6de1'
```

## 11 Observability

* [Logs Explorer](https://console.cloud.google.com/logs/query)
* [SLO](https://console.cloud.google.com/monitoring/services)
* [Uptime](https://console.cloud.google.com/monitoring/uptime)
* [Trace](https://console.cloud.google.com/traces/list)

```bash
k6 run k6-load-testing.js
```

## Security

* [Docker Image Scan](https://console.cloud.google.com/artifacts/docker/{YOUR GCP PROJECT}/asia-southeast1/devfest/fastapi/)
