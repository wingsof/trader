#ifndef TNINE_THIRTY_LIST_MODEL_H_
#define TNINE_THIRTY_LIST_MODEL_H_

#include "AbstractListModel.h"

class TnineThirtyListModel : public AbstractListModel {
    Q_OBJECT
    QML_ELEMENT

public:
    TnineThirtyListModel(QObject *parent=nullptr);
    QStringList getServerList() override;
    Q_INVOKABLE void menuClicked(int index) override;
    QString sectionName() { return "ninethirty"; }
};


#endif
