#include <iostream>
#include <QTimer>

#include "gui.hpp"

// #include "bar.hpp"
// import foo;

int main(int /* argc*/, char **/* argv*/)
{
  // Foo{}.foo();
  auto g = GUI{};


  // QTimer::singleShot((int)2000, [] () {
  //   std::cout << "main() qtimer fired" << std::endl;
  // } );


  return g.exec();
}
