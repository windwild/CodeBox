#coding=utf-8
import math
import scipy.stats
 
def get_d1(S0,K,r,sigma,T):
    S0 = 1.0*S0
    K = 1.0*K
    r = 1.0*r
    sigma = 1.0*sigma
    T = 1.0*T
    return (math.log(S0/K) + (r + sigma**2/2)*T)/(sigma*math.sqrt(T))

def get_d2(S0,K,r,sigma,T):
    return (math.log(S0/K) + (r - sigma**2/2)*T)/(sigma*math.sqrt(T))

def get_N(x):
    mynorm = scipy.stats.norm(0,1)
    return mynorm.cdf(x)

def get_c(S0,K,r,sigma,T):
    S0 = 1.0*S0
    K = 1.0*K
    r = 1.0*r
    sigma = 1.0*sigma
    T = 1.0*T
    return S0*get_N(get_d1(S0,K,r,sigma,T))-K*math.exp(-r*T)*get_N(get_d2(S0,K,r,sigma,T))

def get_p(S0,K,r,sigma,T):
    S0 = 1.0*S0
    K = 1.0*K
    r = 1.0*r
    sigma = 1.0*sigma
    T = 1.0*T
    return K*math.exp(-r*T)*get_N(-get_d2(S0,K,r,sigma,T)) - S0*get_N(-get_d1(S0,K,r,sigma,T))

def main():
    S0,K,r,sigma,T = 100,103,0.04,0.3,1.5
    print get_c(S0,K,r,sigma,T)
    K = 97
    print get_p(S0,K,r,sigma,T)
 
if __name__ == '__main__':
    main()
