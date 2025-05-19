from aqt import QPushButton, QSizePolicy, Qt

def mini_button(button:QPushButton):
    button.setStyleSheet("QPushButton { padding: 2px; }")
    button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    button.setFocusPolicy(Qt.FocusPolicy.NoFocus)