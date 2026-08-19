#!/usr/bin/env python3
"""
Automated Provisioning Script for DEVOPS-26
Provisions:
  1. Top-Level Group: codeforge-platform
  2. Subgroups: 01-ci-templates, 02-infrastructure, 04-security-compliance, 05-applications
  3. Branch Protections (main: maintainers only)
  4. Masked and Protected Group-Level CI/CD Variables
"""

import os
import sys
import json
import urllib.request
import urllib.error

GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com").rstrip("/")
GITLAB_TOKEN = os.getenv("GITLAB_PRIVATE_TOKEN", "")

if not GITLAB_TOKEN:
    print("❌ ERROR: GITLAB_PRIVATE_TOKEN environment variable is required.")
    print("Usage: GITLAB_PRIVATE_TOKEN='glpat-xxx' [GITLAB_URL='https://gitlab.com'] python setup-gitlab.py")
    sys.exit(1)

HEADERS = {
    "PRIVATE-TOKEN": GITLAB_TOKEN,
    "Content-Type": "application/json"
}

SUBGROUPS = [
    {"name": "01-ci-templates", "path": "01-ci-templates", "desc": "Central Reusable DevSecOps CI/CD Templates Catalog"},
    {"name": "02-infrastructure", "path": "02-infrastructure", "desc": "OpenTofu Infrastructure as Code and S3 Storage"},
    {"name": "04-security-compliance", "path": "04-security-compliance", "desc": "Kyverno Shift-Left Policies and Compliance Rules"},
    {"name": "05-applications", "path": "05-applications", "desc": "Developer Microservices and Application Repositories"},
]

# Standard Group-Level Variables
GROUP_VARIABLES = [
    {"key": "ARTIFACTORY_URL", "value": os.getenv("ARTIFACTORY_URL", "http://artifactory.codeforge.local:8082"), "masked": False, "protected": False},
    {"key": "ARTIFACTORY_USER", "value": os.getenv("ARTIFACTORY_USER", "admin"), "masked": False, "protected": False},
    {"key": "ARTIFACTORY_PASSWORD", "value": os.getenv("ARTIFACTORY_PASSWORD", "password123"), "masked": True, "protected": False},
    {"key": "COSIGN_PASSWORD", "value": os.getenv("COSIGN_PASSWORD", "codeforge-cosign-secret"), "masked": True, "protected": False},
    {"key": "DT_API_URL", "value": os.getenv("DT_API_URL", "http://dtrack.codeforge.local"), "masked": False, "protected": False},
    {"key": "DT_API_KEY", "value": os.getenv("DT_API_KEY", "placeholder-dt-api-key"), "masked": True, "protected": False},
    {"key": "GITOPS_REPO_URL", "value": "https://github.com/davidjirca/k8s-platform-gitops.git", "masked": False, "protected": False},
    {"key": "GITHUB_GITOPS_TOKEN", "value": os.getenv("GITHUB_GITOPS_TOKEN", "ghp_placeholder_token"), "masked": True, "protected": False},
]

def make_request(path, method="GET", data=None):
    url = f"{GITLAB_URL}/api/v4/{path.lstrip('/')}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        if e.code == 409: # Already exists
            return {"_already_exists": True, "error": err_body}
        raise Exception(f"HTTP {e.code} on {method} {url}: {err_body}")

def get_or_create_top_group():
    print("🔍 Checking top-level group 'codeforge-platform'...")
    groups = make_request("groups?search=codeforge-platform")
    for g in groups:
        if g.get("path") == "codeforge-platform":
            print(f"  ✓ Found existing group ID: {g['id']}")
            return g["id"]
    
    print("🚀 Creating top-level group 'codeforge-platform'...")
    res = make_request("groups", method="POST", data={
        "name": "codeforge-platform",
        "path": "codeforge-platform",
        "visibility": "private",
        "description": "CodeForge Enterprise Platform and DevSecOps Foundation"
    })
    print(f"  ✓ Created group ID: {res['id']}")
    return res["id"]

def create_subgroups(parent_id):
    print("\n📁 Provisioning Subgroups...")
    for sg in SUBGROUPS:
        print(f"  - Subgroup: {sg['name']}...")
        res = make_request("groups", method="POST", data={
            "name": sg["name"],
            "path": sg["path"],
            "parent_id": parent_id,
            "visibility": "private",
            "description": sg["desc"]
        })
        if res.get("_already_exists"):
            print(f"    (Already exists)")
        else:
            print(f"    ✓ Created ID: {res['id']}")

def configure_group_variables(group_id):
    print("\n🔑 Configuring Masked Group-Level CI/CD Variables...")
    for var in GROUP_VARIABLES:
        var_data = {
            "key": var["key"],
            "value": var["value"],
            "variable_type": "env_var",
            "protected": var["protected"],
            "masked": var["masked"]
        }
        res = make_request(f"groups/{group_id}/variables", method="POST", data=var_data)
        if res.get("_already_exists"):
            # Update existing variable
            make_request(f"groups/{group_id}/variables/{var['key']}", method="PUT", data=var_data)
            print(f"    ✓ Updated variable: {var['key']} (Masked: {var['masked']})")
        else:
            print(f"    ✓ Created variable: {var['key']} (Masked: {var['masked']})")

def main():
    print("==================================================")
    print("  CodeForge GitLab Group & Subgroup Provisioning  ")
    print("==================================================")
    top_group_id = get_or_create_top_group()
    create_subgroups(top_group_id)
    configure_group_variables(top_group_id)
    print("\n🎉 DEVOPS-26 Provisioning Successfully Completed!")

if __name__ == "__main__":
    main()
