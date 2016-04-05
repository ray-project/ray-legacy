import orchpy.services as services
import imagenet
import benchmark

test_path = os.path.join(test_dir, "benchmark.py")
services.start_cluster(num_workers=1, worker_path=test_path)

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

a = time.time(); orchpy.pull(imagenet.load_images_from_tars(images)); b = time.time() - a
print "time to load images is", b
