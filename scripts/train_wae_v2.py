#!/usr/bin/env python
# coding: utf-8
import sys

sys.path.append("..")

from pprint import pprint

try:
    import cuml, cudf
except:
    print("Failed to import CUML. This is not breaking unless you want to use KNN.")

from torch.utils.data import DataLoader
from torchvision.datasets import MNIST, FashionMNIST

import common as common_loaders
import json
import torch
from torch import nn
from pathlib import Path
import matplotlib.pyplot as plt
import shutil
from tqdm import tqdm

from inpainting.datasets.mask_coding import UNKNOWN_LOSS
from inpainting.datasets.utils import RandomRectangleMaskConfig
from inpainting.datasets.mnist import train_val_datasets as mnist_train_val_ds
from inpainting.datasets.svhn import train_val_datasets as svhn_train_val_ds
from inpainting.datasets.celeba import train_val_datasets as celeba_train_val_ds
from inpainting.visualizations.digits import img_with_mask
from inpainting.custom_layers import ConVar, ConVarNaive
from inpainting.inpainters import mocks as inpainters_mocks
from inpainting.utils import printable_history, dump_history
import inpainting.visualizations.visualizations_utils as vis
import inpainting.backbones as bkb
from inpainting.evaluation import frechet_models as fid_models
from inpainting.generative.pre_inpainted_wae import (
    PreInpaintedWAE,
    get_discriminator,
    train_pre_inpainted_wae,
)
from torch.nn import BCELoss, MSELoss
from datetime import datetime
from dotted.utils import dot
from inpainting.utils import (
    printable_history,
    dump_history,
    predictions_for_entire_loader_as_dataset,
)

import numpy as np

import matplotlib

matplotlib.rcParams["figure.facecolor"] = "white"

from common_args import parser, environment_args, experiment_args

experiment_args.add_argument(
    "--convar_type",
    type=str,
    default="full",
    choices=["full", "naive", "partial"],
    help="ConVar implementation to use.",
)

experiment_args.add_argument(
    "--seed",
    action="store_true",
    default=False,
    help="If true, random seed will be used for determinism.",
)

experiment_args.add_argument(
    "--train_inpainter_layer",
    action="store_true",
    default=False,
    help="Train inpainter layer with gradient from classification loss. If False, only the classifier layers are trained.",
)


environment_args.add_argument(
    "--results_dir",
    type=Path,
    default="../results/generation",
    help="Base of path where experiment results will be dumped.",
)

inpainter_args = parser.add_argument_group("Inpainter model")

inpainter_args.add_argument(
    "--inpainter_type",
    type=str,
    default="gt",
    choices=["gt", "noise", "zero", "dmfa", "mfa", "acflow", "knn"],
    help="Type of Inpainter. 'gt', 'noise', 'zero' are mock models which produce ground-truth, randn noise and zero imputations, respectively. ",
)

inpainter_args.add_argument(
    "--inpainter_path",
    type=Path,
    help="Used if inpainter_type=dmfa. Should point to DMFA export directory which contains 'args.json' and 'training.state' files.",
    required=False,
    default=None,
)

wae_args = parser.add_argument_group("WAE model")

wae_args.add_argument(
    "--convar_channels",
    type=int,
    default=32,
    help="N of output channels of convar layer",
)

wae_args.add_argument(
    "--wae_depth",
    type=int,
    default=2,
    help="Number of conv-relu-batchnorm blocks in fully convolutional WAE",
)

wae_args.add_argument(
    "--wae_bl",
    type=int,
    default=1,
    help="Number of repetitions of conv-relu-batchnorm sequence in fully convolutional WAE.",
)

wae_args.add_argument(
    "--wae_fc",
    type=int,
    default=32,
    help="Number of channels in the first convolution of WAE encoder",
)

wae_args.add_argument(
    "--wae_lc",
    type=int,
    default=32,
    help="Number of channels in the last convolution of WAE decoder",
)
wae_args.add_argument(
    "--wae_latent_size",
    type=int,
    default=20,
    help="Latent size of WAE backbone",
)
wae_args.add_argument(
    "--wae_disc_hidden",
    type=int,
    default=64,
    help="Hidden size of WAE discriminator",
)

wae_args.add_argument(
    "--wae_disc_loss_weight",
    type=float,
    default=0.01,
    help="Weight of discriminator loss",
)

