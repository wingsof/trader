######################################################################
# Automatically generated by qmake (3.1) Wed Mar 25 10:37:47 2020
######################################################################

include ( /opt/qwt-6.1.4/features/qwt.prf )
TEMPLATE = app
TARGET = chart
INCLUDEPATH += .
QT += widgets
QT += charts

OBJECTS_DIR=generated_files
MOC_DIR=generated_files

# You can make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# Please consult the documentation of the deprecated API in order to know
# how to port your code away from it.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

# Input
SOURCES += main.cpp testwidget.cpp qwt_widget.cpp
          
HEADERS += testwidget.h chart_creator.h qwt_widget.h
         
