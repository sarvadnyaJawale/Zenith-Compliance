from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import subprocess
import time
import threading
import os

# To run this application, do "uvicorn app:app --host 0.0.0.0 --port 8000" application will be live on 8000

app = FastAPI()

SCAN_SCRIPT = "/home/ubuntu/GMS-Compliance/production_code/scan.sh"  # Path to scan.sh
S3_BUCKET = "soc2-compliance-check-reports-bucket"
SCAN_STATUS = {"running": False, "s3_link": None}


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
    """Returns the HTML page to enter AWS credentials and track scanning progress."""
    return HTML_FORM


@app.get("/scan-status")
def scan_status():
    """Returns the current scan status."""
    return SCAN_STATUS


def run_scan():
    """Executes scan.sh and updates scan status."""
    global SCAN_STATUS
    SCAN_STATUS["running"] = True
    SCAN_STATUS["s3_link"] = None

    try:
        # 🔹 Ensure the scan script is executable
        if not os.path.exists(SCAN_SCRIPT):
            SCAN_STATUS["s3_link"] = "⚠️ Scan script not found!"
            return
        subprocess.run(["chmod", "+x", SCAN_SCRIPT])  # Make sure it's executable

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
    """Configures AWS CLI with user-provided credentials and starts the compliance scan in a separate thread."""
    try:
        # 🔹 Step 1: Configure AWS CLI with User Credentials
        subprocess.run(["aws", "configure", "set", "aws_access_key_id", aws_access_key], check=True)
        subprocess.run(["aws", "configure", "set", "aws_secret_access_key", aws_secret_key], check=True)
        subprocess.run(["aws", "configure", "set", "region", aws_region], check=True)

        # 🔹 Step 2: Start Compliance Scan in Background
        threading.Thread(target=run_scan, daemon=True).start()

        return {"message": "AWS credentials configured successfully! Scan started. Check status on the main page."}

    except subprocess.CalledProcessError as e:
        return {"error": f"Command failed: {e}", "stderr": e.stderr}


