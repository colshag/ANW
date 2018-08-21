# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# globals.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Store Global Variables
# ---------------------------------------------------------------------------

currentVersion = '0.0.4.07'

# default RGB values for each color used in game
colors = {'yellow':(252, 224, 0, 255),
          'orange':(255, 92, 0, 255),
          'green':(62, 249, 79, 255),
          'cyan':(0, 194, 226, 255),
          'red':(238, 21, 21, 255),
          'pink':(254, 156, 176, 255),
          'white':(254, 246, 248, 255),
          'ltpurple':(239, 144, 250, 255),
          'blue':(57, 165, 248, 255),
          
          'blood':(156, 0, 0, 255),
          'dkgrey':(60, 60, 60, 255),
          'dkpurple':(110, 4, 122, 255),
          'dkgreen':(6, 61, 11, 255),
          'dkblue':(30, 13, 136, 255),
          'black':(10, 10, 10, 255),
          'dkyellow':(150,150,0,255)
          }

# test empire image combos
simEmpireColors = {'1':{'color1':'white', 'color2':'dkblue'},
                   '2':{'color1':'yellow', 'color2':'blood'}
                   }

# simulator interval value
intervalValue = 0.02

# amount of resources required to add one city to a system
addCityResource = {'CR':5000.0, 'AL':1000.0, 'EC':250.0, 'IA':100.0}

# amount to modify the resource focus of one city
updateCityResource = {'CR':500.0, 'AL':0.0, 'EC':0.0, 'IA':0.0}

# amount of resources one city will generate without bonuses
cityCRGen = 200.0
cityALGen = 20.0
cityECGen = 10.0
cityIAGen = 5.0

# armor modifiers
reflectiveArmorModifier = 0.5
impactArmorModifier = 0.5

# quadrants
quadAngles = {'fore':0.0, 'port':90.0, 'aft':180.0, 'star':270.0}
angleQuads = {0.0:'fore', 90.0:'port', 180.0:'aft', 270.0:'star'}

# compass angles allows for easier player understanding of directional angles for fleet directional placement
compassAngles = {90:'N', 270:'S', 0:'E', 180:'W', 45:'NE', 135:'NW', 225:'SW', 315:'SE'}

# components
weaponComponent = '64'

# max movement
maxAccel = 4000.0
maxRotation = 40.0
maxDroneAccel = 5000.0
maxDroneRotation = 50.0

