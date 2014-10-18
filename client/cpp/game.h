#ifndef GAME
#define GAME

#include <vector>
#include "point.h"

using namespace std;

typedef vector<Point> block;

struct Move{
  int index;
  int rotations;
  int x;
  int y;
};

struct args{
  vector<vector<block> > blocks;
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
  Game() {};

  vector<block> blocks;
  vector<vector<int> > grid;
  vector<Point> bonus_squares;
  int my_number;
  int dimension;
  int turn;
 
  

  Move find_move();
  bool my_turn();
  void interpret_data(args args);

 private:
  int area_enclosed;
  bool can_place(block b, Point p);
  block rotate_block(block b, int num_rotations);
  int score_move(block b, Point p);

  string toString(Move m);


};
#endif /* GAME */
