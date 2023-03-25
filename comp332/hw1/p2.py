# calc n choose k x p_succ^k x (1-p_succ)^(n-k)
# n = 40 ; k = 11 .. 40 ; p_succ = .9

import scipy.special

tot_prob = 0
p_succ = 0.1
for i in range(11,41):
    bnom = scipy.special.comb(40,i, exact=True)
    #print(bnom * p_succ**(i) * (1-p_succ)**(40-i))
    tot_prob += bnom * p_succ**(i) * (1-p_succ)**(40-i)

print(tot_prob)
