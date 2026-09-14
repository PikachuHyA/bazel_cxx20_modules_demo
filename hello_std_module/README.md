# Bazel with C++20 Modules: Using Standard Library Modules

This document shows how to use C++23 standard library modules (`import std;`) with Bazel and Clang.

## Environment

- OS: Ubuntu 26.04 (resolute)
- Compiler: Clang 20+ (for C++23 `import std;` support)
- Bazel: requires a version including commit [60b1e19...](https://github.com/bazelbuild/bazel/commit/60b1e19baa4df5148bdc0a5ec8edb4cb6671fcc1) or later

Verify system info:
```bash
$ cat /etc/os-release
PRETTY_NAME="Ubuntu 26.04 LTS"
VERSION_CODENAME=resolute
```

Install dependencies:
```bash
sudo apt-get update
sudo apt-get install -y curl git clang libc++-dev libc++abi-dev lld
```
## MODULE.bazel

Use the std module support branch of `rules_cc`:
```python
module(name = "demo")

bazel_dep(name = "rules_cc", version = "0.2.22")
git_override(
    module_name = "rules_cc",
    remote = "https://github.com/PikachuHyA/rules_cc.git",
    branch = "support_std_module",
)
```

Enable the feature that matches the standard-library module imported by a target:

```text
# For targets that use import std;
build --features=std_module

# For targets that use import std.compat;
build --features=std_module_compat
```

`std_module` discovers and injects the compiler-provided `std` module. `std_module_compat` discovers and injects `std.compat`, including its dependency on `std`. Do not create, configure, or add either standard-module target to `deps` manually.


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

### 6. `std.compat`

Shows the compatibility module without an explicit dependency. `std-compat/main.cc` imports `std.compat` and uses global C-library names such as `printf` and `strlen`; its BUILD target enables `std_module_compat`.

### 7. Module Library

Shows mixing modules with traditional header files.

**Files:**
- `module-library/a.cppm`: A module
- `module-library/b.cc`, `module-library/b.h`: Traditional header/source
- `module-library/main.cc`: Uses both module and headers, plus `import std;`

## Build and Run

Build all examples:
```bash
$ BAZEL_LINKLIBS=-lc++:-lm BAZEL_CXXOPTS=-std=c++23:-stdlib=libc++ \
  bazel build //... --cxxopt=-std=c++23 --features=cpp_modules
```

Or use the provided build script:
```bash
$ ./build.sh
```

## Key Points

- Use `--repo_env=CC=clang` to select Clang for C++23 standard library modules.
- Add `--cxxopt=-std=c++23` to enable C++23.
- Set `BAZEL_LINKLIBS=-lc++:-lm` and `BAZEL_CXXOPTS=-std=c++23:-stdlib=libc++` to select libc++; omit them to use libstdc++.
- Add `--experimental_cpp_modules` to enable C++20 Modules support in Bazel.
- Enable `std_module` for targets that import `std`; it selects and injects the `std` module.
- Enable `std_module_compat` for targets that import `std.compat`; it selects and injects `std.compat`, which includes `std`.
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
