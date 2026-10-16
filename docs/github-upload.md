# GitHub Upload

## Create the remote repository

Create a new empty GitHub repository named `sentinel-uas-assurance-lab`. Do not initialize it with another README, license, or `.gitignore` because those files already exist here.

## Push from Windows PowerShell

Open PowerShell inside the extracted project folder:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "Initial UAS assurance lab"
git remote add origin https://github.com/YOUR-USERNAME/sentinel-uas-assurance-lab.git
git push -u origin main
```

Replace `YOUR-USERNAME` with the new GitHub username.

## Before pushing

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python tools\validate_repository.py
python tools\check_traceability.py
pytest --cov=sentinel_uas --cov-report=term-missing
```

The `.gitignore` excludes the virtual environment, local secrets, caches, browser artifacts, and local reports.

## Repository settings worth enabling

- Default branch: `main`.
- Private vulnerability reporting.
- Dependabot alerts and security updates.
- Secret scanning when available for the account.
- Branch protection after the first successful Actions run: require CI and Security checks before merge.

Do not upload `.env`, real credentials, real UAS data, employer-confidential information, or operational locations.
