import time
from multiprocessing import Pool

import pandas as pd
import os
import shutil
import re
import logging

from src.download_ncbi import download_ncbi


class Pretraitement:
    def __init__(self):
        self.genbank_path = 'Genbank'
        self.cache_genbank_path = '.cache_Genbank'
        self.ncbi_files = "ncbi"
        self.tab = []
        self.create_folder()

        dt1 = time.time()

        data_path = self.ncbi_files
        ids_path = os.path.join(data_path, "IDS")

        # IDS PATH
        bacteria_path = os.path.join(ids_path, "Bacteria.ids")
        eukaryota_path = os.path.join(ids_path, "Eukaryota.ids")
        archaea_path = os.path.join(ids_path, 'Archaea.ids')
        viruses_path = os.path.join(ids_path, 'Viruses.ids')

        # OVERVIEW PATH
        overview_path = os.path.join(data_path, "overview.txt")

        # LOAD IDS IN  DATAFRAMES
        paths = [bacteria_path, eukaryota_path, archaea_path, viruses_path]
        with Pool(5) as p:
            self.bacteria, self.eukaryota, self.archaea, self.viruses = p.map(self.read_csv, paths)

        self.overview = pd.read_csv(overview_path, sep='\t')
        self.overview.set_index('Kingdom', append=True)

        self.nb_organism = self.overview.shape[0]
        dt2 = time.time()
        print("Elapsed time for downloading is {}".format(dt2 - dt1))

        # SPEED SEARCH BY NAME
        self.bacteria_group_by = self.bacteria.groupby("name")
        self.eukaryota_group_by = self.eukaryota.groupby("name")
        self.archaea_group_by = self.archaea.groupby("name")
        self.viruses_group_by = self.viruses.groupby("name")

    def create_folder(self):
        """
        This function create folders in which we put data.
        cache_genbank_path is a mirror of genbank_path. genbank_path contains downloaded organisme with their
        sequences. ncbi_files contains files fetch from ncbi site (overview.txt, IDS)
        """

        if os.path.exists(self.genbank_path):
            shutil.rmtree(self.genbank_path)

        if os.path.exists(self.cache_genbank_path):
            shutil.rmtree(self.cache_genbank_path)

        if not os.path.exists(self.ncbi_files):
            download_ncbi("ncbi")

        if not os.path.exists(self.genbank_path):
            os.mkdir(self.genbank_path)

        if not os.path.exists(self.cache_genbank_path):
            os.mkdir(self.cache_genbank_path)

    def read_csv(self, path):
        # Read an ids file and load i in a dataframe
        organism = pd.read_csv(path, header=None, sep='\t')
        organism.columns = ['A', 'NC', 'C', 'D', 'E', 'name', 'G']
        organism.set_index('name', append=True)
        organism.set_index('NC', append=True)
        return organism

    def NC_research(self, organism, kingdom):
        """
        This function return a tab with all NC associated to an organism.
        """
        ids_file = None
        if kingdom == "Bacteria":
            ids_file = self.bacteria_group_by
        elif kingdom == "Eukaryota":
            ids_file = self.eukaryota_group_by
        elif kingdom == "Archaea":
            ids_file = self.archaea_group_by
        elif kingdom == "Viruses":
            ids_file = self.viruses_group_by

        tab = []
        if ids_file is not None:
            try:
                matching_organism = ids_file.get_group(organism)
            except KeyError:
                matching_organism = None

            if matching_organism is not None:
                nb_match = matching_organism.shape[0]
                for i in range(nb_match):
                    if matching_organism["NC"].iloc[i].startswith("NC"):
                        tab.append(matching_organism["NC"].iloc[i])

        return tab

    def create_genbank(self):
        dt2 = time.time()

        lines = [i for i in range(self.nb_organism)]
        with Pool(5) as p:
            p.map(self.one_step, lines)

        dt3 = time.time()
        print("Elapsed time for NC {}".format(dt3 - dt2))

    def one_step(self, i):
        organism = self.overview['#Organism/Name'][i]

        # on crée tous les dossiers qui vont bien s'ils n'existent pas déjà
        kingdom = self.overview['Kingdom'][i]
        tab = self.NC_research(organism, kingdom)

        if len(tab) != 0:
            kingdom_path = os.path.join(self.genbank_path, kingdom)
            if not os.path.exists(kingdom_path):
                os.mkdir(kingdom_path)

            cache_kingdom_path = os.path.join(self.cache_genbank_path, kingdom)
            if not os.path.exists(cache_kingdom_path):
                os.mkdir(cache_kingdom_path)

            group = self.overview['Group'][i]
            group = re.sub('([a-z]*)/([a-z]*)', "\g<1> \g<2>", group)  # replace the '/' by a space
            group_path = os.path.join(kingdom_path, group)
            if not os.path.exists(group_path):
                os.mkdir(group_path)

            cache_group_path = os.path.join(cache_kingdom_path, group)
            if not os.path.exists(cache_group_path):
                os.mkdir(cache_group_path)

            subgroup = self.overview['SubGroup'][i]
            subgroup = re.sub('([a-z]*)/([a-z]*)', "\g<1> \g<2>", str(subgroup))  # replace the '/' by a space
            subgroup_path = os.path.join(group_path, subgroup)
            if not os.path.exists(subgroup_path):
                os.mkdir(subgroup_path)

            cache_subgroup_path = os.path.join(cache_group_path, subgroup)
            if not os.path.exists(cache_subgroup_path):
                os.mkdir(cache_subgroup_path)

            with open(os.path.join(subgroup_path, "NC.txt"), "a+", newline='') as f:
                for nc in tab:
                    f.write(nc + ";")

            with open(os.path.join(cache_subgroup_path, "NC.txt"), "a+", newline='') as f:
                for nc in tab:
                    f.write(nc + ";")


def pretraitement(max_attempts=3):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    for k in range(max_attempts):
        try:
            pretrait = Pretraitement()
            pretrait.create_genbank()
            break
        except Exception as e:
            if os.path.exists(".cache_Genbank"):
                shutil.rmtree(".cache_Genbank")
            if os.path.exists("Genbank"):
                shutil.rmtree("Genbank")
            if os.path.exists("ncbi"):
                shutil.rmtree("ncbi")

            if k != max_attempts - 1:
                logging.error(str(e))
                logging.error(f"Attempt number {k + 1} out of {max_attempts} failed. Retrying.")
            else:
                raise Exception("Too many failed attempts at initializing ncbi. Aborted.")

    print("done.")
