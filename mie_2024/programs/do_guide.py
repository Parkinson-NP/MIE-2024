# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 23:06:04 2024

@author: ellio
"""


import os, json, datetime, sys
import pandas as pd
from user_input import user_input

when = str(datetime.datetime.now())[:17].replace(' ', '_').replace(':', '.')
def user_information(when):
    path_in = user_input(name='path_in', 
                         prompt='Full path to program 2 output directory: ',
                         gate_type='value'
                         ).value_received
    
    p2 = path_in.split('/')[-1]
    p3 = f'{p2}---{when}p3'
    
    #SAVE LOCATION
    save_preference = user_input(name='save_preference', 
                                 prompt='Would you like to save your output file to a location other than the default folder? ', 
                                 gate_type='preference'
                                 ).value_received
    if save_preference == True:
        path_out = user_input(name='path_out', 
                                   prompt='Full path to your desired save folder: ', 
                                   gate_type='value'
                                   ).value_received + '.csv'
    else:
        path_out = f'{os.getcwd()}\\program_outputs\\program3_out\\{p3}.csv'
    return path_in, path_out
 
def antismash_json_to_AA(filename):
    products={}
    nucleotide_source = filename.split('.p2\\')[1].partition('-nuccore_of-')[0]
    
    with open(filename, 'r') as input_file:
        antismash_json = json.load(input_file)
        
    record = antismash_json['records'][0]    
    if 'modules' in record.keys():
        if 'antismash.modules.nrps_pks' in record['modules'].keys():
            product_regions = record['modules']['antismash.modules.nrps_pks']['region_predictions']
            
            for product_n, prediction in product_regions.items():
                polymer_raw = prediction[0]['polymer'].split(' + ')
                polymer_formatted = []
                polymer_dict = {}
                for p in polymer_raw:
                    p = p[1:-1].split(' - ')
                    polymer_formatted.extend(p)
                for i, p in enumerate(polymer_formatted):
                    polymer_dict[f'AA_{i+1}'] = p
                    
                products[f'{nucleotide_source}_product{product_n}'] = polymer_dict
    return products

def save_results(path_in, path_out):
    
    output = {}
    for result in os.listdir(path_in):
        file=f'{path_in}\\{result}\\{result}.json'
        products = antismash_json_to_AA(file)
        for key, value in products.items():
            output[key] = value
    df = pd.DataFrame(output).T
    df.to_csv(path_out)
    print('Result saved to: ', path_out)
    
def main(when):
    path_in, path_out = user_information(when)
    save_results(path_in, path_out)
    
if __name__ == "__main__":
    main(when)