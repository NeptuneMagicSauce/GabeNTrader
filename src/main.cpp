#include "gui.hpp"

// #include "bar.hpp"
import foo;

int main3(int /* argc*/, char **/* argv*/)
{
  Foo{}.foo();
  auto g = GUI{};
  return g.exec();
}
