import os
from API import efetch
from genbank_manager import manager

head = "[\033[94mWriter\033[0m]"
warning = "[\033[93mWriter warning\033[0m]"

DEFAULT_VALID_REGIONS = ["CDS","centromere","exon","mobile_element","ncRNA","rRNA","telomere","tRNA","3'UTR","5'UTR"]

class NC :
    def __init__ (self, path, fasta_list, region, log, valid_regions=DEFAULT_VALID_REGIONS) :
        self.cache_path = os.path.join(".cache_Genbank", path)
        self.genbank_path = os.path.join("Genbank", path)
        self.fasta_list = fasta_list
        self.exists = False if region != "Toutes" else True
        self.region = region
        self.valid_regions = valid_regions
        self.ignored_regions = []
        self.downloaded_features = []

        for fasta in self.fasta_list :
            if fasta is not None :
                self.write_fasta(fasta)

        if os.path.exists(os.path.join(self.cache_path, ".meta.json")):
            print(f"{warning} .meta file already exists. Manager error ?")
        else:
            manager(path, region).create_metadata(self.downloaded_features)
            print(f"{head} Sucessfuly created file {os.path.join(self.cache_path, '.meta.json')}")

        if len(self.ignored_regions):
            print(f"{head} Ignored feature type(s): {' '.join(self.ignored_regions)}")

        if len(self.downloaded_features) == 0 and region == "Toutes":
            log.emit(f"warning: No regions were found for organism '{path}' !")

    def write_fasta(self, fasta) :
        sequence = fasta.seq

        nc_name = fasta.annotations["accessions"][0]
        organism_name = os.path.basename(self.genbank_path[:-1])


        for feature in fasta.features:
            if self.valid_regions is not None and feature.type not in self.valid_regions:
                if feature.type not in self.ignored_regions:
                    self.ignored_regions.append(feature.type)
                continue

            self.downloaded_features.append(feature.type)

            region = feature.type
            if region == self.region :
                self.exists = True

            if self.region == region or self.region == "Toutes" :
                complete_path = os.path.join(self.genbank_path, region)
            else :
                complete_path = os.path.join(self.cache_path, region)

            if not os.path.exists(complete_path) :
                try:
                    os.mkdir(complete_path)
                    print(f"{head} Sucessfuly created directory '{complete_path}'")
                except OSError:
                    print(f"{warning} Creation of the directory '{complete_path}' failed.")

            file_name = region + '_' + organism_name + '_' + nc_name + ".txt"
            title = region + " " + organism_name + " " + nc_name

            operation = feature.location_operator #none ou join
            sub_seq = ""

            if operation == "join" :
                tab_introns = []
                tab_exons = []

                #get exons parts as a string
                all_exons = "("
                last_end = None
                all_complement = True
                pb_happened = False
                no_introns = False
                for idx, part in enumerate(feature.location.parts) :
                    if ("<" in str(part.start)) or (">" in str(part.start)) or ("<" in str(part.end)) or (">" in str(part.end)):
                        pb_happened = True
                        continue

                    if int(part.start) <= int(part.end) and (last_end == None or last_end < int(part.start)) :
                        if last_end == int(part.start)-1: # les 2 sequences jointes se suivent
                            no_introns = True
                        tab_exons.append((int(part.start),int(part.end), part.strand))
                        if part.strand == 1 :
                            all_complement = False
                        last_end = int(part.end)

                    else :
                        pb_happened = True
                        continue

                    if not no_introns:
                        if idx % 2 == 0 :
                            #pair : prend la fin
                            tab_introns.append(int(part.end)+1)
                        else :
                            #impair : prend le début
                            tab_introns.append(int(part.start)) # pas de -1 car borne sup exclue

                    all_exons = all_exons + str(part.start) + ".." + str(part.end) + ","

                if not pb_happened: # on écrit rien sur ce join s'il y a eu un pb
                    all_exons = all_exons[0:len(all_exons)-1]
                    all_exons += ")"

                    title_exons = region + " " + organism_name + " " + nc_name + " join" + all_exons
                    title_introns = "intron" + " " + organism_name + " " + nc_name + " join" + all_exons
                    file_path_exons = os.path.join(complete_path, file_name)

                    if all_complement:
                        title_exons = region + " " + organism_name + " " + nc_name + " complement(join" + all_exons +")"
                        title_introns = "intron" + " " + organism_name + " " + nc_name + " complement(join" + all_exons + ")"

                    file_name_introns = "intron" + '_' + organism_name + '_' + nc_name + ".txt"

                    if self.region == "Toutes" or self.region == "intron":
                        path_introns = os.path.join(self.genbank_path, "Intron")
                    else :
                        path_introns = os.path.join(self.cache_path, "Intron")

                    if not os.path.exists(path_introns) and not no_introns:
                        try:
                            os.mkdir(path_introns)
                            print(f"{head} Sucessfuly created directory '{path_introns}'")
                        except OSError:
                            print(f"{warning} Creation of the directory '{path_introns}' failed.")

                    if not no_introns:
                        self.write_introns(os.path.join(path_introns, file_name_introns), title_introns, sequence, tab_introns, all_complement)

                    self.write_exons(file_path_exons, title_exons, sequence, tab_exons, all_complement)



            else : #no join
                if (("<" in str(feature.location.start)) or (">" in str(feature.location.start))
                or ("<" in str(feature.location.end)) or (">" in str(feature.location.end))):
                    continue

                if int(feature.location.start) < int(feature.location.end) :
                    file_path = os.path.join(complete_path, file_name)
                    file_output = open(file_path, mode='a+')

                    if feature.location.strand == -1 :
                        sub_seq = str(sequence[feature.location.start : feature.location.end].reverse_complement())
                        title += " complement"
                    else :
                        sub_seq = str(sequence[feature.location.start : feature.location.end])

                    file_output.write(title + " (" + str(feature.location.start) + ":" + str(feature.location.end) + ")\n")
                    file_output.write(sub_seq + "\n")


    def write_exons (self, file_path, title, sequence, tab_exons, all_complement) :
        if all_complement :
            tab_exons.reverse() # pour les prendre depuis la fin
        file_output = open(file_path, mode='a+')
        global_seq = ""

        for tuple in tab_exons :
            if all_complement:
                global_seq += sequence[tuple[0]:tuple[1]].reverse_complement()
            else:
                global_seq += sequence[tuple[0]:tuple[1]]

        file_output.write(title + "\n")
        file_output.write(str(global_seq)+ "\n")

        for idx, tuple in enumerate(tab_exons) :
            file_output.write(title + "EXON " + str(idx+1)+ "\n")
            if tuple[2] == -1 : #cplmt
                file_output.write(str(sequence[tuple[0] : tuple[1]].reverse_complement())+ "\n")
            else :
                file_output.write(str(sequence[tuple[0] : tuple[1]]) + "\n")



    def write_introns (self, file_path, title, sequence, tab_introns, all_complement) :
        self.downloaded_features.append("intron")

        file_output = open(file_path, mode='a+')
        global_seq = ""

        n = len(tab_introns)
        nb_introns = n//2

        for i in range(nb_introns):
            if all_complement:
                k = (nb_introns-i-1)*2 # commence par la fin
                global_seq += sequence[tab_introns[k]:tab_introns[k+1]].reverse_complement()
            else:
                k = i*2
                global_seq += sequence[tab_introns[k]:tab_introns[k+1]]

        file_output.write(title + "\n")
        file_output.write(str(global_seq) + "\n")

        if (nb_introns > 1):
            for i in range (nb_introns) :
                file_output.write(title + "INTRON " + str(i+1) + "\n")
                if all_complement:
                    k = (nb_introns-i-1)*2
                    file_output.write(str(sequence[tab_introns[k]:tab_introns[k+1]].reverse_complement()) + "\n")
                else:
                    k = i*2
                    file_output.write(str(sequence[tab_introns[k]:tab_introns[k+1]]) + "\n")
