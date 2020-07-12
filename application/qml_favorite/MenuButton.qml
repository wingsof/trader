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
    property string firstCheckText
    property bool firstCheck
    property string secondCheckText
    property bool secondCheck
    property string thirdCheckText
    property bool thirdCheck

    signal selected(int index)
    signal checkStateChanged(int index, bool state)

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
            onClicked: root.selected(1)
        }

        RoundButton {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: thirdText
            visible: thirdText.length > 0? true:false
            palette.button: buttonColor
            onClicked: root.selected(2)
        }
        
        RoundButton {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: fourthText
            visible: fourthText.length > 0? true:false
            palette.button: buttonColor
            onClicked: root.selected(3)
        }

        CheckBox {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: firstCheckText
            visible: firstCheckText.length > 0? true:false
            checked: firstCheck
            onClicked: root.checkStateChanged(0, checked)
        }

        CheckBox {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: secondCheckText
            visible: secondCheckText.length > 0? true:false
            checked: secondCheck
            onClicked: root.checkStateChanged(1, checked)
        }

        CheckBox {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            text: thirdCheckText
            visible: thirdCheckText.length > 0? true:false
            checked: thirdCheck
            onClicked: root.checkStateChanged(2, checked)
        }
    }
}
