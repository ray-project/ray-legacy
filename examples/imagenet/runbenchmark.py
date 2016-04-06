import orchpy as op
import orchpy.services as services
import imagenet
import benchmark
import os
import time
import IPython

test_dir = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.join(test_dir, "benchmark.py")
services.start_cluster(num_workers=10, worker_path=test_path)

time.sleep(1)

op.connect("127.0.0.1:10001", "127.0.0.1:20001", "127.0.0.1:11111")

images = [
  "ILSVRC2012_img_val/val.000.tar",
  "ILSVRC2012_img_val/val.001.tar",
  "ILSVRC2012_img_val/val.002.tar",
  "ILSVRC2012_img_val/val.003.tar",
  "ILSVRC2012_img_val/val.004.tar",
  "ILSVRC2012_img_val/val.005.tar",
  "ILSVRC2012_img_val/val.006.tar",
  "ILSVRC2012_img_val/val.007.tar",
  "ILSVRC2012_img_val/val.008.tar",
  "ILSVRC2012_img_val/val.009.tar"
]

data = op.pull(imagenet.load_images_from_tars(images))
a = time.time(); op.pull(imagenet.mean_image(data)); b = time.time() - a

# print "time to load images is", b

import IPython
IPython.embed()


