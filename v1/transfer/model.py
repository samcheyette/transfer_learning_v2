from LOTlib.Primitives import primitive
from LOTlib.Miscellaneous import Infinity
from LOTlib.Grammar import Grammar
from collections import defaultdict

from LOTlib.Miscellaneous import attrmem
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood

from LOTlib.Miscellaneous import Infinity, beta, attrmem
from LOTlib.FunctionNode import FunctionNode

from math import log, exp
import numpy as np

#ugh, python
import sys
sys.path.insert(0, 'utils/')
from model_helpers import *


####################################################################
MAX = 30
INF = 30

#####################################################################
def get_rule_counts(grammar, t, add_counts ={}):
    """
            A list of vectors of counts of how often each nonterminal is expanded each way

            TODO: This is probably not super fast since we use a hash over rule ids, but
                    it is simple!
    """

    counts = defaultdict(int) # a count for each hash type

    for x in t:
        if type(x) != FunctionNode:
            raise NotImplementedError("Rational rules not implemented for bound variables")
        
        counts[x.get_rule_signature()] += 1 


    for k in add_counts:
        counts[k] += add_counts[k]

    # and convert into a list of vectors (with the right zero counts)
    out = []
    for nt in grammar.rules.keys():
        v = np.array([ counts.get(r.get_rule_signature(),0) for r in grammar.rules[nt] ])
        out.append(v)
    return out


def RR_prior(grammar, t, rr_alpha=1.0, add_counts={}):
    """
            Compute the rational rules prior from Goodman et al.

            NOTE: This has not yet been extensively debugged, so use with caution

            TODO: Add variable priors (different vectors, etc)
    """
    lp = 0.0

    for c in get_rule_counts(grammar, t, add_counts=add_counts):
        theprior = np.ones(len(c)) * rr_alpha

        #theprior = np.repeat(alpha,len(c)) # Not implemented in numpypy
        lp += (beta(c+theprior) - beta(theprior))
    return lp


###########################################################



@primitive
def repeat(x):
    if len(x) >= MAX or len(x) < 1:
        return x
    else:
        out =""
        while len(out) < MAX:
            out += x
        return out[:MAX]


@primitive
def append(x1, x2):
    return((x1 + x2)[:MAX])


@primitive
def invert(x):
    inv = ""
    for i in x:
        if i == "0":
            inv += "1"
        else:
            inv += "0"
    return inv

@primitive
def delete(s1, n):
    if (len(s1) >= MAX and (n == MAX)) or (len(s1) <= n):
        return s1
    else:
        return s1[:n]


@primitive
def cut(x, lower, upper):
    if upper <= lower:
        return ""
    elif ((len(x) == MAX) and (upper == MAX)):
        return x
    else:
        return x[lower:upper]



####################################################

grammar = Grammar(start='SEQ')

for i in xrange(0,10):
    grammar.add_rule('INT', str(i), None, 1.0)
grammar.add_rule('INT', str(MAX), None, 1.0)


grammar.add_rule('SEQ', "'1'", None, 3.0)
grammar.add_rule('SEQ', "'0'", None, 3.0)
grammar.add_rule('SEQ', 'from_seq', None, 3.0) 
grammar.add_rule('SEQ', 'invert', ['SEQ'], 1.0) 
grammar.add_rule('SEQ', "repeat(%s)", ["SEQ"], 1.0)
grammar.add_rule('SEQ', "append(%s, %s)", ["SEQ", "SEQ"], 1.0)
grammar.add_rule('SEQ', "delete(%s, %s)", ["SEQ", "INT"], 1.0)
grammar.add_rule('SEQ', "cut(%s, %s, %s)", ["SEQ", "INT", "INT"], 1.0)



class MyHypothesis(LOTHypothesis):
    def __init__(self, **kwargs):

        self.start_counts={}
        LOTHypothesis.__init__(self, grammar=grammar,
        maxnodes=400, display='lambda from_seq: %s', **kwargs)
        #LOTHypothesis.__init__(self, grammar=grammar,
        #maxnodes=400, display='lambda x: %s', **kwargs)


    def __call__(self, *args):
        out = LOTHypothesis.__call__(self, *args)
        return out
    

    def compute_single_likelihood(self, datum):
        alpha = datum.alpha
        true_val = datum.output.keys()[0]
        generated = self(*datum.input)

        generated = generated[:len(true_val)]


        dist = (hamming_distance(generated, true_val[:len(generated)]) + 
                     len(true_val) - len(generated))

        return dist * log(alpha) + (len(true_val) - dist) * log(1.-alpha)

    @attrmem('prior')
    def compute_prior(self,  rr_alpha=1.0):
        """
            Rational rules prior
        """
        if self.value.count_subnodes() > self.maxnodes:
            return -Infinity
        else:

            # compute the prior with either RR or not.
            return RR_prior(self.grammar, self.value,
                     rr_alpha=rr_alpha,
                     add_counts=self.start_counts)







if __name__ == "__main__":
    from LOTlib.SampleStream import *
    from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
    from LOTlib.DataAndObjects import FunctionData
    from LOTlib.TopN import TopN
    import copy
    from model_helpers import *


    #to_seq = "001001001001001"


    #from_seq = "00010001000100010001"
    #print delete_every(to_seq, 3)
    ALPHA = 0.001
    STEPS = 1000
    N_H = 20

    seqs_trans = {}

    c1 = vanilla_conditions(True, False)[0:2]
    c2 = vanilla_conditions( False, True)[0:1]

    for to_seq in c1:
        for from_seq in c2:
            print_star("")
            print from_seq, to_seq
            data = [FunctionData(alpha=ALPHA,
                     input=[from_seq], output={to_seq: len(to_seq)})]
            h0 = MyHypothesis()
            step = 0
            tn = TopN(N=N_H)
            # Stream from the sampler to a printer
            for h in MHSampler(h0, data, 
                steps=STEPS, acceptance_temperature=5.):                
                tn.add(h)

            print

            for h in tn.get_all(sorted=True):
                out= h(from_seq)
                if len(out) >= len(to_seq):
                    hd = hamming_distance(out[:len(to_seq)], to_seq)
                else:
                    hd = 15

                print h.posterior_score, h.likelihood, h.prior, h, hd
                print out[:len(to_seq)]
      



            print_star("")
