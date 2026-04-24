"""Tests for CronService."""

from unittest.mock import MagicMock

from postgres_dba.commands.cron import CronService
from postgres_dba.models.postgres.pg_cron import CronJob, CronJobRunDetail, CronRunStatus

_SAMPLE_JOBS = [
    CronJob(
        database="postgres",
        user="postgres",
        active=True,
        job_id=1,
        name="vacuum",
        schedule="0 * * * *",
        command="VACUUM",
    ),
    CronJob(
        database="postgres",
        user="postgres",
        active=False,
        job_id=2,
        name="analyze",
        schedule="30 * * * *",
        command="ANALYZE",
    ),
]

_SAMPLE_RUN_DETAILS = [
    CronJobRunDetail(
        start="2026-01-01 00:00:00 UTC",
        end="2026-01-01 00:00:01 UTC",
        name="vacuum",
        status="succeeded",
        response="OK",
        command="VACUUM",
    ),
    CronJobRunDetail(
        start="2026-01-01 01:00:00 UTC",
        end="2026-01-01 01:00:02 UTC",
        name="analyze",
        status="failed",
        response="error",
        command="ANALYZE",
    ),
]


def test_cron_service_jobs() -> None:
    """Test CronService.jobs delegates to pg_cron."""
    mock_db = MagicMock()
    mock_db.pg_cron.return_value.jobs.return_value = _SAMPLE_JOBS

    result = CronService(mock_db).jobs(None)

    assert result == _SAMPLE_JOBS
    mock_db.pg_cron.return_value.jobs.assert_called_once_with(None)


def test_cron_service_jobs_with_job_id() -> None:
    """Test CronService.jobs passes job_id through to pg_cron."""
    mock_db = MagicMock()
    mock_db.pg_cron.return_value.jobs.return_value = [_SAMPLE_JOBS[0]]

    result = CronService(mock_db).jobs(1)

    assert result == [_SAMPLE_JOBS[0]]
    mock_db.pg_cron.return_value.jobs.assert_called_once_with(1)


def test_cron_service_job_run_details() -> None:
    """Test CronService.job_run_details delegates to pg_cron."""
    mock_db = MagicMock()
    mock_db.pg_cron.return_value.job_run_details.return_value = _SAMPLE_RUN_DETAILS

    result = CronService(mock_db).job_run_details(CronRunStatus.ALL, limit=14)

    assert result == _SAMPLE_RUN_DETAILS
    mock_db.pg_cron.return_value.job_run_details.assert_called_once_with(CronRunStatus.ALL, limit=14, job_id=None)


def test_cron_service_job_run_details_with_filters() -> None:
    """Test CronService.job_run_details passes status, limit, and job_id through."""
    mock_db = MagicMock()
    mock_db.pg_cron.return_value.job_run_details.return_value = [_SAMPLE_RUN_DETAILS[1]]

    result = CronService(mock_db).job_run_details(CronRunStatus.FAILED, limit=5, job_id=2)

    assert result == [_SAMPLE_RUN_DETAILS[1]]
    mock_db.pg_cron.return_value.job_run_details.assert_called_once_with(CronRunStatus.FAILED, limit=5, job_id=2)
