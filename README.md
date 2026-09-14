# Bazel C++20 Modules demos

[bazel-9.0.0rc2](https://github.com/bazelbuild/bazel/releases/tag/9.0.0rc2) includes support for C++20 Modules. Happy to try!

Examples of building C++ modules with Bazel.
Each example has its own Bazel module and configuration; run build commands from the example directory.

## Examples

- [Hello world](./hello_world/README.md): a basic C++20 module.
- [Hello fmt](./hello_fmt/README.md): use `fmt` as a C++ module.
- [Standard library modules](./hello_std_module/README.md): C++23 `import std;` with Clang.
- [Multiple module interfaces](./hello_multi_module_interfaces/README.md): reverse the imports between `foo` and `bar` and rebuild without clearing the cache.

