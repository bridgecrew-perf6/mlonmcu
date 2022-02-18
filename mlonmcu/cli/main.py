"""Console script for mlonmcu."""

import os
import argparse
import sys
import logging
import subprocess
import platform

from ..version import __version__

from mlonmcu.logging import get_logger

logger = get_logger()

import mlonmcu.cli.init as init

# from .init import get_init_parser
import mlonmcu.cli.setup as setup
import mlonmcu.cli.flow as flow
import mlonmcu.cli.cleanup as cleanup
import mlonmcu.cli.check as check
import mlonmcu.cli.export as export
import mlonmcu.cli.env as env
import mlonmcu.cli.models as models

from .common import handle_logging_flags, add_common_options


def handle_docker(args):
    if args.docker:
        home = os.environ.get("MLONMCU_HOME")
        assert (
            home is not None
        ), "To use the --docker functionality, please export the MLONMCU_HOME environment variable to a directory which should be mounted by the container"
        exec_args = sys.argv[1:]
        exec_args.remove("--docker")
        docker = subprocess.Popen(
            [
                "docker-compose",
                "-f",
                "docker/docker-compose.yml",
                "run",
                "-e",
                f"MLONMCU_HOME={home}",
                "--rm",
                "mlonmcu",
                "python3",
                "-m",
                "mlonmcu.cli.main",
                *exec_args,
            ],
            env={"MLONMCU_HOME": home},
        )
        stdout, stderr = docker.communicate()
        exit_code = docker.wait()
        if exit_code > 0:
            logger.warning(f"Docker compose process completed with exit code: {exit_code}")
        sys.exit(exit_code)

    if platform.system() in ["Darwin", "Windows"]:
        raise RuntimeError(
            "Only Linux is supported at the Moment. If you have Docker installed, you may want to try running this script using the `--docker` flag."
        )


# def main(args):
def main(args=None):
    """Console script for mlonmcu."""
    parser = argparse.ArgumentParser(
        description="ML on MCU Flow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # parser.add_argument('_', nargs='*')
    parser.add_argument("-V", "--version", action="version", version="mlonmcu " + __version__)
    add_common_options(parser)
    subparsers = parser.add_subparsers(dest="subcommand")  # this line changed
    init_parser = init.get_parser(subparsers)
    setup_parser = setup.get_parser(subparsers)
    flow_parser = flow.get_parser(subparsers)
    # TODO: hide load,build,compile,run,debug,test behind flow subcommand?
    # trace_parser = get_trace_parser(subparsers)  # Handled as a flag to run subcommand or target-feature
    # TODO: cleanup
    cleanup_parser = cleanup.get_parser(subparsers)
    # TODO: check
    check_parser = check.get_parser(subparsers)
    # TODO: run
    # TODO: env
    export_parser = export.get_parser(subparsers)
    env_parser = env.get_parser(subparsers)
    # TODO: models
    models_parser = models.get_parser(subparsers)
    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()
    handle_logging_flags(args)
    handle_docker(args)

    if hasattr(args, "func"):
        args.func(args)
    else:
        print("Invalid subcommand for `mlonmcu`!")
        parser.print_help(sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main(args=sys.argv[1:]))  # pragma: no cover
