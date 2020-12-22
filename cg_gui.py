import sys
from typing import Optional

from PyQt5.QtCore import QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtWidgets import (
	QApplication,
	QMainWindow,
	qApp,
	QGraphicsScene,
	QGraphicsView,
	QGraphicsItem,
	QListWidget,
	QHBoxLayout,
	QWidget,
	QStyleOptionGraphicsItem)

import cg_algorithms as alg


class MyCanvas(QGraphicsView):
	"""
	画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
	"""

	statusChanged = pyqtSignal(str, str)  # 状态改变的信号

	# selectChanged = pyqtSignal()  # 选中图元变化的信号

	def __init__(self, *args):
		super().__init__(*args)
		self.main_window: MainWindow = None
		self.list_widget: QListWidget = None
		self.item_dict = {}
		self.selected_id = ''

		self.status = ''
		self.temp_algorithm = ''
		self.temp_id = ''
		self.temp_item = None
		self.temp_cnt = 0  # 当前点的计数
		self.color: QColor = QColor(0, 0, 0)

	def renew_status(self, new_status):
		self.status = new_status
		self.statusChanged.emit(self.status, self.temp_algorithm)

	def start_draw(self, new_status, algorithm):
		self.renew_status(new_status)
		self.temp_id = self.main_window.get_id()
		self.temp_algorithm = algorithm

	# def start_draw_line(self, algorithm, item_id):
	#     self.status = 'line'
	#     self.temp_algorithm = algorithm
	#     self.temp_id = item_id
	#     self.temp_cnt=0

	def finish_draw(self):
		# self.temp_id = self.main_window.get_id
		self.item_dict[self.temp_id] = self.temp_item
		#TODO
		#self.list_widget.addItem(self.temp_item)  # add item instead of id
		self.temp_cnt = 0
		self.updateScene([self.sceneRect()])

	def clear_selection(self):
		if self.selected_id != '':
			self.item_dict[self.selected_id].selected = False
			self.selected_id = ''

	def selection_changed(self, selected):
		self.main_window.statusBar().showMessage('图元选择： %s' % selected)
		if self.selected_id != '':
			self.item_dict[self.selected_id].selected = False
			self.item_dict[self.selected_id].update()
		self.selected_id = selected
		self.item_dict[selected].selected = True
		self.item_dict[selected].update()
		self.status = ''
		self.updateScene([self.sceneRect()])

	def mousePressEvent(self, event: QMouseEvent) -> None:
		# pos_click = event.localPos().toPoint()
		pos = self.mapToScene(event.localPos().toPoint())
		x = int(pos.x())
		y = int(pos.y())
		pos = pos.toPoint()
		if self.status == '':
			if self.selected_id != '':
				self.item_dict[self.selected_id].selected = False
				self.item_dict[self.selected_id].update()
			self.temp_item = self.main_window.canvas_widget.itemAt(pos)
			if self.temp_item is not None:
				self.selected_id = self.temp_item.id
				self.item_dict[self.selected_id].selected = True
				self.item_dict[self.selected_id].update()
			else:
				self.main_window.list_widget.clearSelection()
			self.update()
		else:  # draw
			# new an item
			if self.temp_cnt == 0:
				self.temp_cnt = 1
				self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm)
				self.scene().addItem(self.temp_item)
			# add point
			else:
				if self.temp_cnt >= len(self.temp_item.p_list):
					self.temp_item.p_list.append([x, y])
				else:
					self.temp_item.p_list[self.temp_cnt] = [x, y]
				self.temp_cnt += 1
		# elif self.status == 'line':
		# 	self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm)
		# 	self.scene().addItem(self.temp_item)
		self.updateScene([self.sceneRect()])
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event: QMouseEvent) -> None:
		pos = self.mapToScene(event.localPos().toPoint())
		x = int(pos.x())
		y = int(pos.y())
		#TODO
		#self.main_window.status_label.setText('position: (%d, %d) ' % (x, self.scene().height() - y - 1))
		if self.status == ' ':
			return
		else:  # draw
			if self.temp_cnt > 0:
				if self.temp_cnt >= len(self.temp_item.p_list):
					self.temp_item.p_list.append([x, y])
				else:
					self.temp_item.p_list[self.temp_cnt] = [x, y]
		# if self.status == 'line':
		# 	self.temp_item.p_list[1] = [x, y]
		self.updateScene([self.sceneRect()])
		super().mouseMoveEvent(event)

	def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
		if self.status == 'polygon' and self.temp_item and self.temp_cnt >= 2:
			self.finish_draw()
		elif self.status == 'curve' and self.temp_item:
			if self.temp_item.algorithm == 'Bezier' and self.temp_cnt >= 2:
				self.finish_draw()
			elif self.temp_item.algorithm == 'B-spline' and self.temp_cnt >= 4:
				self.finish_draw()
		super().mouseDoubleClickEvent(event)

	def mouseReleaseEvent(self, event: QMouseEvent) -> None:
		if self.status == 'line' or self.status == 'ellipse':
			# self.item_dict[self.temp_id] = self.temp_item
			# self.list_widget.addItem(self.temp_id)
			self.finish_draw()
		super().mouseReleaseEvent(event)
		# TODO
		#self.main_window.en_disable(self.status, self.temp_algorithm)


