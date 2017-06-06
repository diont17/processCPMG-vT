#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Python version of:

% Fast 2D NMR relaxation distribution estimation - Matlab/octave version
% Paul Teal, Victoria University of Wellington
% paul.teal@vuw.ac.nz
% Let me know of feature requests, and if you find this algorithm does
% not perform as it should, please send me the data-set, so I can improve it.
% Issued under the GNU AFFERO GENERAL PUBLIC LICENSE Version 3.
% If you distribute this code or a derivative work you are required to make the
% source available under the same terms

% Versions:
% 0.1 30 October 2013
% 0.2 31 October 2013
% 0.3 20 December 2013
% 0.4  1 May 2014
% 0.5  6 May 2014
% 0.6 11 Aug 2014
% 0.7  2 Aug 2016
% 0.8  6 Sep 2016
% 1.0 15 Sep 2016

% If you use this software, please cite P.D. Teal and C. Eccles. Adaptive
% truncation of matrix decompositions and efficient estimation of NMR
% relaxation distributions. Inverse Problems, 31(4):045010, April
% 2015. http://dx.doi.org/10.1088/0266-5611/31/4/045010 (Section 4: although
% the Lipshitz constant there does not have alpha added as it should have)

% Y is the NMR data for inversion
% alpha is the (Tikhonov) regularisation (scalar)
% S is an optional starting estimate

% K1 and K2 are the kernel matrices
% They can be created with something like this:
%N1 = 50;       % number of data points in each dimension
%N2 = 10000;
%Nx = 100;      % number of bins in relaxation time grids
%Ny = 101;

%tau1min = 1e-4;
%tau1max = 10;
%deltatau2 = 3.5e-4;
%T1 = logspace(-2,1,Nx);
%T2 = logspace(-2,1,Ny);
%tau1 = logspace(log10(tau1min),log10(tau1max),N1)';
%tau2 = (1:N2)'*deltatau2;
%K2 = exp(-tau2 * (1./T2) );     % simple T2 relaxation data
%K1 = 1-2*exp(-tau1 *(1./T1) );  % T1 relaxation data

"""
import numpy as np
import numpy.random
import matplotlib.pyplot as plt

def flint(K1, K2, Z, alpha, S=None):
    maxiter = 100000
    if S is None:
        Nx = K1.shape[1]
        Ny = K2.shape[1]
        S = np.ones((Nx, Ny))
    if len(Z.shape) == 1:
        Z = np.expand_dims(Z, axis=0)
    if len(S.shape) == 1:
        S = np.expand_dims(S, axis=0)

    resida = np.zeros(maxiter)
    KK1 = np.dot(K1.T, K1)
    KK2 = np.dot(K2.T, K2)
    KZ12= np.dot(K1.T, np.dot(Z, K2))
    #Lipschitz constant
    L = 2 * (np.trace(KK1) * np.trace(KK2) + alpha)
    tZZ = np.trace(np.dot(Z, Z.T))
    Y = S
    tt = 1
    fac1 = (L-2*alpha)/L
    fac2 = 2.0/L
    lastresid = np.inf
#    print(KK1.shape, Y.shape, KK2.shape, KZ12.shape)
    print("{0:7s} | {1:8s} | {2:8s} | {3:8s} | {4:10s} | {5:10s}|".format(" i ", "tt", "trat", "L", "resid", "resd"))

    for i in xrange(maxiter):
        term2 = KZ12 - np.dot(KK1, np.dot(Y,KK2))
        Snew = fac1 * Y + fac2 * term2
        Snew[Snew < 0] = 0 #changed from Snew=max(0,Snew)
        
        ttnew = 0.5*(1 + np.sqrt(1 + 4*tt**2))
        trat = (tt-1) / ttnew
        Y = Snew + trat * (Snew - S)
        tt = ttnew
        S = Snew
        
        if i % 500 == 0:
            normS = alpha * np.linalg.norm(S)**2
            resid = tZZ - 2* np.trace(np.dot(S.T, KZ12)) + np.trace(np.dot(S.T, np.dot(KK1, np.dot(S,KK2)) ) ) + normS
            resida[i]=resid
            resd = np.abs(resid - lastresid)/resid
            lastresid = resid
            print("{0:7d} | {1:.2e} | {2:.2e} | {3:.2e} | {4:.4e} | {5:.4e}|".format(i, tt, trat, L, resid, resd))
            if resd < 1e-5:
                break
    
    return np.squeeze(S), resida

#Testing
#tau =2e-3
#decay = tau * np.arange(1000)
#
#T2a =  20e-3
#T2b = 100e-3
#T2c = 400e-3
#np.random.seed(123124878)
#sig = 3*np.exp(-decay/T2a) + 6 * np.exp(-decay/T2b) + 2 * np.exp(-decay/T2c)
#sig += 1 * np.random.rand(decay.shape[0])
#sig -= 0.5
#echotime = tau * np.arange(1000)
#Ny = 201 # number of bins in relaxation time grid
#T2out = np.logspace(-3,1, Ny)
#
#K2 = np.exp(np.outer(-echotime, 1/T2out))
#K1 = np.array([[1]])
#
#for alpha in [2e-5, 2e-3]:
#    print('\nalpha = {0:.2e}'.format(alpha))
#    Sflint,resida = flint(K1, K2, sig, alpha)
#    plt.semilogx(T2out, Sflint, label= 'a = {0:.2e}'.format(alpha))
#
#plt.legend()
#plt.vlines([T2a,T2b,T2c], 0,1, 'r')

#
#import scipy.signal as signal
#
#maxPeakInd = signal.argrelmax(Sflint)
#print maxPeakInd
#
#print("max")
#print(maxPeakInd)
#print(T2out[maxPeakInd])
#print(Sflint[maxPeakInd])
#
#plt.scatter(T2out[maxPeakInd],Sflint[maxPeakInd])
