import argparse
import boto3
import tarfile, io
import numpy as np
import PIL.Image

import orchpy as op
import orchpy.services as services
import orchpy.worker as worker
import arrays.dist as dist

s3 = boto3.client('s3')

@op.distributed([str], [np.ndarray])
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
    rgbimg = PIL.Image.new("RGB", img.size)
    rgbimg.paste(img)
    img = rgbimg.resize((256, 256), PIL.Image.ANTIALIAS)
    tensors.append(np.array(img).reshape(1, 256, 256, 3))
  return np.concatenate(tensors)

@op.distributed([List[str]], [DistArray])
def load_images_from_tars(tar_paths):
  objrefs = []
  for tar_path in tar_paths:
    objrefs.append(download_and_parse_tar(tar_path))
  shapes = dist.shape(objrefs)
  print "shapes ", shapes
