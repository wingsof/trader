import QtQuick 2.0
import QtQuick.Layouts 1.0
import QtQuick.Controls 2.12
import MorningChartView 1.0


ApplicationWindow {
    id: root
    width: 1000; height: 800
    visible: true

    DayView {
        id: dayView
        anchors.fill: parent
    }
}
