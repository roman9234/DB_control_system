from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget,
                             QTabWidget, QAbstractScrollArea,
                             QVBoxLayout, QHBoxLayout,
                             QTableWidget, QGroupBox,
                         QTableWidgetItem, QPushButton, QMessageBox, QDialog, QLabel, QDateEdit)
import psycopg2
import sys
from config import host_c,user_c,password_c,db_name_c,port_c,token


#просмотр изменение добавление удаление


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self._connect_to_db()

        self.start_date = None
        self.end_date = None

        self.setWindowTitle("Shedule")

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self._create_shedule_tab()
        self._create_teachers_tab()
        self._create_subjects_tab()



    def _connect_to_db(self):
        self.conn = psycopg2.connect(host=host_c,
        user=user_c,
        password=password_c,
        database=db_name_c,
        port=port_c)
        self.cursor = self.conn.cursor()



    def _create_shedule_tab(self):
        self.shedule_tab = QWidget()
        self.tabs.addTab(self.shedule_tab, "Shedule")

        self.time_gbox_sh = QGroupBox()

        self.svbox_sh = QVBoxLayout()
        self.shbox1_sh = QHBoxLayout()
        self.shbox2_sh = QHBoxLayout()
        self.date_filter_button = QPushButton("Date Filter")
        self.date_filter_button.clicked.connect(self._open_date_filter_dialog)

        self.svbox_sh.addWidget(self.date_filter_button)
        self.svbox_sh.addLayout(self.shbox1_sh)
        self.svbox_sh.addLayout(self.shbox2_sh)

        self.shbox1_sh.addWidget(self.time_gbox_sh)

        self._create_shedule_table()

        self.update_shedule_button = QPushButton("Update")
        self.shbox2_sh.addWidget(self.update_shedule_button)
        self.update_shedule_button.clicked.connect(self._update_time_table)

        self.shedule_tab.setLayout(self.svbox_sh)

    def _create_shedule_table(self):
        self.time_table = QTableWidget()
        self.time_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.time_table.setColumnCount(4)
        self.time_table.setHorizontalHeaderLabels(["Subject", "Date", "Time", ""])

        self._update_time_table()

        self.mvbox_sh = QVBoxLayout()
        self.mvbox_sh.addWidget(self.time_table)
        self.time_gbox_sh.setLayout(self.mvbox_sh)



    def _open_date_filter_dialog(self):
        dialog = DateFilterDialog(self)
        if dialog.exec_():
            # Retrieve selected filter dates from the dialog
            start_date = dialog.start_date_edit.dateTime().toPyDateTime().date()
            end_date = dialog.end_date_edit.dateTime().toPyDateTime().date()
            # Filter the schedule table
            self._update_time_table(start_date, end_date)



    def _update_time_table(self, s_d=None, e_d=None):
        if e_d and s_d:
            formatted_start_date = s_d.strftime('%Y-%m-%d')
            formatted_end_date = e_d.strftime('%Y-%m-%d')
            self.cursor.execute(f"SELECT * FROM timetable WHERE day BETWEEN '{formatted_start_date}' AND '{formatted_end_date}'")
        else:
            self.cursor.execute("SELECT * FROM timetable")
        records = list(self.cursor.fetchall())

        self.time_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")

            self.time_table.setItem(i, 0,
                                    QTableWidgetItem(str(r[0])))
            self.time_table.setItem(i, 1,
                                    QTableWidgetItem(str(r[2])))
            self.time_table.setItem(i, 2,
                                    QTableWidgetItem(str(r[4])))
            self.time_table.setCellWidget(i, 3, joinButton)

            joinButton.clicked.connect(lambda ch, num=i: self._change_day_from_table(num))

        self.time_table.resizeRowsToContents()
        self.time_table.resizeColumnsToContents()


    
    def _create_teachers_tab(self):
            self.teachers_tab = QWidget()
            self.tabs.addTab(self.teachers_tab, "Teachers")

            self.teachers_gbox = QGroupBox()

            self.svbox_tch = QVBoxLayout()
            self.shbox1_tch = QHBoxLayout()
            self.shbox2_tch = QHBoxLayout()

            self.svbox_tch.addLayout(self.shbox1_tch)
            self.svbox_tch.addLayout(self.shbox2_tch)

            self.shbox1_tch.addWidget(self.teachers_gbox)

            self._create_teachers_table()

            # self.update_shedule_button = QPushButton("Update")
            # self.shbox2.addWidget(self.update_shedule_button)
            # self.update_shedule_button.clicked.connect(self._update_shedule)

            self.teachers_tab.setLayout(self.svbox_tch)

    def _create_teachers_table(self):
        self.teachers_table = QTableWidget()
        self.teachers_table.setWordWrap(False)
        self.teachers_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.teachers_table.setColumnCount(2)
        self.teachers_table.setHorizontalHeaderLabels(["Teacher Name", "Subject"])

        self._update_teachers_table()

        self.mvbox_tch = QVBoxLayout()
        self.mvbox_tch.addWidget(self.teachers_table)
        self.teachers_gbox.setLayout(self.mvbox_tch)

    def _update_teachers_table(self):
        self.cursor.execute("SELECT teacher_full_name, subject_name FROM teachers")
        records = list(self.cursor.fetchall())
        self.teachers_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            self.teachers_table.setItem(i, 0,
                                    QTableWidgetItem(str(r[0])))
            self.teachers_table.setItem(i, 1,
                                    QTableWidgetItem(str(r[1])))
        # self.subjects_table.setItem(len(records) + 1,0,QTableWidgetItem(""))

        self.teachers_table.resizeRowsToContents()
        self.teachers_table.resizeColumnsToContents()



    
    def _create_subjects_tab(self):
            self.subjects_tab = QWidget()
            self.tabs.addTab(self.subjects_tab, "Subjects")

            self.subjects_gbox = QGroupBox()

            self.svbox_sbj = QVBoxLayout()
            self.shbox1_sbj = QHBoxLayout()
            self.shbox2_sbj = QHBoxLayout()

            self.svbox_sbj.addLayout(self.shbox1_sbj)
            self.svbox_sbj.addLayout(self.shbox2_sbj)

            self.shbox1_sbj.addWidget(self.subjects_gbox)

            self._create_subjects_table()

            # self.update_shedule_button = QPushButton("Update")
            # self.shbox2.addWidget(self.update_shedule_button)
            # self.update_shedule_button.clicked.connect(self._update_shedule)

            self.subjects_tab.setLayout(self.svbox_sbj)

    
    def _create_subjects_table(self):
            self.subjects_table = QTableWidget()
            self.subjects_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

            self.subjects_table.setColumnCount(1)
            self.subjects_table.setHorizontalHeaderLabels(["Subjects"])

            self._update_subjects_table()

            self.mvbox_sbj = QVBoxLayout()
            self.mvbox_sbj.addWidget(self.subjects_table)
            self.subjects_gbox.setLayout(self.mvbox_sbj)


    def _update_subjects_table(self):
        self.cursor.execute("SELECT * FROM subjects")
        records = list(self.cursor.fetchall())
        self.subjects_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
             self.subjects_table.setItem(i,0,QTableWidgetItem(str(r[0])))
        # self.subjects_table.setItem(len(records) + 1,0,QTableWidgetItem(""))

        self.subjects_table.resizeRowsToContents()
        self.subjects_table.resizeColumnsToContents()



    def _change_day_from_table(self, rowNum, day):
            row = list()
            for i in range(self.time_table.columnCount()):
                try:
                    row.append(self.time_table.item(rowNum, i).text())
                except:
                    row.append(None)

            try:
                self.cursor.execute("UPDATE SQL запрос на изменение одной строки в базе данных", (row[0],))
                self.conn.commit()
            except:
                QMessageBox.about(self, "Error", "Enter all fields")

        
    

class DateFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Date Filter")

        self.start_date_label = QLabel("Start Date:")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QtCore.QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)

        self.end_date_label = QLabel("End Date:")
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QtCore.QDate.currentDate().addDays(7))
        self.end_date_edit.setCalendarPopup(True)

        button_box = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.cancel_button = QPushButton("Cancel")
        button_box.addStretch()
        button_box.addWidget(self.apply_button)
        button_box.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        date_range_box = QHBoxLayout()
        date_range_box.addWidget(self.start_date_label)
        date_range_box.addWidget(self.start_date_edit)
        date_range_box.addWidget(self.end_date_label)
        date_range_box.addWidget(self.end_date_edit)

        main_layout.addLayout(date_range_box)
        main_layout.addLayout(button_box)
        self.setLayout(main_layout)

        self.apply_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)



app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
