from typing import Any, Optional

import numpy as np
from numpy.random import Generator


def np_random(seed: Optional[int] = None) -> np.random.Generator:
    """Get a numpy random number generator."""
    rng = Generator(np.random.PCG64(seed))
    return rng
