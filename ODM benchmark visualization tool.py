import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QComboBox, QPushButton, QFileDialog, QStackedWidget
import pandas as pd

class LogHelperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogHelper Widget")
        self.setGeometry(100, 100, 400, 200)
        self.merged_df = pd.DataFrame()

        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.initVis()

        # 将堆叠窗口添加到主布局中
        layoutMain = QVBoxLayout()
        layoutBtns=QVBoxLayout()

        # 初始化主窗口部件
        self.selectFilesButton = QPushButton("Select Files")
        self.selectFilesButton.clicked.connect(self.showVisPage) 
        layoutBtns.addWidget(self.selectFilesButton)

        self.finalizeButton = QPushButton("Final Results")
        self.finalizeButton.clicked.connect(self.finalizeProcess)
        layoutBtns.addWidget(self.finalizeButton)

        layoutMain.addLayout(layoutBtns)

        self.setLayout(layoutMain)


    def initVis(self):
        # 初始化显示内容部件
        visWidget = QWidget()
        layoutVis = QVBoxLayout(visWidget)

        self.projectLabel = QLabel("Enter Project Name")
        layoutVis.addWidget(self.projectLabel)
        self.projectName = QLabel()
        layoutVis.addWidget(self.projectName)

        self.phaseLabel = QLabel("Enter Phase Name")
        layoutVis.addWidget(self.phaseLabel)
        self.phase = QComboBox()
        self.phase.addItems(["DB", "SI", "PV", "MV"])
        layoutVis.addWidget(self.phase)

        self.skuLabel = QLabel("Product SKU")
        layoutVis.addWidget(self.skuLabel)
        self.prodSKU = QLabel()
        layoutVis.addWidget(self.prodSKU)

        # 将内容部件添加到堆叠窗口
        self.stacked_widget.addWidget(visWidget)

    def showVisPage(self):
        # 切换到显示内容窗口
        self.stacked_widget.setCurrentIndex(1)  # 索引1对应显示内容窗口

    def selectFiles(self):
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(self, "Select Files", "", "CSV Files (*.csv)")
        # Process selected files here
        pass

    def finalizeProcess(self):
        # Implement finalize process logic here
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LogHelperApp()
    window.show()
    sys.exit(app.exec_())