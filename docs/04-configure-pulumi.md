# Configure Pulumi and Proxmox Access

This project reads configuration from Pulumi config values.

## 1) Required Provider Configuration

At minimum, set:

- `proxmoxve:endpoint`
- one authentication method

### Option A (Recommended): API Token

```bash
pulumi config set proxmoxve:endpoint https://proxmox.example.internal:8006
pulumi config set --secret proxmoxve:apiToken 'root@pam!pulumi=TOKEN_SECRET'
```

### Option B: Username + Password

```bash
pulumi config set proxmoxve:endpoint https://proxmox.example.internal:8006
pulumi config set proxmoxve:username root@pam
pulumi config set --secret proxmoxve:password 'YOUR_PASSWORD'
```

### Option C: Auth Ticket (+ optional CSRF token)

```bash
pulumi config set proxmoxve:endpoint https://proxmox.example.internal:8006
pulumi config set --secret proxmoxve:authTicket 'YOUR_AUTH_TICKET'
pulumi config set --secret proxmoxve:csrfPreventionToken 'YOUR_CSRF_TOKEN'
```

For self-signed TLS certs:

```bash
pulumi config set proxmoxve:insecure true
```

## 2) Program Configuration

The input YAML file path:

```bash
pulumi config set container-reconcile:containersFile containers.yaml
```

If not set, default is `containers.yaml`.

## 3) Optional App Overrides for Next-ID API

Normally the app uses `proxmoxve:*` values directly. You can override next-id API settings with:

- `container-reconcile:proxmoxEndpoint`
- `container-reconcile:proxmoxInsecure`
- `container-reconcile:proxmoxApiToken`
- `container-reconcile:proxmoxUsername`
- `container-reconcile:proxmoxPassword`
- `container-reconcile:proxmoxOtp`
- `container-reconcile:proxmoxAuthTicket`
- `container-reconcile:proxmoxCsrfToken`

Use `--secret` for sensitive values:

```bash
pulumi config set --secret container-reconcile:proxmoxApiToken 'root@pam!pulumi=TOKEN_SECRET'
```

## 4) Verify Config

Run:

```bash
pulumi config
```

You should see endpoint values and masked secret entries.

## 5) Important Behavior Note

If any container omits `vm_id`, this app calls Proxmox `cluster/nextid` before creating resources.  
That call requires valid endpoint/auth config.

## Next Step

Continue with [Write `containers.yaml`](05-write-containers-yaml.md).

