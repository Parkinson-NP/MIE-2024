import csv
import numpy as np

pathy="C:\\Users\\ellio\\OneDrive - purdue.edu\\Summer 2024\\Research Lab\\Clean Library\\input_files\\reductase_test2.csv"
yoyo = np.loadtxt(pathy, delimiter=",", dtype=str, encoding='utf-8')
print(yoyo, np.shape(yoyo))
print(yoyo[0])