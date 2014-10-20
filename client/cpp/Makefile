#Compiler:
CC=g++

all: build game

build:
	mkdir build

game: build/main.o build/game.o build/point.o build/parser.o
	$(CC) build/main.o build/point.o build/parser.o build/game.o -o game

build/point.o: point.cpp
	$(CC) -c point.cpp -o build/point.o

build/game.o: game.cpp
	$(CC) -c game.cpp -o build/game.o

build/parser.o: parser.cpp 
	$(CC) -c parser.cpp -o build/parser.o

build/main.o: main.cpp
	$(CC) -c main.cpp -o build/main.o

clean:
	rm -rf *o game build
