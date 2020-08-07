#include "bullcard.h"

#include "bulltable.h"
#include "bullmodel.h"

#include <QHeaderView>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPushButton>


BullCard::BullCard(StockModel & _model, QWidget *p)
: QWidget(p), model(_model) {
    QVBoxLayout * layout = new QVBoxLayout;

    QHBoxLayout * menuLayout = new QHBoxLayout;
    QPushButton * refreshButton = new QPushButton("REFRESH");
    QPushButton * nextButton = new QPushButton("NEXT");
    connect(refreshButton, SIGNAL(clicked()), SLOT(refresh()));
    connect(nextButton, SIGNAL(clicked()), SLOT(next()));
    menuLayout->addWidget(refreshButton);
    menuLayout->addWidget(nextButton);

    table = new BullTable;
    bullmodel = new BullModel(model);
    connect(table, SIGNAL(clicked(const QModelIndex &)), bullmodel, SLOT(codeSelected(const QModelIndex &)));
    table->setModel(bullmodel);

    layout->addLayout(menuLayout);
    layout->addWidget(table);
    currentUpdateColumn = 0;
    setLayout(layout);
}

BullCard::~BullCard() {}


void BullCard::refresh() {
    bullmodel->refresh();
}


void BullCard::next() {
    bullmodel->next(); 
}
