import QtQuick 2.15
import QtQuick.Layouts 1.0
import QtQuick.Controls 2.12


ApplicationWindow {
    id: root
    width: 500; height: 500
    visible: true

    RowLayout { 
        anchors.fill: parent
        spacing: 0.0
        TodayBullListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
