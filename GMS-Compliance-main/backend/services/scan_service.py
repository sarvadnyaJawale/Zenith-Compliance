import subprocess
import os

SCAN_SCRIPT = "/home/ubuntu/GMS-Compliance/production_code/scan.sh"
S3_BUCKET = "soc2-compliance-check-reports-bucket"

def run_scan():
    """Executes scan.sh and updates scan status."""
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