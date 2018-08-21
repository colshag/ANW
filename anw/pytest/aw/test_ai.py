# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# test_ai.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents an AI Player in ANW
# ---------------------------------------------------------------------------
import os
from anw.admin import generate
from anw.aw import galaxy
from anw.func import globals

class TestAI(object):
    
    def setup_class(self):
        osPath = os.getcwd()
        self.dataPath = osPath[:-7] + '/Data/'
        self.myGalaxy = None
        self.myEmpire = None
        self.generate = None
        self.mySystem = None
        self.myAI = None
        self.generate = generate.GenerateGalaxy()
        self.generate.genGalaxy(self.dataPath, 'starMap4A.map')
        self.myGalaxy = self.generate.getGalaxy()
        self.myEmpire = self.myGalaxy.empires['1']
        self.myAI = self.myEmpire.myAIPlayer
    
    def testGenGalaxy(self):
        """Can entire Galaxy Object be generated"""
        assert self.myGalaxy.xMax == 14 * globals.systemSize
        assert self.myGalaxy.yMax == 8 * globals.systemSize
        assert self.myEmpire.ai == 1
        assert self.myAI != None
        assert self.myAI.id != ''
        assert self.myAI.type != ''
        assert self.myAI.name != ''
        assert self.myAI.tech != 0
        assert self.myEmpire.designsLeft == 1
        self.myAI.updateRound()
        
    def testDoMyTech(self):
        """An AI will research technology each round"""
        assert self.myEmpire.rpUsed == 0
        assert self.myEmpire.rpAvail == 300 #already did turn for round 2 and end of round 1
        keys1 = self.myEmpire.techOrders.keys()
        self.myAI.doMyTech()
        assert self.myEmpire.rpUsed == 300
        assert self.myEmpire.rpAvail == 0 #new round of tech orders
        keys2 = self.myEmpire.techOrders.keys()
        assert len(keys2) > len(keys1)
    
    def testDoMySystemBuilds(self):
        """Every system needs to go through its system build orders based on earlier assessments"""
        self.myAI.reset()
        self.myAI.assessSituation()
        total1 = self.getTotalIndustry()
        total2 = 0
        for systemID in self.myAI.mySystemOrders.keys():
            mySystem = self.myGalaxy.systems[systemID]
            assert mySystem.myIndustry.keys() > 0
            self.myAI.buildNewIndustry(mySystem, 'misc')
            for key, num in mySystem.myIndustry.iteritems():
                total2 += num
        assert total1 < total2
    
    def testRemoveAllIndustry(self):
        """System will remove all industry for system"""
        self.myAI.myEmpire.techTree['107'].complete = 1
        self.myAI.reset()
        self.myAI.assessSituation()
        total1 = self.getTotalIndustry()
        total2 = 0
        for systemID in self.myAI.mySystemOrders.keys():
            mySystem = self.myGalaxy.systems[systemID]
            assert mySystem.myIndustry.keys() > 0
            self.myAI.removeAllIndustry(mySystem)
            for key, num in mySystem.myIndustry.iteritems():
                total2 += num
        assert total1 > total2
        
    def getTotalIndustry(self):
        """return the total industry for ai player from all systems"""
        total = 0
        for systemID in self.myAI.mySystemOrders.keys():
            mySystem = self.myGalaxy.systems[systemID]
            assert mySystem.myIndustry.keys() > 0
            for key, num in mySystem.myIndustry.iteritems():
                total += num
        return total
                