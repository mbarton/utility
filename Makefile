# Das Uber Makefile
#  Utility makefile to actually compile things easily
#  Stick all your cpp files in src then fiddle with the
#  variables below to add includes and libs
#  Set the binary name and voila, that binary will be produced

# BEGIN CUSTOMISATION
BINARY_NAME=groovers
CXX?=g++
CFLAGS?=-Wall -Werror
INCLUDE_DIRS=ThirdParty/bass/include
LIB_DIRS=ThirdParty/bass/lib
LD_FLAGS=-lbass
# END CUSTOMISATION

SOURCES=$(wildcard src/*.cpp)
OBJECTS=$(subst src,build,$(SOURCES:.cpp=.o))

all:
	-mkdir -p build
	$(MAKE) $(BINARY_NAME)

-include $(OBJECTS:.o=.d)

build/%.o: src/%.cpp
	$(CXX) $(CFLAGS) -I$(INCLUDE_DIRS) -c $< -o $@
	@$(CXX) -MM $(CFLAGS) -I$(INCLUDE_DIRS) $< > build/$*.d
	@mv -f build/$*.d build/$*.d.tmp
	@sed -e 's|.*:|build/$*.o:|' < build/$*.d.tmp > build/$*.d
	@sed -e 's/.*://' -e 's/\\$$//' < build/$*.d.tmp | fmt -1 | \
	  sed -e 's/^ *//' -e 's/$$/:/' >> build/$*.d
	@rm -f build/$*.d.tmp

$(BINARY_NAME): $(OBJECTS)
	$(CXX) $(CFLAGS) -L$(LIB_DIRS) $(LD_FLAGS) $(OBJECTS) -o $@

clean:
	rm -rf build/*
	rm -rf $(BINARY_NAME)