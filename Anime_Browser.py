import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QScrollArea, QFrame, QMessageBox, QListWidget,
    QListWidgetItem, QDialog, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QDesktopServices, QCursor, QFont
from PyQt5.QtCore import Qt, QUrl, QTimer, QSize


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("加载中")
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint  # 始终置顶
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        self.setStyleSheet("""
        QDialog {
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
        }
        QLabel {
            font-size: 18px;
            color: #333;
            font-weight: bold;
        }
        """)

        layout = QVBoxLayout(self)
        self.loading_label = QLabel("正在加载，请稍候...")
        self.loading_label.setAlignment(Qt.AlignCenter)

        # 添加加载动画（可选）
        self.movie_label = QLabel()
        self.movie_label.setFixedSize(50, 50)

        layout.addWidget(self.loading_label)
        layout.addWidget(self.movie_label, 0, Qt.AlignCenter)
        self.setFixedSize(200, 150)



class AnimeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_loading = None  # 用于跟踪当前加载提示

    def initUI(self):
        self.setWindowTitle('动漫信息查询')
        self.setGeometry(100, 100, 800, 600)

        self.setStyleSheet("""
        QFrame#animeFrame {
            background-color: #f0f0f0;
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            padding: 5px;
        }
        QFrame#animeFrame:hover {
            background-color: #e0e0e0;
            border: 2px solid #a0a0a0;
        }
        QFrame#animeFrame:pressed {
            background-color: #d0d0d0;
            border: 2px solid #808080;
        }
        """)

        # 主布局
        main_layout = QVBoxLayout()

        # 输入区域布局
        input_layout = QHBoxLayout()

        # 动漫名称输入
        self.msg_label = QLabel('动漫名称:')
        self.msg_input = QLineEdit()
        input_layout.addWidget(self.msg_label)
        input_layout.addWidget(self.msg_input)

        # 线路类型选择
        self.type_label = QLabel('选择线路:')
        self.type_combo = QComboBox()
        self.type_combo.addItems(['线路 1', '线路 2', '线路 3'])
        input_layout.addWidget(self.type_label)
        input_layout.addWidget(self.type_combo)

        # 查询按钮
        self.search_button = QPushButton('查询')
        self.search_button.clicked.connect(self.fetch_anime_data)
        input_layout.addWidget(self.search_button)

        main_layout.addLayout(input_layout)

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # 添加默认提示
        self.add_default_prompt()

        self.setLayout(main_layout)

    def add_default_prompt(self):
        """添加默认提示信息"""
        prompt_label = QLabel("点击右上角‘查询’按钮搜索，可能要一会\n如果太久（超过1分钟）还没加载出来那可能是网络炸了或者你得把搜索的关键词写得详细点\n每次点按钮和其他东西，点一次就够了！不要狂点！")
        prompt_label.setAlignment(Qt.AlignCenter)
        prompt_label.setStyleSheet("""
            QLabel {pyinstaller --onefile --noconsole --clean your_script.py
                color: #666;
                font-size: 18px;
                font-style: italic;
                margin-top: 50px;
            }
        """)
        self.scroll_layout.addWidget(prompt_label)

    def show_loading(self, text="正在加载..."):
        """显示加载提示"""
        if self.current_loading:
            self.current_loading.deleteLater()

        loading_frame = QFrame()
        loading_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        loading_layout = QVBoxLayout(loading_frame)
        loading_label = QLabel(text)
        loading_label.setAlignment(Qt.AlignCenter)
        loading_layout.addWidget(loading_label)

        self.current_loading = loading_frame
        self.scroll_layout.addWidget(loading_frame)
        QApplication.processEvents()  # 强制立即更新UI

    def clear_loading(self):
        """清除加载提示"""
        if self.current_loading:
            self.scroll_layout.removeWidget(self.current_loading)
            self.current_loading.deleteLater()
            self.current_loading = None
            QApplication.processEvents()

    def fetch_anime_data(self):
        anime_name = self.msg_input.text().strip()
        if not anime_name:
            QMessageBox.warning(self, '输入错误', '请输入动漫名称')
            return

        self.search_button.setEnabled(False)
        self.show_loading()

        line_type = self.type_combo.currentIndex() + 1

        url = 'https://oiapi.net/API/Anime'
        params = {
            'msg': anime_name,
            'n': 0,
            'j': 0,
            'type': line_type
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            self.clear_loading()
            self.search_button.setEnabled(True)

            if data.get('code') == 200:
                self.display_anime_list(data.get('data', []))
            else:
                QMessageBox.warning(self, '查询失败', data.get('msg', '未知错误'))

        except requests.RequestException as e:
            self.clear_loading()
            self.search_button.setEnabled(True)
            QMessageBox.critical(self, '请求异常', f'请求过程中发生错误: {e}')

    def display_anime_list(self, anime_list):
        # 清空之前的内容（包括默认提示）
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        if not anime_list:
            QMessageBox.information(self, '无结果', '未找到相关动漫')
            return

        for index, anime in enumerate(anime_list):
            anime_frame = QFrame()
            anime_frame.setObjectName("animeFrame")  # 应用样式表
            anime_frame.setCursor(QCursor(Qt.PointingHandCursor))  # 设置手型光标
            anime_layout = QHBoxLayout(anime_frame)

            # 封面
            image_label = QLabel()
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(anime['image']).content)
            image_label.setPixmap(pixmap.scaled(100, 150, Qt.KeepAspectRatio))
            anime_layout.addWidget(image_label)

            # 动漫信息
            info_layout = QVBoxLayout()
            name_label = QLabel(f"名称: {anime['name']}")
            year_label = QLabel(f"年份: {anime['year']}")
            status_label = QLabel(f"状态: {anime['ji']}")
            info_layout.addWidget(name_label)
            info_layout.addWidget(year_label)
            info_layout.addWidget(status_label)

            # 点击事件
            anime_frame.mousePressEvent = lambda event, idx=index + 1: self.show_anime_details(idx)

            anime_layout.addLayout(info_layout)
            self.scroll_layout.addWidget(anime_frame)

    def show_anime_details(self, n_index):
        # 在显示详情前清空加载提示
        self.clear_loading()
        self.show_loading("正在加载动漫详情...")
        line_type = self.type_combo.currentIndex() + 1
        anime_name = self.msg_input.text().strip()

        url = 'https://oiapi.net/API/Anime'
        params = {
            'msg': anime_name,
            'n': n_index,
            'j': 0,
            'type': line_type
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            self.clear_loading()

            if data.get('code') == 200:
                anime_data = data.get('data', {})
                self.open_anime_detail_window(anime_data, n_index)
            else:
                QMessageBox.warning(self, '查询失败', data.get('msg', '未知错误'))
        except requests.RequestException as e:
            self.clear_loading()
            QMessageBox.critical(self, '请求异常', f'请求过程中发生错误: {e}')

    def open_anime_detail_window(self, anime_data, n_index):
        detail_window = QDialog(self)
        detail_window.setWindowTitle(anime_data.get('name', '动漫详情'))
        detail_window.setGeometry(150, 150, 600, 400)
        detail_window.setWindowFlags(detail_window.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout(detail_window)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 封面
        image_label = QLabel()
        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(anime_data['image']).content)
        image_label.setPixmap(pixmap.scaled(200, 300, Qt.KeepAspectRatio))
        scroll_layout.addWidget(image_label, alignment=Qt.AlignCenter)

        # 信息标签
        info_labels = [
            f"名称: {anime_data.get('name', 'N/A')}",
            f"类别: {anime_data.get('class', 'N/A')}",
            f"标签: {anime_data.get('tags', 'N/A')}",
            f"状态: {anime_data.get('ji', 'N/A')}",
            f"年份: {anime_data.get('year', 'N/A')}",
            f"国家: {anime_data.get('country', 'N/A')}",
            f"简介: {anime_data.get('desc', 'N/A')}"
        ]

        for label in info_labels:
            lbl = QLabel(label)
            lbl.setWordWrap(True)
            scroll_layout.addWidget(lbl)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 集数列表
        playlist_label = QLabel("集数列表:")
        main_layout.addWidget(playlist_label)

        playlist_widget = QListWidget()
        for idx, ep in enumerate(anime_data.get('playlist', [])):
            item = QListWidgetItem(ep)
            item.setData(Qt.UserRole, idx + 1)
            playlist_widget.addItem(item)

        playlist_widget.itemClicked.connect(lambda item: self.handle_episode_click(n_index, item))
        main_layout.addWidget(playlist_widget)

        detail_window.exec_()

    def handle_episode_click(self, n_index, item):
        self.show_loading("正在加载视频信息...")
        line_type = self.type_combo.currentIndex() + 1
        anime_name = self.msg_input.text().strip()
        episode_index = item.data(Qt.UserRole)

        url = 'https://oiapi.net/API/Anime'
        params = {
            'msg': anime_name,
            'n': n_index,
            'j': episode_index,
            'type': line_type
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            self.clear_loading()

            if data.get('code') == 200:
                episode_data = data.get('data', {})
                self.show_episode_details(episode_data)
            else:
                QMessageBox.warning(self, '获取集数失败', data.get('msg', '未知错误'))
        except requests.RequestException as e:
            self.clear_loading()
            QMessageBox.critical(self, '请求异常', f'请求过程中发生错误: {e}')

    def show_episode_details(self, episode_data):
        detail_dialog = QDialog(self)
        detail_dialog.setWindowTitle(f"{episode_data.get('name', 'N/A')} - {episode_data.get('play_num', 'N/A')}")
        detail_dialog.setGeometry(200, 200, 400, 200)
        detail_dialog.setWindowFlags(detail_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(detail_dialog)

        # 集数名称
        name_label = QLabel(f"名称: {episode_data.get('name', 'N/A')}")
        layout.addWidget(name_label)

        # 集数编号
        play_num_label = QLabel(f"集数: {episode_data.get('play_num', 'N/A')}")
        layout.addWidget(play_num_label)

        # 视频类型
        video_type_label = QLabel(f"视频类型: {episode_data.get('video_type', 'N/A')}")
        layout.addWidget(video_type_label)

        play_url = episode_data.get('play_url', '')
        if play_url:
            play_url_label = QLabel(f'<a href="{play_url}">点击播放（外部链接）</a>')
            play_url_label.setOpenExternalLinks(True)
            layout.addWidget(play_url_label)
        else:
            layout.addWidget(QLabel("暂无播放链接"))

        detail_dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AnimeApp()
    ex.show()
    sys.exit(app.exec_())
