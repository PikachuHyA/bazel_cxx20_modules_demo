export module a;

// import std;   // directly from 'b'
// import <iostream>;

import b;

export inline void run_a() {
  std::println("A");
  run_b();
}
