from typing import Callable

import numpy as np
import torch
from torch.distributions import MultivariateNormal

InpainterLossFn = Callable[[
                               torch.Tensor,
                               torch.Tensor,
                               torch.Tensor,
                               torch.Tensor,
                               torch.Tensor,
                               torch.Tensor
                           ],
                           torch.Tensor
]


def nll_masked_sample_loss_v1(
        x: torch.Tensor,
        j: torch.Tensor,
        p: torch.Tensor,
        m: torch.Tensor,
        a: torch.Tensor,
        d: torch.Tensor
) -> torch.Tensor:
    """
    c - channels
    h - height
    w - width
    mx - n_mixes
    aw - covariance matrix width
    Args:
        x: [c, h, w]
        j: [h, w]
        p: [mx]
        m: [mx, c*h*w]
        a: [mx, aw, c*h*w]
        d: [mx, c*h*w]

    Returns:

    """
    x_c_hw = x.reshape(x.shape[0], x.shape[1] * x.shape[2])
    j_hw = j.reshape(-1)
    mask_inds = (j_hw == 0).nonzero().squeeze()
    x_masked = torch.index_select(x_c_hw, 1, mask_inds)
    a_masked = torch.index_select(a, 2, mask_inds)
    m_masked, d_masked = [
        torch.index_select(t, 1, mask_inds)
        for t in [m, d]
    ]
    covs = torch.bmm(a_masked.transpose(1, 2), a_masked)
    losses_for_p = []
    for (p_i, m_i, d_i, cov_i) in zip(p, m_masked, d_masked, covs):
        if cov_i.shape[1] > 0:
            cov = cov_i + torch.diag(d_i ** 2)
            mvn_d = MultivariateNormal(m_i, cov)  # calculate this manually
            loss_for_p = - mvn_d.log_prob(x_masked.float())
            losses_for_p.append(p_i * loss_for_p)
    return torch.stack(losses_for_p).sum()


log_2pi = torch.log(torch.tensor(2 * np.pi))


def nll_masked_sample_loss_v2(
        x: torch.Tensor,
        j: torch.Tensor,
        p: torch.Tensor,
        m: torch.Tensor,
        a: torch.Tensor,
        d: torch.Tensor
) -> torch.Tensor:
    """
    A potentially vectorized version of v1
    c - channels
    h - height
    w - width
    mx - n_mixes
    aw - covariance matrix width
    Args:
        x: [c, h, w]
        j: [c, h, w]
        p: [mx]
        m: [mx, c*h*w]
        a: [mx, aw, c*h*w]
        d: [mx, c*h*w]

    Returns:

    """
    x_c_hw = x.reshape(-1)
    j_hw = j.reshape(-1)
    mask_inds = (j_hw == 0).nonzero().squeeze()
    x_masked = torch.index_select(x_c_hw, 0, mask_inds).float()
    a_masked = torch.index_select(a, 2, mask_inds)
    m_masked, d_masked = [
        torch.index_select(t, 1, mask_inds)
        for t in [m, d]
    ]
    covs = a_masked.transpose(1, 2).bmm(a_masked) + torch.diag_embed(d_masked ** 2)
    x_minus_means = (x_masked - m_masked).unsqueeze(1)
    log_noms = x_minus_means.bmm(covs.inverse()).bmm(x_minus_means.transpose(1, 2))
    log_dets = covs.det().log()
    losses = p * (1/2) * (log_noms + log_dets + log_2pi * x_masked.shape[0])
    return losses.sum()


def inpainter_batch_loss_fn(
        sample_loss: Callable[[
                                  torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor
                              ], torch.Tensor] = nll_masked_sample_loss_v1) -> InpainterLossFn:
    def loss(
            X: torch.Tensor,
            J: torch.Tensor,
            P: torch.Tensor,
            M: torch.Tensor,
            A: torch.Tensor,
            D: torch.Tensor,
    ) -> torch.Tensor:
        return torch.stack([
            sample_loss(x, j, p, m, a, d)
            for (x, j, p, m, a, d) in zip(X, J, P, M, A, D)
        ]).mean()

    return loss


def r2_total_batch_loss(
        X: torch.Tensor,
        J: torch.Tensor,
        P: torch.Tensor,
        M: torch.Tensor,
        A: torch.Tensor,
        D: torch.Tensor,
) -> torch.Tensor:
    return ((X - M[:, 0, :]) ** 2).mean()


def r2_masked_sample_loss(
        x: torch.Tensor,
        j: torch.Tensor,
        p: torch.Tensor,
        m: torch.Tensor,
        a: torch.Tensor,
        d: torch.Tensor
) -> torch.Tensor:
    """A very unvectorized loss"""
    x_c_hw = x.reshape(x.shape[0], x.shape[1] * x.shape[2])
    j_hw = j.reshape(-1)
    mask_inds = (j_hw == 0).nonzero().squeeze()
    x_masked = torch.index_select(x_c_hw, 1, mask_inds)

    m_masked, d_masked = [
        torch.index_select(t, 1, mask_inds)
        for t in [m, d]
    ]
    return torch.stack([p_i * ((x_masked - m_i) ** 2).sum() for (p_i, m_i) in zip(p, m_masked)]).sum()


nll_masked_batch_loss = inpainter_batch_loss_fn(nll_masked_sample_loss_v2)
r2_masked_batch_loss = inpainter_batch_loss_fn(r2_masked_sample_loss)
