import subprocess
import json

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