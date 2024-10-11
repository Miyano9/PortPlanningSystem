import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.setParent(parent)

        # 初始化鼠标悬停事件
        self.rectangles = []  # 存储矩形的引用
        self.annotations = []  # 存储注释的引用
        self.text_annotation = None

        # 连接鼠标事件
        self.mpl_connect("motion_notify_event", self.on_hover)

    def plot_port_solution_enhanced(self, solution):
        """根据传入的solution数据绘制港口布局"""
        self.ax.clear()
        sns.set(style="whitegrid")
        palette = sns.color_palette("muted", 6)

        n = solution.shape[0]
        width_scale = 0.8
        height_scale = 0.8
        self.rectangles = []  # 清空以前的矩形

        for i in range(n):
            length_of_vessel = solution[i, 1]  # 船舶长度
            berth_time = solution[i, 2]        # 停泊时间
            departure_time = solution[i, 3]    # 离港时间

            position = i * (length_of_vessel * height_scale + 10)

            rect_height = length_of_vessel * height_scale
            rect_width = (departure_time - berth_time) * width_scale

            color = palette[i % len(palette)]

            # 绘制矩形并保存引用
            rect = plt.Rectangle((berth_time, position),
                                 rect_width,
                                 rect_height,
                                 facecolor=color, edgecolor='black', lw=1)

            self.ax.add_patch(rect)
            self.rectangles.append((rect, length_of_vessel, berth_time, departure_time))

            # 标注船舶编号
            self.ax.text(berth_time + rect_width / 2,
                         position + rect_height / 2,
                         str(i + 1), color='white', fontsize=12,
                         ha='center', va='center', weight='bold')

        self.ax.set_title('Port Planning', fontsize=16, weight='bold')
        self.ax.set_xlabel('Berth Time (minutes)', fontsize=14)
        self.ax.set_ylabel('Berth Position (m)', fontsize=14)

        sns.despine()
        self.ax.autoscale()
        self.ax.set_aspect('auto')

        # 初始化鼠标悬停显示信息的注释
        if self.text_annotation is None:
            self.text_annotation = self.ax.annotate("", xy=(0, 0), xytext=(20, 20),
                                                    textcoords="offset points",
                                                    bbox=dict(boxstyle="round", fc="w"),
                                                    arrowprops=dict(arrowstyle="->"))
        self.text_annotation.set_visible(False)

        self.draw()

    def on_hover(self, event):
        """鼠标悬停事件处理"""
        if not hasattr(self, 'text_annotation') or self.text_annotation is None:
            return

        is_visible = self.text_annotation.get_visible()
        annotation = self.text_annotation

        if event.inaxes == self.ax and self.rectangles:
            for rectangle, vessel_length, berth_time, departure_time in self.rectangles:
                if rectangle.contains(event)[0]:  # 检查鼠标是否在某个矩形内
                    xdata = event.xdata if event.xdata is not None else 0
                    ydata = event.ydata if event.ydata is not None else 0
                    annotation.xy = (xdata, ydata)
                    text = f"the length of vessel: {vessel_length}m\nthe berth time: {berth_time}\nthe departure time: {departure_time}"
                    annotation.set_text(text)
                    annotation.set_visible(True)
                    self.draw()
                    return

        if is_visible:
            annotation.set_visible(False)
            self.draw()


class PortLayoutApp(QMainWindow):
    def __init__(self):
        super(PortLayoutApp, self).__init__()
        self.setWindowTitle("港口布局绘制")
        self.showMaximized()

        # 读取Excel数据
        self.file_path = 'Vessel.xlsx'
        self.vessel_df = pd.read_excel(self.file_path)

        self.initUI()

    def initUI(self):
        widget = QWidget(self)
        self.setCentralWidget(widget)

        self.canvas = PlotCanvas(self, width=8, height=6)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.plot_button = QPushButton('绘制港口布局', self)
        self.plot_button.setStyleSheet("font-size: 16px; padding: 10px;")

        self.plot_button.clicked.connect(self.plot_port_layout)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.toolbar)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.plot_button)
        hbox.addStretch(1)

        vbox.addLayout(hbox)
        widget.setLayout(vbox)

    def plot_port_layout(self):
        try:
            solution = self.vessel_df[[
                'vessel_number', 'length_of_vessel', 'time_of_arrival_at_port', 'cargo_dead_weight'
            ]].values

            self.canvas.plot_port_solution_enhanced(solution)
        except Exception as e:
            print(f"绘图时发生错误: {e}")


def show_MainWindow():
    app = QApplication(sys.argv)
    window = PortLayoutApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    show_MainWindow()
