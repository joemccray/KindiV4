from django.core.management.base import BaseCommand, CommandError

from ip_rotator import services


class Command(BaseCommand):
    help = "Provisions AWS API Gateway proxies for a given target site in specified regions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--site",
            type=str,
            required=True,
            help="The target site base URL (e.g., https://api.example.com)",
        )
        parser.add_argument(
            "--regions",
            nargs="+",
            type=str,
            required=True,
            help="A space-separated list of AWS regions (e.g., us-east-1 eu-west-2)",
        )

    def handle(self, *args, **options):
        site = options["site"]
        regions = options["regions"]

        self.stdout.write(
            f"Starting provisioning for site '{site}' in regions: {', '.join(regions)}..."
        )

        try:
            created_proxies = services.provision_gateways(site, regions)
            if created_proxies:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully provisioned or verified {len(created_proxies)} proxies."
                    )
                )
                for proxy in created_proxies:
                    self.stdout.write(
                        f"  - Region: {proxy.aws_region}, Endpoint: {proxy.endpoint_url}"
                    )
            else:
                self.stdout.write(
                    self.style.WARNING("No new proxies were provisioned.")
                )
        except Exception as e:
            raise CommandError(f"An error occurred during provisioning: {e}") from e
