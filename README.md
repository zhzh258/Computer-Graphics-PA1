#
python ./Sketch.py

# 
- Zhaozhan Huang
- U03088498
- CS680 Assignment 1

## Modified methods

- In Sketch.py: 
```python
Interrupt_MouseL()
Interrupt_MouseR()
drawPoint()
drawLine()
drawTriangle()
```

- In ColorType.py
```python
__add__()
__sub__()
__rmul__()
__truediv__()
__floordiv__()
```
## Requirements 1
Use Bresenham Algorithm. Divide the question into into two cases:
1. abs(m) <= 1
- In this cased, we use x-based Bresenham's. 
- We make sure that p1.x \< p2.x.
- The $ \Delta y $ depends on p1.y and p2.y
2. abs(m) > 1
- In this cased, we use y-based Bresenham's.
- We make sure that p1.y \< p2.y
- The $ \Delta x $ depends on p1.x and p2.x

> The doSmooth and doAA are also included in drawLine()

## Requirements 2
Use scan-fill Algorithm. 
- Divide the triangle. Make p1.y \< p2.y \< p3.y. The triangle is divided in to two parts: above y2 and below y2.
- Scan by y. First from y1 to y2. Then from y2 to y3.
- For doSmooth, we use linear interpolation.
Use linear interpolation to get p13: the point on p1p3. (First step + Second step)
Use linear interpolation to get p12: the point on p1p2. (First step)
Use linear interpolation to get p23: the point on p1p2. (Second step)
Then do linear interpolation between p13 + p12/p23

## Requirements 3
- I create a rectangle around the triangle by analyzing y_min, y_max, x_min, x_max.
And then do a mapping from the texture to the rectangle, based on their width and height.
- (x, y) is the coordinate in rectangle
- (u, v) is the coordinate in texture
- For the doSmooth, I use bilinear interpolation by considering ceil(u), ceil(v), floor(u), floor(v)

## Requirements 4
I only implemented the anti-aliasing for lines. Please see "TODO 4" part (code + comment) in drawLine(). And the print() output.



