# Project explanation video link
https://drive.google.com/file/d/1nIo55DqH4vyDurr1q0SPI2ZTZxEkbHI1/view?usp=sharing

# Tech Stack intergrated : 
    IAM + EKS + SSM(AWS System Manager Parameter Store) + S3 + CloudFront + DynamoDB + Jira + Terraform + CICD pipeline (GITHUB Action)

# Developing-for-the-cloud-Project
    Go to CICD pipeline action 

    Choose “Run Workflow.” After entering the workflow, there are three execution options: Apply, Destroy, and Bootstrap.

    Choose option bootstrap first to execute bootstrap configuration on pipeline for connecting remote state 
    from your local project to the AWS to store the tfstate insine the s3 

    Then choose option apply to apply everything about project execution

    Finally, choose destroy to clean up the infrastructure in AWS along with bootstrap
    
    Sometimes VPC can not delete due to ENI issue so go to the AWS console to manual delete it 




Use your own IAM access key to access your AWS and region (or you can use us-east-1 that i am using)

# ${{ secrets.AWS_ACCESS_KEY_ID }}

# ${{ secrets.AWS_SECRET_ACCESS_KEY }}

# ${{ vars.AWS_REGION }}

DOCKER REGISTRY SECRET:
# $ {{ secrets.DOCKER_TOKEN }}
# $ {{ secrets.DOCKER_USERNAME }}



use your own jira acccount to fulfill these vars and secrets:

# ${{ vars.JIRA_BASE_URL}}

# ${{ secrets.JIRA_EMAIL }}

# ${{ secrets.JIRA_API_TOKEN }}

# ${{ vars.PROJECT_KEY }}

secret EKS_CLUSTER_NAME must be cloud-incident-system-eks : name ${{ secrets.EKS_CLUSTER_NAME }}
