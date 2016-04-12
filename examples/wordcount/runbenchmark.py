import orchpy as op
import orchpy.services as services
import wordcount
import benchmark
import os
import time
import IPython

test_dir = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.join(test_dir, "benchmark.py")
services.start_cluster(num_workers=10, worker_path=test_path)

# services.start_cluster(num_workers=16, worker_path="benchmark.py")

time.sleep(1)

op.connect("127.0.0.1:10001", "127.0.0.1:20001", "127.0.0.1:11111")

basedir = "/home/ubuntu/wordcount/"
# basedir = "/home/pcmoritz/wordcount/"

books = {
  "War and Peace": basedir + "pg2600.txt",
  "Alice's Adventures in Wonderland": basedir + "pg11.txt",
  "The Complete Works of William Shakespeare": basedir + "pg100.txt",
  "Leviathan by Thomas Hobbes": basedir + "pg3207.txt",
  "The Brothers Karamazov by Fyodor Dostoyevsky": basedir + "28054-0.txt",
  "The Bible": basedir + "pg10.txt",
  "Moby Dick": basedir + "pg2701.txt",
  "The Iliad": basedir + "pg6130.txt",
  "Peter Norvig dataset": basedir + "big.txt"
}

urls = books.values()

# urls = urls + urls + urls + urls + urls + urls + urls + urls

urls = 34 * [urls[0]]

urls_copy = [url.split(".")[0] + " (copy).txt" for url in urls]

from collections import Counter
from collections import defaultdict

def red(*dicts):
  result = defaultdict(int)
  for d in dicts:
    d_get = d.get
    for key in d.keys():
      result[key] += d_get(key)
  return result

from collections import Counter

def map_reduce2(*data):
  dicts = []
  for s in data:
    word_list = s.split()
    dicts.append(Counter(word_list))
  return red(*dicts)

import IPython
IPython.embed()

load = [wordcount.load_textfile(url) for url in urls]
content_refs, size_refs = zip(*load)
sizes = [op.pull(size) for size in size_refs]
res = wordcount.split_partitions(sizes, 8)

textfiles = [wordcount.load_textfile(url) for url in urls]

a = time.time(); y = wordcount.map_reduce(*[content_refs[i] for i in res[0]]); d = op.pull(y); b = time.time() - a


a = time.time();
result = wordcount.sum_by_key(*[wordcount.count_words(textfile) for textfile in textfiles]);
op.pull(result);
b = time.time() - a

a = time.time();
counts = [wordcount.count_words(textfile) for textfile in textfiles];
result = wordcount.sum_by_key_return_len(wordcount.sum_by_key(*counts[1:36]), wordcount.sum_by_key(*counts[36:72]));
op.pull(result); b = time.time() - a

a = time.time(); x = wordcount.map_reduce2(*textfiles[0:8]); y = wordcount.map_reduce2(*textfiles[8:16]); z = wordcount.map_reduce2(*textfiles[16:24]); w = wordcount.map_reduce2(*textfiles[24:32]); X = op.pull(x); Y = op.pull(y); Z = op.pull(z); W = op.pull(w); b = time.time() - a

perm = np.random.permutation(len(textfiles))

textfiles = list(np.array(textfiles)[perm])

a = time.time(); x = wordcount.map_reduce2(*textfiles[0:8]); X = op.pull(x); b = time.time() - a
a = time.time(); x = wordcount.map_reduce2(*textfiles[8:16]); X = op.pull(x); b = time.time() - a
a = time.time(); x = wordcount.map_reduce2(*textfiles[16:24]); X = op.pull(x); b = time.time() - a
a = time.time(); x = wordcount.map_reduce2(*textfiles[24:32]); X = op.pull(x); b = time.time() - a
# this is on 4 workers
# with serialization: 4.1s
# without serialization 3.36s
# serial time: 8.52s

pulled_textfiles = [op.pull(textfile) for textfile in textfiles]

a = time.time(); d = map_reduce2(*pulled_textfiles); b = time.time() - a

# 8.52 s

# data = op.pull(imagenet.load_images_from_tars(images))
# a = time.time(); op.pull(imagenet.mean_image(data)); b = time.time() - a

# print "time to load images is", b

a = time.time(); objrefs = [wordcount.map_reduce(*[content_refs[i] for i in res[j]]) for j in range(2)]; op.pull(wordcount.sum_by_key_return_len(*objrefs)); b = time.time() - a

a = time.time(); objrefs = [wordcount.map_reduce(*[content_refs[i] for i in res[j]]) for j in range(4)]; [op.pull(objref) for objref in objrefs]; b = time.time() - a
