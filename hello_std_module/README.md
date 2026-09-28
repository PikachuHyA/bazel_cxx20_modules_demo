# Bazel with C++ Modules and the Standard Library

This repository exercises C++23 standard-library modules with Bazel, Clang, and
the `rules_cc` standard-module support branch.

## Environment

- Ubuntu 26.04
- Clang 20 or newer, libc++ and libc++abi development packages
- A Bazel version containing [60b1e19](https://github.com/bazelbuild/bazel/commit/60b1e19baa4df5148bdc0a5ec8edb4cb6671fcc1) or later

Install the dependencies:

```sh
sudo apt-get update
sudo apt-get install -y curl git clang libc++-dev libc++abi-dev lld
```

## rules_cc dependency

```starlark
module(name = "demo")

bazel_dep(name = "rules_cc", version = "0.2.22")
git_override(
    module_name = "rules_cc",
    remote = "https://github.com/PikachuHyA/rules_cc.git",
    branch = "support_std_module",
)
```

The repository enables `cpp_modules`, `std_module`, and standard-module
detection in `.bazelrc`. With `std_module` enabled, C++ rules obtain the
standard module from the selected standard-module companion toolchain. The
auto-configured companion supplies `@local_config_cc//:std`, which contains
both `std` and `std.compat`. No standard-module dependency needs to be
listed manually. To supply a different standard module, register another
companion toolchain for `@rules_cc//cc/toolchains:std_module_toolchain_type`,
as `custom-std` does. The `cc_std_module_library` target the toolchain points
at must carry the `no_implicit_std_module` tag so it does not pick up a
standard module from the toolchain that points back at it.

## Examples

- `basic`: direct `import std;`.
- `std-compat`: direct `import std.compat;`; it uses the same `std_module`
  feature as `import std;`.
- `hello-world`, `transitive`, `template-module`, and `multi_src_module`:
  module interfaces, transitive imports, templates, and implementation units.
- `module-library`: C++ modules together with traditional headers and sources.
- `custom-std`: registers a companion toolchain that supplies an independent
  `my_std` module. Its bootstrap `cc_std_module_library` carries the
  `no_implicit_std_module` tag, so it does not depend on
  `@local_config_cc//:std`; the example covers `cc_library`, `cc_binary`, and
  `cc_test`.
- `fallback`: ordinary C++ code that verifies the empty `:std` fallback target
  when automatic detection is disabled. It deliberately does not import `std`.

## Build

Build the automatically detected examples against libc++:

```sh
bazel build --config=libcxx //... -- -//custom-std/...
```

Build against libstdc++ when the compiler provides `libstdc++.modules.json`:

```sh
bazel build --config=libstdcxx //... -- -//custom-std/...
```

Verify the custom standard-module companion toolchain:

```sh
bazel build --config=no_std_detection --config=custom_std_module //custom-std:all
bazel test --config=no_std_detection --config=custom_std_module //custom-std:std_module_test
bazel run --config=no_std_detection --config=custom_std_module //custom-std:demo
```

Verify the no-manifest fallback target:

```sh
bazel build --config=no_std_detection //fallback:demo
```

`BAZEL_DETECT_STD_MODULE=1` controls auto-detection at `local_config_cc`
configuration time. It is set in `.bazelrc`; changing it requires a repository
reconfiguration, for example `bazel sync`.
