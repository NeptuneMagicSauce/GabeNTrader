#pragma once

#include <qtmetamacros.h>

#include <QObject>
#include <memory>

namespace std {
struct thread;
}

class Init : public QObject {
  Q_OBJECT
 public:
  Init();
  void start();
  ~Init();

 signals:
  void showLogin(void);

 private:
  std::shared_ptr<std::thread> t = nullptr;
  void work();
};
