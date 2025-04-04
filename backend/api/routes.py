
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from backend.services.scan_service import run_scan
from backend.services.aws_service import configure_aws
TEMPLATE_PATH = "/home/ubuntu/GMS-Compliance/frontend/templates/index.html"
SCAN_SCRIPT = "/home/ubuntu/GMS-Compliance/production_code/scan.sh"
S3_BUCKET = "soc2-compliance-check-reports-bucket"
import threading
import os 
import subprocess

router = APIRouter()

SCAN_STATUS = {"running": False, "s3_link": None}

def load_html():
    """Reads the HTML file and returns its contents."""
    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "<h1>Error: Template file not found!</h1>"

@router.get("/", response_class=HTMLResponse)
def home():
    """Returns the HTML page to enter AWS credentials and track scanning progress."""
    return HTMLResponse(content=load_html(), status_code=200)

@router.get("/scan-status")
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


@router.post("/configure-aws")
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