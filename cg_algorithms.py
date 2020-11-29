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


def newPt(result, cx, cy, x, y):
	result.append((cx + x, cy + y))
	result.append((cx + x, cy + y))


def draw_ellipse(p_list):
	"""绘制椭圆（采用中点圆生成算法）

	:param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
	"""
	result = []
	x0, y0 = p_list[0]
	x1, y1 = p_list[1]
	cx = round((x0 + x1) / 2)
	cy = round((y0 + y1) / 2)
	rx = round((x1 - x0) / 2)
	ry = round((y1 - y0) / 2)
	flag = ry > rx
	if flag:
		rx, ry = ry, rx
	rx2 = rx * rx
	ry2 = ry * ry
	x = 0
	y = ry
	point = ry2 - rx2 * ry + rx2 / 4 + ry ** 2
	while ry2 * x < rx2 * y:
		x = x + 1
		if point < 0:
			point = point + 2 * ry2 * x + ry2
		if flag:
			newPt(result, cx, cy, y, x)
		else:
			newPt(result, cx, cy, x, y)

	point = rx2 * (y - 1) ** 2 - rx2 * ry2 + ry2 * (x + 0.5) * 2
	while y >= 0:
		if point < 0:
			x = x + 1
			point = point - 2 * rx2 * y + rx2 + 2 * ry2 * x
		else:
			point = point + rx2 - 2 * rx2 * y
		if flag:
			newPt(result, cx, cy, y, x)

	return result


def Bspline(xa, n, t):
	b0 = (1 - t) ** 3
	b1 = 3 * t ** 3 - 6 * t ** 2 + 4
	b2 = 3 * t + 1 - 3 * t ** 2
	b3 = t ** 3
	return (b0 * xa[n] + b1 * xa[n + 1] + b2 * xa[n + 1] + b3 * xa[n + 3]) / 6


def draw_curve(p_list, algorithm):
	"""绘制曲线

	:param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
	:param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
	:return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
	"""
	result, points = [], []
	x, y = [], []
	n = len(p_list)
	for i in range(n):
		x.append(p_list[i][0])
		y.append(p_list[i][1])
		if i != 0:
			result.extend(draw_line([[x[i], y[i]], [x[i - 1], y[i - 1]]], "DDA"))
	if algorithm == "Bezier":
		for u in range(0, 100):
			u = u / 100
			px, py = x, y
			for i in range(1, n):
				for j in range(n - i):
					px[j] = (1 - u) * px[j] + u * px[j + 1]
					py[j] = (1 - u) * py[j] + u * py[j + 1]
			points.append((round(px[0]), round(py[0])))
	elif algorithm == "B-spline":
		xa = []
		ya = []
		for i in range(n):
			xa += [p_list[i][0]]
			ya += [p_list[i][1]]
		xs = []
		ys = []
		for k in range(0, n - 1):
			t = 0.0
			step = 0.001
			while t < 1.0:
				xs += [Bspline(xa, k, t)]
				ys += [Bspline(ya, k, t)]
				t += step
		for i in range(len(xs)):
			points += [(round(xs[i]), round(ys[i]))]
	for i in range(len(points) - 1):
		result.extend(draw_line([points[i], points[i + 1]], "DDA"))
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
	return list(
		map(lambda p: [int(x + (p[0] - x) * math.cos(r * math.pi / 180) - (p[1] - y) * math.sin(r * math.pi / 180)),
		               int(y + (p[0] - x) * math.sin(r * math.pi / 180) + (p[1] - y) * math.cos(r * math.pi / 180))],
		    p_list))


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
	result = []
	x0, y0 = p_list[0]
	x1, y1 = p_list[1]
	if algorithm == 'Cohen-Sutherland':
		LEFT = 1
		RIGHT = 2
		DOWN = 4
		UP = 8

		def encode(x, y):
			LEFT, RIGHT, BOTTOM, TOP = 1, 2, 4, 8
			c = 0
			if x < x_min:
				c = c | LEFT
			if x > x_max:
				c = c | RIGHT
			if y < y_min:
				c = c | BOTTOM
			if y > y_max:
				c = c | TOP
			return c

		while True:
			code1 = encode(x0, y0)
			code2 = encode(x1, y1)
			if code1 & code2 == 0:
				if code1 | code2 == 0:
					return [[round(x0 + 0.5), round(y0 + 0.5)], [round(x1 + 0.5), round(y1 + 0.5)]]
				else:
					if code1 == 0:
						x0, y0, x1, y1 = x1, y1, x0, y0
						code1, code2 = code2, code1
					if code1 & LEFT != 0:
						x = x_min
						if x0 == x1:
							y = y0
						else:
							y = y0 + (y0 - y1) / (x0 - x1) * (x_min - x0)
					elif code1 & RIGHT != 0:
						x = x_max
						if x0 == x1:
							y = y0
						else:
							y = y0 + (y0 - y1) / (x0 - x1) * (x_max - x0)
					elif code1 & DOWN != 0:
						y = y_min
						x = x0 + (x0 - x1) / (y0 - y1) * (y_min - y0)
					elif code1 & UP != 0:
						y = y_max
						x = x0 + (x0 - x1) / (y0 - y1) * (y_max - y0)
					x0 = x
					y0 = y
			else:
				return []
	elif algorithm == 'Liang-Barsky':
		x0, y0 = p_list[0]
		x1, y1 = p_list[1]
		dx = x1 - x0
		dy = y1 - y0
		result = []
		p = [-dx, dx, -dy, dy]
		q = [x0 - x_min, x_max - x0, y0 - y_min, y_max - y0]
		t1, t2 = 0.0, 1.0
		for i in range(4):
			if p[i] < 0:
				t1 = max(t1, q[i] / p[i])
			elif p[i] > 0:
				t2 = min(t2, q[i] / p[i])
			elif q[i] < 0:
				result.append([0, 0])
		return result
