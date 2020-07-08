import QtQuick 2.15
import QtQuick.Layouts 1.0
import QtQuick.Controls 2.12
import Qt.labs.qmlmodels 1.0
import favorite.backend 1.0

    
ListView {
    id: codeListView
    clip: true
    Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
    spacing: -1.0

    Component {
        id: profitText
        Text {
            leftPadding: 5

            verticalAlignment: Text.AlignVCenter
            color: {
                if (profit < 0.0)
                    return "blue"
                else if (profit > 0.0)
                    return "red"

                return "black"
            }
            text: profit.toFixed(2) + "%"
        }
    }

    Component {
        id: amountText

        Text {
            rightPadding: 3

            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignRight
            text: amount
        }
    }


    delegate: Rectangle {
        width: 200
        height: 50 
        border.width: 1
        border.color: "#80d7d7d7" 
        
        GridLayout {
            anchors.fill: parent
            rows: 3
            columns: 6
            rowSpacing: 0
            columnSpacing: 0
            Text {
                Layout.row: 0
                Layout.column: 0
                Layout.minimumWidth: parent.width * 4 / 6
                Layout.maximumWidth: parent.width * 4 / 6
                Layout.minimumHeight: parent.height * 2 / 3
                width: parent.width * 4 / 6
                height: parent.height * 2 / 3
                Layout.rowSpan: 2
                Layout.columnSpan: 4
                text: display
                verticalAlignment: Text.AlignVCenter
                leftPadding: 3
                elide: Text.ElideRight
                font.pointSize: 13
            }

            Loader {
                sourceComponent: amountText
                Layout.row: 0
                Layout.column: 4
                Layout.columnSpan: 2
                Layout.fillWidth: true
                height: parent.height / 3
                property var amount: tamount
            }
            Loader {
                sourceComponent: amountText
                Layout.row: 1
                Layout.column: 4
                Layout.columnSpan: 2
                Layout.fillWidth: true
                height: parent.height / 3

                property var amount: yamount
            }

            Loader {
                Layout.row: 2
                Layout.column: 0
                Layout.columnSpan: 2
                width: parent.width * 2 / 6
                height: parent.height / 3
                sourceComponent: profitText
                property double profit: tprofit
            }
             Loader {
                Layout.row: 2
                Layout.column: 2
                Layout.columnSpan: 2
                width: parent.width * 2 / 6
                height: parent.height / 3
                sourceComponent: profitText
                property double profit: yprofit
            }
            Text {
                Layout.row: 2
                Layout.column: 4
                Layout.columnSpan: 2
                width: parent.width * 2 / 6
                height: parent.height / 3
                text: code
            }
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: codeListView.currentIndex = index
        }
    }
    highlight: Rectangle {
        width: 200
        height: 100
        color: 'red'
    }
    
    onCurrentItemChanged: {
        codeListView.model.currentSelectionChanged(codeListView.currentIndex)
    }

    onCurrentIndexChanged: {
        codeListView.model.setCurrentIndex(currentIndex)
    }

    currentIndex: -1
}

