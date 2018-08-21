# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# StarMap2A.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents the data for a galactic map layout, used to auto generate
# a Galactic Map with the Admin program
# ---------------------------------------------------------------------------

numEmpires = 3

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
                    '.': (None, None)
                    }

genSystemsData =[
    'Aaaaa.a.aeEeA',
    'AaBaa.b.afFfA',
    '.a.a.b.b.a.a.',
    'aAa.A.X.A.aAa',
    '.a.a.b.b.a.a.',
    'AdDda.b.aaBaA',
    'AcCca.a.aaaaA'
    ]

defaultIndustry = [[1,'16'],# basic design center
                   [1,'13'],# basic simulation center
                   [20,'43'],# basic research center
                   [3,'34'],# basic shipyard
                   [3,'37']# basic military installation
                   ]
citiesUsed = 0

startingTech = [0,1,2,3,5,6,7,8,10,11,12,13,15,16,17,18,19,20,21,22,23,24,25,26,30,38,39,40,41,42,71,77]