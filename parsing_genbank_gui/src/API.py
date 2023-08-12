"""
This file contains all the code necessary to communicate with the Entrez API.

The only function that should be imported from here is efetch. All other functions
are solely used by efetch and are internal to the API calls management.

If this file is called directly (ie. python3 API.py) multiple unit tests are
done in order to test the API response to various situations.
"""

import time
import urllib
from math import ceil

from Bio import Entrez
from Bio.SeqIO import InsdcIO


# === API CONFIG === #
email = "A.N.Other@example.com"
Entrez.email = email
db = "nucleotide"
rettype = "gb"
style = "withparts"
retmode = "full"
valid_types = ["CDS", "centromere", "intron", "mobile_element",
               "ncRNA", "rRNA", "telomere", "tRNA", "3'UTR", "5'UTR"]
# ===            === #


api_error = "[\033[91mAPI error\033[0m]"
api_warning = "[\033[93mAPI warning\033[0m]"
api_neutral = "[\033[94mAPI\033[0m]"
api_goodnews = "[\033[92mAPI\033[0m]"


def __isUseq__(fasta):
    try:
        return fasta.seq[0] == 'N'
    except:
        return True


def __efetch__(chunk, chunk_id, nb_of_chunks, log, verbose=False):
    """
    Calls the API function Entrez.efetch.
    This function's main purpose is to filter URL or HTTP exceptions that might
    be thrown.
    
    @param chunk_id: the identifier of the chunk

    @param nb_of_chunks: total number of chunks (ie. batches)
    
    @param log: A log object used to write to the consol of the GUI.

    @returns: the output of the function Entrez.efetch or None if there were
    some HTTP or URL exceptions.
    """
    if log is not None:
        if chunk[0] != chunk[-1]:
            log.emit(f"Fetched batch {chunk_id}/{nb_of_chunks}... [{chunk[0]}...{chunk[-1]}]")
        else:
            log.emit(f"Fetched batch {chunk_id}/{nb_of_chunks}... [{chunk[0]}]")
    elif chunk_id != -1:
        print(f"{api_neutral} Fetched batch {chunk_id}/{nb_of_chunks}...")

    try:
        if verbose:
            start = time.time()
            handle = Entrez.efetch(db=db, rettype=rettype, id=chunk)
            end = time.time()
            if verbose: print(f"{api_neutral} Fetching took {end - start}s.")
            return handle
        return Entrez.efetch(db=db, rettype=rettype, id=chunk)

    except urllib.error.HTTPError as e:
        print("%s %s for batch [%i/%i]" % (api_error, e, chunk_id, nb_of_chunks))
        print("%s This is likely caused by a non-valid NC in the batch."
              % (api_error))

    except urllib.error.URLError as e:
        print("%s %s for batch [%i/%i]" % (api_error, e, chunk_id, nb_of_chunks))

    except urllib.error.ContentTooShortError as e:
        print("%s %s for batch [%i/%i]" % (api_error, e, chunk_id, nb_of_chunks))

    print("%s Returning 'None' as a result of the unexcpected Exception.\n"
          % (api_error))


def __parse__(handle, chunk_id, nb_of_chunks, batch_size, bar=None, log=None, verbose=False):
    """
    This function simply calls the SeqIO parse method on the handle
    given by the efetch of the API.

    @param handle: the output of the API method efetch

    @param chunk_id: the identifier of the chunk

    @param nb_of_chunks: total number of chunks (ie. batches)
    
    @param log: A log object used to write to the consol of the GUI.

    @returns: the outpout given by SeqIO.parse.
    """
    if log is not None:
        log.emit(f"Reading from the Genbank database... ({chunk_id}/{nb_of_chunks})")
    elif chunk_id != -1:
        print(f"{api_neutral} Parsing batch {chunk_id}/{nb_of_chunks}...")

    if verbose is True: start = time.time()

    iterator = InsdcIO.GenBankIterator(handle)

    fastas = []
    for k, fasta in enumerate(iterator):
        if bar is not None: bar(ceil((99*(k+1))/batch_size))
        fastas.append(fasta)

    if verbose is True: print(f"{api_neutral} Parsing took {time.time() - start}s.")

    return fastas


