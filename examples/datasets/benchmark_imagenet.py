import argparse
import orchpy
import cProfile

import arrays.single as single
import arrays.dist as dist

import datasets.imagenet as imagenet
import orchpy.worker as worker

parser = argparse.ArgumentParser(description='Parse addresses for the worker to connect to.')
parser.add_argument("--scheduler-address", default="127.0.0.1:10001", type=str, help="the scheduler's address")
parser.add_argument("--objstore-address", default="127.0.0.1:20001", type=str, help="the objstore's address")
parser.add_argument("--worker-address", default="127.0.0.1:40001", type=str, help="the worker's address")

@op.distributed([np.ndarray], [np.ndarray])
def single_mean_image(images):
  return images.sum(axis=0)

@op.distributed([np.ndarray], [np.ndarray])
def mean_image(images):
  mean_image_refs = [single_mean_image(image) for image in images]
  mean_images = [op.pull(image) for image in mean_image_refs]
  result = np.zeros_like(mean_images[0])
  for i in range(len(mean_images)):
    result += mean_images[i]
  return result

if __name__ == '__main__':
  args = parser.parse_args()
  worker.connect(args.scheduler_address, args.objstore_address, args.worker_address)
  orchpy.register_module(imagenet)
  orchpy.register_module(single)
  orchpy.register_module(dist)
  # worker.main_loop()
  worker.main_loop(profile_filename='profile-'+args.worker_address)
