# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# StarMap4A.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents the data for a galactic map layout, used to auto generate
# a Galactic Map with the Admin program
# ---------------------------------------------------------------------------

numEmpires = 5

genSystemsLegend = {'a': ('1', 10),
                    'b': ('1', 15),
                    'A': ('1', 20),
                    'B': ('1', 30),
                    'X': ('1', 50),
                    'c': ('2', 10),
                    'd': ('2', 15),
                    'C': ('2', 20),
                    'D': ('2', 40),
                    'e': ('3', 10),
                    'f': ('3', 15),
                    'E': ('3', 20),
                    'F': ('3', 40),
                    'g': ('4', 10),
                    'h': ('4', 15),
                    'G': ('4', 20),
                    'H': ('4', 40),
                    'i': ('5', 10),
                    'j': ('5', 15),
                    'I': ('5', 20),
                    'J': ('5', 40),
                    '.': (None, None)
                    }

genSystemsData =[
    'acCcaaBaaeEea',
    'adDda.A.afFfa',
    'aa.a.b.b.a.aa',
    'ABA.A.X.A.ABA',
    'aa.a.b.b.a.aa',
    'ajJja.A.ahHha',
    'aiIiaaBaagGga'
    ]

defaultIndustry = [[1,'16'],# basic design center
                   [1,'13'],# basic simulation center
                   [20,'43'],# basic research center
                   [3,'34'],# basic shipyard
                   [3,'37']# basic military installation
                   ]
citiesUsed = 0

startingTech = [0,1,2,3,5,6,7,8,10,11,12,13,15,16,17,18,19,20,21,22,23,24,25,26,30,38,39,40,41,42,71,77]