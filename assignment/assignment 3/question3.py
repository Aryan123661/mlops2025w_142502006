
import os
import sys
import json
import warnings
import logging
import contextlib
from datetime import datetime
from itertools import product

warnings.filterwarnings("ignore")

logging.getLogger().setLevel(logging.ERROR)

try:
    import torch
    import torchvision.models as models
except Exception:
    pass

config_json = {
    "data": {
        "name": "synthetic",
        "description": "No external dataset required; uses random tensors for inference",
        "input_size": [3, 224, 224]
    },
    "models": [
        "resnet34",
        "resnet50",
        "resnet101",
        "resnet152"
    ]
}

config_toml = r"""
[hyperparams.resnet34]
learning_rate = 0.01
optimizer = "sgd"
momentum = 0.9
epochs = 1
batch_size = 1

[hyperparams.resnet50]
learning_rate = 0.001
optimizer = "adam"
momentum = 0.0
epochs = 1
batch_size = 1
"""

toml_cfg = {}
try:
    import tomli

    try:
        toml_cfg = tomli.loads(config_toml)
    except Exception:
        toml_cfg = {}
except Exception:
    toml_cfg = {}

RESNETS = {}
try:
    RESNETS = {
        "resnet34": models.resnet34,
        "resnet50": models.resnet50,
        "resnet101": models.resnet101,
        "resnet152": models.resnet152
    }
except Exception:
    RESNETS = {}

def _silent_call(fn, *args, **kwargs):
    """
    Call fn(*args, **kwargs) while silencing stdout/stderr and ignoring warnings.
    Returns the function result, or raises the original exception if construction fails.
    """

    devnull = open(os.devnull, "w")
    try:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return fn(*args, **kwargs)
    finally:
        devnull.close()

def safe_build_model(constructor):

    try:
        model = _silent_call(constructor, pretrained=True)
        return model
    except Exception:
        try:
            model = _silent_call(constructor, pretrained=False)
            return model
        except Exception:
            return None

def run_inference_and_grid_search_print():

    lines = []
    now = datetime.utcnow().isoformat() + "Z"
    lines.append(f"Assignment 3 - Q3 run at {now}\n")
    lines.append("1) JSON config (data + models):\n")
    lines.append(json.dumps(config_json, indent=2))
    lines.append("\n\n2) TOML-derived hyperparameter samples (showing any provided per-model defaults):\n")
    lines.append(json.dumps(toml_cfg, indent=2))
    lines.append("\n\n3) Performing inference (dummy inputs) on ResNet models and enumerating a small grid:\n")

    c, h, w = config_json["data"]["input_size"]
    try:
        dummy = torch.randn(1, c, h, w, dtype=torch.float32)
    except Exception:
        dummy = None

    grid_lrs = [0.1, 0.01, 0.001]
    grid_opts = ["adam", "sgd"]
    grid_moms = [0.5, 0.9]

    tried = []

    for model_name in config_json["models"]:
        lines.append(f"--- Model: {model_name} ---")
        constructor = RESNETS.get(model_name)
        if constructor is None:
            lines.append(f"Model constructor for {model_name} not available (torch/torchvision missing). Skipping.\n")
            continue

        model = safe_build_model(constructor)
        if model is None:
            lines.append(f"Could not instantiate {model_name}. Skipping.\n")
            continue

        try:
            model.eval()
            model.to(torch.device("cpu"))
        except Exception:
            pass

        if dummy is None:
            lines.append("Torch not available - skipping inference (no dummy tensor).\n")
        else:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    with contextlib.redirect_stdout(open(os.devnull, "w")), contextlib.redirect_stderr(open(os.devnull, "w")):
                        with torch.no_grad():
                            out = model(dummy)
                lines.append(f"Inference output shape for {model_name}: {tuple(out.shape)}")
            except Exception:
                lines.append(f"Inference failed for {model_name} (silently skipped).")

        lines.append("Enumerating grid (lr, optimizer, momentum) - lightweight (no training):")
        for lr, opt_name, mom in product(grid_lrs, grid_opts, grid_moms):
            params = [p for p in model.parameters() if p.requires_grad]
            try:
                if opt_name == "adam":
                    _ = torch.optim.Adam(params, lr=lr)
                elif opt_name == "sgd":
                    _ = torch.optim.SGD(params, lr=lr, momentum=mom)
                else:
                    continue
            except Exception:
                continue
            tried.append({"model": model_name, "lr": lr, "opt": opt_name, "momentum": mom})

        count_for_model = len([t for t in tried if t["model"] == model_name])
        lines.append(f"Total grid combinations tried for {model_name}: {count_for_model}\n")

    output_text = "\n".join(lines)
    print(output_text)


if __name__ == "__main__":
    run_inference_and_grid_search_print()
