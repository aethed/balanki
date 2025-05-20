# Shigeyuki <https://www.patreon.com/Shigeyuki>

from aqt import QAction, QDialog, QHBoxLayout, QIcon, QResizeEvent, QTabWidget, QTextBrowser, QWidget, Qt, qconnect
from aqt import QVBoxLayout, QLabel, QPushButton
from aqt import mw
from os.path import join, dirname
from aqt import QPixmap,gui_hooks
from aqt.utils import openLink

from .button_manager import mini_button
from .shige_addons import add_shige_addons_tab
from .endroll.endroll import add_credit_tab

from .change_log import OLD_CHANGE_LOG #🟢
from .patrons_list import PATRONS_LIST #🟢

CHANGE_LOG_DEFAULT = ""
CHANGE_LOG = "is_change_log"
CHANGE_LOG_DAY = "2025-02-15d" #🟢


POKEBALL_PATH = r"popup_icon.png"

THE_ADDON_NAME = "🎧Advanced Answer Sounds (Fixed by Shige)" #🟢

REPORT_URL = "https://shigeyukey.github.io/shige-addons-wiki/advanced-answer-sound.html#report"


# popup-size
# mini-pupup
SIZE_MINI_WIDTH = 500
SIZE_MINI_HEIGHT = 415
# Width: 500, Height: 415

# Large-popup
SIZE_BIG_WIDTH = 700
SIZE_BIG_HEIGHT = 500

ANKI_WEB_URL = ""
RATE_THIS_URL = ""

ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
# ｱﾄﾞｵﾝのURLが数値であるか確認
if (isinstance(ADDON_PACKAGE, (int, float))
    or (isinstance(ADDON_PACKAGE, str)
    and ADDON_PACKAGE.isdigit())):
    ANKI_WEB_URL = f"https://ankiweb.net/shared/info/{ADDON_PACKAGE}"
    RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"


PATREON_URL = "http://patreon.com/Shigeyuki"
REDDIT_URL = "https://www.reddit.com/r/Anki/comments/1b0eybn/simple_fix_of_broken_addons_for_the_latest_anki/"

POPUP_PNG = r"popup_shige.png"


NEW_FEATURE = """
2025-02-15
[1] Enhanced
    - Added decimal support for fade-in and fade-out.
    - Fixed a bug that sometimes occurs an error.

2025-01-25
[1] First Release
    - Latest Mac support added (arm64)
    - Linux support added (Python3.9-3.13)
    - New button for the user folder added.
"""


UPDATE_TEXT = "I updated this Add-on."

SPECIAL_THANKS ="""\
[ Patreon ] Special thanks
Without the support of my Patrons, I would never have been
able to develop this. Thank you very much!🙏"""

CHANGE_LOG_TEXT = """\
[ Change log : {addon} ]

Shigeyuki :
Hello, thank you for using this add-on!😆
{update_text}
{new_feature}
If you like this add-on, please support
my volunteer development on Patreon. Thank you!


[ Old change log ]
{old_change_log}

{special_thanks}

{patron}

""".format(addon=THE_ADDON_NAME,
            update_text=UPDATE_TEXT,
            new_feature=NEW_FEATURE,
            old_change_log = OLD_CHANGE_LOG,
            special_thanks=SPECIAL_THANKS,
            patron=PATRONS_LIST)



CHANGE_LOG_TEXT_B = """\
Shigeyuki :
Hello, thank you for using this add-on, I'm Shige!😆

I development of Anki Add-ons for Gamification Learning
and so far I fixed 40+ broken add-ons.
If you like this add-on, please support my development on Patreon,
and you can get add-ons for patrons only(about 28 Contents).

If you have any problems or requests feel free to contact me.
Thanks!

[1] How to contact me
    - AnkiWeb (Rate Comment) : You can contact me anonymously.
    - Reddit (Fixed add-ons) : You can request me to repair broken Add-ons.
    - Github (Issues) : Makes it easier to track problems.
    - Patreon (DM) : Response will be prioritized.


----
{addon}
[ Change log ]

{new_feature}

{old_change_log}

----
{special_thanks}

{patron}
""".format(
            addon=THE_ADDON_NAME,
            patron=PATRONS_LIST,
            special_thanks=SPECIAL_THANKS,
            new_feature=NEW_FEATURE,
            old_change_log=OLD_CHANGE_LOG,
            )



