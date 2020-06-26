import QtQuick 2.0
import QtQuick.Layouts 1.0
import QtQuick.Controls 2.12
import search.backend 1.0


ApplicationWindow {
    id: root
    width: 1000
    height: 100
    visible: true

    ColumnLayout {
        id: col
        RowLayout {
            DateTime {
                id: dateTime
                Layout.minimumWidth: 350 
                Layout.preferredWidth: 250 
                Layout.preferredHeight: 40
                Layout.rightMargin: 50 
            }

            CodeSearch {
                id: codeSearch
                Layout.preferredWidth: 180 
                Layout.preferredHeight: 40
                Layout.rightMargin: 20
            }

            TextField {
                id: daysField
                Layout.preferredWidth: 50 
                Layout.preferredHeight: 40
                text: SearchBackend.days
            }


            Text {
                Layout.preferredWidth: 50 
                text: "DAYS"
            }

            Button {
                Layout.preferredWidth: 50
                Layout.preferredHeight: 40
                text: "SET"

                onClicked: {
                    SearchBackend.sendCurrent(codeSearch.code,
                                        new Date(dateTime.year, dateTime.month - 1, dateTime.day,
                                            dateTime.hour, dateTime.minute, 0),
                                        parseInt(daysField.text))
                }
            }

            
            Button {
                id: startButton
                Layout.leftMargin: 50
                Layout.preferredWidth: 80
                Layout.preferredHeight: 40
                text: "START"
                background: Rectangle {
                    color: {
                        if (startButton.down) {
                            return "#d0d0d0"
                        }
                        else {
                            if (SearchBackend.simulationRunning)
                                return "#ff0000"
                            else
                                return "#e0e0e0"
                        }
                    }
                }
            }

            Button {
                id: stopButton
                Layout.preferredWidth: 80
                Layout.preferredHeight: 40
                text: "STOP"
                background: Rectangle {
                    color: {
                        if (stopButton.down) {
                            return "#d0d0d0"
                        }
                        else {
                            if (!SearchBackend.simulationRunning)
                                return "#ff0000"
                            else
                                return "#e0e0e0"
                        }
                    }
                }

            }
            Layout.bottomMargin: 10
        }

        RowLayout {
            spacing: 20
            Button {
                text: "TICK"
                Layout.preferredWidth: 50 
                Layout.preferredHeight: 30 
                onClicked: {
                    SearchBackend.launchTick()
                }
            }

            Button {
                text: "DAY"
                Layout.preferredWidth: 50 
                Layout.preferredHeight: 30 
                onClicked: {
                    SearchBackend.launchDayChart()
                }
            }

            Button {
                text: "BA"
                Layout.preferredWidth: 50 
                Layout.preferredHeight: 30 
                onClicked: {
                    SearchBackend.launchBidAsk()
                }
            }

            Button {
                text: "VOL Trend"
                Layout.preferredWidth: 100 
                Layout.preferredHeight: 30 
                onClicked: {
                    SearchBackend.launchVolumeGraph()
                }
            }
        }
    }
}
