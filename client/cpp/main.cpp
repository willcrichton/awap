#include <iostream>
#include "Point.h"
#include "Game.h"
#include "Parser.h"

int main(){
  char BUF[8192] = { 0 };
  std::cin.get (BUF, 8192);
  Game game;
  while (!cin.fail()){
    std::cin.ignore(); //Ignore \n.
    StringStream ss(BUF);
    args params = load_json(ss); 
    if(params.has_error)
      {
	cout << "Error: " << params.error << "\n";
      }
    
    game.interpret_data(params);
    if(game.my_turn())
      {
	Move m = game.find_move();
	cout << m.index << " " << m.rotations << " "  << m.x <<  " " << m.y << "\n";
      }
    std::cin.get (BUF, 8192);
  }
  return 0;
}
