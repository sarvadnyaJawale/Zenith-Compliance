#!/bin/bash

# Set variables
JSON_REPORT="report"
OUTPUT_DIR="output_reports"
S3_BUCKET="soc2-compliance-check-reports-bucket"

# Step 1: Run Prowler and generate JSON report
echo "Running Prowler for compliance checks..."
prowler aws -M json-ocsf -F $JSON_REPORT -o /home/ubuntu

# Step 2: Convert JSON to PDF
echo "Generating compliance reports..."
python3 convert_to_pdf.py $JSON_REPORT.ocsf.json

# Step 3: Compress output_reports directory
echo "Compressing report."
tar -czf output_reports.tar.gz $OUTPUT_DIR

# Step 4: Upload to S3
echo "Uploading reports to S3..."
aws s3 cp output_reports.tar.gz s3://$S3_BUCKET/

# Step 5: Cleanup (Optional)
echo "Cleaning up local files..."
rm -rf $OUTPUT_DIR output_reports.tar.gz $JSON_REPORT.ocsf.json compliance

# Step 6: Notify user
echo "Compliance reports have been generated and uploaded to S3!"
