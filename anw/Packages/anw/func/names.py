# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# names.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# generates random names based on name lists
# ---------------------------------------------------------------------------
import string
import random
import math
import os

alphabet = "abcdefghijklmnopqrstuvwxyz"

class LetterMap:
    """utility class used by NameGenerator to track
    mapping between tokens and letters.
    """
    def __init__(self, token):
        self.token = token
        self.totalSize = 0
        self.letterMap = {}

    def addLetter(self, toLetter):
        """collect an instance in the sample data of
        a character after this token
        """
        if not toLetter in alphabet:
            return
        
        self.totalSize += 1
        value = self.letterMap.get(toLetter, 0)
        self.letterMap[toLetter] = value + 1

    def getLetter(self, random):
        """get a random letter based on my
        statistics
        """
        i = random.randint(0, self.totalSize)
        pos = 0
        for letter, number in self.letterMap.items():
            if i > pos and i <= pos + number:
                return letter
            pos += number
        return None
    
class NameGenerator:
    """class to generator random names from a seed and
    a set of input data.
    """
    def __init__(self, seed):
        self.nameMap = {}
        self.numNames = 0
        self.numCharacters = 0
        self.random = random.Random(seed)
        self.wordSizes = []

    def inputFile(self, fileName):
        """read a set of words from an input file"""
        f = open(fileName)
        text = f.read()
        f.close()
        words = text.split(" ")
        self.input(words)
        
    def input(self, inputNames):
        """collect statistcs from a set of words in a string
        """
        for name in inputNames:
            for i in range(0, len(name)-2):
                # extract the token and next character
                fromToken = name[i:i+2]
                nextChar = name[i+2]
                if not fromToken[0] in alphabet:
                    continue

                # add to letter map
                letterMap = self.nameMap.get(fromToken, LetterMap(fromToken))
                letterMap.addLetter(nextChar)
                self.nameMap[fromToken] = letterMap

            # update statistics
            self.numNames += 1
            self.numCharacters += len(name)
            self.wordSizes.append(len(name))

        self.calcStandardDeviation()

    def calcStandardDeviation(self):
        """calculates the standard deviation of the size
        of words in the input set.
        """
        self.mean = self.numCharacters / self.numNames
        variance = 0
        for size in self.wordSizes:
            variance += (self.mean-size)**2
        self.standardDeviation = math.sqrt(variance/float(self.numNames))

    def makeName(self):
        """makes a new random name based on the statistics
        collected from the sample data.
        """
        size = self.random.choice([3,4,5,6,7,8,9])
        output = self.random.choice(self.nameMap.keys() )
        for i in range(0,size):
            lastChar = output[-2:]
            letterMap = self.nameMap.get(lastChar, None)
            if letterMap:
                newChar = letterMap.getLetter(self.random)
                if newChar:
                    output += newChar
        return string.capwords(output)

def getNames(inputFile, num, rand=19):
    """Return a List of Names based on input file"""
    list = []
    dict = {}
    systemName = NameGenerator(rand)
    systemName.inputFile(inputFile)
    for i in range(0,num):
        name = systemName.makeName()
        if len(name) > 2 and dict.has_key(name) == 0:
            list.append(name)
            dict[name] = 1
    return list
                
