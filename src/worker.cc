#include <ether/api.h>

#include "worker.h"
#include "serialize.h"

Status WorkerServiceImpl::InvokeCall(ServerContext* context, const InvokeCallRequest* request, InvokeCallReply* reply) {
  call_ = request->call(); // Copy call
  ORCH_LOG(ORCH_INFO, "invoked task " << request->call().name());
  Call* callptr = &call_;
  send_queue_.send(&callptr);
  return Status::OK;
}

Worker::Worker(const std::string& worker_address, std::shared_ptr<Channel> scheduler_channel, std::shared_ptr<Channel> objstore_channel)
    : worker_address_(worker_address),
      scheduler_stub_(Scheduler::NewStub(scheduler_channel)),
      objstore_stub_(ObjStore::NewStub(objstore_channel)) {
  receive_queue_.connect(worker_address_, true);
}

RemoteCallReply Worker::remote_call(RemoteCallRequest* request) {
  RemoteCallReply reply;
  ClientContext context;
  Status status = scheduler_stub_->RemoteCall(&context, *request, &reply);
  return reply;
}

void Worker::register_worker(const std::string& worker_address, const std::string& objstore_address) {
  RegisterWorkerRequest request;
  request.set_worker_address(worker_address);
  request.set_objstore_address(objstore_address);
  RegisterWorkerReply reply;
  ClientContext context;
  Status status = scheduler_stub_->RegisterWorker(&context, request, &reply);
  workerid_ = reply.workerid();
  request_obj_queue_.connect(std::string("queue:") + objstore_address + std::string(":obj"), false);
  std::string queue_name = std::string("queue:") + objstore_address + std::string(":worker:") + std::to_string(workerid_) + std::string(":obj");
  receive_obj_queue_.connect(queue_name, true);
  return;
}

void Worker::request_object(ObjRef objref) {
  PullObjRequest request;
  request.set_workerid(workerid_);
  request.set_objref(objref);
  AckReply reply;
  ClientContext context;
  Status status = scheduler_stub_->PullObj(&context, request, &reply);
  return;
}

ObjRef Worker::get_objref() {
  // first get objref for the new object
  PushObjRequest push_request;
  PushObjReply push_reply;
  ClientContext push_context;
  Status push_status = scheduler_stub_->PushObj(&push_context, push_request, &push_reply);
  return push_reply.objref();
}

slice Worker::get_object(ObjRef objref) {
  ObjRequest request;
  request.workerid = workerid_;
  request.type = ObjRequestType::GET;
  request.objref = objref;
  request_obj_queue_.send(&request);
  ObjHandle result;
  receive_obj_queue_.receive(&result);
  slice slice;
  slice.data = segmentpool_.get_address(result);
  slice.len = result.size();
  return slice;
}

// TODO(pcm): More error handling
void Worker::put_object(ObjRef objref, const Obj* obj) {
  std::string data;
  obj->SerializeToString(&data); // TODO(pcm): get rid of this serialization
  ObjRequest request;
  request.workerid = workerid_;
  request.type = ObjRequestType::ALLOC;
  request.objref = objref;
  request.size = data.size();
  request_obj_queue_.send(&request);
  ObjHandle result;
  receive_obj_queue_.receive(&result);
  uint8_t* target = segmentpool_.get_address(result);
  std::memcpy(target, &data[0], data.size());
  request.type = ObjRequestType::DONE;
  request.metadata_offset = 0;
  request_obj_queue_.send(&request);
}

void Worker::put_arrow(ObjRef objref, PyObject* obj) {
  arrow::MemoryPool* pool = arrow::default_memory_pool();
  PyObjectWriter writer(obj, pool);
  size_t size;
  if (PyArray_Check(obj)) {
    size = arrow_size((PyArrayObject*) obj);
  } else {
    size = writer.assemble_payload_and_return_size();
  }
  ObjRequest request;
  request.workerid = workerid_;
  request.type = ObjRequestType::ALLOC;
  request.objref = objref;
  request.size = size;
  request_obj_queue_.send(&request);
  ObjHandle result;
  receive_obj_queue_.receive(&result);
  uint8_t* address = segmentpool_.get_address(result);
  auto source = std::make_shared<BufferMemorySource>(address, result.size());
  if (PyArray_Check(obj)) {
    store_arrow((PyArrayObject*) obj, result, &segmentpool_);
  } else {
    request.metadata_offset = writer.write_object_and_return_metadata_offset(source.get());
  }
  request.type = ObjRequestType::DONE;
  request_obj_queue_.send(&request);
}

PyObject* Worker::get_arrow(ObjRef objref) {
  ObjRequest request;
  request.workerid = workerid_;
  request.type = ObjRequestType::GET;
  request.objref = objref;
  request_obj_queue_.send(&request);
  ObjHandle result;
  receive_obj_queue_.receive(&result);
  uint8_t* address = segmentpool_.get_address(result);
  auto source = std::make_shared<BufferMemorySource>(address, result.size());
  // return read_arrow_object(source.get(), result.metadata_offset());
  return deserialize_array(result, &segmentpool_);
}

bool Worker::is_arrow(ObjRef objref) {
  ObjRequest request;
  request.workerid = workerid_;
  request.type = ObjRequestType::GET;
  request.objref = objref;
  request_obj_queue_.send(&request);
  ObjHandle result;
  receive_obj_queue_.receive(&result);
  return result.metadata_offset() != 0;
}

void Worker::register_function(const std::string& name, size_t num_return_vals) {
  ClientContext context;
  RegisterFunctionRequest request;
  request.set_fnname(name);
  request.set_num_return_vals(num_return_vals);
  request.set_workerid(workerid_);
  AckReply reply;
  scheduler_stub_->RegisterFunction(&context, request, &reply);
}

Call* Worker::receive_next_task() {
  Call* call;
  receive_queue_.receive(&call);
  return call;
}

void Worker::notify_task_completed() {
  ClientContext context;
  WorkerReadyRequest request;
  request.set_workerid(workerid_);
  AckReply reply;
  scheduler_stub_->WorkerReady(&context, request, &reply);
}

// Communication between the WorkerServer and the Worker happens via a message
// queue. This is because the Python interpreter needs to be single threaded
// (in our case running in the main thread), whereas the WorkerService will
// run in a separate thread and potentially utilize multiple threads.
void Worker::start_worker_service() {
  const char* server_address = worker_address_.c_str();
  worker_server_thread_ = std::thread([server_address]() {
    WorkerServiceImpl service(server_address);
    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    std::unique_ptr<Server> server(builder.BuildAndStart());
    ORCH_LOG(ORCH_INFO, "worker server listening on " << server_address);
    server->Wait();
  });
}
