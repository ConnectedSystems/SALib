
import numpy as np
from . import sobol_sequence
from SALib.util import scale_samples
from typing import Dict, Optional

__all__ = ['sample']


def sample(problem: Dict, N: int, 
           seed: Optional[int] = None):
    """Generates `N` samples for a radial OAT approach.

    Campolongo, F., Saltelli, A., Cariboni, J., 2011. 
    From screening to quantitative sensitivity analysis: A unified approach. 
    Computer Physics Communications 182, 978–988.
    https://www.sciencedirect.com/science/article/pii/S0010465510005321
    DOI: 10.1016/j.cpc.2010.12.039

    Arguments
    ---------
    problem : dict
        SALib problem specification

    N : int
        The number of sample sets to generate

    seed : int
        Seed value to use for np.random.seed

    Example
    -------
    >>> X = sample(problem, N, seed)
    
    `X` will now hold:
    [[x_{1,1}, x_{1,2}, ..., x_{1,p}]
    [b_{1,1}, x_{1,2}, ..., x_{1,p}]
    [x_{1,1}, b_{1,2}, ..., x_{1,p}]
    [x_{1,1}, x_{1,2}, ..., b_{1,p}]
    ...
    [x_{N,1}, x_{N,2}, ..., x_{N,p}]
    [b_{N,1}, x_{N,2}, ..., x_{N,p}]
    [x_{N,1}, b_{N,2}, ..., x_{N,p}]
    [x_{N,1}, x_{N,2}, ..., b_{N,p}]]

    where `p` denotes the number of parameters as
    specified in `problem`

    We can now run the model using the values in `X`. 
    The total number of model evaluations will be `N(p+1)`.

    Returns
    ---------
    numpy.ndarray : An array of samples
    """
    if seed:
        np.random.seed(seed)

    num_vars = problem['num_vars']
    bounds = problem['bounds']

    # Generate the "nominal" values and their perturbations.
    # "We obtain good results by systematically discarding four points (R = r + 4)" 
    # (Campolongo et al. 2011, p 5)
    # in this context, `N := r`
    discard = 4
    R = N + discard

    # Generate the 'nominal' parameter positions
    # Total number of parameter sets = N*(p+1)
    base_sequence = sobol_sequence.sample(R, num_vars)
    subsetted_base = base_sequence[discard:]
    scale_samples(subsetted_base, bounds)

    group = num_vars+1
    sample_set = np.repeat(subsetted_base, repeats=group, axis=0)

    perturbations = sobol_sequence.sample(R+N, num_vars)
    perturbations = perturbations[R:]
    scale_samples(perturbations, bounds)

    grp_start = 0
    for i in range(perturbations.shape[0]):
        mod = np.diag(perturbations[i])

        np.copyto(sample_set[grp_start+1:grp_start+num_vars+1], mod, where=mod != 0.0)
        grp_start += num_vars + 1
    # End for

    return sample_set
