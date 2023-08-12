# coding: utf-8

from fileinput import filename
from ftplib import FTP
from turtle import end_fill
import urllib 
import os
import os.path
from os import path
import pandas as pd
import tkinter as tk
from pathlib import Path
import sys
import shutil
import urllib.request as request
import logging
from contextlib import closing
from Bio.SeqFeature import SeqFeature, FeatureLocation
import ftplib

def create_tree(df):
    df = df.reset_index()
    df = df.dropna()
    print("Création de l'arborescence en cours")
    for index in df.index:
        prefix = "Results/{}/{}/{}/{}/".format(df["Kingdom"][index], df["Group"][index], df["SubGroup"][index], df["#Organism/Name"][index])
        try:
            Path(prefix).mkdir(parents=True, exist_ok=True)
        except:
            continue

def get_dataframe_genome(filename):
    url = 'https://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/'+filename
    file = urllib.request.urlopen(url)
    col_lst = ["#Organism/Name", "Kingdom", "Group", "SubGroup"]
    df = pd.read_csv(file, sep="\t", usecols=col_lst)
    return df

def get_dataframe_kingdom(lst_dataframe, kingdom):
    '''
    Retourne le dataframe correspondant au kingdom
    '''
    for dataframe in lst_dataframe:
        if dataframe['Kingdom'].iloc[0] == kingdom:
            return dataframe

def regroup_organism_by_kingdom(df, kingdom_name):
    '''
    Regroupe les organismes par groupe principal (kingdom)

    Parameters:
        filename (str): Nom du fichier dans lequel on extrait les organismes
        kingdom_lst (list): Liste contenant les noms des différents kingdom

    Returns:
        Liste de DataFrame où chaque DataFrame correspond à un kingdom
    '''
    
    #url = 'https://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/'+filename
    #file = urllib.request.urlopen(url)
    #col_lst = ["#Organism/Name", "Kingdom", "Group", "SubGroup"]
    #df = pd.read_csv(file, sep="\t", usecols=col_lst)
    #df = get_dataframe_genome(filename)
    #create_tree(df)
    #result = [df.loc[df['Kingdom'] == kingdom_name] for kingdom_name in kingdom_lst]
    result = df.loc[(df['Kingdom'] == kingdom_name)]
    #print("Regroupement terminé\n")
    return result

def get_organism_from_group(df, kingdom, group):
    '''
    Renvoie les organismes pour un groupe donné

    Parameters:
        filename (str): Nom du fichier dans lequel on extrait les organismes
        kingdom (str): Nom du groupe principal
        group (str): Nom d'un sous répertoire à kingdom

    Returns:
        DataFrame contenant les organismes pour un group donné
    '''
    #url = 'https://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/'+filename
    #file = urllib.request.urlopen(url)
    #col_lst = ["#Organism/Name", "Kingdom", "Group", "SubGroup"]
    #df = pd.read_csv(file, sep="\t", usecols=col_lst)
    #df = get_dataframe_genome(filename)
    #create_tree(df)
    result = df.loc[(df['Kingdom'] == kingdom) & (df['Group'] == group)]
    #print("Regroupement terminé\n")
    return result

def get_organism_from_subgroup(df, kingdom, group, subgroup):
    '''
    Renvoie les organismes pour un sousgroup donné

    Parameters:
        filename (str): Nom du fichier dans lequel on extrait les organismes
        kingdom (str): Nom du groupe principal
        group (str): Nom d'un sous répertoire à kingdom
        subgroup (str): Nom d'un sous répertoire à group

    Returns:
        DataFrame contenant les organismes pour un sousgroup donné
    '''

    #path = 'GENOME_REPORTS/'+filename
    #url = 'https://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/'+filename
    #file = urllib.request.urlopen(url)
    #col_lst = ["#Organism/Name", "Kingdom", "Group", "SubGroup"]
    #df = pd.read_csv(file, sep="\t", usecols=col_lst)
    #df = get_dataframe_genome(filename)
    #create_tree(df)
    result = df.loc[(df['Kingdom'] == kingdom) & (df['Group'] == group) & (df['SubGroup'] == subgroup)]
    #print("Regroupement terminé\n")
    return result

