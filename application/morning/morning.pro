######################################################################
# Automatically generated by qmake (3.1) Wed Mar 25 10:37:47 2020
######################################################################

TEMPLATE = app
CONFIG += link_pkgconfig
TARGET = morning
INCLUDEPATH += .
QT += widgets
QT += charts
#LIBS += -L/usr/local/lib
PKGCONFIG += protobuf
PKGCONFIG += grpc++

OBJECTS_DIR=generated_files
MOC_DIR=generated_files

# You can make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# Please consult the documentation of the deprecated API in order to know
# how to port your code away from it.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

# Input
SOURCES += main.cpp \
           stock_server/stock_provider.grpc.pb.cc \
           stock_server/stock_provider.pb.cc \
           stock_server/data_provider.cpp \
           stock_server/stock_object.cpp \
           stock_server/tick_thread.cpp \
           stock_server/bidask_thread.cpp \
           stock_server/subject_thread.cpp \
           stock_server/time_thread.cpp \
           stock_server/plugin/chooser/chooserplugin.cpp \
           stock_server/plugin/chooser/topamount.cpp \
           stock_server/time_info.cpp \
           stock_model/stockmodel.cpp \
           view/mainwindow.cpp \
           view/statusbar.cpp \
           view/tick_view/tickwindow.cpp \
           view/bull_card/bullcard.cpp \
           view/bull_card/bulltable.cpp \
           view/bull_card/bullmodel.cpp \
           util/morning_timer.cpp

HEADERS += stock_server/stock_provider.grpc.pb.h \
           stock_server/stock_provider.pb.h \
           stock_server/data_provider.h \
           stock_server/stock_object.h \
           stock_server/tick_thread.h \
           stock_server/bidask_thread.h \
           stock_server/subject_thread.h \
           stock_server/time_thread.h \
           stock_server/time_info.h \
           stock_server/plugin/chooser/chooserplugin.h \
           stock_server/plugin/chooser/topamount.h \
           stock_model/stockmodel.h \
           stock_model/chart_creator.h \
           view/mainwindow.h \
           view/statusbar.h \
           view/tick_view/tickwindow.h \
           view/bull_card/bullcard.h \
           view/bull_card/bulltable.h \
           view/bull_card/bullmodel.h \
           util/morning_timer.h