wae_args.add_argument(
    "--wae_recon_loss",
    type=str,
    default="bce",
    choices=["bce", "mse"],
    help="BCE for MNIST, MSE for others?",
)

wae_args.add_argument(
    "--skip_fid", action="store_true", default=False, help="Skip FID evaluation."
)


experiment_args.add_argument(
    "--convar_append_mask",
    action="store_true",
    default=False,
    help="If True, known/missing mask will be appended to convar output.",
)


args = parser.parse_args()

if args.inpainter_type in ["gt", "noise", "zero"]:
    args.inpainter_path = None

if args.seed:
    np.random.seed(0)
    torch.manual_seed(0)
    torch.set_deterministic(True)

args_dict = vars(args)
pprint(args_dict)
device = args.device
experiment_path = (
    args.results_dir / args.dataset / "pre_inpainting" / args.experiment_name
)
experiment_path.mkdir(exist_ok=True, parents=True)

print("Experiment path:", experiment_path.absolute())

with (experiment_path / "args.json").open("w") as f:
    json.dump(
        {
            k: v if isinstance(v, (int, str, bool, float)) else str(v)
            for (k, v) in args_dict.items()
        },
        f,
        indent=2,
    )

with (experiment_path / "rerun.sh").open("w") as f:
    print("#", datetime.now(), file=f)
    print("python", *sys.argv, file=f)

img_size = args.img_size

mask_configs_train, mask_configs_val = common_loaders.mask_configs_from_args(args)

if "mnist" in args.dataset:
    ds_train, ds_val = mnist_train_val_ds(
        ds_type=FashionMNIST if args.dataset == "fashion_mnist" else MNIST,
        save_path=Path(args.dataset_root),
        mask_configs_train=mask_configs_train,
        mask_configs_val=mask_configs_val,
        resize_size=(img_size, img_size),
    )
elif args.dataset == "svhn":
    ds_train, ds_val = svhn_train_val_ds(
        save_path=Path(args.dataset_root),
        mask_configs_train=mask_configs_train,
        mask_configs_val=mask_configs_val,
        resize_size=(img_size, img_size),
    )
elif args.dataset == "celeba":
    img_to_crop = 1.875
    # celebA images are cropped to contain only the faces, which are assumed to be in images' centers
    full_img_size = int(img_size * img_to_crop)
    ds_train, ds_val = celeba_train_val_ds(
        save_path=Path(args.dataset_root),
        mask_configs_train=mask_configs_train,
        mask_configs_val=mask_configs_val,
        resize_size=(full_img_size, full_img_size),
        crop_size=(img_size, img_size),
    )
else:
    raise ValueError(f"Unknown dataset {args.dataset}.")

