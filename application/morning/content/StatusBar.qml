import QtQuick 2.0
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.4
import QtQuick.Controls 2.0


Rectangle {
    height: 80
    RowLayout {
        anchors.fill: parent
        TextField {
            id: codeId
            Layout.fillWidth: true
            Layout.preferredWidth: 100
            Layout.maximumWidth: 100
            text: 'A005930'
            focus: true
        }

        Button {
            id: codeSearch
            Layout.fillWidth: true
            text: "search"
            onClicked: {

            }
        }

        Button {
            id: datePicker
            Layout.fillWidth: true
            //inputMethodHints: Qt.ImhDate
            text: Qt.formatDate(cal.selectedDate, "dd-MM-yyyy")
            onClicked: {
                cal.visible = true
            }
        }

        Calendar {
            id: cal
            visible: false
            selectedDate: new Date()
        }
    }
}