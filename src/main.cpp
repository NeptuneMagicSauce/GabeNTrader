#include "gui.hpp"
#include "init.hpp"

int main(int /* argc*/, char** /* argv*/) {
  // instantiate the GUI and the Initial thread
  auto gui = GUI{};
  auto init = Init{};

  // connect the signals
  QObject::connect(&init, &Init::showLogin, &gui, &GUI::showLogin);

  // start the Initial thread
  init.start();

  // start the GUI
  return gui.exec();
}
