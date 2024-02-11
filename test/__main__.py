import argparse
import pathlib
import sys
import webbrowser

import pytest

import coverage.config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--open-browser', action='store_true')
    open_browser = parser.parse_args(sys.argv[1:]).open_browser
    status_code = pytest.main(args=['--cov=slmc', '--cov-report=html'])
    if status_code == 0 and open_browser:
        coverage_config = coverage.config.read_coverage_config(
            config_file=True, warn=lambda _: None
        )
        assert coverage_config.config_file is not None
        report_location = (
            pathlib.Path(coverage_config.config_file).parent / coverage_config.html_dir
        )
        webbrowser.open(f'file://{report_location}/index.html')


if __name__ == '__main__':
    main()
