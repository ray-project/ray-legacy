import argparse
import random
import redis
import time

parser = argparse.ArgumentParser(description="Parse addresses for the global scheduler to connect to.")
parser.add_argument("--redis-address", required=True, type=str, help="the port to use for Redis")

# This is a dictionary mapping object IDs to a list of the nodes containing
# that object ID.
cached_object_table = {}
# This is a dictionary mapping function IDs to a list of the nodes (or
# workers?) that can execute that function.
cached_function_table = {}
cached_function_info = {}
cached_task_info = {}
cached_workers = []

cached_worker_info = {}

# Replace this with a deque.
unscheduled_tasks = []

available_workers = []

def add_remote_function(key):
  function_id = key.split(":", 1)[1]
  function_export_counter, num_return_vals = redis_client.hmget(key, ["function_export_counter", "num_return_vals"])
  function_export_counter = int(function_export_counter)
  num_return_vals = int(num_return_vals)
  cached_function_info[function_id] = {"export_counter": function_export_counter,
                                       "num_return_vals": num_return_vals}

def update_cached_workers():
  new_worker_ids = redis_client.lrange("Workers", len(cached_workers), -1)
  for worker_id in new_worker_ids:
    cached_workers.append(worker_id)
    available_workers.append(worker_id)
    worker_info_key = "WorkerInfo:{}".format(worker_id)
    export_counter = redis_client.hget(worker_info_key, "export_counter")
    export_counter = int(export_counter) if export_counter is not None else 0
    cached_worker_info[worker_id] = {"export_counter": export_counter}

def update_function_table(function_table_key):
  function_id = function_table_key.split(":", 1)[1]
  cached_function_table[function_id] = redis_client.lrange(function_table_key, 0, -1)

def update_object_table(object_key):
  # Update the cached object table.
  obj_id = object_key.split(":", 1)[1]
  cached_object_table[obj_id] = redis_client.lrange(object_key, 0, -1)

def update_export_counter(worker_info_key):
  worker_id = worker_info_key.split(":", 1)[1]
  cached_worker_info[worker_id]["export_counter"] = int(redis_client.hget(worker_info_key, "export_counter"))

num_tasks_added = 0
def add_new_tasks():
  global num_tasks_added
  new_task_ids = redis_client.lrange("GlobalTaskQueue", num_tasks_added, -1)
  for task_id in new_task_ids:
    unscheduled_tasks.append(task_id)
    task_key = "graph:{}".format(task_id)
    task_info = redis_client.hgetall(task_key)
    function_id = task_info["function_id"]
    dependencies = extract_dependencies(task_info)
    cached_task_info[task_id] = {"function_id": function_id,
                                 "dependencies": dependencies}
    num_tasks_added += 1









def extract_dependencies(task_info):
  dependencies = []
  i = 0
  while True:
    if "arg:{}:id".format(i) in task_info:
      dependencies.append(task_info["arg:{}:id".format(i)])
    elif "arg:{}:val".format(i) not in task_info:
      break
    i += 1
  return dependencies

def can_schedule(worker_id, task_id):
  task_info = cached_task_info[task_id]
  function_id = task_info["function_id"]
  if not cached_function_table.has_key(function_id):
    return False
  if cached_worker_info[worker_id]["export_counter"] < cached_function_info[function_id]["export_counter"]:
    return False
  if worker_id not in cached_function_table[function_id]:
    return False
  for obj_id in task_info["dependencies"]:
    if not cached_object_table.has_key(obj_id):
      return False
  return True

def schedule():
  scheduled_tasks = []
  for task_id in unscheduled_tasks:
    for worker_id in available_workers:
      if can_schedule(worker_id, task_id):
        redis_client.rpush("TaskQueue:Worker{}".format(worker_id), task_id)
        scheduled_tasks.append(task_id)
        available_workers.remove(worker_id)
        break
  # Remove the scheduled tasks.
  for task_id in scheduled_tasks:
    unscheduled_tasks.remove(task_id)

if __name__ == "__main__":
  args = parser.parse_args()

  redis_host, redis_port = args.redis_address.split(":")
  redis_port = int(redis_port)

  redis_client = redis.StrictRedis(host=redis_host, port=redis_port)
  redis_client.config_set("notify-keyspace-events", "AKE")
  pubsub_client = redis_client.pubsub()

  # Messages published after the call to pubsub_client.psubscribe and before the
  # call to pubsub.listen should be received in the pubsub_client.listen loop.
  pubsub_client.psubscribe("*")

  # Get anything that may have been pushed to Redis before we called psubscribe.
  # Some of the things that we get here may be processed a second time in the
  # event loop, so we have to handle that.

  # First update cached worker info.
  update_cached_workers()

  # Update the function table.
  for function_table_key in redis_client.scan_iter("FunctionTable:"):
    update_function_table(function_table_key)

  # Update the remote function info.
  for remote_function_key in redis_client.scan_iter("RemoteFunction:"):
    add_remote_function(key)

  # Update the object table.
  for object_key in redis_client.scan_iter("Object:"):
    update_object_table(object_key)

  # Update the task queue.
  add_new_tasks()

  # Schedule anything that can be scheduled already.
  schedule()

  # Receive messages and process them.
  for msg in pubsub_client.listen():
    if msg["channel"].startswith("__keyspace@0__:Object:"):
      object_key = msg["channel"].split(":", 1)[1]
      update_object_table(object_key)
    elif msg["channel"] == "__keyspace@0__:GlobalTaskQueue" and msg["data"] == "rpush":
      add_new_tasks()
    elif msg["channel"] == "__keyspace@0__:Workers":
      update_cached_workers()
    elif msg["channel"].startswith("__keyspace@0__:RemoteFunction:"):
      key = msg["channel"].split(":", 1)[1]
      add_remote_function(key)
    elif msg["channel"].startswith("__keyspace@0__:FunctionTable"):
      function_table_key = msg["channel"].split(":", 1)[1]
      update_function_table(function_table_key)
    elif msg["channel"].startswith("__keyspace@0__:WorkerInfo") and msg["data"] == "hincrby":
      worker_info_key = msg["channel"].split(":", 1)[1]
      update_export_counter(worker_info_key)
    elif msg["channel"] == "ReadyForNewTask":
      worker_id = msg["data"]
      available_workers.append(worker_id)
    else:
      # No need to do scheduling in this case.
      continue

    # Schedule things that can be scheduled.
    schedule()
