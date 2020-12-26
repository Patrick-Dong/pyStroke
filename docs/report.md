# CG Project Final Report

## About

**Month	Dec.**

**author	董宸郅**

**mail	181830044@smail.nju.edu.cn**

**Dev. Environment	Windows 10 2004 	Pycharm 2020.2 	Python 3.8.3	Anaconda 4.9.2	PyQt 5.9.2**

---

## Progress

**9月**：完成cg_cli.py与cg_algorithms.py的部分算法；

**10月**：继续完善cg_algorithms.py的算法；

**11月**：完成cg_algorithms.py的全部算法以及cg_gui.py的大致框架；

**12月**：完成cg_gui.py的全部工作，美化界面，并寻找潜在bug，反复调试完善；

至此，本项目全部工作完成。

---

## Algorithms

### 直线生成

#### DDA算法

DDA算法是计算机图形学基本的绘制直线算法，主要的思想来源于$y=kx+b$， 已知两个端点$(x_0,y_0),(x_1，y_1)$就可以知道k和b具体的值；

实际操作中绘画直线是一个迭代的过程，相对于前一个点$(x_i,y_i)$，后一个点$(x_{i+1}，y_{i+1})$可以记作:

- $$x_{i+1}=x_i+x_{Step}$$

- $$y_{i+1}=y_i+y_{Step}$$

$x_{Step}$，$y_{Step}$是通过$dx=abs(x0-x1),dy=abs(y_0-y_1)$的比较确定的：

- 如果$dx>dy$，那么x轴方向上面两个点的距离更远，置$x_{Step}=1,y_{Step}=k$
- 反之，则y轴方向上面两个点的距离更远，置$x_{Step}=1/k, y_{Step}=1$

#### Bresenham算法

DDA算法的弊端在于浮点数运算的速度一般比较慢，Bresenham的好处则是仅仅使用了整数增量运算；

以下是Bresenham算法的分析:

假设起点是(x0，y0)，终点是(x1，y1)，那么斜率m为$\frac{y1-y0}{x1-x0}=\frac{dy}{dx}$；

在画图时实际坐标是整数的，就需要找到更加接近于真实点的那个整数点；如果固定$x_k$，那么这个整数点的选择就在$y_k$和$y_k+1$两者之间展开:

对于直线$y=mx+c (0<=|m|<=1)$，已知下一个$x=xk+1$，那么下一个$y=m(xk+1)+c$

$$d1=y-yk=m(xk+1)+c-yk$$

$$d2=yk+1-y=yk+1-m(xk+1)-c$$

又：

$$d1-d2=m(xk+1)+c-yk-(yk+1-m(xk+1)-c)=2m(xk+1)-2yk+2c-1$$

得决策变量：

$$p_k=2dyx_k-2dxy_k+c$$

$p_k=2dyx_k-2dxy_k+(2dy+2dxc-dx)=2dyx_k-2dxy_k+c$

因为$dx>0$，从而$p_k$和$(d1-d2)$同号，可以得到如下的结论:

- 如果$p_k>0$，那么$d1-d2>0$，$y_k+1$距离真实的y更接近，选择$(x_{k+1},y_k+1)$；
- 如果$p_k<0$，那么$d1-d2<0$，$y_k$距离真实的y更接近，选择$(x_{k+1},y_k)$；

根据$p_k$的公式，$p_{k+1}-p_k=2dy(x_{k+1}-x_k)-2dx(y_{k+1}-yk)$

且$x_{k+1}=x_k+1$，由此得知决策参数的增量公式；

- 若$p_k>0$，$y_{k+1}=y_k+1$，$p_{k+1}=p_k+2dy-2dx$
- 若$p_k< 0$，$y_{k+1}=y_k$，$p_{k+1}=p_k+2dy$

从而，Bresenham的算法流程处理如下:


1. 选择起始点$(x_0,y_0)$，终止点$(x_1，y_1)$，满足$x1>x0$，否则交换；计算得到$dx=x_1-x_0,dy=y_1-y_0; p_0=2dy-dx$

