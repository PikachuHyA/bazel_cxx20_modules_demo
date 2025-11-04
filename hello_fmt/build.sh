bazel build :all \
    --repo_env=CC=clang \
    --experimental_cpp_modules \
    --features cpp_modules \
    --copt -std=c++20