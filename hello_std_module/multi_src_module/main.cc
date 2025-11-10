import speech;

import std;

std::string get_phrase() {
    return "Hello, world!";
}

int main() {
  std::println("{}", get_phrase());
  std::println("{}", get_phrase_en());
  std::println("{}", get_phrase_es());
  return 0;
}