def __getUnkownSeqs__(fastas, useTwins=False, log=None, verbose=False):
    """
    Given a list of outputs from the API, retrieves each NC which
    contains an unknown sequence (full of 'N')

    @param fastas: the output of the API

    @returns: a list of tuples (i, fasta) where i is the position
    in the fasta list of the UnknownSeq and fasta the Sequence itself.
    """
    start = time.time()
    useqs = []

    for i, fasta in enumerate(fastas):
        if fasta is None:
            continue

        if __isUseq__(fasta):
            useqs.append((i, fasta))

            if log is not None and useTwins is not True:
                log.emit(f"warning: '{fasta.name}' is an unknown sequence and was not saved.")
            else:
                print("%s '%s' (description : '%s') is an Unknown Sequence [N]." 
                      % (api_warning, fasta.name, fasta.description))

    if verbose: print(f"{api_neutral} Verificiation took {time.time() - start}s")
    return useqs


def __useTwins__(useqs, verbose):
    """
    The function which applies the 'twin method' explained
    in the description of function efetch()

    This function calls the API on a batch of twins which are
    equivalent elements to the faulty NCs found by __getUnkownSeqs__.

    @param useqs: the sequence of unknown sequences given by __getUnkownSeqs__

    @returns: Returns a list of tuples (i, fasta) where i is the position
    of the fasta in the original list fastas (this is so we recover the correct NC)
    and the new fasta with the sequence recovered.
    """
    twins, twins_id, result = [], [], []

    for (i, bad_fasta) in useqs:
        comment = bad_fasta.annotations["comment"]
        twin_pos = comment.find("The reference sequence is identical to")
        if twin_pos != -1:
            twin = comment[twin_pos + 39:].split('.')[0]
            twins.append(twin)
            twins_id.append(i)

    # Call the API in order to get the handle of the twin
    if verbose: print(f"{api_neutral} Fetching recovery batch...")
    handle = __efetch__(twins, -1, len(twins), None, verbose)
    if verbose: print(f"{api_neutral} Done.")
        
    if handle is None:
        return None
    
    # Parse using API built in function
    if verbose: print(f"{api_neutral} Parsing recovery batch...")
    fastas = __parse__(handle, -1, len(twins), None, verbose=verbose)
    if verbose: print(f"{api_neutral} Done.")

    if verbose: print(f"{api_neutral} Itterating through {len(fastas)} recovery fastas...")
    for k, (id, fasta) in enumerate(zip(twins_id, fastas)):
        tmp = useqs[k][1]
        tmp.seq = fasta.seq
        result.append((id, tmp, fasta.name))
    if verbose: print(f"{api_neutral} Done.")

    if verbose: print(f"{api_neutral} Twins sucessfuly built.")
    return result


def __fixBrokenBatch__(fastas, chunk, chunk_id, nb_of_chunks, verbose=False):
    """
    A function used to correct broken batches. A broken batch is a batch
    where some NCs were lost; meaning the output of the API no longer matches
    the length of the input. This is a problem since we loose the initial
    order in the output.

    This function corrects the order of the output by adding 'None' to the
    faulty NCs.

    For example: 

    ["NC_1", "bad_NC", "NC_2"] -> [SeqRecord, SeqRecord] -> [SeqRecord, None, SeqRecord]
                            API call             __fixBrokenBatch__

    @param fastas: A list of fastas given by the API. This is the list who
    lacks elements.

    @param chunk: The initial list of NCs, which contain the NCs that were
    dismissed by the API.

    @param chunk_id: the identifier of the chunk.

    @param nb_of_chunks: the total number of chunks (ie. batches).

    @return: returns the same output as the API but with extra elements 'None'
    when the API failed to fetch some NCs.
    """
    assert len(fastas) < len(chunk), "[API] internal error 0: batch not broken."

    loss = len(chunk) - len(fastas)
    print(f"{api_error} Batch {chunk_id}/{nb_of_chunks} is broken (lost %d out of %d)"
          % (loss, len(chunk)))

    fixed_fastas = []
    fasta_idx, none_idx = 0, 0

    for NC in chunk:
        if fasta_idx == len(fastas):
            break
        if NC == fastas[fasta_idx].name:
            fixed_fastas.append(fastas[fasta_idx])
            fasta_idx += 1
        else:
            fixed_fastas.append(None)
            none_idx += 1

    if len(fixed_fastas) != len(chunk):
        fixed_fastas += [None] * (loss - none_idx)

    return fixed_fastas


