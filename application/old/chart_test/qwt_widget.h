#ifndef QWT_WIDGET_H_
#define QWT_WIDGET_H_

#include <QWidget>
#include <QVector>
#include <qwt_samples.h>

class QwtTestWidget : public QWidget {
Q_OBJECT
public:
    QwtTestWidget(QWidget *p=0);
    QVector<QwtOHLCSample> addTestData();
};


#endif
