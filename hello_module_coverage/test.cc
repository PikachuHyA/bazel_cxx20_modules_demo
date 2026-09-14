#ifdef USE_MODULE
import lib;
#else
#include "lib.h"
#endif

int main() { 
  return classify(1) == 1 ? 0 : 1; 
}

