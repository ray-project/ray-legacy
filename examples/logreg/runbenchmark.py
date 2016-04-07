import orchpy as op
import orchpy.services as services
import logreg
import benchmark
import os
import time
import IPython
import numpy as np

import arrays.dist as dist
import arrays.single as single

test_dir = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.join(test_dir, "benchmark.py")
services.start_cluster(num_workers=10, worker_path=test_path)

time.sleep(1)

op.connect("127.0.0.1:10001", "127.0.0.1:20001", "127.0.0.1:11111")

import IPython
IPython.embed()

batchsize = 100

Xdata = single.random.normal([batchsize, 784], "float32")
ydata = logreg.random_onehot(batchsize, 2)

W = np.zeros((784, 2), dtype="float32")
b = np.zeros(2, dtype="float32")

Wnew, bnew = logreg.train(W, b, Xdata, ydata)
