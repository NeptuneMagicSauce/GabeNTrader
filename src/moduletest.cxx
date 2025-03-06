module;
#include <iostream>

export module moduletest;

export class ModuleTest {
 public:
  void foo();
};

void ModuleTest::foo() { std::cout << "foo\n"; }
