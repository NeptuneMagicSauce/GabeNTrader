module;
#include <iostream>
#include "gui.hpp"
export module main2;
import foo;

int main(int /* argc*/, char **/* argv*/)
{
  std::cout << "main2\n";
  Foo{}.foo();
  auto g = GUI{};
  return g.exec();
}
