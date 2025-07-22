import pytest

from makeproto.report import CompileError, CompileReport


def test_show_no_errors(capfd: pytest.CaptureFixture[str]) -> None:
    report = CompileReport("TestModule", errors=[])

    report.show()

    out, err = capfd.readouterr()
    assert "No compile errors found" in out
    assert "TestModule" in out


def test_show_with_errors(capfd: pytest.CaptureFixture[str]) -> None:
    errors = [
        CompileError("E001", "line 10", "Syntax error"),
        CompileError("E002", "line 20", "Name not defined"),
    ]
    report = CompileReport("MyModule", errors)

    report.show()

    out, err = capfd.readouterr()
    assert "Compile Report for: MyModule" in out
    assert "E001" in out
    assert "line 10" in out
    assert "Syntax error" in out
    assert "E002" in out
    assert "line 20" in out
    assert "Name not defined" in out

    assert str(report).startswith("CompileReport(name=")
