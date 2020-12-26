# pyStroke：User Guide

## 开发环境

| 环境/程序 |版本|
| ---- | ---- |
| Windows 10 | 2004 |
|Pycharm| 2020.2 |
|Python| 3.8.3|
|Anaconda| 4.9.2|
|PyQt| 5.9.2|

## 操作方式

### 整体概览

如下所示，`pyStroke`分为菜单栏、工具栏与图元编辑区三个部分。

在图元绘制过程中，会有额外的点、线增强视觉效果，帮助用户绘制。

---

工具栏是额外增加的部分，依次包括以下这些选项：

- 指针点选、保存画布、退出、重置画布、画笔颜色、平移、旋转、缩放、复制、粘贴、删除

---

菜单栏依次包括以下这些选项：

- 画布
  - 指针点选
  - 画笔颜色
  - 保存画布
  - 重置画布
  - 退出
- 绘制
  - 线段
    - Naive
    - DDA
    - Bresenham
  - 多边形
    - DDA
    - Bresenham
  - 椭圆
  - 曲线
    - Bezier
    - B-spline
- 编辑
  - 平移
  - 旋转
  - 缩放
  - 复制
  - 粘贴
  - 删除
  - 裁剪
    - Cohen-Sutherland
    - Liang-Barsky
    - Sutherland-Hodgeman

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226173956821.png" alt="image-20201226173956821" style="zoom: 67%;" />

### 画布-指针点选或对应按钮

![image-20201226175110981](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226175110981.png)

点击该选项，则可开始选择图元，其实对应于画布`status == ''`。

- 若选中部分无图元，且当前有被选的图元，则**该选择清除**
- 若选中部分有图元，则可选中该图元，此时该图元会**被矩形框住**
- 进一步的编辑操作必须以**先选中某图元为前提**，否则无效
- 在一些需要**双击才能结束**的绘制操作中（如多边形与曲线），**若中途切换为指针，则正在绘制的临时图元会被清除**。

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225011714057.png" alt="image-20201225011714057" style="zoom: 50%;" />

### 画布-画笔颜色或对应按钮

![image-20201226175209188](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226175209188.png)

点击该选项，即可开始选择画笔颜色。

- 之后所绘制的所有图元将以最新选择的颜色为准
- 有一种例外：**复制粘贴所得的新图元，颜色与旧图元一致**

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225011955322.png" alt="image-20201225011955322" style="zoom: 67%;" />

### 画布-保存画布或对应按钮

![image-20201226175229447](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226175229447.png)

点击该选项，即可保存当前所绘制画面，支持自定义路径与文件名。

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225012407782.png" alt="image-20201225012407782" style="zoom: 50%;" />

### 画布-重置画布或对应按钮

![image-20201226175258813](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226175258813.png)

点击该选项，即可重置当前画布。需注意，该操作执行后已有图元将丢失，画面被清空。

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225012614570.png" alt="image-20201225012614570" style="zoom: 33%;" />

### 画布-退出或对应按钮

![image-20201226175328762](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226175328762.png)

点击该选项，即可退出程序，建议退出前先保存画布。

### 绘制-线段

点击该选项和对应算法，即可开始绘制线段。

- 绘制算法可选Naive、DDA、Bresenham
- 按下鼠标开始绘制，松开鼠标结束绘制
- 若不点选其他选项，则当前模式维持在线段绘制中（算法同理），可持续绘制

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225013028245.png" alt="image-20201225013028245" style="zoom: 50%;" />

### 绘制-多边形

点击该选项和对应算法，即可开始绘制多边形。

- 绘制算法可选DDA、Bresenham
- 若不点选其他选项，则当前模式维持在多边形绘制中（算法同理），可持续绘制
- 基于多边形绘制的特性，每次点击新增一个顶点，并**以双击为结束标志**，便于用户操作
- 未完成前切换到`指针点选`模式，将导致**临时图元丢失**

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225013410315.png" alt="image-20201225013410315" style="zoom: 50%;" />

### 绘制-椭圆

点击该选项，即可开始绘制椭圆

