# Bazel with C++20 Modules: Using Standard Library Modules

This document shows how to use C++23 standard library modules (`import std;`) with Bazel and Clang.

## Environment

- OS: Ubuntu 24.04.1 LTS
- Compiler: Clang 19+ (for C++23 `import std;` support)
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
sudo apt install curl git clang-20 libc++-20-dev libc++abi-20-dev liblld-20-dev
```

Verify Clang:
```bash
$ clang-20 -v
Ubuntu clang version 20.1.2 (0ubuntu1~24.04.2)
Target: x86_64-pc-linux-gnu
Thread model: posix
InstalledDir: /usr/lib/llvm-20/bin
Found candidate GCC installation: /usr/lib/gcc/x86_64-linux-gnu/13
Selected GCC installation: /usr/lib/gcc/x86_64-linux-gnu/13
Candidate multilib: .;@m64
Selected multilib: .;@m64
```

## Get Bazel

This feature is not yet in an official release. [bazel-9.0.0rc2](https://github.com/bazelbuild/bazel/releases/tag/9.0.0rc2) includes support for it.
```bash
wget -O bazel https://github.com/bazelbuild/bazel/releases/download/9.0.0rc2/bazel-9.0.0rc2-linux-x86_64
chmod +x bazel
```

Verify Bazel:
```bash
$ ./bazel --version
```

Tip: switch to the official Bazel release once it contains Modules support.

## MODULE.bazel

Because a specific `rules_cc` version is required, override it manually:
```python
module(name = "demo")
bazel_dep(name = "rules_cc")

git_override(
    module_name = "rules_cc",
    remote = "https://github.com/PikachuHyA/rules_cc.git",
    branch = "support_std_module",
)
cc_configure = use_extension("@rules_cc//cc:extensions.bzl", "cc_configure_extension")
use_repo(cc_configure, "local_config_cc")
```

After that, you can use `@local_config_cc//:std_modules` as a dependency to enable standard library modules in your targets.

Note: remove this override once `rules_cc` is updated upstream.

## Examples

This directory contains several examples demonstrating different aspects of using standard library modules with Bazel.

### 1. Basic Example

The simplest example using `import std;` directly.

**Files:**
- `basic/main.cc`: Uses `import std;` and `std::println`

**BUILD.bazel:**
```python
load("@rules_cc//cc:defs.bzl", "cc_binary")

cc_binary(
    name = "demo",
    srcs = ["main.cc"],
    features = ["cpp_modules"],
    deps = ["@local_config_cc//:std_modules"],
)
```

### 2. Hello World Module

A module that uses `import std;` and is imported by the main program.

**Files:**
- `hello-world/hello.cppm`: Module interface that imports std
- `hello-world/main.cc`: Imports both hello module and std

### 3. Transitive Dependencies

Demonstrates how std module dependencies propagate through module chains.

**Files:**
- `transitive/b.cppm`: Module that imports and re-exports std
- `transitive/a.cppm`: Module that imports b (and transitively gets std)
- `transitive/main.cc`: Uses module a

### 4. Template Module

Shows how to use std module with template code.

**Files:**
- `template-module/algorithm.cppm`: Template module using std algorithms
- `template-module/main.cc`: Uses the algorithm module

### 5. Multi-Source Module

Demonstrates modules with separate interface and implementation files.

**Files:**
- `multi_src_module/spanish_english_dictionary.cppm`: Module interface
- `multi_src_module/spanish_english_dictionary_impl.cc`: Module implementation
- `multi_src_module/speech.cppm`: Another module interface
- `multi_src_module/speech_impl.cc`: Another module implementation
- `multi_src_module/main.cc`: Uses speech module

### 6. Module Library

Shows mixing modules with traditional header files.

**Files:**
- `module-library/a.cppm`: A module
- `module-library/b.cc`, `module-library/b.h`: Traditional header/source
- `module-library/main.cc`: Uses both module and headers, plus `import std;`

## Build and Run

Build all examples:
```bash
$ BAZEL_LINKOPTS=-stdlib=libc++ BAZEL_CXXOPTS=-stdlib=libc++ bazel build ... --cxxopt -std=c++23 -s --experimental_cpp_modules
```

Or use the provided build script:
```bash
$ ./build.sh
```

## Key Points

- Use `--repo_env=CC=clang-20` (or clang-19) to select a Clang version that supports C++23 standard library modules.
- Add `--cxxopt=-std=c++23` to enable C++23.
- Add `BAZEL_LINKOPTS=-stdlib=libc++` and `BAZEL_CXXOPTS=-stdlib=libc++` to use libc++ (required for std modules).
- Add `--experimental_cpp_modules` to enable C++20 Modules support in Bazel.
- Add `@local_config_cc//:std_modules` as a dependency to targets that use `import std;`.
- Add `cpp_modules` to the `features` list in BUILD targets.
- Use `module_interfaces` attribute for module interface files (`.cppm`).

## Known Issues

- If you encounter `fatal error: cannot open file '/proc/self/cwd/xxx.cppm': No such file or directory`, add the following to `copts` in your BUILD file:
  ```python
  copts = [
      "-Xclang",
      "-fmodules-embed-all-files",
  ],
  ```