def get_organism_from_field(df, kingdom, group, subgroup, organism):
    result = df.loc[(df['Kingdom'] == kingdom) & (df['Group'] == group) & (df['SubGroup'] == subgroup) & (df['#Organism/Name'] == organism)]
    return result

def search_nc_by_organism(kingdom, organism_name, df_log):
    '''
    Renvoie tous les NC correspondant à un organisme

    Parameters:
        kingdom (str): Nom du groupe principal
        organism_name (str): Nom de l'organisme à traiter
    
    Returns:
        Liste des NC pour un organisme donné
    '''
    path = 'GENOME_REPORTS/IDS/'+kingdom+".ids"
    df = pd.read_csv(path, sep="\t", header=None)
    df.columns = ["1", "NC", "3", "4", "5", "Organism", "7"]
    df_tmp = df[df['NC'].str.contains('NC_')]
    nc_organism = df_tmp[["NC", "Organism"]]
    result = nc_organism[[organism_name in organism for organism in nc_organism['Organism']]]["NC"]
    #result = nc_organism.loc[nc_organism["Organism"].str.contains(organism_name, regex=False), "NC"]
    #result = nc_organism.loc[nc_organism["Organism"].str.contains(organism_name), "NC"]
    df_result = result.to_frame()

    #df_result[~df_result.apply(tuple,1).isin(df_log.apply(tuple,1))]
    res = pd.concat([df_result, df_log]).drop_duplicates(keep=False)
    #res = res.reset_index(drop=True)
    #df_gpby = res.groupby(list(res.columns))
    #idx = [x[0] for x in df_gpby.groups.values() if len(x) == 1]
    #res.reindex(idx)
    return res['NC'].values.tolist()

def has_valid_boundary(a, b, max_length):
    if ((not a.isdigit()) or (int(a) > max_length)):
        return False
    if (b == None):
        return True
    if ((not b.isdigit()) or (int(b) > max_length)):
        return False
    if (int(a) > int(b)):
        return False
    return True

