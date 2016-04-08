import orchpy as op
import orchpy.services as services
import wordcount
import benchmark
import os
import time
import IPython

test_dir = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.join(test_dir, "benchmark.py")
services.start_cluster(num_workers=2, worker_path=test_path)

time.sleep(1)

op.connect("127.0.0.1:10001", "127.0.0.1:20001", "127.0.0.1:11111")

basedir = "/home/pcmoritz/wordcount/"

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

urls_copy = [url.split(".")[0] + " (copy).txt" for url in urls]

urls.extend(urls_copy)

import IPython
IPython.embed()

textfiles = [wordcount.load_textfile(url) for url in urls]

a = time.time(); result = wordcount.sum_by_key_return_len(*[wordcount.count_words(textfile) for textfile in textfiles]); op.pull(result); b = time.time() - a

# data = op.pull(imagenet.load_images_from_tars(images))
# a = time.time(); op.pull(imagenet.mean_image(data)); b = time.time() - a

# print "time to load images is", b
