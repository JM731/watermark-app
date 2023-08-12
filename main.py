from PyQt6.QtWidgets import (QMainWindow,
                             QApplication,
                             QLabel,
                             QWidget,
                             QGridLayout,
                             QPushButton,
                             QLineEdit,
                             QFileDialog,
                             QStackedWidget,
                             QMessageBox,
                             QSpinBox,
                             QColorDialog,
                             QGroupBox,
                             QSizePolicy,
                             QRadioButton,
                             QButtonGroup,
                             QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QImage
from PIL import Image, ImageDraw, ImageFont


def generate_positions():
    tuples_list = []

    for y_num in range(1, 9, 2):
        y = y_num / 8

        if y_num % 4 == 1:
            x_values = [1/6 + i * 1/3 for i in range(3)]
        else:
            x_values = [i * 1/3 for i in range(4)]

        tuples_list.extend([(x, y) for x in x_values])

    return tuples_list


def PIL_to_qimage(pil_img):
    temp = pil_img.convert('RGBA')
    return QImage(
        temp.tobytes('raw', "RGBA"),
        temp.size[0],
        temp.size[1],
        QImage.Format.Format_RGBA8888
    )


def get_text_color(rgb):

    luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

    if luminance > 100:
        return "black"
    return "white"


positions = generate_positions()


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.setWindowTitle("Watermark App")
        self.setFixedSize(1200, 750)

        self.current_image = None
        self.download_image = None
        self.font_style = {
            "type": "arial.ttf",
            "color": (255, 255, 255),
        }

        self.image_display_stack = QStackedWidget()
        self.image_display = QLabel()
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_font_button = QPushButton("Upload font type")
        self.remove_font_button = QPushButton("Remove Font")
        self.remove_font_button.hide()
        self.font_buttons_layout = QHBoxLayout()

        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 100)
        self.font_size_spinbox.setValue(36)

        self.color_picker_button = QPushButton("Choose color")
        button_size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.color_picker_button.setSizePolicy(button_size_policy)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Write your watermark here...")

        self.radio_button_single = QRadioButton("Single")
        self.radio_button_multiple = QRadioButton("Multiple")
        self.radio_button_single.setChecked(True)

        self.radio_button_group = QButtonGroup()
        self.radio_button_group.addButton(self.radio_button_single)
        self.radio_button_group.addButton(self.radio_button_multiple)

        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        layout = QGridLayout()
        font_groupbox = QGroupBox("Font Style")
        font_style_layout = QGridLayout()

        upload_image_button = QPushButton("Upload")
        download_button = QPushButton("Download")

        font_type_label = QLabel("Font Type")
        font_size_label = QLabel("Font Size")

        upload_label_font = QFont()
        upload_label_font.setPointSize(36)
        upload_label_font.setBold(True)
        upload_image_label = QLabel("Upload an image")
        upload_image_label.setFont(upload_label_font)
        upload_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_image_label.setScaledContents(True)

        self.image_display_stack.addWidget(upload_image_label)
        self.image_display_stack.addWidget(self.image_display)

        upload_image_button.clicked.connect(self.uploadImage)
        download_button.clicked.connect(self.downloadImage)
        self.text_input.textEdited.connect(self.insertWatermark)
        self.upload_font_button.clicked.connect(self.uploadFont)
        self.remove_font_button.clicked.connect(self.onRemoveFont)
        self.color_picker_button.clicked.connect(self.pickColor)
        self.font_size_spinbox.valueChanged.connect(self.insertWatermark)
        self.radio_button_group.buttonClicked.connect(self.insertWatermark)

        self.font_buttons_layout.addWidget(self.upload_font_button)
        self.font_buttons_layout.addWidget(self.remove_font_button)

        font_style_layout.addWidget(font_type_label, 0, 0, 1, 1)
        font_style_layout.addWidget(font_size_label, 0, 1, 1, 1)
        font_style_layout.addWidget(self.color_picker_button, 0, 2, 2, 1)
        font_style_layout.addLayout(self.font_buttons_layout, 1, 0, 1, 1)
        font_style_layout.addWidget(self.font_size_spinbox, 1, 1, 1, 1)

        font_groupbox.setLayout(font_style_layout)
        layout.addWidget(upload_image_button, 0, 0, 1, 8)
        layout.addWidget(download_button, 0, 8, 1, 8)
        layout.addWidget(self.image_display_stack, 1, 0, 1, 16)
        layout.addWidget(self.text_input, 2, 0, 1, 16)
        layout.addWidget(self.radio_button_single, 3, 0, 1, 1)
        layout.addWidget(self.radio_button_multiple, 3, 1, 1, 1)
        layout.addWidget(font_groupbox, 4, 0, 1, 16)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.show()

    def uploadImage(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)")
        if file_name:
            valid_extensions = [".png", ".jpg", ".jpeg", ".bmp"]
            file_extension = file_name[file_name.rfind("."):].lower()

            if file_extension in valid_extensions:
                pixmap = QPixmap(file_name)
                self.setPixmap(pixmap)

                self.current_image = pixmap

                if self.image_display_stack.currentIndex() == 0:
                    self.image_display_stack.setCurrentIndex(1)
            else:
                self.invalidFileMessage("Please upload an image file with one of the"
                                        " following extensions: .png, .jpg, .jpeg, .bmp.")

    def invalidFileMessage(self, text):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Invalid File Format")
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def pickColor(self):
        color = QColorDialog.getColor()
        rgb = (color.red(), color.green(), color.blue())
        if color.isValid():
            self.color_picker_button.setText(color.name())
            self.color_picker_button.setStyleSheet(f"background-color: {color.name()};"
                                                   f" color: {get_text_color(rgb)};")
            self.font_style["color"] = rgb

        self.insertWatermark()

    def uploadFont(self):
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Select TTF Font File",
                                                   "",
                                                   "Font Files (*.ttf);;All Files (*)")
        if file_name:
            file_extension = file_name[file_name.rfind("."):].lower()

            if file_extension == ".ttf":
                self.font_style["type"] = file_name
                display_name = file_name.split("/")[-1]
                if len(display_name) > 25:
                    display_name = "..." + display_name[-22:]
                self.upload_font_button.setText(display_name)
                self.remove_font_button.show()

            else:
                self.invalidFileMessage("Please select a TTF font file.")

        self.insertWatermark()

    def onRemoveFont(self):
        self.font_style["type"] = "arial.ttf"
        self.remove_font_button.hide()
        self.upload_font_button.setText("Upload font type")
        self.insertWatermark()

    def setPixmap(self, pixmap):
        if pixmap.width() >= self.width() or pixmap.height() >= self.height():
            self.pixmap = pixmap.scaled(self.width(),
                                        self.height(),
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
            self.image_display.setScaledContents(True)
        else:
            self.pixmap = pixmap
            self.image_display.setScaledContents(False)

        self.image_display.setPixmap(self.pixmap)

    def downloadImage(self):
        if self.download_image:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                       "Images (*.png *.jpg *.jpeg *.bmp *.gif)")

            if file_path:
                self.download_image.save(file_path)

    def insertWatermark(self):
        watermark = self.text_input.text()

        if self.current_image:

            image = self.current_image.copy()

            if watermark:

                image = Image.fromqimage(image.toImage())
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype(self.font_style["type"], size=self.font_size_spinbox.value())
                image_width, image_height = image.size

                if self.radio_button_single.isChecked():

                    x = image_width // 2
                    y = int(0.75 * image_height)
                    draw.text((x, y), watermark, self.font_style["color"], font, anchor="mm")

                elif self.radio_button_multiple.isChecked():

                    for position in positions:
                        x = int(position[0] * image_width)
                        y = int(position[1] * image_height)
                        draw.text((x, y), watermark, self.font_style["color"], font, anchor="mm")

                qimage = PIL_to_qimage(image)
                pixmap = QPixmap.fromImage(qimage)
                self.download_image = pixmap

            else:

                self.download_image = None
                pixmap = image

            self.setPixmap(pixmap)


if __name__ == "__main__":
    main_event_thread = QApplication([])
    main_event_thread.setStyle("Fusion")
    window = Window()
    main_event_thread.exec()
