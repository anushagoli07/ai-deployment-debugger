import boto3
import os
import subprocess
import base64
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
ECR_REPO_NAME = "ai-deployment-debugger"
IMAGE_TAG = "latest"
SERVICE_NAME = "ai-debugger-service"

def execute_cmd(cmd):
    print(f"Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error Output: {result.stderr}")
        raise Exception(f"Command failed with exit code {result.returncode}")
    return result.stdout.strip()

def deploy():
    print("[*] Initiating Cloud Deployment for AI Debugger...")
    
    sts = boto3.client('sts', region_name=REGION)
    try:
        account_id = sts.get_caller_identity()['Account']
    except Exception as e:
        print("[-] AWS Credentials not found or invalid.")
        return

    ecr = boto3.client('ecr', region_name=REGION)
    
    # 1. Create ECR Repo if not exists
    try:
        ecr.describe_repositories(repositoryNames=[ECR_REPO_NAME])
        print(f"[+] ECR repository '{ECR_REPO_NAME}' already exists.")
    except ecr.exceptions.RepositoryNotFoundException:
        print(f"[*] Creating ECR repository '{ECR_REPO_NAME}'...")
        ecr.create_repository(repositoryName=ECR_REPO_NAME)
        
    ecr_uri = f"{account_id}.dkr.ecr.{REGION}.amazonaws.com/{ECR_REPO_NAME}"
    full_image_name = f"{ecr_uri}:{IMAGE_TAG}"
    
    # 2. Authenticate Docker to ECR via Boto3 (No AWS CLI needed)
    print("[*] Authenticating Docker with ECR...")
    try:
        auth_response = ecr.get_authorization_token()
        auth_data = auth_response['authorizationData'][0]
        token = auth_data['authorizationToken']
        decoded_token = base64.b64decode(token).decode('utf-8')
        password = decoded_token.split(':')[1]
        
        login_cmd = f"docker login --username AWS --password {password} {auth_data['proxyEndpoint']}"
        execute_cmd(login_cmd)
        print("[+] Docker authenticated.")
    except Exception as e:
        print(f"[-] Docker authentication failed: {e}")
        return
    
    # 3. Build & Push
    print("[*] Building Docker image...")
    try:
        execute_cmd(f"docker build -t {ECR_REPO_NAME} .")
        execute_cmd(f"docker tag {ECR_REPO_NAME}:{IMAGE_TAG} {full_image_name}")
        execute_cmd(f"docker push {full_image_name}")
        print("[+] Image pushed to ECR.")
    except Exception as e:
        print(f"[-] Build/Push failed: {e}")
        return
    
    # 4. Deploy to AppRunner
    print("[*] Deploying to AWS AppRunner...")
    apprunner = boto3.client('apprunner', region_name=REGION)
    
    # Check if service exists
    services = apprunner.list_services()
    service_arn = next((s['ServiceArn'] for s in services.get('ServiceSummaryList', []) if s['ServiceName'] == SERVICE_NAME), None)
    
    source_config = {
        'ImageRepository': {
            'ImageIdentifier': full_image_name,
            'ImageConfiguration': {
                'Port': '8080',
                'RuntimeEnvironmentVariables': {
                    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', '')
                }
            },
            'ImageRepositoryType': 'ECR'
        },
        'AutoDeploymentsEnabled': True
    }
    
    # Attempt to get IAM role for ECR access
    iam = boto3.client('iam')
    try:
        role = iam.get_role(RoleName='AppRunnerECRAccessRole')
        source_config['AuthenticationConfiguration'] = {'AccessRoleArn': role['Role']['Arn']}
    except:
        print("[!] Warning: AppRunnerECRAccessRole not found.")

    try:
        if service_arn:
            apprunner.update_service(ServiceArn=service_arn, SourceConfiguration=source_config)
            print("[+] Service update initiated.")
        else:
            response = apprunner.create_service(
                ServiceName=SERVICE_NAME,
                SourceConfiguration=source_config,
                InstanceConfiguration={'Cpu': '1 vCPU', 'Memory': '2 GB'}
            )
            service_arn = response['Service']['ServiceArn']
            print("[+] Service creation initiated.")
        
        print(f"\n[🚀] Deployment is rolling out!\nService ARN: {service_arn}")
    except Exception as e:
        print(f"[-] AppRunner failed: {e}")

if __name__ == "__main__":
    deploy()
