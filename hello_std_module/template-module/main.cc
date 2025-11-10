import std;
// import <iostream>;
// import <vector>;

import algorithm;

int main() {
  std::vector<int> v1 = {1, -9, 7};
  std::println("{}",  compute_median(v1.begin(), v1.end()));
  std::vector<double> v2 = {10.0, 5.0, 7.2, -3.5};
  std::println("{}", compute_median(v2.begin(), v2.end()));
  return 0;
}
