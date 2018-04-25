from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.DataAndObjects import FunctionData
from LOTlib.TopN import TopN
from collections import Counter
from LOTlib.Miscellaneous import logsumexp, qq
from model import *
import copy
import numpy


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


def get_top_N(pair1, pair2):
    priors = {}
    complete = 0
    for p1 in pair1:
        for p2 in pair2:
            data = [FunctionData(alpha=alpha,
                     input=[p1], output={p2: len(p2)})]
            h0 = MyHypothesis()
            top_hyps = set()
            seen = set()

            chains = 0
            while ((len(seen) < n_top and chains < max_chains) or (len(seen) < 3)):
                chains += 1
                x = 0
                for h in MHSampler(h0, data, steps=steps, acceptance_temperature=acc_temp):
                        #print y
                    out = h(p1)[:len(p2)]

                    str_h =str(h)
                    if len(out) == len(p2) and hamming_distance(out, p2) == 0:
                        if str_h not in seen: #and "from" not in str_h[14:]:
                            top_hyps.add((copy.deepcopy(h), h.prior))
                            seen.add(str_h)

                    if x % 1000 == 0:
                        print_star(x, h, out, p2, h.value.get_rule_signature(), len(seen))

                    x += 1

            print_star()
            priors[(p1,p2)] = []
            for h in sorted(top_hyps, key=lambda tup: -tup[1])[:n_top]:
                print p1, p2
                print h[0], h[1] , h[0].value.count_subnodes()
                priors[(p1,p2)].append((copy.deepcopy(h[0]), h[1], h[0].value.count_subnodes()))
            complete += 1
            print "complete: %d" % complete


    for key in priors:
        print "***"
        print key
        for p in priors[key]:
            print p

        print "***"

    return priors

def output_top(top_h,rule_keys, out_f):
    o = "from,to,h,prior,n_subnodes,type,name,count\n"
    for k in top_h:
        frm = toAB(str(k[0]))
        to = toAB(str(k[1]))
        for p in top_h[k]:
            print p
            h = str(p[0].value).replace(" ","")
            h = h.replace(","," ")
            prior=p[1]
            n_subnodes = p[2]

            rc = numpy.hstack(get_rule_counts(grammar, p[0].value))
            print rc
            print len(rc), len(rule_keys)
            assert(len(rc) == len(rule_keys))
            for r in xrange(len(rc)):
                type_r = rule_keys[r][0]
                name_r = rule_keys[r][1]
                count_r = rc[r]

                o += ("%s,%s,%s,%f,%d,%s,%s,%d\n" % 
                        (frm,to,h,prior,n_subnodes,type_r,name_r,count_r))


    f = open(out_f, "a+")
    f.write(o)
    f.close()


def output_top2(top_h,rule_keys, out_f):
    o = "from,to,h,prior,n_subnodes,type,name,count\n"
    for k in top_h:
        to = toAB(str(k[1]))

        for frms in pair1:
            #frm = toAB(str(k[0]))
            frm = toAB(frms)
            for p in top_h[k]:
                print p
                h = str(p[0].value).replace(" ","")
                h = h.replace(","," ")
                prior=p[1]
                n_subnodes = p[2]

                rc = numpy.hstack(get_rule_counts(grammar, p[0].value))
                print rc
                print len(rc), len(rule_keys)
                assert(len(rc) == len(rule_keys))
                for r in xrange(len(rc)):
                    type_r = rule_keys[r][0]
                    name_r = rule_keys[r][1]
                    count_r = rc[r]

                    o += ("%s,%s,%s,%f,%d,%s,%s,%d\n" % 
                            (frm,to,h,prior,n_subnodes,type_r,name_r,count_r))


    f = open(out_f, "a+")
    f.write(o)
    f.close()

if __name__ == "__main__":

    alpha = 0.0005
    steps = 10000
    n_top = 25
    acc_temp = 5.
    max_chains = 10

    pair1 = vanilla_conditions(True, False)
    pair2 = vanilla_conditions(False, True)

    print pair1
    print pair2
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


    #rule_keys = numpy.array(rule_keys).flatten()
    print rule_keys
    #top = get_top_N(pair1, pair2)
    #top = get_top_N(pair2, pair1)
    top = get_top_N([pair1[0]], pair2)



        
    #output_top(top, rule_keys, out_f="grammar_inf/out_prior_no_reuse2.csv")

    output_top2(top, rule_keys, out_f="grammar_inf/out_prior_no_reuse1.csv")
