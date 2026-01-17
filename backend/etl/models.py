from django.db import models


class ETLRun(models.Model):
    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    run_id = models.BigAutoField(primary_key=True)
    source = models.CharField(max_length=64)  # e.g. "csv", "mock_api"
    job_name = models.CharField(max_length=128)  # e.g. "load_orders"
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RUNNING)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    rows_extracted = models.IntegerField(default=0)
    rows_loaded = models.IntegerField(default=0)

    error_message = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "etl_runs"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["job_name"]),
            models.Index(fields=["started_at"]),
        ]

    def __str__(self):
        return f"{self.job_name} ({self.status})"