class MyItem(QGraphicsItem):
	"""
	自定义图元类，继承自QGraphicsItem
	"""

	def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '',
	             color: QColor = QColor(100, 100, 100),
	             parent: QGraphicsItem = None):
		"""
		:param item_id: 图元ID
		:param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
		:param p_list: 图元参数
		:param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
		:param parent:
		"""
		super().__init__(parent)
		self.id = item_id  # 图元ID
		self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
		self.p_list = p_list  # 图元参数
		self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
		self.selected = False
		self.color = color
		self.item_pixels = []  # 图元像素

	def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
		if self.item_type == 'line':
			self.item_pixels = alg.draw_line(self.p_list, self.algorithm)
		elif self.item_type == 'polygon':
			self.item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
		elif self.item_type == 'ellipse':
			self.item_pixels = alg.draw_ellipse(self.p_list)
		elif self.item_type == 'curve':
			if self.algorithm == 'B-spline' and len(self.p_list) < 4:
				self.item_pixels = []
			else:
				self.item_pixels = alg.draw_curve(self.p_list, self.algorithm, False)
		for p in self.item_pixels:
			painter.setPen(self.color)
			painter.drawPoint(p[0], p[1])
		if self.selected:
			painter.setPen(QColor(255, 0, 0))
			painter.drawRect(self.boundingRect())

	def boundingRect(self) -> QRectF:
		if not self.p_list:
			return QRectF()
		if self.item_type == 'line' or self.item_type == 'ellipse':
			x0, y0 = self.p_list[0]
			x1, y1 = self.p_list[1]
			x = min(x0, x1)
			y = min(y0, y1)
			w = max(x0, x1) - x
			h = max(y0, y1) - y
		elif self.item_type == 'polygon' or self.item_type == 'curve':
			x = min(list(map(lambda p: p[0], self.p_list)))
			y = min(list(map(lambda p: p[1], self.p_list)))
			w = max(list(map(lambda p: p[0], self.p_list))) - x
			h = max(list(map(lambda p: p[1], self.p_list))) - y
		return QRectF(x - 1, y - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
	"""
	主窗口类
	"""

	def __init__(self):
		super().__init__()
		self.item_cnt = 0

		# 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
		self.list_widget = QListWidget(self)
		self.list_widget.setMinimumWidth(200)

		# 使用QGraphicsView作为画布
		self.scene = QGraphicsScene(self)
		self.scene.setSceneRect(0, 0, 600, 600)
		self.canvas_widget = MyCanvas(self.scene, self)
		self.canvas_widget.setFixedSize(600, 600)
		self.canvas_widget.main_window = self
		self.canvas_widget.list_widget = self.list_widget

		# 设置菜单栏
		menubar = self.menuBar()
		file_menu = menubar.addMenu('文件')
		set_pen_act = file_menu.addAction('设置画笔')
		reset_canvas_act = file_menu.addAction('重置画布')
		exit_act = file_menu.addAction('退出')
		draw_menu = menubar.addMenu('绘制')
		line_menu = draw_menu.addMenu('线段')
		line_naive_act = line_menu.addAction('Naive')
		line_dda_act = line_menu.addAction('DDA')
		line_bresenham_act = line_menu.addAction('Bresenham')
		polygon_menu = draw_menu.addMenu('多边形')
		polygon_dda_act = polygon_menu.addAction('DDA')
		polygon_bresenham_act = polygon_menu.addAction('Bresenham')
		ellipse_act = draw_menu.addAction('椭圆')
		curve_menu = draw_menu.addMenu('曲线')
		curve_bezier_act = curve_menu.addAction('Bezier')
		curve_b_spline_act = curve_menu.addAction('B-spline')
		edit_menu = menubar.addMenu('编辑')
		translate_act = edit_menu.addAction('平移')
		rotate_act = edit_menu.addAction('旋转')
		scale_act = edit_menu.addAction('缩放')
		clip_menu = edit_menu.addMenu('裁剪')
		clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
		clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

		# 连接信号和槽函数
		exit_act.triggered.connect(qApp.quit)
		self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
		self.canvas_widget.statusChanged.connect(self.en_disable)

		line_naive_act.triggered.connect(self.line_naive_action)
		line_dda_act.triggered.connect(self.line_dda_action)
		line_bresenham_act.triggered.connect(self.line_bresenham_action)
		polygon_dda_act.triggered.connect(self.polygon_dda_action)
		polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
		ellipse_act.triggered.connect(self.ellipse_action)
		curve_bezier_act.triggered.connect(self.curve_bezier_action)
		curve_b_spline_act.triggered.connect(self.curve_b_spline_action)

		# 设置主窗口的布局
		self.hbox_layout = QHBoxLayout()
		self.hbox_layout.addWidget(self.canvas_widget)
		self.hbox_layout.addWidget(self.list_widget, stretch=1)
		self.central_widget = QWidget()
		self.central_widget.setLayout(self.hbox_layout)
		self.setCentralWidget(self.central_widget)
		self.statusBar().showMessage('空闲')
		self.resize(600, 600)
		self.setWindowTitle('CG Demo')

	def get_id(self):
		_id = str(self.item_cnt)
		self.item_cnt += 1
		return _id

	def en_disable(self):
		"""
		更新一些按钮的可用性
		"""
		pass

	def line_naive_action(self):
		self.canvas_widget.start_draw('line', 'Naive')
		self.list_widget.clearSelection()
		self.canvas_widget.clear_selection()

	def line_dda_action(self):
		self.canvas_widget.start_draw('line', 'DDA')
		self.list_widget.clearSelection()
		self.canvas_widget.clear_selection()

	def line_bresenham_action(self):
		self.canvas_widget.start_draw('line', 'Bresenham')
		self.list_widget.clearSelection()
		self.canvas_widget.clear_selection()

	def polygon_dda_action(self):
		self.canvas_widget.start_draw('polygon', 'DDA')
		self.list_widget.clearSelection()
		self.canvas_widget.clear_selection()

	def polygon_bresenham_action(self):
		self.canvas_widget.start_draw('polygon', 'Bresenham')
		self.list_widget.clearSelection()
		self.canvas_widget.clear_selection()

	def ellipse_action(self):
		self.canvas_widget.start_draw('ellipse', '')
		self.list_widget.clearSelection()
		self.canvas_widget.clear_selection()

	# Description: curve actions
	def curve_bezier_action(self):
		self.canvas_widget.start_draw('curve', 'Bezier')
		self.list_widget.clearSelection()
		self.canvas_widget.clear_selection()

	def curve_b_spline_action(self):
		self.canvas_widget.start_draw('curve', 'B-spline')
		self.list_widget.clearSelection()
		self.canvas_widget.clear_selection()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()
	sys.exit(app.exec_())
