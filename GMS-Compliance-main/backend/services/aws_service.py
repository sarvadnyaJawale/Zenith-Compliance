import subprocess
from backend.services.iam_service import check_iam_permissions
from fastapi import Form
from backend.services.scan_service import run_scan
import threading

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