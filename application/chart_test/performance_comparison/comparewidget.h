#ifndef COMPARE_WIDGET_H_
#define COMPARE_WIDGET_H_


#include <QWidget>


class QwtMinuteWindow;
class MinuteWindow;

class CompareWidget : public QWidget {
Q_OBJECT
public:
    CompareWidget(QWidget *p=0);

private:
    MinuteWindow *minuteWindow;
    QwtMinuteWindow *qwtMinuteWindow;

private slots:
    void displayData1();
    void displayData2();
    void clearData1();
    void clearData2();
};


#endif
