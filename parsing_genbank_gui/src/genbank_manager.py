import os
import json
import shutil
import time
import random

head = "[\033[94mGenbank Manager\033[0m]"
error = "[\033[91mGenbank Manager error\033[0m]"

class manager:
    """
    """
    def __init__(self, path, region, bar=None, all_region_token="Toutes", verbose=True,
                 from_genbank=False, from_cache=False):
        if from_genbank is True:
            path = path[len("Genbank/"):]
        if from_cache is True:
            path = path[len(".cache_Genbank/"):]
        
        if bar is not None:
            bar(0)
            for k in range(random.randint(5,10)):
                bar(k*10)
                time.sleep(random.randint(0, 3) * 0.02)

        self.region = region
        self.verbose = verbose
        self.path = path
        self.genbank_path = os.path.join("Genbank", path)
        self.cache_path = os.path.join(".cache_Genbank", path)
        self.meta_path = os.path.join(self.cache_path, ".meta.json")

        self.genbank_path_w_region = os.path.join(self.genbank_path, region)
        self.cache_path_w_region = os.path.join(self.cache_path, region)

        if verbose is True:
            print(f"{head} Receiving general path '{path}' on region '{region}'.")

        self.already_downloaded = os.path.exists(self.meta_path)

        self.attempted_unavailable_regions = []

        self.is_region_all = region == all_region_token

        if self.already_downloaded:
            with open(self.meta_path, "r") as f:
                metadata = json.load(f)
                for p in metadata['metadata']:
                    self.curently_in_genbank = p['curently_in_genbank']
                    self.curently_in_cache = p['curently_in_cache']
                    self.overall_available_regions = p['overall_available_regions']
                    self.attempted_unavailable_regions = p['attempted_unavailable_regions']
                    self.full_download_done = p['full_download_done']
                    self.recovery_possible = p['recovery_possible']

            if self.is_region_all is not True:
                self.path_in_genbank = region in self.curently_in_genbank
                self.path_in_cache = region in self.curently_in_cache
                self.unavailable_region = region not in self.overall_available_regions
            else:
                self.path_in_genbank = len(self.curently_in_genbank) == len(self.overall_available_regions)   
                self.path_in_cache = not self.path_in_genbank
                self.unavailable_region = len(self.overall_available_regions) == 0
                if self.unavailable_region:
                    self.path_in_genbank = False
        else:
            self.curently_in_genbank = []
            self.curently_in_cache = []
            self.overall_available_regions = []
            self.full_download_done = False
            self.path_in_genbank = False
            self.path_in_cache = False
            self.unavailable_region = False
            self.recovery_possible = False

        if verbose is True:
            print(f"{head} Stored in Genbank ? {self.path_in_genbank} | Stored in cache ? {self.path_in_cache} | Unavailable region ? {self.unavailable_region}")
        
        if bar is not None:
            bar(100)
            time.sleep(0.04)

    def create_metadata(self, downloaded_regions):
        if self.already_downloaded is True:
            print(f"{error} Cannot create .meta.json file. File exists.")
            return

        downloaded_regions = list(set(downloaded_regions))
        if self.is_region_all:
            curently_in_genbank = downloaded_regions
            curently_in_cache = []
            if len(downloaded_regions) == 0:
                attempted_unavailable_regions = [self.region]
            else:
                attempted_unavailable_regions = []
        else:
            if self.region in downloaded_regions:
                curently_in_genbank = [self.region]
                curently_in_cache = [r for r in downloaded_regions if r != self.region]
                attempted_unavailable_regions = []
            else:
                curently_in_genbank = []
                curently_in_cache = downloaded_regions
                attempted_unavailable_regions = [self.region]

        metadata = {}
        metadata['metadata'] = []
        metadata['metadata'].append({
            'curently_in_genbank': curently_in_genbank,
            'curently_in_cache': curently_in_cache,
            'overall_available_regions': downloaded_regions,
            'attempted_unavailable_regions': attempted_unavailable_regions,
            'full_download_done': self.is_region_all,
            'recovery_possible': False
        })

        if self.verbose:
            print(f"{head} Creating metadata: '{metadata}'.")

        with open(self.meta_path, 'w') as f:
            json.dump(metadata, f)

    def update_metadata(self):
        if not self.already_downloaded:
            print(f"{error} Should not update not yet downloaded organism (at update_metadata).")
            return

        if self.is_region_all is not True:
            new_curently_in_genbank = list(set(self.curently_in_genbank + [self.region])) 
            new_curently_in_cache = list(set([r for r in self.curently_in_cache if r != self.region]))
        else:
            new_curently_in_genbank = self.overall_available_regions
            new_curently_in_cache = []

        metadata = {}
        metadata['metadata'] = []
        metadata['metadata'].append({
            'curently_in_genbank': new_curently_in_genbank,
            'curently_in_cache': new_curently_in_cache,
            'overall_available_regions': self.overall_available_regions,
            'attempted_unavailable_regions': list(set(self.attempted_unavailable_regions)),
            'full_download_done': self.is_region_all or self.full_download_done,
            'recovery_possible': self.recovery_possible
        })

        with open(self.meta_path, 'w') as f:
            json.dump(metadata, f)

    def add_attempted_unavailable_regions(self):
        if not self.already_downloaded:
            print(f"{error} Should not update not yet downloaded organism (at add_attempted_unavailable_regions).")
        
        new_full_donwload_done = self.full_download_done
        new_attempted_unavailable_regions = list(set(self.attempted_unavailable_regions))
        
        if not self.is_region_all:
            new_attempted_unavailable_regions = list(set(self.attempted_unavailable_regions + [self.region]))
        if self.is_region_all and len(self.overall_available_regions) == 0:
            new_attempted_unavailable_regions = list(set(self.attempted_unavailable_regions + [self.region]))
            new_full_donwload_done = True

        metadata = {}
        metadata['metadata'] = []
        metadata['metadata'].append({
            'curently_in_genbank': self.curently_in_genbank,
            'curently_in_cache': self.curently_in_cache,
            'overall_available_regions': self.overall_available_regions,
            'attempted_unavailable_regions': new_attempted_unavailable_regions,
            'full_download_done': new_full_donwload_done,
            'recovery_possible': self.recovery_possible
        })

        with open(self.meta_path, 'w') as f:
            json.dump(metadata, f)


    def add_recovery_possible(self):
        if not self.already_downloaded:
            self.create_metadata()
        
        metadata = {}
        metadata['metadata'] = []
        metadata['metadata'].append({
            'curently_in_genbank': self.curently_in_genbank,
            'curently_in_cache': self.curently_in_cache,
            'overall_available_regions': self.overall_available_regions,
            'attempted_unavailable_regions': self.attempted_unavailable_regions,
            'full_download_done': self.full_download_done,
            'recovery_possible': True
        })

        print(f"{head} Updated metadata: {metadata}")

        with open(self.meta_path, 'w') as f:
            json.dump(metadata, f)


    def move_to_genbank(self):
        # Move region to Genbank
        if not self.is_region_all:
            shutil.move(self.cache_path_w_region, self.genbank_path_w_region)
            print(f"{head} Sucessfuly moved '{self.cache_path_w_region}' to '{self.genbank_path_w_region}'")
        # Move all (available) regions to Genbank
        else:
            for dir in os.listdir(self.cache_path):
                dir = os.path.join(self.cache_path, dir)
                if os.path.isdir(dir):
                    try:
                        shutil.move(dir, self.genbank_path)
                        print(f"{head} Sucessfuly moved '{dir}' to '{self.genbank_path}'")
                    except Exception as e:
                        print(f"{error} Fatal error:\n {e}")


    def move_and_update(self):
        if not self.already_downloaded:
            print(f"{error} move_and_update() should not be called before download.")
            return False
        if self.unavailable_region:
            self.add_attempted_unavailable_regions()
            return False

        self.move_to_genbank()
        self.update_metadata()

        return True


    def reset_organism(self):
        for region in self.overall_available_regions:
            region_in_cache = os.path.join(".cache_Genbank", self.path, region)
            region_in_genbank = os.path.join("Genbank", self.path, region)

            if os.path.exists(region_in_cache):
                shutil.rmtree(region_in_cache)
                print(f"{head} Sucessfuly removed '{region_in_cache}' (after reset signal received)")
            if os.path.exists(region_in_genbank):
                shutil.rmtree(region_in_genbank)
                print(f"{head} Sucessfuly removed '{region_in_genbank}' (after reset signal received)")
        meta_path = os.path.join(".cache_Genbank", self.path, ".meta.json")
        os.remove(meta_path)
        print(f"{head} Sucessfuly removed '{meta_path}' (after reset signal received)")


    def get_icon_type(self):
        """
        usage: case_idx = genbank_manager(path, region, verbose=False).get_icon_type()
        # Ici path est le chemin relatif sans Genbank/ ou .cache_Genbank/ avant

        cas 0: Rien n'a été téléchargée dans le cache OU la région existe mais est encore dans le cache
        cas 1: La région est dans genbank
        cas 2: La région n'existe pas
        cas 3: cache != genbank
        """
        if not self.already_downloaded or self.region in self.curently_in_cache:
            return 0

        if self.is_region_all:
            if self.full_download_done and "Toutes" not in self.attempted_unavailable_regions:
                return 1
            if "Toutes" in self.attempted_unavailable_regions:
                return 2
            if not self.full_download_done:
                return 3
        else:
            if self.region in self.curently_in_genbank:
                return 1
            if self.region in self.attempted_unavailable_regions:
                return 2
            if self.full_download_done:
                return 2
