from __future__ import division

import numpy as np

from . import common_args
from ..util import nonuniform_scale_samples, scale_samples, read_param_file


def sample(problem, N):
    """Generate model inputs using Latin hypercube sampling (LHS).

    Returns a NumPy matrix containing the model inputs generated by Latin
    hypercube sampling.  The resulting matrix contains N rows and D columns,
    where D is the number of parameters.

    Parameters
    ----------
    problem : dict
        The problem definition
    N : int
        The number of samples to generate
    calc_second_order : bool
        Calculate second-order sensitivities (default True)
    """
    D = problem['num_vars']

    result = np.zeros([N, D])
    temp = np.zeros([N])
    d = 1.0 / N

    for i in range(D):

        for j in range(N):
            temp[j] = np.random.uniform(
                low=j * d, high=(j + 1) * d, size=1)[0]

        np.random.shuffle(temp)

        for j in range(N):
            result[j, i] = temp[j]

    if not problem.get('dists'):
        # scaling values out of 0-1 range with uniform distributions
        scale_samples(result, problem['bounds'])
        return result
    else:
        # scaling values to other distributions based on inverse CDFs
        scaled_result = nonuniform_scale_samples(result, problem['bounds'], problem['dists'])
        return scaled_result


if __name__ == "__main__":

    parser = common_args.create()
    parser.add_argument(
        '-n', '--samples', type=int, required=True, help='Number of Samples')
    args = parser.parse_args()
    np.random.seed(args.seed)
    problem = read_param_file(args.paramfile)

    param_values = sample(problem, args.samples)
    np.savetxt(args.output, param_values, delimiter=args.delimiter,
               fmt='%.' + str(args.precision) + 'e')
