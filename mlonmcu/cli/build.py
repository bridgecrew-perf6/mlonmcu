"""Command line subcommand for the build process."""

import copy
import logging

import mlonmcu
from mlonmcu.flow import SUPPORTED_BACKENDS
import mlonmcu.flow.tflite
import mlonmcu.flow.tvm
from mlonmcu.models.model import Model
from mlonmcu.session.run import Run
from mlonmcu.session.session import Session
from mlonmcu.cli.common import add_common_options, add_context_options, add_model_options, add_flow_options
from mlonmcu.cli.load import handle as handle_load, add_load_options, add_model_options

logger = logging.getLogger("mlonmcu")
logger.setLevel(logging.DEBUG)

def add_build_options(parser):
    build_parser = parser.add_argument_group("build options")
    build_parser.add_argument(
        "-b",
        "--backend",
        type=str,
        action='append',
        choices=["tflmc", "tflmi", "tvmaot", "tvmrt", "tvmcg", "tflm", "utvm"],
        help="Backends to use (default: %(default)s)")

def get_parser(subparsers, parent=None):
    """"Define and return a subparser for the build subcommand."""
    parser = subparsers.add_parser('build', description='Build model using the ML on MCU flow.', parents=[parent] if parent else [], add_help = (parent is None))
    parser.set_defaults(func=handle)
    add_model_options(parser)
    add_common_options(parser)
    add_context_options(parser)
    add_build_options(parser)
    add_flow_options(parser)
    return parser

def _handle(context, args):
    handle_load(args, ctx=context)
    print(args)
    if args.config:
        configs = sum(args.config,[])
    else:
        configs = {}
    def parse_var(s):
        """
        Parse a key, value pair, separated by '='
        That's the reverse of ShellArgs.

        On the command line (argparse) a declaration will typically look like:
            foo=hello
        or
            foo="hello world"
        """
        items = s.split('=')
        key = items[0].strip() # we remove blanks around keys, as is logical
        if len(items) > 1:
            # rejoin the rest:
            value = '='.join(items[1:])
        return (key, value)


    def parse_vars(items):
        """
        Parse a series of key-value pairs and return a dictionary
        """
        d = {}

        if items:
            for item in items:
                key, value = parse_var(item)
                d[key] = value
        return d
    configs = parse_vars(configs)
    print("configs", configs)
    # print(configs)
    # input()
    backends_names = args.backend
    assert len(context.sessions) > 0
    session = context.sessions[-1]
    print("session", session)
    print("backends_names", backends_names)
    new_runs = []
    for run in session.runs:
        if backends_names and len(backends_names) > 0:
            for backend_name in backends_names:
                new_run = copy.deepcopy(run)
                backend_class = SUPPORTED_BACKENDS[backend_name]
                backend = backend_class(config=configs)
                new_run.backend = backend
                new_run.cfg = configs
                new_runs.append(new_run)
        else:
            raise NotImplementedError("TODO: Default backends!")
    session.runs = new_runs
    for run in session.runs:
        run.build(context=context)
    print("session.runs", session.runs)

def handle(args, ctx=None):
    print("HANDLE BUILD")
    if ctx:
        _handle(ctx, args)
    else:
        with mlonmcu.context.MlonMcuContext(path=args.home, lock=True) as context:
            _handle(context, args)
    print("HANDLED BUILD")