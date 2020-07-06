import QtQuick 2.15
import QtQuick.Layouts 1.0
import QtQuick.Controls 2.15


Rectangle {
    color: "blue"
    RowLayout {
        anchors.fill: parent
        RoundButton {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: "Hello"
        }
    }
}
