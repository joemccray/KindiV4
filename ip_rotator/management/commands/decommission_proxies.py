from django.core.management.base import BaseCommand, CommandError

from ip_rotator import services


class Command(BaseCommand):
    help = "Decommissions AWS API Gateway proxies for a given list of proxy IDs."

    def add_arguments(self, parser):
        parser.add_argument(
            "proxy_ids",
            nargs="+",
            type=str,
            help="A space-separated list of proxy IDs (UUIDs) to decommission.",
        )

    def handle(self, *args, **options):
        proxy_ids = options["proxy_ids"]

        self.stdout.write(f"Starting decommissioning for {len(proxy_ids)} proxies...")

        try:
            services.decommission_gateways(proxy_ids)
            self.stdout.write(
                self.style.SUCCESS(
                    "Decommissioning process completed. Check logs for details on each proxy."
                )
            )
        except Exception as e:
            raise CommandError(f"An error occurred during decommissioning: {e}") from e
