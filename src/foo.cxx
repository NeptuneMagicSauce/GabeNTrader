// Global module fragment where #includes can happen
module;
#include <iostream>

// first thing after the Global module fragment must be a module command
export module foo;

export class Foo {
 public:
  // Foo();
  // ~Foo();
  void foo();
};

// foo::foo() = default;
// foo::~foo() = default;
void Foo::foo() { std::cout << "foo\n"; }
