# Set Up Project Locally

This step gets the project ready on your machine and prepares Pulumi state.

## 1) Get the Project

Clone the repository and enter the directory:

```bash
git clone <your-repo-url> container-reconcile
cd container-reconcile
```

If the project is already on disk, just `cd` into it.

## 2) Create and Activate Virtual Environment

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3) Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `pulumi`
- `pulumi-proxmoxve`
- `PyYAML`
- `requests`

## 4) Login to a Pulumi Backend

Choose one:

### Pulumi Cloud backend

```bash
pulumi login
```

### Local backend

```bash
pulumi login --local
```

## 5) Create or Select a Stack

If this is your first run:

```bash
pulumi stack init dev
```

If stack already exists:

```bash
pulumi stack select dev
```

## 6) Verify You Are in the Right Place

Run:

```bash
pulumi stack
```

Expected:

- a selected stack (for example `dev`)
- command works from this project directory (where `Pulumi.yaml` exists)

## Next Step

Continue with [Configure Pulumi and Proxmox Access](04-configure-pulumi.md).

