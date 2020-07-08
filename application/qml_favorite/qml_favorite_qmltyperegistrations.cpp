/****************************************************************************
** Generated QML type registration code
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <QtQml/qqml.h>
#include <QtQml/qqmlmoduleregistration.h>

#include <FavoriteListModel.h>
#include <RecentListModel.h>

void qml_register_types_favorite_backend()
{
    qmlRegisterTypesAndRevisions<FavoriteListModel>("favorite.backend", 1);
    qmlRegisterTypesAndRevisions<RecentListModel>("favorite.backend", 1);
    qmlRegisterModule("favorite.backend", 1, 0);
}

static const QQmlModuleRegistration registration("favorite.backend", 1, qml_register_types_favorite_backend);
