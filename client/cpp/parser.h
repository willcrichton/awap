#ifndef PARSER
#define PARSER

#include "rapidjson/document.h"
#include "game.h"

using namespace rapidjson;

args load_json(StringStream ss);

#endif /*PARSER*/
