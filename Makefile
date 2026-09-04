CXX      = g++
CXXFLAGS = -O2 -std=c++17 -Wall

all: exec_engine

exec_engine: exec_engine.cpp
	$(CXX) $(CXXFLAGS) -o exec_engine exec_engine.cpp

fonts:
	mkdir -p fonts
	ln -sf /usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf \
	       fonts/DejaVuSansMono-Bold.ttf

clean:
	rm -f exec_engine

.PHONY: all clean fonts
