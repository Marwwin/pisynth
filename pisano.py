#%%

## THIS CELL COUNTS THE PISANO PERIODS

import time 
import numpy as np
import sys

# Fibbonacci
def getFibonacci(n):
  res = [0,1]
  return fibHelper(n,2, res)

def fibHelper(n,i,res):
  if len(res) == n:
    return res
  else:
    res.append(res[i-1]+res[i-2])
    i += 1
    return fibHelper(n,i,res)

def findPeriod(fList):
  for f in range(len(fList)):
    valueToTest = "".join(list(map(str,fList[0:f+1])))
    against = "".join(list(map(str,fList[f+1:(f+1)*2])))
    against2 = "".join(list(map(str,fList[(f+1)*2:(f+1)*3])))
    if valueToTest == against and valueToTest == against2:
      return fList[0:f+1]

# Pisano period
def getPisano(modulo):
  fib = np.array(getFibonacci(5000))
  pisano = fib%modulo
  series = findPeriod(pisano)
  return series

sys.setrecursionlimit(10000)

#startT = time.time()

#fib = np.array(getFibonacci(5000))
#pisanoPeriods = {}
#for i in range(1,20):
#  period = getPisano(i,fib)
#  pisanoPeriods.update({i:period})

#print(pisanoPeriods)
#print("Runtime:",time.time() - startT)

#%%

## GET THE TURTLE READY FOR ACTION

#import turtle
#
#s = turtle.getscreen()
#s.setup(startx=20,starty=20)
#t = turtle.Turtle()
#
#def getCircleData(period):
#  return len(getPisano(period))
#
#def getAllPoints(p):
#  points = []
#  for i in range(p):
#    points.append(t.pos())
#    t.circle(50,360/p)
#  return points
#
#def drawPisano(mod):
#  currentPeriod = getPisano(mod)
#  points = getAllPoints(mod)
#  for i in range(len(currentPeriod)):
#    t.goto(points[currentPeriod[i]])
#
#t.clear()
#t.speed(0)
#cn = 0
#yValue = 525
#for i in range(1,40):
#  t.pu()
#  xValue = -380+(115*(cn%8))
#  if cn %8 == 0:
#    yValue -= 115
#  t.setpos(xValue,yValue)
#  t.pd()
#  drawPisano(i)
#  cn += 1
#
#s.exitonclick()
#
##t.circle(100,360/5)
##t.pos()

#%%


##%%
#
#while True:
#  print("Number Series to Circles App v0.1")
#  print("-----------------------------------------")
#  print("1. Load number series")
#  print("2. Change modulator")
#  print("3. Draw one circle")
#  print("4. Draw many circles")
#  print("5. Draw circles and save to file")
#  meny = input("Pick your destiny:")
#  
#
#
#