from aqt import  QWebEnginePage, QWidget, QWebEngineView, QWebEngineSettings, QVBoxLayout,QTabWidget
import requests
from aqt.utils import openLink

# PATREON_LABEL_WIDTH = 500
# WIDGET_HEIGHT = 550

    #     self.adjust_self_size()


    # def adjust_self_size(self):
    #     min_size = self.layout().minimumSize()
    #     # self.resize(min_size.width(), min_size.height())
    #     self.resize(min_size.width(), WIDGET_HEIGHT)

def handle_new_window(url):
    openLink(url)

class CustomWebEnginePage(QWebEnginePage):
    def createWindow(self, _type):
        new_page = CustomWebEnginePage(self)
        new_page.urlChanged.connect(handle_new_window)
        return new_page

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass

def add_shige_addons_tab(self, tab_widget:"QTabWidget"):

    url = "https://raw.githubusercontent.com/shigeyukey/shige-addons/main/HTML/ShigeAddons.html"
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        html_content = response.text
    except:
        return

    tab4 = QWidget(self)

    web_view = QWebEngineView(tab4)
    web_view.setPage(CustomWebEnginePage(web_view))
    web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
    web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

    web_view.setHtml(html_content)

    tab4_layout = QVBoxLayout()
    tab4_layout.addWidget(web_view)
    tab4.setLayout(tab4_layout)
    tab_widget.addTab(tab4, "addons")

