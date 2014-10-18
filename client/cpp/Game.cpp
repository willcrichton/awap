#include <iostream>
#include <sstream>
#include "Game.h"

/*
  Game.cpp - Responsible for generating moves to give to client.py         
  Moves via stdout in the form of "# # # #" (block index, # rotations, x, y)
  Important function is find_move, which should contain the main AI
*/


Move Game::find_move()
{
  //To Be Implemented
  Move move = {0, 0, 0, 0};
  
  return move;
}

bool Game::my_turn()
{
  return turn == my_number;
}


void Game::interpret_data(args args)
{
  my_number = args.my_number;
  dimension = args.dimension;
  turn = args.turn;
  blocks = args.blocks;
  grid = args.grid;
  bonus_squares = args.bonus_squares;
}



bool Game::can_place(block b, Point p)
{
  bool onAbsCorner = false;
  bool onRelCorner = false;
  int N = dimension - 1;

  Point corners[4] ={ Point(0,0), Point(N, 0), Point(0, N), Point(N, N) };
  Point corner = corners[my_number];
  for(int i = 0; i < b.size(); i++){
    Point q = b[i].add(p);
    int x = q.x;
    int y = q.y;
    if (x > N || x < 0 || y < 0 || y > N || grid[x][y] >= 0
	|| (x > 0 && grid[x-1][y] == my_number)
	|| (y > 0 && grid[x][y-1] == my_number)
	|| (x < N && grid[x+1][y] == my_number)
	|| (y < N && grid[x][y+1] == my_number)) {
      return false;
    }
    
    onAbsCorner = onAbsCorner || q.eq(corner);
    onRelCorner = onRelCorner
      || (x > 0 && y > 0 && grid[x-1][y-1] == my_number)
      || (x < N && y > 0 && grid[x+1][y-1] == my_number)
      || (x > 0 && y < N && grid[x-1][y+1] == my_number)
      || (x < N && y < N && grid[x+1][y+1] == my_number);
  }
  
  return !((grid[corner.x][corner.y] < 0 && !onAbsCorner) || (!onAbsCorner && !onRelCorner));      
}


block Game::rotate_block(block b, int num_rotations)
{
  block newBlock;
  for(int i = 0; i < b.size(); i++){
    newBlock.push_back(b[i].rotate(num_rotations));
  }
  return newBlock;
}


//Currently returns 0, you might want to modify this yourself!
int Game::score_move(block b, Point p)
{
  int score = 0;
  int blockSize = b.size();
  int bonus_points = 0;
  int N = dimension;
  
  for(int i = 0; i < blockSize; i++){
    Point s = b[i].add(p);
    for(int j = 0; j < bonus_squares.size(); j++){
      if(s.eq(bonus_squares[j])){
	bonus_points += 2;
      }
      area_enclosed = max(area_enclosed, -1 * (s.distance(Point(N/2, N/2))));
    }
  }
  
  return score;
}

string Game::toString(Move m)
{
  stringstream ss;
  ss << m.index << " " << m.rotations << " " << m.x << " " << m.y;
  return ss.str();
}
