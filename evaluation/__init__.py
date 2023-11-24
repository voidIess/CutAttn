import re
from pathlib import Path


def get_epochs(experiments, args):
    experiment = experiments[args.experiment_id]
    epochs = [re.sub(r"([0-9]*).*_.*", r"\1", checkpoint.name) for checkpoint in
              (Path("checkpoints") / experiment.kvs["name"]).glob("*net_G.pth")]
    epochs = [int(epoch) for epoch in epochs if epoch.isdigit()]
    epochs.sort()
    return experiment, epochs