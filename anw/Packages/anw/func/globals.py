# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# globals.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Store Global Variables
# ---------------------------------------------------------------------------
try:
    from pandac.PandaModules import Vec4
except:
    pass
currentVersion = '0.14.0'
currentVersionShort = 'master'
currentVersionTag = '.2'
serverMode = 0

maxShipsPerBattle = 120

try:
    colors = {'yellow':Vec4(0.922,0.910,0.047,1),
          'orange':Vec4(0.996, 0.359, 0, 1),
          'green':Vec4(0.242, 0.973, 0.309, 1),
          'cyan':Vec4(0, 0.758, 0.883, 1),
          'red':Vec4(0.93, 0.08, 0.08, 1),
          'pink':Vec4(0.99, 0.61, 0.688, 1),
          'white':Vec4(0.99, 0.961, 0.969, 1),
          'ltpurple':Vec4(0.93, 0.563, 0.977, 1),
          'blue':Vec4(0.223, 0.6445, 0.95, 1),
          'brown':Vec4(0.7059, 0.396, 0.192, 1),
          
          'blood':Vec4(0.61, 0, 0, 1),
          'dkgrey':Vec4(0.234, 0.234, 0.234, 1),
          'dkpurple':Vec4(110, 4, 122, 1),
          'dkblue':Vec4(0.43, 0.05, 0.531, 1),
          'black':Vec4(0.04, 0.04, 0.04, 1),
          'dkyellow':Vec4(0.586, 0.586, 0, 1),
          'dkgreen':Vec4(0.024,0.239,0.043,1),
          
          'guiblue1':Vec4(0,0.4,0.91,1),
          'guiblue2':Vec4(0,0.255,0.58,1),
          'guiblue3':Vec4(0,0.114,0.255,1),
          'guigrey':Vec4(0.549,0.549,0.549,1),
          'guiyellow':Vec4(0.922,0.910,0.047,1),
          'guired':Vec4(1,0,0,1),
          'guigreen':Vec4(0,1,0,1),
          'guiblack':Vec4(0,0,0,1),
          'guiwhite':Vec4(1,1,1,1),
          
          'mod0':Vec4(0.6,0.8,0.9,1),
          'mod1':Vec4(0.8,0.8,0,1),
          'mod2':Vec4(1,0.5,0.2,1),
          'mod3':Vec4(0.5,0.6,0.6,1),
          'mod4':Vec4(0.8,0,1,1),
          'mod5':Vec4(0.6,0.8,0.1,1),
          'mod6':Vec4(1,0.5,0.5,1),
          'mod7':Vec4(0,0.8,0.9,1),
          'mod8':Vec4(0.4,0.2,0,1)
          }
except:
    colors = {}

empires = [{'id':'0', 'name':'Neutral', 'color1':'white', 'color2':'black','CR':0, 'ai':1},
           {'id':'1', 'name':'Yellow Empire', 'color1':'yellow', 'color2':'black','CR':0},
           {'id':'2', 'name':'Brown Empire', 'color1':'brown', 'color2':'black','CR':0},
           {'id':'3', 'name':'Green Empire', 'color1':'green', 'color2':'black','CR':0},
           {'id':'4', 'name':'Blue Empire', 'color1':'blue', 'color2':'black','CR':0},
           {'id':'5', 'name':'Pink Empire', 'color1':'pink', 'color2':'dkpurple','CR':0},
           {'id':'6', 'name':'Red Empire', 'color1':'red', 'color2':'black','CR':0},
           {'id':'7', 'name':'Cyan Empire', 'color1':'cyan', 'color2':'black','CR':0},
           {'id':'8', 'name':'Fire Empire', 'color1':'yellow', 'color2':'blood','CR':0},]


marinesPerTransport = 10

alternateTargetRadius = 4

# simulator interval value
intervalValue = 0.02

resourceNames = ['AL','EC','IA']
resourceColors = {'CR':'guigreen', 'AL':'guiblue1', 'EC':'guiyellow', 'IA':'guired'}
# amount of resources required to add one city to a system
addCityResource = {'CR':5000.0, 'AL':1000.0, 'EC':250.0, 'IA':100.0}

# amount to modify the resource focus of one city
updateCityResource = {'CR':500.0, 'AL':0.0, 'EC':0.0, 'IA':0.0}

# amount of resources one city will generate without bonuses
cityCRGen = 200.0
cityALGen = 20.0
cityECGen = 10.0
cityIAGen = 5.0

# default value of resources in credits [AL,EC,IA]
resourceCreditValue = [20.0,40.0,80.0]

AL = resourceCreditValue[0]/2
EC = resourceCreditValue[1]/2
IA = resourceCreditValue[2]/2

