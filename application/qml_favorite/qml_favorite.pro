######################################################################
# Automatically generated by qmake (3.1) Wed Mar 25 10:37:47 2020
######################################################################

TEMPLATE = app
CONFIG += link_pkgconfig
CONFIG += qmltypes
CONFIG += metatypes
TARGET = qml_favorite
INCLUDEPATH += . /home/nnnlife/workspace/trader/application/data_provider
QT += widgets
QT += qml quick
QML_IMPORT_NAME = favorite.backend
QML_IMPORT_MAJOR_VERSION = 1
LIBS += -L/home/nnnlife/workspace/trader/application/data_provider -lMorningDataProvider
PKGCONFIG += protobuf
#PKGCONFIG += grpc++

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
           StockStat.cpp \
           AbstractListModel.cpp \
           FavoriteListModel.cpp \
           ViListModel.cpp \
           YtopAmountListModel.cpp \
           TtopAmountListModel.cpp \
           RecentListModel.cpp

HEADERS += StockStat.h \ 
           AbstractListModel.h \
           FavoriteListModel.h \
           ViListModel.h \
           YtopAmountListModel.h \
           TtopAmountListModel.h \
           RecentListModel.h

