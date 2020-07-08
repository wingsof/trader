#ifndef YTOP_AMOUNT_LIST_MODEL_H_
#define YTOP_AMOUNT_LIST_MODEL_H_

#include "AbstractListModel.h"

class YtopAmountListModel : public AbstractListModel {
    Q_OBJECT
    QML_ELEMENT

public:
    YtopAmountListModel(QObject *parent=nullptr);
    QStringList getServerList() override;
    Q_INVOKABLE void menuClicked(int index) override;
    QString secitonName() { return "ytopamount"; }
};


#endif