2. 从$k=0$开始，已知$(x_k，y_k), p_k$，计算下一个要画的点$(x_{k+1}，y_{k+1})$以及决策变量$p_{k+1}$:

3. 循环直到$x_k=x1$；

当斜率为其他情况的时候，主要是一些正负号的问题；其中当斜率为正无穷和0的时候需要像处理DDA算法一样进行特判。

### 多边形生成

绘制多边形，其实就是绘制线段，只需要通过给定的一系列点，多次调用`DDA`或`Bresenham`直线生成算法即可完成。

### 绘制椭圆

#### 中点圆生成算法

计算出椭圆中心$(x_c,y_c)$，长短轴径$r_x$和$r_y$。

**区域1：|切线斜率|$\leqslant 1$**

计算得中心在原点的椭圆上的第一个点$(0,r_y)$。
在区域1每个$x_k$处，计算相应的决策参数：
$$p1_{k}=r_y^2(x_k+1)^2+r_x^2(y_k-\frac{1}{2})^2-r_x^2r_y^2$$
并对决策参数进行检测：

- $p1_k<0$，下一个点为$(x_{k+1},y_k)$；
- $p1_k\geqslant 0$，下一个点为$(x_{k+1},y_k-1)$

循环直到$2r_y^2x\geqslant 2r_x^2xy$。

**区域2：|切线斜率|$>1$**

在区域2每个$y_k$处，计算相应的决策参数：
$$
\begin{equation*}
p2_{k}=r_y^2(x_k+\frac{1}{2})^2+r_x^2(y_k-1)^2-r_x^2r_y^2
\end{equation*}
$$
并对决策参数进行检测：

- $p2_k\leqslant 0$，下一个点为$(x_k,y_{k+1})$；

- $p2_k>0$，下一个点为$(x_k-1,y_{k+1})$

循环直到 $y=0$。

最后，利用对称、平移等操作得到其他三个象限中的点即可。

### 绘制曲线

#### Bezier

给定任一参数$u$，$u\in [0,1]$，利用`de Castelijau`递推算法来产生曲线上的点。
计算公式为：
$$
\begin{equation*}
    P_i^r=
    \begin{cases}
        P_i & r=0\\
        (1-u)P_i^{r-1}+uP_{i+1}^{r-1} & r=1,2,...,n;\; i=0,1,...,n-r
    \end{cases}
\end{equation*}
$$

$r=0$ 时，对应的顶点是曲线的控制点；
$r$不断增加时，每两个顶点生成一个新的顶点，
对应的顶点数递减，直到只剩下一个顶点。

在$[0,1]$内对$u$取值，对任一$u$的取值，
运行`de Castelijau`递推算法，得到Bezier曲线上的一个点。
最后，即可得到Bezier曲线。

#### B-spline

实验要求B-Spline绘制出的曲线为三次均匀B样条曲线，设共给定$n+1$个控制点。
在定义域$[u_3,u_{n+1}]$中对$u$取值，对任一$u$的取值，利用`deBoox-Cox`递推公式：
$$
\begin{equation*}
    B_{i,k}(u)
    =[\frac{u-u_i}{u_{i+k-1}-u_i}]B_{i,k-1}(u)
    +[\frac{u_{i+k}-u}{u_{i+k}-u_{i+1}}]B_{i+1,k-1}(u)
\end{equation*}
$$
$$
\begin{equation*}
    B_{i,1}(u)=
    \begin{cases}
    1, & u\in[u_i,u_{i+1}]\\
    0, & u\not\in[u_i,u_{i+1}]
    \end{cases}
\end{equation*}
$$
计算出每个顶点的B-Spline基函数$B_{i,k}(u)$;
再根据B-Spline曲线公式:
$$
\begin{equation*}
    P(u)=\sum_{i=0}^nP_iB_{i,k}(u),u\in[u_3,u_{n+1}]
\end{equation*}
$$
计算得曲线上的某一点。
最后，即可得到B-Spline曲线。

### 图元的平移

假设$(x_1,y_1)$平移至$(x_2,y_2)$：
$$
\begin{equation*}
    \begin{cases}
        x_2=x_1+dx\\
        y_2=y_1+dy
    \end{cases}
