######################################################################
# Automatically generated by qmake (3.1) Wed Mar 25 10:37:47 2020
######################################################################

include ( /opt/qwt-6.1.4/features/qwt.prf )
CONFIG += link_pkgconfig
TEMPLATE = app
TARGET = chartlib_compare
INCLUDEPATH += .
QT += widgets
QT += charts

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
           stock_provider.grpc.pb.cc \
           stock_provider.pb.cc \
           minutedata_provider.cpp \
           data_provider.cpp \
           pastminutechart.cpp \
           minutewindow.cpp \
           qwt_pastminutechart.cpp \
           qwt_minutewindow.cpp \
           comparewidget.cpp 

          
HEADERS +=  \
           stock_provider.grpc.pb.h \
           stock_provider.pb.h \
           minutedata_provider.h \
           data_provider.h \
           pastminutechart.h \
           minutewindow.h \
           qwt_pastminutechart.h \
           qwt_minutewindow.h \
           comparewidget.h
