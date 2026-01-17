from rest_framework import serializers
from etl.models import ETLRun


class ETLRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETLRun
        fields = [
            "run_id",
            "source",
            "job_name",
            "status",
            "started_at",
            "finished_at",
            "rows_extracted",
            "rows_loaded",
            "error_message",
        ]
