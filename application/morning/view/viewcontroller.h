#ifndef VIEW_CONTROLLER_H_
#define VIEW_CONTROLLER_H_


#include <QObject>


class ViewController : public QObject {
Q_OBJECT
public:
    static ViewController & getInstance() {
        static ViewController controller;
        return controller;
    }

    void setCurrentCode(const QString &);

private:
    ViewController();
    ~ViewController();

    QString currentCode;

signals:
    void codeChanged(QString);
};

#endif