def write_available_feature(record, prefix_path, regions, kingdom, name_organism):
    '''
    Renvoie les régions valides

    Parameters:
        features (list): Liste des régions trouvées dans un NC 

    Returns:
        Liste correspondant à l'intersection des listes features et regions
    '''
    #print(f"Dans {prefix_path}")
    #prefix = f"{prefix_path}{name_organism}"
    range_index = ""
    region_to_parse = []
    for region in regions:
        if (not path.exists(f"{prefix_path}/{region}_{name_organism}_{record.name}.txt")):
            region_to_parse.append(region)

    for feature in record.features:
        if ((feature.type not in region_to_parse) and ((feature.type != "CDS") or ("intron" not in region_to_parse))):
            continue

        if(not has_valid_boundary(str(feature.location.parts[0].start), str(feature.location.parts[0].end), len(record.seq))):
            continue
        filename = f"{prefix_path}/{feature.type}_{name_organism}_{record.name}.txt"
        #Path(prefix+"/").mkdir(parents=True, exist_ok=True)
        filepath = f"{prefix_path}/"
        isExist = os.path.exists(filepath)
        if not isExist:
            try:
                os.makedirs(filepath)
            except OSError:
                print(f"{filepath} n'est pas un chemin valide")
        if feature.location_operator == None: # ne contient pas un opérateur join
            if (feature.type in region_to_parse):
                range_index = str(feature.location.parts[0].start+1)+".."+str(feature.location.parts[0].end)
                if feature.strand == 1:
                    name_request = "{} {} {}: {}".format(feature.type, record.annotations["organism"], record.name, range_index)
                elif feature.strand == -1:
                    name_request = "{} {} {}: complement({})".format(feature.type, record.annotations["organism"], record.name, range_index)
                try:
                    with open(filename, 'a+') as external_file:
                        print("Dans",filename)
                        print(name_request, file=external_file)
                        print(feature.extract(record.seq), file=external_file)
                        print(f"Extraction feature {feature.type} réussie")
                except OSError:
                    #print(f"{filename} impossible à traiter")
                    continue
        elif feature.location_operator == "join":
            l = []
            for part in feature.location.parts:
                if(not has_valid_boundary(str(part.start), str(part.end), len(record.seq))):
                    break
                l.append(str(part.start+1)+".."+str(part.end))
            range_index = ",".join(l)
            if feature.strand == 1:
                seq_valid = True
                for i in range (len(l)-1):
                    curr_part = l[i].split("..")
                    next_part = l[i+1].split("..")
                    if (curr_part[1] > next_part[0]):
                        seq_valid = False
                        break
                if not seq_valid:
                    continue
                name_request = "{} {} {}: join({})".format(feature.type, record.annotations["organism"], record.name, range_index)
                exon_order = feature.location.parts
            elif feature.strand == -1:
                l.reverse()
                seq_valid = True
                for i in range (len(l)-1):
                    curr_part = l[i].split("..")
                    next_part = l[i+1].split("..")
                    if (curr_part[1] > next_part[0]):
                        seq_valid = False
                        break
                if not seq_valid:
                    continue
                range_index = ",".join(l)
                #exon_order = reversed(feature.location.parts)
                name_request = "{} {} {}: complement(join({}))".format(feature.type, record.annotations["organism"], record.name, range_index)
            else:
                continue
            if feature.type == "CDS":
                if "CDS" in region_to_parse:
                    feature_part_name = "Exon"
                    location = []
                    for part in feature.location.parts:
                        location.append([int(part.start),int(part.end)])
                    if feature.strand == 1:
                        seq_valid = True
                        for i in range (len(l)-1):
                            curr_part = l[i].split("..")
                            next_part = l[i+1].split("..")
                            if (curr_part[1] > next_part[0]):
                                seq_valid = False
                                break
                        if not seq_valid:
                            continue
                    if (feature.strand == -1):
                        location.reverse()
                        seq_valid = True
                        for i in range (len(location)-1):
                            if (location[i][1] > location[i+1][0]):
                                seq_valid = False
                                break
                        if not seq_valid:
                            continue
                    if feature.strand == 1 or feature.strand == -1:
                        try:
                            with open(filename, 'a+') as external_file:
                                print("Dans",filename)
                                print(name_request, file=external_file)
                                print(feature.extract(record.seq), file=external_file)
                                for i, part in enumerate(feature.location.parts):
                                    print(name_request,feature_part_name,(i+1), file=external_file)
                                    print(part.extract(record.seq), file=external_file)
                            print(f"Extraction feature {feature.type} réussie")
                        except OSError:
                            #print(f"{filename} impossible à traiter")
                            continue
                if "intron" in region_to_parse:
                    feature_part_name = "Intron"
                    filename = f"{prefix_path}/intron_{name_organism}_{record.name}.txt"
                    reverse_location = []
                    for part in feature.location.parts:
                        reverse_location.append([int(part.start),int(part.end)])
                    if feature.strand == 1:
                        seq_valid = True
                        for i in range (len(reverse_location)-1):
                            if (reverse_location[i][1] > reverse_location[i+1][0]):
                                seq_valid = False
                                break
                        if not seq_valid:
                            continue
                    if (feature.strand == -1):
                        reverse_location.reverse()
                        seq_valid = True
                        for i in range (len(reverse_location)-1):
                            if (reverse_location[i][1] > reverse_location[i+1][0]):
                                seq_valid = False
                                break
                        if not seq_valid:
                            continue

                    if feature.strand == 1:
                        try:
                            with open(filename, 'a+') as external_file:
                                print("Dans",filename)
                                #print(name_request, file=external_file)
                                #print(feature.extract(record.seq), file=external_file)
                                name_request = "intron {} {}: join({})".format(record.annotations["organism"], record.name, range_index)
                                for i in range(len(reverse_location) - 1):
                                    feature_tmp = SeqFeature(FeatureLocation(reverse_location[i][1], reverse_location[i+1][0], strand=1), type="CDS")
                                    print(name_request,feature_part_name,(i+1), file=external_file)
                                    print(feature_tmp.extract(record.seq), file=external_file)
                            reverse_location = []
                            print(f"Extraction feature intron réussie")
                        except OSError:
                            #print(f"{filename} impossible à traiter")
                            continue
                    elif feature.strand == -1:
                        try:
                            with open(filename, 'a+') as external_file:
                                print("Dans",filename)
                                #print(name_request, file=external_file)
                                #print(feature.extract(record.seq), file=external_file)
                                name_request = "intron {} {}: complement(join({}))".format(record.annotations["organism"], record.name, range_index)
                                for i in range(len(reverse_location) - 1):
                                    feature_tmp = SeqFeature(FeatureLocation(reverse_location[len(reverse_location)-1-i-1][1], reverse_location[len(reverse_location)-1-i][0], strand=-1), type="CDS")
                                    print(name_request,feature_part_name,(i+1), file=external_file)
                                    print(feature_tmp.extract(record.seq), file=external_file)
                            reverse_location = []
                            print(f"Extraction feature intron réussie")
                        except OSError:
                            #print(f"{filename} impossible à traiter")
                            continue
            elif feature.type == "intron":
                feature_part_name = "Intron"
                if feature.strand == 1:
                    try:
                        with open(filename, 'a+') as external_file:
                            print("Dans",filename)
                            print(name_request, file=external_file)
                            print(feature.extract(record.seq), file=external_file)
                            for i in range(len(exon_order)  - 1):
                                print(name_request,feature_part_name,(i+1), file=external_file)
                                print(record[exon_order[i].end:exon_order[i+1].start], file=external_file)
                        print(f"Extraction feature intron réussie")
                    except OSError:
                        #print(f"{filename} impossible à traiter")
                        continue
                elif feature.strand == -1:
                    try:
                        with open(filename, 'a+') as external_file:
                            print("Dans",filename)
                            print(name_request, file=external_file)
                            print(feature.extract(record.seq), file=external_file)
                            
                            for i in range(len(exon_order) - 1):
                                print(name_request,feature_part_name,(i+1), file=external_file)
                                print(record[exon_order[i+1].end:exon_order[i].start].reverse_complement(), file=external_file)
                        print(f"Extraction feature intron réussie")
                    except OSError:
                        #print(f"{filename} impossible à traiter")
                        continue
            else:
                if (feature.type in region_to_parse):
                    try:
                        with open(filename, 'a+') as external_file:
                            print("Dans",filename)
                            print(name_request, file=external_file)
                            print(feature.extract(record.seq), file=external_file)
                        print(f"Extraction feature {feature.type} réussie")
                    except:
                        #print("Erreur:",feature.type)
                        print(f"{filename} impossible à traiter")
                        #continue
                        continue
    print(f"Extraction des régions terminée pour {name_organism}: {record.name}")
    write_nc_in_log(record.name, name_organism, kingdom)

