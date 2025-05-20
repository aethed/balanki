
from aqt import QTabWidget, QUrl, QWebEngineSettings
from aqt import QWidget
from os.path import join, dirname, exists
from aqt import  QWebEnginePage, QWidget, QWebEngineView, QVBoxLayout
from . import listOfSupportedPatrons

background = "Space.gif"

from aqt.utils import openLink
def handle_new_window(url):
    openLink(url)
class CustomWebEnginePage(QWebEnginePage):
    def createWindow(self, _type):
        new_page = CustomWebEnginePage(self)
        new_page.urlChanged.connect(handle_new_window)
        return new_page
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass


class EndrollWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        backColor = "rgb(54, 54, 54)"

        addon_path = dirname(__file__)
        background_image = join(addon_path, background)
        print(background_image)
        print(exists(background_image))

        # ｻﾝﾌﾟﾙﾃﾞｰﾀ
        credit_data_attributes = [
                                'credits',
                                # 'caractor',
                                # 'sound',
                                # 'addons',
                                # 'budle',
                                'patreon',
                                'thankYou',
                                ]

        # HTMLｺﾝﾃﾝﾂを生成
        html_content = f"""
            <html>
            <head>
                <style>
                    body {{
                        background-image: url("{background}");
                        background-attachment: fixed;
                        background-color: {backColor};
                        background-size: 128px 128px;
                        margin: 0;
                        padding: 0;
                        color: white;
                        font-family: 'Times New Roman', serif;
                        font-size: 18px;
                        text-align: center;
                    }}
                    .content {{
                        padding-top: 50px;
                    }}
                    a {{
                        color: white;
                    }}


                    ::-webkit-scrollbar {{
                        width: 16px;
                    }}
                    ::-webkit-scrollbar-track {{
                        background: url("{background}");
                        background-size: 128px 128px;
                    }}
                    ::-webkit-scrollbar-thumb {{
                        background-color: rgba(255, 255, 255, 0.5);
                        border-radius: 10px;
                        border: 3px solid transparent;
                        background-clip: content-box;
                    }}


                </style>
            </head>
            <body>
                <div class="content">
        """

        for attribute in credit_data_attributes:
            html_content += f"<p>{getattr(listOfSupportedPatrons, attribute)}</p>"

        html_content += """
                </div>
            </body>
            <script>
                function scrollToBottom() {{
                    window.scrollBy(0, 1);
                    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {{
                        clearInterval(scrollInterval);
                    }}
                }}
                var scrollInterval = setInterval(scrollToBottom, 50);
            </script>
            </html>
        """

        self.web_view = QWebEngineView()
        self.web_view.setPage(CustomWebEnginePage(self.web_view))
        # self.web_view.setHtml(html_content)
        self.web_view.setHtml(html_content, baseUrl=QUrl.fromLocalFile(addon_path + '/'))
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)


        layout = QVBoxLayout(self)
        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def showEvent(self, event):
        # ﾀﾌﾞが表示されたときにﾀｲﾏｰを開始（50ﾐﾘ秒ごとに更新）
        self.web_view.page().runJavaScript("clearInterval(scrollInterval);")
        self.web_view.page().runJavaScript("scrollInterval = setInterval(scrollToBottom, 50);")

    def hideEvent(self, event):
        self.web_view.page().runJavaScript("clearInterval(scrollInterval);")


def add_credit_tab(self, tab_widget:"QTabWidget"):

    credits_tab = EndrollWidget(self)
    tab_widget.addTab(credits_tab, "credit")
