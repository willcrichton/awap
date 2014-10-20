#include <iostream>
#include "parser.h"

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

using namespace rapidjson;

args load_json(StringStream ss)
{
  Document d;  
  args parsedArgs;
  d.ParseStream(ss);
  
  if(!d.IsObject()){
    return parsedArgs;
  }
  
  if(d.HasMember("error"))
    {
      parsedArgs.error = d["error"].GetString();
      parsedArgs.has_error = true;
      return parsedArgs;
    }
  
  
  if(d.HasMember("url"))
    {
      parsedArgs.url = d["url"].GetString();
    }
  
  if(d.HasMember("turn"))
    {
      parsedArgs.turn = d["turn"].GetInt();
    }
  
  if(d.HasMember("number"))
    {
      parsedArgs.my_number = d["number"].GetInt();
    }

  if(d.HasMember("turn"))
    {
      parsedArgs.turn = d["turn"].GetInt();
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

  if(d.HasMember("blocks"))
    {
      Value& players = d["blocks"];
      assert(players.IsArray());
      vector<vector<block> > blocks;
      for(int i = 0; i < players.Size(); i++)
  	{
	  assert(players[i].IsArray());
	  vector<block> ithPlayerBlocks;
	  for(int j = 0; j < players[i].Size(); j++)
	    {
	      block piece;
	      assert(players[i][j].IsArray());
	      for(int k = 0; k < players[i][j].Size(); k++){
		Value& blok = players[i][j][k];
		assert(blok.IsObject());
		piece.push_back(Point(blok["x"].GetInt(), blok["y"].GetInt()));		
	      }
	      ithPlayerBlocks.push_back(piece);
	    }
	  blocks.push_back(ithPlayerBlocks);
	}
      parsedArgs.blocks = blocks;

    } 

  return parsedArgs;
}

