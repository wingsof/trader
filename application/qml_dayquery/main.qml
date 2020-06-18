import QtQuick 2.0
import QtQuick.Layouts 1.0
import QtQuick.Controls 2.12
import MorningChartView 1.0
import "./"


ApplicationWindow {
    id: root
    width: 1000; height: 800
    visible: true

    header: StatusBar {
        focus: true
        onSearchClicked: {
            dayView.search(code, untilTime, countDays)
        }
    }

    DayView {
        id: dayView
        anchors.fill: parent
    }
}
