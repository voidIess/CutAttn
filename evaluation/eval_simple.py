from pathlib import Path

import numpy as np
from evaluation import get_epochs, visualize



def eval(name, args, epoch=None):
    if epoch is None:
        epoch = args.epoch

    print(f"Evaluating {name} at epoch {epoch}")
    if args.dry:
        return

    # import all the heavy stuff only here
    from piq import FID, KID
    from torch.utils.data import DataLoader
    from torchvision.transforms import transforms
    from PIL import Image
    from torchvision.datasets import VisionDataset

    # Define the transforms for preprocessing the images
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        # transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # Adjust with the appropriate normalization values
    ])

    # Paths to your directories
    prefix = Path('results') / name / f'test_{epoch}' / 'images'
    fake_images_path = prefix / 'fake_B'
    real_images_path = prefix / 'real_B'

    # prevent heavy stuff from being loaded all the time
    class DomainDataset(VisionDataset):
        def __init__(self, root, transform=None, target_transform=None):
            super(DomainDataset, self).__init__(root, transform=transform, target_transform=target_transform)
            root = Path(root)
            self.images = list(root.iterdir())

        def __len__(self):
            return len(self.images)

        def __getitem__(self, index):
            path = str(self.images[index])
            image = Image.open(path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return {'images': image}

    # Load images using ImageFolder and create DataLoaders
    fake_dataset = DomainDataset(root=fake_images_path, transform=transform)
    real_dataset = DomainDataset(root=real_images_path, transform=transform)

    fake_dl = DataLoader(fake_dataset, batch_size=args.batch_size, shuffle=False)
    real_dl = DataLoader(real_dataset, batch_size=args.batch_size, shuffle=False)

    # Initialize FID metric
    metrics = [FID, KID]
    scores = []
    score_names = []
    for METRIC in metrics:
        metric_init = METRIC()
        metric_name = METRIC.__name__
        print(f"Computing {metric_name}...")
        # Compute features using the valid DataLoaders
        fake_feats = metric_init.compute_feats(fake_dl)
        real_feats = metric_init.compute_feats(real_dl)

        # Compute FID
        score = metric_init(real_feats, fake_feats)
        print(f"The {metric_name} score is: {score.item()}")
        scores.append(score)
        score_names.append(metric_name)

    return {"score_names": score_names, "scores": scores}


def eval_all(experiments, args):
    experiment, epochs = get_epochs(experiments, args)
    experiment_name = experiment.kvs['name']
    scores = [eval(experiment_name, args, epoch) for epoch in epochs]
    if args.dry:
        return

    # strip metric names out of the return type
    metric_names = np.array(scores[0]["score_names"])

    # scores: turn list(dict(list)) into list(list())
    scores = [result["scores"] for result in scores]
    scores = np.array(scores)
    scores = np.transpose(scores)
    np.savez(visualize.get_eval_file(experiment_name), metric_names=metric_names, scores=scores, epochs=epochs)

    print(scores)

