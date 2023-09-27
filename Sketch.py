"""
This is the main entry of your program. Almost all things you need to implement is in this file.
The main class Sketch inherit from CanvasBase. For the parts you need to implement, they all marked TODO.
First version Created on 09/28/2018

:author: micou(Zezhou Sun)
:version: 2021.2.1

"""

"""
CS 680
Name: Zhaozhan Huang
U03088498
"""

import os

import wx
import math
import random
import numpy as np

from Buff import Buff
from Point import Point
from ColorType import ColorType
from CanvasBase import CanvasBase

try:
    # From pip package "Pillow"
    from PIL import Image
except Exception:
    print("Need to install PIL package. Pip package name is Pillow")
    raise ImportError


class Sketch(CanvasBase):
    """
    Please don't forget to override interrupt methods, otherwise NotImplementedError will throw out
    
    Class Variable Explanation:

    * debug(int): Define debug level for log printing

        * 0 for stable version, minimum log is printed
        * 1 will print general logs for lines and triangles
        * 2 will print more details and do some type checking, which might be helpful in debugging
    
    * texture(Buff): loaded texture in Buff instance
    * random_color(bool): Control flag of random color generation of point.
    * doTexture(bool): Control flag of doing texture mapping
    * doSmooth(bool): Control flag of doing smooth
    * doAA(bool): Control flag of doing anti-aliasing
    * doAAlevel(int): anti-alising super sampling level
        
    Method Instruction:

    * Interrupt_MouseL(R): Used to deal with mouse click interruption. Canvas will be refreshed with updated buff
    * Interrupt_Keyboard: Used to deal with key board press interruption. Use this to add new keys or new methods
    * drawPoint: method to draw a point
    * drawLine: method to draw a line
    * drawTriangle: method to draw a triangle with filling and smoothing
    
    List of methods to override the ones in CanvasBase:

    * Interrupt_MouseL
    * Interrupt_MouseR
    * Interrupt_Keyboard
        
    Here are some public variables in parent class you might need:

    * points_r: list<Point>. to store all Points from Mouse Right Button
    * points_l: list<Point>. to store all Points from Mouse Left Button
    * buff    : Buff. buff of current frame. Change on it will change display on screen
    * buff_last: Buff. Last frame buffer
        
    """

    debug = 0
    texture_file_path = "./pattern.jpg"
    texture = None

    # control flags
    randomColor = False
    doTexture = False
    doSmooth = False
    doAA = False
    doAAlevel = 4

    # test case status
    MIN_N_STEPS = 6
    MAX_N_STEPS = 192
    n_steps = 12  # For test case only
    test_case_index = 0
    test_case_list = []  # If you need more test case, write them as a method and add it to list

    def __init__(self, parent):
        """
        Initialize the instance, load texture file to Buff, and load test cases.

        :param parent: wxpython frame
        :type parent: wx.Frame
        """
        super(Sketch, self).__init__(parent)
        self.test_case_list = [lambda _: self.clear(),
                               self.testCaseLine01,
                               self.testCaseLine02,
                               self.testCaseTri01,
                               self.testCaseTri02,
                               self.testCaseTriTexture01]  # method at here must accept one argument, n_steps
        # Try to read texture file
        if os.path.isfile(self.texture_file_path):
            # Read image and make it to an ndarray
            texture_image = Image.open(self.texture_file_path)
            texture_array = np.array(texture_image).astype(np.uint8)
            # Because imported image is upside down, reverse it
            texture_array = np.flip(texture_array, axis=0)
            # Store texture image in our Buff format
            self.texture = Buff(texture_array.shape[1], texture_array.shape[0])
            self.texture.setStaticBuffArray(np.transpose(texture_array, (1, 0, 2)))
            if self.debug > 0:
                print("Texture Loaded with shape: ", texture_array.shape)
                print("Texture Buff have size: ", self.texture.size)
        else:
            raise ImportError("Cannot import texture file")

    def __addPoint2Pointlist(self, pointlist, x, y):
        if self.randomColor:
            p = Point((x, y), ColorType(random.random(), random.random(), random.random()))
        else:
            p = Point((x, y), ColorType(1, 0, 0))
        pointlist.append(p)

    # Deal with Mouse Left Button Pressed Interruption
    def Interrupt_MouseL(self, x, y):
        self.__addPoint2Pointlist(self.points_l, x, y)
        # Draw a point when one point provided or a line when two ends provided
        if len(self.points_l) % 2 == 1:
            if self.debug > 0:
                print("draw a point", self.points_l[-1])
            # first click: draw a point
            self.drawPoint(self.buff, self.points_l[-1])
        elif len(self.points_l) % 2 == 0 and len(self.points_l) > 0:
            if self.debug > 0:
                print("draw a line from ", self.points_l[-1], " -> ", self.points_l[-2])
            # Second click: draw a line
            self.drawLine(self.buff, self.points_l[-2], self.points_l[-1], self.doSmooth, self.doAA, 4)
            self.points_l.clear()

    # Deal with Mouse Right Button Pressed Interruption
    def Interrupt_MouseR(self, x, y):
        self.__addPoint2Pointlist(self.points_r, x, y)
        if len(self.points_r) % 3 == 1:
            if self.debug > 0:
                print("draw a point", self.points_r[-1])
            # First click: draw a point
            self.drawPoint(self.buff, self.points_r[-1])
        elif len(self.points_r) % 3 == 2:
            if self.debug > 0:
                print("draw a line from ", self.points_r[-1], " -> ", self.points_r[-2])
            # Second click: draw a line
            self.drawLine(self.buff, self.points_r[-2], self.points_r[-1], self.doSmooth)
        elif len(self.points_r) % 3 == 0 and len(self.points_r) > 0:
            if self.debug > 0:
                print("draw a triangle {} -> {} -> {}".format(self.points_r[-3], self.points_r[-2], self.points_r[-1]))
            # Third click: draw a triangle
            self.drawTriangle(self.buff, self.points_r[-3],self.points_r[-2],self.points_r[-1], self.doSmooth)
            self.points_r.clear()

    def Interrupt_Keyboard(self, keycode):
        """
        keycode Reference: https://docs.wxpython.org/wx.KeyCode.enumeration.html#wx-keycode

        * r, R: Generate Random Color point
        * c, C: clear buff and screen
        * LEFT, UP: Last Test case
        * t, T, RIGHT, DOWN: Next Test case
        """
        # Trigger for test cases
        if keycode in [wx.WXK_LEFT, wx.WXK_UP]:  # Last Test Case
            self.clear()
            if len(self.test_case_list) != 0:
                self.test_case_index = (self.test_case_index - 1) % len(self.test_case_list)
            self.test_case_list[self.test_case_index](self.n_steps)
            print("Display Test case: ", self.test_case_index, "n_steps: ", self.n_steps)
        if keycode in [ord("t"), ord("T"), wx.WXK_RIGHT, wx.WXK_DOWN]:  # Next Test Case
            self.clear()
            if len(self.test_case_list) != 0:
                self.test_case_index = (self.test_case_index + 1) % len(self.test_case_list)
            self.test_case_list[self.test_case_index](self.n_steps)
            print("Display Test case: ", self.test_case_index, "n_steps: ", self.n_steps)
        if chr(keycode) in ",<":
            self.clear()
            self.n_steps = max(self.MIN_N_STEPS, round(self.n_steps / 2))
            self.test_case_list[self.test_case_index](self.n_steps)
            print("Display Test case: ", self.test_case_index, "n_steps: ", self.n_steps)
        if chr(keycode) in ".>":
            self.clear()
            self.n_steps = min(self.MAX_N_STEPS, round(self.n_steps * 2))
            self.test_case_list[self.test_case_index](self.n_steps)
            print("Display Test case: ", self.test_case_index, "n_steps: ", self.n_steps)

        # Switches
        if chr(keycode) in "rR":
            self.randomColor = not self.randomColor
            print("Random Color: ", self.randomColor)
        if chr(keycode) in "cC":
            self.clear()
            print("clear Buff")
        if chr(keycode) in "sS":
            self.doSmooth = not self.doSmooth
            print("Do Smooth: ", self.doSmooth)
        if chr(keycode) in "aA":
            self.doAA = not self.doAA
            print("Do Anti-Aliasing: ", self.doAA)
        if chr(keycode) in "mM":
            self.doTexture = not self.doTexture
            print("texture mapping: ", self.doTexture)

    def queryTextureBuffPoint(self, texture: Buff, x: int, y: int) -> Point:
        """
        Query a point at texture buff, should only be used in texture buff query

        :param texture: The texture buff you want to query from
        :type texture: Buff
        :param x: The query point x coordinate
        :type x: int
        :param y: The query point y coordinate
        :type y: int
        :rtype: Point
        """
        if self.debug > 1:
            if x != min(max(0, int(x)), texture.width - 1):
                print("Warning: Texture Query x coordinate outbound! x = {} texture.width = {}".format(x, texture.width))
            if y != min(max(0, int(y)), texture.height - 1):
                print("Warning: Texture Query y coordinate outbound! y = {} texture.height = {}".format(x, texture.height))
        return texture.getPointFromPointArray(x, y)

    @staticmethod
    def drawPoint(buff, point):
        # print("Now calling drawPoint()... point is {}".format(point))
        """
        Draw a point on buff

        :param buff: The buff to draw point on
        :type buff: Buff
        :param point: A point to draw on buff
        :type point: Point
        :rtype: None
        """
        x, y = point.coords
        c = point.color
        # because we have already specified buff.buff has data type uint8, type conversion will be done in numpy
        buff.buff[x, y, 0] = c.r * 255
        buff.buff[x, y, 1] = c.g * 255
        buff.buff[x, y, 2] = c.b * 255

    def drawLine(self, buff, p1:Point, p2:Point, doSmooth=True, doAA=False, doAAlevel=4):
        if p1 == p2:
            return
        
        """
        Draw a line between p1 and p2 on buff

        :param buff: The buff to edit
        :type buff: Buff
        :param p1: One end point of the line
        :type p1: Point
        :param p2: Another end point of the line
        :type p2: Point
        :param doSmooth: Control flag of color smooth interpolation
        :type doSmooth: bool
        :param doAA: Control flag of doing anti-aliasing
        :type doAA: bool
        :param doAAlevel: anti-aliasing super sampling level
        :type doAAlevel: int
        :rtype: None 
        """
        ##### TODO 1: Use Bresenham algorithm to draw a line between p1 and p2 on buff.
        # Requirements:
        #   1. Only integer is allowed in interpolate point coordinates between p1 and p2
        #   2. Float number is allowed in interpolate point color

        # We use Bresenham's
        # We divide the question into two cases: 1. abs(m) <= 1 (x-based Bresenham)  2. abs(m) > 1 (y-based Bresenham)
        # In x-based case, we make x1 < x2. In y-based case, we make y1 < y2

        m = abs(p1.coords[1] - p2.coords[1]) / abs(p1.coords[0] - p2.coords[0]) if p1.coords[0] != p2.coords[0] else "inf"
        firstColor = p1.color

        if doAA == False:
            # case 1    0 <= |m| < 1 ----- x based
            if m != "inf" and m <= 1:
                if p1.coords[0] > p2.coords[0]: # make sure that p1.x <= p2.x 
                    p1, p2 = p2, p1
                x1 = p1.coords[0]
                y1 = p1.coords[1]
                x2 = p2.coords[0]
                y2 = p2.coords[1]
                x = x1; y = y1; dx = x2 - x1; dy = y2 - y1
                D = 2*abs(dy) - abs(dx)
                while x <= x2:
                    if doSmooth == True:
                        c1 = p1.color
                        c2 = p2.color
                        f1 = (x2 - x) / (x2 - x1)
                        f2 = (x - x1) / (x2 - x1)
                        # x1 --- x --- x2
                        self.drawPoint(buff, Point((x,y), ColorType(f1*c1.r + f2*c2.r, f1*c1.g + f2*c2.g, f1*c1.b + f2*c2.b), None))
                    else:
                        self.drawPoint(buff, Point((x,y), firstColor, None))

                    x += 1 if(dx > 0) else -1
                    if D <= 0:
                        D = D + 2*abs(dy)
                    else:
                        D = D + 2*abs(dy) - 2*abs(dx)
                        y += 1 if (dy > 0) else -1
            
            # case 2    1 < m < +inf ------ y based
            if m == "inf" or m > 1:
                if p1.coords[1] > p2.coords[1]: # make sure that p1.y <= p2.y
                    p1, p2 = p2, p1
                x1 = p1.coords[0]
                y1 = p1.coords[1]
                x2 = p2.coords[0]
                y2 = p2.coords[1]
                x = x1; y = y1; dx = x2 - x1; dy = y2 - y1
                D = 2*abs(dx) - abs(dy)
                while y <= y2:
                    if doSmooth == True:
                        c1 = p1.color
                        c2 = p2.color
                        f1 = (y2 - y) / (y2 - y1)
                        f2 = (y - y1) / (y2 - y1)
                        # y1 --- y --- y2
                        self.drawPoint(buff, Point((x,y), ColorType(f1*c1.r + f2*c2.r, f1*c1.g + f2*c2.g, f1*c1.b + f2*c2.b), None))
                    else:
                        self.drawPoint(buff, Point((x,y), firstColor, None))
                        
                    y += 1 if(dy > 0) else -1
                    if D <= 0:
                        D = D + 2*abs(dx)
                    else:
                        D = D + 2*abs(dx) - 2*abs(dy)
                        x += 1 if (dx > 0) else -1

        ### TODO 4 (extra credit: anti aliased rendering of line) ###
        
        # We do a mapping between [x1, x2] * [y1, y2] and [0, 4(x2 - x1)] * [0, 4(y2 - y1)]
        # We keep track of num_of_points, num_of_point belongs to {1,2,3,4}. It decides the brightness of each pixel
        # (x, y) is the current Point in [0, 4(x2 - x1)] * [0, 4(y2 - y1)]
        # Whenever x % 4 becomes 0 || y % 4 becomes 0, we know that we enter a new pixel in [x1, x2] * [y1, y2] 
        if doAA == True:
            m = abs(p1.coords[1] - p2.coords[1]) / abs(p1.coords[0] - p2.coords[0]) if p1.coords[0] != p2.coords[0] else "inf"
            if m != "inf" and m <= 1: # x based
                p1, p2 = sorted([p1, p2], key=lambda p: p.coords[0])
                x1 = p1.coords[0]
                x2 = p2.coords[0]
                y1 = p1.coords[1]
                y2 = p2.coords[1]
                dx = 4*(x2 - x1); dy = 4*(y2 - y1)
                D = 2*abs(dy) - abs(dx)
                num_of_points = 0
                x_prev = 0
                y_prev = 0
                x = 0
                y = 0
                while x <= 4*(x2 - x1):
                    num_of_points += 1
                    print(f"x1={x1}, x2={x2} x={x}, y={y}, x_prev={x_prev}, y_prev={y_prev}")
                    if( x % 4 == 0 and x != x_prev) or (y % 4 == 0 and y != y_prev):
                        print(f"drawPoint at ({x1 + x//4}, {y1 + y//4})... rgb: {(num_of_points / 4) * firstColor}... num_of_points == {num_of_points}")
                        print(f"rgb: {(num_of_points / 4) * firstColor}")
                        self.drawPoint(buff, Point((x1 + x_prev//4, y1 + y_prev//4), (num_of_points / 4) * firstColor , None))
                        num_of_points = 0
                    x_prev = x
                    x += 1 if(dx > 0) else -1
                    if D <= 0:
                        y_prev = y
                        D = D + 2*abs(dy)
                    else:
                        D = D + 2*abs(dy) - 2*abs(dx)
                        y_prev = y
                        y += 1 if (dy > 0) else -1
                return
            elif m == "inf" or m > 1: # y based
                p1, p2 = sorted([p1, p2], key=lambda p: p.coords[1])
                x1 = p1.coords[0]
                x2 = p2.coords[0]
                y1 = p1.coords[1]
                y2 = p2.coords[1]
                dx = 4*(x2 - x1); dy = 4*(y2 - y1)
                D = 2*abs(dx) - abs(dy)
                num_of_points = 0
                x_prev = 0
                y_prev = 0
                x = 0
                y = 0
                while y <= 4*(y2 - y1):
                    self.drawPoint(buff, Point((x,y), ColorType(0,1,0), None))
                    num_of_points += 1
                    print(f"y1={y1}, y2={y2} x={x}, y={y}, x_prev={x_prev}, y_prev={y_prev}")
                    if( x % 4 == 0 and x != x_prev) or (y % 4 == 0 and y != y_prev):
                        print(f"drawPoint at ({x1 + x//4}, {y1 + y//4})... rgb: {(num_of_points / 4) * firstColor}... num_of_points == {num_of_points}")
                        print(f"rgb: {(num_of_points / 4) * firstColor}")
                        self.drawPoint(buff, Point((x1 + x_prev//4, y1 + y_prev//4), (num_of_points / 4) * firstColor , None))
                        num_of_points = 0
                    y_prev = y
                    y += 1 if(dy > 0) else -1
                    if D <= 0:
                        x_prev = x
                        D = D + 2*abs(dx)
                    else:
                        D = D + 2*abs(dx) - 2*abs(dx)
                        x_prev = x
                        x += 1 if (dx > 0) else -1
                return

        return

    def drawTriangle(self, buff: Buff, p1: Point, p2: Point, p3: Point, doSmooth=True, doAA=False, doAAlevel=4, doTexture=False):
        """
        draw Triangle to buff. apply smooth color filling if doSmooth set to true, otherwise fill with first point color
        if doAA is true, apply anti-aliasing to triangle based on doAAlevel given.

        :param buff: The buff to edit
        :type buff: Buff
        :param p1: First triangle vertex
        :param p2: Second triangle vertex
        :param p3: Third triangle vertex
        :type p1: Point
        :type p2: Point
        :type p3: Point
        :param doSmooth: Color smooth filling control flag
        :type doSmooth: bool
        :param doAA: Anti-aliasing control flag
        :type doAA: bool
        :param doAAlevel: Anti-aliasing super sampling level
        :type doAAlevel: int
        :param doTexture: Draw triangle with texture control flag
        :type doTexture: bool
        :rtype: None
        """
        ##### TODO 2: Write a triangle rendering function, which support smooth bilinear interpolation of the vertex color
        firstColor = p1.color
        
        p1, p2, p3 = sorted([p1, p2, p3], key=lambda p: p.coords[1])

        y1 = p1.coords[1]
        y2 = p2.coords[1]
        y3 = p3.coords[1]

        x1 = p1.coords[0]
        x2 = p2.coords[0]
        x3 = p3.coords[0]

        # degenerate?
        m12 = (y2 - y1) / (x2 - x1) if (x1 != x2) else "inf"
        m13 = (y3 - y1) / (x3 - x1) if (x1 != x3) else "inf"
        m23 = (y3 - y2) / (x3 - x2) if (x2 != x3) else "inf"

        c1 = p1.color
        c2 = p2.color
        c3 = p3.color

        if doTexture == False and doSmooth == False:
            for y in range(y1, y2): # p1 -> p2   v.s  p1 -> p3 (partial)
                x12 = round(x1 + (y - y1) / m12) if m12 != "inf" else x1
                x13 = round(x1 + (y - y1) / m13) if m13 != "inf" else x1
                for x in range(min(x12, x13), max(x12, x13) + 1):
                    self.drawPoint(self.buff, Point((x,y), firstColor, None))
            for y in range(y2, y3): # p2 -> p3  v.s  p1 -> p3 (partial)
                x13 = round(x1 + (y - y1) / m13) if m13 != "inf" else x1
                x23 = round(x2 + (y - y2) / m23) if m23 != "inf" else x2
                for x in range(min(x13, x23), max(x13, x23) + 1):
                    self.drawPoint(self.buff, Point((x,y), firstColor, None))
            return
                
        if doTexture == False and doSmooth == True:
            for y in range(y1, y2): # p1 -> p2   v.s  p1 -> p3 (partial)
                x12 = round(x1 + (y - y1) / m12) if m12 != "inf" else x1
                c12 = (y - y1)/(y2 - y1) * c2 + (y2 - y)/(y2 - y1) * c1 if y2 - y1 != 0 else c1
                x13 = round(x1 + (y - y1) / m13) if m13 != "inf" else x1
                c13 = (y - y1)/(y3 - y1) * c3 + (y3 - y)/(y3 - y1) * c1 if y3 - y1 != 0 else c1
                for x in range(min(x12, x13), max(x12, x13)):
                    c123 = (x - x13)/(x12 - x13) * c12 + (x12 - x)/(x12 - x13) * c13
                    self.drawPoint(self.buff, Point((x,y), c123, None))
            for y in range(y2, y3): # p2 -> p3  v.s  p1 -> p3 (partial)
                x13 = round(x1 + (y - y1) / m13) if m13 != "inf" else x1
                c13 = (y - y1)/(y3 - y1) * c3 + (y3 - y)/(y3 - y1) * c1
                x23 = round(x2 + (y - y2) / m23) if m23 != "inf" else x2
                c23 = (y - y2)/(y3 - y2) * c3 + (y3 - y)/(y3 - y2) * c2
                for x in range(min(x13, x23), max(x13, x23)):
                    c123 = (x - x13)/(x23 - x13) * c23 + (x23 - x)/(x23 - x13) * c13
                    self.drawPoint(self.buff, Point((x,y), c123, None))
            return
            
            

        ##### TODO 3(For CS680 Students): Implement texture-mapped fill of triangle. Texture is stored in self.texture
        # Requirements:
        #   1. For flat shading of the triangle, use the first vertex color.
        #   2. Polygon scan fill algorithm and the use of barycentric coordinate are not allowed in this function
        #   3. You should be able to support both flat shading and smooth shading, which is controlled by doSmooth
        #   4. For texture-mapped fill of triangles, it should be controlled by doTexture flag.

        if doTexture == True:
            x_min = min([p1.coords[0], p2.coords[0], p3.coords[0]])
            x_max = max([p1.coords[0], p2.coords[0], p3.coords[0]])
            y_min = min([p1.coords[1], p2.coords[1], p3.coords[1]])
            y_max = max([p1.coords[1], p2.coords[1], p3.coords[1]])
            dx = x_max - x_min
            dy = y_max - y_min
            texture_width = self.texture.width
            texture_height = self.texture.height

            for y in range(y1, y2): # p1 -> p2   v.s  p1 -> p3 (partial)
                x12 = round(x1 + (y - y1) / m12) if m12 != "inf" else x1
                x13 = round(x1 + (y - y1) / m13) if m13 != "inf" else x1

                for x in range(min(x12, x13), max(x12, x13)):
                    u = (texture_width - 1) * (x - x_min) / dx
                    v = (texture_height - 1) * (y - y_min) / dy
                    # get the four nearest points, then c123 = avg(colors)

                    color1 = self.texture.getPoint(math.floor(u), math.floor(v)).color
                    color2 = self.texture.getPoint(math.floor(u), math.ceil(v)).color
                    color3 = self.texture.getPoint(math.ceil(u), math.floor(v)).color
                    color4 = self.texture.getPoint(math.ceil(u), math.ceil(v)).color
                    if math.floor(u) != math.ceil(u) and math.floor(v) != math.ceil(v):
                        c_left = (v - math.floor(v)) * color2 + (math.ceil(v) - v) * color1
                        c_right = (v - math.floor(v)) * color4 + (math.ceil(v) - v) * color3
                        c123 = (u - math.floor(u)) * c_right + (math.ceil(u) - u) * c_left
                    elif math.floor(u) != math.ceil(u):
                        c123 = (u - math.floor(u)) * color3 + (math.ceil(u) - u) * color1
                    elif math.floor(v) != math.ceil(v):
                        c123 = (v - math.floor(v)) * color2 + (math.ceil(v) - v) * color1
                    else:
                        c123 = color1
                    self.drawPoint(self.buff, Point((x,y), c123, None))

            for y in range(y2, y3): # p2 -> p3  v.s  p1 -> p3 (partial)
                x13 = round(x1 + (y - y1) / m13) if m13 != "inf" else x1
                x23 = round(x2 + (y - y2) / m23) if m23 != "inf" else x2
                for x in range(min(x13, x23), max(x13, x23)):
                    u = (texture_width - 1) * (x - x_min) / dx
                    v = (texture_height - 1) * (y - y_min) / dy
                    # get the four nearest points, then c123 = avg(colors)
                    color1 = self.texture.getPoint(math.floor(u), math.floor(v)).color
                    color2 = self.texture.getPoint(math.floor(u), math.ceil(v)).color
                    color3 = self.texture.getPoint(math.ceil(u), math.floor(v)).color
                    color4 = self.texture.getPoint(math.ceil(u), math.ceil(v)).color
                    # if math.floor(u) != math.ceil(u) and math.floor(v) != math.ceil(v):
                    if math.floor(u) != math.ceil(u) and math.floor(v) != math.ceil(v):
                        c_left = (v - math.floor(v)) * color2 + (math.ceil(v) - v) * color1
                        c_right = (v - math.floor(v)) * color4 + (math.ceil(v) - v) * color3
                        c123 = (u - math.floor(u)) * c_right + (math.ceil(u) - u) * c_left
                    elif math.floor(u) != math.ceil(u):
                        c123 = (u - math.floor(u)) * color3 + (math.ceil(u) - u) * color1
                    elif math.floor(v) != math.ceil(v):
                        c123 = (v - math.floor(v)) * color2 + (math.ceil(v) - v) * color1
                    else:
                        c123 = color1
                    self.drawPoint(self.buff, Point((x,y), c123, None))
            return
        return

    # test for lines lines in all directions
    def testCaseLine01(self, n_steps):
        center_x = int(self.buff.width / 2)
        center_y = int(self.buff.height / 2)
        radius = int(min(self.buff.width, self.buff.height) * 0.45)

        v0 = Point([center_x, center_y], ColorType(1, 1, 0))
        for step in range(0, n_steps):
            theta = math.pi * step / n_steps
            v1 = Point([center_x + int(math.sin(theta) * radius), center_y + int(math.cos(theta) * radius)],
                       ColorType(0, 0, (1 - step / n_steps)))
            v2 = Point([center_x - int(math.sin(theta) * radius), center_y - int(math.cos(theta) * radius)],
                       ColorType(0, (1 - step / n_steps), 0))
            self.drawLine(self.buff, v2, v0, doSmooth=True)
            self.drawLine(self.buff, v0, v1, doSmooth=True)

    # test for lines: drawing circle and petal 
    def testCaseLine02(self, n_steps):
        n_steps = 2 * n_steps
        d_theta = 2 * math.pi / n_steps
        d_petal = 12 * math.pi / n_steps
        cx = int(self.buff.width / 2)
        cy = int(self.buff.height / 2)
        radius = (0.75 * min(cx, cy))
        p = radius * 0.25

        # Outer petals
        for i in range(n_steps + 2):
            self.drawLine(self.buff,
                          Point((math.floor(0.5 + radius * math.sin(d_theta * i) + p * math.sin(d_petal * i)) + cx,
                                 math.floor(0.5 + radius * math.cos(d_theta * i) + p * math.cos(d_petal * i)) + cy),
                                ColorType(1, (128 + math.sin(d_theta * i * 5) * 127) / 255,
                                          (128 + math.cos(d_theta * i * 5) * 127) / 255)),
                          Point((math.floor(
                              0.5 + radius * math.sin(d_theta * (i + 1)) + p * math.sin(d_petal * (i + 1))) + cx,
                                 math.floor(0.5 + radius * math.cos(d_theta * (i + 1)) + p * math.cos(
                                     d_petal * (i + 1))) + cy),
                                ColorType(1, (128 + math.sin(d_theta * 5 * (i + 1)) * 127) / 255,
                                          (128 + math.cos(d_theta * 5 * (i + 1)) * 127) / 255)),
                          doSmooth=True, doAA=self.doAA, doAAlevel=self.doAAlevel)

        # Draw circle
        for i in range(n_steps + 1):
            v0 = Point((math.floor(0.5 * radius * math.sin(d_theta * i)) + cx,
                        math.floor(0.5 * radius * math.cos(d_theta * i)) + cy), ColorType(1, 97. / 255, 0))
            v1 = Point((math.floor(0.5 * radius * math.sin(d_theta * (i + 1))) + cx,
                        math.floor(0.5 * radius * math.cos(d_theta * (i + 1))) + cy), ColorType(1, 97. / 255, 0))
            self.drawLine(self.buff, v0, v1, doSmooth=True, doAA=self.doAA, doAAlevel=self.doAAlevel)

    # test for smooth filling triangle
    def testCaseTri01(self, n_steps):
        n_steps = int(n_steps / 2)
        delta = 2 * math.pi / n_steps
        radius = int(min(self.buff.width, self.buff.height) * 0.45)
        cx = int(self.buff.width / 2)
        cy = int(self.buff.height / 2)
        theta = 0

        for _ in range(n_steps):
            theta += delta
            v0 = Point((cx, cy), ColorType(1, 1, 1))
            v1 = Point((int(cx + math.sin(theta) * radius), int(cy + math.cos(theta) * radius)),
                       ColorType((127. + 127. * math.sin(theta)) / 255,
                                 (127. + 127. * math.sin(theta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + 4 * math.pi / 3)) / 255))
            v2 = Point((int(cx + math.sin(theta + delta) * radius), int(cy + math.cos(theta + delta) * radius)),
                       ColorType((127. + 127. * math.sin(theta + delta)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 4 * math.pi / 3)) / 255))
            self.drawTriangle(self.buff, v1, v0, v2, False, self.doAA, self.doAAlevel)

    def testCaseTri02(self, n_steps):
        # Test case for no smooth color filling triangle
        n_steps = int(n_steps / 2)
        delta = 2 * math.pi / n_steps
        radius = int(min(self.buff.width, self.buff.height) * 0.45)
        cx = int(self.buff.width / 2)
        cy = int(self.buff.height / 2)
        theta = 0

        for _ in range(n_steps):
            theta += delta
            v0 = Point((cx, cy), ColorType(1, 1, 1))
            v1 = Point((int(cx + math.sin(theta) * radius), int(cy + math.cos(theta) * radius)),
                       ColorType((127. + 127. * math.sin(theta)) / 255,
                                 (127. + 127. * math.sin(theta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + 4 * math.pi / 3)) / 255))
            v2 = Point((int(cx + math.sin(theta + delta) * radius), int(cy + math.cos(theta + delta) * radius)),
                       ColorType((127. + 127. * math.sin(theta + delta)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 4 * math.pi / 3)) / 255))
            self.drawTriangle(self.buff, v0, v1, v2, True, self.doAA, self.doAAlevel)

    def testCaseTriTexture01(self, n_steps):
        # Test case for no smooth color filling triangle
        n_steps = int(n_steps / 2)
        delta = 2 * math.pi / n_steps
        radius = int(min(self.buff.width, self.buff.height) * 0.45)
        cx = int(self.buff.width / 2)
        cy = int(self.buff.height / 2)
        theta = 0

        triangleList = []
        for _ in range(n_steps):
            theta += delta
            v0 = Point((cx, cy), ColorType(1, 1, 1))
            v1 = Point((int(cx + math.sin(theta) * radius), int(cy + math.cos(theta) * radius)),
                       ColorType((127. + 127. * math.sin(theta)) / 255,
                                 (127. + 127. * math.sin(theta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + 4 * math.pi / 3)) / 255))
            v2 = Point((int(cx + math.sin(theta + delta) * radius), int(cy + math.cos(theta + delta) * radius)),
                       ColorType((127. + 127. * math.sin(theta + delta)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 4 * math.pi / 3)) / 255))
            triangleList.append([v0, v1, v2])

        for t in triangleList:
            self.drawTriangle(self.buff, *t, doTexture=True)


if __name__ == "__main__":
    def main():
        print("This is the main entry! ")
        app = wx.App(False)
        # Set FULL_REPAINT_ON_RESIZE will repaint everything when scaling the frame
        # here is the style setting for it: wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE
        # wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER will disable canvas resize.
        frame = wx.Frame(None, size=(500, 500), title="Test", style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        canvas = Sketch(frame)
        canvas.debug = 0

        frame.Show()
        app.MainLoop()


    def codingDebug():
        """
        If you are still working on the assignment, we suggest to use this as the main call.
        There will be more strict type checking in this version, which might help in locating your bugs.
        """
        print("This is the debug entry! ")
        import cProfile
        import pstats
        profiler = cProfile.Profile()
        profiler.enable()

        app = wx.App(False)
        # Set FULL_REPAINT_ON_RESIZE will repaint everything when scaling the frame
        # here is the style setting for it: wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE
        # wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER will disable canvas resize.
        frame = wx.Frame(None, size=(500, 500), title="Test", style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)
        canvas = Sketch(frame)
        canvas.debug = 2
        frame.Show()
        app.MainLoop()

        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime').reverse_order()
        stats.print_stats()


    # main()
    codingDebug()
