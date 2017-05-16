# -*- coding: utf-8 -*-
"""
Created on Sun May 07 12:24:11 2017

@author: dion-
"""

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(15123)

def makeLMdata(echoTime,R0,Tex,K0):
    """Calculates expected relaxivities following equation (1) from Stefanovic & Pike 2004.
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

#Values of T20, K from Table 1 Stefanovic and Pike 2004

r94 = makeLMdata(ET, 5.0505, 3e-3, 0.5e-14) #Y=94%: T20=198ms, K=0.5e-14
r87 = makeLMdata(ET, 5.0761, 3e-3, 1.4e-14) #Y=87%: T20=197ms, K=1.4e-14 
r72 = makeLMdata(ET, 5.0000, 3e-3, 2.9e-14) #Y=72%: T20=200ms, K=2.9e-14
r66 = makeLMdata(ET, 5.4644, 3e-3, 3.7e-14) #Y=66%: T20=183ms, K=3.7e-14
r62 = makeLMdata(ET, 5.4347, 3e-3, 4.6e-14) #Y=62%: T20=184ms, K=4.6e-14
r42 = makeLMdata(ET, 6.0240, 3e-3, 9.4e-14) #Y=42%: T20=166ms, K=9.4e-14

plt.plot(1e3*ET, r94, label="Y=0.94")
plt.plot(1e3*ET, r87, label="Y=0.87")
plt.plot(1e3*ET, r72, label="Y=0.72")
plt.plot(1e3*ET, r66, label="Y=0.66")
plt.plot(1e3*ET, r62, label="Y=0.62")
plt.plot(1e3*ET, r42, label="Y=0.42")
plt.xlabel("Echo Time (ms)")
plt.ylabel("R2 (s-1)")
plt.legend()

#build echo decays
nrEchoes=32
snr=6

plt.figure()

decayX=np.ndarray((ET.shape[0],nrEchoes))
decayY=np.ndarray((ET.shape[0],nrEchoes))

echoes=np.zeros((ET.shape[0],nrEchoes,32), dtype=np.complex)
echotimeaxis=np.arange(32)

for i in range(len(ET)):
    decayX[i]=np.arange(nrEchoes)*ET[i]
    decayY[i]=np.exp(-1*r62[i]*decayX[i])
    plt.plot(decayX[i],decayY[i])
    
    for j in range(nrEchoes):
        #Gaussian echo + noise:
        echoes[i,j]=decayY[i,j]*snr*np.exp(-0.01*(16-echotimeaxis)**2 )+ np.random.rand(echotimeaxis.shape[0]) + 1j*np.random.rand(echotimeaxis.shape[0])
    np.savetxt('r62/ET%1d.csv'%i, echoes[i],delimiter=',')
np.savetxt('r62/echoTimes.csv',ET)
    