\end{equation*}
$$

对图元中的点执行上述操作即可。

### 图元的旋转

先考虑以原点为中心进行旋转的情况，再通过平移进行转化。

假设以原点为中心，P$(x_1,y_1) $逆时针旋转n度，

由于半径R=OA=$\sqrt{x_1^2+y^2_1}$，因此极坐标P$(R\cos\theta,R\sin\theta)$

其中 $\cos\theta=\frac{x_1}{R},$        $\sin\theta=\frac{y_1}{R}$

旋转后：

$x'=R\cos(\theta+n)=R(\cos\theta\cos n-\sin\theta\sin n)=x1\cos n-y1\sin n $

$y'=R\sin(\theta+n)=R(\sin \theta \cos n+\cos \theta \sin n)=y1\cos n+x1\sin n$

从而绕$(x_0,y_0)$旋转的公式：

$x'=x_0+(x_1-x_0)\cos n-(y_1-y_0)\sin n $

$y'=y_0+(y_1-y_0)\cos n+(x_1-x_0)\sin n$

对图元中的点执行上述操作即可。

### 图元的缩放

具体推导先假设以原点为中心的情况进行缩放，然后考虑以任意点为中心进行缩放

对于$(x_0,y_0)$，缩放倍数为$s$时：

$x'=sx_0,y'=sy_0$

那么对于以$(x_1,y_1)$为中心点进行缩放时：

$x'=sx_0+x_1,y'=sy_0+y_1$

对图元中的点执行上述操作即可。

### 线段的裁剪

#### Cohen-Sutherland

1. 输入直线段的两端点坐标：$p1(x1,y1)$、$p2(x2,y2)$，以及窗口的四条边界坐标。
2. 对p1、p2进行编码：点p1的编码为code1，点p2的编码为code2。
3. 若code1 | code2=0，对直线段应简取之，转(6)；
   否则，若code1&code2≠0，对直线段可简弃之，转(7)；
   当上述两条均不满足时，进行步骤(4)。
4.  确保p1在窗口外部：若p1在窗口内，则交换p1和p2的坐标值和编码。
5.  求出直线段与窗口边界的交点，并用该交点的坐标值替换p1的坐标值。也即在交点s处把线段一分为二。考虑到p1是窗口外的一点，因此可以去掉p1s。转(2)。
6.  用直线扫描转换算法画出当前的直线段p1p2。
7.  算法结束。

#### Liang-Barsky

初始化参数：

$$
\begin{equation*}
    \begin{cases}
        p_1=-\Delta x,q_1=x_0-x_{min}\\
        p_2=\Delta x,q_2=x_{max}-x_0\\
        p_3=-\Delta y,q_3=y_0-y_{min}\\
        p_4=\Delta y,q_4=y_{max}-y_0
    \end{cases}
\end{equation*}
$$

令$u_1=0$，$u_2=1$。
对任一组$p_k$和$q_k$，做如下检测：

1. $p_k==0 ~and~q_k<0$，说明不在窗口内，舍弃该线段，算法结束；
2. $p_k>0,u_2=max(q_k/p_k)$
3. $p_k<0,u_1=max(u_1,q_k/p_k)$
4. $u_1>u_2$，舍弃该线段，算法结束。

### 多边形的裁剪

#### Sutherland-Hodgeman

以裁剪窗口的某一条边为界，将画布区域分为内侧和外侧。

按序处理原多边形的每一条边，输出裁剪后的顶点坐标列表。

裁剪一条线段时，先求出端点$P_1$和$P_2$的编码$code_1$和$code_2$：

1. 如果$code_1$和$code_2$均为0，则$P_1$和$P_2$均在窗口内，线段全部位于窗口内部，应取之。
2. 如果$code_1$ & $code_2$不等于0，则$P_1$和$P_2$同时在窗口的外部某方向，线段全部位于窗口的外部，应弃之。
3. 如果上述两种条件均不成立，求出线段与窗口边界的交点，在交点处把线段一分为二，其中必有一段完全在窗口外，可以弃之；对另一段重复上述处理，直到该线段完全被舍弃或者找到位于窗口内的一段线段为止。

