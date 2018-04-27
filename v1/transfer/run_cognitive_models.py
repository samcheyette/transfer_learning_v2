from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.DataAndObjects import FunctionData
from LOTlib.TopN import TopN
from collections import Counter
from LOTlib.Miscellaneous import logsumexp, qq
from model import *
import copy
import numpy
import itertools as it
import time

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

def run(pairs):

    priors = {}
    complete = 0
    top_hyps = set()
    already_done = set()
    t_start = time.time()

    for pair in pairs:
        p1 = pair[0]
        p2 = pair[1]

        h0 = MyHypothesis()
        t_pair = time.time()
        #h0.start_counts = add_counts

        seen = set()
        #for ind in xrange(2, 3):
        for ind in xrange(len(p1)+1):

            seen_round = set()
            x = 0
            p1_i = p1[:ind]
            p2_i = p2[:ind]
            if (p1, p2_i) not in already_done:
                already_done.add((p1, p2_i))
                data = [FunctionData(alpha=alpha,
                     input=[p1], output={p2_i: len(p2_i)})]

                while len(seen_round) < n_top:
                    for h in MHSampler(h0, data, steps=steps, 
                        acceptance_temperature=acc_temp, prior_temperature=prior_temp):
                        if len(seen_round) >= n_top:
                            break
                        str_h = str(h.value)
                        out = h(p1)[:len(p2_i)]
                        if (len(out) == len(p2_i) and
                                 (hamming_distance(out, p2_i) == 0) and
                                (len(h(p1)[:len(p1)]) == len(p1))) :
                            if str_h not in seen: #and "from" not in str_h[14:]:
                                l_rules = [str(i) for i in list(numpy.hstack(get_rule_counts(grammar, h.value)))]
                                top_hyps.add((toAB(p1), ind,copy.deepcopy(h), toAB(p2), toAB(h(p1_i)[:len(p1)]),
                                       ",".join(l_rules), str(h.value)))
                                seen.add(str_h)
                            if str_h not in seen_round:
                                seen_round.add(str_h)

                        if x % 1000 == 0:
                            print_star("seen:%d" % len(seen_round),
                                         "steps:%d" % x, "hyp:%s"%str_h,
                                         "p2:%s" % p2_i, 
                                     "out:%s"%out, 
                                    "prior:%f" % h.prior, 
                                "pair_time:%.2f" % (time.time() - t_pair),
                                 "tot_time:%.2f" % (time.time()-t_start))

                        x += 1

        for h in top_hyps:
            print_star(h[0],h[1], h[2],h[3],h[4],h[5])

    return top_hyps



def output(hyps, rule_keys, out_f, poss_pairs, use_poss=False):
    type_name = ""
    for rule in rule_keys:
        #types += "%s," % rule[0] 
        type_name += "%s_%s," % (rule[0], rule[1])
    #types = types[:len(types)-1]
    type_name = type_name[:len(type_name)-1]
    out_s = "p1,p2,out,upto,%s,hyp\n" % type_name

    for tup in hyps:
        p1 = tup[0]
        p2 = tup[3]
        for p in poss_pairs:
            poss_p1 = toAB(p[0])
            poss_p2 = toAB(p[1])
            if ((poss_p2 == p2) and 
                ((p1 == poss_p1) or use_poss)):
                out = tup[4]
                upto = tup[1]

                rules = tup[5]
                hyp = tup[6].replace(" ","").replace(","," ")

                out_s += "%s,%s,%s,%d,%s,%s\n" % (poss_p1,poss_p2,out,upto,rules,hyp)


    f = open(out_f, "w+")
    f.write(out_s)
    f.close()


                
def run_nothing(pairs):
    complete = 0
    #add_counts = {('SEQ', 'from_seq'):-1 + 1e-10, ('SEQ', '1'):1, ('SEQ', '0'):1}
    add_counts = {}
    p1 = "011101010010011"

    p2s = list(set(list(set([(p1, p[1]) for p in pairs])) + 
                list(set([(p1, p[0]) for p in pairs]))))

    #p2s = p2s[3:4]
    best_h = run(p2s)
    return best_h

def run_reuse(pairs):
    best_h = run(pairs)
    return best_h


if __name__ == "__main__":
    alpha = 1e-4
    steps = 15000
    n_top = 10
    acc_temp = 5.
    prior_temp = 1.0

    max_chains = 1

    pairs_1 = [x for x in it.product(vanilla_conditions(True, False),
             vanilla_conditions(False, True))]
    pairs_2 = [x for x in it.product(vanilla_conditions(False, True), 
                    vanilla_conditions(True, False))]

    pairs = copy.copy(pairs_1)
    pairs += copy.copy(pairs_2)

    poss_pairs = copy.copy(pairs)

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


    #hyps = run_nothing(pairs)
    #output(hyps, rule_keys, "nothing.csv", poss_pairs, use_poss=True)

    
    hyps=run_reuse(pairs)
    output(hyps, rule_keys, "reuse.csv", poss_pairs, use_poss=False)