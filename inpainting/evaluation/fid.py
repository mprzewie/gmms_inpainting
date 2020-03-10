"""Code adapted from https://github.com/mseitzer/pytorch-fid
"""
from pathlib import Path
import torch
import numpy as np
from scipy import linalg
import time
import sys


use_cuda = torch.cuda.is_available()
device = torch.device('cuda' if use_cuda else 'cpu')

FEATURE_DIM = 2048
RESIZE = 299


def get_activations(image_iterator, images, model, feature_dim, verbose=True):
    """Calculates the activations of the pool_3 layer for all images.
    Params:
    -- image_iterator
                   : A generator that generates a batch of images at a time.
    -- images      : Number of images that will be generated by
                     image_iterator.
    -- model       : Instance of inception model
    -- verbose     : If set to True and parameter out_step is given, the number
                     of calculated batches is reported.
    Returns:
    -- A numpy array of dimension (num images, dims) that contains the
       activations of the given tensor when feeding inception with the
       query tensor.
    """
    model.eval()

    if not sys.stdout.isatty():
        verbose = False

    pred_arr = np.empty((images, feature_dim))
    end = 0
    t0 = time.time()

    for batch in image_iterator:
        if not isinstance(batch, torch.Tensor):
            batch = batch[0]
        start = end
        batch_size = batch.shape[0]
        end = start + batch_size

        with torch.no_grad():
            batch = batch.to(device)
            pred = model(batch)[0]
            batch_feature = pred.cpu().numpy().reshape(batch_size, -1)
            pred_arr[start:end] = batch_feature

        if verbose:
            print('\rProcessed: {}   time: {:.2f}'.format(
                end, time.time() - t0), end='', flush=True)

    assert end == images

    if verbose:
        print(' done')

    return pred_arr


def calculate_frechet_distance(mu1, sigma1, mu2, sigma2, eps=1e-6):
    """Numpy implementation of the Frechet Distance.
    The Frechet distance between two multivariate Gaussians X_1 ~ N(mu_1, C_1)
    and X_2 ~ N(mu_2, C_2) is
            d^2 = ||mu_1 - mu_2||^2 + Tr(C_1 + C_2 - 2*sqrt(C_1*C_2)).
    Stable version by Dougal J. Sutherland.
    Params:
    -- mu1   : Numpy array containing the activations of a layer of the
               inception net (like returned by the function 'get_predictions')
               for generated samples.
    -- mu2   : The sample mean over activations, precalculated on an
               representive data set.
    -- sigma1: The covariance matrix over activations for generated samples.
    -- sigma2: The covariance matrix over activations, precalculated on an
               representive data set.
    Returns:
    --   : The Frechet Distance.
    """

    mu1 = np.atleast_1d(mu1)
    mu2 = np.atleast_1d(mu2)

    sigma1 = np.atleast_2d(sigma1)
    sigma2 = np.atleast_2d(sigma2)

    assert mu1.shape == mu2.shape, \
        'Training and test mean vectors have different lengths'
    assert sigma1.shape == sigma2.shape, \
        'Training and test covariances have different dimensions'

    diff = mu1 - mu2

    # Product might be almost singular
    covmean, _ = linalg.sqrtm(sigma1.dot(sigma2), disp=False)
    if not np.isfinite(covmean).all():
        msg = ('fid calculation produces singular product; '
               'adding %s to diagonal of cov estimates') % eps
        print(msg)
        offset = np.eye(sigma1.shape[0]) * eps
        covmean = linalg.sqrtm((sigma1 + offset).dot(sigma2 + offset))

    # Numerical error might give slight imaginary component
    if np.iscomplexobj(covmean):
        if not np.allclose(np.diagonal(covmean).imag, 0, atol=1e-3):
            m = np.max(np.abs(covmean.imag))
            raise ValueError('Imaginary component {}'.format(m))
        covmean = covmean.real

    tr_covmean = np.trace(covmean)

    return (diff.dot(diff) + np.trace(sigma1) +
            np.trace(sigma2) - 2 * tr_covmean)


def calculate_activation_statistics(image_iterator, images, model, feature_dim=FEATURE_DIM, verbose=False):
    """Calculation of the statistics used by the FID.
    Params:
    -- image_iterator
                   : A generator that generates a batch of images at a time.
    -- images      : Number of images that will be generated by
                     image_iterator.
    -- model       : Instance of inception model
    -- verbose     : If set to True and parameter out_step is given, the
                     number of calculated batches is reported.
    Returns:
    -- mu    : The mean over samples of the activations of the pool_3 layer of
               the inception model.
    -- sigma : The covariance matrix of the activations of the pool_3 layer of
               the inception model.
    """
    act = get_activations(image_iterator, images, model, feature_dim, verbose)
    mu = np.mean(act, axis=0)
    sigma = np.cov(act, rowvar=False)
    return mu, sigma


class FID:
    def __init__(self, data_name, verbose=True):
        block_idx = InceptionV3.BLOCK_INDEX_BY_DIM[FEATURE_DIM]
        model = InceptionV3([block_idx], RESIZE).to(device)
        self.verbose = verbose

        stats_dir = Path('fid_stats')
        stats_file = stats_dir / '{}_act_{}_{}.npz'.format(
            data_name, FEATURE_DIM, RESIZE)

        try:
            f = np.load(str(stats_file))
            mu, sigma = f['mu'], f['sigma']
            f.close()
        except FileNotFoundError:
            data_loader, images = self.complete_data()
            mu, sigma = calculate_activation_statistics(
                data_loader, images, model, verbose)
            stats_dir.mkdir(parents=True, exist_ok=True)
            np.savez(stats_file, mu=mu, sigma=sigma)

        self.model = model
        self.stats = mu, sigma

    def complete_data(self):
        raise NotImplementedError

    def fid(self, image_iterator, images):
        mu, sigma = calculate_activation_statistics(
            image_iterator, images, self.model, verbose=self.verbose)
        return calculate_frechet_distance(mu, sigma, *self.stats)


class BaseSampler:
    def __init__(self, images):
        self.images = images

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.images:
            batch = self.sample()
            batch_size = batch.shape[0]
            self.n += batch_size
            if self.n > self.images:
                return batch[:-(self.n - self.images)]
            return batch
        else:
            raise StopIteration

    def sample(self):
        raise NotImplementedError


class BaseImputationSampler:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def __iter__(self):
        self.data_iter = iter(self.data_loader)
        return self

    def __next__(self):
        data, mask = next(self.data_iter)[:2]
        data = data.to(device)
        mask = mask.float()[:, None].to(device)
        imputed_data = self.impute(data, mask)
        return mask * data + (1 - mask) * imputed_data

    def impute(self, data, mask):
        raise NotImplementedError

