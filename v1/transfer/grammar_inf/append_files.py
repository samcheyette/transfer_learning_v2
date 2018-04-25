import csv
import copy
import pandas as pd


def get_data(file):
	return pd.read_csv(file)

def add_reuse(data):

	h_add = "append(" + data["h"] + " from_seq)"

	data["h"] = h_add 
	data.loc[data.name == "from_seq", "count"] += 1
	data.loc[data.name == "append", "count"] += 1


	return data

def main():
	files = ["out_prior", "out_prior_reuse", "out_prior_no_reuse1", "out_prior_no_reuse2"]
	files = [f + ".csv" for f in files]
	out_f = "comb_prior.csv"

	df = get_data(files[0])
	#print len(df)
	for f in files[1:]:

		data = get_data(f)
		reuse_added = add_reuse(copy.deepcopy(data))
		df = df.append(copy.deepcopy(data))
		df = df.append(copy.deepcopy(reuse_added))

	df.to_csv(out_f)



if __name__ == "__main__":
	main()



