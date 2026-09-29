[English](README.md) | 简体中文

# 使用 Bazel 构建 C++20 Modules：Hello World

本文档演示如何用开源 Bazel 构建一个简单的 C++20 Modules 项目，编译器可选用 Clang 或 GCC。

环境
- 操作系统：Ubuntu 26.04
- 编译器：Clang 18+、GCC 15+；同时也支持 MSVC。
- Bazel：9.0.0 或更高版本

安装 Clang（`clang-tools` 提供 `clang-scan-deps`）：
```bash
sudo apt update
sudo apt install clang clang-tools git wget
```

验证 Clang：
```bash
$ clang --version
Ubuntu clang version 21.1.8 (6ubuntu1)
Target: x86_64-pc-linux-gnu
Thread model: posix
InstalledDir: /usr/lib/llvm-21/bin
```

Bazel 会在解析到的 `clang` 旁边查找无版本号的 `clang-scan-deps`。如果该文件不存在，请创建指向与你的 clang 版本匹配的扫描器的符号链接：
```bash
$ sudo ln -sfn /usr/lib/llvm-$(clang -dumpversion | cut -d. -f1)/bin/clang-scan-deps /usr/bin/clang-scan-deps

$ clang-scan-deps --version
Ubuntu LLVM version 21.1.8
  Optimized build.
```

安装 GCC 16（支持 C++20 Modules）：
```bash
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo apt update
sudo apt install -y gcc-16 g++-16
```

验证 GCC：
```bash
$ gcc-16 --version
gcc-16 (Ubuntu 16-20260322-1ubuntu1) 16.0.1 20260322 (experimental) [trunk r16-8246-g569ace1fa50]
```

获取 Bazel
需要包含提交 [60b1e19...](https://github.com/bazelbuild/bazel/commit/60b1e19baa4df5148bdc0a5ec8edb4cb6671fcc1)（或更晚）的 Bazel 版本，也就是说 Bazel 9.0.0 及以上均可。这里使用最新的 [bazel-9.2.0](https://github.com/bazelbuild/bazel/releases/tag/9.2.0)。
```bash
wget -O bazel https://github.com/bazelbuild/bazel/releases/download/9.2.0/bazel-9.2.0-linux-x86_64
chmod +x bazel
```

验证 Bazel：
```bash
$ ./bazel --version
bazel 9.2.0
```

也可以安装 [bazelisk](https://github.com/bazelbuild/bazelisk)：它会使用 `.bazelversion` 中固定的版本，与 CI 中的 `bazelbuild/setup-bazelisk` 行为一致。

## C++20 Modules 版 Hello World
本示例改编自 [Kitware 的 CMake 博客](https://www.kitware.com/import-cmake-the-experiment-is-over/)，包含三个文件：
- foo.cppm：定义模块 `foo` 的模块接口
- main.cc：导入并使用该模块
- BUILD.bazel：Bazel 构建配置

1) 模块接口 foo.cppm
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

2) 主程序 main.cc
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
`rules_cc` 0.2.25 起支持 GCC：
```python
module(name = "demo")

bazel_dep(name = "rules_cc", version = "0.2.25")
```

构建并运行
使用 Clang：
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

使用 GCC 16：
```bash
$ ./bazel build //... --repo_env=CC=gcc-16 --experimental_cpp_modules \
    --cxxopt -fmodules --cxxopt -Mno-modules

$ ./bazel run //:demo --repo_env=CC=gcc-16 --experimental_cpp_modules \
    --cxxopt -fmodules --cxxopt -Mno-modules
INFO: Running command line: bazel-bin/demo
hello world
```

也可以直接运行二进制文件：
```bash
$ ./bazel-bin/demo
hello world
```

CI 会用两种编译器构建并运行本示例，详见 [.github/workflows/hello-world.yml](../.github/workflows/hello-world.yml)。

要点
- 通过 `--repo_env=CC=clang` 或 `--repo_env=CC=gcc-16` 选择编译器。
- Clang 需要 `clang-scan-deps`（随 `clang-tools` 安装）；Bazel 会在解析到的 `clang` 旁边查找无版本号的扫描器。
- GCC 15+ 需要 `--cxxopt -fmodules`；`--cxxopt -Mno-modules` 能让 `-M` 依赖输出不包含模块产物，保证 Bazel 的依赖扫描正常解析。
- 添加 `--experimental_cpp_modules` 启用 C++20 Modules 支持。
- Bazel 以 target 为粒度管理 Modules（默认关闭）；把 `cpp_modules` 加入 `features` 即可启用。
- 在编译选项（`copts`）中包含 `-std=c++20`。
- 使用 MSVC 时，添加 `--copt /std:c++20` 以启用 C++20 Modules，并添加 `--action_env=VSLANG=1033` 强制输出英文编译器信息，避免 CJK 乱码。
