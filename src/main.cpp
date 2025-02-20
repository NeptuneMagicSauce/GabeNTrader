#include "gui.hpp"

int main(int /* argc*/, char **/* argv*/)
{
  auto g = GUI{};
  return g.exec();
}
