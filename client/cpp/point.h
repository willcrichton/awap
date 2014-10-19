//Simple Point class that supports equality, addition, and rotation
#ifndef POINT
#define POINT

class Point
{
  
public:
  int x, y; 
  Point(int xval = 0, int yval = 0);
  bool eq(Point p);
  
  Point add(Point p);
  int distance(Point p);
  Point rotate(int num_rotations);

  void print();
};

#endif /*POINT*/
