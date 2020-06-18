import QtQuick 2.0
import QtQuick.Layouts 1.0
import QtQuick.Controls 1.4

RowLayout {
    id: searchHeader

    signal searchClicked(string code, date untilTime, int countDays)

    TextField {
        Layout.fillWidth: true
        Layout.fillHeight: true
        inputMethodHints: Qt.ImhTime
        inputMask: "D999/B9/99"
    }

    TextField {
        Layout.fillWidth: true
        Layout.fillHeight: true        
    }

    Button {
        Layout.fillWidth: true
        Layout.fillHeight: true
        text: "Search"
        onClicked: {
            console.log("clicked")
            searchHeader.searchClicked("A005930", Date.fromLocaleString(Qt.locale(), "06/12/2020", "MM/dd/yyyy"), 200)
        }
    }
}