systemSize = 6
techSize = 3

# armor modifiers
reflectiveArmorModifier = 0.5
impactArmorModifier = 0.5

# quadrants
quadAngles = {'fore':0.0, 'star':90.0, 'aft':180.0, 'port':270.0}
angleQuads = {0.0:'fore', 270.0:'port', 180.0:'aft', 90.0:'star'}

# components
weaponComponent = '64'

# max movement
maxAccel = 5.0
maxRotation = 60.0
droneAccel = 5.0
droneRotation = 60.0

targetPreference = {'INT':['ECA','HCA','BCA'],
                    'COR':['LAS','HAS','BAS']}

targetPrefDisplay = {'INT':'drone carriers',
                    'COR':'assault ships'} 

# hardpoints
hardPoints = {'SCT':{'fore-1':[0,8],
                     'aft-1':[180,7],
                     'port-1':[225,7],
                     'star-1':[135,7]
                     },
              'INT':{'fore-1':[0,8],
                     'aft-1':[180,8],
                     'port-1':[270,8],
                     'star-1':[90,8]
                     },
              'COR':{'fore-1':[30,4],'fore-2':[330,4],
                     'aft-1':[150,4],'aft-2':[210,4],
                     'port-1':[120,16],'port-2':[120,12],
                     'star-1':[240,16],'star-2':[240,12]
                     },
              'HCO':{'fore-1':[30,4],'fore-2':[330,4],
                     'aft-1':[150,4],'aft-2':[210,4],
                     'port-1':[120,16],'port-2':[120,12],
                     'star-1':[240,16],'star-2':[240,12]
                     },
              'FRG':{'fore-1':[0,30],'aft-1':[225,8],'port-1':[340,12],'star-1':[20,12],
                     'fore-2':[10,30],'aft-2':[135,8],'port-2':[330,4],'star-2':[30,4],
                     'fore-3':[350,30],'aft-3':[180,8],'port-3':[225,26],'star-3':[135,26]
                     },
              'BFR':{'fore-1':[0,35],'aft-1':[225,8],'port-1':[335,18],'star-1':[25,18],
                     'fore-2':[10,35],'aft-2':[135,8],'port-2':[330,10],'star-2':[30,10],
                     'fore-3':[350,35],'aft-3':[180,8],'port-3':[225,30],'star-3':[135,30]
                     },
              'DST':{'fore-1':[5,46],'aft-1':[180,20],'port-1':[337,20],'star-1':[23,20],
                     'fore-2':[355,46],'aft-2':[200,20],'port-2':[330,14],'star-2':[30,14],
                     'fore-3':[13,46],'aft-3':[220,20],'port-3':[315,4],'star-3':[45,4],
                     'fore-4':[347,46],'aft-4':[180,30],'port-4':[225,30],'star-4':[135,30]
                     },
              'CRU':{'fore-1':[5,50],'aft-1':[180,40],'port-1':[260,40],'star-1':[100,40],
                     'fore-2':[355,50],'aft-2':[200,30],'port-2':[250,42],'star-2':[110,42],
                     'fore-3':[13,45],'aft-3':[220,30],'port-3':[235,44],'star-3':[125,44],
                     'fore-4':[347,45],'aft-4':[180,10],'port-4':[260,18],'star-4':[100,18]
                     },
              'HCU':{'fore-1':[7,50],'aft-1':[180,40],'port-1':[260,40],'star-1':[100,40],
                     'fore-2':[353,50],'aft-2':[200,30],'port-2':[250,42],'star-2':[110,42],
                     'fore-3':[16,45],'aft-3':[220,30],'port-3':[235,44],'star-3':[125,44],
                     'fore-4':[346,45],'aft-4':[200,40],'port-4':[255,18],'star-4':[105,18],
                     'fore-5':[0,50],'aft-5':[220,40],'port-5':[270,16],'star-5':[90,16]
                     },
              'BCU':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[270,16],'star-5':[90,16]
                     },
              'DRN':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[270,16],'star-5':[90,16],
                     'fore-6':[0,16],'aft-6':[180,16],'port-6':[270,16],'star-6':[90,16]
                     },
              'SDN':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[270,16],'star-5':[90,16],
                     'fore-6':[0,16],'aft-6':[180,16],'port-6':[270,16],'star-6':[90,16],
                     'fore-7':[0,16],'aft-7':[180,16],'port-7':[270,16],'star-7':[90,16]
                     },
              'ECA':{'fore-1':[10,15],'aft-1':[170,15],'port-1':[320,25],'star-1':[40,25],
                     'fore-2':[350,15],'aft-2':[190,15],'port-2':[260,20],'star-2':[260,20],
                     'fore-3':[0,15],'aft-3':[180,15],'port-3':[210,25],'star-3':[150,25]
                     },
              'HCA':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16]
                     },
              'BCA':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[270,16],'star-5':[90,16]
                     },
              'LAS':{'fore-1':[10,15],'aft-1':[170,15],'port-1':[320,25],'star-1':[40,25],
                     'fore-2':[350,15],'aft-2':[190,15],'port-2':[260,20],'star-2':[260,20],
                     'fore-3':[0,15],'aft-3':[180,15],'port-3':[210,25],'star-3':[150,25]
                     },
              'HAS':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16]
                     },
              'BAS':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[270,16],'star-5':[90,16]
                     },
              'LWP':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[270,16],'star-5':[90,16]
                     },
              'HWP':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[270,16],'star-5':[90,16],
                     'fore-6':[0,16],'aft-6':[180,16],'port-6':[270,16],'star-6':[90,16],
                     'fore-7':[0,16],'aft-7':[180,16],'port-7':[270,16],'star-7':[90,16]
                     },
              'BWP':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[270,16],'star-1':[90,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[270,16],'star-2':[90,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[270,16],'star-3':[90,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[270,16],'star-4':[90,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[270,16],'star-5':[90,16],
                     'fore-6':[0,16],'aft-6':[180,16],'port-6':[270,16],'star-6':[90,16],
                     'fore-7':[0,16],'aft-7':[180,16],'port-7':[270,16],'star-7':[90,16],
                     'fore-8':[0,16],'aft-8':[180,16],'port-8':[270,16],'star-8':[90,16],
                     'fore-9':[0,16],'aft-9':[180,16],'port-9':[270,16],'star-9':[90,16]
                     }
              }
              
# limitations
componentLimitations = {'warship':['SES','PES','UES'],
                        'drone':['SMP','PMP','UMP','SJD','PJD','UJD','SES','PES','UES',
                                 'SSE','PSE','USE','SRT','PRT','URT','SRX','PRX','URX','CSE','CRT'],
                        'platform':['CSE','CRT'],
                        'carrier':['LNTA','MNTA','HNTA','LFTA','MFTA','HFTA','LPTA',
                                   'MPTA','HPTA','LGGA','MGGA','HGGA','LACA','MACA',
                                   'HACA','LRGA','MRGA','HRGA','LNMA','MNMA','HNMA',
                                   'LFMA','MFMA','HFMA','LPMA','MPMA','HPMA','SES','PES','UES','CSE','CRT'],
                        'assault':['LNTA','MNTA','HNTA','LFTA','MFTA','HFTA','LPTA',
                                     'MPTA','HPTA','LGGA','MGGA','HGGA','LACA','MACA',
                                     'HACA','LRGA','MRGA','HRGA','LNMA','MNMA','HNMA',
                                     'LFMA','MFMA','HFMA','LPMA','MPMA','HPMA',
                                     'SES','PES','UES','CSE','CRT']}

weaponLimitations = {'warship':['LNL','MNL','HNL','LFL','MFL','HFL','LPL','MPL','HPL'],
                     'drone':['LNL','MNL','HNL','LFL','MFL','HFL','LPL','MPL','HPL',
                              'APG','AFC','APC','AGG','AAC','ARG'],
                     'platform':[],
                     'carrier':['LPG','MPG','HPG','LFC','MFC','HFC','LPC','MPC','HPC',
                                'LNT','MNT','HNT','LFT','MFT','HFT','LPT','MPT','HPT',
                                'LGG','MGG','HGG','LAC','MAC','HAC','LRG','MRG','HRG',
                                'LNM','MNM','HNM','LFM','MFM','HFM','LPM','MPM','HPM'],
                     'assault':['LNL','MNL','HNL','LFL','MFL','HFL','LPL','MPL','HPL',
                                  'LPG','MPG','HPG','LFC','MFC','HFC','LPC','MPC','HPC',
                                  'LNT','MNT','HNT','LFT','MFT','HFT','LPT','MPT','HPT',
                                  'LGG','MGG','HGG','LAC','MAC','HAC','LRG','MRG','HRG',
                                  'LNM','MNM','HNM','LFM','MFM','HFM','LPM','MPM','HPM']}

# fleet Ranks
shipRank0 = 'Rookie'
shipRank1 = 'Cadet'
shipRank2 = 'Ensign'
shipRank3 = 'Lieutenant'
shipRank4 = 'Captain'
shipRank5 = 'Commander'
shipRank6 = 'Admiral'
shipRank7 = 'Legendary'

# army Ranks
armyRank0 = 'Green'
armyRank1 = 'Trained'
armyRank2 = 'Veteran'
armyRank3 = 'Elite'
armyRank4 = 'Legend'

# any existing modifiers from targeting computers)
rankMods = {shipRank0:{'weaptarget':200,'retarget':400,'toHit':50,'kWtoSPfactor':0.3,'targetLock':0,'missileSpeed':0.8,'droneDodge':20},
            shipRank1:{'weaptarget':150,'retarget':360,'toHit':60,'kWtoSPfactor':0.6,'targetLock':0,'missileSpeed':1.1,'droneDodge':30},
            shipRank2:{'weaptarget':50,'retarget':320,'toHit':70,'kWtoSPfactor':0.7,'targetLock':0,'missileSpeed':1.2,'droneDodge':40},
            shipRank3:{'weaptarget':40,'retarget':280,'toHit':80,'kWtoSPfactor':0.8,'targetLock':10,'missileSpeed':1.3,'droneDodge':50},
            shipRank4:{'weaptarget':30,'retarget':240,'toHit':90,'kWtoSPfactor':0.9,'targetLock':20,'missileSpeed':1.4,'droneDodge':60},
            shipRank5:{'weaptarget':20,'retarget':200,'toHit':100,'kWtoSPfactor':1.0,'targetLock':30,'missileSpeed':1.5,'droneDodge':70},
            shipRank6:{'weaptarget':10,'retarget':160,'toHit':100,'kWtoSPfactor':1.0,'targetLock':50,'missileSpeed':2.0,'droneDodge':80},
            shipRank7:{'weaptarget':5,'retarget':120,'toHit':100,'kWtoSPfactor':2.0,'targetLock':70,'missileSpeed':3.0,'droneDodge':90},
            
            armyRank0:{'bonus':0},
            armyRank1:{'bonus':100},
            armyRank2:{'bonus':400},
            armyRank3:{'bonus':800},
            armyRank4:{'bonus':1200}
            }

# kW to shield point conversion factor: 0.5 means 1kW makes 0.5SP
# targetLock: percentage improvment to target lock time (applies to all ship weapons and stacks on

# map quadrant information
battlemapQuadrants = {}
battlemapQuadSize = 200.0/3.0
midQuadDistance = battlemapQuadSize/2
i = 1
for y in range(0,3):
    for x in range(0,3):
        battlemapQuadrants[i] = (midQuadDistance-100+battlemapQuadSize*x, midQuadDistance-100+battlemapQuadSize*y)
        i += 1

regimentCombinedBonus = 100
missileHitDroneMultiplier = 3

militiaType = {'BMF':'1', 'AMF':'11', 'IMF':'21'}

# diplomacy
diplomacy = {1:{'name':'At War', 'engage':1, 'invade':1, 'trade':0, 'move':1, 'alliance':0,
                'description':'Being At War means you can attack and invade another player, you can do this at No Relations, however its one step harder to move to better relations when you are at War' },
             2:{'name':'No Relations', 'engage':1, 'invade':1, 'trade':0, 'move':1, 'alliance':0,
                'description':'Being At No Relations is the default relations, you can decide to attack another player without warning, however this will move you to an At War state'},
             3:{'name':'Non Agression Pact', 'engage':1, 'invade':0, 'trade':0, 'move':0, 'alliance':0,
                'description':'A Non Agression pack means your ships can only attack each other if they meet on a neutral battlefield.  You cannot move your ships onto each others planets until you decrease diplomacy'},
             4:{'name':'Trade Agreement', 'engage':0, 'invade':0, 'trade':1, 'move':0, 'alliance':0,
                'description':'A Trade Agreement allows two Empires to trade resources directly to each other including using warp gates to trade, your ships will also not fight each other if they meet on a neutral system, you can move your ships to your new friends planets, but if they lower diplomacy you could get stuck there.'},
             5:{'name':'Mutual Trading Partnership', 'engage':0, 'invade':0, 'trade':1, 'move':1, 'alliance':0,
                'description':'A Mutual Trading Partnership is the same as a Trade Agreement, you can still move ships and troops onto each others planets (you will not invade), its just one step closer to an alliance, and one step further from being backstabbed later, ie it would take one more turn of decreased diplomacy before the player could be attacked'},
             6:{'name':'Alliance', 'engage':0, 'invade':0, 'trade':1, 'move':1, 'alliance':1,
                'description':'An Alliance is the highest level of diplomacy, at this level players can use each others warp gates, although you can have many trade partners, you can only have one ally in the game at one time'}
             }


signalreceived = False            
dolePerCity = 700.0
shipUpkeep = 5.0 #ship mass divided by this number
armyUpkeep = 400.0
cityupkeepMultiplier = 400.0 #upkeep based on cities in empire in relation to this number

adminaccess = "will be filled in by main"
