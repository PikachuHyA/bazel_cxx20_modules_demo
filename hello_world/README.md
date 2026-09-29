English | [简体中文](README.zh-CN.md)

# Bazel with C++20 Modules: Hello World

This document shows how to build a simple C++20 Modules project with open-source Bazel, using either Clang or GCC.

Environment
- OS: Ubuntu 26.04
- Compilers: Clang 18+ and GCC 15+; MSVC is also supported.
- Bazel: 9.0.0 or later

Install Clang (`clang-tools` provides `clang-scan-deps`):
```bash
sudo apt update
sudo apt install clang clang-tools git wget
```

Verify Clang:
```bash
$ clang --version
Ubuntu clang version 21.1.8 (6ubuntu1)
Target: x86_64-pc-linux-gnu
Thread model: posix
InstalledDir: /usr/lib/llvm-21/bin
```

Bazel looks for the unversioned `clang-scan-deps` next to the resolved `clang`. If it is missing, create the symlink to the scanner that matches your clang:
```bash
$ sudo ln -sfn /usr/lib/llvm-$(clang -dumpversion | cut -d. -f1)/bin/clang-scan-deps /usr/bin/clang-scan-deps

$ clang-scan-deps --version
Ubuntu LLVM version 21.1.8
  Optimized build.
```

Install GCC 16 (C++20 Modules support):
```bash
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo apt update
sudo apt install -y gcc-16 g++-16
```

Verify GCC:
```bash
$ gcc-16 --version
gcc-16 (Ubuntu 16-20260322-1ubuntu1) 16.0.1 20260322 (experimental) [trunk r16-8246-g569ace1fa50]
```

Get Bazel
A Bazel version containing commit [60b1e19...](https://github.com/bazelbuild/bazel/commit/60b1e19baa4df5148bdc0a5ec8edb4cb6671fcc1) or later is required, so Bazel 9.0.0 or later works. Here we use the latest release, [bazel-9.2.0](https://github.com/bazelbuild/bazel/releases/tag/9.2.0).
```bash
wget -O bazel https://github.com/bazelbuild/bazel/releases/download/9.2.0/bazel-9.2.0-linux-x86_64
chmod +x bazel
```

Verify Bazel:
```bash
$ ./bazel --version
bazel 9.2.0
```

Alternatively, install [bazelisk](https://github.com/bazelbuild/bazelisk): it picks the version pinned in `.bazelversion`, just like `bazelbuild/setup-bazelisk` in the CI.

## Hello World with C++20 Modules
This example is adapted from [Kitware’s CMake blog](https://www.kitware.com/import-cmake-the-experiment-is-over/) and contains three files:
- foo.cppm: module interface defining a module named foo
- main.cc: imports and uses the module
- BUILD.bazel: Bazel build configuration

1) Module interface foo.cppm
```cpp
// Global module fragment where #includes can happen
module;
#include <iostream>

// first thing after the Global module fragment must be a module command
export module foo;

export class foo {
public:
  foo();
  ~foo();
  void helloworld();
};

foo::foo() = default;
foo::~foo() = default;
void foo::helloworld() { std::cout << "hello world\n"; }
```

2) Main program main.cc
```cpp
import foo;

int main() {
    foo f;
    f.helloworld();
    return 0;
}
```

3) BUILD.bazel
```python
load("@rules_cc//cc:defs.bzl", "cc_binary")

cc_binary(
    name = "demo",
    srcs = ["main.cc"],                 # regular source files
    module_interfaces = ["foo.cppm"],   # module interface files (new attribute)
    copts = ["-std=c++20"],             # enable C++20
    features = ["cpp_modules"],         # required: enable Modules support
)
```

MODULE.bazel
`rules_cc` 0.2.25 supports GCC:
```python
module(name = "demo")

bazel_dep(name = "rules_cc", version = "0.2.25")
```

Build and run
With Clang:
```bash
$ ./bazel build //... --repo_env=CC=clang --experimental_cpp_modules
INFO: Analyzed target //:demo (93 packages loaded, 546 targets configured).
INFO: Found 1 target...
Target //:demo up-to-date:
  bazel-bin/demo

$ ./bazel run //:demo --repo_env=CC=clang --experimental_cpp_modules
INFO: Running command line: bazel-bin/demo
hello world
```

With GCC 16:
```bash
$ ./bazel build //... --repo_env=CC=gcc-16 --experimental_cpp_modules \
    --cxxopt -fmodules --cxxopt -Mno-modules

$ ./bazel run //:demo --repo_env=CC=gcc-16 --experimental_cpp_modules \
    --cxxopt -fmodules --cxxopt -Mno-modules
INFO: Running command line: bazel-bin/demo
hello world
```

Or run the binary directly:
```bash
$ ./bazel-bin/demo
hello world
```

The CI builds and runs this demo with both compilers; see [.github/workflows/hello-world.yml](../.github/workflows/hello-world.yml).

Key points
- Use `--repo_env=CC=clang` or `--repo_env=CC=gcc-16` to select the compiler.
- Clang requires `clang-scan-deps` (installed with `clang-tools`); Bazel looks for the unversioned scanner next to the resolved `clang`.
- GCC 15+ requires `--cxxopt -fmodules`; `--cxxopt -Mno-modules` keeps module artifacts out of the `-M` dependency output that Bazel's include scanning parses.
- Add `--experimental_cpp_modules` to enable C++20 Modules support.
- Bazel controls Modules on a per-target basis (disabled by default); add `cpp_modules` to `features` to enable them.
- Include `-std=c++20` in the compiler options (`copts`).
- For MSVC, add `--copt /std:c++20` to enable C++20 Modules, and `--action_env=VSLANG=1033` to force English compiler messages and avoid garbled CJK output.
