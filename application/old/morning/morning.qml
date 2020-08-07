import QtQuick 2.0
import QtQml.Models 2.1
import QtQuick.Layouts 1.1
import "./content"

Rectangle {
    id: mainRect
    width: 1000
    height: 800

    anchors.fill: parent
    
    GridLayout {
        anchors.fill: parent
        rows: 2
        columns: 1
        columnSpacing: 0
        rowSpacing: 0

        StatusBar {
            id: statusbar
            Layout.fillWidth: true
        }

        Rectangle {
            id: stockView
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "blue"
        }
    }
}