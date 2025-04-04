from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import subprocess
import time
import threading
import json
import os

app = FastAPI()

SCAN_SCRIPT = "/home/ubuntu/GMS-Compliance/production_code/scan.sh"
S3_BUCKET = "soc2-compliance-check-reports-bucket"
SCAN_STATUS = {"running": False, "s3_link": None}

# Required IAM policies
REQUIRED_POLICIES = {
    "arn:aws:iam::aws:policy/SecurityAudit",
    "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess",
    "arn:aws:iam::aws:policy/AdministratorAccess",
    "arn:aws:iam::aws:policy/PowerUserAccess"
}

# 🟠 Updated HTML Form with Loader & Real-time Progress
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>AWS Compliance Scanner</title>
    <script>
        function checkScanStatus() {
            fetch('/scan-status')
            .then(response => response.json())
            .then(data => {
                if (data.running) {
                    document.getElementById('status').innerHTML = "⏳ Scanning in progress... Please wait.";
                    setTimeout(checkScanStatus, 5000);
                } else if (data.s3_link) {
                    document.getElementById('status').innerHTML = "✅ Scan completed! <br><a href='" + data.s3_link + "' target='_blank'>Download Report</a>";
                } else {
                    document.getElementById('status').innerHTML = "⚠️ No scan is running.";
                }
            });
        }
    </script>
</head>
<body onload="checkScanStatus()">
    <h2>AWS Compliance Scanner</h2>
    <form action="/configure-aws" method="post">
        <label>AWS Access Key:</label>
        <input type="text" name="aws_access_key" required><br><br>

        <label>AWS Secret Key:</label>
        <input type="password" name="aws_secret_key" required><br><br>

        <label>AWS Region:</label>
        <input type="text" name="aws_region" placeholder="us-east-1" required><br><br>

        <input type="submit" value="Configure & Start Scan">
    </form>

    <h3 id="status">Checking scan status...</h3>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_FORM

@app.get("/scan-status")
def scan_status():
    return SCAN_STATUS

def get_iam_username():
    """Fetch IAM username from AWS CLI"""
    try:
        result = subprocess.run(
            ["aws", "iam", "get-user"],
            capture_output=True,
            text=True,
            check=True
        )
        user_data = json.loads(result.stdout)
        return user_data["User"]["UserName"]
    except Exception as e:
        return {"error": f"⚠️ Error fetching IAM username: {str(e)}"}

def check_iam_permissions():
    """Check if the IAM user has BOTH SecurityAudit and ViewOnlyAccess permissions."""
    try:
        # 🔹 Step 1: Get the current IAM user ARN
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--query", "Arn", "--output", "text"],
            capture_output=True,
            text=True,
            check=True
        )
        iam_arn = result.stdout.strip()

        # 🔹 Step 2: Extract the username from the ARN
        iam_user = iam_arn.split("/")[-1]

        # 🔹 Step 3: List attached policies for the user
        policies = subprocess.run(
            ["aws", "iam", "list-attached-user-policies", "--user-name", iam_user, "--query", "AttachedPolicies[*].PolicyArn", "--output", "json"],
            capture_output=True,
            text=True,
            check=True
        )

        if policies.returncode != 0:
            return {"error": f"⚠️ Error checking IAM permissions: {policies.stderr}"}

        attached_policies = json.loads(policies.stdout)

        # 🔹 Required policies (both must be attached)
        required_policies = {
            "arn:aws:iam::aws:policy/SecurityAudit",
            "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess"
        }

        # 🔹 Check if BOTH required policies are attached
        if required_policies.issubset(set(attached_policies)):
            return {"message": "✅ IAM permissions verified successfully! Both required policies are attached."}
        else:
            return {
                "error": "⚠️ Insufficient IAM permissions! The IAM user must have BOTH 'SecurityAudit' and 'ViewOnlyAccess' permissions."
            }

    except subprocess.CalledProcessError as e:
        return {"error": f"⚠️ Error checking IAM permissions: {e.stderr}"}
    except json.JSONDecodeError:
        return {"error": "⚠️ Failed to parse IAM policy response. Please check your AWS credentials."}

def run_scan():
    """Executes .sh and updates scan status."""
    global SCAN_STATUS
    SCAN_STATUS["running"] = True
    SCAN_STATUS["s3_link"] = None

    try:
        if not os.path.exists(SCAN_SCRIPT):
            SCAN_STATUS["s3_link"] = "⚠️ Scan script not found!"
            return
        
        subprocess.run(["chmod", "+x", SCAN_SCRIPT])

        # 🔹 Run the scan script
        result = subprocess.run(["bash", SCAN_SCRIPT], capture_output=True, text=True)

        if result.returncode != 0:
            SCAN_STATUS["s3_link"] = f"⚠️ Scan failed: {result.stderr}"
            return

        # 🔹 Extract S3 link from scan logs (assuming file is named output_reports.tar.gz)
        s3_link = f"https://{S3_BUCKET}.s3.amazonaws.com/output_reports.tar.gz"
        SCAN_STATUS["s3_link"] = s3_link

    except Exception as e:
        SCAN_STATUS["s3_link"] = f"⚠️ Scan failed: {str(e)}"

    finally:
        SCAN_STATUS["running"] = False

@app.post("/configure-aws")
def configure_aws(aws_access_key: str = Form(...), aws_secret_key: str = Form(...), aws_region: str = Form(...)):
    """Configures AWS CLI and checks IAM permissions before running the scan."""
    try:
        # Configure AWS CLI
        subprocess.run(["aws", "configure", "set", "aws_access_key_id", aws_access_key], check=True)
        subprocess.run(["aws", "configure", "set", "aws_secret_access_key", aws_secret_key], check=True)
        subprocess.run(["aws", "configure", "set", "region", aws_region], check=True)

        # 🔹 Check IAM Permissions
        permissions_check = check_iam_permissions()
        if "error" in permissions_check:
            return permissions_check  # Return error if IAM user lacks permissions

        # 🔹 Start Compliance Scan in Background
        threading.Thread(target=run_scan, daemon=True).start()

        return {"message": "✅ AWS credentials configured successfully! Scan started. Check status on the main page."}

    except subprocess.CalledProcessError as e:
        return {"error": f"⚠️ Command failed: {e}", "stderr": e.stderr}