# hardpoints
hardPoints = {'SCT':{'fore-1':[0,8],
                     'aft-1':[180,7],
                     'port-1':[135,7],
                     'star-1':[225,7]
                     },
              'INT':{'fore-1':[0,8],
                     'aft-1':[180,8],
                     'port-1':[90,8],
                     'star-1':[270,8]
                     },
              'COR':{'fore-1':[330,4],'fore-2':[30,4],
                     'aft-1':[210,4],'aft-2':[150,4],
                     'port-1':[120,16],'port-2':[120,12],
                     'star-1':[240,16],'star-2':[240,12]
                     },
              'HCO':{'fore-1':[330,4],'fore-2':[30,4],
                     'aft-1':[210,4],'aft-2':[150,4],
                     'port-1':[120,16],'port-2':[120,12],
                     'star-1':[240,16],'star-2':[240,12]
                     },
              'FRG':{'fore-1':[0,30],'aft-1':[135,8],'port-1':[20,12],'star-1':[340,12],
                     'fore-2':[10,30],'aft-2':[225,8],'port-2':[30,4],'star-2':[330,4],
                     'fore-3':[350,30],'aft-3':[180,8],'port-3':[135,26],'star-3':[225,26]
                     },
              'BFR':{'fore-1':[0,35],'aft-1':[135,8],'port-1':[25,18],'star-1':[335,18],
                     'fore-2':[10,35],'aft-2':[225,8],'port-2':[30,10],'star-2':[330,10],
                     'fore-3':[350,35],'aft-3':[180,8],'port-3':[135,30],'star-3':[225,30]
                     },
              'DST':{'fore-1':[5,46],'aft-1':[180,20],'port-1':[23,20],'star-1':[337,20],
                     'fore-2':[355,46],'aft-2':[200,20],'port-2':[30,14],'star-2':[330,14],
                     'fore-3':[13,46],'aft-3':[220,20],'port-3':[45,4],'star-3':[315,4],
                     'fore-4':[347,46],'aft-4':[180,30],'port-4':[135,30],'star-4':[225,30]
                     },
              'CRU':{'fore-1':[5,50],'aft-1':[180,40],'port-1':[100,40],'star-1':[260,40],
                     'fore-2':[355,50],'aft-2':[200,30],'port-2':[110,42],'star-2':[250,42],
                     'fore-3':[13,45],'aft-3':[220,30],'port-3':[125,44],'star-3':[235,44],
                     'fore-4':[347,45],'aft-4':[180,10],'port-4':[100,18],'star-4':[260,18]
                     },
              'BCU':{'fore-1':[7,50],'aft-1':[180,40],'port-1':[100,40],'star-1':[260,40],
                     'fore-2':[353,50],'aft-2':[200,30],'port-2':[110,42],'star-2':[250,42],
                     'fore-3':[16,45],'aft-3':[220,30],'port-3':[125,44],'star-3':[235,44],
                     'fore-4':[346,45],'aft-4':[200,40],'port-4':[105,18],'star-4':[255,18],
                     'fore-5':[0,50],'aft-5':[220,40],'port-5':[90,16],'star-5':[270,16]
                     },
              'HCU':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[90,16],'star-5':[270,16]
                     },
              'DRN':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[90,16],'star-5':[270,16],
                     'fore-6':[0,16],'aft-6':[180,16],'port-6':[90,16],'star-6':[270,16]
                     },
              'SDN':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[90,16],'star-5':[270,16],
                     'fore-6':[0,16],'aft-6':[180,16],'port-6':[90,16],'star-6':[270,16],
                     'fore-7':[0,16],'aft-7':[180,16],'port-7':[90,16],'star-7':[270,16]
                     },
              'ECA':{'fore-1':[10,15],'aft-1':[170,15],'port-1':[40,25],'star-1':[320,25],
                     'fore-2':[350,15],'aft-2':[190,15],'port-2':[100,20],'star-2':[100,20],
                     'fore-3':[0,15],'aft-3':[180,15],'port-3':[150,25],'star-3':[210,25]
                     },
              'BCA':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16]
                     },
              'HCA':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[90,16],'star-5':[270,16]
                     },
              'LTT':{'fore-1':[10,15],'aft-1':[170,15],'port-1':[40,25],'star-1':[320,25],
                     'fore-2':[350,15],'aft-2':[190,15],'port-2':[100,20],'star-2':[100,20],
                     'fore-3':[0,15],'aft-3':[180,15],'port-3':[150,25],'star-3':[210,25]
                     },
              'BTT':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16]
                     },
              'HTT':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[90,16],'star-5':[270,16]
                     },
              'LWP':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[90,16],'star-5':[270,16]
                     },
              'BWP':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[90,16],'star-5':[270,16],
                     'fore-6':[0,16],'aft-6':[180,16],'port-6':[90,16],'star-6':[270,16],
                     'fore-7':[0,16],'aft-7':[180,16],'port-7':[90,16],'star-7':[270,16]
                     },
              'HWP':{'fore-1':[0,16],'aft-1':[180,16],'port-1':[90,16],'star-1':[270,16],
                     'fore-2':[0,16],'aft-2':[180,16],'port-2':[90,16],'star-2':[270,16],
                     'fore-3':[0,16],'aft-3':[180,16],'port-3':[90,16],'star-3':[270,16],
                     'fore-4':[0,16],'aft-4':[180,16],'port-4':[90,16],'star-4':[270,16],
                     'fore-5':[0,16],'aft-5':[180,16],'port-5':[90,16],'star-5':[270,16],
                     'fore-6':[0,16],'aft-6':[180,16],'port-6':[90,16],'star-6':[270,16],
                     'fore-7':[0,16],'aft-7':[180,16],'port-7':[90,16],'star-7':[270,16],
                     'fore-8':[0,16],'aft-8':[180,16],'port-8':[90,16],'star-8':[270,16],
                     'fore-9':[0,16],'aft-9':[180,16],'port-9':[90,16],'star-9':[270,16]
                     }
              }
              
# limitations
componentLimitations = {'warship':['SMP','PMP','UMP','SJD','PJD','UJD','SES','PES','UES'],
                        'platform':['SMP','PMP','UMP'],
                        'carrier':['SMP','PMP','UMP',
                                   'LNTA','MNTA','HNTA','LFTA','MFTA','HFTA','LPTA',
                                   'MPTA','HPTA','LGGA','MGGA','HGGA','LACA','MACA',
                                   'HACA','LRGA','MRGA','HRGA','LNMA','MNMA','HNMA',
                                   'LFMA','MFMA','HFMA','LPMA','MPMA','HPMA','SES','PES','UES'],
                        'troopship':['LNTA','MNTA','HNTA','LFTA','MFTA','HFTA','LPTA',
                                     'MPTA','HPTA','LGGA','MGGA','HGGA','LACA','MACA',
                                     'HACA','LRGA','MRGA','HRGA','LNMA','MNMA','HNMA',
                                     'LFMA','MFMA','HFMA','LPMA','MPMA','HPMA',
                                     'SJD','PJD','UJD','SES','PES','UES']}

