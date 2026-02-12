from container_reconcile.domain.models import ContainerSpec, DeploymentSpec, HostSpec


def test_hosts_with_missing_vm_ids_returns_aliases(
    sample_deployment_spec: DeploymentSpec,
) -> None:
    assert sample_deployment_spec.hosts_with_missing_vm_ids() == {"hostA"}


def test_hosts_with_missing_vm_ids_returns_empty_when_all_set(
    sample_host: HostSpec,
    sample_container: ContainerSpec,
) -> None:
    spec = DeploymentSpec(hosts={"hostA": sample_host}, containers=[sample_container])
    assert spec.hosts_with_missing_vm_ids() == set()


def test_hosts_with_missing_vm_ids_returns_empty_for_no_containers(
    sample_host: HostSpec,
) -> None:
    spec = DeploymentSpec(hosts={"hostA": sample_host}, containers=[])
    assert spec.hosts_with_missing_vm_ids() == set()


def test_containers_for_host_filters_correctly(
    sample_deployment_spec: DeploymentSpec,
) -> None:
    result = sample_deployment_spec.containers_for_host("hostA")
    assert len(result) == 2
    assert all(c.host == "hostA" for c in result)
    assert sample_deployment_spec.containers_for_host("unknown") == []

