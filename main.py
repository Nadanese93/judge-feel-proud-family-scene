#!/usr/bin/env python3
"""Write the family-scene entry to $MAKEFUN_OUTPUT_DIR/entry.txt.

The entry text is embedded as a constant. The program validates it
(non-empty after strip, exactly 2 lines, 1-280 characters, UTF-8
encodable) and writes it byte-for-byte, with no trailing newline
beyond the text itself. After writing, it reads the file back and
verifies the bytes on disk match the constant exactly.
"""

import os
import sys

ENTRY = (
    "It snowed once where we live, so Dad built a snowman out of the freezer's ice cubes and named him Gerald.\n"
    "Mum made Gerald a scarf. Gerald lasted eleven minutes. We still talk about him."
)


class EntryError(ValueError):
    """Base class for entry validation failures."""


class BlankError(EntryError):
    """The entry is empty or only whitespace."""


class LineCountError(EntryError):
    """The entry does not have exactly 2 lines."""


class LengthError(EntryError):
    """The entry is outside the 1-280 character range."""


class EncodingError(EntryError):
    """The entry is not UTF-8 encodable."""


class OutputMismatchError(EntryError):
    """The bytes read back from entry.txt differ from the entry."""


def validate(text):
    """Validate the entry, raising a distinct error class per failure."""
    if not text.strip():
        raise BlankError("entry is blank (empty or only whitespace)")
    lines = text.split("\n")
    if len(lines) != 2:
        raise LineCountError(
            "entry must be exactly 2 lines, got %d" % len(lines)
        )
    if not 1 <= len(text) <= 280:
        raise LengthError(
            "entry must be 1-280 characters, got %d" % len(text)
        )
    try:
        data = text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise EncodingError("entry is not UTF-8 encodable: %s" % exc)
    return data, len(lines)


def main() -> int:
    try:
        data, line_count = validate(ENTRY)
    except EntryError as exc:
        print("error: %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("error: MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "wb") as f:
        f.write(data)
    with open(out_path, "rb") as f:
        written = f.read()
    if written != data:
        print("error: OutputMismatchError: read-back mismatch: entry.txt holds %d bytes, expected %d"
              % (len(written), len(data)), file=sys.stderr)
        return 1
    print("Wrote entry.txt (%d bytes, %d lines, read-back verified)"
          % (len(data), line_count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
