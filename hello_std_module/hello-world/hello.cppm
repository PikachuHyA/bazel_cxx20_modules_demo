// hello.cppm

export module hello;

import std;

export inline void say_hello(std::string_view const &name)
{
  std::cout << "Hello " << name << "!\n";
}
