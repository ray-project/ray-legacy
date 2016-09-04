load("@protobuf//:protobuf.bzl", "cc_proto_library")

cc_library(
    name = "ray_headers",
    srcs = [
        "include/ray/logging.h",
        "include/ray/ray.h",
    ],
    includes = ["include"],
)

cc_proto_library(
    name = "types_proto",
    srcs = ["protos/types.proto"],
    default_runtime = "@protobuf//:protobuf",
    protoc = "@protobuf//:protoc",
    use_grpc_plugin = True,
)

cc_proto_library(
    name = "graph_proto",
    srcs = ["protos/graph.proto"],
    default_runtime = "@protobuf//:protobuf",
    protoc = "@protobuf//:protoc",
    use_grpc_plugin = True,
    deps = [":types_proto"],
)

cc_proto_library(
    name = "ray_proto",
    srcs = ["protos/ray.proto"],
    default_runtime = "@protobuf//:protobuf",
    protoc = "@protobuf//:protoc",
    use_grpc_plugin = True,
    deps = [
        ":graph_proto",
        ":types_proto",
    ],
)

cc_library(
    name = "ipc",
    srcs = ["src/ipc.cc"],
    hdrs = ["src/ipc.h"],
    deps = [
        ":ray_headers",
        ":utils",
        "@grpc//:grpc++_unsecure",
    ],
    # Possibly not needed on macOS
    linkopts = ["-lrt"],
)

cc_library(
    name = "utils",
    srcs = ["src/utils.cc"],
    hdrs = ["src/utils.h"],
    deps = [
        ":ray_headers",
        "@grpc//:grpc++_unsecure",
    ],
)

cc_binary(
    name = "objstore",
    srcs = [
        "src/objstore.cc",
        "src/objstore.h",
    ],
    deps = [
        ":ipc",
        ":ray_headers",
        ":ray_proto",
        ":utils",
        "@grpc//:grpc++_unsecure",
    ],
)

cc_binary(
    name = "scheduler",
    srcs = [
        "src/computation_graph.cc",
        "src/computation_graph.h",
        "src/scheduler.cc",
        "src/scheduler.h",
    ],
    deps = [
        ":ray_headers",
        ":ray_proto",
        ":utils",
        "@grpc//:grpc++_unsecure",
    ],
)

cc_binary(
    name = "libraylib.so",
    srcs = [
        "src/raylib.cc",
        "src/worker.cc",
        "src/worker.h",
    ],
    linkshared = 1,
    linkstatic = 1,
    deps = [
        ":ipc",
        ":ray_proto",
        ":utils",
        "@python//:python_headers",
    ],
)
