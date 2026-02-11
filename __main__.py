import pulumi

from container_reconcile.domain.errors import SpecError
from container_reconcile.infrastructure.config_reader import ConfigReader
from container_reconcile.infrastructure.spec_loader import SpecLoader
from container_reconcile.services.container_args_factory import ContainerArgsFactory
from container_reconcile.services.deployment_service import DeploymentService
from container_reconcile.services.spec_service import SpecService


def main() -> None:
    deployment_service = DeploymentService(
        config_reader=ConfigReader(),
        spec_loader=SpecLoader(),
        spec_service=SpecService(),
        args_factory=ContainerArgsFactory(),
    )

    try:
        deployment_service.run()
    except SpecError as exc:
        raise pulumi.RunError(str(exc)) from exc


main()