def efetch(NC_list, batch_size=200, bar=None, log=None, delete_USeq=True, use_twins=False,
           use_twins_threshold=30, verbose=False, debug=False):
    """
    A function used to call the API to fetch and parse NCs.

    @param NC_list: A string representing a NC ("NC_xxxxxx") or a list
    of strings representing a list of NCs.

    @param batch_size: The size of the batches to use when fetching multiple NCs.

    @param log: A log object used to write to the consol of the GUI.

    @param use_twins: If set to True, efetch will attempt to correct Unknown Sequences.
    Unknown Sequences are sequences full of the character 'N'. The 'twin method' consists
    in looking at the description of the faulty NC and search for identicial sequence
    references in the dataset. When found, the API fetches the identical sequence (ie. the twin)
    instead of the faulty NC and uses the sequence of the twin instead (without changing the
    name of the original faulty NC)

    @return: Returns a list of outputs from Seq.IO.parse. If, for some reason, there was a problem
    with a given NC, their Seq.IO.parse object will be None. Length of the output is always equal
    to the length of the input list.
    warning: if a single string is given as input, output will be a list of one element.
    """
    try:
        if isinstance(NC_list, str):
            NC_list = [NC_list]

        print(f"{api_neutral} Building sequences for {len(NC_list)} NC's")
        
        if use_twins and len(NC_list) > use_twins_threshold:
            use_twins=False

        # Segmenting NC_list in batches
        chunks = [NC_list[x:x+batch_size] for x in range(0, len(NC_list), batch_size)]
        
        fastas_result = []

        for chunk_id, chunk in enumerate(chunks):
            # Call the API in order to get the handle
            handle = __efetch__(chunk, chunk_id, len(chunks) - 1, log, verbose)

            if handle is None:
                # Dealing with API errors
                fastas = [None] * len(chunk)
            else:
                # Parse using API built in function - Converting to list is important.
                fastas = __parse__(handle, chunk_id, len(chunks) - 1, min(len(NC_list), batch_size), 
                                   bar, log, verbose=verbose)

                print(f"{api_goodnews} Done with batch {chunk_id}/{len(chunks) - 1}.")

                # Deal with borken NCs
                if verbose: print(f"{api_neutral} Verifying batch {chunk_id}/{len(chunks) - 1}...")
                if len(fastas) != len(chunk): # One or more NCs are missing
                    fastas = __fixBrokenBatch__(fastas, chunk, chunk_id, len(chunks) - 1, verbose)
        
                # Try the twin method
                recovered_indexes = []
                if use_twins is True:
                    useq = __getUnkownSeqs__(fastas, useTwins=use_twins, log=log, verbose=verbose)
                    twins = __useTwins__(useq, verbose)
                    if twins is None:
                        print("%s Twins method failed." % api_warning)
                        fastas = None
                    else:
                        for (i, twin, twin_name) in twins:
                            if not __isUseq__(twin):
                                print("%s Recovered sequence '%s' with '%s'!"
                                    % (api_goodnews, fastas[i].name, twin_name))
                            else:
                                print("%s Could not recover sequence '%s'."
                                      % (api_warning, fastas[i].name))
                            fastas[i] = twin
                            recovered_indexes.append(i)

                # Remove Unknown sequences  
                if delete_USeq is True:
                    useq = useq if use_twins is True else __getUnkownSeqs__(fastas, log=log, verbose=verbose)
                    for (i, _) in useq:
                        if i not in recovered_indexes:
                            fastas[i] = None    
                    if len(useq) - len(recovered_indexes):
                        print(f"{api_warning} {len(useq) - len(recovered_indexes)} NC(s) defaulted to None.")
                
            fastas_result += fastas

        print(f"{api_neutral} API is done and closed!")
        if log is not None: log.emit("done.")
        return fastas_result, len(NC_list) != len([x for x in fastas_result if x is not None])

    except Exception as e:
        if debug is True:
            raise Exception(e)
        print(e)
        print(f"{api_error} API fatal error.")
        return [None]


