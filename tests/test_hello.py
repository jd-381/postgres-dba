"""Tests for the hello command."""

from typer.testing import CliRunner

from template_package.main import app

runner = CliRunner()


def test_hello_single_name():
    """Test greeting a single person."""
    result = runner.invoke(app, ["hello", "--name", "Alice"])
    assert result.exit_code == 0
    assert "Hello Alice" in result.stdout


def test_hello_default_language():
    """Test greeting with default language (English)."""
    result = runner.invoke(app, ["hello", "--name", "World"])
    assert result.exit_code == 0
    assert "Hello World" in result.stdout


def test_hello_spanish():
    """Test greeting in Spanish."""
    result = runner.invoke(app, ["hello", "--name", "Mundo", "--language", "spanish"])
    assert result.exit_code == 0
    assert "Hola Mundo" in result.stdout


def test_hello_short_options():
    """Test using short option flags."""
    result = runner.invoke(app, ["hello", "-n", "Alice", "-l", "english"])
    assert result.exit_code == 0
    assert "Hello Alice" in result.stdout


def test_hello_short_options_spanish():
    """Test using short option flags with Spanish."""
    result = runner.invoke(app, ["hello", "-n", "Carlos", "-l", "spanish"])
    assert result.exit_code == 0
    assert "Hola Carlos" in result.stdout
