from django.core.management.base import BaseCommand

from people_search import services


class Command(BaseCommand):
    help = "Polls for the results of any pending People Search queries."

    def handle(self, *args, **options):
        self.stdout.write("Starting to poll for pending search results...")

        try:
            result_message = services.poll_and_process_results()
            self.stdout.write(self.style.SUCCESS(f"Polling finished. {result_message}"))
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"An unexpected error occurred during polling: {e}")
            )
