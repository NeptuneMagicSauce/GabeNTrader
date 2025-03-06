// #define NOQT
#ifndef NOQT

import foo;

#include <iostream>
#include <string>
#include <QApplication>
#include <QMainWindow>
#include <QToolBar>
#include <QWidget>
#include <QHBoxLayout>
#include <QStyle>
#include <QLineEdit>
#include <QPushButton>
#include <QShortcut>
#include <QKeySequence>
#include <QAction>
#include <QTimer>
#include <QLabel>

#endif
#include "gui.hpp"

#ifdef NOQT
GUI::GUI() { }
int GUI::exec() { return 0; }
#else

using namespace std;

struct SpinnerAscii {
  int index = 0;
  wchar_t value();

  // static vector<int> buildValues() { return {}; }
  // static const vector<int> values = buildValues();
};

struct Impl {
  struct ToolBar: public QToolBar {
    ToolBar();
    struct User: public QWidget {
      User();
      QTimer update;
      QLabel image;
      QLabel name;
      SpinnerAscii spinner;
    };
  };
  int argc;
  QApplication a;
  QMainWindow w;
  ToolBar t;
  Impl();

  QIcon standardIcon(QStyle::StandardPixmap name) const;
};

struct Central: public QWidget {
  Central();
};

namespace {
  std::unique_ptr<Impl> instance = nullptr;
}

GUI::GUI() { instance = std::make_unique<Impl>(); }
int GUI::exec() { return instance->a.exec(); }

void GUI::stopSpinner(void) {
  std::cout << __PRETTY_FUNCTION__ << std::endl;
  emit spinnerStopped();
}

Impl::Impl() :
  argc(0),
  a(argc, nullptr)
{
  std::cout << "GUI ctor" << std::endl;
  QTimer::singleShot(100, [] () { std::cout << "after ctor GUI qtimer" << std::endl; } );

  Foo{}.foo();

  w.addToolBar(&t);
  w.show();
  w.setWindowIcon(standardIcon(QStyle::StandardPixmap::SP_MessageBoxWarning));
  w.setCentralWidget(new Central());

  auto quitShortcut = new QShortcut(QKeySequence(Qt::Key_F12), &w);
  quitShortcut->setContext(Qt::ApplicationShortcut);
  QObject::connect(quitShortcut, &QShortcut::activated, &a, &QApplication::quit);
}

QIcon Impl::standardIcon(QStyle::StandardPixmap name) const {
  return a.style()->standardIcon(name);
}

Central::Central() {
  auto layout = new QVBoxLayout(this);
  layout->addWidget(new QLineEdit());
  layout->addWidget(new QWidget());
  layout->addWidget(new QPushButton());
}

Impl::ToolBar::ToolBar() {
  setMovable(false);
  setFloatable(false);
  setContextMenuPolicy(Qt::ContextMenuPolicy::PreventContextMenu);
  setFixedHeight(30);

  auto logs = new QAction();
  logs->setIcon(instance->standardIcon(QStyle::StandardPixmap::SP_MessageBoxInformation));
  logs->setText("Logs");
  logs->setCheckable(true);
  addAction(logs);

  auto spacer = new QWidget();
  spacer->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
  addWidget(spacer);

  addWidget(new User());
}

Impl::ToolBar::User::User() {

// "TODO here: constexpr, no conversion at runtime, clean up ..."
  auto foo = [this] {
    auto value = spinner.value();
    return QString::fromWCharArray(&value, 1);
  };

  QObject::connect(&update, &QTimer::timeout, this, [this, foo] { name.setText(foo()); });
  auto layout = new QHBoxLayout(this);
  layout->addWidget(&image);
  layout->addWidget(&name);
  update.start(50);
  auto margins = layout->contentsMargins();
  margins.setTop(0);
  margins.setBottom(0);
  layout->setContentsMargins(margins);
}

wchar_t SpinnerAscii::value() {
  // auto constexpr values = std::array<int, 15>{
  auto values = vector<uint16_t> {
                0x2801,
                0x2809,
                0x2819,
                0x281b,
                0x281f,
                0x283f,
                0x28bf,
                0x28ff,

                0x28fe,
                0x28f6,
                0x28e6,
                0x28e4,
                0x28e0,
                0x28c0,
                0x2840,
  };
  auto reversed = values;
  reverse(reversed.begin(), reversed.end());
  auto v = vector{values};
  for (int i=1; i<(int)reversed.size() - 1; ++i) {
    v.push_back(reversed[i]);
  }

  auto ret = v[index];
  index += 1;
  index %= v.size();
  return ret;
}
#endif
