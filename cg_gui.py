import math
import sys
from typing import Optional

from PyQt5.QtCore import QRectF, pyqtSignal, QLine, Qt
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QIcon
from PyQt5.QtWidgets import (
	QApplication,
	QMainWindow,
	qApp,
	QGraphicsScene,
	QGraphicsView,
	QGraphicsItem,
	QHBoxLayout,
	QWidget,
	QStyleOptionGraphicsItem, QColorDialog, QFileDialog, QAction)

import cg_algorithms as alg


class MyCanvas(QGraphicsView):
	"""
	画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
	"""

	statusChanged = pyqtSignal(str, str)  # 状态改变的信号

	def __init__(self, *args):
		super().__init__(*args)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.main_window: MainWindow = None
		# self.list_widget: QListWidget = None
		self.item_dict = {}
		self.selected_id = ''

		self.status = ''
		self.temp_algorithm = ''
		self.temp_id = ''
		self.temp_item = None
		self.temp_cnt = 0  # 当前点的计数
		self.temp_points = []
		self.temp_list = []
		self.color: QColor = QColor(0, 0, 0)

	def renew_status(self, new_status):
		self.status = new_status
		self.statusChanged.emit(self.status, self.temp_algorithm)

	def start_draw(self, new_status, algorithm):
		self.renew_status(new_status)
		self.temp_algorithm = algorithm

	def start_edit(self, new_status):
		if self.selected_id == '':
			self.renew_status('')
			return
		# 椭圆不能旋转
		if new_status == 'rotate' and self.item_dict[self.selected_id].item_type == 'ellipse':
			self.clear_selection()
			self.renew_status('')
			return
		self.renew_status(new_status)
		self.temp_id = self.selected_id
		self.item_dict[self.temp_id].auxiliary = True
		self.temp_list = self.item_dict[self.temp_id].p_list
		self.item_dict[self.temp_id].prepareGeometryChange()

	def start_clip(self, algorithm):
		if self.selected_id == '':
			self.renew_status('')
			return
		cur_item = self.item_dict[self.selected_id]
		if (cur_item.item_type == 'line' and algorithm != 'Sutherland-Hodgeman') \
				or (cur_item.item_type == 'polygon' and algorithm == 'Sutherland-Hodgeman'):
			self.renew_status('clip')
			self.temp_id = self.selected_id
			self.temp_algorithm = algorithm
		else:
			self.renew_status('')

	def finish_draw(self):
		self.item_dict[self.temp_id] = self.temp_item
		self.temp_cnt = 0
		self.temp_id = ''
		self.temp_item.modified = True
		self.temp_item.auxiliary = False
		# self.list_widget.addItem(self.temp_id)
		self.updateScene([self.sceneRect()])

	def finish_edit(self):
		self.renew_status('')
		self.temp_item = self.item_dict[self.temp_id]
		self.temp_id = ''
		self.temp_item.modified = True
		self.temp_item.auxiliary = False
		self.temp_points = []
		self.updateScene([self.sceneRect()])

	def finish_clip(self):
		self.renew_status('')
		self.temp_id = ''
		self.temp_points = []
		minPoint = min(self.temp_item.p_list)
		maxPoint = max(self.temp_item.p_list)
		self.temp_list = self.item_dict[self.selected_id].p_list.copy()
		new_p_list = alg.clip(self.item_dict[self.selected_id].p_list, minPoint[0], minPoint[1], maxPoint[0],
		                      maxPoint[1], self.temp_algorithm)
		if len(new_p_list) > 0:
			self.item_dict[self.selected_id].p_list = new_p_list
			self.item_dict[self.selected_id].modified = True
		else:
			self.main_window.delete_action()
		self.scene().removeItem(self.temp_item)
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
		if selected:
			self.item_dict[selected].selected = True
			self.item_dict[selected].update()
		self.status = ''
		self.updateScene([self.sceneRect()])

	def mousePressEvent(self, event: QMouseEvent) -> None:
		pos = self.mapToScene(event.localPos().toPoint())
		x = int(pos.x())
		y = int(pos.y())
		pos = pos.toPoint()
		if self.status == '':
			click_item = self.main_window.canvas_widget.itemAt(pos)
			if click_item and not click_item.auxiliary:
				self.selection_changed(click_item.id)
			else:
				self.clear_selection()
			self.update()
		elif self.status == 'scale':
			self.temp_points = [[x - 100, y - 100], [x, y]]
		elif self.status == 'translate' or self.status == 'rotate':
			self.temp_points = [[x, y], [x, y]]
		elif self.status == 'clip':
			self.temp_item = MyItem(self.temp_id, 'polygon', [[x, y], [x, y], [x, y], [x, y]], 'DDA', QColor(255, 0, 0))
			self.scene().addItem(self.temp_item)
		else:  # draw
			# new an item
			if self.temp_cnt == 0:
				self.temp_id = self.main_window.get_id()
				self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.color)
				self.scene().addItem(self.temp_item)
			# add point
			else:
				if self.temp_cnt >= len(self.temp_item.p_list):
					self.temp_item.p_list.append([x, y])
				else:
					self.temp_item.p_list[self.temp_cnt] = [x, y]
			self.temp_cnt += 1
			self.temp_item.modified = True
		self.updateScene([self.sceneRect()])
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event: QMouseEvent) -> None:
		pos = self.mapToScene(event.localPos().toPoint())
		x = int(pos.x())
		y = int(pos.y())
		if self.status == '':
			return
		if self.status == 'translate' and len(self.temp_points):
			self.temp_points[1] = [x, y]
			dx = self.temp_points[1][0] - self.temp_points[0][0]
			dy = self.temp_points[1][1] - self.temp_points[0][1]
			self.item_dict[self.selected_id].p_list = alg.translate(self.temp_list, dx, dy)
			self.item_dict[self.selected_id].modified = True
		elif self.status == 'rotate' and len(self.temp_points):
			self.temp_points[1] = [x, y]
			dx = self.temp_points[1][0] - self.temp_points[0][0]
			dy = self.temp_points[1][1] - self.temp_points[0][1]
			if dx:
				self.item_dict[self.selected_id].p_list = alg.rotate(self.temp_list, self.temp_points[0][0],
				                                                     self.temp_points[0][1],
				                                                     math.degrees(math.atan2(dy, dx)))
				self.item_dict[self.selected_id].modified = True
		elif self.status == 'scale' and len(self.temp_points):
			self.temp_points[1] = [x, y]
			dx = self.temp_points[1][0] - self.temp_points[0][0]
			self.item_dict[self.selected_id].p_list = alg.scale(self.temp_list, self.temp_points[0][0] + 100,
			                                                    self.temp_points[0][1] + 100, dx / 100)
			self.item_dict[self.selected_id].modified = True
		elif self.status == 'clip' and len(self.temp_item.p_list) == 4:
			self.temp_item.p_list[2] = [x, y]
			self.temp_item.p_list = [self.temp_item.p_list[0], [self.temp_item.p_list[0][0], y], [x, y],
			                         [x, self.temp_item.p_list[0][1]]]
			self.temp_item.modified = True
		else:  # draw
			if self.temp_cnt > 0:
				self.temp_item.modified = True
				if self.temp_cnt >= len(self.temp_item.p_list):
					self.temp_item.p_list.append([x, y])
				else:
					self.temp_item.p_list[self.temp_cnt] = [x, y]
		self.updateScene([self.sceneRect()])
		super().mouseMoveEvent(event)

	def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
		if not self.temp_item:
			return
		if (self.status == 'polygon' and self.temp_cnt >= 2) or (self.status == 'curve' and (
				(self.temp_item.algorithm == 'Bezier' and self.temp_cnt >= 2) or
				(self.temp_item.algorithm == 'B-spline' and self.temp_cnt >= 4))):
			self.finish_draw()
		super().mouseDoubleClickEvent(event)

	def mouseReleaseEvent(self, event: QMouseEvent) -> None:
		if self.status == 'translate' or self.status == 'rotate' or self.status == 'scale':
			self.finish_edit()
		elif self.status == 'clip':
			self.finish_clip()
		elif self.status == 'line' or self.status == 'ellipse':
			self.finish_draw()
		super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
	"""
	自定义图元类，继承自QGraphicsItem
	"""

	def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '',
	             color: QColor = QColor(0, 0, 0),
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
		self.modified = True  # 是否已被修改
		self.auxiliary = True  # 是否需要辅助点

	def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
		if self.modified:
			self.modified = False
			if self.item_type == 'line':
				self.item_pixels = alg.draw_line(self.p_list, self.algorithm)
			elif self.item_type == 'polygon':
				self.item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
			elif self.item_type == 'ellipse':
				self.item_pixels = alg.draw_ellipse(self.p_list)
			elif self.item_type == 'curve':
				if not (self.algorithm == 'B-spline' and len(self.p_list) < 4):
					self.item_pixels = alg.draw_curve(self.p_list, self.algorithm, self.auxiliary)
		for p in self.item_pixels:
			painter.setPen(self.color)
			painter.drawPoint(p[0], p[1])
		if self.selected:
			painter.setPen(QColor(10, 100, 200))
			painter.drawRect(self.boundingRect())
		if self.auxiliary:
			self.auxiliary_point(painter)
			if self.item_type == 'curve':
				self.curve_auxiliary(painter)

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

	def auxiliary_point(self, painter: QPainter):
		painter.setPen(QColor(250, 60, 200))
		for p in self.p_list:
			x, y = p
			painter.drawRect(QRectF(x - 1, y - 1, 2, 2))
			painter.drawRect(QRectF(x - 2, y - 2, 4, 4))

	def curve_auxiliary(self, painter: QPainter):
		painter.setPen(QColor(125, 250, 250))
		for i in range(len(self.p_list) - 1):
			painter.drawLine(QLine(self.p_list[i][0], self.p_list[i][1], self.p_list[i + 1][0], self.p_list[i + 1][1]))


