# Multiple C++20 module interfaces: incremental-build reproducer

This demo places `foo.cppm` and `bar.cppm` in the `module_interfaces` of a single `cc_library`, `//:foobar`. It exercises dependency invalidation when the import direction changes between builds.

The checked-in sources start with `foo` importing `bar`. After switching, `bar` imports `foo` and `foo` no longer imports `bar`. Neither source configuration contains an import cycle.

## Environment

- CI runner: Ubuntu 26.04.
- Bazelisk, using Bazel 9.2.0 selected by [`.bazeliskrc`](./.bazeliskrc).
- `rules_cc` 0.2.22, selected by [`MODULE.bazel`](./MODULE.bazel).
- Clang and a matching `clang-scan-deps` executable.
- Python 3; the switching script uses only the standard library.

[`.bazelrc`](./.bazelrc) enables experimental C++ modules and selects `clang` with C++20 on Linux. [`BUILD.bazel`](./BUILD.bazel) enables the `cpp_modules` feature on the library.

## Reproduce

From the repository root:

```bash
cd hello_multi_module_interfaces
bazelisk --version
bazelisk build //:all
python3 toggle_imports.py
bazelisk build //:all
```

failed
```
Computing main repo mapping: 
Loading: 
Loading: 0 packages loaded
Analyzing: target //:foobar (0 packages loaded, 0 targets configured)
Analyzing: target //:foobar (0 packages loaded, 0 targets configured)
INFO: Analyzed target //:foobar (0 packages loaded, 0 targets configured).
ERROR: /home/runner/work/bazel_cxx20_modules_demo/bazel_cxx20_modules_demo/hello_multi_module_interfaces/BUILD.bazel:4:11: in cc_library rule //:foobar: cycle in dependency graph:
    configured target: //:foobar
    action from: ActionLookupData9{actionLookupKey=ConfiguredTargetKey{label=//:foobar, config=BuildConfigurationKey[81d5099ff8315b6fae7bcd2095f6e6fed06dda744d2393b0867673f060a78c2e]}, actionIndex=9}
.-> action from: ActionLookupData7{actionLookupKey=ConfiguredTargetKey{label=//:foobar, config=BuildConfigurationKey[81d5099ff8315b6fae7bcd2095f6e6fed06dda744d2393b0867673f060a78c2e]}, actionIndex=7}
|   action from: ActionLookupData5{actionLookupKey=ConfiguredTargetKey{label=//:foobar, config=BuildConfigurationKey[81d5099ff8315b6fae7bcd2095f6e6fed06dda744d2393b0867673f060a78c2e]}, actionIndex=5}
`-- action from: ActionLookupData7{actionLookupKey=ConfiguredTargetKey{label=//:foobar, config=BuildConfigurationKey[81d5099ff8315b6fae7bcd2095f6e6fed06dda744d2393b0867673f060a78c2e]}, actionIndex=7}
Target //:foobar failed to build
Use --verbose_failures to see the command lines of failed build steps.
INFO: Elapsed time: 0.593s, Critical Path: 0.07s
INFO: 6 processes: 1 internal, 5 processwrapper-sandbox.
ERROR: Build did NOT complete successfully
```

## CI

The [Ubuntu 26.04 workflow](../.github/workflows/ubuntu-multi-module-interfaces.yml) runs the four reproduction commands above as separate steps in this directory. It runs on pushes to `main` or `ci`, on pull requests, and via manual dispatch. Both builds use the same job environment without clearing Bazel's cache; either build failing fails the job.

## Related Bazel changes

- [#29924](https://github.com/bazelbuild/bazel/pull/29924): split mandatory/discovered action-cache checking for C++20 module compilation.
- [#29925](https://github.com/bazelbuild/bazel/pull/29925): alternative approach to multiple module interfaces and cache invalidation.
