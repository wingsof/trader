#ifndef TEST_WIDGET_H_
#define TEST_WIDGET_H_

#include <QWidget>


class TestWidget : public QWidget {
Q_OBJECT
public:
    TestWidget(QWidget *p=0);

protected:
    void paintEvent(QPaintEvent *p);


private:
    QPixmap *pixmap;
};


#endif
