#include "viewcontroller.h"

ViewController::ViewController()
: QObject(0) {
}


ViewController::~ViewController() {
}


void ViewController::setCurrentCode(const QString & code) {
    if (code != currentCode) {
        currentCode = code;
        emit codeChanged(currentCode);
    }
}