- 按下鼠标开始绘制，松开鼠标结束绘制
- 若不点选其他选项，则当前模式维持在椭圆绘制中，可持续绘制

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225014151063.png" alt="image-20201225014151063" style="zoom: 50%;" />

### 绘制-曲线

点击该选项和对应算法，即可开始绘制曲线

- 绘制算法可选Bezier、B-spline
- 若不点选其他选项，则当前模式维持在曲线绘制中（算法同理），可持续绘制
- 基于曲线绘制的特性，每次点击新增一个参考点，并**以双击为结束标志**，便于用户操作
- 未完成前切换到`指针点选`模式，将导致**临时图元丢失**
- 注意到`B-spline`算法要求为三次（四阶）均匀B样条曲线，**点击的次数需要满足最少要求**，否则双击也不能结束
- 绘制过程中会出现临时的**虚线来表示当前步骤下生成的曲线**，辅助判断

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225014703561.png" alt="image-20201225014703561" style="zoom: 50%;" />

### 编辑-平移或对应按钮

![image-20201226175518751](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226175518751.png)

点击该选项，即可开始平移图元

- 确保开始前已选择好某个图元，否则该操作无效
- 按住鼠标并拖动开始平移图元，平移至理想位置后，松开鼠标以结束
- 每次只能执行一次平移操作，不能连续执行

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225020421241.png" alt="image-20201225020421241" style="zoom: 50%;" />

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225020452365.png" alt="image-20201225020452365" style="zoom: 50%;" />

### 编辑-旋转或对应按钮

![image-20201226180024875](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226180024875.png)

点击该选项，即可开始旋转图元

- 确保开始前已选择好某个图元，否则该操作无效
- 以**按下鼠标的位置为圆心**，开始旋转图元；旋转至理想位置后，松开鼠标以结束
- 每次只能执行一次旋转操作，不能连续执行
- **旋转操作对于椭圆无效**

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225020155537.png" alt="image-20201225020155537" style="zoom:;" />

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225020222109.png" alt="image-20201225020222109"  />

### 编辑-缩放或对应按钮

![image-20201226180051945](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226180051945.png)

点击该选项，即可开始缩放图元

- 确保开始前已选择好某个图元，否则该操作无效
- 以按**下鼠标的位置为基准**，移动鼠标，开始缩放图元；缩放至理想位置后，松开鼠标以结束
- 每次只能执行一次缩放操作，不能连续执行

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225020641812.png" alt="image-20201225020641812" style="zoom: 80%;" />

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225020727120.png" alt="image-20201225020727120" style="zoom:80%;" />

### 编辑-复制、粘贴或对应按钮

![image-20201226180113691](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226180113691.png)

先选中某个图元，再点击复制选项，即可复制该图元

再点击粘贴选项，则刚刚被复制的图元将被粘贴到画布上

- 一次点击后，完成一次粘贴
- 在切换到其他模式之前，**可连续进行粘贴操作**
- 复制得到的图元**颜色与原图元一致**，即使画笔颜色已改变

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225021708279.png" alt="image-20201225021708279" style="zoom:80%;" />

### 编辑-删除或对应按钮

![image-20201226180206534](C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226180206534.png)

先选中某个图元，再点击删除选项，即可删除该图元

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225021740142.png" alt="image-20201225021740142" style="zoom: 67%;" />

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225021803671.png" alt="image-20201225021803671" style="zoom: 67%;" />

### 编辑-裁剪

点击该选项和对应算法，即可开始裁剪线段/多边形

- 线段裁剪算法可选`Cohen-Sutherland`、`Liang-Barsky`
- 多边形裁剪算法可选`Sutherland-Hodgeman`
- 应先按上述对应关系选择图元，**否则操作无效**
- 按下鼠标开始裁剪，此时会出现**辅助的矩形框显示当前裁剪得到的范围**，松开鼠标完成裁剪

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225022720121.png" alt="image-20201225022720121" style="zoom:67%;" />

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201225022845720.png" alt="image-20201225022845720" style="zoom:67%;" />


