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
detection in `.bazelrc`. `std_module` injects `@local_config_cc//:std` into
`cc_library` and `cc_binary`; that target supplies both `std` and `std.compat`.
No standard-module dependency needs to be listed manually.

## Examples

- `basic`: direct `import std;`.
- `std-compat`: direct `import std.compat;`; it uses the same `std_module`
  feature as `import std;`.
- `hello-world`, `transitive`, `template-module`, and `multi_src_module`:
  module interfaces, transitive imports, templates, and implementation units.
- `module-library`: C++ modules together with traditional headers and sources.
- `custom-std`: overrides `@rules_cc//cc:std_module` with an independent
  `my_std` module. It does not depend on `@local_config_cc`; the
  `no_implicit_std_module` tag prevents a dependency cycle.
- `fallback`: ordinary C++ code that verifies the empty `:std` fallback target
  when automatic detection is disabled. It deliberately does not import `std`.

## Build

Build every example against libc++:

```sh
bazel build --config=libcxx //...
```

Build against libstdc++ when the compiler provides `libstdc++.modules.json`:

```sh
bazel build --config=libstdcxx //...
```

Verify a custom standard-module target:

```sh
bazel build --config=libcxx --config=custom_std_module //custom-std:demo
```

Verify the no-manifest fallback target:

```sh
bazel build --config=no_std_detection //fallback:demo
```

`BAZEL_DETECT_STD_MODULE=1` controls auto-detection at `local_config_cc`
configuration time. It is set in `.bazelrc`; changing it requires a repository
reconfiguration, for example `bazel sync`.
