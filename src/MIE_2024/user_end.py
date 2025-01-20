# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 16:20:44 2024

@author: ellio
"""
import os, sys, re, logging, pprint, platform
fsep = '/' if platform.system() == 'Linux' else '\\'

explanations = {'--end': 'At any input point, use --end to halt the program. No additional outputs will be given, including save locations. Lost information may be recovered from the associated .log file created for your run.',
                'email': '''Accessing NCBI's E-Utilities through BioPython requires an email. This email is used by NCBI to track usage rates and enquire about excessive use. See "Accessing NCBI’s Entrez databases" > "Entrez Guidelines" available at https://biopython-tutorial.readthedocs.io/en/latest/ for details.''',
                'api_use': '''Using an NCBI API key allows for an allowed query rate upgrade from 3/sec to 10/sec. API keys are available upon request free of charge, see https://support.nlm.nih.gov/knowledgebase/article/KA-05317/en-us for instructions.''',
                'api_key' : '''Your API key should be a string of numbers and letters, available via your NCBI profile.''',
                'path_in': f'''A CSV file containing protein accessions in the NCBI protein database. If your header row contains the '.' character, it will be mistaken for an accession. Files with and without headers are supported. If your file path as pasted is not recognized, first ensure you are utilizing the correct slash notation for your operating system (/path/to/file vs {fsep}path{fsep}to{fsep}file). If issues persist, try using double slashes to catch any accidental unicode interpretations (writing /path/to/file as //path//to//file).''',
                'col' : '''Column number containing protein accessions in input csv.''',
                'save_preference': f'You will need this save location for the next step, product prediction. By default, your outputs will be saved to {os.getcwd()}{fsep}mie_2024_outputs{fsep}script{fsep}job_id.',
                'path_out' : '''You will need this save location for the next step, product prediction. If operating with a virtual machine, please ensure you will be able to access this path from your UNIX system.''', 
                'keyword' : '''A word or word fragment to be found in the '/product' field of a CDS in a GenBanl feature table. Keywords are case sensitive.''',
                'needs_neighbor' : '''Adjacent products may be used to identify modular combinations, for example an NRPS accompanied by a PBP-like peptide cyclase, rather than an NRPS alone.''',
                'neighbor_separation' : '''If adjacent products should be direct neighbors, their separation should be entered as +/-0. Directionality is considered, where negative values indicate the neighboring product is to be upstream of your initial search, and positive separation searches for your neighboring product downstream of your initial search. If no +/- is indicated, both upstream and downstream relationships will be counted. To search for product pairs of unknown or variable separation, enter '00'. Searches for multiple products in series are not currently supported.''',
                'neighbors' : ''''Adjacent products may be used to identify modular combinations, for example an NRPS accompanied by a PBP-like peptide cyclase, rather than an NRPS alone.''',
                'more_searches' : '''Multiple searches are intended to account for the use of acronyms in the product description field, such that records which fulfill the parameters of one or more searches will be saved for product prediction.''', 
                'margin' : '''Downstream bioinformatics tools often require context to operate. For example, antiSMASH may not recognize a product as an NRPS if it appears to be a contig. Control the amount of context in your output files as an integer number of products to include on either side of matches for your product of interest.''',
                'welcome' : 'Hello!',
                'batch' : '''To offer more control over your experience, you may opt to release your queries in small batches. At the end of each batch, you will be offered a time estimate for remaining queries and the choice to continue batching or release all remaining queries.''',
                'batch_size' : 'A positive integer, less than the length of your query list.',
                'convert_path' : '''For users needing virtualization to use antiSMASH, files may prove difficult to navigate to given the differences in path conventions between operating systems. Selecting yes will attempt to programatically convert any Windows path to the corresponding mount. If programatic conversion repeatedly fails, opt out and manually convert your path.''',
                'smiles' : '''Optionally include product SMILES in the synthesis guide sheet.'''}

def log_it(script_name, when, basedir):
    save_file = f'{basedir}{fsep}mie_2024_logs{fsep}{script_name}{fsep}{script_name}_{when}.log'
    if not os.path.exists(f'{basedir}{fsep}mie_2024_logs{fsep}{script_name}'):
        os.makedirs(f'{basedir}{fsep}mie_2024_logs{fsep}{script_name}')

    cf = logging.Formatter('%(message)s')
    ff = '%(asctime)s - %(name)s: %(message)s'
    logging.basicConfig(filename=save_file, format=ff)
    logger = logging.getLogger(f'mie_2024.{script_name}')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(cf)
    logger.addHandler(ch)
    return logger, save_file

class user_input:
    def __init__(self, name, prompt, gate_type):
        self.prompt = prompt
        self.info = explanations[name]
        self.gate_type = gate_type
        self.name = name 
        self.value_received = self.gate_loop()
    
    def echo_YIN(prompt, choice, echo): #echo, yes/no/info loop

        if echo == False: #only asking once
            print(prompt)
            print('\t (Y) to confirm | (I) for more info | (N) to decline')
            
            user = input('\t Choice: ')
            if '--help' in user:
                pprint.pprint(explanations, width=os.get_terminal_size()[0])

            if '--end' in user:
                print(f"Voluntary exit completed.")
                sys.exit()
                
            if type(user) == str:
                choice = re.sub(r'\W+', '', user).lower()[0]
                    
        if echo == True: 
            if str(choice).lower() != 'i':
                if type(choice) == str:
                    print('\t', 'You entered: ', choice)
                                    
            print('\t (Y) to confirm | (I) for more info | (N) to retype your answer')
            
            user = input('\t Choice: ')
            if '--help' in user:
                pprint.pprint(explanations, width=os.get_terminal_size()[0])

            if '--end' in user:
                print(f"Voluntary exit completed.")
                sys.exit()
                
            if type(user) == str:
                choice = re.sub(r'\W+', '', user).lower()[0]

        else:
            choice = choice.lower() #otherwise do info

        if choice[0] == 'y':
            return True
        
        if choice[0] == 'i':
            return None
        
        if choice[0] == 'n':
            return False
        
        else:
            print('Unrecognized input or choice. Please rerun the program to assure accurate setup parameters.')
            sys.exit()
            
            
    def value_check(self, value):
        if '--help' in value:
            pprint.pprint(explanations, width=os.get_terminal_size()[0])

        if '--end' in value:
            print(f"Voluntary exit completed.")
            sys.exit()

        gate = False
        if self.name == 'email':
            error_message = 'Invalid email address given. Please include a domain, such as @org.edu'
            gate = '@' in value and '.' in value
        if self.name == 'path_out':
            error_message = 'File/path not found. Please check the location of your file/path and try again.'
            if not os.path.exists(value.strip('"')):
                os.makedirs(value.strip('"'))
            gate = os.path.exists(value.strip('"'))
        if self.name == 'path_in':
            error_message = 'File/path not found. Please check the location of your file/path and try again.'
            gate = os.path.exists(value.strip('"'))
        if self.name == 'neighbor_separation' or self.name == 'margin':
            error_message = 'Please enter an integer with optional directionality; (+n, -n, or n) for n separating products.'
            gate = any(p.isnumeric() for p in value)
        if self.name == 'margin' or self.name == 'col':
            error_message = 'Please enter an integer >= 0.'
            gate = value.isnumeric() and int(value) >= 0
        if self.name == 'batch_size':
            error_message = explanations['batch_size']
            gate = value.isnumeric() and int(value) > 0
            
        if self.name in ['keyword', 'api_key', 'neighbors']:
            error_message = None
            gate = None
        if gate == False:
            print(error_message)
            
        else:
            gate = user_input.echo_YIN(self.prompt, value, echo = True)
            
        if gate == None:
            print(self.info)
        
        return gate
    
    def gate_loop(self):
        
        if self.gate_type == 'value':
            gate = False
            value = None
            while gate != True:
                value = input(self.prompt).strip()
                gate = user_input.value_check(self, value)
            return value
        
        if self.gate_type == 'preference':
            gate = None
            while type(gate) != bool:
                gate = user_input.echo_YIN(self.prompt, None, echo = False)
                if gate == None:
                    print(self.info)
            return gate 