import copy
import math


def draw_line(p_list, algorithm):
	"""绘制线段

	:param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
	:param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
	"""
	x0, y0 = p_list[0]
	x1, y1 = p_list[1]
	result = []
	if algorithm == 'Naive':
		if x0 == x1:
			for y in range(y0, y1 + 1):
				result.append((x0, y))
		else:
			if x0 > x1:
				x0, y0, x1, y1 = x1, y1, x0, y0
			k = (y1 - y0) / (x1 - x0)
			for x in range(x0, x1 + 1):
				result.append((x, int(y0 + k * (x - x0))))
	elif algorithm == 'DDA':
		result.append((x0, y0))
		length = max(abs(x1 - x0), abs(y1 - y0))
		if length > 0:
			dx = (x1 - x0) / length
			dy = (y1 - y0) / length
			x, y = x0, y0
			for i in range(length):
				x += dx
				y += dy
				result.append((int(x), int(y)))

	elif algorithm == 'Bresenham':
		x, y = x0, y0
		dx = abs(x1 - x0)
		dy = abs(y1 - y0)
		sx = 1 if (x1 > x0) else -1
		sy = 1 if (y1 > y0) else -1
		swap = (dy > dx)
		if swap:
			dx, dy = dy, dx
		p = 2 * dy - dx
		for i in range(dx):
			result.append((int(x), int(y)))
			if p > 0:
				if swap:
					x += sx
				else:
					y += sy
				p -= 2 * dx
			if swap:
				y += sy
			else:
				x += sx
			p += 2 * dy
		result.append((int(x1), int(y1)))
	return result


def draw_polygon(p_list, algorithm):
	"""绘制多边形

	:param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
	:param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
	"""
	result = []
	for i in range(len(p_list)):
		line = draw_line([p_list[i - 1], p_list[i]], algorithm)
		result += line
	return result


