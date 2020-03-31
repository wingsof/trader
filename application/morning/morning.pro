######################################################################
# Automatically generated by qmake (3.1) Wed Mar 25 10:37:47 2020
######################################################################

TEMPLATE = app
CONFIG += link_pkgconfig
TARGET = morning
INCLUDEPATH += .
QT += widgets
#LIBS += -L/usr/local/lib
PKGCONFIG += protobuf
PKGCONFIG += grpc++

# You can make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# Please consult the documentation of the deprecated API in order to know
# how to port your code away from it.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

# Input
SOURCES += main.cpp stock_provider.grpc.pb.cc stock_provider.pb.cc data_provider.cpp tick_thread.cpp bidask_thread.cpp
HEADERS += stock_provider.grpc.pb.h stock_provider.pb.h data_provider.h tick_thread.h bidask_thread.h