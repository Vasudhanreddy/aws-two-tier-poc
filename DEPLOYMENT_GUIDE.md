Two-Tier POC Deployment Guide - Updated
This guide reflects the changes to deploy a functional Python/Flask backend on the EC2 instance that connects to the private RDS database for user persistence.

1. Deploying the AWS Infrastructure (CloudFormation)
The updated poc-infra.yaml now provisions:

VPC: Two Public and two Private Subnets across two AZs.

NAT Gateway: For private subnet outbound access.

EC2 Instance: Running a Python/Flask application on port 80.

IAM Role: Attached to the EC2 instance for security best practices.

RDS PostgreSQL: In the private subnet, only accessible from the EC2 instance's security group.

Deployment Steps:

Prepare: Ensure you have an existing EC2 Key Pair created in the target region.

AWS Console: Navigate to the CloudFormation service.

Create Stack: Upload the latest poc-infra.yaml file.

Specify Details:

Stack name: MyWebAppPOC-Backend

Parameters: Provide your desired DBPassword and select the KeyName of your EC2 Key Pair. Note the new DBName parameter is set to pocdb.

Deploy: Acknowledge the IAM creation and click "Create Stack".

Wait Time: Deployment usually takes 15-25 minutes (due to NAT Gateway and RDS provisioning).

2. Testing the Functional PoC
Once the stack status is CREATE_COMPLETE:

Retrieve Public IP: Go to the Outputs tab of your new CloudFormation stack and copy the WebInstancePublicIP.

Access the Application: Open the http://<WebInstancePublicIP> in your browser.

Signup Test:

Click "Need an account? Sign Up".

Enter an email and a password (min 8 chars).

Click "Create Account".

Expected Result: You should see a green success message and be switched to the Login screen. The user account is now stored in the RDS database.

Login Test:

Use the email and password you just created.

Click "Log In".

Expected Result: You should see a green "Login successful" message.

If the application is not immediately available, wait a few minutes for the EC2 UserData script to finish installing Python, dependencies, and starting the gunicorn service.

Next Steps (Preparing for CI/CD)
The current setup uses UserData to embed the application logic. For CI/CD, you would replace the file creation steps in UserData with a build process that:

Pulls the code from GitHub (app.py, index.html, requirements.txt).

Builds the environment.

Starts the application.

We can now move on to creating the CI/CD pipeline to automate deployment from your GitHub repository!