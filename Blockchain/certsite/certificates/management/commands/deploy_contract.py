from django.core.management.base import BaseCommand
from certificates.deploy_contract import deploy_contract

class Command(BaseCommand):
    help = "Deploy CertificateVerification contract"

    def handle(self, *args, **kwargs):
        address = deploy_contract()
        self.stdout.write(self.style.SUCCESS(
            f"Contract deployed at {address}"
        ))
