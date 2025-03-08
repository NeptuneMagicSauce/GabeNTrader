#include "init.hpp"

#include <iostream>

void Init::start() {
  t = std::thread{[this]() { work(); }};
}
Init::~Init() {
  if (t) {
    t->join();
  }
}

void Init::work() {
  using namespace std::chrono_literals;
  for (int i = 0; i < 20; ++i) {
    std::cout << i << std::endl;
    std::this_thread::sleep_for(50ms);
  }
  emit showLogin();
}
