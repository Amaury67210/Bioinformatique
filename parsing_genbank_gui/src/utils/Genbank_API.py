import os, shutil, re, time
from Bio import Entrez, SeqIO


class Genbank_API:
    """
    This class is used to call the genbank API and fetch an NC id.

    """

    def __init__(self, email="A.N.Other@example.com", db="nucleotide",
                 rettype="gb", style="withparts", retmode="full",
                 valid_types=["CDS","centromere","intron","mobile_element","ncRNA","rRNA","telomere","tRNA","3'UTR","5'UTR"]):
        """

        Initializes a Genbank_API object, that is ready to call the api.

        Paramaters
        ----------
        email: The email used to call the API.

        db: Database from which to retrieve records. The value must be a valid
        Entrez database name
        (default = nucleotide).

        rettype: Retrieval type. This parameter specifies the record view returned,
        (default = gb)

        style:

        retmode:
        Retrieval type. Determines the format of the returned output.
        (defaultl = full)

        valid_types:
        valid types for a feature types. All other types will be ignored
        """
        self.email = email
        Entrez.email = email
        self.db = db
        self.rettype = rettype
        self.style = style
        self.retmode = retmode
        self.valid_types = valid_types


    def parse_features (self, fasta) :
        '''
        fasta : SeqRecord object (biopython) 
        '''
        print("DEBUT SEQ FATSA")
        print(fasta)
        seq = fasta.seq
        type_list, location_operator_list, location_list = [], [], []

        for feature in fasta.features:
            if str(feature.type) not in self.valid_types:
                continue

            location_list_per_part = []
            for part in feature.location.parts:
                if "<" in str(part) or ">" in str(part):
                    continue
                if int(part.start) < int(part.end) : 
                    location_list_per_part.append([int(part.start), int(part.end)])

            if location_list_per_part == []:
                continue

            location_list.append(location_list_per_part)
            type_list.append(feature.type)
            location_operator_list.append(feature.location_operator)
        
        return [seq, type_list, location_operator_list, location_list]


    def write_files (self, seq, type_list, location_operator_list, 
        location_list, root, nc, quiet = True):
        """
        """
        for i in range (len(type_list)):
            #print(i)
            # Crée le dossier associé au type (intron, CDS etc)
            path = os.path.join(root, str(type_list[i]))
            if os.path.exists(path) == False :
                try:
                    os.mkdir(path)
                except OSError:
                    print ("warning: creation of the directory %s failed" % path)
                else:
                    if not quiet:
                        print ("Successfully created the directory %s " % path)
            elif i == 0:
                if not quiet:
                    print("Folder already existes %s" % path)

            # Découpe la bonne partie de la séquence
            location = location_list[i] #début-fin
            mode = location_operator_list[i]

            #vérifier si le couple est valide 
            if mode == "None" : 
                gene = seq[(location[0][0]-1) : location[0][1]]

            elif mode == "join" : #join : location = liste de couples. 
                gene = ""
                c0 = location[0]
                c1 = location[1]
                i = 1 
                n = len(location) 

                #vérifie la concordance intercouples : (x1, y1) ; (x2, y2) :
                #on a x1 < y1 et x2 < y2 mais on doit aussi avoir y1 < x2 
                while (i < n-1) and (c0[1] < c1[0]) :
                    c0 = location[i]
                    c1 = location[i+1] 
                    i = i+1 
                
                if i == n : #c'est bon tous les couples sont ok 
                    for couple in location:
                        gene += seq[couple[0]-1 : couple[1]]

            elif mode == "complement" : 
                #complement : location = liste avec 1 seul couple
                a = seq[(location[0][0]-1) : location[0][1]]
                gene = a.reverse_complement()
            
            else :
                #join + complement 
                '''
                location : commencer par la fin 
                pour chaque loc : complementer et écrire '''
                gene = ""
                for couple in location[::-1] : #location mais à l'envers
                    gene += seq[(couple[0] - 1) : couple[1]].reverse_complement()


            # if mode == 1 : #join : location = liste de couples. 
            #     #vérifier la concordance entre TOUS les couples x1 < y1 < x2 ... 
            #     gene = ""
            #     for couple in location:
            #         gene += seq[couple[0]-1 : couple[1]]
            # elif mode == -1 : #complement : location = liste avec 1 seul couple
            #     a = seq[(location[0][0]-1) : location[0][1]]
            #     gene = a.reverse_complement()

            # #manque un mode ? join + complement
 
            # else :
            #     gene = seq[(location[0][0]-1) : location[0][1]]

            # Ecrit la sequence dans le fichier
            #genbank/group/subgroup/organism/cds/NC....txt
            #retrouver le numéro du NC ??? 
            nc_name = nc + ".txt"
            region = os.path.basename(path) 
            dir_name = os.path.dirname(path) 
            organism_name = os.path.basename(dir_name) 

            file_name = region + '_' + organism_name + '_' + nc_name 

            file_output = open(os.path.join(path, file_name), mode='w+')
            file_output.write(region + " " + organism_name + " " + nc_name + "\n")

            file_output.write(str(gene))
            file_output.close()

        try: 
            f = open(os.path.join(root, ".meta"), "w") 
        except:
            raise ValueError ("Could not create .meta file; root path: {}".format(root))
        
        f.close()


    def try_fetch_from_cache (self, path) :
        """
        Tests if the path was already in cache. 
        Returns True if it is the case so fetch does
        not call the API and aborts directly to the
        cache extraction
        """
        for file in os.listdir(path):
            if file == ".meta":
                return True
        return False
    

    def fetch_and_treat_to_cache (self, ids, paths, log, bar, quiet=True):
        """
        Calls the Genbank API for all the NCs.

        If the NC is already in cache, this function does nothing.

        This function fetches an NC and writes the results to .cache_GenBank
        Once the result is written in .cache_GenBank, another function should
        add the result (with only the selected region) to Genbank 

        """
        failures = []

        def fetch_batch (i,j) :
            if not quiet:
                log.emit ("Fetching and parsing batch of NCs [%i:%i]..." % (i,j))

            try :
                handle = Entrez.efetch(db=self.db, rettype=self.rettype, id=ids[i:j])
            except :
                if not quiet:
                    log.emit ("warning: failed to fetch batch of NCs [%i:%i]" % (i,j))
                failures.append ([i,j])
                return False
            try:
                fastas = SeqIO.parse(handle, 'genbank')
            except:
                if not quiet:
                    log.emit ("wrning: failed to parse batch of NCs [%i:%i]" % (i,j))
                failures.append ([i,j])
                return False

            k = 0

            while True:
                try:
                    fasta = next(fastas)
                except:
                    break
                
                seq, type_list, loc_op_list, loc_list = self.parse_features (fasta)
                self.write_files (seq, type_list, loc_op_list, loc_list, paths[i+k], ids[i:j][k])
                if bar != None:
                    bar (k % 100)

                k += 1

            if k == 0 :
                if not quiet:
                    log.emit ("wrning: failed to parse batch of NCs [%i:%i] (empty iterator)" % (i,j))
                return False

            if not quiet:
                log.emit ("Sucessfuly treated NCs' batch [%i:%i]" % (i,j))
            return True

        genbank_batch_size = 200

        for i in range(0, len(ids), genbank_batch_size):
            j = i + genbank_batch_size
            if j >= len(ids):
                j = len(ids)

            fetch_batch (i,j)

        if len(failures) != 0:
            log.emit ("warning: {} error(s) were found. Attempting to correct them...".format(len(failures)))

        max_attempts = 3

        failures_out = []

        for e, i_j in enumerate(failures):
            failures_out = []

            if not quiet:
                log.emit ("Attempt {}.".format(e + 1))
                log.emit ("Trying NC batch [%i:%i] again..." % (i,j))

            if e + 1 == max_attempts:
                break

            time.sleep(3) # Sleeping to prevent an API IP block
            failures_out.append(fetch_batch (i_j[0], i_j[1]))

        if len(failures) != 0 and True not in failures_out:
            log.emit ("error: Unable to fetch. Either the Genbank server or your internet connection might be down.")
            return bar, False

        return bar, True


    def fetch_from_cache (self, cache_path, path, region, log, checked) :
        """
        This function should ONLY be called if fetch_and_treat was called
        previously. It will simply go to the path in the cache, and select
        the region the user wants so we can copy the folder region to the
        Genbank directory
        """
        def __fetch_from_cache__ (reg, quiet):
            if not os.path.exists(os.path.join (cache_path, reg)):
                if not quiet:
                    log.emit ("warning: organism %s has no sequence on region %s" % (path, reg))
                return

            try:
                shutil.copytree(os.path.join (cache_path, reg), os.path.join (path, reg))
            except FileExistsError:
                pass
            except:
                raise ValueError ("shutil copy os cache directory failed. path:", path,
                    "cache_path:", cache_path)

        if region == "Toutes":
            for reg in ["CDS","centromere","intron","mobile_element","ncRNA","rRNA","telomere","tRNA","3'UTR","5'UTR"]:
                __fetch_from_cache__ (reg, True)
        else:
            __fetch_from_cache__ (region, False)

        meta_path = os.path.join(path, ".meta")
        if not os.path.exists(meta_path):
            try:
                f = open(meta_path, 'a')
                f.close()
            except:
                pass


        if checked != None:
            try:
                checked.emit(path)
            except:
                pass

    def fetch_and_treat (self, ids, paths, logs, bar=None, region="CDS", quiet=True, checked=None) :
        if not type(ids) == list:
            ids = [ids] 
        if not type(paths) == list:
            paths = [paths for _ in range(len(ids))]

        new_ids, new_paths = [], []

        for nc, path in zip(ids, paths):
            if not self.try_fetch_from_cache (path):
                new_ids.append(nc)
                new_paths.append(path)

        log, clear_log = logs

        log.emit ("Using {} NCs that are already in cache.".format(len(ids) - len(new_ids)))

        if bar == None:
            _, valid = self.fetch_and_treat_to_cache (new_ids, new_paths, log, bar=bar, quiet=quiet)
        else:
            bar, valid = self.fetch_and_treat_to_cache (new_ids, new_paths, log, bar=bar, quiet=quiet)

        if valid == False:
            return bar

        for src_path in paths:
            dst_path = re.sub(r'.cache_Genbank', 'Genbank', src_path)
            self.fetch_from_cache (src_path, dst_path, region, log, checked)

        clear_log.emit ("done.")

        bar(100)

        return bar