"""Command line subcommand for the build process."""

import copy

import mlonmcu
from mlonmcu.flow import get_available_backend_names
import mlonmcu.flow.tflite
import mlonmcu.flow.tvm
from mlonmcu.models.model import Model
from mlonmcu.session.run import Run
from mlonmcu.session.session import Session
from mlonmcu.cli.build import add_build_options  # Currently we do not have specific tune options
from mlonmcu.cli.common import (
    add_common_options,
    add_context_options,
    add_model_options,
    add_flow_options,
    kickoff_runs,
)
from mlonmcu.config import resolve_required_config
from mlonmcu.cli.load import handle as handle_load, add_load_options
from mlonmcu.cli.build import handle as handle_build, add_build_options
from mlonmcu.flow import SUPPORTED_BACKENDS, SUPPORTED_FRAMEWORKS
from mlonmcu.session.run import RunStage


def get_parser(subparsers, parent=None):
    """ "Define and return a subparser for the tune subcommand."""
    parser = subparsers.add_parser(
        "tune",
        description="Tune model using the ML on MCU flow.",
        parents=[parent] if parent else [],
        add_help=(parent is None),
    )
    parser.set_defaults(flow_func=handle)
    add_build_options(parser)
    return parser


def handle(args, ctx=None):
    if ctx:
        handle_build(ctx, args)
    else:
        with mlonmcu.context.MlonMcuContext(path=args.home, lock=True) as context:
            handle_build(context, args)
            kickoff_runs(args, RunStage.TUNE, context)
