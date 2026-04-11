# AWS Cloud Training — Beginner to Intermediate Guide
### For Software Developers (0–2 Years Experience)

---

## Table of Contents

1. [What is Cloud Computing?](#1-what-is-cloud-computing)
2. [Why AWS?](#2-why-aws)
3. [Setting Up Your AWS Account](#3-setting-up-your-aws-account)
4. [AWS Global Infrastructure](#4-aws-global-infrastructure)
5. [IAM — Identity and Access Management](#5-iam--identity-and-access-management)
6. [EC2 — Virtual Servers in the Cloud](#6-ec2--virtual-servers-in-the-cloud)
7. [S3 — Simple Storage Service](#7-s3--simple-storage-service)
8. [RDS — Relational Database Service](#8-rds--relational-database-service)
9. [VPC — Virtual Private Cloud (Networking Basics)](#9-vpc--virtual-private-cloud-networking-basics)
10. [Elastic Beanstalk — Deploy Apps Without Managing Servers](#10-elastic-beanstalk--deploy-apps-without-managing-servers)
11. [Lambda — Serverless Computing](#11-lambda--serverless-computing)
12. [API Gateway — Build and Expose APIs](#12-api-gateway--build-and-expose-apis)
13. [CloudWatch — Monitoring and Logging](#13-cloudwatch--monitoring-and-logging)
14. [CodePipeline & CodeDeploy — CI/CD on AWS](#14-codepipeline--codedeploy--cicd-on-aws)
15. [AWS CLI — Control AWS From Your Terminal](#15-aws-cli--control-aws-from-your-terminal)
16. [ECR & ECS — Containers on AWS](#16-ecr--ecs--containers-on-aws)
17. [CloudFormation — Infrastructure as Code](#17-cloudformation--infrastructure-as-code)
18. [Cost Management — Don't Get Surprised by Your Bill](#18-cost-management--dont-get-surprised-by-your-bill)
19. [Real-World Project: Deploy a Python Web App on AWS](#19-real-world-project-deploy-a-python-web-app-on-aws)
20. [Next Steps & What to Learn After This](#20-next-steps--what-to-learn-after-this)
21. [CloudFront CDN — Deep Dive](#21-cloudfront-cdn--deep-dive)
22. [ECS Fargate — Serverless Containers Explained](#22-ecs-fargate--serverless-containers-explained)
23. [App Runner — Simplest Container Deployment](#23-app-runner--simplest-container-deployment)
24. [Production Deployment Cheat Sheet — When to Use What](#24-production-deployment-cheat-sheet--when-to-use-what)

---

## 1. What is Cloud Computing?

### Think of it like renting instead of buying

Imagine you need a powerful computer to run your application. You have two options:

- **Option A (Old way):** Buy a physical server, set it up in a data center, pay for electricity, cooling, security, and maintenance — even when nobody is using it.
- **Option B (Cloud way):** Rent a virtual computer online, pay only for the hours you use it, and shut it down when you are done.

**Cloud Computing = Option B.**

Cloud computing means using IT resources (servers, databases, storage, networking) over the internet, on-demand, and paying only for what you use — just like your electricity bill.

### Three Types of Cloud Services

| Type | Full Form | What It Means | Example |
|------|-----------|---------------|---------|
| **IaaS** | Infrastructure as a Service | You get raw hardware (virtual machines, storage) and manage everything else | AWS EC2 |
| **PaaS** | Platform as a Service | You get a platform to deploy code; AWS manages the OS and runtime | AWS Elastic Beanstalk |
| **SaaS** | Software as a Service | A complete application you just use via browser | Gmail, Zoom |

> **As a developer**, you will mostly deal with **IaaS** and **PaaS**.

### Three Cloud Deployment Models

- **Public Cloud** — Resources owned and operated by AWS, shared across many customers (you never see the physical server). This is what most developers use.
- **Private Cloud** — A cloud built and used exclusively by one company (very expensive, used by large banks/governments).
- **Hybrid Cloud** — A mix of on-premises servers and public cloud working together.

---

## 2. Why AWS?

AWS (Amazon Web Services) was launched in **2006** by Amazon. It is currently the **world's leading cloud provider**.

### Why should you learn AWS as a developer?

- **Most popular:** Over 33% of the global cloud market belongs to AWS. Most job descriptions for backend/full-stack roles mention AWS.
- **Huge tool set:** AWS has 200+ services — from running a simple website to training AI models.
- **Free Tier:** AWS offers a free tier for 12 months so you can practice without paying.
- **Industry standard:** If you join a startup or a large company, there is a very high chance they are on AWS.

### AWS vs. Azure vs. GCP (Quick Comparison)

| Feature | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Market share | ~33% | ~22% | ~11% |
| Best for | General use, startups | Enterprise (Microsoft shops) | Data & ML |
| Learning resources | Massive community | Good | Growing |
| Free tier | 12 months + always free | 12 months | $300 credit |

> Start with AWS. The concepts you learn here (compute, storage, networking) transfer easily to Azure or GCP later.

---

## 3. Setting Up Your AWS Account

### Step-by-Step

1. Go to [https://aws.amazon.com](https://aws.amazon.com) and click **"Create an AWS Account"**.
2. Enter your email address and choose an account name.
3. Enter your credit/debit card details — **you won't be charged** as long as you stay within the Free Tier limits.
4. Complete phone verification.
5. Choose the **"Basic (Free)"** support plan.
6. Log in to the **AWS Management Console** — this is the web UI where you manage everything.

### Free Tier — What You Get for Free

| Service | Free Tier Limit |
|---------|-----------------|
| EC2 (virtual server) | 750 hours/month for 12 months (t2.micro or t3.micro) |
| S3 (file storage) | 5 GB for 12 months |
| RDS (database) | 750 hours/month for 12 months (db.t2.micro) |
| Lambda (serverless) | 1 million requests/month — **always free** |
| CloudWatch | Basic monitoring — always free |

> **Important:** Always set a **billing alarm** after creating your account so you get an email if charges go beyond $1. We will cover this in Section 18.

---

## 4. AWS Global Infrastructure

### Regions and Availability Zones

AWS does not run from a single building. It has data centers spread across the entire world.

**Region** = A geographic area (like "US East — Virginia" or "Asia Pacific — Mumbai"). Each region is completely independent.

**Availability Zone (AZ)** = One or more physical data centers within a region. Each region has at least 2–3 AZs. They are physically separate but connected with low-latency links.

```
Region: ap-south-1 (Mumbai)
  ├── AZ: ap-south-1a  (Data center group A)
  ├── AZ: ap-south-1b  (Data center group B)
  └── AZ: ap-south-1c  (Data center group C)
```

### Why does this matter to you?

- **High availability:** If one AZ goes down (fire, flood), your app keeps running in another AZ.
- **Low latency:** Deploy your app in the region closest to your users. If your users are in India, use `ap-south-1` (Mumbai).
- **Data residency:** Some regulations require data to stay in a specific country.

### Choosing a Region

When you log into AWS Console, always check which region is selected in the top-right corner. Resources created in one region are **not visible** in another region.

> **Tip for learning:** Use `us-east-1` (N. Virginia) — it has the most services available and is the default for many AWS tutorials.

---

## 5. IAM — Identity and Access Management

### What is IAM?

When you create your AWS account, you become the **root user** — you have unlimited power. But you should **never use the root user** for daily work. Instead, you create smaller accounts with only the permissions they need.

IAM is the AWS service that controls **who can access what** in your AWS account.

> **Real-world analogy:** In a company, not everyone has access to everything. A junior developer can deploy code but cannot delete the production database. IAM sets those rules in AWS.

### Key IAM Concepts

#### Users
An IAM User represents a person or application. Each user gets their own username and password (for console access) or access keys (for CLI/API access).

```
Root Account
  └── IAM User: "manu-dev"        ← You create this for daily work
  └── IAM User: "ci-cd-bot"       ← For your deployment pipeline
  └── IAM User: "intern-raj"      ← Limited permissions for interns
```

#### Groups
Instead of giving permissions to each user one by one, you create groups and attach permissions to the group.

```
Group: "Developers"
  ├── Permission: Read/Write to S3
  ├── Permission: Deploy to Elastic Beanstalk
  └── Members: manu-dev, intern-raj
```

#### Policies
A policy is a JSON document that defines what actions are **allowed** or **denied** on which AWS resources.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

This policy says: **Allow** the actions `GetObject` (download) and `PutObject` (upload) on the S3 bucket named `my-bucket`.

#### Roles
A Role is like a policy that can be **assumed** by an AWS service itself (not a human). For example, if your EC2 server needs to read files from S3, you create a Role with S3 access and attach it to the EC2 instance.

> **Think of a Role as a temporary badge** — the EC2 server wears the badge to get access to S3, and doesn't need a hardcoded username/password.

### Hands-On: Create Your First IAM User

1. Go to **IAM** in the AWS Console.
2. Click **Users → Add users**.
3. Enter username: `my-dev-user`.
4. Enable **"Access key"** (for CLI) and **"Password"** (for console).
5. Attach the policy: **AdministratorAccess** (for learning — in production, use least privilege).
6. Download the `.csv` file with the Access Key ID and Secret Access Key — **you won't see the secret key again**.
7. From now on, always log in using this IAM user, not root.

### IAM Best Practices

- Never share your root account credentials.
- Enable **Multi-Factor Authentication (MFA)** on the root account immediately.
- Follow the **Principle of Least Privilege** — give users only the permissions they actually need.
- Rotate access keys regularly.
- Never hardcode access keys in your source code — use environment variables or IAM Roles instead.

---

## 6. EC2 — Virtual Servers in the Cloud

### What is EC2?

EC2 (Elastic Compute Cloud) is AWS's service to rent virtual computers. You can spin up a Linux or Windows server in under 2 minutes, install your app on it, and shut it down when not needed.

> **Analogy:** EC2 is like renting a laptop from AWS. You choose the specs (CPU, RAM, storage), install what you need, and pay only while you use it.

### EC2 Key Concepts

#### Instance Types
AWS offers many instance types optimized for different use cases.

| Family | Use Case | Example |
|--------|----------|---------|
| `t` (General) | Small apps, development | `t3.micro` (Free Tier) |
| `m` (Balanced) | Web servers, databases | `m5.large` |
| `c` (Compute) | CPU-heavy tasks | `c5.xlarge` |
| `r` (Memory) | In-memory databases (Redis) | `r5.large` |
| `g` (GPU) | Machine learning, video | `g4dn.xlarge` |

> **For learning:** Always use `t2.micro` or `t3.micro` — they are in the Free Tier.

#### AMI (Amazon Machine Image)
An AMI is a pre-configured template for your EC2 instance — it includes the operating system (like Ubuntu 22.04 or Amazon Linux 2) and sometimes pre-installed software.

> Think of an AMI as a **snapshot/blueprint** of a computer's disk. You pick an AMI and EC2 creates your server from it.

#### Key Pairs
When you create an EC2 instance running Linux, you connect to it using SSH. AWS uses a key pair (a public key stored on the server + a private key `.pem` file you download). The `.pem` file is your password — **never lose it or share it**.

#### Security Groups
A Security Group is a virtual firewall that controls **inbound** (incoming) and **outbound** (outgoing) traffic to your EC2 instance.

```
Security Group: "web-server-sg"
  Inbound Rules:
    ├── Port 22   (SSH)   — Allow from My IP only
    ├── Port 80   (HTTP)  — Allow from anywhere (0.0.0.0/0)
    └── Port 443  (HTTPS) — Allow from anywhere (0.0.0.0/0)
  Outbound Rules:
    └── All traffic — Allow (default)
```

### Hands-On: Launch Your First EC2 Instance

1. Go to **EC2** in the AWS Console → **Launch Instance**.
2. Name it: `my-first-server`.
3. Choose AMI: **Amazon Linux 2023** (or Ubuntu 22.04 LTS).
4. Instance type: `t2.micro` (Free Tier eligible).
5. Key pair: Create a new one, name it `my-key`, download the `.pem` file.
6. Security group: Allow SSH (port 22) from your IP, HTTP (port 80) from anywhere.
7. Storage: 8 GB gp3 (default is fine).
8. Click **Launch Instance**.

### Connect to Your Instance

```bash
# Fix permissions on your key file (required on Mac/Linux)
chmod 400 my-key.pem

# Connect via SSH
ssh -i "my-key.pem" ec2-user@<your-public-ip>

# For Ubuntu AMIs, the default user is "ubuntu"
ssh -i "my-key.pem" ubuntu@<your-public-ip>
```

### Install a Simple Web Server on EC2

```bash
# Once connected to the EC2 instance:
sudo yum update -y                     # Update packages (Amazon Linux)
sudo yum install -y httpd              # Install Apache web server
sudo systemctl start httpd             # Start Apache
sudo systemctl enable httpd            # Auto-start on reboot

# Create a test page
echo "<h1>Hello from EC2!</h1>" | sudo tee /var/www/html/index.html
```

Open your browser and go to `http://<your-public-ip>` — you should see "Hello from EC2!".

### EC2 Pricing Models

| Model | How It Works | When to Use |
|-------|--------------|-------------|
| **On-Demand** | Pay by the hour/second, no commitment | Learning, unpredictable workloads |
| **Reserved** | Commit for 1–3 years, up to 72% cheaper | Stable production workloads |
| **Spot** | Bid for unused capacity, up to 90% cheaper | Batch jobs, can be interrupted |
| **Savings Plans** | Commit to a dollar amount/hour | Flexible alternative to Reserved |

> **For learning:** Always use On-Demand and **stop (not terminate) your instance when not using it** to avoid charges.

---

## 7. S3 — Simple Storage Service

### What is S3?

S3 is AWS's object storage service. You can store any kind of file — images, videos, PDFs, database backups, code deployments — and access them from anywhere in the world.

> **Analogy:** S3 is like Google Drive or Dropbox, but for developers — it has a programmable API, scales to petabytes, and integrates with every AWS service.

### S3 Key Concepts

#### Buckets
A bucket is like a top-level folder that holds your files. Bucket names must be **globally unique** across all AWS accounts worldwide.

```
Bucket: my-app-assets-2024
  ├── images/
  │     ├── logo.png
  │     └── banner.jpg
  ├── uploads/
  │     └── user-123-profile.jpg
  └── backups/
        └── db-2024-03-28.sql
```

#### Objects
Each file stored in S3 is called an **object**. An object has:
- A **key** (the file path/name): `images/logo.png`
- The **data** (the actual file content)
- **Metadata** (content type, size, custom tags, etc.)

#### Storage Classes

| Class | Use Case | Cost |
|-------|----------|------|
| **S3 Standard** | Frequently accessed data | Higher |
| **S3 Infrequent Access** | Backups, older data | Lower |
| **S3 Glacier** | Long-term archival (retrieved in minutes/hours) | Very low |
| **S3 Intelligent-Tiering** | Auto-moves data between tiers based on access | Smart |

### Hands-On: Create a Bucket and Upload a File

```bash
# Using AWS CLI (covered in Section 15)

# Create a bucket (bucket names must be globally unique)
aws s3 mb s3://my-first-bucket-manu-2024

# Upload a file
aws s3 cp myfile.txt s3://my-first-bucket-manu-2024/

# List files in bucket
aws s3 ls s3://my-first-bucket-manu-2024/

# Download a file
aws s3 cp s3://my-first-bucket-manu-2024/myfile.txt ./downloaded.txt

# Delete a file
aws s3 rm s3://my-first-bucket-manu-2024/myfile.txt
```

### Making S3 Files Publicly Accessible

By default, all S3 objects are **private**. To host a static website or share files publicly:

1. Go to your bucket → **Permissions** → Disable "Block all public access".
2. Add a **Bucket Policy**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-first-bucket-manu-2024/*"
    }
  ]
}
```

3. Enable **Static website hosting** under the Properties tab.

### Using S3 in Python (Boto3)

```python
import boto3

# Create S3 client
s3 = boto3.client('s3', region_name='us-east-1')

# Upload a file
s3.upload_file('local_file.txt', 'my-bucket-name', 'remote_path/file.txt')

# Download a file
s3.download_file('my-bucket-name', 'remote_path/file.txt', 'local_file.txt')

# Generate a Pre-signed URL (temporary access link — expires after 1 hour)
url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'my-bucket-name', 'Key': 'remote_path/file.txt'},
    ExpiresIn=3600
)
print(url)  # Share this URL — it expires in 1 hour
```

### S3 Best Practices

- Enable **versioning** on important buckets to recover accidentally deleted files.
- Use **lifecycle rules** to automatically move old files to cheaper storage classes.
- Never store secrets or credentials in S3 — use AWS Secrets Manager instead.
- Use **Pre-signed URLs** to give temporary access to private files instead of making them public.

---

## 8. RDS — Relational Database Service

### What is RDS?

RDS is AWS's managed relational database service. Instead of installing and managing MySQL/PostgreSQL yourself on an EC2 server, AWS handles all the heavy lifting — backups, patching, failover, scaling.

> **Analogy:** It's the difference between cooking your own meal (EC2 with manual DB install) versus ordering from a restaurant (RDS) — you get the food either way, but the restaurant handles all the prep work.

### Supported Database Engines

- **MySQL** — Most popular open-source relational database
- **PostgreSQL** — Advanced open-source database (supports JSON, full-text search, etc.)
- **MariaDB** — MySQL fork
- **Oracle** — Enterprise (paid license)
- **Microsoft SQL Server** — Enterprise (paid)
- **Amazon Aurora** — AWS's own high-performance database, compatible with MySQL/PostgreSQL (5x faster than standard MySQL)

### RDS Key Concepts

#### Multi-AZ Deployment
AWS can automatically replicate your database to a second Availability Zone. If the primary DB fails, AWS automatically fails over to the standby — usually in under 2 minutes. This is for **high availability**.

#### Read Replicas
A Read Replica is a read-only copy of your database. Your app can send all the heavy `SELECT` queries to the read replica, reducing load on the primary database. This is for **scaling reads**.

```
Primary DB (writes):   ← Your app writes new data here
  └── Read Replica 1   ← Your app reads data from here
  └── Read Replica 2   ← Another region, for global users
```

### Hands-On: Create a PostgreSQL RDS Instance

1. Go to **RDS** in the AWS Console → **Create database**.
2. Choose: **Standard Create** → **PostgreSQL**.
3. Templates: **Free tier**.
4. DB instance identifier: `my-postgres-db`.
5. Master username: `admin`, set a strong password.
6. Instance type: `db.t3.micro` (Free Tier).
7. Storage: 20 GB gp2.
8. **Important:** Under Connectivity → VPC security group → Create a new one, allow port `5432` from your EC2 instance or your IP.
9. Click **Create database** (it takes ~5 minutes).

### Connect to RDS from Python

```python
import psycopg2

conn = psycopg2.connect(
    host="my-postgres-db.xxxx.us-east-1.rds.amazonaws.com",
    port=5432,
    database="postgres",
    user="admin",
    password="your-password"
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())

conn.close()
```

> **Security Tip:** Never hardcode database passwords in your code. Use **AWS Secrets Manager** or environment variables.

---

## 9. VPC — Virtual Private Cloud (Networking Basics)

### What is VPC?

A VPC is your own **private, isolated network** within AWS. Think of it as the walls of your house — everything inside is yours and separated from other AWS customers.

> **Analogy:** If AWS is a large apartment complex, your VPC is your own apartment. You control the doors (security groups), windows (network ACLs), and who can enter or leave.

### VPC Key Concepts

#### Subnets
A subnet is a section of your VPC's IP address range assigned to a specific AZ.

- **Public Subnet** — Has a route to the internet. Resources here (like EC2 web servers) can be accessed from the outside.
- **Private Subnet** — No direct route to the internet. Resources here (like databases) are protected from the outside world.

```
VPC: 10.0.0.0/16 (Mumbai Region)
  ├── Public Subnet:  10.0.1.0/24  (AZ: ap-south-1a)  ← Web Servers
  ├── Public Subnet:  10.0.2.0/24  (AZ: ap-south-1b)  ← Load Balancer
  ├── Private Subnet: 10.0.3.0/24  (AZ: ap-south-1a)  ← Database
  └── Private Subnet: 10.0.4.0/24  (AZ: ap-south-1b)  ← Database (Standby)
```

#### Internet Gateway
An Internet Gateway (IGW) lets resources in your public subnet communicate with the internet. Without it, nothing in your VPC can reach the internet.

#### NAT Gateway
A NAT Gateway lets resources in your **private subnet** initiate outbound connections to the internet (like downloading software updates), but prevents the internet from initiating connections to them. It's a one-way door.

#### Route Tables
A route table has a set of rules (routes) that determine where network traffic is directed. Think of it as a GPS for network packets.

### Default VPC

When you create an AWS account, AWS automatically creates a **default VPC** in each region. This is why you can launch an EC2 instance without setting up networking yourself during learning. For production, you should create a custom VPC.

> **As a developer**, you don't need to design VPCs from scratch immediately. But understanding subnets (public vs. private) and security groups is essential because they affect what can talk to what.

---

## 10. Elastic Beanstalk — Deploy Apps Without Managing Servers

### What is Elastic Beanstalk?

Elastic Beanstalk is a **PaaS (Platform as a Service)** from AWS. You give it your application code (Python, Node.js, Java, Ruby, etc.), and it automatically provisions EC2 instances, load balancers, auto-scaling, and health monitoring for you.

> **Analogy:** EC2 is like renting an empty apartment — you bring your own furniture. Elastic Beanstalk is like a serviced apartment — it comes with everything set up, you just move in.

### How Elastic Beanstalk Works

```
You provide:   → Application code (zip file or Git repo)
Beanstalk creates: → EC2 instances, Load Balancer, Auto Scaling Group,
                      Security Groups, CloudWatch monitoring
```

### Supported Platforms

- Python (Django, Flask)
- Node.js
- Java (Spring Boot)
- Ruby on Rails
- PHP
- .NET
- Docker (single container or multi-container)
- Go

### Hands-On: Deploy a Flask App to Elastic Beanstalk

#### Step 1: Prepare Your Flask App

```
my-flask-app/
  ├── application.py      ← Must be named "application.py" for Beanstalk
  ├── requirements.txt
  └── .ebextensions/      ← Optional: Beanstalk config files
```

```python
# application.py
from flask import Flask

application = Flask(__name__)  # Must be named "application"

@application.route('/')
def hello():
    return '<h1>Hello from Elastic Beanstalk!</h1>'

if __name__ == '__main__':
    application.run(debug=True)
```

```
# requirements.txt
flask==3.0.0
```

#### Step 2: Install the EB CLI

```bash
pip install awsebcli

# Verify installation
eb --version
```

#### Step 3: Deploy

```bash
cd my-flask-app

# Initialize Beanstalk project
eb init -p python-3.11 my-flask-app --region us-east-1

# Create environment and deploy
eb create my-flask-env

# Open the deployed app in browser
eb open

# Deploy new changes
eb deploy

# View logs
eb logs

# Terminate environment (to avoid charges)
eb terminate my-flask-env
```

### When to Use Elastic Beanstalk

- You want to deploy quickly without managing infrastructure.
- You are building a web app or REST API.
- You don't yet need the fine-grained control of EC2.

---

## 11. Lambda — Serverless Computing

### What is Lambda?

AWS Lambda lets you run code **without provisioning or managing any servers**. You just upload your function, define what triggers it, and AWS runs it automatically — scaling instantly from 1 to 1,000,000 executions.

> **Analogy:** With EC2, you rent a car and are responsible for it (fuel, maintenance, insurance) even when parked. With Lambda, you use a taxi — you pay only for each trip, and the car disappears when the trip is done.

### How Lambda Works

```
Trigger → Lambda Function Runs → Result

Examples of Triggers:
  - HTTP request via API Gateway
  - A file uploaded to S3
  - A message arrives in an SQS queue
  - A schedule (like a cron job)
  - A database change in DynamoDB
```

### Lambda Key Concepts

- **Function** — Your code (a Python function, Node.js handler, etc.)
- **Handler** — The entry point. For Python: `lambda_function.lambda_handler`
- **Event** — The JSON data passed to your function (contains trigger details)
- **Context** — Runtime info (function name, timeout remaining, request ID)
- **Timeout** — Maximum 15 minutes per execution
- **Memory** — 128 MB to 10 GB RAM (you choose)

### Hands-On: Your First Lambda Function (Python)

```python
# lambda_function.py

def lambda_handler(event, context):
    print(f"Event received: {event}")
    
    name = event.get('name', 'World')
    
    return {
        'statusCode': 200,
        'body': f'Hello, {name}! This is running serverlessly!'
    }
```

**Deploy via AWS Console:**
1. Go to **Lambda** → **Create function**.
2. Choose **"Author from scratch"**.
3. Function name: `my-first-function`, Runtime: **Python 3.12**.
4. Click **Create function**.
5. Copy-paste the code above into the inline editor.
6. Click **Deploy**, then **Test**.
7. Create a test event: `{ "name": "Manu" }` → **Test**.
8. You should see: `Hello, Manu! This is running serverlessly!`

### Lambda Free Tier

Lambda has an **always-free tier** (not just 12 months):
- **1 million free requests per month**
- **400,000 GB-seconds of compute time per month**

For most small apps and APIs, Lambda will cost you **literally $0**.

### Lambda with S3 Trigger (Auto-resize Images)

A very common pattern — every time someone uploads an image to S3, a Lambda function automatically resizes it:

```python
import boto3
from PIL import Image
import io

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    # Get the uploaded file details from the S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Download the image
    response = s3.get_object(Bucket=bucket, Key=key)
    image_data = response['Body'].read()
    
    # Resize the image
    image = Image.open(io.BytesIO(image_data))
    image.thumbnail((200, 200))
    
    # Upload resized image
    buffer = io.BytesIO()
    image.save(buffer, 'JPEG')
    buffer.seek(0)
    
    s3.put_object(
        Bucket=bucket,
        Key=f"thumbnails/{key}",
        Body=buffer
    )
    
    return {'statusCode': 200, 'body': 'Image resized successfully'}
```

---

## 12. API Gateway — Build and Expose APIs

### What is API Gateway?

API Gateway is a fully managed service that lets you create, publish, and secure REST APIs (or WebSocket APIs). It acts as the **front door** for your backend services — whether they are Lambda functions, EC2 servers, or other AWS services.

```
User's Browser/App
       ↓  HTTPS Request
  API Gateway        ← Handles auth, rate limiting, routing, SSL
       ↓
  Lambda Function    ← Your business logic
       ↓
  Response back to user
```

### Lambda + API Gateway = Serverless REST API

This is one of the most popular patterns in modern cloud development.

```python
# lambda_function.py — A simple REST API handler

import json

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']
    
    if method == 'GET' and path == '/users':
        users = [
            {"id": 1, "name": "Manu Sri"},
            {"id": 2, "name": "Uday"}
        ]
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(users)
        }
    
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'})
    }
```

### Hands-On: Create an API with API Gateway + Lambda

1. Create the Lambda function above (name it `users-api`).
2. Go to **API Gateway** → **Create API** → **REST API** → **Build**.
3. API name: `users-rest-api`.
4. Create a resource: `/users`.
5. Create a method: **GET** → Integration type: **Lambda Function** → Select `users-api`.
6. Click **Deploy API** → Stage: `dev`.
7. AWS gives you a URL like: `https://abc123.execute-api.us-east-1.amazonaws.com/dev/users`
8. Open it in your browser — you should see the JSON list of users!

---

## 13. CloudWatch — Monitoring and Logging

### What is CloudWatch?

CloudWatch is AWS's monitoring and observability service. It collects logs, metrics, and events from all your AWS services so you can see what's happening, set alarms, and debug issues.

> **Analogy:** CloudWatch is like the dashboard of your car — it shows CPU usage, memory, and throws warnings when something is wrong.

### Key Features

#### Metrics
Automatic numeric data about your resources — collected every 1 or 5 minutes.

Examples:
- EC2: CPU utilization, network in/out, disk read/write
- RDS: Database connections, FreeStorageSpace
- Lambda: Invocations, Duration, Errors, Throttles

#### Logs (CloudWatch Logs)
Your application's log output, stored and searchable in CloudWatch.

For Lambda, `print()` statements automatically go to CloudWatch Logs. For EC2, you install the **CloudWatch Agent**.

```python
# Lambda — logs automatically appear in CloudWatch
def lambda_handler(event, context):
    print("Processing request...")  # → appears in CloudWatch Logs
    result = process_data(event)
    print(f"Done. Result: {result}")
    return result
```

#### Alarms
Set a threshold on any metric and get notified (via email, SMS, or trigger an action) when it crosses.

```
Alarm Example:
  - Metric: EC2 CPU Utilization
  - Threshold: > 80% for 5 minutes
  - Action: Send email to "admin@myapp.com"
```

### Hands-On: Set a Billing Alarm

1. Go to **CloudWatch** → **Alarms** → **Billing** (switch to `us-east-1` — billing alarms only work here).
2. **Create Alarm** → **Select metric** → **Billing** → **Total Estimated Charge**.
3. Set threshold: Greater than `$1`.
4. Notification: **Create new SNS topic** → enter your email → **Create topic**.
5. Alarm name: `billing-alert-1-dollar`.
6. Click **Create alarm**.
7. Check your email and **confirm the subscription**.

> Now you will receive an email if your AWS bill exceeds $1 for the month.

---

## 14. CodePipeline & CodeDeploy — CI/CD on AWS

### What is CI/CD?

**CI (Continuous Integration)** = Every time you push code, it is automatically built and tested.
**CD (Continuous Deployment/Delivery)** = After tests pass, code is automatically deployed to servers.

Without CI/CD: Developer → manually builds → manually SSHes into server → manually deploys → hopes nothing breaks.
With CI/CD: Developer → `git push` → automated pipeline tests and deploys for you.

### AWS CI/CD Tools

| Tool | What It Does |
|------|--------------|
| **CodeCommit** | AWS's managed Git repository (like GitHub, but private) |
| **CodeBuild** | Runs your build and test commands in a managed container |
| **CodeDeploy** | Deploys your application to EC2, Lambda, or ECS |
| **CodePipeline** | Orchestrates CodeCommit → CodeBuild → CodeDeploy into one automated pipeline |

### A Typical CI/CD Pipeline on AWS

```
Developer pushes code to CodeCommit / GitHub
          ↓
    CodePipeline triggers
          ↓
    CodeBuild (runs tests, builds Docker image)
          ↓
    Image pushed to ECR (container registry)
          ↓
    CodeDeploy deploys new version to ECS/EC2/Lambda
          ↓
    CloudWatch monitors for errors
```

### Hands-On: Create a Simple Pipeline

1. Go to **CodePipeline** → **Create pipeline**.
2. Name: `my-first-pipeline` → New service role.
3. **Source stage:** Choose GitHub (connect your GitHub account) → select repo and branch.
4. **Build stage:** AWS CodeBuild → Create project → choose runtime (e.g., standard:5.0).
5. **Deploy stage:** AWS Elastic Beanstalk → select your app and environment.
6. **Review and Create.**

Now every `git push` to your branch automatically builds and deploys your app!

---

## 15. AWS CLI — Control AWS From Your Terminal

### What is the AWS CLI?

The AWS CLI (Command Line Interface) is a tool that lets you manage all AWS services from your terminal instead of clicking through the web console.

> As a developer, the CLI is essential — you will use it for scripts, automation, and CI/CD pipelines.

### Installation

```bash
# macOS (using Homebrew)
brew install awscli

# Or using the official installer
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation
aws --version
```

### Configuration

```bash
aws configure
# It will ask for:
# AWS Access Key ID: (from your IAM user CSV file)
# AWS Secret Access Key: (from your IAM user CSV file)
# Default region name: us-east-1
# Default output format: json
```

This stores credentials in `~/.aws/credentials`.

### Common CLI Commands

```bash
# ---- S3 ----
aws s3 ls                                          # List all buckets
aws s3 ls s3://my-bucket/                          # List contents of bucket
aws s3 cp file.txt s3://my-bucket/file.txt         # Upload file
aws s3 sync ./local-dir s3://my-bucket/remote-dir  # Sync a directory

# ---- EC2 ----
aws ec2 describe-instances                          # List all instances
aws ec2 start-instances --instance-ids i-1234567890abcdef0
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# ---- Lambda ----
aws lambda list-functions                           # List all Lambda functions
aws lambda invoke --function-name my-function out.json  # Invoke a function
cat out.json                                        # See the response

# ---- IAM ----
aws iam list-users                                  # List all IAM users
aws iam create-user --user-name new-dev-user

# ---- RDS ----
aws rds describe-db-instances                       # List all RDS databases

# ---- General ----
aws configure list                                  # Show current configuration
aws sts get-caller-identity                         # Show which account you are logged into
```

### Named Profiles (Switching Between AWS Accounts)

```bash
# Set up a second profile
aws configure --profile production

# Use a specific profile
aws s3 ls --profile production

# Set default profile for a terminal session
export AWS_PROFILE=production
```

---

## 16. ECR & ECS — Containers on AWS

### What is ECR?

ECR (Elastic Container Registry) is AWS's private Docker image registry. It's like DockerHub, but private and integrated with AWS services.

```bash
# Authenticate Docker with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Create a repository
aws ecr create-repository --repository-name my-python-app

# Tag your local Docker image
docker tag my-python-app:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/my-python-app:latest

# Push to ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-python-app:latest
```

### What is ECS?

ECS (Elastic Container Service) is AWS's service for running Docker containers in the cloud. You define what Docker image to run, how much CPU/memory to give it, and ECS manages the rest.

### ECS Key Concepts

- **Task Definition** — A blueprint for your container (image, CPU, memory, environment variables, ports).
- **Task** — A running instance of a Task Definition (like a running container).
- **Service** — Ensures a desired number of tasks are always running. If one crashes, ECS starts a new one.
- **Cluster** — A group of EC2 instances (or Fargate capacity) where tasks run.

### ECS Fargate

Fargate is the **serverless mode** for ECS — you don't manage any EC2 instances at all. You just say "run this container with 512 MB RAM and 0.25 vCPU" and AWS figures out where to run it.

```
ECS on EC2:      You manage EC2 instances + containers
ECS on Fargate:  No servers to manage → just containers
```

> **For developers:** Use **Fargate**. It removes infrastructure management entirely.

### Quick ECS Fargate Deployment

```bash
# Using AWS CLI to run a container on Fargate
aws ecs run-task \
  --cluster my-cluster \
  --task-definition my-app:1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-xxxx],
    securityGroups=[sg-xxxx],
    assignPublicIp=ENABLED
  }"
```

---

## 17. CloudFormation — Infrastructure as Code

### What is Infrastructure as Code (IaC)?

Normally, you click through the AWS Console to create resources. But what if you need to recreate the exact same setup in a different region? Or if someone accidentally deletes a resource?

**Infrastructure as Code** means writing your AWS infrastructure in a configuration file (YAML or JSON) — then AWS creates all the resources automatically.

> **Analogy:** Instead of assembling furniture by hand every time, you write a detailed instruction manual. Anyone can use the manual to assemble the exact same furniture in minutes.

### CloudFormation Basics

```yaml
# template.yaml — Creates an S3 bucket and an EC2 instance

AWSTemplateFormatVersion: '2010-09-09'
Description: My First CloudFormation Stack

Resources:

  # Create an S3 bucket
  MyAppBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-cloudformation-bucket-2024
      VersioningConfiguration:
        Status: Enabled

  # Create an EC2 security group
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow HTTP and SSH
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

Outputs:
  BucketName:
    Description: Name of the created S3 bucket
    Value: !Ref MyAppBucket
```

```bash
# Deploy the CloudFormation template
aws cloudformation create-stack \
  --stack-name my-first-stack \
  --template-body file://template.yaml

# Check status
aws cloudformation describe-stacks --stack-name my-first-stack

# Delete everything created by the stack
aws cloudformation delete-stack --stack-name my-first-stack
```

> The big advantage: When you delete the stack, **all resources are deleted automatically** — so you don't accidentally leave running services that cost money.

---

## 18. Cost Management — Don't Get Surprised by Your Bill

### Understanding AWS Pricing

AWS pricing can feel complex but follows simple rules:
- **Compute (EC2, Lambda):** Pay for the actual compute time used.
- **Storage (S3, EBS):** Pay for GB stored per month.
- **Data transfer:** Transferring data INTO AWS is usually free. Transferring data OUT costs money.
- **Managed services (RDS, ElastiCache):** Usually more expensive than running software yourself on EC2, but saves time.

### Tools to Control Costs

#### AWS Free Tier Usage Dashboard
Go to **Billing → Free Tier** in the console to see exactly how much of your free-tier allowance you have used this month.

#### AWS Cost Explorer
Go to **Billing → Cost Explorer** to visualize your spending over time, broken down by service.

#### AWS Budgets
Set a budget and receive an alert when you are projected to exceed it.

```
Monthly Budget: $10
Alert at: 80% of budget ($8) — send email warning
Alert at: 100% ($10) — send urgent email
```

### Developer Tips to Avoid Unexpected Charges

1. **Stop EC2 instances** when not using them (stopping = no compute charge, but EBS storage still costs ~$0.10/GB/month).
2. **Terminate EC2 instances** you no longer need (this also deletes the attached EBS volume by default).
3. **Delete unused Elastic IPs** — allocated Elastic IPs that are not attached to a running instance are billed.
4. **Delete RDS instances** when done practicing (they are not free after the 12-month Free Tier).
5. **Delete NAT Gateways** — these cost ~$0.045/hour even when idle.
6. **Set a billing alarm** (Section 13) and a **Budget** for $5/month.
7. Use **CloudFormation** templates for practice — delete the entire stack when done.

---

## 19. Real-World Project: Deploy a Python Web App on AWS

Let's put everything together. We will deploy a simple Flask API that:
- Runs on EC2 (or Elastic Beanstalk)
- Stores uploaded files in S3
- Uses an RDS PostgreSQL database
- Is monitored with CloudWatch

### Project Structure

```
flask-aws-app/
  ├── application.py          ← Flask app
  ├── requirements.txt
  ├── .ebextensions/
  │     └── 01_env.config     ← Beanstalk environment variables
  └── README.md
```

### application.py

```python
import os
import boto3
import psycopg2
from flask import Flask, request, jsonify

application = Flask(__name__)

# S3 client
s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME', 'appdb'),
        user=os.environ.get('DB_USER', 'admin'),
        password=os.environ.get('DB_PASSWORD')
    )

@application.route('/')
def home():
    return jsonify({'status': 'running', 'message': 'Flask app is live on AWS!'})

@application.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    s3.upload_fileobj(file, BUCKET_NAME, file.filename)
    
    return jsonify({
        'message': 'File uploaded successfully',
        'url': f'https://{BUCKET_NAME}.s3.amazonaws.com/{file.filename}'
    })

@application.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM users;')
    users = [{'id': r[0], 'name': r[1], 'email': r[2]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(users)

if __name__ == '__main__':
    application.run(debug=False)
```

### Deployment Steps

```bash
# 1. Set up requirements.txt
echo "flask==3.0.0
psycopg2-binary==2.9.9
boto3==1.34.0" > requirements.txt

# 2. Initialize Elastic Beanstalk
eb init -p python-3.11 flask-aws-app --region us-east-1

# 3. Set environment variables (don't hardcode secrets!)
eb setenv S3_BUCKET_NAME=my-app-bucket \
          DB_HOST=my-postgres-db.xxxx.us-east-1.rds.amazonaws.com \
          DB_NAME=appdb \
          DB_USER=admin \
          DB_PASSWORD=mysecretpassword

# 4. Deploy
eb create flask-prod-env

# 5. Open in browser
eb open
```

---

## 20. Next Steps & What to Learn After This

Congratulations! You now have a solid foundation in AWS as a developer. Here is what to learn next:

### Intermediate Level (Next 3-6 Months)

| Topic | Why It Matters |
|-------|---------------|
| **DynamoDB** | AWS's NoSQL database — fast, serverless, used by large-scale apps |
| **SQS / SNS** | Message queuing and pub/sub — for decoupled, async architectures |
| **ElastiCache (Redis)** | In-memory caching to speed up database queries |
| **EKS (Kubernetes on AWS)** | Running containers at scale with Kubernetes |
| **Secrets Manager** | Safely store and rotate secrets (DB passwords, API keys) |
| **Route 53** | AWS's DNS service — map your domain to your app |
| **CloudFront** | AWS's CDN — serve your app globally with low latency |
| **WAF (Web Application Firewall)** | Protect your app from common web attacks |

### Certifications to Target

| Certification | Level | Best For |
|---------------|-------|----------|
| **AWS Cloud Practitioner** | Beginner | Understanding cloud concepts — a great first cert |
| **AWS Solutions Architect Associate** | Intermediate | Designing AWS architectures |
| **AWS Developer Associate** | Intermediate | Developing and deploying on AWS |
| **AWS DevOps Engineer Professional** | Advanced | CI/CD, automation, infrastructure at scale |

> **Recommended path for you:** Cloud Practitioner → Developer Associate

### Additional Tools for a Modern Developer

- **Terraform** — A popular open-source alternative to CloudFormation (works across AWS, Azure, GCP)
- **AWS CDK (Cloud Development Kit)** — Define AWS infrastructure using Python/TypeScript code instead of YAML
- **Docker + ECS/Fargate** — The modern way to deploy applications
- **GitHub Actions with AWS** — Popular CI/CD pipeline using GitHub Actions to deploy to AWS

---

## Quick Reference — AWS Services Cheat Sheet

| Service | Category | What It Does |
|---------|----------|--------------|
| **IAM** | Security | Users, roles, and permissions |
| **EC2** | Compute | Virtual servers |
| **Lambda** | Compute | Serverless functions |
| **Elastic Beanstalk** | Compute | Managed app deployment (PaaS) |
| **ECS / Fargate** | Containers | Run Docker containers |
| **ECR** | Containers | Private Docker image registry |
| **S3** | Storage | Object/file storage |
| **EBS** | Storage | Block storage for EC2 (hard disks) |
| **RDS** | Database | Managed relational databases |
| **DynamoDB** | Database | Managed NoSQL database |
| **ElastiCache** | Database | Managed Redis/Memcached |
| **VPC** | Networking | Private network in AWS |
| **Route 53** | Networking | DNS and domain management |
| **CloudFront** | Networking | CDN for global content delivery |
| **API Gateway** | Integration | Create and manage REST APIs |
| **SQS** | Messaging | Managed message queues |
| **SNS** | Messaging | Pub/sub notifications |
| **CloudWatch** | Monitoring | Logs, metrics, and alarms |
| **CloudFormation** | DevOps | Infrastructure as Code |
| **CodePipeline** | DevOps | CI/CD pipelines |
| **CodeBuild** | DevOps | Build and test automation |
| **CodeDeploy** | DevOps | Automated deployments |
| **Secrets Manager** | Security | Store and rotate secrets |
| **WAF** | Security | Web Application Firewall |
| **App Runner** | Containers | Simplest container deployment |
| **EKS** | Containers | Kubernetes on AWS |

---

## 21. CloudFront CDN — Deep Dive

### The Problem It Solves

Your React app's files (HTML, JS, CSS) live in one S3 bucket in, say, `us-east-1` (Virginia, USA). When a user in Mumbai opens your site, their browser has to travel all the way to Virginia to download those files. That is slow.

CloudFront fixes this by putting cached copies of your files **close to every user in the world**.

### What CloudFront Does

CloudFront has **servers (called Edge Locations) in 400+ cities worldwide** — Mumbai, London, Tokyo, São Paulo, and more. The first time someone in Mumbai visits your site, CloudFront fetches the files from your S3 bucket (the origin) and stores a copy at the nearest edge location. Every user after that in Mumbai gets the files from that local city — not Virginia.

```
Without CloudFront:
  User in Mumbai → Virginia S3 bucket     (high latency — slow)

With CloudFront:
  User in Mumbai → Mumbai Edge Location   (fast — cached copy)
  User in London → London Edge Location   (fast — cached copy)
  User in Tokyo  → Tokyo Edge Location    (fast — cached copy)
```

### Key Concepts

| Concept | What It Means |
|---|---|
| **Origin** | Where CloudFront fetches the original files from. Usually your S3 bucket or a backend server. |
| **Edge Location** | A CloudFront server in a city near the user. Caches and serves your content locally. |
| **Distribution** | A CloudFront configuration that ties an origin to all edge locations. You create one per app. |
| **Cache Invalidation** | Tells all edge locations to delete their cached copy and fetch fresh files from the origin. Run this after every deployment. |
| **TTL (Time To Live)** | How long edge locations keep the cached copy before checking the origin for a newer version. |

### How Deployment Works with S3 + CloudFront

```
1. npm run build  →  creates dist/ folder (HTML, JS, CSS)
         ↓
2. aws s3 sync dist/ s3://your-bucket  →  uploads new files to S3
         ↓
3. aws cloudfront create-invalidation  →  clears old cached files at all edge locations
         ↓
4. Next user request fetches fresh files from S3  →  caches at edge locations again
         ↓
5. All users now get the new version from their nearest city
```

### Extra Benefits

- **Free HTTPS** — CloudFront provides a free SSL certificate via AWS Certificate Manager (ACM). No manual SSL setup.
- **DDoS protection** — AWS Shield Standard is automatically included.
- **Cost savings at scale** — Edge caching reduces the number of direct requests to S3, which lowers your S3 costs.

### CloudFront vs. Serving Directly from S3

| | S3 Direct | S3 + CloudFront |
|---|---|---|
| **Latency for global users** | High | Low |
| **HTTPS** | Complicated to configure | Automatic |
| **Cost at high traffic** | Higher | Lower (caching reduces S3 reads) |
| **Custom domain support** | Limited | Full support |

> **Rule of thumb:** Always put CloudFront in front of S3 for any production app. It is faster for users everywhere and cheaper at scale.

### Simple Analogy
**S3** is the central warehouse. **CloudFront** is a network of local stores. Your users shop at the nearest local store instead of ordering from the central warehouse every single time.

---

## 22. ECS Fargate — Serverless Containers Explained

### Start with ECS

ECS (Elastic Container Service) is AWS's system for **running Docker containers**. You give it a Docker image, tell it "run this container with 1 vCPU and 512 MB RAM", and it runs it and keeps it running.

### The Problem with Raw EC2

When you run containers on EC2, you are responsible for the **virtual machine underneath** the containers too:
- Keep the OS patched and updated
- Install and configure Docker
- Monitor disk space and server health
- Handle crashes and restarts manually
- Scale by provisioning more EC2 instances yourself

You are managing two things at once — the server AND the container.

### What Fargate Changes

Fargate is ECS **without any server to manage**. You only think about your container. AWS handles the underlying machine completely invisibly.

```
ECS on EC2:                          ECS on Fargate:
  You manage:                          You manage:
  - EC2 instance (OS, disk, Docker)    - Your container only
  - Container on top of it
                                       AWS manages everything else
                                       invisibly underneath
```

### Key Concepts

| Concept | What It Means |
|---|---|
| **Task Definition** | A blueprint for your container — image URL, CPU, RAM, port, and environment variables |
| **Task** | A single running instance of a Task Definition — essentially one live container |
| **Service** | Ensures a specific number of tasks are always running. If one crashes, ECS automatically starts a replacement |
| **Cluster** | A logical group that holds your services and tasks |
| **Load Balancer** | Sits in front of your service — distributes traffic across multiple running tasks and gives you a stable public URL |

### How to Think About It

```
You define:
  Task Definition: "Run this ECR image, port 8000, 0.5 vCPU, 1 GB RAM"

You create:
  Service: "Keep 2 copies of this task running at all times"

Fargate does:
  - Finds spare capacity in AWS's infrastructure
  - Starts your containers on it
  - Monitors container health
  - Restarts containers that crash
  - Scales up/down based on your rules
```

### Fargate Pricing

You pay for the exact vCPU and memory your containers consume, billed per second. No idle server costs. Run 2 tasks × 0.5 vCPU × 1 GB RAM and you pay exactly for that, nothing more.

### When to Use Fargate

- Standard REST APIs and backend services that run 24/7
- Microservices in a growing application
- Teams without a dedicated DevOps or infrastructure engineer
- Variable traffic workloads where auto-scaling saves cost
- The vast majority of production containerized apps on AWS use Fargate

### Simple Analogy
**EC2** is renting an apartment — you manage everything inside (furniture, cleaning, repairs, utilities). **Fargate** is staying in a hotel — you just use the room, and the hotel handles all maintenance, cleaning, and security invisibly.

---

## 23. App Runner — Simplest Container Deployment

### The Problem Fargate Still Has

Even with Fargate, you configure many pieces before your container is publicly live:
- Task Definition (CPU, RAM, port, environment variables)
- ECS Cluster
- ECS Service
- Application Load Balancer
- Target Groups and Listener Rules
- Security Groups and IAM roles for the task

That is typically 15–20 setup steps before you get a public URL.

### What App Runner Does

App Runner is the **simplest way to deploy a container on AWS**. You point it at an ECR image and answer three questions:

1. Which image?
2. What port does it listen on?
3. How much CPU and RAM?

That is it. App Runner creates everything else automatically.

```
App Runner setup:
  Source:  123456789.dkr.ecr.us-east-1.amazonaws.com/gpt-app:latest
  Port:    8000
  CPU:     1 vCPU
  RAM:     2 GB

  → Done. Here is your URL:
    https://abc123xyz.us-east-1.awsapprunner.com
```

### What App Runner Handles Automatically

- Creates a load balancer and HTTPS endpoint (no manual configuration)
- Auto-scales up when traffic increases
- Scales down to near-zero when idle (saves cost)
- Restarts containers that crash
- Can watch ECR for new image pushes and redeploy automatically
- Free TLS/SSL certificate included

### App Runner vs. Fargate

| | App Runner | ECS Fargate |
|---|---|---|
| **Setup steps** | ~5 | ~20 |
| **Load balancer** | Auto-created | You configure it |
| **Auto-scaling** | Fully automatic | You define scaling rules |
| **Private VPC networking** | Optional, limited | Full control |
| **Cost at scale** | Slightly higher | Lower |
| **Best for** | Quick deploys, small teams | Production workloads needing full control |

### When to Use App Runner

- Internal tools, admin dashboards, or side projects needing a real HTTPS URL
- MVPs where speed of deployment matters more than cost optimization
- Teams with no DevOps engineer — anyone can deploy a container in minutes
- Low to medium traffic APIs

### When NOT to Use App Runner

- High-traffic production APIs where cost efficiency at scale matters
- Apps that need deep private VPC networking (talking to RDS in a private subnet, etc.)
- When you need fine-grained control over auto-scaling behavior

### Simple Analogy
**Fargate** is a fully customizable hotel suite — you configure the room layout, temperature, lighting, and services yourself. **App Runner** is an Airbnb with automatic check-in — you just show up, everything is already set up for you.

---

## 24. Production Deployment Cheat Sheet — When to Use What

As a developer, one of the most important decisions is: **where do I actually run my application in production?**

This section is a complete reference for every real option, from simplest to most complex.

### The Spectrum

```
Least control, simplest setup                    Most control, most complex
         │                                                   │
    App Runner → ECS Fargate → ECS on EC2 → EKS (K8s) → Raw EC2
         │                                                   │
   Small apps                                    Large, complex systems
```

---

### Option 1 — Raw EC2

**What it is:** A virtual machine. You install Docker yourself and run containers manually.

**Used in production?** Rarely for new projects. Seen in:
- Legacy systems built before containers were standard
- Workloads with specific low-level OS or GPU requirements

**Skip it for:** Web APIs, microservices, anything modern.

---

### Option 2 — ECS on EC2 (EC2 Launch Type)

**What it is:** ECS orchestrates your containers, but they run on EC2 instances that you provision and maintain.

**Used in production?** Yes, in specific cases:
- Need GPU (Fargate does not support GPU)
- Very large containers (Fargate max is 16 vCPU / 120 GB RAM)
- Extreme cost optimization at very high volume using EC2 Reserved Instances

**Skip it for:** Standard web APIs and services.

---

### Option 3 — Elastic Beanstalk

**What it is:** A PaaS (Platform as a Service) from AWS. You give it your application code or a Docker image and it automatically provisions EC2 instances, a load balancer, auto-scaling, and health monitoring for you. It supports both traditional code deploys (Python, Node.js, Java, Ruby, PHP, Go) and Docker (single container or multi-container via Docker Compose).

**Used in production?** Yes, and more common than people think — especially in teams that want EC2-level access without manually wiring all the infrastructure pieces.

**Use it when:**
- You are deploying a traditional web app or REST API **without Docker** (plain Python/Node.js code) — this is its strongest use case
- You want EC2-like control (you can SSH into the underlying instance, tune the OS) but without manually setting up a load balancer and auto-scaling group
- You are already using Docker but also want the ability to SSH into the server for debugging (unlike Fargate/App Runner where the underlying server is completely hidden)
- You want a quick production-grade setup with minimal AWS infrastructure knowledge
- You are migrating an existing app to AWS and want the least-friction path

**Do not use it when:**
- You want a fully serverless setup where the underlying EC2 is completely hidden — use Fargate or App Runner instead
- You need very fine-grained container orchestration across many services — use ECS Fargate or EKS

**The key difference from Fargate/App Runner:**
Beanstalk runs your containers (or code) **on EC2 instances that you can see and SSH into**. Fargate and App Runner are truly serverless — the underlying server is invisible. Choose Beanstalk when EC2-level access matters; choose Fargate/App Runner when you want zero server management.

**Elastic Beanstalk vs. the others:**

| | Elastic Beanstalk | App Runner | ECS Fargate |
|---|---|---|---|
| **Uses Docker?** | Yes (optional — also supports plain code) | Required | Required |
| **Underlying servers** | EC2 (you can SSH in) | Hidden completely | Hidden completely |
| **Setup complexity** | Low | Very low | Medium |
| **Infrastructure control** | Medium | Low | High |
| **Best for** | Quick deploys, SSH access needed, or no-Docker code | Quick container deploys, no infra management | Production containers, full control |

> **Simple analogy:** Elastic Beanstalk is a **serviced apartment** — it comes fully furnished (EC2, load balancer, auto-scaling) but you can still go in and rearrange the furniture (SSH in, change OS settings). App Runner and Fargate are **hotels** — everything is managed for you and you cannot touch the underlying infrastructure at all.

---

### Option 4 — ECS Fargate

**What it is:** Serverless containers. You define the container, AWS manages everything else.

**Used in production?** **Yes — the most common choice for containerized apps on AWS.**

**Use it when:**
- You have a standard REST API, backend service, or microservice
- Your team does not have a dedicated DevOps engineer
- Traffic is variable and you want auto-scaling without managing servers
- You want to pay only for what actually runs

**Real-world examples:** Most startups, SaaS products, REST APIs, background services.

---

### Option 5 — App Runner

**What it is:** ECS Fargate with everything pre-configured. Point at an ECR image, get a public HTTPS URL in minutes.

**Used in production?** Yes, for the right use cases.

**Use it when:**
- Internal tools, admin panels, or low-to-medium traffic APIs
- No DevOps engineer on the team
- Speed of deployment matters more than cost optimization
- Personal and side projects that still need a real HTTPS endpoint

**Do not use it when:**
- You need complex private VPC networking
- Traffic is high and cost efficiency matters
- You need fine-grained control over scaling

---

### Option 6 — EKS (Kubernetes on AWS)

**What it is:** AWS-managed Kubernetes cluster. A full container orchestration platform for running many services at scale.

**Used in production?** Yes — at large scale.

**Use it when:**
- You have 10+ microservices that need to communicate with each other
- You need advanced traffic management (canary deployments, blue/green, circuit breakers)
- You want multi-cloud portability — the same Kubernetes config works on GCP, Azure, and on-premise
- Your company has a dedicated Platform Engineering or DevOps team

**Do not use it when:** You only have one or two services. Kubernetes has serious operational overhead and a steep learning curve.

**Real-world examples:** Netflix, Airbnb, large enterprises, companies with 50+ engineers.

---

### Bonus — AWS Lambda (Serverless Functions)

Lambda is fundamentally different from all of the above. There is no container to manage and no server that stays running. Your function runs only when triggered, then shuts down completely. You pay per invocation — zero cost when idle.

**Use it for:**
- Processing files when uploaded to S3 (resize an image, parse a CSV)
- Webhook receivers (GitHub, Stripe, Slack webhooks)
- Scheduled background jobs (cron-like tasks)
- Event-driven processing triggered by SQS, SNS, or DynamoDB

**Do not use it for:**
- Long-running processes
- Streaming HTTP responses (like Server-Sent Events)
- WebSockets
- Latency-sensitive APIs (Lambda has a cold start delay on first invocation after being idle)

---

### The Full Decision Table

| Scenario | Use This |
|---|---|
| Learning or personal project | EC2 or App Runner |
| MVP or startup with 1–3 services | **ECS Fargate** |
| Traditional code deploy, no Docker, quick setup | **Elastic Beanstalk** |
| Simple API, small team, just needs to work | **App Runner** |
| Standard production microservices (with Docker) | **ECS Fargate** |
| 10+ services, dedicated infra team | **EKS (Kubernetes)** |
| Containers that need GPU (ML inference) | ECS on EC2 |
| Multi-cloud or cloud portability required | **EKS** |
| Event-driven, short-lived background tasks | **Lambda** |
| Static website or React frontend | **S3 + CloudFront** |

---

### Recommended Setup for a Typical Python/FastAPI Web App

| App Component | Recommendation | Why |
|---|---|---|
| **FastAPI backend** | **ECS Fargate** | Stays running, handles HTTP, supports streaming responses, scales automatically |
| **React frontend** | **S3 + CloudFront** | Static files need no server — S3 is near-free, CloudFront delivers files fast globally |
| **Background jobs** | **Lambda** | Event-driven tasks (send email, process an upload) run only when needed — zero idle cost |
| **Future: 10+ services** | **EKS** | Only when your architecture genuinely requires Kubernetes-level orchestration |

> **Bottom line:** Use **ECS Fargate** for your backend and **S3 + CloudFront** for your frontend. This is the standard production setup used by the majority of companies on AWS. Graduate to EKS only when the scale and complexity of your system genuinely requires it.

---

*This guide was created for Manu Sri's cloud training journey. Cover one section per day, do hands-on practice for every section, and always clean up resources after practice to avoid unexpected costs. Happy cloud learning!*
