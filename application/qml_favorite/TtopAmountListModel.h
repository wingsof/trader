#ifndef TTOP_AMOUNT_LIST_MODEL_H_
#define TTOP_AMOUNT_LIST_MODEL_H_

#include "AbstractListModel.h"

class TtopAmountListModel : public AbstractListModel {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(bool accumulatedPeriod READ accumulatedPeriod WRITE setAccumulatedPeriod NOTIFY accumulatedPeriodChanged)
    Q_PROPERTY(bool catchPlus READ catchPlus WRITE setCatchPlus NOTIFY catchPlusChanged)

public:
    TtopAmountListModel(QObject *parent=nullptr);
    QStringList getServerList() override;
    Q_INVOKABLE void menuClicked(int index) override;
    Q_INVOKABLE void checkStateChanged(int index, bool state);
    QString sectionName() { return "ttopamount"; }

    bool catchPlus() { return mCatchPlus; }
    bool accumulatedPeriod() { return mAccumulatedPeriod; }

    void setCatchPlus(bool c);
    void setAccumulatedPeriod(bool a);

private:
    bool mAccumulatedPeriod;
    bool mCatchPlus;

signals:
    void accumulatedPeriodChanged();
    void catchPlusChanged();
};


#endif
