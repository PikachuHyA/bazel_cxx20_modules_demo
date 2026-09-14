# C++20 modules coverage reproduction

This directory demonstrates a code-coverage gap for C++20 module interfaces built with Bazel.

With Bazel 9.2.0 and the default <code>rules_cc</code>, the test passes but the LLVM LCOV report does not list <code>lib.cppm</code>. The equivalent ordinary C++ library is included. With the corresponding Bazel and <code>rules_cc</code> changes, the module interface is included in the report.

## Contents

| File | Purpose |
| --- | --- |
| <code>lib.cc</code>, <code>lib.h</code> | Ordinary C++ library used as the control case. |
| <code>lib.cppm</code> | C++20 module interface that exports the same <code>classify</code> function. |
| <code>test.cc</code> | Uses the header normally, or imports the module when <code>USE_MODULE</code> is set. |
| <code>BUILD.bazel</code> | Defines <code>test_no_module</code> and <code>test_with_module</code>. |
| <code>MODULE.bazel</code> | Uses the default <code>rules_cc</code> release. |
| <code>MODULE.bazel.fixed</code> | Uses the <code>rules_cc</code> commit containing module-interface coverage support. |
| <code>.bazelrc</code> | Enables C++ modules and LLVM native coverage. |

## Reproduce the missing coverage

Run the module test with Bazel 9.2.0:

~~~bash
bazelisk coverage :test_with_module --nocache_test_results
cat bazel-out/_coverage/_coverage_report.dat
~~~

The test succeeds, but <code>SF:lib.cppm</code> is absent from <code>_coverage_report.dat</code>.

For comparison, run the ordinary C++ target:

~~~bash
bazelisk coverage :test_no_module --nocache_test_results
cat bazel-out/_coverage/_coverage_report.dat
~~~

That report contains <code>SF:lib.cc</code>.

## Reproduce with the fix

The fixed configuration needs both:

1. The Bazel build that supports collecting module-interface files for coverage.
2. The <code>rules_cc</code> commit referenced by <code>MODULE.bazel.fixed</code>.

Use the fixed module configuration, then invoke the patched Bazel binary:

~~~bash
cp MODULE.bazel.fixed MODULE.bazel
/path/to/patched/bazel coverage :test_with_module --nocache_test_results
cat bazel-out/_coverage/_coverage_report.dat
~~~

The report contains <code>SF:lib.cppm</code>.

## Continuous integration

The repository workflow at <code>../.github/workflows/module-coverage.yml</code> runs two independent jobs:

1. <code>bazel_9_2_0</code> uses Bazel 9.2.0 and the default <code>rules_cc</code>, and verifies that <code>lib.cppm</code> is absent from the report.
2. <code>patched_bazel</code> downloads the patched Bazel binary, verifies its SHA-256, selects <code>MODULE.bazel.fixed</code>, and verifies that <code>lib.cppm</code> is present in the report.

Both jobs print <code>_coverage_report.dat</code> and <code>_baseline_report.dat</code> so the LCOV differences are visible in the Actions log.
