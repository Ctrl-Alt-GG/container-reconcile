from container_reconcile.domain.models import ContainerSpec, DeploymentSpec, HostSpec


def test_has_missing_vm_ids_returns_true_when_any_container_missing(
    sample_deployment_spec: DeploymentSpec,
) -> None:
    assert sample_deployment_spec.has_missing_vm_ids() is True


def test_has_missing_vm_ids_returns_false_when_all_containers_have_vm_id(
    sample_host: HostSpec,
    sample_container: ContainerSpec,
) -> None:
    spec = DeploymentSpec(hosts={"hostA": sample_host}, containers=[sample_container])
    assert spec.has_missing_vm_ids() is False


def test_has_missing_vm_ids_returns_false_for_empty_container_list(
    sample_host: HostSpec,
) -> None:
    spec = DeploymentSpec(hosts={"hostA": sample_host}, containers=[])
    assert spec.has_missing_vm_ids() is False

