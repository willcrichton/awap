#ifndef GAME
#define GAME

#include <vector>
#include "Point.h"

using namespace std;

typedef vector<Point> block;

struct Move{
  int index;
  int rotations;
  int x;
  int y;
};

struct args{
  vector<block> blocks;
  string url;
  vector<vector<int> > grid;
  vector<Point> bonus_squares;
  int my_number;
  int dimension;
  int turn;
  bool has_error;
  string error;
};
 
class Game{
 public:
  vector<block> blocks;
  vector<vector<int> > grid;
  vector<pair<Point, int> > bonus_squares;
  int my_number;// = -1;
  int dimension;// = -1;
  int turn;// = -1;
 
  Game(string args);
  Move find_move();

 private:
  int area_enclosed;

  void interpret_data(string args);
  bool can_place(block b, Point p);
  block rotate_block(block b, int num_rotations);
  int score_move(block b, Point p);

  string toString(Move m);


};
#endif /* GAME */