def download_genome_files(files):
    dir = 'GENOME_REPORTS/IDS/'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

    ftp = ftplib.FTP("ftp.ncbi.nlm.nih.gov")
    ftp.login()
    ftp.cwd('genomes/GENOME_REPORTS')
    with open('GENOME_REPORTS/'+files[0],'wb') as f:
            ftp.retrbinary(f"RETR {files[0]}", f.write)
    ftp.cwd('IDS/')

    for i, file in enumerate(files):
        if (i != 0):
            with open('GENOME_REPORTS/IDS/'+file,'wb') as f:
                ftp.retrbinary(f"RETR {file}", f.write)
    ftp.quit()

def create_log_file():
    myfile = Path('NC_done.log')
    myfile.touch(exist_ok=True)

def write_nc_in_log(nc, organism, kingdom):
    filename = "NC_done.log"
    row = f"{nc}\t{organism}\t{kingdom}"
    with open(filename, "a+") as external_file:
        print(row, file=external_file)

def read_log():
    path = 'NC_done.log'
    filesize = os.path.getsize(path)
    if filesize != 0:
        df = pd.read_csv(path, sep="\t", header=None)
        df.columns = ["NC", "Organism", "Kingdom"]
        return df
    return pd.DataFrame(columns= ["NC", "Organism", "Kingdom"])

def search_last_nc_index(lst_nc, nc):
    for i, ncs in enumerate(lst_nc):
        if nc in ncs[1]:
            return i
    return -1

def remove_treated_nc():
    df_log = read_log()
    if (not df_log.empty):
        return df_log.iloc[:,0].to_list()
    return []
