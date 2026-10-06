#!/usr/bin/env python
import os
import sys


def main():
    # The test command automatically opts into test-only settings (fast password
    # hashing, etc.). Explicit --settings still wins when supplied by the caller.
    default_settings = "config.settings_test" if len(sys.argv) > 1 and sys.argv[1] == "test" else "config.settings"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django is not installed. Run `poetry install` first.") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
