from typing import Tuple

import torch
from torch import nn

from inpainting.custom_layers import Reshape


class UNet(nn.Module):
    """
    UNet adapted from
    https://github.com/steveli/misgan
    """

    def __init__(
        self, input_nc=3, output_nc=3, ngf=64, layers=5, norm_layer=nn.BatchNorm2d
    ):
        super().__init__()

        mid_layers = layers - 2
        fact = 2 ** mid_layers

        unet_block = UnetSkipConnectionBlock(
            ngf * fact,
            ngf * fact,
            input_nc=None,
            submodule=None,
            norm_layer=norm_layer,
            innermost=True,
        )

        for _ in range(mid_layers):
            half_fact = fact // 2
            unet_block = UnetSkipConnectionBlock(
                ngf * half_fact,
                ngf * fact,
                input_nc=None,
                submodule=unet_block,
                norm_layer=norm_layer,
            )
            fact = half_fact

        unet_block = UnetSkipConnectionBlock(
            output_nc,
            ngf,
            input_nc=input_nc,
            submodule=unet_block,
            outermost=True,
            norm_layer=norm_layer,
        )

        self.model = unet_block

    def forward(self, input):
        return self.model(input)


class UnetSkipConnectionBlock(nn.Module):
    def __init__(
        self,
        outer_nc,
        inner_nc,
        input_nc=None,
        submodule=None,
        outermost=False,
        innermost=False,
        norm_layer=nn.BatchNorm2d,
    ):
        super().__init__()
        self.outermost = outermost
        use_bias = norm_layer == nn.InstanceNorm2d
        if input_nc is None:
            input_nc = outer_nc
        downconv = nn.Conv2d(
            input_nc, inner_nc, kernel_size=4, stride=2, padding=1, bias=use_bias
        )
        downrelu = nn.LeakyReLU(0.2, True)
        if norm_layer is not None:
            downnorm = norm_layer(inner_nc)
            upnorm = norm_layer(outer_nc)
        uprelu = nn.ReLU(True)

        if outermost:
            upconv = nn.ConvTranspose2d(
                inner_nc * 2, outer_nc, kernel_size=4, stride=2, padding=1
            )
            down = [downconv]
            up = [uprelu, upconv]
            model = down + [submodule] + up
        elif innermost:
            upconv = nn.ConvTranspose2d(
                inner_nc, outer_nc, kernel_size=4, stride=2, padding=1, bias=use_bias
            )
            down = [downrelu, downconv]
            up = [uprelu, upconv]
            if norm_layer is not None:
                up.append(upnorm)
            model = down + up
        else:
            upconv = nn.ConvTranspose2d(
                inner_nc * 2,
                outer_nc,
                kernel_size=4,
                stride=2,
                padding=1,
                bias=use_bias,
            )
            down = [downrelu, downconv]
            up = [uprelu, upconv]
            if norm_layer is not None:
                down.append(downnorm)
                up.append(upnorm)

            model = down + [submodule] + up

        self.model = nn.Sequential(*model)

    def forward(self, x):
        if self.outermost:
            return self.model(x)
        else:
            model_output = self.model(x)
            return torch.cat([x, model_output], 1)


def conv_relu_bn(
    in_channels: int, out_channels: int, kernel_size: int = 3, dropout: float = 0.0
) -> nn.Module:
    modules = [
        nn.Conv2d(in_channels, out_channels, kernel_size, padding=kernel_size // 2),
        nn.ReLU(),
        nn.BatchNorm2d(out_channels),
    ]

    if dropout != 0:
        modules.append(nn.Dropout(dropout))

    return nn.Sequential(*modules)


def down_up_backbone_v2(
    chw: Tuple[int, int, int],
    depth: int,
    block_length: int = 1,
    first_channels: int = 16,
    last_channels: int = 1,
    kernel_size: int = 3,
    latent_size: int = -1,
    dropout: float = 0.0,
) -> Tuple[nn.Module, ...]:
    c, h, w = chw
    down = [nn.Conv2d(c, first_channels, kernel_size=3, padding=1)]

    up = [nn.Conv2d(last_channels, last_channels, kernel_size=3, padding=1)]
    for i in range(depth):
        up_block = []
        down_block = []
        for j in range(block_length):
            down_block = down_block + [
                conv_relu_bn(
                    first_channels * (2 ** (i - 1))
                    if (j == 0 and i != 0)
                    else first_channels * (2 ** i),
                    first_channels * (2 ** i),
                    kernel_size=kernel_size,
                    dropout=dropout,
                )
            ]

            up_block = [
                conv_relu_bn(
                    last_channels * (2 ** i),
                    last_channels * (2 ** (i - 1))
                    if (j == 0 and i != 0)
                    else last_channels * (2 ** i),
                    kernel_size=kernel_size,
                    dropout=dropout,
                )
            ] + up_block

        down_block = down_block + [
            nn.Conv2d(
                first_channels * (2 ** i),
                first_channels * (2 ** i),
                kernel_size=3,
                padding=1,
                stride=2,
            )
        ]

        up_block = [
            nn.ConvTranspose2d(
                last_channels * (2 ** i),
                last_channels * (2 ** i),
                kernel_size=3,
                padding=1,
                stride=2,
                output_padding=1,
            )
        ] + up_block

        down = down + down_block
        up = up_block + up


    if latent_size > 0:
        h_d = h // (2 ** depth)
        w_d = w // (2 ** depth)
        c_d_i = first_channels * (2 ** (depth - 1))
        c_d_o = last_channels * (2 ** (depth - 1))

        enc_out_size = c_d_i * h_d * w_d
        dec_in_size = c_d_o * h_d * w_d

        down.append(
            nn.Sequential(
                nn.ReLU(),
                Reshape((-1, enc_out_size)),
                nn.Linear(enc_out_size, latent_size),
            )
        )
        up = [
            nn.Sequential(
                nn.Linear(latent_size, dec_in_size),
                Reshape((-1, c_d_o, h_d, w_d)),
                nn.ReLU(),
            )
        ] + up

    return nn.Sequential(*down), nn.Sequential(*up)
