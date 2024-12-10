# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 14:18:52 2024

@author: ellio
"""

#included with python 3.12
import os, time, datetime, json, platform, csv, sys
import requests #2.32.2

#via biopython 
import Bio.Entrez as Entrez
from Bio.Entrez import esearch, elink, efetch

#mie_2024 file
from . import user_end
from .user_end import user_input

when = str(datetime.datetime.now())[:17].replace(' ', '_').replace(':', '.')
welcome ='''This program takes a list of NCBI protein accessions and uses NCBI's E-Utilities to find the corresponding nucleotide record.
The coding (CDS) regions of the record are then searched for your product(s) of interest.
\nIf your 1 or more of your product(s) of interest is found:
\toutputs: a .fasta file
\twith the regions containing and surrounding hits for your product of interest.
\nIf there are no hits for your product(s) of interest:
\toutputs: a .json file
\twith all CDS regions labeled by product for later parsing.
\nYou can stop the program at any time without losing files written so far, but remaining queries will not be saved.
\nType --help in any interactive field to view information on input requirements and usage.'''
log_it = user_end.log_it('filter', when, os.getcwd())
logger = log_it[0]
log_loc = log_it[1]

def user_information(when):     
    print('\nUser Information', '-'*(os.get_terminal_size()[0]-17))
    #EMAIL
    Entrez.email = user_input(name= 'email', 
                       prompt='Email to share with NCBI E-Utilities: ', 
                       gate_type='value'
                       ).value_received
    
    #API
    api_use = user_input(name='api_use',
                         prompt='Would you like to use an NCBI API key for better speeds? ',
                         gate_type='preference' 
                         ).value_received
    if api_use == True:
        Entrez.api_key = user_input(name='api_key',
                             prompt='API key associated with NCBI account: ', 
                             gate_type='value'
                             ).value_received
    else:
        Entrez.api_key = None

    #QUERY FILE    
    path_in = user_input(name='path_in', 
                            prompt='Full path to input file containing protein accessions, including .csv extension: ',
                            gate_type='value'
                            ).value_received.strip('"')
    p1 = path_in.split('\\')[-1].strip('.csv') + f'_._{when}p1'
    col = int(user_input(name='col',
                     prompt='Protein Accession column number: ',
                     gate_type='value'
                     ).value_received)
    query_list, file_name = read_input(path_in, col) 

    #SAVE LOCATION
    save_preference = user_input(name='save_preference', 
                                 prompt='Would you like to save outputs to a location other than the default folder? ', 
                                 gate_type='preference'
                                 ).value_received
    if save_preference == True:
        path_out = user_input(name='path_out', 
                                   prompt='Full path to your desired save folder: ', 
                                   gate_type='value'
                                   ).value_received
    else:
        path_out = f'{os.getcwd()}\\mie_2024_outputs\\filter\\{p1}'
        if not os.path.exists(path_out):
            os.makedirs(path_out)

    #SEARCH REQUESTS
    print('\nSearch Parameters', '-'*(os.get_terminal_size()[0]-18))
    compiled_searches = []
    more_searches = True
    while more_searches != False:
        new_search = search_parameters()
        compiled_searches.append(new_search)
        more_searches = user_input(name='more_searches', 
                                  prompt='Would you like to add another search? ',
                                  gate_type='preference'
                                  ).value_received
        
    #MARGIN
    margin = int(user_input(name='margin', 
                            prompt='How many products would you like to include when trimming around matches for your product of interest? ',
                            gate_type='value'
                            ).value_received)
    
    return query_list, file_name, path_out, compiled_searches, margin, p1

def read_input(path_in, col):
    file_name = path_in.split('\\')[-1]
    query_file = csv.reader(open(path_in, 'r'))
    query_list = [row[col-1] for row in query_file]
    query_list = query_list[1:] if '.' not in query_list[0] else query_list
    return query_list, file_name

def search_parameters():
    search_parameters = {}
    keyword = user_input(name='keyword', 
                         prompt='Keyword to search: ',
                         gate_type='value'
                         ).value_received
    
    needs_neighbor = user_input(name='needs_neighbor', 
                                prompt='Requires adjacent product? ', 
                                gate_type='preference'
                                ).value_received
   
    if needs_neighbor == True:
        search_parameters['neighbor_separation'] = user_input(name='neighbor_separation',
                                                              prompt='Permissible separation of neighboring products: ',
                                                              gate_type='value'
                                                              ).value_received
        search_parameters['neighbors'] = user_input(name='neighbors',
                                                    prompt='Possible adjacent product(s), comma separated: ',
                                                    gate_type='value'
                                                    ).value_received.split(', ')
    search_parameters['keyword']=keyword
    search_parameters['needs_neighbor']=needs_neighbor
    
    return search_parameters
    
def accession_link(queries, db_pep, db_nuc): 
    start=time.time()
    acc_links={} #a dictionary of {nucelotide record ID : query protein ID}
    
    #b_proteins: records for the queried proteins via a mass fetch request
    b_proteins = efetch(db = db_pep,
                        id=queries,
                        idtype='acc', 
                        rettype='gb', 
                        retmode = 'txt'
                        ).read(
                        ).split('//\n\n')[:-1]
    
    for p_record in b_proteins:
        #accomodate mixed accession functionality: Entrez vs. DBSOURCE
        #records without GI numbers cannot be Entrez linked (no esearch/elink)
        #records with GI numbers must be Entrez linked (no 'DBSOURCE')
        p_accession = p_record.split('\nSOURCE')[0
                                     ].split('VERSION')[1
                                     ].split('\n')[0
                                     ].split()[0]
                                                   
        if 'RefSeq.' in p_record: #RefSeq. indicates GI number usage
            s = json.load(esearch(db = 'protein',
                                  term = p_record.split('KEYWORDS')[0
                                         ].split('VERSION')[-1].strip(),
                                  usehistory='y',
                                  rettype='uilist',
                                  retmode='json')
                                  )['esearchresult']
            
            l = json.load(elink(dbfrom = 'protein',
                                db = 'nuccore',
                                linkname = 'protein_nuccore',
                                id = s['idlist'][0],
                                usehistory='y', 
                                webenv=s['webenv'], 
                                querykey=s['querykey'],
                                retmode='json', 
                                idtype='acc'))
        
            nuc_accession = l['linksets'][0]['linksetdbs'][0]['links'][0]
            #nucleotide record of GI indexed protein found by search/link
        else:
            nuc_accession = p_record.split('KEYWORDS')[0
                                   ].split('DBSOURCE')[1
                                   ].split()[1]
            #nucleotide record of non-GI indexed protein found by text parse
                                          
        acc_links[f'{nuc_accession}'] = p_accession
        #GI and non-GI indexed proteins treated identically in linking dict
       
    return acc_links, time.time()-start

def fetch_CDS(acc_links, db_nuc):
    start=time.time()
    
    nucs = requests.get(efetch(db= db_nuc, 
                               id= acc_links.keys(),
                               idtype='acc', 
                               rettype='fasta_cds_na', 
                               retmode='txt'
                               ).url, stream=True)
    

    records ={}
    accumulate_record = str()
    for chunk in nucs.iter_content(chunk_size=1024):  #reading 1kb at a time
        chunk = chunk.decode('utf-8')
                  
        if '\n\n' not in chunk:
            accumulate_record += chunk
          
        else: #reaching the break between records
        #finish current record and prepare for storage
            accumulate_record += chunk.partition('\n\n')[0]
    
            n_proteins=[] #to store CDS regions of nucleotide record
            n_accession = accumulate_record.split('>lcl|')[1
                                          ].split(' ')[0
                                          ].split('_cds')[0]                                         
            linker = f'{n_accession}_nuccore_of_{acc_links[n_accession]}'
            
            for cds in accumulate_record.split('>lcl|')[1:]:
                info={} #qualifiers of a single CDS
                
                #manual input of 1st and last qualifiers
                info['identifier'] = cds.partition(' [')[0]
                info['locus_tag'] = cds.partition(' [')[2
                                      ].partition('] [')[0
                                      ].partition('=')[2]                
                info['seq'] = cds.partition(']\n')[2]  
                
                #addition of standardly formatted qualifiers
                for i in cds.partition(']\n')[0].split('] [')[1:]:
                    info[i.partition('=')[0]] = i.partition('=')[2]
              
                n_proteins.append(info)
                     
            #continue after break between records
            accumulate_record = chunk.partition('\n\n')[2]
            records[linker] = n_proteins
            
    return records, time.time()-start

def product_search(linker, record, compiled_searches, margin): 
    start=time.time()
    
    all_proteins=[]
    for cds in record:
        if 'protein' in cds.keys():
            all_proteins.append(cds['protein'])
        elif 'pseudo' in cds.keys():
            all_proteins.append(cds['pseudo'])
            
    catch_inds = []
    #set up the clipping window, considering all search terms
    for search in compiled_searches:
        
        if (search['needs_neighbor'] == True) and any(n in str(all_proteins) for n in search['neighbors']):
            
            #check directionality, assume bidirectional if unspecified
            direction = '+-'
            if '+' in search['neighbor_separation']:
                direction = '+'
            if '-' in search['neighbor_separation']:
                direction = '-'
            for i in search['neighbor_separation'].partition(direction):
                if i.isnumeric():
                    neighbor_separation = int(i)
                elif len(i) > 0:
                    direction = i 
            
            #for neighbors with unspecified separation
            if neighbor_separation == '00':
               for loc, protein in enumerate(all_proteins):
                   if search['keyword'] in protein:
                       catch_inds.append(loc)
            
            #for neighbors with specified separation
            else:
                neighbor_separation = int(neighbor_separation)
                #for unidirectional
                check_ind = (loc + neighbor_separation) if (direction == '+') else (loc - neighbor_separation) if (direction == '-') else 0
                for loc, protein in enumerate(all_proteins):
                    if (check_ind != 0) and (check_ind in range(len(all_proteins))) and (any(search['neighbors'] in all_proteins[check_ind])):
                        catch_inds.append(loc)
                        
                #for bidirectional    
                if direction == '+-':
                    checkn = loc-neighbor_separation
                    checkp = loc+neighbor_separation
                if checkn in range(len(all_proteins)) and any(n in all_proteins[checkn] for n in search['neighbors']):
                    catch_inds.append(loc)
                if checkp in range(len(all_proteins)) and any(n in all_proteins[checkp] for n in search['neighbors']):
                    catch_inds.append(loc)
                                   
        if search['needs_neighbor'] == False:
            for loc, protein in enumerate(all_proteins):
                if search['keyword'] in protein:
                    catch_inds.append(loc)
                    
    print(f'- {linker}: found {len(catch_inds)} total products from {len(compiled_searches)} searches.')
    logger.debug(f'{len(catch_inds)} hits for {linker} at {catch_inds}')

    catch_inds=sorted(catch_inds)
    if len(catch_inds) > 0:
        window = (catch_inds[0]-margin, catch_inds[-1]+margin, len(catch_inds))
    else:
        window = len(all_proteins)
    return window, time.time()-start

def save_clip(record, linker, searches, window, save_to):
    start = time.time()
    if not os.path.exists(save_to):
        os.makedirs(save_to)
        os.chdir(save_to)
        
    if type(window) == tuple:
        coding_clip = record[window[0]:window[1]]
        header = f'>Partial from {linker} | CDS_{window[0]} - CDS_{window[1]} of {len(record[1])} | with 1 or more findings of {searches}\n'
        neighborhood = str()
        
        for cds in coding_clip:
            neighborhood += cds['seq'].replace('\n','')
            
        if len(neighborhood) < 1000:
            logger.debug(f'Extended window for {linker}')
            print('\tChosen margin will trim this record too short for product prediction. Extending to length >= 1000.')
            n = window[1]
            while len(neighborhood) < 1000:
                n = n+1
                cds = record[n]
                neighborhood += cds['seq'].replace('\n', '')
            header = f'>Partial from {linker} | CDS_{window[0]} - CDS_{window[1]} of {len(record[1])} (margin extended) | with 1 or more findings of {searches}\n'
        with open(f'{save_to}\\{linker}.fasta', 'w') as file:
            file.write(header)
            file.write(neighborhood)
    
    else:
        with open(f'{save_to}\\{linker}.json', 'w') as file:
            json.dump(record, file)
    return time.time()-start

def process_selection(selection, compiled_searches, margin, path_out, db_pep, db_nuc):
    for attempt in range(3):
        try:
            links, link_t = accession_link(selection, db_pep, db_nuc)
        except:
            logger.info(f'Encountered a web error, attempt {attempt+1}/3. Sleeping 5 seconds.')
            time.sleep(5)
            continue
        else:
            break
        
    records, record_t = fetch_CDS(links, db_nuc)
    elapsed = link_t + record_t
    
    for linker, record in records.items():
        window, window_t = product_search(linker, record, compiled_searches, margin)
        clip_t = save_clip(record, linker, compiled_searches, window, path_out)
        elapsed += window_t
        elapsed += clip_t
    return elapsed

def use_batches(query_list, file_name, path_out, compiled_searches, margin, db_pep, db_nuc):
    print('\nRun Information','-'*(os.get_terminal_size()[0]-16))
    print(f'{len(query_list)} queries found in {file_name}')
    
    if len(query_list) > 5:
        print('Warning: Large Query Request')
        batch = user_input(name='batch',
                           prompt='Would you like to estimate your job time by running a batch? ',
                           gate_type='preference'
                           ).value_received
    if batch == True:
        batch_size = int(user_input(name='batch_size',
                                prompt='Size of batch: ',
                                gate_type='value'
                                ).value_received)
        if batch_size > len(query_list):
            print(user_input.explanations['batch_size'])
            batch_size = int(user_input(name='batch_size',
                                    prompt='batch_size',
                                    gate_type='value'
                                    ).value_received)
    else:
        batch_size = len(query_list)
        
    b=1
    run=True
    remaining = len(query_list)
    start = 0
    while run != 'stop':
        end = (b * batch_size) 
        if run == False:
            end = len(query_list)

        selection = query_list[start : end]
        print(f'\nRecords {start+1}-{end}')
        elapsed = process_selection(selection, compiled_searches, margin, path_out, db_pep, db_nuc)
        remaining = len(query_list) - end
        
        if remaining > 0:
            start = end
            b+=1
            run = job_estimate(elapsed, remaining, batch_size)
        
    if remaining in range(1, batch_size-1):
        print(f'Running remaining {remaining} queries.')
        selection = query_list[start : len(query_list)]
        process_selection(selection, compiled_searches, margin, path_out, db_pep, db_nuc)

    if remaining == 0:
            run = 'stop'

    print('\nQuery list completed.')
    return remaining

def job_estimate(speeds, remaining, batch_size):
    print('Rate per entry: ', round(speeds/batch_size, 5), ' seconds')
    estimate = speeds*remaining/batch_size
    if estimate >= 60:
        estimate = str(estimate/60)[0:5] + ' minutes'
        if estimate > 3600:
            estimate = str(estimate/3600)[0:5] + ' hours'
    else:
        estimate = str(estimate)[0:5] + ' seconds'
        
    print('Estimated time remaining: ', estimate, f'for {remaining} queries.')
    
    if remaining >= batch_size:
        batch = user_input(name='batch',
                           prompt='Would you like to continue batching? ',
                           gate_type='preference'
                           ).value_received
    else:
        batch = 'stop'
    return batch

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
        logger.debug(f'ENV: {os.environ['CONDA_PREFIX'] if 'CONDA_PREFIX' in os.environ.keys() else None}')
        pass
    db_pep = 'protein'
    db_nuc= 'nuccore'
    query_list, file_name, path_out, compiled_searches, margin, p1 = user_information(when)

    logger.debug(f'email: {Entrez.email}')
    logger.debug(f'api key: {Entrez.api_key}')
    logger.debug(f'queries: {query_list}')
    logger.debug(f'searches: {compiled_searches}')
    logger.debug(f'margin: {margin}')
   
    use_batches(query_list, file_name, path_out, compiled_searches, margin, db_pep, db_nuc)
    
    logger.info(f'Results saved to: {path_out}')
    logger.info(f'Log saved to: {log_loc}')
if __name__ == "__main__":
     main(welcome, when)
    







