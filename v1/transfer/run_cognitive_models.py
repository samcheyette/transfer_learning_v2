from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.DataAndObjects import FunctionData
from LOTlib.TopN import TopN
from collections import Counter
from LOTlib.Miscellaneous import logsumexp, qq
from model import *
import copy
import numpy
import itertools as it


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
        v = numpy.array([counts.get(r.get_rule_signature(),0) for r in grammar.rules[nt] ])
        out.append(v)
    return out


def run_nothing(pairs):
    priors = {}
    complete = 0
    for pair in pairs:
        p1 = pair[0]
        p2 = pair[1]
        data = [FunctionData(alpha=alpha,
                 input=[p1], output={p2: len(p2)})]
        h0 = MyHypothesis()
        top_hyps = set()
        seen = set()
        for ind in xrange(0, len(p2), 3):
            for h in MHSampler(h0, data, steps=steps, 
                acceptance_temperature=acc_temp):

                print h, h(p1)




 



if __name__ == "__main__":

    alpha = 0.0005
    steps = 10000
    n_top = 25
    acc_temp = 5.
    max_chains = 10

    pairs = [x for x in it.product(vanilla_conditions(True, False),
             vanilla_conditions(False, True))]
    pairs += [x for x in it.product(vanilla_conditions(False, True), 
                    vanilla_conditions(True, False))]


    print pairs
    print len(pairs)
    rule_keys = []

    for z in grammar: 
        #print z.get_rule_signature()
        rs_orig = z.get_rule_signature()
        name = rs_orig[1].replace("'", "")
        name = name.replace("(", "")
        name = name.replace(")", "")
        name = name.replace(",","")
        name = name.replace("%s", "")
        name = name.replace(" ", "")

        rs = (rs_orig[0], name)

        rule_keys.append(rs)


    print rule_keys

    run_nothing(pairs)