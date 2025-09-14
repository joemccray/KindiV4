from django.core.management.base import BaseCommand

from people_search import services


class Command(BaseCommand):
    help = "Triggers Celery tasks to poll for pending People Search queries."

    def handle(self, *args, **options):
        self.stdout.write("Triggering Celery tasks for all pending searches...")

        try:
            result_message = services.trigger_poll_for_all_searches()
            self.stdout.write(self.style.SUCCESS(result_message))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
