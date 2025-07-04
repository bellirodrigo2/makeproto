import textwrap

from makeproto.format_comment import format_comment


def test_already_single_line_comment() -> None:
    assert format_comment("// existing comment", 50, False) == "// existing comment"


def test_already_multiline_comment() -> None:
    assert (
        format_comment("/* multiline comment */", 50, False)
        == "/* multiline comment */"
    )


def test_force_format_existing_comment() -> None:
    assert format_comment("// existing comment", 50, True) == "// existing comment"


def test_single_line_under_max_chars() -> None:
    assert format_comment("short description", 50, False) == "// short description"


def test_single_line_equals_max_chars() -> None:
    text = "a" * 50
    assert format_comment(text, 50, False) == f"// {text}"


def test_multiline_comment_when_over_max_chars() -> None:
    text = "This is a very long description that should be split into multiple lines"
    expected = "/*\nThis is a very long description that should be\nsplit into multiple lines\n*/"
    assert format_comment(text, 50, False) == expected


def test_multiline_comment_with_newlines() -> None:
    text = "This is a line\nand this is another line"
    expected = "/*\nThis is a line and this is another line\n*/"
    assert format_comment(text, 50, False) == expected


def test_always_format_true_for_multiline() -> None:
    text = "/* already formatted */"
    expected = "// already formatted"
    assert format_comment(text, 50, True) == expected


def test_removes_prefix_suffix_and_trims() -> None:
    text = " /* text with extra spaces */ "
    expected = "// text with extra spaces"
    assert format_comment(text, 50, True) == expected


def test_extremely_long_text() -> None:
    text = "word " * 20  # ~100 characters
    expected = "/*\n" + "\n".join(textwrap.wrap(text.strip(), width=30)) + "\n*/"
    assert format_comment(text, 30, False) == expected