# Some Unit Tests
if __name__ == '__main__':
    print(f"{api_neutral} Testing API...")
    assert len(efetch("NC_010991", debug=True)) == 1
    print(f"{api_goodnews} OK.\n")
    print(f"{api_neutral} Testing API recovery...")
    assert len(efetch(["NC_016049", "NC_008318"], use_twins=True, debug=True)) == 2
    print(f"{api_goodnews} OK.\n")
    print(f"{api_neutral} Testing API error response...")
    assert efetch("testing", debug=True)[0] is None
    print(f"{api_goodnews} OK.\n")
    print(f"{api_neutral} Testing API batching...")
    assert len(efetch(["NC_010984", "NC_010989", "NC_010990", "NC_010991", "NC_020103", "NC_020100", 
            "NC_020101", "NC_020102", "NC_014360", "NC_021222", "NC_021223", "NC_010985",
            "NC_010986", "NC_013699", "NC_006937", "NC_013469", "NC_013470", "NC_013471",
            "NC_020252", "NC_023983", "NC_001782", "NC_017915", "NC_014359"], batch_size=5)) == 23
    print(f"{api_goodnews} OK.\n")
    print(f"{api_neutral} Testing API with broken batch (1)...")
    data = ["NC_008318", "NC_010984", "NC_010989", "NC_010990", "NC_010991", "NC_020103", "NC_020100", 
            "NC_020101", "NC_020102", "NC_014360", "NC_021222", "NC_021223", "fst_error",
            "NC_010986", "NC_013699", "NC_006937", "NC_013469", "NC_013470", "NC_013471",
            "NC_020252", "NC_023983", "NC_001782", "NC_017915", "NC_014359", "snd_error"]

    tmp, _ = efetch(data, use_twins=True, debug=True, batch_size=5)
    assert len(tmp) == 25, f"received {len(tmp)}."
    assert tmp[-1] is None
    assert tmp[-2] is not None
    print(f"{api_goodnews} OK.\n")
    print(f"{api_neutral} Testing API with broken batch (2)...")
    data = ["NC_014359", "NC_010984", "NC_010989", "NC_010990", "NC_010991", "NC_020103", "aekoeakd", 
            "adkokjaod", "dkzejfzie", "xkxkxkxkjze"]

    tmp, _ = efetch(data, use_twins=True, debug=True, batch_size=5)
    assert len(tmp) == 10, f"received {len(tmp)}."
    for k in range(4):
        assert tmp[-(k+1)] is None
    print(f"{api_neutral} Testing API with broken batch (3)...")
    data = ["NC_014359", "NC_010984", "NC_010989", "NC_010990", "NC_010991", "NC_008318", "aekoeakd", 
            "adkokjaod", "dkzejfzie", "xkxkxkxkjze"]

    tmp, _ = efetch(data, use_twins=True, debug=True, batch_size=5)
    assert len(tmp) == 10, f"received {len(tmp)}."
    assert tmp[-5].name == "NC_008318"
    for k in range(4):
        assert tmp[-(k+1)] is None
    print(f"{api_goodnews} OK.\n")

    print(f"{api_neutral} Testing API performance with large batch...")
    data = ['NC_001275', 'NC_022074', 'NC_019327', 'NC_019337', 'NC_004991', 'NC_007293', 'NC_010177', 'NC_008691', 'NC_015183', 'NC_015508', 'NC_015184', 'NC_002575', 'NC_010841', 'NC_002377', 'NC_010929', 'NC_006277', 'NC_019555', 'NC_002147', 'NC_016617', 'NC_016594', 'NC_016618', 'NC_016595', 'NC_016596', 'NC_016619', 'NC_016597', 'NC_006374', 'NC_004308', 'NC_010615', 'NC_017082', 'NC_010917', 'NC_004527', 'NC_004458', 'NC_025155', 'NC_024993', 'NC_024994', 'NC_024995', 'NC_025011', 'NC_007706', 'NC_002033', 'NC_019287', 'NC_019288', 'NC_019273', 'NC_019316', 'NC_019366', 'NC_013513', 'NC_019289', 'NC_019315', 'NC_025023', 'NC_021239', 'NC_021240', 'NC_021241', 'NC_019367', 'NC_019319', 'NC_019356', 'NC_019314', 'NC_004160', 'NC_022535', 'NC_022545', 'NC_022536', 'NC_013548', 'NC_019229', 'NC_010927', 'NC_019364', 'NC_019363', 'NC_019362', 'NC_019313', 'NC_004965', 'NC_013545', 'NC_016000', 'NC_025133', 'NC_008246', 'NC_008247', 'NC_014466', 'NC_002978', 'NC_018267', 'NC_019019']
    tmp, _ = efetch(data, debug=True, verbose=True)
    print(f"{api_goodnews} OK.\n")
