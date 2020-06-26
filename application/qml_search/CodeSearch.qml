import QtQuick 2.0
import QtQuick.Layouts 1.0
import QtQuick.Controls 2.12
import search.backend 1.0


Item {
    property alias code: codeField.text
    RowLayout {
        TextField {
            id: codeField
            Layout.preferredWidth: 100
            text: SearchBackend.currentCode
        }

        Button {
            Layout.preferredWidth: 80
            text: "Search"
        }
    }
}
