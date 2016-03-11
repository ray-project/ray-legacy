import argparse
import boto3
import tarfile, io
import numpy as np
import PIL.Image

import orchpy
import orchpy.services as services
import orchpy.worker as worker

s3 = boto3.client('s3')

parser = argparse.ArgumentParser(description='Parse addresses for the worker to connect to.')
parser.add_argument("--scheduler-address", default="127.0.0.1:10001", type=str, help="the scheduler's address")
parser.add_argument("--objstore-address", default="127.0.0.1:20001", type=str, help="the objstore's address")
parser.add_argument("--worker-address", default="127.0.0.1:40001", type=str, help="the worker's address")

@worker.distributed([str], [np.ndarray])
def download_and_parse_tar(tar_path):
  response = s3.get_object(Bucket='sparknet', Key=tar_path)
  output = io.BytesIO()
  chunk = response['Body'].read(1024 * 8)
  while chunk:
    output.write(chunk)
    chunk = response['Body'].read(1024 * 8)
  output.seek(0) # go to the beginning of the .tar file
  tar = tarfile.open(mode= "r", fileobj=output)
  tensors = []
  for member in tar.getmembers():
    filename = member.path # in a format like 'n02099601_3085.JPEG'
    content = tar.extractfile(member)
    print "decompressing", content.name
    img = PIL.Image.open(content)
    img = img.resize((256, 256), PIL.Image.ANTIALIAS)
    tensors.append(np.array(img).reshape(1, 256, 256, 3))
  return np.concatenate(tensors)

if __name__ == '__main__':
  args = parser.parse_args()
  worker.connect(args.scheduler_address, args.objstore_address, args.worker_address)

  worker.global_worker.register_function(download_and_parse_tar)

  worker.main_loop()
