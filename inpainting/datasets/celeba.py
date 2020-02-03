from pathlib import Path
from typing import Tuple, Sequence

from torchvision import transforms as tr
from torchvision.datasets import CelebA

from inpainting.datasets.mask_coding import UNKNOWN_LOSS
from inpainting.datasets.rgb_utils import random_mask_fn
from inpainting.datasets.utils import RandomRectangleMaskConfig

DEFAULT_MASK_CONFIGS = (
    RandomRectangleMaskConfig(
        UNKNOWN_LOSS,
        12, 12, 0,0,
    ),
    # RandomRectangleMaskConfig(
    #     UNKNOWN_NO_LOSS,
    #     8,8,2,2
    # )
)


def train_val_datasets(
        save_path: Path,
        mask_configs: Sequence[RandomRectangleMaskConfig] = DEFAULT_MASK_CONFIGS,
) -> Tuple[CelebA, CelebA]:
    train_transform = tr.Compose([
        tr.ToTensor(),
        tr.Lambda(random_mask_fn(mask_configs=mask_configs))
    ])

    val_transform = tr.Compose([
        tr.ToTensor(),
        tr.Lambda(random_mask_fn(
            mask_configs=[
                m for m in mask_configs if m.value == UNKNOWN_LOSS
            ]  # only the mask which will be inpainted
        ))
    ])

    ds_train = CelebA(save_path, split="train", download=True, transform=train_transform)
    ds_val = CelebA(save_path, split="val", download=True, transform=val_transform)

    return ds_train, ds_val