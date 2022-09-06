def test_get_target_log_R():
    from pyTOPSScrape.misc.utils import get_target_log_R
    import numpy as np

    assert all(np.equal(np.arange(-8.0, 1.5, 0.5), get_target_log_R()))


def test_get_target_log_T():
    import numpy as np
    target = np.load("./T.npy")

    from pyTOPSScrape.misc.utils import get_target_log_T

    result = get_target_log_T()

    assert all([x == y for x, y in zip(target, result)])