class MainWindow(QMainWindow):
	"""
	主窗口类
	"""

	def __init__(self):
		super().__init__()
		self.item_cnt = 0
		self.temp_item = None  # 复制粘贴

		# 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
		# self.list_widget = QListWidget(self)
		# self.list_widget.setMinimumWidth(200)

		# 使用QGraphicsView作为画布
		self.scene = QGraphicsScene(self)
		self.scene.setSceneRect(0, 0, 750, 750)
		self.canvas_widget = MyCanvas(self.scene, self)
		self.canvas_widget.setFixedSize(750, 750)
		self.canvas_widget.main_window = self
		# self.canvas_widget.list_widget = self.list_widget

		# 设置菜单栏、工具栏
		menubar = self.menuBar()
		toolbar = self.addToolBar('快捷工具栏')
		t_cursor_act = QAction(QIcon('./icons/pointer.png'), '指针点选', self)
		t_save_act = QAction(QIcon('./icons/save.png'), '保存画布', self)
		t_reset_canvas_act = QAction(QIcon('./icons/reset.png'), '重置画布', self)
		t_set_pen_act = QAction(QIcon('./icons/color.png'), '画笔颜色', self)
		t_exit_act = QAction(QIcon('./icons/exit.png'), '退出', self)
		t_translate_act = QAction(QIcon('./icons/translate.png'), '平移', self)
		t_rotate_act = QAction(QIcon('./icons/rotate.png'), '旋转', self)
		t_scale_act = QAction(QIcon('./icons/scale.png'), '缩放', self)
		t_copy_act = QAction(QIcon('./icons/copy.png'), '复制', self)
		t_paste_act = QAction(QIcon('./icons/paste.png'), '粘贴', self)
		t_delete_act = QAction(QIcon('./icons/delete.png'), '删除', self)
		toolbar.addAction(t_cursor_act)
		toolbar.addAction(t_save_act)
		toolbar.addAction(t_exit_act)
		toolbar.addAction(t_reset_canvas_act)
		toolbar.addAction(t_set_pen_act)
		toolbar.addSeparator()
		toolbar.addSeparator()
		toolbar.addAction(t_translate_act)
		toolbar.addAction(t_rotate_act)
		toolbar.addAction(t_scale_act)
		toolbar.addAction(t_copy_act)
		toolbar.addAction(t_paste_act)
		toolbar.addAction(t_delete_act)

		file_menu = menubar.addMenu('画布')
		cursor_act = file_menu.addAction('指针点选')
		set_pen_act = file_menu.addAction('画笔颜色')
		save_act = file_menu.addAction('保存画布')
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
		copy_act = edit_menu.addAction('复制')
		paste_act = edit_menu.addAction('粘贴')
		delete_act = edit_menu.addAction('删除')
		clip_menu = edit_menu.addMenu('裁剪')
		clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
		clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
		clip_sutherland_hodgeman_act = clip_menu.addAction('Sutherland-Hodgeman')

		# 连接信号和槽函数
		exit_act.triggered.connect(qApp.quit)
		t_exit_act.triggered.connect(qApp.quit)
		cursor_act.triggered.connect(self.cursor_action)
		t_cursor_act.triggered.connect(self.cursor_action)
		set_pen_act.triggered.connect(self.set_pen_action)
		t_set_pen_act.triggered.connect(self.set_pen_action)
		save_act.triggered.connect(self.save_action)
		t_save_act.triggered.connect(self.save_action)
		reset_canvas_act.triggered.connect(self.reset_canvas_action)
		t_reset_canvas_act.triggered.connect(self.reset_canvas_action)
		# self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

		line_naive_act.triggered.connect(self.line_naive_action)
		line_dda_act.triggered.connect(self.line_dda_action)
		line_bresenham_act.triggered.connect(self.line_bresenham_action)
		polygon_dda_act.triggered.connect(self.polygon_dda_action)
		polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
		ellipse_act.triggered.connect(self.ellipse_action)
		curve_bezier_act.triggered.connect(self.curve_bezier_action)
		curve_b_spline_act.triggered.connect(self.curve_b_spline_action)

		translate_act.triggered.connect(self.translate_action)
		t_translate_act.triggered.connect(self.translate_action)
		rotate_act.triggered.connect(self.rotate_action)
		t_rotate_act.triggered.connect(self.rotate_action)
		scale_act.triggered.connect(self.scale_action)
		t_scale_act.triggered.connect(self.scale_action)
		copy_act.triggered.connect(self.copy_action)
		t_copy_act.triggered.connect(self.copy_action)
		paste_act.triggered.connect(self.paste_action)
		t_paste_act.triggered.connect(self.paste_action)
		delete_act.triggered.connect(self.delete_action)
		t_delete_act.triggered.connect(self.delete_action)

		clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
		clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
		clip_sutherland_hodgeman_act.triggered.connect(self.clip_sutherland_hodgeman_action)

		# 设置主窗口的布局
		self.hbox_layout = QHBoxLayout()
		self.hbox_layout.addWidget(self.canvas_widget)
		# self.hbox_layout.addWidget(self.list_widget, stretch=1)
		self.central_widget = QWidget()
		self.central_widget.setLayout(self.hbox_layout)
		self.setCentralWidget(self.central_widget)
		self.statusBar().showMessage('空闲')
		self.resize(750, 750)
		self.setWindowTitle('pyStroke')
		self.setWindowIcon(QIcon('./icons/painter.png'))

	def get_id(self):
		_id = str(self.item_cnt)
		self.item_cnt += 1
		return _id

	def cursor_action(self):
		if self.canvas_widget.temp_item and self.canvas_widget.temp_item.auxiliary:
			self.canvas_widget.scene().removeItem(self.canvas_widget.temp_item)
			self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])
		self.temp_item = None
		self.canvas_widget.renew_status('')
		self.canvas_widget.temp_algorithm = ''
		self.canvas_widget.temp_id = ''
		self.canvas_widget.temp_cnt = 0

	def set_pen_action(self):
		self.temp_item = None
		new_color = QColorDialog.getColor(self.canvas_widget.color, self, '选择绘图颜色')
		self.canvas_widget.color = new_color

	def save_action(self):
		self.temp_item = None
		filename = QFileDialog.getSaveFileName(self, "保存当前画布", "new_image", "Portable Network Graphics(*.png)")
		if filename[0] == '':
			return
		self.canvas_widget.clear_selection()
		self.canvas_widget.scene().update()
		cur_img = self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
		cur_img.save(filename[0])

	def reset_canvas_action(self):
		# self.list_widget.clear()
		self.canvas_widget.clear_selection()
		self.canvas_widget.item_dict.clear()
		self.item_cnt = 0
		self.temp_item = None
		self.scene.clear()
		self.scene = QGraphicsScene(self)
		self.scene.setSceneRect(0, 0, 750, 750)
		self.canvas_widget.setScene(self.scene)
		self.canvas_widget.setFixedSize(750, 750)
		self.canvas_widget.temp_cnt = 0
		self.canvas_widget.temp_item = None
		self.canvas_widget.scene().update()
		self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])

	def draw_action(self, status: str, algorithm: str):
		self.temp_item = None
		self.canvas_widget.start_draw(status, algorithm)
		# self.list_widget.clearSelection()
		self.canvas_widget.clear_selection()

	def line_naive_action(self):
		self.draw_action('line', 'Naive')

	def line_dda_action(self):
		self.draw_action('line', 'DDA')

	def line_bresenham_action(self):
		self.draw_action('line', 'Bresenham')

	def polygon_dda_action(self):
		self.draw_action('polygon', 'DDA')

	def polygon_bresenham_action(self):
		self.draw_action('polygon', 'Bresenham')

	def ellipse_action(self):
		self.draw_action('ellipse', '')

	def curve_bezier_action(self):
		self.draw_action('curve', 'Bezier')

	def curve_b_spline_action(self):
		self.draw_action('curve', 'B-spline')

	def edit_action(self, status: str):
		self.temp_item = None
		self.canvas_widget.start_edit(status)

	def translate_action(self):
		self.edit_action('translate')

	def rotate_action(self):
		self.edit_action('rotate')

	def scale_action(self):
		self.edit_action('scale')

	def clip_action(self, algorithm: str):
		self.temp_item = None
		self.canvas_widget.start_clip(algorithm)

	def clip_cohen_sutherland_action(self):
		self.clip_action('Cohen-Sutherland')

	def clip_liang_barsky_action(self):
		self.clip_action('Liang-Barsky')

	def clip_sutherland_hodgeman_action(self):
		self.clip_action('Sutherland-Hodgeman')

	def copy_action(self):
		if self.canvas_widget.selected_id != '':
			self.temp_item = self.canvas_widget.item_dict[self.canvas_widget.selected_id]
		else:
			self.temp_item = None

	# self.updateUI(new=self.canvas_widget.status)

	def paste_action(self):
		if not self.temp_item:
			return
		new_item = MyItem(self.get_id(), self.temp_item.item_type, self.temp_item.p_list.copy(),
		                  self.temp_item.algorithm, self.temp_item.color)
		new_item.p_list = alg.translate(new_item.p_list, 15, 15)
		new_item.auxiliary = False
		self.temp_item = new_item
		self.canvas_widget.scene().addItem(new_item)
		self.canvas_widget.item_dict[new_item.id] = new_item
		# self.canvas_widget.list_widget.addItem(new_item.id)
		self.canvas_widget.scene().update()
		self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])

	def delete_action(self):
		self.temp_item = None
		self.canvas_widget.renew_status('')
		if self.canvas_widget.selected_id != '':
			item = self.canvas_widget.item_dict.pop(self.canvas_widget.selected_id)
			self.canvas_widget.selected_id = ''
			self.canvas_widget.scene().removeItem(item)
			self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()
	sys.exit(app.exec_())
