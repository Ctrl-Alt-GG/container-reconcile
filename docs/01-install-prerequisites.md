# Install Prerequisites

This project assumes Git and Python are already installed. In this step, install Pulumi CLI and verify the toolchain.

## 1) Verify Existing Tools

Run:

```bash
git --version
python --version
```

Expected:

- Git returns a version string.
- Python returns `3.10` or newer.

## 2) Install Pulumi CLI

Install Pulumi CLI using your OS flow.

### Linux / macOS

```bash
curl -fsSL https://get.pulumi.com | sh
```

If `pulumi` is still not found, add Pulumi to `PATH` for your current shell:

```bash
export PATH="$PATH:$HOME/.pulumi/bin"
```

### Windows (PowerShell)

```powershell
iwr https://get.pulumi.com/install.ps1 -useb | iex
```

## 3) Verify Pulumi Installation

Run:

```bash
pulumi version
```

Expected:

- A Pulumi version string is printed.

## Next Step

Continue with [Prepare Proxmox VE](02-prepare-proxmox.md).

