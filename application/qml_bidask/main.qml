import QtQuick 2.15
import QtQuick.Layouts 1.0
import QtQuick.Controls 2.12
import BidAskModel 1.0
import Qt.labs.qmlmodels 1.0
import "../data_provider"


ApplicationWindow {
    id: root
    width: 1000; height: 800
    visible: true

    TableView {
        id: bidAskTable
        anchors.fill: parent
        columnSpacing: 0
        rowSpacing: 0
        clip: true

        model: BidAskModel{
            id: bidaskModel
        }

        delegate: DelegateChooser {
            DelegateChoice {
                column: 3
                Rectangle {
                    id: priceColumn
                    implicitWidth: (root.width) / 7
                    implicitHeight: (root.height) / 22

                    color: {
                        if (model.row <= 20 && model.row > 10) return "#10ff0000"
                        else if (model.row > 0 && model.row <= 10) return "#100000ff"
                        else return "#ffffff"
                    }
                    border.color: bidaskModel.highlight == model.row ?"black":"#d7d7d7"
                    border.width: bidaskModel.highlight == model.row ? 2:1

                    Text {
                        text: display
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        anchors.fill: parent
                        font.pointSize: 12
                        color: {
                            var fcolor = "black"

                            if (typeof(display) == "number"){
                                if (display > bidaskModel.yesterdayClose) {
                                    fcolor = "red"
                                }
                                else if (display < bidaskModel.yesterdayClose) {
                                    fcolor = "blue"
                                }
                            }
                            // console.log("display", typeof(display), parseInt(display), bidaskModel.yesterdayClose, typeof(bidaskModel.yesterdayClose), fcolor)
                            return fcolor;
                        }
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            console.log("row : ", model.row)
                        }
                    }
                }
            }

            DelegateChoice {
                column: 2
                Rectangle {
                    id: askRemainColumn
                    implicitWidth: (root.width) / 7
                    implicitHeight: (root.height) / 22
                    color: "#ffffff"
                    border.color: "#d7d7d7"
                    border.width: 1

                    Rectangle {
                        height: parent.height
                        color: "#100000ff"
                        anchors.right: askRemainColumn.right
                        width: {
                            if (model.row <= 10 && typeof(display) == "number" && bidaskModel.totalAskRemain > 0) {
                                return parent.width * display / bidaskModel.totalAskRemain
                            }
                            return 0
                        }
                    }
                    Text {
                        text: {
                            if (model.row == 0)
                                return bidaskModel.totalAskRemain
                            else
                                return display
                        }
                        anchors.fill: parent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pointSize: 11
                        color: model.row == 11 ? "blue":"black"
                    }

                }
            }

            DelegateChoice {
                column: 4
                Rectangle {
                    id: bidRemainColumn
                    implicitWidth: (root.width) / 7
                    implicitHeight: (root.height) / 22
                    color: "#ffffff"
                    border.color: "#d7d7d7"
                    border.width: 1
                    Rectangle {
                        height: parent.height
                        color: "#10ff0000"
                        anchors.left: bidRemainColumn.left
                        width: {
                            if (model.row >= 11 && typeof(display) == "number" && bidaskModel.totalBidRemain > 0) {
                                return parent.width * display / bidaskModel.totalBidRemain
                            }
                            return 0
                        }
                    }
                    Text {
                        text: {
                            if (model.row == 21)
                                return bidaskModel.totalBidRemain
                            else
                                return display
                        }
                        anchors.fill: parent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pointSize: 11
                        color: model.row == 10 ? "red":"black"
                    }

                }
            }


            DelegateChoice {
                Rectangle {
                    implicitWidth: (root.width - 6) / 7
                    implicitHeight: (root.height - 20) / 22
                    color: "#ffffff"
                    border.color: "#d7d7d7"
                    border.width: {
                        if (model.column == 0 || model.column == 6)
                            return 1
                        return 0
                    }

                    Text {
                        text: display
                        anchors.fill: parent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pointSize: 10
                        color: {
                            if (typeof(display) == "number") {
                                if (display > 0)
                                    return "red"
                                else
                                    return "blue"
                            }
                            return "black"
                        }
                    }
                }
            }
        }
    }
}
