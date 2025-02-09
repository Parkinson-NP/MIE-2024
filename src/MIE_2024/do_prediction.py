# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 13:44:16 2024

@author: ellio
"""
import datetime, os, sys, subprocess, platform, json, csv
import user_end
from user_end import user_input

when = str(datetime.datetime.now())[:16].replace(' ', '_').replace(':', '.')

welcome = '''This program combs through results of do_filter.py (or any other directory containing .fasta files) and automates product prediction by antiSMASH.
Product prediction may take considerable time - antiSMASH will supply reporting on product prediction status automatically. Please take care when providing input and output folder paths.
Type --help in any interactive field to view information on input requirements and usage, or --end to terminate the program.'''
log_it = user_end.log_it('prediction', when, os.getcwd())
logger = log_it[0]
log_loc = log_it[1]
error_message = '''As a start to interpreting the auto-generated error message, some common issues include:
    - command line arguments entered out of order
    - improperly converted file paths for your operating system
    - improperly written nucleotide records
    - failure to set a conda environment with access to antiSMASH
    - issues with your antiSMASH installation.'''

def close_out(error, step):
    print('Something went wrong. Please see auto-generated error information below:')
    logger.info(type(error).__name__, "-", error)
    print('Step impacted: ', step)
    print(error_message)
    sys.exit()

def user_info(when):
    print('Input/Output Information', '-'*(os.get_terminal_size()[0]-25))
    #PATH IN
    convert_path = user_input(name='convert_path',
                              prompt='Would you like to utilize path conversion?',
                              gate_type='preference',
                              ).value_received
    logger.debug(f'Path conversion: {convert_path}')

    path_in = user_input(name='path_in', 
                            prompt='Full path to folder containing .fasta files: ',
                            gate_type='value'
                            ).value_received.strip('"')
    
    if convert_path == True:
        path_in = WL_conversion(path_in)
    
    #PATH OUT
    path_out = user_input(name='path_out', 
                                   prompt='Full path to your desired save folder: ', 
                                   gate_type='value'
                                   ).value_received.strip("\"")
    
    if not os.path.exists(path_out):
            os.makedirs(path_out)

    if convert_path == True:
        path_out = WL_conversion(path_out)

    return path_in, path_out

def WL_conversion(path):
    linux_path = '/mnt/' + path.replace('C:', 'c').replace("\\", "'/'")
    return linux_path

def prepare(path_in, path_out):
    
    p1 = path_in.split('/')[-1].split('_._')[0]
    p2 = f'{p1}_._{when}.p2'
    
    try:
        files = str(subprocess.check_output(['ls', path_in])).strip('b\'').split('\\n')[:-1]
        files = [f for f in files if '.fasta' in f]
        print('Found', len(files), 'results to run.')
    except Exception as error:
        close_out(error, 'Accessing .fasta outputs from you unix system or virtual machine via your 2nd argument.')
    
    try:    
        subprocess.call(['mkdir', f'{path_out}/{p2}'])
    except Exception as error:
        close_out(error, 'Creating a new path to a folder interpretable by your unix system or virtual machine using your 3rd argument.')
    logger.info(f'New folder created: {path_out}/{p2}\n')
    return files, p2

def check_pred(outgo):
    name=outgo.split('/')[-1]
    file=f'{outgo}/{name}.json'
    with open(file, 'r') as input_file:
        antismash_json = json.load(input_file)
    record = antismash_json['records'][0]
  
    if len(record['areas']) < 1:
        logger.info(f'\tNo predictions made for {name}.')
        redo = name.strip('.json')
        return redo
    else:
        return '' 

def run(files, path_in, path_out,  p2):
    redo=[]
    for file in files:
        income = path_in + '/' + file
        outgo = path_out + '/' + p2 + '/' + file.strip('.fasta')
        logger.info(f'Running antiSMASH for {file.strip(".fasta")}')
        subprocess.call(['antismash', income,
                        '--output-dir', outgo,
                         '--genefinding-tool', 'prodigal',])
        do=check_pred(outgo)
        if len(do)>0:
            redo.append([do])
  
    if len(redo) > 0:
        oops = path_out + '/' + p2 + '/' + 'redo_prediction'
        with open(f'{oops}.csv', 'w', newline='') as sheet:
            writer = csv.writer(sheet)
            writer.writerows(redo)
        logger.info(f'Some predictions appear to have failed.  Your records may be incomplete or contain a contig that interferes with antiSMASH prediction capabilities. Protein accessions of all failed predictions can be found in {oops}.csv')
    print('\nProduct prediction completed.')

def main(welcome, when):
    if input('Press (W) to see a welcome message, To continue, press any other key. ').lower() == 'w':
        print('-'*os.get_terminal_size()[0])
        print(welcome)
        print('Please ensure all system and environment information is as expected before continuing.')
        logger.info(f'\tOperating system: {platform.system()}')
        logger.info(f'\tWorking directory: {os.getcwd()}')
        if 'CONDA_PREFIX' in os.environ.keys():
            env = os.environ['CONDA_PREFIX']
            logger.info(f'\tPython environment: {env}')
        else:
            logger.info('No Conda environment found.')
    else:
        logger.debug(f'OS: {platform.system()}')
        logger.debug(f'CWD: {os.getcwd()}')
        envy = os.environ['CONDA_PREFIX'] if 'CONDA_PREFIX' in os.environ.keys() else None
        logger.debug(f'ENV: {envy}')
        pass
    
    path_in, path_out = user_info(when)
    files, p2 = prepare(path_in, path_out)
    run(files, path_in, path_out, p2)
    logger.info(f'Results saved to: {path_out}/{p2}')
    logger.info(f'Log saved to: {log_loc}')
if __name__ == "__main__":
    main(welcome, when)
    