---

## 系统介绍

### CLI

实现在cg_cli.py中，使用PIL中的Image类型进行图形的绘制。

逐句扫描指令，调用cg_algorithms.py中对应算法得到像素并存储在item_dict中；

遇到saveCanvas指令，遍历item_dict并绘制图片，然后调用Image保存图片。

### GUI

实现在cg_gui.py中，主要借助PyQt5来完成图形用户界面的构建。

我将自己的GUI程序命名为`pyStroke`，意为用Python实现的画笔。

#### 组织模块

整体遵循参考代码的框架，分为以下三个部分。

##### MyCanvas

维护画布的各种状态，并响应针对画布的交互操作。

**鼠标控制：**

`mouseMoveEvent`

在绘制或编辑过程中根据鼠标的移动作出实时反馈，以便实时更新画布。

`mousePressEvent`

根据当前的不同**status**，按下鼠标会有不同的响应：可能是点选某个图元、从某处开始绘制、编辑或是新增一个绘制点。

`mouseReleaseEvent`

松开鼠标这个动作大多数情况下不做操作，若当前正在绘制或编辑图元（对于有些图元类型还需进一步判断），则可作为停止该操作的标志。

`mouseDoubleClickEvent`

双击鼠标主要为了**多控制点**的图元绘制而设计，双击后，当前多边形和曲线的绘制操作能够方便地结束。

**开始/结束操作：**

`start_draw` `start_edit` `start_clip`

被对应按钮的槽函数调用。

作为开始绘制、编辑、裁剪的准备工作，往往会重置或是初始化一些辅助变量，为后续鼠标操作提供支持。

`finish_draw` `finish_edit` `finish_clip`

根据当前的不同**status**，结束标志不同，就会被不同的鼠标操作调用。

作为结束绘制、编辑、裁剪的收尾工作，往往会将有效的临时变量存入item_dict等记录型变量中，并更新当前图元的一些属性。

**点选控制：**

`clear_selection` `selection_changed`

控制当前图元的选择操作，分别是清空、改变选择的图元，完成被选图元的属性更新。

##### MyItem

维护单个图元的各项属性，计算并绘制图元像素。

`paint`

调用`cg_algorithms.py`提供图元的像素，并调用**painter**加以绘制，在绘制过程中会调用以下几个辅助函数来丰富视觉效果。

`boundingRect` `auxiliary_point` `curve_auxiliary`

作为辅助函数，在绘制、选择、编辑图元时给出一些额外的辅助点、线以丰富视觉效果，更好地与用户交互。

##### MainWindow

维护图形界面的各种控件与对应的槽函数，同时依照参考代码，它的实例与`MyCanvas`的实例互为成员，方便互相调用更新（但在实际操作中我发现，也可能因此增大耦合度，使代码维护变得困难）。

我仿照`MyCanvas`的组织方式，将draw、edit、clip对应的槽函数通过统一的函数与`canvas_widget`进行联系，提高了代码可维护性。

**各种控件与对应的槽函数相链接**，被触发时即可调用，通过对应变量名称可以清晰判断。

#### 界面设计

界面整体沿用参考代码的实现，去除了`list_widget`，因为代码中已经实现了鼠标点选图元的操作，保留`list_widget`显得画蛇添足。

在此基础上，**新增了应用图标和一些常用操作的按钮**，依次包括指针点选、保存画布、退出、重置画布、画笔颜色、平移、旋转、缩放、复制、粘贴、删除。

<img src="C:\Users\dongc\AppData\Roaming\Typora\typora-user-images\image-20201226173933603.png" alt="image-20201226173933603" style="zoom:67%;" />

#### 交互逻辑

引入**鼠标点选图元**的功能，使整体操作更为方便，基本是所见即所得的效果。

选择`指针点选`，则进入正常选择的状态：若选到空白处，则去除已有的选择项，并重置状态；若选到图元，则可进行下一步编辑操作。判断某图元是否被选中的标志是其周围是否**被矩形框住**。

工具栏中若干按钮的效果与菜单栏中一致，引入的目的是方便操作。

