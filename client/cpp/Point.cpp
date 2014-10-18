//Simple Point class that supports equality, addition, and rotation

#include <cmath>
#include <iostream>
#include "Point.h"

Point::Point(int xval, int yval)
{
   x = xval; 
   y = yval;
}

bool Point::eq(Point p)
{
  return x == p.x && y == p.y;
}

Point Point::add(Point p)
{
  return Point(x + p.x, y + p.y);
}

//Manhattan metric
int Point::distance(Point p)
{
  return std::abs(x - p.x) + std::abs(y-p.y);
}

Point Point::rotate(int num_rotations)
{
  switch(num_rotations){
  case 1: return Point(-y, x); break;
  case 2: return Point(-x, y); break;
  case 3: return Point(y, -x); break;
  default: return Point(x, y); break;
  }
}

//Modify if you want a newline
void Point::print()
{
  std::cout << "(" << x << "," << y << ")";
}
