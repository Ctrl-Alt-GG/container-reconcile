# Preview and Deploy

After config and `containers.yaml` are ready, use Pulumi to preview and apply changes.

## 1) Preview Changes

```bash
pulumi preview
```

What to look for:

- resources of type `proxmoxve:CT:Container`
- expected create/update/delete actions
- no validation/auth errors

## 2) Deploy

```bash
pulumi up
```

When prompted, confirm the update if it matches expectations.

## 3) Check Outputs

After a successful run:

```bash
pulumi stack output
```

Expected outputs include:

- `yaml_file`
- `container_count`
- `container_names`
- `container_vm_ids`
- `container_hosts`

## 4) Verify in Proxmox

In Proxmox UI, confirm:

- containers were created on expected node(s),
- VM IDs match expected values,
- network and resource sizing look correct.

## 5) Update Workflow

To change containers:

1. Edit `containers.yaml`
2. Run:

```bash
pulumi preview
pulumi up
```

Pulumi will apply only the diff.

## 6) Delete Workflow

### Delete one or more containers from this project

- Remove them from `containers.yaml`
- Run:

```bash
pulumi preview
pulumi up
```

Pulumi will destroy resources no longer declared.

### Destroy everything in the stack

```bash
pulumi destroy
```

## Next Step

If something fails, use [Troubleshooting](07-troubleshooting.md).