图元绘制过程中，会有额外的点、线增强视觉效果，辅助绘制。

具体操作方式及截图详见使用说明书。

---

## 补充说明

### 关于演示视频

演示视频中有不少地方**声音不清晰**，我尝试了多次，但限于设备与软件无法很好地解决这个问题。

如有需要，我可以对其中内容再进行解释。

### 附加功能

- 文件操作：将画布**保存**为图片
- 图元编辑：**多边形裁剪，删除、复制、粘贴**图元
- 交互方式：**鼠标点选**图元，双击结束多边形、曲线的绘制
- 视觉辅助：在绘制图元时会展现一些**辅助点和线**帮助用户绘制，增强视觉丰富性。
- 引入**工具栏**：加入若干常用操作，方便使用

---

## 总结

在本项目开发过程中，我可谓受益良多：

- 运用并实现各类图形学算法，夯实基础；
- 基于PyQt5实现了图形用户界面，熟悉了基础的接口运用，并第一次完整开发了一个GUI程序；
- 在反复debug过程中，加深了对图形学算法的掌握程度和对Python 的运用能力。
- 加强了程序设计的整体框架思维，相比于以往只关注功能能否顺利实现，我现在会更多地关注代码是否写得简洁、高效、鲁棒、易于维护。

图形学的大作业到此为止，但我相信以后的学习与工作中还会大量地与图形学打交道，尽管或许不会像现在这样自己实现算法，但正确理解算法才是正确调用各种库的前提。虽然过程中也踩了很多坑，但奇怪地没有出现烦躁的抗拒感——衷心感谢这次大作业带给我的收获和启发！

## References

《计算机图形学教程》 by 孙正兴

南京大学 计算机图形学 课堂ppt

[计算机图形学----DDA、Bresenham直线算法  by ljheee](https://blog.csdn.net/ljheee/article/details/73235302?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2.channel_param&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2.channel_param)

[【计算机图形学】直线的两种生成算法（DDA算法、Bresenham算法）by 酱懵静](https://blog.csdn.net/the_ZED/article/details/105546159?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-3.channel_param&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-3.channel_param)

[【计算机图形学】DDA算法和Bresenham算法 by MMomega](https://blog.csdn.net/mmogega/article/details/53055596?utm_medium=distribute.pc_relevant.none-task-blog-title-2&spm=1001.2101.3001.4242)

[图形学变换——平移、旋转和缩放 by zhanxi1992](https://blog.csdn.net/zhanxi1992/article/details/106532991/)

[图形学 ---- 二维几何变换（二维图形矩阵平移，旋转，缩放）by 天道ぃ](https://blog.csdn.net/qq_37682160/article/details/105609001?utm_medium=distribute.pc_relevant.none-task-blog-title-2&spm=1001.2101.3001.4242)

[算法系列之十三：椭圆的生成算法_oRbIt 的专栏-CSDN博客](https://blog.csdn.net/orbit/article/details/7496008)

[ Cohen-SutherLand算法(编码算法)_vincent2610的专栏-CSDN博客](https://blog.csdn.net/vincent2610/article/details/47948737)

[Cohen-Sutherland算法概述_徐奕的专栏-CSDN博客](https://blog.csdn.net/xyisv/article/details/83514472)

[Liang-Barsky算法 - cnblog-null - 博客园 (cnblogs.com)](https://www.cnblogs.com/cnblog-wuran/p/9813841.html)

[B样条曲线（B-spline Curves）_温故而知新-CSDN博客_b样条曲线](https://blog.csdn.net/qq_40597317/article/details/81155571)

[简单粗暴：B-样条曲线入门 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/50626506)

[Cohen-SutherLand算法(编码算法) - 明明是悟空 - 博客园 (cnblogs.com)](https://www.cnblogs.com/x_wukong/p/4186890.html)

[Riverbank Computing | Introduction](https://riverbankcomputing.com/software/pyqt/intro)

[PyQt Tutorial - Tutorialspoint](https://www.tutorialspoint.com/pyqt/index.htm)

[Qt for Python — Qt for Python](https://doc.qt.io/qtforpython/)