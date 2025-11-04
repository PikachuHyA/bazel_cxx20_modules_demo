# Bazel with C++20 Modules: Hello fmt

This document shows how to build a C++20 Modules project using the `fmt` library with open-source Bazel and Clang.

Environment

Same as in [Hello World](../hello_world/README.md).

## Hello fmt with C++20 Modules

This example demonstrates how to use the `fmt` library as a C++20 module. It contains:
- main.cc: imports and uses the fmt module
- BUILD.bazel: Bazel build configuration
- MODULE.bazel: Bazel module configuration with fmt dependency
- fix.patch: patch to enable fmt to work as a C++20 module

1) Main program main.cc
```cpp
import fmt;

int main() {
    fmt::print("Hello, fmt!\n");
    fmt::println("The answer is {}.", 42);
    return 0;
}
```

2) BUILD.bazel
```python
load("@rules_cc//cc:defs.bzl", "cc_binary")

cc_binary(
    name = "demo",
    srcs = ["main.cc"],
    deps = ["@fmt"],
)
```

3) MODULE.bazel
Because a specific `rules_cc` version is required, override it manually. Also configure fmt to work with C++20 modules:
```python
module(name = "demo")
bazel_dep(name = "fmt", version = "12.1.0")
bazel_dep(name = "rules_cc")
git_override(
    module_name = "rules_cc",
    remote = "https://github.com/bazelbuild/rules_cc.git",
    commit = "a8f6a9241380a726a9131dc4d2ecc3543d7d6fb8",
)
single_version_override(
    module_name = "fmt",
    version = "12.1.0",
    patches = [
        ":fix.patch",
    ],
)
```

Note: The `fix.patch` enables fmt to work as a C++20 module by adding `FMT_ATTACH_TO_GLOBAL_MODULE` and configuring module interfaces.

Build and run
Build with explicit Clang and experimental modules enabled:
```bash
$ ./bazel build :demo --repo_env=CC=clang --experimental_cpp_modules --features cpp_modules --copt -std=c++20
```

Or use the provided build script:
```bash
$ ./build.sh
```

Run:
```bash
$ ./bazel run :demo --repo_env=CC=clang --experimental_cpp_modules --features cpp_modules --copt -std=c++20
INFO: Running command line: bazel-bin/demo
Hello, fmt!
The answer is 42.
```

Or run the binary directly:
```bash
$ ./bazel-bin/demo
Hello, fmt!
The answer is 42.
```

Key points
- Use `--repo_env=CC=clang` to select Clang.
- Clang requires `clang-scan-deps`; install via `clang-tools`.
- Add `--experimental_cpp_modules` to enable C++20 Modules support.
- Add `--features cpp_modules` to enable Modules support on targets.
- Include `--copt -std=c++20` to enable C++20 standard.
- The fmt library requires a patch to work as a C++20 module (provided in `fix.patch`).

