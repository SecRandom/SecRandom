from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
from loguru import logger

from app.common.config import load_custom_font

class history_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("历史记录")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"
        self.default_settings = {
            "history_enabled": True
        }

        # 刷新按钮
        self.refresh_button = PrimaryPushButton('刷新列表/记录')
        self.refresh_button.setFixedSize(180, 50)
        self.refresh_button.setFont(QFont(load_custom_font(), 15))
        self.refresh_button.clicked.connect(self.refresh_class_list)
        
        # 选择班级的下拉框
        self.class_comboBox = ComboBox()
        self.class_comboBox.setFixedWidth(320)
        self.class_comboBox.setPlaceholderText("选择一个需要查看历史记录的班级")
        self.class_comboBox.addItems([])
        self.class_comboBox.setFont(QFont(load_custom_font(), 14))
        self.class_comboBox.currentIndexChanged.connect(self.load_students)

        # 选择同学的下拉框
        self.student_comboBox = ComboBox()
        self.student_comboBox.setFixedWidth(320)
        self.student_comboBox.setPlaceholderText("选择需要查看历史记录的同学")
        self.student_comboBox.addItems([])
        self.student_comboBox.setFont(QFont(load_custom_font(), 15))

        # 清除历史记录按钮
        self.clear_history_Button = PushButton("清除历史记录")
        self.clear_history_Button.clicked.connect(self.clear_history)
        self.clear_history_Button.setFont(QFont(load_custom_font(), 14))

        # 历史记录开关
        self.history_switch = SwitchButton()
        self.history_switch.setOnText("开启")
        self.history_switch.setOffText("关闭")
        self.history_switch.checkedChanged.connect(self.on_switch_changed)
        self.history_switch.setFont(QFont(load_custom_font(), 14))
        
        # 程序启动时自动加载班级名称
        self.refresh_class_list()
        # 当选择班级时加载对应的学生名称
        self.load_students()

        # 添加组件到分组中
        self.addGroup(FIF.SYNC, "刷新列表/记录", "点击按钮刷新班级列表/记录表格", self.refresh_button)
        self.addGroup(FIF.EDUCATION, "选择班级", "选择一个需要查看历史记录的班级", self.class_comboBox)
        self.addGroup(FIF.PEOPLE, "选择同学", "全班同学是详细的内容,个人是只有抽取的时间与方式", self.student_comboBox)
        self.addGroup(FIF.DELETE, "清除历史记录", "点击按钮清除当前选择的班级点名历史记录", self.clear_history_Button)
        self.addGroup(FIF.VIEW, "历史记录", "选择是否开启历史记录功能", self.history_switch)

        self.load_settings()
        self.save_settings()

    def on_switch_changed(self, checked):
        self.save_settings()

    def refresh_class_list(self):
        try:
            if os.path.exists("app/resource/class/class.ini"):
                with open("app/resource/class/class.ini", 'r', encoding='utf-8') as f:
                    classes = [line.strip() for line in f.read().split('\n') if line.strip()]
                    self.class_comboBox.clear()
                    self.class_comboBox.addItems(classes)
        except Exception as e:
            logger.error(f"加载班级名称失败: {str(e)}")

    def load_students(self):
        class_name = self.class_comboBox.currentText()
        try:
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_set = settings.get('list_strings', {})
                    list_strings_settings = list_strings_set.get('use_lists', False)
                    if not list_strings_settings:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people_{class_name}.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"
            except KeyError:
                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    students = [line.strip() for line in f.read().split('\n') if line.strip()]
                    self.student_comboBox.clear()
                    students = ['全班同学'] + students
                    self.student_comboBox.addItems(students)
        except Exception as e:
            logger.error(f"加载学生名称失败: {str(e)}")

    def clear_history(self):
        class_name = self.class_comboBox.currentText()
        try:
            if os.path.exists(f"app/resource/history/{class_name}.json"):
                os.remove(f"app/resource/history/{class_name}.json")
                logger.info("历史记录已清除！")
                InfoBar.success(
                    title='清除成功',
                    content="历史记录已清除！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
            else:
                logger.info("没有找到历史记录文件。")
                InfoBar.info(
                    title='提示',
                    content="没有找到历史记录文件。",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
        except Exception as e:
            logger.error(f"清除历史记录失败: {str(e)}")
            InfoBar.error(
                title='错误',
                content=f"清除历史记录失败: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )   

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    history_settings = settings.get("history", {})
                        
                    history_enabled = history_settings.get("history_enabled", self.default_settings["history_enabled"])
                    
                    self.history_switch.setChecked(history_enabled)
                    logger.info(f"加载历史记录设置完成")
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.history_switch.setChecked(self.default_settings["history_enabled"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.history_switch.setChecked(self.default_settings["history_enabled"])
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

        if "history" not in existing_settings:
            existing_settings["history"] = {}
            
        history_settings = existing_settings["history"]
        history_settings["history_enabled"] = self.history_switch.isChecked()
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)