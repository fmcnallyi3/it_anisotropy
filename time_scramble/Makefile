SHELL         = /bin/sh
CXX           = g++
CXXFLAGS      = -g -Wall -O2 -DSDST_V3 -I. $(ICETRAY_FLAGS) $(ROOT_FLAGS) $(HP_FLAGS) $(ASTRO_FLAGS)
LD            = g++
LDFLAGS       = -O2 $(ICETRAY_LIBS) $(ROOT_LIBS) $(HP_LIBS) $(ASTRO_LIBS)

ROOT_FLAGS    = $(shell root-config --cflags)
ROOT_LIBS     = $(shell root-config --libs)

ICETRAY_FLAGS = $(shell icetray-config astro --cflags)
ICETRAY_LIBS  = $(shell icetray-config astro --ldflags)

ICEREC = /data/user/fmcnally/offline/V04-08-00

ASTRO_FLAGS = -I$(ICEREC)/src/astro/public -I$(I3_PORTS)/include/slalib-0.0
ASTRO_LIBS  = -L$(ICEREC)/build/lib -lastro -lsla

HP_FLAGS = -I$(ICEREC)/src/healpix-cxx/public -I$(I3_PORTS)/include
HP_LIBS  = -L$(ICEREC)/build/lib -lhealpix-cxx -lcxxsupport -L$(I3_PORTS)/lib -lcfitsio

#BOOST_FLAGS = -I$(I3_PORTS)/include/boost-1.38.0
#BOOST_LIBS = -L$(I3_PORTS)/lib/boost-1.38.0

.PHONY: all clean

all: TimeScramble


TimeScramble: TimeScramble.o SimpleDST.o
	$(LD) $^ $(LDFLAGS) -o $@

%.o:%.cc
	$(CXX) $(CXXFLAGS) -c $^

clean:
	rm -f *.o a.out TimeScramble

