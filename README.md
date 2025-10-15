# aws-two-tier-poc

A minimal Flask + Gunicorn web app with AWS-ready CI/CD using CodeBuild and CodeDeploy. Includes a CloudFormation template (`poc-infra.yaml`) to spin up an EC2-based environment.

## Prerequisites
- Python 3.9+
- AWS account and credentials configured (`aws configure`)
- AWS CLI v2

## Run Locally
```bash
cd /Users/vasudhanreddy/Desktop/my-web-app-poc
python3 -m venv .venv && source .venv/bin/activate
pip install -r app/requirements.txt

# Development server
export FLASK_APP=app/app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000

# Or production-like using Gunicorn
chmod +x app/start_app.sh
./app/start_app.sh
# Open http://localhost:8000
```

## Deploy with AWS (High-level)
1. Create infrastructure with CloudFormation using `poc-infra.yaml`.
2. Connect your repo to CodePipeline → CodeBuild (`deployment/buildspec.yml`) → CodeDeploy (`deployment/appspec.yml`).
3. Push to the main branch; the pipeline builds and deploys to the EC2 instance created by the stack.

See `DEPLOYMENT_GUIDE.md` for a step-by-step guide.

## Project Structure
```
/my-web-app-poc
├── .gitignore
├── poc-infra.yaml
├── DEPLOYMENT_GUIDE.md
├── app/
│   ├── app.py
│   ├── index.html
│   ├── requirements.txt
│   └── start_app.sh
├── deployment/
│   ├── buildspec.yml
│   └── appspec.yml
└── README.md
```

## Health Check
- HTTP: `GET /health` returns `200 OK` and `{ "status": "ok" }`.

## License
MIT (for POC use)
