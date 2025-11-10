set -ex
BAZEL_LINKOPTS=-stdlib=libc++ BAZEL_CXXOPTS=-stdlib=libc++ \
bazel build ... --cxxopt -std=c++23 -s --experimental_cpp_modules
