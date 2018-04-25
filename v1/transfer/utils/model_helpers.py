
def print_star(*args):
    if len(args) > 0:
        for arg in args:
            print arg
        print "*" * 100
        print


def vanilla_conditions(appstim=True, append=True):
	stims = []
	endings = []
	if appstim:
		stims = ["aabaabaabaabaab", "baabaaabaaaabaa", "aaaaaabbbbbbbbb", "bbaaabbaaabbaaa", "bbbbbababababab",
		             "ababbababbababb"]
		stims = [fromAB(s) for s in stims]
	if append:
		endings = ["aaabaaabaaabaaa", "abaabaaabaaaaba", "bbbbaaaaaaaaaaa", 
						"bbaaaabbaaaabba", "aaaabababababab",
		           "babaababaababaa"]
		endings = [fromAB(s) for s in endings]

	all_use = []
	for k in stims:
		all_use.append(k)
	for k in endings:
		all_use.append(k)

	return all_use


def fromAB(s):
    #inverse of toAB
    ret = ""
    for j in s:
        if j == "a":
            l = "0"
        else:
            l = "1"
        ret += l
    return ret


def toAB(s):
    #inverse of toAB
    ret = ""
    for j in s:
        if j == "0":
            l = "a"
        else:
            l = "b"
        ret += l
    return ret
    
def hamming_distance(a, b):
    assert(len(a) == len(b))
    hd = 0
    for i in xrange(len(a)):
        if a[i] != b[i]:
            hd += 1

    return hd