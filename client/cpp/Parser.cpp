#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include <iostream>
#include "Parser.h"
#include <typeinfo>

using namespace rapidjson;


args load_json(char* BUF)
{
  Document d;  
  args parsedArgs;
  std::cin.get (BUF, 8192);
  StringStream s(BUF);
  d.ParseStream(s);
  
  assert(d.IsObject());
  
  if(d.HasMember("error"))
    {
      parsedArgs.error = d["error"].GetString();
      parsedArgs.has_error = true;
      return parsedArgs;
    }
  
  
  if(d.HasMember("url"))
    {
      parsedArgs.url = d["url"].GetString();
      cout << "Parsed Url" << "\n";
    }
  
  if(d.HasMember("turn"))
    {
      parsedArgs.turn = d["turn"].GetInt();
      cout << "Parsed turn" << "\n";
    }
  
  if(d.HasMember("number"))
    {
      parsedArgs.my_number = d["number"].GetInt();
      cout << "Parsed number" << "\n";
    }

  if(d.HasMember("move"))
    {
      if(d["move"] == 1)
	{
	  parsedArgs.turn = 1;
	}
      parsedArgs.turn = 0;
    }
  
  if(d.HasMember("board"))
    {
      Value& boardTree = d["board"];
      assert(boardTree.IsObject());
      if(boardTree.HasMember("bonus_squares"))
      	{
      	  vector<Point> bonus_squares;
      	  const Value& bonus = boardTree["bonus_squares"];      

      	  for(int i = 0; i < bonus.Size(); i++)
      	    {
	      bonus_squares.push_back(Point(bonus[i][0u].GetInt(), bonus[i][1].GetInt()));
	      bonus_squares[i].print();
      	    }
      	  parsedArgs.bonus_squares = bonus_squares;
      	}

      if(boardTree.HasMember("dimension"))
      	{
      	  parsedArgs.dimension = boardTree["dimension"].GetInt();
      	}
      
      if(boardTree.HasMember("grid"))
	{
	  vector<vector<int> > grid;
	  const Value& currGrid = boardTree["grid"];
	  
	  for(int i = 0; i < currGrid.Size(); i++)
	    {
	      vector<int> row;
	      for(int j = 0; j < currGrid[i].Size(); j++)
		{
		  row.push_back(currGrid[i][j].GetInt());
		}
	      grid.push_back(row);
	    }
	  parsedArgs.grid = grid;
	}

    }  
  
  return parsedArgs;
}

