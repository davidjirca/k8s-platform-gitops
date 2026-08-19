# GitLab Platform Provisioning (DEVOPS-25 & DEVOPS-26)

This directory contains automated tooling to provision the **`codeforge-platform`** GitLab enterprise group hierarchy, subgroups, and group-level masked CI/CD variables.

---

## 🏗️ Structure Provisioned

```text
codeforge-platform (Top-Level Group)
├── 01-ci-templates/          (Reusable DevSecOps CI/CD Templates Catalog)
├── 02-infrastructure/        (OpenTofu IaC & S3 Storage)
├── 04-security-compliance/   (Kyverno Shift-Left CI Policies)
└── 05-applications/          (Developer Microservices)
```

---

## 🚀 Execution Guide

### Prerequisites
* A Personal Access Token (PAT) or Group Token with `api` and `create_runner` scopes from your GitLab instance (e.g. `https://gitlab.com` or self-hosted).

### Run the Provisioning Script
```bash
# For GitLab.com
export GITLAB_PRIVATE_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
python scripts/gitlab-setup/setup-gitlab.py

# For Self-Hosted GitLab (optional URL override)
export GITLAB_URL="https://gitlab.codeforge.local"
export GITLAB_PRIVATE_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
python scripts/gitlab-setup/setup-gitlab.py
```

---

## 🔑 Configured Group-Level CI/CD Variables

| Variable Key | Type | Description |
| :--- | :---: | :--- |
| `ARTIFACTORY_URL` | String | Internal OCI container registry URL (`http://artifactory.codeforge.local:8082`) |
| `ARTIFACTORY_USER` | String | Registry authentication username |
| `ARTIFACTORY_PASSWORD` | Masked | Registry authentication password / API token |
| `COSIGN_PASSWORD` | Masked | Cryptographic password for Cosign container signing |
| `DT_API_URL` | String | Dependency-Track API URL (`http://dtrack.codeforge.local`) |
| `DT_API_KEY` | Masked | Ingestion API key for Dependency-Track SBOM upload |
| `GITOPS_REPO_URL` | String | Target GitOps repository (`https://github.com/davidjirca/k8s-platform-gitops.git`) |
| `GITHUB_GITOPS_TOKEN` | Masked | GitHub PAT with write access to commit automated image tag bumps |
