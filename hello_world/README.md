# Bazel with C++20 Modules: Hello World

This document shows how to build a simple C++20 Modules project using open-source Bazel and Clang.

Environment
- OS: Ubuntu 24.04.1 LTS
- Compiler: Clang 18.1.3
- Bazel: requires a version including commit [60b1e19...](https://github.com/bazelbuild/bazel/commit/60b1e19baa4df5148bdc0a5ec8edb4cb6671fcc1) or later

Verify system info:
```bash
$ cat /etc/lsb-release
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=24.04
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="Ubuntu 24.04.1 LTS"
```

Install dependencies:
```bash
sudo apt update
sudo apt install clang clang-tools git wget
```

Verify Clang:
```bash
$ ./clang -v
Ubuntu clang version 18.1.3 (1ubuntu1)
Target: x86_64-pc-linux-gnu
Thread model: posix
InstalledDir: /usr/bin
Found candidate GCC installation: /usr/bin/../lib/gcc/x86_64-linux-gnu/13
Selected GCC installation: /usr/bin/../lib/gcc/x86_64-linux-gnu/13
Candidate multilib: .;@m64
Selected multilib: .;@m64
```

Get Bazel
This feature is not yet in an official release. For temporary testing you can use a provided test build:
```bash
wget https://github.com/PikachuHyA/bazel/releases/download/cxx20-modules-support-v20251104/bazel
chmod +x bazel
```

Verify Bazel:
```bash
$ ./bazel --version
```

Tip: switch to the official Bazel release once it contains Modules support.

## Hello World with C++20 Modules
This example is adapted from [Kitware’s CMake blog](https://www.kitware.com/import-cmake-the-experiment-is-over/) and contains three files:
- foo.cppm: module interface defining module named foo
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
Because a specific `rules_cc` version is required, override it manually:
```python
module(name = "demo")

bazel_dep(name = "rules_cc")
git_override(
    module_name = "rules_cc",
    remote = "https://github.com/bazelbuild/rules_cc.git",
    commit = "a8f6a9241380a726a9131dc4d2ecc3543d7d6fb8",
)
```

Note: remove this override once `rules_cc` is updated upstream.

Build and run
Build with explicit Clang and experimental modules enabled:
```bash
$ ./bazel build :demo --repo_env=CC=clang --experimental_cpp_modules
INFO: Analyzed target //:demo (83 packages loaded, 456 targets configured).
INFO: Found 1 target...
Target //:demo up-to-date:
  bazel-bin/demo
INFO: Elapsed time: 2.031s, Critical Path: 1.23s
INFO: Build completed successfully, 17 total actions
```

Run:
```bash
$ ./bazel run :demo --repo_env=CC=clang --experimental_cpp_modules
INFO: Running command line: bazel-bin/demo
hello world
```

Or run the binary directly:
```bash
$ ./bazel-bin/demo
hello world
```

Key points
- Use `--repo_env=CC=clang` to select Clang.
- Clang requires `clang-scan-deps`; install via `clang-tools`.
- Add `--experimental_cpp_modules` to enable C++20 Modules support.
- Bazel controls Modules on a target basis (disabled by default); add `cpp_modules` to features to enable it.
- Include `-std=c++20` in compiler options (copts).

