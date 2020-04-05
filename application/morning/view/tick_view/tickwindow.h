#ifndef TICK_WINDOW_H_
#define TICK_WINDOW_H_

#include <QWidget>

class TickWindow : public QWidget {
Q_OBJECT
public:
    explicit TickWindow(QWidget *parent=0);
    ~TickWindow();

private slots:
    void codeChanged(QString);
};


#endif
