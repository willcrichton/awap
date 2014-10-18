all:
	solver

solver: main.o Game.o Point.o Parser.o

main.o: main.cpp
	g++ -c main.cpp

Point.o: Point.cpp
	g++ -c Point.cpp

Parser.o: Parser.cpp
	g++ -c Parser.cpp

Game.o: Game.cpp
	g++ -c Game.cpp

clean:
	rm -rf *o solver
