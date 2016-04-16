from __future__ import division
import urllib2
from collections import Counter
from collections import defaultdict
import orchpy as op
import time
import numpy as np

# TODO(pcm): Replace the greedy algorithm by the Karmarkar-Karp heuristic
def split_tasks(sizes, num_partitions):
  sorted_sizes = sorted(sizes, reverse=True)
  indices = range(num_partitions)
  totals = [0 for i in indices]
  outlist = [[] for i in indices]
  for size in sorted_sizes:
    m = min(indices, key=lambda i: totals[i])
    totals[m] += size
    outlist[m].append(size)
  return outlist

def count_words_local(data):
  c = Counter()
  for s in data:
    c.update(s.split())
  return c

def test(num_reducers, d):
  partitions = [{} for i in range(num_reducers)]
  for key, val in d.iteritems():
    partitions[hash(key) % num_reducers][key] = val
  return np.array([op.push(partition) for partition in partitions])

@op.distributed([int, str, str, None], [np.ndarray])
def map_and_split(num_reducers, *data):
  result = count_words_local(data)
  partitions = [{} for i in range(num_reducers)]
  for key, val in result.iteritems():
    partitions[hash(key) % num_reducers][key] = val
  return np.array([op.push(partition) for partition in partitions])

@op.distributed([dict, None], [dict])
def do_reduce(*dicts):
  result = defaultdict(int)
  for d in dicts:
    d_get = d.get
    for key in d.keys():
      result[key] += d_get(key)
  return result

@op.distributed([int, int, list], [dict])
def mapreduce(num_mappers, num_reducers, urls):
  with open("/tmp/timing", 'w') as outfile:
    a = time.time()
    data = [load_textfile(url) for url in urls]
    content_refs, size_refs = zip(*data)
    sizes = [op.pull(size) for size in size_refs]
    b = time.time() - a
    outfile.write("loading files took " + str(b) + "s\n")
    a = time.time()
    partitions = split_tasks(sizes, num_mappers)
    b = time.time() - a
    outfile.write("splitting took " + str(b) + "s\n")
    a = time.time()
    map_results = []
    for (i, partition) in enumerate(partitions):
      map_results.append(map_and_split(num_reducers, *[content_refs[j] for j in partition]))
    X = []
    for map_result in map_results:
      X.append(op.pull(map_result))
    b = time.time() - a
    outfile.write("mapping took " + str(b) + "s\n")
    a = time.time()
    reduce_results = []
    for j in range(num_reducers):
      reduce_results.append(do_reduce(*[X[i][j] for i in range(num_mappers)]))
    b = time.time() - a
    outfile.write("submitting reducers took " + str(b) + "s\n")
    a = time.time()
    result = {}
    for i in range(num_mappers):
      result.update(op.pull(reduce_results[i]))
    b = time.time() - a
    outfile.write("reducing took " + str(b) + "s\n")
    return result

# files = books.values()

# data = urllib2.urlopen(files[0]).read()

# this is incorrect use default dict with a zero and accumulate into that!
# def sum_up(dict1, dict2):
#   result = {}
#   for key in dict1.keys():
#     result[key] = dict1[key] + dict2[key]
#   return result

@op.distributed([str], [str, int])
def load_textfile(url):
  # return urllib2.urlopen(url).read()
  result = open(url, "r").read()
  return result, len(result)

@op.distributed([str], [dict])
def count_words(data):
  word_list = data.split()
  return Counter(word_list)

# @op.distributed([str], [dict])
# def parse_time(data):
#   word_list = data.split()
#  d = Counter(word_list)

# @op.distributed
# def count_words(data: str) -> dict:
#     # ...

@op.distributed([str], [dict])
def count_words_fast(data):
 counter = defaultdict(int)
 for k in data:
   counter[k] += 1
 return dict(counter)

@op.distributed([dict, None], [dict])
def sum_by_key(*dicts):
  result = defaultdict(int)
  for d in dicts:
    d_get = d.get
    for key in d.keys():
      result[key] += d_get(key)
  return result

@op.distributed([dict, None], [int])
def sum_by_key_return_len(*dicts):
  result = defaultdict(int)
  for d in dicts:
    d_get = d.get
    for key in d.keys():
      result[key] += d_get(key)
  return len(result)

def red(*dicts):
  result = defaultdict(int)
  for d in dicts:
    d_get = d.get
    for key in d.keys():
      result[key] += d_get(key)
  return result

@op.distributed([str, None], [dict])
def map_reduce(*data):
  c = Counter()
  for s in data:
    c.update(s.split())
  return c

@op.distributed([str, None], [int])
def map_reduce2(*data):
  c = Counter()
  for s in data:
    c.update(s.split())
  return 1
