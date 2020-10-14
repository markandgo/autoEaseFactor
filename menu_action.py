from aqt.gui_hooks import deck_browser_will_show_options_menu
from aqt import mw

try:
    import simulator
except ImportError:
    from .autoEaseFactor import simulator


from PyQt5.QtWidgets import QAction

# errors with event loop already running
# action = QAction("Simulate Auto Ease Factor", mw)
# action.triggered.connect(simulator.launch_simulator)
# mw.form.menuTools.addAction(action)


def add_option_to_menu(menu, deck_id):
    """Add simulate option to deck context menu."""
    action = menu.addAction("Simulate Auto Ease Factor")
    action.triggered.connect(simulator.launch_simulator)


# deck_browser_will_show_options_menu.append(add_option_to_menu)
