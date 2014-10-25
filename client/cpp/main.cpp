#include <iostream>
#include "game.h"
#include "parser.h"
#include "point.h"

int main(){
  Game game;
  while (true){
    std::string buf;
    if (!getline(std::cin, buf)) continue;

    StringStream ss(buf.c_str());
    args params = load_json(ss);
    if(params.has_error) {
      if (params.error.compare("ignore")) {
        std::cout << "DEBUG error " << params.error << "\n";
      }

      continue;
    }

    game.interpret_data(params);

    if(game.my_turn()) {
      Move m = game.find_move();
      cout << m.index << " " << m.rotations << " "  << m.x <<  " " << m.y << "\n";
    }
  }
  return 0;
}