# ------- Rate This PopUp ---------------

def set_gui_hook_change_log():
    gui_hooks.main_window_did_init.append(change_log_popup)
    # gui_hooks.main_window_did_init.append(add_config_button)

def change_log_popup(*args,**kwargs):
    try:
        config = mw.addonManager.getConfig(__name__)
        if (config.get(CHANGE_LOG, CHANGE_LOG_DEFAULT) != CHANGE_LOG_DAY):
            dialog = CustomDialog(mw, CHANGE_LOG_TEXT, size_mini=True)
            dialog.show()
            config[CHANGE_LOG] =  CHANGE_LOG_DAY
            mw.addonManager.writeConfig(__name__, config)
    except Exception as e:
        pass




def change_log_popup_B(*args,**kwargs):
    try:
        dialog = CustomDialog(mw, CHANGE_LOG_TEXT_B, True)
        dialog.show()
    except Exception as e:
        pass



# ----- add-onのconfigをｸﾘｯｸしたら設定ｳｨﾝﾄﾞｳを開く -----
def add_config_button():
    mw.addonManager.setConfigAction(__name__, change_log_popup_B)
    # ----- ﾒﾆｭｰﾊﾞｰに追加 -----🟢
    # action = QAction(THE_ADDON_NAME, mw)
    # qconnect(action.triggered, change_log_popup_B)
    # mw.form.menuTools.addAction(action)

# ================================================


class CustomDialog(QDialog):
    def __init__(self, parent=None,change_log_text=CHANGE_LOG_TEXT,more_button=False,size_mini=False):
        super().__init__(parent)

        addon_path = dirname(__file__)
        icon = QPixmap(join(addon_path, POPUP_PNG))

        if size_mini:
            self.resize(SIZE_MINI_WIDTH, SIZE_MINI_HEIGHT)
        else:
            self.resize(SIZE_BIG_WIDTH, SIZE_BIG_HEIGHT)

        pokeball_icon = QIcon(join(addon_path, POKEBALL_PATH))
        self.setWindowIcon(pokeball_icon)

        self.setWindowTitle(THE_ADDON_NAME)

        tab_widget = QTabWidget()
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        icon_label = QLabel()
        icon_label.setPixmap(icon)

        hbox = QHBoxLayout()

        change_log_label = QTextBrowser()
        change_log_label.setReadOnly(True)
        change_log_label.setOpenExternalLinks(True)

        change_log_label.setPlainText(change_log_text)

        hbox.addWidget(icon_label)
        hbox.addWidget(change_log_label)

        tab_layout.addLayout(hbox)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.yes_button = QPushButton("💖Patreon")
        self.yes_button.clicked.connect(lambda: openLink(PATREON_URL))
        self.yes_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        mini_button(self.yes_button)

        self.report_button = QPushButton("🚨Report")
        self.report_button.clicked.connect(lambda: openLink(REPORT_URL))
        self.report_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        mini_button(self.report_button)

        self.no_button = QPushButton("OK (Close)")
        self.no_button.clicked.connect(self.close)
        self.no_button.setFixedWidth(120)

        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.report_button)
        button_layout.addWidget(self.no_button)

        tab_widget.addTab(tab, "Change Log")
        add_credit_tab(self, tab_widget)
        add_shige_addons_tab(self, tab_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tab_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def resizeEvent(self, event:"QResizeEvent"):
        size = event.size()
        print(f"Width: {size.width()}, Height: {size.height()}")
        super().resizeEvent(event)