weaponLimitations = {'warship':['LNL','MNL','HNL','LFL','MFL','HFL','LPL','MPL','HPL'],
                     'platform':[],
                     'carrier':['LPG','MPG','HPG','LFC','MFC','HFC','LPC','MPC','HPC',
                                'LNT','MNT','HNT','LFT','MFT','HFT','LPT','MPT','HPT',
                                'LGG','MGG','HGG','LAC','MAC','HAC','LRG','MRG','HRG',
                                'LNM','MNM','HNM','LFM','MFM','HFM','LPM','MPM','HPM'],
                     'troopship':['LNL','MNL','HNL','LFL','MFL','HFL','LPL','MPL','HPL',
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
rankMods = {shipRank0:{'weaptarget':80,'retarget':500,'toHit':50,'kWtoSPfactor':0.3,'targetLock':0,'missileSpeed':0.8},
            shipRank1:{'weaptarget':40,'retarget':350,'toHit':60,'kWtoSPfactor':0.6,'targetLock':0,'missileSpeed':1.1},
            shipRank2:{'weaptarget':35,'retarget':300,'toHit':70,'kWtoSPfactor':0.7,'targetLock':0,'missileSpeed':1.2},
            shipRank3:{'weaptarget':30,'retarget':250,'toHit':80,'kWtoSPfactor':0.8,'targetLock':10,'missileSpeed':1.3},
            shipRank4:{'weaptarget':25,'retarget':200,'toHit':90,'kWtoSPfactor':0.9,'targetLock':20,'missileSpeed':1.4},
            shipRank5:{'weaptarget':20,'retarget':150,'toHit':100,'kWtoSPfactor':1.0,'targetLock':30,'missileSpeed':1.5},
            shipRank6:{'weaptarget':10,'retarget':35,'toHit':100,'kWtoSPfactor':1.0,'targetLock':50,'missileSpeed':2.0},
            shipRank7:{'weaptarget':10,'retarget':25,'toHit':100,'kWtoSPfactor':2.0,'targetLock':70,'missileSpeed':3.0},
            
            armyRank0:{'bonus':0},
            armyRank1:{'bonus':250},
            armyRank2:{'bonus':500},
            armyRank3:{'bonus':1000},
            armyRank4:{'bonus':2000}
            }

# kW to shield point conversion factor: 0.5 means 1kW makes 0.5SP
# targetLock: percentage improvment to target lock time (applies to all ship weapons and stacks on

# map quadrant information
battlemapUnitLength = 1000
battlemapQuadrants = {}
i = 1
for y in range(0,3):
    for x in range(0,3):
        battlemapQuadrants[i] = (1000+3000*x, 1000+3000*y)
        i += 1

# regiment states
regimentStates = {1:'On System',
                  2:'Loaded on Ship',
                  3:'Loaded on Ship',
                  4:'Landed on System'}

regimentCombinedBonus = 100

militiaType = {2:'1', 4:'11', 6:'21'}

# diplomacy
diplomacy = {1:{'name':'At War', 'engage':1, 'invade':1, 'trade':0, 'move':1, 'alliance':0},
             2:{'name':'No Relations', 'engage':1, 'invade':1, 'trade':0, 'move':1, 'alliance':0},
             3:{'name':'Non Agression Pact', 'engage':1, 'invade':0, 'trade':0, 'move':0, 'alliance':0},
             4:{'name':'Trade Agreement', 'engage':0, 'invade':0, 'trade':1, 'move':1, 'alliance':0},
             5:{'name':'Mutual Trading Partnership', 'engage':0, 'invade':0, 'trade':1, 'move':1, 'alliance':0},
             6:{'name':'Alliance', 'engage':0, 'invade':0, 'trade':1, 'move':1, 'alliance':1}
             }

#TODO: remove this when proper player config is setup
players = {'colshag@gmail.com':'Chris Lewis',
           'jefflewis12@gmail.com':'Jeff Lewis',
           'qcaron@coylecaron.com':'Q Caron',
           'bhavinmistry76@gmail.com':'Bhavin Mistry',
           'gumshoes@gmail.com':'Ruedi Eder',
           'kameron.malik@gmail.com':'Kameron Malik',
           'kris.kundert@gmail.com':'Kris Kundert',
           'impulsemt@shaw.ca':'Matt Turner',
           'lewiscaron@shaw.ca':'Patrick Caron',
           'perry@kundert.ca':'Perry Kundert',
           'tdowling@gmail.com':'Tavis Dowling'
           }