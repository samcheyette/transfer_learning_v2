import copy
import random
import pandas as pd
import numpy as np
from collections import defaultdict
#import pymc3 as pm  



def get_data(file):
	data = pd.read_csv(file)

	data["unique_name"] = map("".join, data[["type", "name"]].values)
	names = data["unique_name"]
	types = np.unique(data["type"])
	unique_names = "".join(np.unique(names))
	counts = dict(zip(types, map(lambda x: unique_names.count(x), types)))
	type_counts = np.array([counts[x] for x in data["type"]])
	data["type_counts"] = type_counts
	data["term_prior"] =  np.log(1./type_counts) * data["count"]

	fr = data["from"]
	to = data["to"]
	

	unique_names = data["unique_name"]
	types = data["type"]
	counts = data["count"]
	h = data["h"]
	term_prior = data["term_prior"]

	vals1 = zip(counts, types, type_counts, term_prior)
	keys1 = zip(fr, to, unique_names, h)
	ret_dct1 = dict(zip(keys1, vals1))

	ret_dct2 = dict()

	for k in ret_dct1:
		newk = (k[0], k[1], k[3])
		if newk not in ret_dct2:
			ret_dct2[newk] = []
		ret_dct2[newk].append(tuple(list(ret_dct1[k]) + [k[2]]))

	for k in ret_dct2:
		print k, sorted(list(ret_dct2[k]), key=lambda tup: tup[len(tup)-1])


	#return ret_dct
	#data = data.set_index(['from', 'to', 'h', 'unique_name']).T.to_dict('list')
	


def main():
	file = "out_prior.csv"
	data = get_data(file)






 
if __name__ == "__main__":
	main()