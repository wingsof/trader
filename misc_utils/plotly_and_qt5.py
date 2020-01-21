import plotly.offline as po
import plotly.graph_objs as go

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore, QtWidgets
import sys


def show_qt(fig):
    raw_html = '<html><head><meta charset="utf-8" />'
    raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
    raw_html += '<body>'
    raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
    raw_html += '</body></html>'

    fig_view = QWebEngineView()
    # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
    # for large figures.
    fig_view.setHtml(raw_html)
    fig_view.show()
    fig_view.raise_()
    return fig_view


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    fig = go.Figure(data=[{'type': 'scattergl', 'y': [2, 1, 3, 1]}])
    fig_view = show_qt(fig)
    sys.exit(app.exec_())
