# Deployment Guide — GPT FastAPI Application
### AWS ECS Fargate + S3 + CloudFront + GitHub Actions + Auth0

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [How a Request Flows — End to End](#2-how-a-request-flows--end-to-end)
3. [Prerequisites](#3-prerequisites)
4. [Step 1 — AWS IAM User Setup](#4-step-1--aws-iam-user-setup)
5. [Step 2 — Create ECR Repository](#5-step-2--create-ecr-repository)
6. [Step 3 — Fix ECS Service-Linked Role](#6-step-3--fix-ecs-service-linked-role)
7. [Step 4 — Create ECS Cluster](#7-step-4--create-ecs-cluster)
8. [Step 5 — Create ECS Task Definition](#8-step-5--create-ecs-task-definition)
9. [Step 6 — Create ALB + Target Group](#9-step-6--create-alb--target-group)
10. [Step 7 — Create ECS Service](#10-step-7--create-ecs-service)
11. [Step 8 — Fix Security Groups](#11-step-8--fix-security-groups)
12. [Step 9 — Create S3 Bucket for Frontend](#12-step-9--create-s3-bucket-for-frontend)
13. [Step 10 — Create CloudFront Distribution](#13-step-10--create-cloudfront-distribution)
14. [Step 11 — Add ALB as Second CloudFront Origin (API Proxy)](#14-step-11--add-alb-as-second-cloudfront-origin-api-proxy)
15. [Step 12 — Configure Auth0](#15-step-12--configure-auth0)
16. [Step 13 — Add GitHub Secrets](#16-step-13--add-github-secrets)
17. [Step 14 — Push Code and Trigger CI/CD](#17-step-14--push-code-and-trigger-cicd)
18. [Errors We Hit and How We Fixed Them](#18-errors-we-hit-and-how-we-fixed-them)
19. [Cost Overview](#19-cost-overview)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER'S BROWSER                             │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTPS
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CLOUDFRONT (CDN)                                │
│         https://d1v2k6g99m4u7p.cloudfront.net                      │
│                                                                     │
│   Path /*        → S3 bucket (React static files)                  │
│   Path /api/*    → ALB (FastAPI backend)                            │
└──────────────┬───────────────────────────┬──────────────────────────┘
               │ serves HTML/JS/CSS         │ proxies API calls (HTTP)
               ▼                            ▼
┌──────────────────────┐     ┌──────────────────────────────────────┐
│   S3 BUCKET          │     │   APPLICATION LOAD BALANCER (ALB)    │
│  (React frontend)    │     │   port 80                            │
│  index.html          │     └──────────────────┬───────────────────┘
│  assets/             │                        │ port 8000
└──────────────────────┘                        ▼
                              ┌──────────────────────────────────────┐
                              │   ECS FARGATE (FastAPI container)    │
                              │   port 8000                          │
                              │   uvicorn app.main:app               │
                              └──────────────────┬───────────────────┘
                                                 │
                                                 ▼
                              ┌──────────────────────────────────────┐
                              │   OPENAI API                         │
                              │   (external, called by FastAPI)      │
                              └──────────────────────────────────────┘
```

**Key URLs:**

| Service | URL |
|---|---|
| Frontend (React) | `https://d1v2k6g99m4u7p.cloudfront.net` |
| Backend API | `https://d1v2k6g99m4u7p.cloudfront.net/api/v1` |
| ALB (internal) | `http://gpt-app-backend-1357233706.eu-north-1.elb.amazonaws.com` |
| Health check | `https://d1v2k6g99m4u7p.cloudfront.net/api/v1/health` |

---

## 2. How a Request Flows — End to End

### Step A — User Opens the App

```
1. User opens: https://d1v2k6g99m4u7p.cloudfront.net

2. CloudFront receives the request
   → Path is "/" → matches default behaviour → fetches from S3

3. S3 returns index.html
   → CloudFront caches it at the nearest edge location

4. Browser downloads index.html + assets/index.js (React bundle)

5. React app boots up in the browser
   → Auth0Provider initialises
   → useAuth0() checks if user has a valid session
```

### Step B — User Logs In (Auth0 SSO)

```
6. User clicks "Sign in with Auth0"

7. loginWithRedirect() called
   → Browser redirects to:
      https://dev-5yxjxh8ys4lrkckf.us.auth0.com/authorize
      ?client_id=KVdynvgjer0Octrb8zD9jxb0uZUnxk1F
      &redirect_uri=https://d1v2k6g99m4u7p.cloudfront.net/callback
      &audience=http://gpt-app-backend-1357233706...
      &response_type=code

8. User enters username + password on Auth0's page

9. Auth0 verifies credentials → redirects back to:
   https://d1v2k6g99m4u7p.cloudfront.net/callback?code=TEMP_CODE

10. @auth0/auth0-react exchanges code → gets JWT token (background HTTP call)
    → isAuthenticated becomes true
    → GptChat component renders
```

### Step C — User Sends a Chat Message

```
11. User types a message and clicks Send

12. GptChat.jsx calls getAccessTokenSilently()
    → Returns the cached JWT token (or silently refreshes if expired)
    → Token looks like: eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ...

13. api.js sends:
    POST https://d1v2k6g99m4u7p.cloudfront.net/api/v1/chat/completions
    Headers:
      Content-Type: application/json
      Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...
    Body:
      { "messages": [...], "model": "gpt-3.5-turbo", "stream": true }

14. CloudFront receives the request
    → Path is "/api/v1/chat/completions" → matches /api/* behaviour
    → Forwards to ALB over HTTP (CloudFront handles HTTPS externally)

15. ALB receives the request on port 80
    → Forwards to the ECS Fargate task on port 8000

16. FastAPI receives the request:
    a. HTTPBearer extracts the JWT from the Authorization header
    b. Depends(verify_token) runs:
       - Fetches Auth0 public keys from JWKS endpoint (cached in memory)
       - Reads token header to find which key was used (kid)
       - Matches kid to public key
       - jwt.decode() verifies: signature + audience + issuer + expiry
       - Returns decoded payload: { "sub": "user-id", "email": "..." }
    c. chat_completions() function runs with the verified user payload
    d. FastAPI calls OpenAI API with the messages
    e. OpenAI streams back the response chunk by chunk

17. FastAPI streams the response back as Server-Sent Events (SSE):
    data: {"delta": "Hello"}
    data: {"delta": " world"}
    data: [DONE]

18. CloudFront passes the stream through to the browser
    (compression disabled → stream flows without buffering)

19. React reads the SSE stream chunk by chunk
    → Updates the UI in real time as each word arrives

20. User sees the response being typed out word by word
```

---

## 3. Prerequisites

Before starting, you need:

- **AWS Account** with billing alerts set up
- **GitHub account** with the code in a repository
- **Auth0 account** (free tier is fine)
- **AWS CLI** installed and configured on your machine:
  ```bash
  brew install awscli
  aws configure   # enter your IAM user credentials
  ```
- **Docker** installed on your machine (to test the image locally)

---

## 4. Step 1 — AWS IAM User Setup

Create a dedicated IAM user for GitHub Actions. Never use your root account for CI/CD.

1. **AWS Console → IAM → Users → Create user**
   - Username: `github-actions-deployer`
   - Access type: **Programmatic access only** (no console login needed)

2. **Attach these policies:**
   - `AmazonEC2ContainerRegistryPowerUser` — push/pull ECR images
   - `AmazonECS_FullAccess` — manage ECS clusters, services, tasks
   - `AmazonS3FullAccess` — upload frontend files
   - `CloudFrontFullAccess` — invalidate CloudFront cache

3. **Download the credentials CSV** — you get:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - These go into GitHub Secrets later

---

## 5. Step 2 — Create ECR Repository

ECR (Elastic Container Registry) is where your Docker images are stored.

```bash
aws ecr create-repository \
  --repository-name gpt-app-backend \
  --region eu-north-1
```

This gives you a repository URI like:
```
123456789012.dkr.ecr.eu-north-1.amazonaws.com/gpt-app-backend
```

---

## 6. Step 3 — Fix ECS Service-Linked Role

**You will get this error if you skip this step:**
```
Unable to assume the service linked role.
Please verify that the ECS service linked role exists.
```

This happens on fresh AWS accounts. ECS needs a special IAM role to manage resources on your behalf. Create it with one command:

```bash
aws iam create-service-linked-role --aws-service-name ecs.amazonaws.com
```

> If you get "Role already exists" — that's fine, it means the role was already created. Continue to the next step.

---

## 7. Step 4 — Create ECS Cluster

1. **AWS Console → ECS → Clusters → Create Cluster**
2. Cluster name: `gpt-app-cluster`
3. Infrastructure: **AWS Fargate** (serverless — no EC2 to manage)
4. Click **Create**

---

## 8. Step 5 — Create ECS Task Definition

The Task Definition is the blueprint for your container — what image to run, how much CPU/RAM, which port, which environment variables.

1. **AWS Console → ECS → Task Definitions → Create new task definition**
2. Task definition family name: `gpt-app-backend`
3. Launch type: **AWS Fargate**
4. CPU: `0.5 vCPU`, Memory: `1 GB`
5. Task role: create a new role or use `ecsTaskExecutionRole`
6. **Container settings:**
   - Container name: `gpt-app-backend`
   - Image URI: `123456789012.dkr.ecr.eu-north-1.amazonaws.com/gpt-app-backend:latest`
   - Port mapping: `8000` TCP
7. Click **Create**

> **Note:** Environment variables (OpenAI key, Auth0 settings) are injected by GitHub Actions at deploy time — not stored in the Task Definition.

---

## 9. Step 6 — Create ALB + Target Group

The Application Load Balancer sits in front of your ECS tasks and provides a stable public URL.

1. **AWS Console → EC2 → Load Balancers → Create Load Balancer**
2. Type: **Application Load Balancer**
3. Name: `gpt-app-backend`
4. Scheme: **Internet-facing**
5. IP address type: IPv4
6. VPC: select your default VPC
7. Availability Zones: select **all** available AZs
8. **Listeners:** Add port `80` (HTTP)
9. **Create a new Target Group:**
   - Type: IP addresses
   - Name: `gpt-app-backend-tg`
   - Protocol: HTTP, Port: **8000**
   - Health check path: `/api/v1/health`  ← very important, must match your FastAPI route
   - Health check success codes: `200`
10. Click **Create load balancer**

**Copy the ALB DNS name** — it looks like:
```
gpt-app-backend-1357233706.eu-north-1.elb.amazonaws.com
```
You will need this for Auth0 and GitHub Secrets.

---

## 10. Step 7 — Create ECS Service

The Service ensures your container keeps running. If it crashes, ECS automatically starts a new one.

1. **AWS Console → ECS → `gpt-app-cluster` → Services → Create**
2. Launch type: **Fargate**
3. Task Definition: `gpt-app-backend` (latest revision)
4. Service name: `gpt-app-backend-service`
5. Desired tasks: `1`
6. **Networking:**
   - VPC: default VPC
   - Subnets: select all public subnets
   - Security group: create new or select existing
   - Auto-assign public IP: **Enabled** (required for Fargate to pull from ECR)
7. **Load Balancing:**
   - Load balancer type: Application Load Balancer
   - Load balancer: `gpt-app-backend`
   - Container to load balance: `gpt-app-backend:8000`
   - Target group: `gpt-app-backend-tg`
8. Click **Create**

---

## 11. Step 8 — Fix Security Groups

This is a critical step that causes the "unhealthy" target group status if missed.

### ECS Task Security Group

The ECS task needs to accept traffic from the ALB on port 8000.

1. **AWS Console → EC2 → Security Groups**
2. Find the security group attached to your ECS tasks
3. **Inbound rules → Edit → Add rule:**
   ```
   Type:    Custom TCP
   Port:    8000
   Source:  <ALB Security Group ID>
   ```
   > Use the ALB's Security Group ID (sg-xxxx), not 0.0.0.0/0 for security

### ALB Security Group

The ALB needs to accept traffic from the internet on port 80.

1. Find the security group attached to the ALB
2. **Inbound rules → Edit → Add rule:**
   ```
   Type:    HTTP
   Port:    80
   Source:  0.0.0.0/0
   ```

---

## 12. Step 9 — Create S3 Bucket for Frontend

1. **AWS Console → S3 → Create bucket**
2. Bucket name: `gpt-app-frontend-myapp` (must be globally unique)
3. Region: `eu-north-1` (same region as everything else)
4. **Uncheck "Block all public access"** → confirm
5. Click **Create bucket**

### Enable Static Website Hosting

1. Click your bucket → **Properties** tab
2. Scroll to **Static website hosting** → Edit → **Enable**
3. Index document: `index.html`
4. Error document: `index.html` (required for React Router — all 404s serve index.html and React handles routing)
5. Save

### Add Bucket Policy (allow public reads)

1. Click your bucket → **Permissions** tab
2. **Bucket policy** → Edit → paste:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::gpt-app-frontend-myapp/*"
       }
     ]
   }
   ```
3. Save

> This is safe — your React HTML/JS/CSS files are intentionally public. Secrets are never in these files.

---

## 13. Step 10 — Create CloudFront Distribution

CloudFront serves your React app globally with low latency and provides free HTTPS.

1. **AWS Console → CloudFront → Create distribution**
2. **Origin domain:** Use the S3 **website endpoint** (not the REST endpoint):
   ```
   gpt-app-frontend-myapp.s3-website.eu-north-1.amazonaws.com
   ```
   > Important: use the `.s3-website.` format, NOT `.s3.amazonaws.com`
3. **Origin protocol:** HTTP only (S3 website endpoint only supports HTTP)
4. **Viewer protocol policy:** Redirect HTTP to HTTPS
5. **Default root object:** `index.html`
6. **Price class:** Use only North America and Europe (cheaper) or All locations
7. Click **Create distribution**

Wait 5–15 minutes for the distribution status to change from **Deploying** to **Enabled**.

**Copy the CloudFront domain name:**
```
d1v2k6g99m4u7p.cloudfront.net
```

### Fix 404 on Page Refresh (React Router)

React is a single-page app — all routes are handled by React, not the server. Without this fix, refreshing on `/callback` returns a 404.

1. CloudFront → your distribution → **Error pages** tab → **Create custom error response**
2. HTTP error code: `403`
3. Response page path: `/index.html`
4. HTTP response code: `200`
5. Repeat for error code `404`

---

## 14. Step 11 — Add ALB as Second CloudFront Origin (API Proxy)

This is the **most important step** to fix the Mixed Content error.

**The problem:**
- Your React app is served over **HTTPS** (CloudFront)
- Your ALB only has **HTTP** (no SSL certificate)
- Browsers block HTTPS pages from calling HTTP APIs (Mixed Content policy)

**The solution:**
Make CloudFront proxy API calls to the ALB. The user's browser only ever talks to CloudFront over HTTPS. CloudFront talks to the ALB over HTTP internally — which is fine because it happens inside AWS's network.

```
Browser → HTTPS → CloudFront → HTTP → ALB → ECS
```

### Add the ALB as a Second Origin

1. **CloudFront → your distribution → Origins tab → Create origin**
2. **Origin domain:** `gpt-app-backend-1357233706.eu-north-1.elb.amazonaws.com`
3. **Protocol:** HTTP only
4. **HTTP port:** 80
5. **Name:** `alb-backend`
6. **Response timeout:** 60 seconds (increase from default 30 — needed for slow AI responses)
7. **Keep-alive timeout:** 60 seconds
8. Click **Save changes**

### Add a Behaviour to Route /api/* to the ALB

1. **CloudFront → Behaviours tab → Create behaviour**
2. **Path pattern:** `/api/*`
3. **Origin:** `alb-backend` (the one you just created)
4. **Viewer protocol policy:** HTTPS only
5. **Allowed HTTP methods:** GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
6. **Cache policy:** `CachingDisabled` — API responses must NEVER be cached
7. **Origin request policy:** `AllViewer` — forwards all headers, cookies, query strings to ALB
8. **Compress objects automatically:** **No** — compression breaks SSE streaming responses
9. Click **Save changes**

### Update VITE_API_BASE_URL

Now your frontend calls the API through CloudFront, not the ALB directly:
```
Old: http://gpt-app-backend-1357233706.eu-north-1.elb.amazonaws.com/api/v1
New: https://d1v2k6g99m4u7p.cloudfront.net/api/v1
```

Update the GitHub secret `VITE_API_BASE_URL` to the new value and redeploy the frontend.

---

## 15. Step 12 — Configure Auth0

### In Auth0 Dashboard — Application Settings

1. Go to **Auth0 Dashboard → Applications → your React SPA application**
2. Update these fields (comma-separate multiple values):

   **Allowed Callback URLs:**
   ```
   http://localhost:5173/callback, https://d1v2k6g99m4u7p.cloudfront.net/callback
   ```

   **Allowed Logout URLs:**
   ```
   http://localhost:5173, https://d1v2k6g99m4u7p.cloudfront.net
   ```

   **Allowed Web Origins:**
   ```
   http://localhost:5173, https://d1v2k6g99m4u7p.cloudfront.net
   ```

3. Click **Save Changes**

> Why both localhost and CloudFront? So the app works both locally and in production without changing any code.

### In Auth0 Dashboard — API Settings

1. Go to **Auth0 Dashboard → APIs → your API**
2. **Identifier (Audience):** must exactly match what your backend expects:
   ```
   http://gpt-app-backend-1357233706.eu-north-1.elb.amazonaws.com
   ```
3. This value must match in **3 places exactly** (including trailing slash — be careful):
   - Auth0 API Identifier
   - GitHub secret: `AUTH0_AUDIENCE`
   - GitHub secret: `VITE_AUTH0_AUDIENCE`

> **Tip:** A common mistake is a trailing slash mismatch. `https://api.example.com` and `https://api.example.com/` are treated as different audiences.

---

## 16. Step 13 — Add GitHub Secrets

Go to: **GitHub → your repository → Settings → Secrets and variables → Actions → New repository secret**

Add every secret in this table:

### AWS Secrets (shared by both workflows)

| Secret Name | Value | Example |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key | `wJalrXUtnFEMI/K7MDENG/...` |
| `AWS_REGION` | AWS region | `eu-north-1` |

### Backend Secrets (used by deploy-backend.yml)

| Secret Name | Value | Example |
|---|---|---|
| `ECR_REPOSITORY` | ECR repo name | `gpt-app-backend` |
| `ECS_CLUSTER` | ECS cluster name | `gpt-app-cluster` |
| `ECS_SERVICE` | ECS service name | `gpt-app-backend-service-pysbnto0` |
| `ECS_TASK_DEFINITION` | Task definition family name | `gpt-app-backend` |
| `CONTAINER_NAME` | Container name in task definition | `gpt-app-backend` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `AUTH0_DOMAIN` | Auth0 tenant domain | `dev-5yxjxh8ys4lrkckf.us.auth0.com` |
| `AUTH0_AUDIENCE` | Auth0 API identifier | `http://gpt-app-backend-1357233706.eu-north-1.elb.amazonaws.com` |
| `AUTH0_CLIENT_ID` | Auth0 application client ID | `KVdynvgjer0Octrb8zD9jxb0uZUnxk1F` |
| `CORS_ORIGINS` | Allowed frontend origins (JSON array) | `["https://d1v2k6g99m4u7p.cloudfront.net"]` |

### Frontend Secrets (used by deploy-frontend.yml)

| Secret Name | Value | Example |
|---|---|---|
| `S3_BUCKET` | S3 bucket name | `gpt-app-frontend-myapp` |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID | `E3468IUABV8DUP` |
| `VITE_API_BASE_URL` | Backend API URL via CloudFront | `https://d1v2k6g99m4u7p.cloudfront.net/api/v1` |
| `VITE_AUTH0_DOMAIN` | Auth0 tenant domain | `dev-5yxjxh8ys4lrkckf.us.auth0.com` |
| `VITE_AUTH0_CLIENT_ID` | Auth0 application client ID | `KVdynvgjer0Octrb8zD9jxb0uZUnxk1F` |
| `VITE_AUTH0_AUDIENCE` | Auth0 API identifier | `http://gpt-app-backend-1357233706.eu-north-1.elb.amazonaws.com` |

> **VITE_ prefix:** Vite only exposes variables prefixed with `VITE_` to the browser bundle. Without this prefix, the variable is undefined in the React app.

---

## 17. Step 14 — Push Code and Trigger CI/CD

### What triggers each workflow

| Workflow | Triggers when |
|---|---|
| `deploy-backend.yml` | You push to `main` and files in `application/backend/` changed |
| `deploy-frontend.yml` | You push to `main` and files in `application/frontend/` changed |
| Both | You can also trigger manually: GitHub → Actions → select workflow → Run workflow |

### What each workflow does

**Backend workflow (deploy-backend.yml):**
```
1. Checkout code
2. Configure AWS credentials using secrets
3. Login Docker to ECR
4. Build Docker image from application/backend/Dockerfile
5. Tag with commit SHA + latest
6. Push both tags to ECR
7. Download current Task Definition from ECS
   → Strip read-only fields with jq (enableFaultInjection, taskDefinitionArn, etc.)
8. Inject new image URI + environment variables into Task Definition
9. Register new Task Definition revision in ECS
10. Update ECS Service to use new revision
11. Wait for new tasks to be healthy before finishing
```

**Frontend workflow (deploy-frontend.yml):**
```
1. Checkout code
2. Set up Node.js 20
3. npm ci (install exact versions from package-lock.json)
4. npm run build with VITE_* env vars injected
   → Creates application/frontend/dist/ folder
5. Configure AWS credentials
6. aws s3 sync dist/ → uploads all files to S3
   → JS/CSS files: cache-control max-age=1 year (they have hashed filenames)
   → index.html: no-cache (always fetch fresh — contains references to hashed files)
7. aws cloudfront create-invalidation /* → tells edge locations to clear cache
```

---

## 18. Errors We Hit and How We Fixed Them

### Error 1 — ECS Cluster creation failed: service-linked role

```
Unable to assume the service linked role.
InvalidParameterException
```

**Cause:** Fresh AWS account — the `AWSServiceRoleForECS` IAM role doesn't exist yet.

**Fix:**
```bash
aws iam create-service-linked-role --aws-service-name ecs.amazonaws.com
```

---

### Error 2 — GitHub Actions: Unexpected key 'enableFaultInjection'

```
Error: Failed to register task definition in ECS:
Unexpected key 'enableFaultInjection' found in params
```

**Cause:** `describe-task-definition` returns newer read-only fields that the older `@v1` action (AWS SDK v2) doesn't accept when re-registering.

**Fix:** Strip the unrecognised fields using `jq` before saving the JSON:
```yaml
aws ecs describe-task-definition \
  --task-definition "$ECS_TASK_DEFINITION" \
  --query taskDefinition \
| jq 'del(
    .taskDefinitionArn, .revision, .status,
    .requiresAttributes, .compatibilities,
    .registeredAt, .registeredBy,
    .deregisteredAt, .enableFaultInjection
  )' \
  > task-definition.json
```

---

### Error 3 — Target Group showed Unhealthy

**Cause 1:** Health check path was wrong — ALB was hitting `/` but FastAPI's health endpoint is at `/api/v1/health`.

**Fix:** EC2 → Target Groups → your TG → Health checks → Edit → set path to `/api/v1/health`

**Cause 2:** ECS task security group only allowed traffic from the default security group — the ALB was in a different security group, so its health check requests were blocked.

**Fix:** Add inbound rule to ECS task security group:
```
Type:   Custom TCP
Port:   8000
Source: <ALB Security Group ID>
```

---

### Error 4 — Frontend showed "Safari can't find the server"

**Cause:** Was opening the S3 URL directly instead of the CloudFront URL.

**Fix:** Use the CloudFront domain name, not the S3 bucket URL:
```
❌ https://gpt-app-frontend-myapp.s3.amazonaws.com
✅ https://d1v2k6g99m4u7p.cloudfront.net
```

---

### Error 5 — 403 AccessDenied from S3

```
Code: AccessDenied
Message: Access Denied
```

**Cause:** S3 bucket had "Block all public access" enabled. CloudFront using the S3 website endpoint accesses S3 as a public anonymous user — it needs the bucket to allow public reads.

**Fix:**
1. S3 → Permissions → Block public access → uncheck all 4 checkboxes
2. Add bucket policy allowing `s3:GetObject` for `Principal: "*"`

---

### Error 6 — "Fetch API cannot load... due to access control checks" (CORS)

```
Fetch API cannot load http://...elb.amazonaws.com/api/v1/chat/completions
due to access control checks.
```

**Cause:** `CORS_ORIGINS` GitHub secret only contained localhost URLs. The CloudFront domain wasn't in the allowed list so FastAPI rejected the request.

**Fix:** Update `CORS_ORIGINS` GitHub secret:
```
["https://d1v2k6g99m4u7p.cloudfront.net"]
```
Then re-run the backend deploy workflow to inject the new value into the running container.

> **Note:** You cannot use `["*"]` (wildcard) because `allow_credentials=True` is set in FastAPI. The browser blocks wildcard + credentials together. You must list the exact origin.

---

### Error 7 — "Network connection was lost" / Mixed Content

**Cause:** React app served over HTTPS (CloudFront) was calling the ALB over HTTP. Browsers hard-block this (Mixed Content policy).

```
HTTPS page → calls → HTTP ALB URL   ← browser blocks this
```

**Fix:** Add the ALB as a second origin in CloudFront and route `/api/*` to it:
- CloudFront handles HTTPS from the browser
- CloudFront calls the ALB over HTTP internally (inside AWS network — safe)

**Additionally:** Disable compression on the `/api/*` behaviour — Gzip compression breaks Server-Sent Events (SSE) streaming because it buffers chunks before sending.

---

### Error 8 — Streaming responses dropped / cut off

**Cause:** CloudFront's default 30-second origin timeout was too short for slow AI responses. Also, CloudFront was compressing the SSE stream, which requires buffering — breaking real-time streaming.

**Fix:**
1. CloudFront → ALB origin → Edit → set **Response timeout: 60 seconds**
2. CloudFront → `/api/*` behaviour → Edit → **Compress objects automatically: No**

---

## 19. Cost Overview

Approximate monthly costs for this setup at low/zero traffic:

| Service | Cost |
|---|---|
| ECS Fargate (1 task, 0.5 vCPU, 1 GB, running 24/7) | ~$15–18/month |
| ALB | ~$16/month (base cost regardless of traffic) |
| ECR (first 500 MB free) | ~$0 |
| S3 (small React app) | ~$0.01/month |
| CloudFront (first 1 TB/month free) | ~$0 |
| **Total** | **~$31–34/month** |

> **To save cost when not in use:** Scale the ECS service desired count to 0 (no running tasks = no Fargate charges). The ALB still charges ~$0.50/day even with 0 tasks. To fully stop costs, delete the ALB when not needed.

---

## Quick Reference — Common Commands

```bash
# Scale ECS service down (stop tasks to save cost)
aws ecs update-service \
  --cluster gpt-app-cluster \
  --service gpt-app-backend-service-pysbnto0 \
  --desired-count 0 \
  --region eu-north-1

# Scale ECS service back up
aws ecs update-service \
  --cluster gpt-app-cluster \
  --service gpt-app-backend-service-pysbnto0 \
  --desired-count 1 \
  --region eu-north-1

# Manually invalidate CloudFront cache (after manual S3 upload)
aws cloudfront create-invalidation \
  --distribution-id E3468IUABV8DUP \
  --paths "/*"

# Check running ECS tasks
aws ecs list-tasks \
  --cluster gpt-app-cluster \
  --region eu-north-1

# View ECS task logs (get task ID first from above command)
aws logs get-log-events \
  --log-group-name /ecs/gpt-app-backend \
  --log-stream-name ecs/gpt-app-backend/<task-id> \
  --region eu-north-1
```

---

*Deployment guide written for the GPT FastAPI Application — April 2026*
*Stack: FastAPI + React + Auth0 + AWS ECS Fargate + S3 + CloudFront + GitHub Actions*
