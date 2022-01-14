import sys
import os
import tempfile
import logging
from pathlib import Path
from .backend import TFLiteBackend
import mlonmcu.setup.utils as utils
from mlonmcu.flow.backend import main, Artifact

logger = logging.getLogger("mlonmcu")

FEATURES = ["debug_arena"]

DEFAULT_CONFIG = {
    "custom_ops": [],
    "registrations": {},
    "tflmc.exe": None,
}


class TFLMCBackend(TFLiteBackend):

    shortname = "tflmc"

    def __init__(self, features=None, config=None, context=None):
        super().__init__(features=features, config=config, context=context)
        self.model_data = None
        self.prefix = "model"  # Without the _
        self.artifacts = (
            []
        )  # TODO: either make sure that ony one model is processed at a time or move the artifacts to the methods
        # TODO: decide if artifacts should be handled by code (str) or file path or binary data

    def generate_code(self):
        artifacts = []
        assert self.model is not None
        tflmc_exe = None
        if "tflmc.exe" in self.config:
            tflmc_exe = self.config["tflmc.exe"]
        else:
            # Lookup cache
            raise NotImplementedError
        with tempfile.TemporaryDirectory() as tmpdirname:
            logger.debug('Using temporary directory for codegen results: %s', tmpdirname)
            args = []
            args.append(str(self.model))
            args.append(str(Path(tmpdirname) / f"{self.prefix}.cc"))
            args.append(f"{self.prefix}_")
            verbose = True  # ???
            utils.exec_getout(tflmc_exe, live=verbose, *args)
            files = [f for f in os.listdir(tmpdirname) if os.path.isfile(os.path.join(tmpdirname, f))]
            # TODO: ensure that main file is processed first
            for filename in files:
                with open(Path(tmpdirname) / filename, "r") as handle:
                    content = handle.read()
                    artifacts.append(Artifact(filename, content=content))

        self.artifacts = artifacts


if __name__ == "__main__":
    sys.exit(
        main(
            "tflmc",
            TFLMCBackend,
            backend_features=FEATURES,
            backend_defaults=DEFAULT_CONFIG,
            args=sys.argv[1:],
        )
    )  # pragma: no cover