def draw_ellipse(p_list):
	"""绘制椭圆（采用中点圆生成算法）

	:param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
	"""
	result = []
	x0, y0 = p_list[0]
	x1, y1 = p_list[1]
	mirror = False
	cx = (x0 + x1) // 2
	cy = (y0 + y1) // 2
	rx = abs((x1 - x0) // 2)
	ry = abs((y1 - y0) // 2)

	if ry > rx:
		rx, ry = ry, rx
		mirror = True

	temp_x = 0
	temp_y = ry

	def new_point(px, py):
		result.append((cx + px, cy - py))
		result.append((cx - px, cy - py))
		result.append((cx + px, cy + py))
		result.append((cx - px, cy + py))

	sq_x = rx * rx
	sq_y = ry * ry
	p = sq_y - sq_x * ry + sq_x / 4
	while sq_y * temp_x < sq_x * temp_y:
		temp_x = temp_x + 1
		if p < 0:
			p += 2 * sq_y * temp_x + sq_y
		else:
			temp_y -= 1
			p += 2 * sq_y * temp_x - 2 * sq_x * temp_y + sq_y
		if mirror:
			new_point(temp_y, temp_x)
		else:
			new_point(temp_x, temp_y)

	p = sq_y * (temp_x + 0.5) ** 2 + sq_x * (temp_y - 1) ** 2 - sq_x * sq_y
	while temp_y >= 0:
		temp_y -= 1
		if p < 0:
			temp_x += 1
			p += 2 * sq_y * temp_x - 2 * sq_x * temp_y + sq_x
		else:
			p += sq_x - 2 * sq_x * temp_y
		if mirror:
			new_point(temp_y, temp_x)
		else:
			new_point(temp_x, temp_y)

	return result


def draw_curve(p_list, algorithm, tmp=False):
	"""绘制曲线

	:param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
	:param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
	:param tmp: 当前是否是临时绘制，可减少采样，加快速度
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
	"""
	result = []
	if algorithm == 'Bezier':
		new_list = []
		bnd = 0
		for i in range(len(p_list) - 1):
			bnd += 10 * max(abs(p_list[i][0] - p_list[i + 1][0]), abs(p_list[i][1] - p_list[i + 1][1]))
		if tmp:
			bnd //= 20

		def Bezier(i):
			c = i / bnd
			n = len(p_list)
			while n > 1:
				for i in range(0, n - 1):
					x0, y0 = new_list[i]
					x1, y1 = new_list[i + 1]
					px = x0 * (1 - c) + x1 * c
					py = y0 * (1 - c) + y1 * c
					new_list[i] = px, py
				n -= 1
			return new_list[0]

		for i in range(0, bnd):
			new_list = p_list.copy()
			px, py = Bezier(i)
			result.append((int(px + 0.5), int(py + 0.5)))
	elif algorithm == 'B-spline':
		t = 3
		dt = 1 / (60 * len(p_list))
		if tmp:
			dt *= 20

		def B_spline(i, j, k):
			if j == 0:
				if i <= k < i + 1:
					return 1
				else:
					return 0
			return B_spline(i, j - 1, k) * (k - i) / j + B_spline(i + 1, j - 1, k) * (i + j + 1 - k) / j

		while t < len(p_list):
			t += dt
			px, py = 0, 0
			for i, p in enumerate(p_list):
				co = B_spline(i, 3, t)
				px += p[0] * co
				py += p[1] * co
			result.append((int(px), int(py)))

	return result


def translate(p_list, dx, dy):
	"""平移变换

	:param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
	:param dx: (int) 水平方向平移量
	:param dy: (int) 垂直方向平移量
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
	"""
	return list(map(lambda p: [p[0] + dx, p[1] + dy], p_list))


def rotate(p_list, x, y, r):
	"""旋转变换（除椭圆外）

	:param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
	:param x: (int) 旋转中心x坐标
	:param y: (int) 旋转中心y坐标
	:param r: (int) 顺时针旋转角度（°）
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
	"""
	rad = r * math.pi / 180
	return list(map(lambda p: [int(x + (p[0] - x) * math.cos(rad) - (p[1] - y) * math.sin(rad)),
	                           int(y + (p[0] - x) * math.sin(rad) + (p[1] - y) * math.cos(rad))], p_list))


def scale(p_list, x, y, s):
	"""缩放变换

	:param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
	:param x: (int) 缩放中心x坐标
	:param y: (int) 缩放中心y坐标
	:param s: (float) 缩放倍数
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
	"""
	return list(map(lambda p: [int(p[0] * s + x * (1 - s)), int(p[1] * s + y * (1 - s))], p_list))


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
	"""线段裁剪

	:param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
	:param x_min: 裁剪窗口左上角x坐标
	:param y_min: 裁剪窗口左上角y坐标
	:param x_max: 裁剪窗口右下角x坐标
	:param y_max: 裁剪窗口右下角y坐标
	:param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
	"""
	x0, y0 = p_list[0]
	x1, y1 = p_list[1]
	if algorithm == 'Cohen-Sutherland':
		def encode(px, py):
			c = 0
			if px < x_min:
				c |= 1
			elif px > x_max:
				c |= 2
			if py < y_min:
				c |= 4
			elif py > y_max:
				c |= 8
			return c

		new_x, new_y = 0, 0
		while True:
			code1 = encode(x0, y0)
			code2 = encode(x1, y1)
			if code1 & code2:
				return []
			if code1 | code2 == 0:
				return [[int(x0 + 0.5), int(y0 + 0.5)], [int(x1 + 0.5), int(y1 + 0.5)]]
			if code1 == 0:
				x0, x1, y0, y1, code1, code2 = x1, x0, y1, y0, code2, code1
			if code1 & 1 or code1 & 2:
				new_y = y0
				if code1 & 1:
					new_x = x_min
				else:
					new_x = x_max
				if x0 != x1:
					new_y += (y0 - y1) / (x0 - x1) * (new_x - x0)
			elif code1 & 4 or code1 & 8:
				if code1 & 4:
					new_y = y_min
				else:
					new_y = y_max
				new_x = x0 + (x0 - x1) / (y0 - y1) * (new_y - y0)
			x0, y0 = new_x, new_y

	elif algorithm == 'Liang-Barsky':
		pl1 = [p_list[0][0] - p_list[1][0], p_list[1][0] - p_list[0][0], p_list[0][1] - p_list[1][1],
		       p_list[1][1] - p_list[0][1]]
		pl2 = [p_list[0][0] - x_min, x_max - p_list[0][0], p_list[0][1] - y_min, y_max - p_list[0][1]]
		co_max, co_min = 0, 1

		def trav(m, n):
			nonlocal co_max, co_min
			for i in range(m, n):
				if pl1[i] < 0:
					co_max = max(co_max, pl2[i] / pl1[i])
				elif pl1[i] > 0:
					co_min = min(co_min, pl2[i] / pl1[i])

		flag = False
		if pl1[0] == 0:
			flag = pl2[0] < 0 or pl2[1] < 0
			if not flag:
				trav(2, 4)
		elif pl1[2] == 0:
			flag = pl2[2] < 0 or pl2[3] < 0
			if not flag:
				trav(0, 2)
		else:
			trav(0, 4)
		if flag or co_max > co_min:
			return []
		return [[int(p_list[0][0] + co_max * pl1[1]), int(p_list[0][1] + co_max * pl1[3])],
		        [int(p_list[0][0] + co_min * pl1[1]), int(p_list[0][1] + co_min * pl1[3])]]

	elif algorithm == 'Sutherland-Hodgeman':
		lines = [[[x_min, y_max], [x_min, y_min]], [[x_min, y_min], [x_max, y_min]],
		         [[x_max, y_min], [x_max, y_max]], [[x_max, y_max], [x_min, y_max]]]
		e1, e2 = [], []
		result = copy.deepcopy(p_list)

		def is_inside(obj):
			return (e1[1] - obj[1]) * (e1[0] - e2[0]) > (e1[0] - obj[0]) * (e1[1] - e2[1])

		def intersect(p1, p2):
			s = p1[0] * p2[1] - p1[1] * p2[0]
			t = e1[0] * e2[1] - e1[1] * e2[0]
			k = (p1[0] - p2[0]) * (e1[1] - e2[1]) - (p1[1] - p2[1]) * (e1[0] - e2[0])
			ix = int((s * (e1[0] - e2[0]) - t * (p1[0] - p2[0])) / k)
			iy = int((s * (e1[1] - e2[1]) - t * (p1[1] - p2[1])) / k)
			return [ix, iy]

		for l in lines:
			r = []
			e1, e2 = l[0], l[1]
			for i in range(len(result)):
				begin, end = result[i - 1], result[i]
				f1 = is_inside(begin)
				f2 = is_inside(end)
				if f1 ^ f2:
					r.append(intersect(begin, end))
				if f2:
					r.append(end)
			result = copy.deepcopy(r)
		return result
