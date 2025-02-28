import foo;
#include <iostream>
#include "bar.hpp"
void bar() {
  std::cout << "bar\n";
  Foo{}.foo();
}