fig, axes = plt.subplots(4, 4, figsize=(5, 5))
for i in range(16):
    (x, j), y = ds_train[i]
    ax = axes[i // 4, i % 4]
    img_with_mask(x.numpy(), j.numpy(), ax)
    ax.set_title(str(y))
train_fig = plt.gcf()
train_fig.savefig(experiment_path / "train.png")
plt.clf()

print("dataset sizes", len(ds_train), len(ds_val))

dl_train_inp = DataLoader(ds_train, args.batch_size, shuffle=False, drop_last=True)
dl_val_inp = DataLoader(ds_val, args.batch_size, shuffle=False, drop_last=True)


img_shape = args.img_size


if args.inpainter_type == "dmfa":
    print(f"Loading DMFA inpainter from {args.inpainter_path}")
    dmfa_path = args.inpainter_path

    with (dmfa_path / "args.json").open("r") as f:
        dmfa_args = dot(json.load(f))

    inpainter = common_loaders.dmfa_from_args(dmfa_args)

    checkpoint = torch.load((dmfa_path / "training.state"), map_location="cpu")
    inpainter.load_state_dict(
        checkpoint["inpainter"],
    )  # strict=False)

elif args.inpainter_type == "mfa":
    print(f"Loading MFA inpainter from {args.inpainter_path}")
    inpainter = common_loaders.mfa_from_path(args.inpainter_path)

elif args.inpainter_type == "acflow":
    inpainter = common_loaders.acflow_from_path(
        args.inpainter_path, batch_size=args.batch_size
    )

elif args.inpainter_type == "gt":
    inpainter = inpainters_mocks.GroundTruthInpainter()

elif args.inpainter_type == "zero":
    inpainter = inpainters_mocks.ZeroInpainter()

elif args.inpainter_type == "noise":
    inpainter = inpainters_mocks.ZeroInpainter()

elif args.inpainter_type == "knn":
    inpainter = inpainters_mocks.KNNInpainter(ds_train)

else:
    raise TypeError(f"Unknown inpainter {args.inpainter_type}")

ds_val_inp, ds_train_inp = [
    predictions_for_entire_loader_as_dataset(inpainter, dl, device)
    for dl in [
        tqdm(dl_val_inp, "Inpainting val DS"),
        tqdm(dl_train_inp, "Inpainting train DS"),
    ]
]

dl_train = DataLoader(ds_train_inp, args.batch_size, shuffle=True)

dl_train_val = DataLoader(ds_train_inp, args.batch_size, shuffle=False)
dl_val = DataLoader(ds_val_inp, args.batch_size, shuffle=False)

convar_in_channels = 1 if "mnist" in args.dataset else 3

convar = common_loaders.convar_from_args(args)


enc_down, dec = bkb.down_up_backbone_v2(
    chw=(
        args.convar_channels,
        img_shape,
        img_shape,
    ),
    depth=args.wae_depth,
    block_length=args.wae_bl,
    first_channels=args.wae_fc,
    last_channels=args.wae_lc,
    latent_size=args.wae_latent_size,
)

dec_final_conv = nn.Conv2d(
    args.wae_lc, out_channels=convar_in_channels, kernel_size=3, padding=1
)
wae_encoder = enc_down
wae_decoder = nn.Sequential(dec, dec_final_conv, nn.Sigmoid())


wae = PreInpaintedWAE(
    convar_layer=convar,
    encoder=wae_encoder,
    decoder=wae_decoder,
    discriminator=get_discriminator(
        in_size=args.wae_latent_size, hidden_size=args.wae_disc_hidden
    ),
    keep_inpainting_gradient=args.train_inpainter_layer,
)

print(
    {
        k: f"{sum(p.numel() for p in model.parameters())} parameters"
        for (k, model) in [
            ("entire model", wae),
            ("encoder", wae.encoder),
            ("decoder", wae.decoder),
            ("discriminator", wae.discriminator),
        ]
    }
)
wae = wae.to(device)

optimizer = torch.optim.Adam(wae.parameters(), lr=args.lr)


# save schemas of the inpainter and optimizer
with (experiment_path / "wae.schema").open("w") as f:
    print(wae, file=f)

if args.skip_fid:
    fid_model = None
else:
    if "mnist" in args.dataset:
        fid_model = fid_models.MNISTNet.pretrained(
            dl_train=dl_train_inp, dl_val=dl_val_inp, device=device
        )
    else:
        print("Loading Inception FID model")
        fid_model = fid_models.InceptionV3().to(device)


recon_loss = BCELoss() if args.wae_recon_loss == "bce" else MSELoss()
history = train_pre_inpainted_wae(
    wae=wae,
    data_loader_train=dl_train,
    data_loaders_val={"train": dl_train_val, "val": dl_val},
    optimizer=optimizer,
    n_epochs=args.num_epochs,
    device=device,
    max_benchmark_batches=args.max_benchmark_batches,
    discriminator_loss_fn=BCELoss(
        weight=torch.tensor(args.wae_disc_loss_weight).to(device)
    ),
    reconstruction_loss_fn=recon_loss,
    fid_model=fid_model,
)

pprint(printable_history(history))

dump_history(history, experiment_path)

# TODO turn this into functions
if args.render_every > 0:

    row_length = (
        vis.row_length(
            *[
                history[0]["sample_results"]["train"][t_name][0]
                for t_name in ["X", "J", "P", "M", "A", "D", "Y"]
            ]
        )
        + 2
    )
    last_epoch = max(h["epoch"] for h in history)

    fig, axes = plt.subplots(
        len(
            [
                h
                for h in history
                if (h["epoch"] % args.render_every) == 0 or h["epoch"] == last_epoch
            ]
        )
        * 2,
        row_length,
        figsize=(20, 30),
    )
    row_no = 0
    for h in tqdm(history):

        e = h["epoch"]
        if e % args.render_every != 0 and e != last_epoch:
            continue

        for ax_no, fold in [(0, "train"), (1, "val")]:
            x, j, p, m, a, d, y, decoder_out, decoder_fake_out = [
                h["sample_results"][fold][k][0]
                for k in [
                    "X",
                    "J",
                    "P",
                    "M",
                    "A",
                    "D",
                    "Y",
                    "decoder_out",
                    "decoder_fake_out",
                ]
            ]
            vis.visualize_sample(
                x,
                j,
                p,
                m,
                a,
                d,
                y,
                ax_row=axes[row_no],
                title_prefixes={0: f"{e} {fold} "},
                drawing_fn=img_with_mask,
            )

            dec_out = (
                decoder_out.reshape(img_shape, img_shape)
                if convar_in_channels == 1
                else decoder_out.transpose(1, 2, 0)
            )

            axes[row_no][-2].set_title("WAE out (true)")
            axes[row_no][-2].imshow(dec_out)

            dec_fake_out = (
                decoder_fake_out.reshape(img_shape, img_shape)
                if convar_in_channels == 1
                else decoder_fake_out.transpose(1, 2, 0)
            )

            axes[row_no][-1].set_title("WAE sample")
            axes[row_no][-1].imshow(dec_fake_out)

            row_no += 1

    epochs_fig = plt.gcf()
    epochs_fig.savefig(experiment_path / "epochs_renders.png")

    epochs_path = experiment_path / "epochs"
    if epochs_path.exists():
        shutil.rmtree(epochs_path)
    epochs_path.mkdir()

    n_rows_fig = 16

    for h in tqdm(history):
        e = h["epoch"]
        if e % args.render_every != 0 and e != last_epoch:
            continue

        for fold in ["train", "val"]:

            sample_results = h["sample_results"][fold]

            # sample results visualization
            X, J, P, M, A, D, Y, decoder_out, convar_out, decoder_fake_out = [
                sample_results[k][:n_rows_fig]
                for k in [
                    "X",
                    "J",
                    "P",
                    "M",
                    "A",
                    "D",
                    "Y",
                    "decoder_out",
                    "convar_out",
                    "decoder_fake_out",
                ]
            ]

            row_length = vis.row_length(*[t[0] for t in [X, J, P, M, A, D, Y]]) + 2

            fig, axes = plt.subplots(n_rows_fig, row_length, figsize=(20, 30))

            for row_no, (x, j, p, m, a, d, y, dec_out, dec_fake_out) in enumerate(
                zip(X, J, P, M, A, D, Y, decoder_out, decoder_fake_out)
            ):

                vis.visualize_sample(
                    x,
                    j,
                    p,
                    m,
                    a,
                    d,
                    y,
                    ax_row=axes[row_no],
                    title_prefixes={0: f"{e} {fold} ", 1: f"gt {y}"},
                    drawing_fn=img_with_mask,
                )
                dec_out = (
                    dec_out.reshape(img_shape, img_shape)
                    if convar_in_channels == 1
                    else dec_out.transpose(1, 2, 0)
                )
                axes[row_no][-2].set_title(f"WAE encdec")
                axes[row_no][-2].imshow(dec_out)

                dec_fake_out = (
                    dec_fake_out.reshape(img_shape, img_shape)
                    if convar_in_channels == 1
                    else dec_fake_out.transpose(1, 2, 0)
                )
                axes[row_no][-1].set_title("WAE sample")
                axes[row_no][-1].imshow(dec_fake_out)

            title = f"{e}_{fold}_predictions"
            plt.suptitle(title)
            plt.savefig(epochs_path / f"{title}.png", bbox_inches="tight", pad_inches=0)

            # convar out visualization

            n_rows_convar, n_cols = convar_out.shape[:2]

            fig, axes = plt.subplots(
                n_rows_convar,
                n_cols,
                figsize=(
                    n_cols // 2,
                    n_rows_convar // 2,
                ),
            )
            for i, row in enumerate(convar_out):
                for j, img in enumerate(row):
                    ax = axes[i, j]
                    ax.imshow(img)
                    ax.axis("off")

            plt.savefig(
                epochs_path / f"{e}_{fold}_convar.png",
                bbox_inches="tight",
                pad_inches=0,
            )
