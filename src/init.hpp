#pragma once

#include <QObject>
#include <optional>
#include <thread>

class Init : public QObject {
  Q_OBJECT
 public:
  Init() = default;
  // can't be copied because member thread is exclusive
  Init(const Init&) = delete;
  Init& operator=(const Init&) = delete;
  void start();
  ~Init();

 signals:
  void showLogin(void);

 private:
  std::optional<std::thread> t;
  void work();
};
