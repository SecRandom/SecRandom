from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel, QPushButton, QComboBox, QLineEdit, QFileDialog, QMessageBox
import json
import os
from loguru import logger

# 配置日志记录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger.add(
    os.path.join(log_dir, "SecRandom_{time:YYYY-MM-DD}.log"),
    rotation="1 MB",
    encoding="utf-8",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}"
)


class global_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("全局设置")
        self.setBorderRadius(8)
        self.settings_file = os.path.join(os.path.dirname(__file__), "..", "Settings", "Settings.json")
        self.default_settings = {
            "draw_mode": 0,
            "animation_mode": 0,
            "voice_enabled": True,
            "student_id": 0,
            "student_name": 0,
            "student_quantity_enabled": True,
            "class_quantity_enabled": True,
        }

        self.global_Draw_comboBox = ComboBox()
        self.global_Animation_comboBox = ComboBox()
        self.global_Voice_switch = SwitchButton()
        self.global_student_id_comboBox = ComboBox()
        self.global_student_name_comboBox = ComboBox()
        self.global_student_quantity_switch = SwitchButton()
        self.global_class_quantity_switch = SwitchButton()
        
        # 抽取模式下拉框
        self.global_Draw_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.global_Draw_comboBox.addItems(["重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部人)"])
        self.global_Draw_comboBox.currentIndexChanged.connect(self.save_settings)

        # 语音播放按钮
        self.global_Voice_switch.setOnText("开启")
        self.global_Voice_switch.setOffText("关闭")
        self.global_Voice_switch.checkedChanged.connect(self.on_global_Voice_switch_changed)

        # 动画模式下拉框
        self.global_Animation_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.global_Animation_comboBox.addItems(["手动停止动画", "自动播放完整动画", "直接显示结果"])
        self.global_Animation_comboBox.currentIndexChanged.connect(lambda: self.save_settings())

        # 学号格式下拉框
        self.global_student_id_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.global_student_id_comboBox.addItems(["⌈01⌋", "⌈ 1 ⌋", "⌈  1⌋"])
        self.global_student_id_comboBox.currentIndexChanged.connect(self.save_settings)

        # 姓名格式下拉框
        self.global_student_name_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.global_student_name_comboBox.addItems(["⌈张  三⌋", "⌈张三  ⌋", "⌈  张三⌋"])
        self.global_student_name_comboBox.currentIndexChanged.connect(self.save_settings)

        # 班级总人数下拉框
        self.global_student_quantity_switch.setOnText("显示")
        self.global_student_quantity_switch.setOffText("不显示")
        self.global_student_quantity_switch.checkedChanged.connect(self.on_global_Voice_switch_changed)

        # 便捷修改班级功能显示下拉框
        self.global_class_quantity_switch.setOnText("显示")
        self.global_class_quantity_switch.setOffText("不显示")
        self.global_class_quantity_switch.checkedChanged.connect(self.on_global_Voice_switch_changed)

        # 添加组件到分组中
        self.addGroup(FIF.SYNC, "抽取模式", "设置抽取模式", self.global_Draw_comboBox)
        self.addGroup(FIF.FEEDBACK, "语音播放", "设置结果公布时是否播放语音", self.global_Voice_switch)
        self.addGroup(FIF.VIDEO, "动画模式", "设置抽取时的动画播放方式", self.global_Animation_comboBox)
        self.addGroup(FIF.EDIT, "学号格式", "设置学号格式设置", self.global_student_id_comboBox)
        self.addGroup(FIF.EDIT, "姓名格式", "设置姓名格式设置", self.global_student_name_comboBox)
        self.addGroup(FIF.PEOPLE, "班级总人数", "设置班级总人数是否显示", self.global_student_quantity_switch)
        self.addGroup(FIF.EDUCATION, "便捷修改班级", "设置便捷修改班级功能是否显示", self.global_class_quantity_switch)

        self.load_settings()  # 加载设置
        self.save_settings()  # 保存设置

    def on_global_Voice_switch_changed(self, checked):
        self.save_settings()
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                logger.info(f"加载设置文件: {self.settings_file}")  # 打印日志信息
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    global_settings = settings.get("global", {})
                    
                    # 优先使用保存的文字选项
                    draw_mode_text = global_settings.get("draw_mode_text", self.global_Draw_comboBox.itemText(self.default_settings["draw_mode"]))
                    draw_mode = self.global_Draw_comboBox.findText(draw_mode_text)
                    if draw_mode == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的抽取模式文本: {draw_mode_text}")
                        draw_mode = global_settings.get("draw_mode", self.default_settings["draw_mode"])
                        if draw_mode < 0 or draw_mode >= self.global_Draw_comboBox.count():
                            # 如果索引值无效，则使用默认值  
                            logger.warning(f"无效的抽取模式索引: {draw_mode}")
                            draw_mode = self.default_settings["draw_mode"]
                        
                    animation_mode_text = global_settings.get("animation_mode_text", self.global_Animation_comboBox.itemText(self.default_settings["animation_mode"]))
                    animation_mode = self.global_Animation_comboBox.findText(animation_mode_text)
                    if animation_mode == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的动画模式文本: {animation_mode_text}")
                        animation_mode = global_settings.get("animation_mode", self.default_settings["animation_mode"])
                        if animation_mode < 0 or animation_mode >= self.global_Animation_comboBox.count():
                            # 如果索引值无效，则使用默认值
                            animation_mode = self.default_settings["animation_mode"]
                        
                    voice_enabled = global_settings.get("voice_enabled", self.default_settings["voice_enabled"])

                    student_id_text = global_settings.get("student_id_text", self.global_student_id_comboBox.itemText(self.default_settings["student_id"]))
                    student_id = self.global_student_id_comboBox.findText(student_id_text)
                    if student_id == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的学号格式文本: {student_id_text}")
                        student_id = global_settings.get("student_id", self.default_settings["student_id"])
                        if student_id < 0 or student_id >= self.global_student_id_comboBox.count():
                            # 如果索引值无效，则使用默认值
                            logger.warning(f"无效的学号格式索引: {student_id}")
                            student_id = self.default_settings["student_id"]
                    
                    student_name_text = global_settings.get("student_name_text", self.global_student_name_comboBox.itemText(self.default_settings["student_name"]))
                    student_name = self.global_student_name_comboBox.findText(student_name_text)
                    if student_name == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的姓名格式文本: {student_name_text}")
                        student_name = global_settings.get("student_name", self.default_settings["student_name"])
                        if student_name < 0 or student_name >= self.global_student_name_comboBox.count():
                            # 如果索引值无效，则使用默认值
                            logger.warning(f"无效的姓名格式索引: {student_name}")
                            student_name = self.default_settings["student_name"]

                    student_quantity_enabled = global_settings.get("student_quantity_enabled", self.default_settings["student_quantity_enabled"])

                    class_quantity_enabled = global_settings.get("class_quantity_enabled", self.default_settings["class_quantity_enabled"])
                    
                    self.global_Draw_comboBox.setCurrentIndex(draw_mode)
                    self.global_Animation_comboBox.setCurrentIndex(animation_mode)
                    self.global_Voice_switch.setChecked(voice_enabled)
                    self.global_student_id_comboBox.setCurrentIndex(student_id)
                    self.global_student_name_comboBox.setCurrentIndex(student_name)
                    self.global_student_quantity_switch.setChecked(student_quantity_enabled)
                    self.global_class_quantity_switch.setChecked(class_quantity_enabled)
                    logger.info(f"加载设置完成: draw_mode={draw_mode}, animation_mode={animation_mode}, voice_enabled={voice_enabled}, student_id={student_id}, student_name={student_name}, student_quantity_enabled={student_quantity_enabled}, class_quantity_enabled={class_quantity_enabled}")
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.global_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
                self.global_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
                self.global_Voice_switch.setChecked(self.default_settings["voice_enabled"])
                self.global_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
                self.global_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
                self.global_student_quantity_switch.setChecked(self.default_settings["student_quantity_enabled"])
                self.global_class_quantity_switch.setChecked(self.default_settings["class_quantity_enabled"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.global_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
            self.global_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
            self.global_Voice_switch.setChecked(self.default_settings["voice_enabled"])
            self.global_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
            self.global_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
            self.global_student_quantity_switch.setChecked(self.default_settings["student_quantity_enabled"])
            self.global_class_quantity_switch.setChecked(self.default_settings["class_quantity_enabled"])
            self.save_settings()
    
    def save_settings(self):
        # 先读取现有设置
        existing_settings = {}
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    existing_settings = {}

        # 先读取现有设置
        current_existing_settings = {}
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    current_existing_settings = json.load(f)
                except json.JSONDecodeError:
                    current_existing_settings = {}
        
        # 更新global部分的所有设置
        if "global" not in existing_settings:
            existing_settings["global"] = {}
            
        global_settings = existing_settings["global"]
        # 保存文字选项
        global_settings["draw_mode_text"] = self.global_Draw_comboBox.currentText()
        global_settings["animation_mode_text"] = self.global_Animation_comboBox.currentText()
        global_settings["student_id_text"] = self.global_student_id_comboBox.currentText()
        global_settings["student_name_text"] = self.global_student_name_comboBox.currentText()
        # 同时保存索引值
        global_settings["draw_mode"] = self.global_Draw_comboBox.currentIndex()
        global_settings["animation_mode"] = self.global_Animation_comboBox.currentIndex()
        global_settings["voice_enabled"] = self.global_Voice_switch.isChecked()
        global_settings["student_id"] = self.global_student_id_comboBox.currentIndex()
        global_settings["student_name"] = self.global_student_name_comboBox.currentIndex()
        global_settings["student_quantity"] = self.global_student_quantity_switch.isChecked()
        global_settings["class_quantity"] = self.global_class_quantity_switch.isChecked()
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)

        # 获取修改后的设置
        modified_settings = {
            "draw_mode": self.global_Draw_comboBox.currentIndex(),
            "animation_mode": self.global_Animation_comboBox.currentIndex(),  
            "voice_enabled": self.global_Voice_switch.isChecked(),
            "student_id": self.global_student_id_comboBox.currentIndex(),
            "student_name": self.global_student_name_comboBox.currentIndex(),
            "student_quantity_enabled": self.global_student_quantity_switch.isChecked(),
            "class_quantity_enabled": self.global_class_quantity_switch.isChecked()
        }

        # 检查draw_mode设置是否改变
        if current_existing_settings.get("global", {}).get("draw_mode") != modified_settings["draw_mode"]:
            import glob
            temp_dir = "app/resource/Temp"
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/*_draw_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                        Flyout.create(
                            icon=InfoBarIcon.SUCCESS,
                            title='清理成功',
                            content="由于您修改了 抽取模式\n临时抽取记录文件已清理成功",
                            target=self.global_Draw_comboBox,
                            parent=self,
                            isClosable=True,
                            aniType=FlyoutAnimationType.PULL_UP
                        )
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")
                        Flyout.create(
                            icon=InfoBarIcon.ERROR,
                            title='清理失败',
                            content=f"由于您修改了 抽取模式\n临时抽取记录文件清理失败\n错误信息: {e}",
                            target=self.global_Draw_comboBox,
                            parent=self,
                            isClosable=True,
                            aniType=FlyoutAnimationType.PULL_UP
                        )