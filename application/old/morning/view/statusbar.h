#ifndef STATUS_BAR_H_
#define STATUS_BAR_H_

#include <QToolBar>
#include <QAction>
#include <QLabel>
#include <QDialog>
#include <QCalendarWidget>
#include <QHBoxLayout>


class DatePick : public QDialog {
Q_OBJECT
public:
    DatePick(QWidget *p=0) : QDialog(p) {
        QHBoxLayout * layout = new QHBoxLayout;
        calendarWidget = new QCalendarWidget;
        layout->addWidget(calendarWidget);
        connect(calendarWidget, SIGNAL(activated(const QDate&)), SIGNAL(dateSelected(const QDate&)));
        setLayout(layout);
    }

private:
    QCalendarWidget * calendarWidget;

signals:
    void dateSelected(const QDate&);
};


class StatusBar : public QToolBar {
Q_OBJECT
public:
    explicit StatusBar(QWidget *p=0);
    ~StatusBar();

private:
    QAction *startAction;
    QAction *simulationAction;
    QLabel *dateLabel;
    QDate simulationDate;

private slots:
    void showCalendarWidget();
    void dateSelected(const QDate &);
    void prepareSimulation();

signals:
    void startSimulation(QDateTime);
};


#endif
