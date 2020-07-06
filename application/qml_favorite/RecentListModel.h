#ifndef RECENT_LIST_MODEL_H_
#define RECENT_LIST_MODEL_H_


#include <qqml.h>
#include <QDateTime>
#include <QAbstractListModel>


class RecentCode : public QObject{
Q_OBJECT
public:
    RecentCode(const QString &code, const QDateTime &dt);

    const QString & code() const { return m_code; }
    const QString & name() const { return m_name; }
    qreal yesterdayProfit() const;
    uint64_t yesterdayAmount() const;
    qreal todayProfit() const;
    uint64_t todayAmount() const;

private:
    QString m_code;
    QString m_name;
    QDateTime m_today;
};


class RecentListModel : public QAbstractListModel {
    Q_OBJECT
    QML_ELEMENT

public:
    RecentListModel(QObject *parent=nullptr);
    int rowCount(const QModelIndex &parent=QModelIndex()) const override;

    QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const override;
    QHash<int, QByteArray> roleNames() const override
    {
        return { {Qt::DisplayRole, "display"},
                 {Qt::UserRole,    "code"},
                 {Qt::UserRole + 1, "yprofit"},
                 {Qt::UserRole + 2, "tprofit"},
                 {Qt::UserRole + 3, "yamount"},
                 {Qt::UserRole + 4, "tamount"}};
    }
    Q_INVOKABLE void currentSelectionChanged(int index);


private:
    QDateTime today;
    QList<RecentCode *> recentList;

    void clearList();
    void refreshList();
    QString uint64ToString(uint64_t amount) const;

private slots:
    void stockCodeChanged(QString code, QDateTime untilTime, int countOfDays);
    void stockListTypeChanged(QString);
    void infoUpdated(QString);
};



#endif
