import numpy as np
import ray.array.remote as ra
import ray

from core import *

@ray.remote
def normal(shape, block_size=BLOCK_SIZE):
  num_blocks = DistArray.compute_num_blocks(shape, block_size)
  objectids = np.empty(num_blocks, dtype=object)
  for index in np.ndindex(*num_blocks):
    objectids[index] = ra.random.normal.remote(DistArray.compute_block_shape(index, shape, block_size))
  result = DistArray(shape, block_size=block_size, objectids=objectids)
  return result
