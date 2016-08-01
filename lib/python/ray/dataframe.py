import pandas as pd
import ray

class DataFrameChunk(pd.core.frame.DataFrame):
  @staticmethod
  def deserialize(primitives):
    return pd.read_json(primitives)

  def serialize(self):
    return self.to_json()

class DDataFrame(object):
  def __init__(self, data, chunk_row_size=100)
    if isinstance(data, list):
      self.objectids = data
    else:
      self.objectids = [ray.put(DataFrameChunk(data[(i*chunk_row_size): (i+1) * chunk_row_size])) for i in range(len(data)/ chunk_row_size + 1)]
  
  @staticmethod
  def deserialize(primitives):
    return DDataFrame(primitives)

  def serialize(self):
    return self.objectids
  
  def todataframe(self):
    return pd.concat([ray.get(dataframe_ref) for dataframe_ref in self.objectids], ignore_index=True)
  
  def __getitem__(self, key):
    return DDataFrame([chunk_getitem(dfc, key) for dfc in self.objectids])

  
@ray.remote([DataFrameChunk, any], [DataFrameChunk])
def chunk_getitem(dfc, key):
  return dfc[key]
