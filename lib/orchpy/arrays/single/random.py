from typing import List
import numpy as np
import orchpy as op

@op.distributed([List[int], str], [np.ndarray])
def normal(shape, dtype_name):
  return np.random.normal(size=shape).astype(dtype_name)

@op.distributed([List[int], int, int, str], [np.ndarray])
def randint(shape, low, high, dtype_name):
  return np.random.randint(low, high, size=shape).astype(dtype_name)
