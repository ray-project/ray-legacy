import urllib2
from collections import Counter
from collections import defaultdict
import orchpy as op

# files = books.values()

# data = urllib2.urlopen(files[0]).read()

# this is incorrect use default dict with a zero and accumulate into that!
# def sum_up(dict1, dict2):
#   result = {}
#   for key in dict1.keys():
#     result[key] = dict1[key] + dict2[key]
#   return result

@op.distributed([str], [str])
def load_textfile(url):
  # return urllib2.urlopen(url).read()
  return open(url, "r").read()

@op.distributed([str], [dict])
def count_words(data):
  word_list = data.split()
  return Counter(word_list)

# @op.distributed([str], [dict])
# def count_words_fast(data):
#     counter = defaultdict(int)
#     for k in data:
#         counter[k] += 1
#     return dict(counter)

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
