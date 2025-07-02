import pytest
import numpy as np

from scotclimpact.db import _make_edges

@pytest.mark.parametrize("dim", [
    np.linspace(0, 10, 11),
    np.linspace(17, 18, num=1200),
    np.linspace(3, 4, num=1200),
])
def test_make_edges(dim):
    upper_bound, lower_bound = _make_edges(dim)

    for i, x in enumerate(dim):
        if i > 0: 
            assert upper_bound[dim[i-1]] == lower_bound[dim[i]], f'{i}, {dim[i]}, {dim[i-1]}'
        if i < dim.shape[0]-1:
            assert lower_bound[dim[i+1]] == upper_bound[dim[i]], f'{i}, {dim[i]}, {dim[i-1]}'


