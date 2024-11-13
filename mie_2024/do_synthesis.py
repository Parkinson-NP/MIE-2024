# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 23:06:04 2024

@author: ellio
"""

import os, json, datetime, sys, platform
import pandas as pd
from user_input import user_input

when = str(datetime.datetime.now())[:17].replace(' ', '_').replace(':', '.')
welcome = '''This program is a short organizational script used to parse the collection of nested files produced by antiSMASH into a CSV.
Results are indexed and organized as series of monomers, aligned with the sequential procedure of solid-phase peptide synthesis.
Product SMILES may be added for further detail.'''
def user_information(when):
    path_in = user_input(name='path_in', 
                         prompt='Full path to antiSMASH output directory: ',
                         gate_type='value'
                         ).value_received
    
    p2 = path_in.split('\\')[-1].split('.csv')[0]
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
        path_out = f'{os.getcwd()}\\mie_2024_outputs\\synthesis'
        if not os.path.exists(path_out):
            os.makedirs(path_out)

    smiles = user_input(name='smiles',
                        prompt='Include SMILES on synthesis sheet? ',
                        gate_type='preference'
                        ).value_received
    
    return path_in, path_out, p3, smiles
 
def antismash_json_to_AA(filename, smiley):
    products=[]
    nucleotide_source = filename.split('.p2\\')[1].split('\\')[0]
    
    with open(filename, 'r') as input_file:
        antismash_json = json.load(input_file)
        
    record = antismash_json['records'][0]    
    if 'modules' in record.keys():
        if 'antismash.modules.nrps_pks' in record['modules'].keys():
            product_regions = record['modules']['antismash.modules.nrps_pks']['region_predictions']
            
            for product_n, prediction in product_regions.items():
                polymer_raw = prediction[0]['polymer'].split(' + ')
                polymer_formatted = []

                smiles = prediction[0]['smiles']
                if smiley == True:
                    polymer_dict = {'Product' : f'{nucleotide_source}_product{product_n}',
                                    'SMILES': smiles}
                else:
                    polymer_dict = {'Product' : f'{nucleotide_source}_product{product_n}'}

                for p in polymer_raw:
                    p = p[1:-1].split(' - ')
                    polymer_formatted.extend(p)
                for i, p in enumerate(polymer_formatted):
                    polymer_dict[f'AA_{i+1}'] = p
                
                products.append(polymer_dict)
    return products

def save_results(path_in, path_out, p3, smiles):
    
    output = {}
    for result in os.listdir(path_in):
        file=f'{path_in}\\{result}\\{result}.json'
        products = antismash_json_to_AA(file, smiles)
        
        #TODO: eliminate pandas dependency by writing longest product keys as header
        sys.exit()
    df = pd.DataFrame(output).T
    df.to_csv(f'{path_out}\\{p3}.csv')
    print('Result saved to: ', path_out)
    
def main(when):
    if input('Press (W) to see a welcome message, To continue, press any other key. ').lower() == 'w':
        print('-'*os.get_terminal_size()[0])
        print(welcome)
        print('Please ensure all system and environment information is as expected before continuing.')
        print('\tOperating system: ', platform.system())
        print('\tWorking directory: ', os.getcwd())
    path_in, path_out, p3, smiles = user_information(when)
    save_results(path_in, path_out, p3, smiles)
    
if __name__ == "__main__":
    main(when)