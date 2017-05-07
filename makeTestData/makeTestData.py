# -*- coding: utf-8 -*-
"""
Created on Sun May 07 12:24:11 2017

@author: dion-
"""

import numpy as np
import matplotlib.pyplot as plt

def makeLMdata(echoTime,R0,Tex,K0):
    """Calculates expected echo times following equation (1) from Stefanovic & Pike 2004.
    echoTime in us
    R0 in 1/s
    Tex in s
    K0 in Tesla squared
    """
    gamma=2.675e8 # rad/s/T
    echoTime=echoTime
    r2=R0 + (gamma**2 * K0 * Tex) *(1- 2*(Tex/echoTime)*np.tanh(echoTime/(2*Tex)))
    return r2

ET=1e-3*np.array([2, 2.5, 3, 3.74, 4, 4.5, 5, 7, 10, 12, 14, 17, 20, 30, 40])
r94 = makeLMdata(ET, 1/0.198, 3e-3, 0.5e-14) #Y=94%: T20=198ms, K=0.5e-14
r87 = makeLMdata(ET, 1/0.197, 3e-3, 1.4e-14) #Y=87%: T20=197ms, K=1.4e-14 
r72 = makeLMdata(ET, 1/0.184, 3e-3, 4.6e-14) #Y=62%: T20=184ms, K=4.6e-14

r62 = makeLMdata(ET, 1/0.184, 3e-3, 4.6e-14) #Y=62%: T20=184ms, K=4.6e-14

r42 = makeLMdata(ET, 1/0.166, 3e-3, 9.4e-14) #Y=42%: T20=166ms, K=9.4e-14

plt.plot(ET,1.0/r94,label="Y=0.94")
plt.plot(ET,1.0/r62,label="Y=0.62")
plt.plot(ET,1.0/r42,label="Y=0.42")
plt.legend()
