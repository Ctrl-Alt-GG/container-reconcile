# Start Here

This guide set helps you go from a machine with Git and Python already installed to running `pulumi up` and creating Proxmox LXC containers.

## What You Will Achieve

By the end, you will:

- Install and verify Pulumi CLI.
- Configure Proxmox API access for this project.
- Define `hosts` and `containers` in `containers.yaml`.
- Preview and deploy containers with Pulumi.

## Guide Order

1. [Install Prerequisites](01-install-prerequisites.md)
2. [Prepare Proxmox VE](02-prepare-proxmox.md)
3. [Set Up Project Locally](03-setup-project.md)
4. [Configure Pulumi and Proxmox Access](04-configure-pulumi.md)
5. [Write `containers.yaml`](05-write-containers-yaml.md)
6. [Preview and Deploy](06-preview-and-deploy.md)
7. [Troubleshooting](07-troubleshooting.md)

## Before You Start

Make sure you already have:

- Git installed.
- Python 3.10+ installed.
- Access to a Proxmox VE environment where you are allowed to create containers.

