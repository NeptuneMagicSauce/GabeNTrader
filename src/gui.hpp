#pragma once

#include <QObject>

class GUI : public QObject {
  Q_OBJECT
 public:
  GUI();
  int exec();

 signals:
  void spinnerStopped(void);
 public slots:
  void stopSpinner(void);
  void showLogin(void);
};
