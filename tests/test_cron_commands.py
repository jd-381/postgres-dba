"""Tests for the cron commands."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from postgres_dba.main import app
from postgres_dba.models.postgres.pg_cron import CronJob, CronJobRunDetail, CronRunStatus

runner = CliRunner()

SAMPLE_JOBS = [
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

SAMPLE_RUN_DETAILS = [
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


@pytest.fixture
def mock_db():
    """Mock PostgresInstance and PostgresDatabase for cron CLI commands."""
    with (
        patch("postgres_dba.commands.cron.PostgresInstance.from_env_vars"),
        patch("postgres_dba.commands.cron.PostgresDatabase.from_instance") as mock_db_cm,
    ):
        mock_db_obj = MagicMock()
        mock_db_cm.return_value.__enter__ = MagicMock(return_value=mock_db_obj)
        mock_db_cm.return_value.__exit__ = MagicMock(return_value=False)
        yield mock_db_obj


def test_cron_jobs(mock_db):
    """Test listing all cron jobs."""
    mock_db.pg_cron.return_value.jobs.return_value = SAMPLE_JOBS

    result = runner.invoke(app, ["cron", "jobs"])
    assert result.exit_code == 0
    assert "vacuum" in result.stdout
    assert "analyze" in result.stdout


def test_cron_jobs_with_job_id(mock_db):
    """Test filtering jobs by job ID."""
    mock_db.pg_cron.return_value.jobs.return_value = [SAMPLE_JOBS[0]]

    result = runner.invoke(app, ["cron", "jobs", "--job", "1"])
    assert result.exit_code == 0
    assert "vacuum" in result.stdout
    mock_db.pg_cron.return_value.jobs.assert_called_once_with(1)


def test_cron_jobs_short_option(mock_db):
    """Test filtering jobs using short -j option."""
    mock_db.pg_cron.return_value.jobs.return_value = [SAMPLE_JOBS[0]]

    result = runner.invoke(app, ["cron", "jobs", "-j", "1"])
    assert result.exit_code == 0
    mock_db.pg_cron.return_value.jobs.assert_called_once_with(1)


def test_cron_jobs_db_error(mock_db):
    """Test that a database error exits with code 1."""
    mock_db.pg_cron.side_effect = Exception("connection refused")

    result = runner.invoke(app, ["cron", "jobs"])
    assert result.exit_code == 1


def test_cron_logs(mock_db):
    """Test listing all cron run logs."""
    mock_db.pg_cron.return_value.job_run_details.return_value = SAMPLE_RUN_DETAILS

    result = runner.invoke(app, ["cron", "logs"])
    assert result.exit_code == 0
    assert "vacuum" in result.stdout
    assert "analyze" in result.stdout


def test_cron_logs_default_args(mock_db):
    """Test that logs defaults to ALL status and limit of 14."""
    mock_db.pg_cron.return_value.job_run_details.return_value = SAMPLE_RUN_DETAILS

    runner.invoke(app, ["cron", "logs"])
    mock_db.pg_cron.return_value.job_run_details.assert_called_once_with(CronRunStatus.ALL, limit=14, job_id=None)


def test_cron_logs_with_status_filter(mock_db):
    """Test filtering logs by status."""
    mock_db.pg_cron.return_value.job_run_details.return_value = [SAMPLE_RUN_DETAILS[1]]

    result = runner.invoke(app, ["cron", "logs", "--status", "failed"])
    assert result.exit_code == 0
    mock_db.pg_cron.return_value.job_run_details.assert_called_once_with(CronRunStatus.FAILED, limit=14, job_id=None)


def test_cron_logs_with_limit(mock_db):
    """Test limiting the number of log entries returned."""
    mock_db.pg_cron.return_value.job_run_details.return_value = SAMPLE_RUN_DETAILS

    result = runner.invoke(app, ["cron", "logs", "--limit", "5"])
    assert result.exit_code == 0
    mock_db.pg_cron.return_value.job_run_details.assert_called_once_with(CronRunStatus.ALL, limit=5, job_id=None)


def test_cron_logs_with_job_id(mock_db):
    """Test filtering logs by job ID includes job ID in title."""
    mock_db.pg_cron.return_value.job_run_details.return_value = [SAMPLE_RUN_DETAILS[0]]

    result = runner.invoke(app, ["cron", "logs", "--job", "1"])
    assert result.exit_code == 0
    assert "Job 1" in result.stdout
    mock_db.pg_cron.return_value.job_run_details.assert_called_once_with(CronRunStatus.ALL, limit=14, job_id=1)


def test_cron_logs_short_options(mock_db):
    """Test logs using short option flags."""
    mock_db.pg_cron.return_value.job_run_details.return_value = [SAMPLE_RUN_DETAILS[0]]

    result = runner.invoke(app, ["cron", "logs", "-s", "succeeded", "-j", "1"])
    assert result.exit_code == 0
    mock_db.pg_cron.return_value.job_run_details.assert_called_once_with(CronRunStatus.SUCCEEDED, limit=14, job_id=1)


def test_cron_logs_db_error(mock_db):
    """Test that a database error exits with code 1."""
    mock_db.pg_cron.side_effect = Exception("connection refused")

    result = runner.invoke(app, ["cron", "logs"])
    assert result.exit_code == 1
