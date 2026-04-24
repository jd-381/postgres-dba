"""Tests for service classes."""

import logging

import pytest

from template_package.commands.hello import HelloService
from template_package.commands.mail import MailService
from template_package.models.language import Language

logger = logging.getLogger(__name__)


def test_hello_service_english(capsys: pytest.CaptureFixture[str]) -> None:
    """Test HelloService.hello method with English."""
    service = HelloService(Language.ENGLISH, logger)
    service.hello("Alice")

    captured = capsys.readouterr()
    assert "Hello Alice" in captured.out


def test_hello_service_spanish(capsys: pytest.CaptureFixture[str]) -> None:
    """Test HelloService.hello method with Spanish."""
    service = HelloService(Language.SPANISH, logger)
    service.hello("Carlos")

    captured = capsys.readouterr()
    assert "Hola Carlos" in captured.out


def test_hello_service_default_language(capsys: pytest.CaptureFixture[str]) -> None:
    """Test HelloService.hello method with default language."""
    service = HelloService(logger=logger)
    service.hello("World")

    captured = capsys.readouterr()
    assert "Hello World" in captured.out


def test_mail_service_fetch() -> None:
    """Test MailService.fetch method."""
    from template_package.models.mail import mail_data

    service = MailService(logger)
    mail = service.fetch()

    assert isinstance(mail, list)
    assert len(mail) > 0
    assert mail is mail_data  # Should return the same list reference


def test_mail_service_delete() -> None:
    """Test MailService.delete method."""
    from template_package.models.mail import mail_data

    # Store original data
    original_data = list(mail_data)
    initial_count = len(mail_data)

    try:
        service = MailService(logger)
        service.delete(3)

        # Verify 3 items were deleted
        assert len(mail_data) == initial_count - 3

        # Verify the first 3 items were removed (items at index 0-2)
        assert mail_data[0] == original_data[3]
    finally:
        # Restore original data
        mail_data.clear()
        mail_data.extend(original_data)
