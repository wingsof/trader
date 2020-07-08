import QtQuick 2.15
import QtQuick.Layouts 1.0
import QtQuick.Controls 2.15


Rectangle {
    id: root
    property string firstText
    property string secondText
    property string thirdText
    property string fourthText
    property string buttonColor: 'salmon'

    signal selected(int index)

    RowLayout {
        anchors.fill: parent
        RoundButton {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: firstText
            visible: firstText.length > 0? true:false
            palette.button: buttonColor
            onClicked: root.selected(0)
        }

        RoundButton {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: secondText
            visible: secondText.length > 0? true:false
            palette.button: buttonColor
        }

        RoundButton {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: thirdText
            visible: thirdText.length > 0? true:false
            palette.button: buttonColor
        }
        
        RoundButton {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: fourthText
            visible: fourthText.length > 0? true:false
            palette.button: buttonColor
        }
    }
}
