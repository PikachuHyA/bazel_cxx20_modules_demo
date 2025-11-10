module spanish_english_dictionary;

// import <string>;
// import <string_view>;
import std;

std::string translate(std::string_view s) {
  if (s == "Hello") {
    return "Hola";
  }
  return "???";
}
