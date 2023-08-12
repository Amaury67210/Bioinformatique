# coding: utf-8

import tkinter as tk
import customtkinter as ctk
import shutil
import ftplib
import os
import sys
import subprocess
from numpy import sign
import genome
import time
import urllib.request
from tkinter import *
from tkinter import ttk
import tkinter.font as font
from PIL import Image, ImageTk
import http.client
from uuid import RFC_4122
from Bio import Entrez
from Bio import SeqIO
import threading
from fileinput import filename
from ftplib import FTP
from turtle import end_fill
import urllib 
import os.path
from os import path
import pandas as pd
from pathlib import Path
import urllib.request as request
import logging
from contextlib import closing
from Bio.SeqFeature import SeqFeature, FeatureLocation
# --- functions ---
is_active = True

stop_event = Event()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def Selection(EtatCheckButton, resultat):
    region = []
    for i in range (10):
        # print(EtatCheckButton[i].get())
        # print("----------------")
        if EtatCheckButton[i].get() == 1 :
            # print(resultat[i])
            region.append(resultat[i])
    # print(region)
    return region

def showEnd(event):
    event.widget.see(tk.END)
    event.widget.edit_modified(0)

# --- classes ---

class Redirect():

    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert('end', text)


# --- fonction principale ---

ctk.set_appearance_mode("dark")
#ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class InterfaceManager():

    def __init__(self) -> None:
        self.root = ctk.CTk()
        self.top_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.top_frame.pack(side=TOP, fill="both", pady=(0,10))

        #CTkFont(family="<family name>", size=<size in px>, <optional keyword arguments>)
        #self.f = font.Font(size=18)
        self.f = ctk.CTkFont(size=18)
        self.f.configure(underline=True)

        self.g = ctk.CTkFont(size=30)

        self.h = ctk.CTkFont(size=20)

        self.root.geometry("1200x800")
        self.root.title('Projet Bioinformatique SDSC Groupe 1')
        # root.configure(bg='lightblue')

        self.label_1 = ctk.CTkLabel(self.top_frame, text="GENOME", font=self.g)
        self.label_1.grid(row=0, column=0,sticky=W)
        self.label_1['font'] = self.g

        self.label_2 = ctk.CTkLabel(self.top_frame, text="Acquisition des régions fonctionnelles dans les génomes",font=self.h)
        self.label_2['font'] = self.h
        self.label_2.grid(row=1, column=0, sticky=W)

        self.resultat = ["CDS", "centromere", "intron", "mobile_element", "ncRNA", "rRNA", "telomere", "tRNA", "3'UTR", "5'UTR"] 
        
        self.top_frame_2 = ctk.CTkFrame(self.root, fg_color="transparent")
        self.top_frame_2.pack(side=TOP, pady=(0,10))
        self.label_3 = ctk.CTkLabel(self.top_frame_2, text="Les choix des régions fonctionnelles :")
        self.label_3['font'] = self.f
        self.label_3.grid(row=4, column=2, columnspan=5, sticky=NS)

        self.EtatCheckButton =[0 for i in range (10)]
        for i in range(10) :
            self.EtatCheckButton[i] = IntVar()

        self.c1 = ctk.CTkCheckBox(self.top_frame_2, text="CDS", variable=self.EtatCheckButton[0], onvalue=1, offvalue=0)
        self.c1.grid(row=5, column=2, padx=5, pady=5, sticky =NSEW)
        self.c1.select()
        self.c2 = ctk.CTkCheckBox(self.top_frame_2, text="centromere", variable=self.EtatCheckButton[1], onvalue=1, offvalue=0)
        self.c2.grid(row=5, column=3, padx=5, pady=5, sticky =NSEW)
        self.c2.select()
        self.c3 = ctk.CTkCheckBox(self.top_frame_2, text="intron", variable=self.EtatCheckButton[2], onvalue=1, offvalue=0)
        self.c3.grid(row=5, column=4, padx=5, pady=5, sticky =NSEW)
        self.c3.select()
        self.c4 = ctk.CTkCheckBox(self.top_frame_2, text="mobile_element", variable=self.EtatCheckButton[3], onvalue=1, offvalue=0)
        self.c4.grid(row=5, column=5, padx=5, pady=5, sticky =NSEW)
        self.c4.select()
        self.c5 = ctk.CTkCheckBox(self.top_frame_2, text="ncRNA", variable=self.EtatCheckButton[4], onvalue=1, offvalue=0)
        self.c5.grid(row=5, column=6, padx=5, pady=5, sticky =NSEW)
        self.c5.select()
        self.c6 = ctk.CTkCheckBox(self.top_frame_2, text="rRNA", variable=self.EtatCheckButton[5], onvalue=1, offvalue=0)
        self.c6.grid(row=6, column=2, padx=5, pady=5, sticky =NSEW)
        self.c6.select()
        self.c7 = ctk.CTkCheckBox(self.top_frame_2, text="telomere", variable=self.EtatCheckButton[6], onvalue=1, offvalue=0)
        self.c7.grid(row=6, column=3, padx=5, pady=5, sticky =NSEW)
        self.c7.select()
        self.c8 = ctk.CTkCheckBox(self.top_frame_2, text="tRNA", variable=self.EtatCheckButton[7], onvalue=1, offvalue=0)
        self.c8.grid(row=6, column=4, padx=5, pady=5, sticky =NSEW)
        self.c8.select()
        self.c9 = ctk.CTkCheckBox(self.top_frame_2, text="3'UTR", variable=self.EtatCheckButton[8], onvalue=1, offvalue=0)
        self.c9.grid(row=6, column=5, padx=5, pady=5, sticky =NSEW)
        self.c9.select()
        self.c10 = ctk.CTkCheckBox(self.top_frame_2, text="5'UTR", variable=self.EtatCheckButton[9], onvalue=1, offvalue=0)
        self.c10.grid(row=6, column=6, padx=5, pady=5, sticky =NSEW)
        self.c10.select()

        # Pour l'arbre si on a besoin d'icones pour les dossiers ou les fichiers :
        # folder_image = Image.open("folder.png")
        self.folder_image = Image.open(resource_path("folder.png"))
        self.folder_image = self.folder_image.resize((16, 16), Image.ANTIALIAS)
        self.folder_image = ImageTk.PhotoImage(self.folder_image)
        # file_image = Image.open("file.png")
        # file_image = file_image.resize((16, 16), Image.ANTIALIAS)
        # file_image = ImageTk.PhotoImage(file_image)

                ###Treeview Customisation (theme colors are selected)
        treestyle = ttk.Style()
        treestyle.theme_use('default')
        
        treestyle.configure("Treeview", background="#565B5E", 
                                foreground="#DCE4EE",
                                fieldbackground="#565B5E",
                                borderwidth=0,
                                font = 18,
                                rowheight = 28)
        
        treestyle.map('Treeview', background=[('selected', "#1B73C2")],
                    foreground=[('selected', "#DCE4EE")])


        self.root.bind("<<TreeviewSelect>>", lambda event: self.root.focus_set())

        self.frame_1 = ctk.CTkFrame(master=self.root, fg_color="transparent")
        self.frame_1.pack(side=TOP, fill="both")
        self.tree = ttk.Treeview(self.frame_1, show="tree")
        self.tree.pack(side=LEFT, fill="both", expand=1)
        self.scroll = Scrollbar(self.frame_1)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.text = tk.Text(self.frame_1, bg = "white", yscrollcommand=self.scroll.set, font=18)
        self.text.pack(side=LEFT, fill="both")
        self.text.bind('<<Modified>>', showEnd)
        self.scroll.config(command=self.text.yview)
        self.old_stdout = sys.stdout
        sys.stdout = Redirect(self.text)
        self.myvar = StringVar()

        self.progress_frame = ctk.CTkFrame(self.root, height=50, fg_color="transparent")

        self.Progressbar = ctk.CTkProgressBar(self.progress_frame, mode='determinate')
        self.Progressbar.grid(row=1, column=0, columnspan =2, padx=10)
        self.Progressbar.set(0)
        self.progress_label = ctk.CTkLabel(master=self.progress_frame, text='0/4')
        self.progress_label.grid(row=1, column=2, padx=10)

        self.Progressbar_2 = ctk.CTkProgressBar(self.progress_frame, mode='determinate')
        self.Progressbar_2.grid(row=2, column=0, columnspan =2, padx=10)
        self.Progressbar_2.set(0)
        self.progress_label_2 = ctk.CTkLabel(master=self.progress_frame, text='0/0')
        self.progress_label_2.grid(row=2, column=2, padx=10)

        self.Progressbar_3 = ctk.CTkProgressBar(self.progress_frame, mode='determinate')
        self.Progressbar_3.grid(row=3, column=0, columnspan =2, padx=10)
        self.Progressbar_3.set(0)
        self.progress_label_3 = ctk.CTkLabel(master=self.progress_frame, text='0/0')
        self.progress_label_3.grid(row=3, column=2, padx=10)

        self.progress_frame.pack(side=TOP, pady=(10,0))

        self.lst_files = [
            "overview.txt", 
            "Archaea.ids",
            "Bacteria.ids",
            "Eukaryota.ids",
            "Viruses.ids"
        ]
        self.button = ctk.CTkButton(self.progress_frame, text='Démarrer', command=lambda : self.thread_function_parser(self.EtatCheckButton, self.resultat, self.root, self.button.cget("text")))
        self.button.grid(row=0, column=0, columnspan=3, padx = 10)
        self.button.grid_forget()
        self.button2 = ctk.CTkButton(self.progress_frame, text='Téléchargement fichiers', command=self.download_file)
        self.button2.grid(row=0, column=0, columnspan=3, padx = 10)
        self.button2.invoke()
        self.button2.configure(state = DISABLED)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        # Arrêt de l'application
        self.root.quit()

    def download_file(self):
        self.button.state = "disabled"
        t = threading.Thread(target=self.extract_tree)
        t.start()
        #self.schedule_check(t)

    def schedule_check(self,t):
        self.root.after(1000, self.check_if_done, t)

    def check_if_done(self,t):
        if not t.is_alive():
            self.button.state = "normal"
        else:
            self.schedule_check(t)

    def recupInfosSelection(self):
        nomKingdom, nomGroup, nomSubgroup, organism = "", "", "", ""
        hierarchie = []
        
        selection = self.tree.selection()[0]
        parent = self.tree.parent(selection)
        hierarchie.append(self.tree.item(selection)['text'])
        parent_name = self.tree.item(parent)['text']

        while (parent_name != self.tree.item(self.tree.get_children(0))['text']):
            hierarchie.append(parent_name)
            parent = self.tree.parent(parent)
            parent_name = self.tree.item(parent)['text']
        
        nomKingdom = hierarchie[len(hierarchie)-1]
        if(len(hierarchie) > 1):
            nomGroup = hierarchie[len(hierarchie)-2]
            if(len(hierarchie) > 2):
                nomSubgroup = hierarchie[len(hierarchie)-3]
                if(len(hierarchie) > 3):
                    organism = hierarchie[len(hierarchie)-4]

        return nomKingdom, nomGroup, nomSubgroup, organism
        
    def extract_tree(self):
        print("Création d'un fichier log")
        genome.create_log_file()
        print("Début téléchargement des génomes")
        self.download_genome_files(self.lst_files)

        self.df = genome.get_dataframe_genome(self.lst_files[0])
        genome.create_tree(self.df)
        print("Affichage de l'arborescence en cours")
        self.create_tree()
        print("Génération de l'arborescence terminée")
        self.button2.grid_forget()
        self.button2.destroy()
        self.button.grid(row=0, column=1, padx = 10, pady = 10)

    def progress(self, Progressbar):
        if Progressbar.get() < 1:
            Progressbar.set(Progressbar.get() + 0.25)
        else:
            print("The progress completed!") 

    def progress_2(self, Progressbar, longueur):
        if Progressbar.get() < 1:
            num = 1 / longueur
            output=f"{num:8f}"
            output = float(output)
            Progressbar.set(Progressbar.get() + output)
        else:
            print("The progress completed!")

    def progress_3(self, Progressbar, longueur):
        if Progressbar.get() < 1:
            Progressbar.set(longueur)
        else:
            print("The progress completed!")

    def create_tree_recursive(self, parent, path):
        for i in os.listdir(path):
            abspath = os.path.join(path,i)
            isdir = os.path.isdir(abspath)
            if isdir: # dossiers
                elements = self.tree.insert(parent,END,text=i,open=False,values=(abspath,),image=self.folder_image)
                self.create_tree_recursive(elements,abspath)
            # else: # fichiers
            #     elements = tree.insert(parent,END,text=i,open=False,values=(abspath,)#,image=file_image
            #     )

    def create_tree(self):
        path = os.path.abspath("Results")
        parent = self.tree.insert("",END,text = path,open=True)
        self.create_tree_recursive(parent, path)

    def thread_function_parser(self, EtatCheckButton, resultat, root, text):
        global is_active
        if (text == "Stop"): 
            is_active = False
            self.button.configure(text = "Reprendre")
        elif (text == "Reprendre"):
            is_active = True
            self.button.configure(text = "Stop")
            self.button.state = NORMAL
            self.waithere()
        else:
            is_active = True
            self.text.delete('1.0', END)
            self.button.configure(text = "Stop")
            t = threading.Thread(target=self.function_parser, args=(EtatCheckButton, resultat, root))
            t.start()
    
    def waithere(self):
        var = IntVar()
        self.root.after(3000, var.set, 1)
        self.root.wait_variable(var)

    def download_genome_files(self, files):
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
                # interface.progress() 
                print(i, "----------------", i) 
                self.progress(self.Progressbar)
                self.progress_label.configure(text=f"{i}/4")
        ftp.quit()      

    def function_parser(self, EtatCheckButton, resultat, root):
        #print(v.get())
        self.Progressbar_2.set(0)
        self.Progressbar_3.set(0)
        self.progress_label_2.configure(text='0/0')
        self.progress_label_3.configure(text='0/0')
        global is_active
        regions = Selection(EtatCheckButton,resultat)
        #print(regions)
        # p = subprocess.run("ls", shell=True, stdout=subprocess.PIPE)
        # print(p.stdout.decode())


        ids_file = [
            "Archaea.ids",
            "Bacteria.ids",
            "Eukaryota.ids",
            "Mito_metazoa.ids",
            "Phages.ids",
            "Plasmids.ids",
            "Samples.ids",
            "Viroids.ids",
            "Viruses.ids",
            "dsDNA_Viruses.ids"
        ]

        Kingdom = ["Archaea", "Bacteria", "Eukaryota", "Viruses"]
        # -----------------------------------
        # Connaitre les NC par organisme
        kingdom_name, group_name, subgroup_name, organisme_name = "", "", "", ""

        if(self.tree.focus() != '' and self.tree.item(self.tree.selection()[0])['text'] != self.tree.item(self.tree.get_children(0))['text']):
            kingdom_name, group_name, subgroup_name, organisme_name = self.recupInfosSelection()

        # Ici tu peux check si les valeurs nomKingdom, nomGroup et nomSubgroup valent "" ou si une valeur a été sélectionnée

        #group_name = "Plants"
        #subgroup_name = "Land Plants"
        prefix = "Results/{}/{}/{}/{}".format(kingdom_name, group_name, subgroup_name, organisme_name)


        if(not is_active):
            print("Mise en pause de l'acquisition")
            while(self.button.cget("text") != "Stop"):
                pass
        
        
        if not group_name and not subgroup_name and not organisme_name:
            dataframe_organism = genome.regroup_organism_by_kingdom(self.df, kingdom_name)
            #dataframe_organism = genome.get_dataframe_kingdom(organism_by_kingdom, kingdom_name)
        elif group_name and not subgroup_name and not organisme_name:
            dataframe_organism = genome.get_organism_from_group(self.df,kingdom_name,group_name)
        elif subgroup_name and not organisme_name:
            # retourne un dataframe contenant le nom des organismes d'un sous groupe donnée
            dataframe_organism = genome.get_organism_from_subgroup(self.df,kingdom_name,group_name,subgroup_name)
        elif organisme_name:
            dataframe_organism = genome.get_organism_from_field(self.df,kingdom_name,group_name,subgroup_name, organisme_name)
            #print(dataframe_organism)
        if(not is_active):
            print("Mise en pause de l'acquisition")
            while(self.button.cget("text") != "Stop"):
                pass
        dataframe_organism = dataframe_organism.sort_values(["Kingdom", "Group", "SubGroup"])
        dataframe_organism.reset_index(drop=True, inplace=True)
        #print("Téléchargement terminé")

        df_log = genome.read_log()

        print(f"Début recherche des NC pour {kingdom_name} {group_name} {subgroup_name}".center(80,"-"),"\n")
        organism_name = dataframe_organism["#Organism/Name"].tolist()
        organism_group = dataframe_organism["Group"].tolist()
        organism_subgroup = dataframe_organism["SubGroup"].tolist()

        longueur = len(organism_name)

        # on recherche les nc par organisme
        nc_by_organism = []
        
        df_ncs_tmp = pd.DataFrame(columns= ["NC", "Organism", "Kingdom"])

        for i, organism in enumerate(organism_name):
            if(not is_active):
                print("Mise en pause de l'acquisition")
                while(self.button.cget("text") != "Stop"):
                    pass
            print(f"Recherche des NC pour l'organisme {organism}")

            if (not df_log.empty):
                df_ncs_tmp = df_log[[organism in o for o in df_log['Organism']]]["NC"].to_frame()
            ncs = genome.search_nc_by_organism(kingdom_name, organism, df_ncs_tmp)
            print(f"{len(ncs)} nouveaux NC trouvés pour l'organisme {organism}\n")
            if(ncs):
                nc_by_organism.append([organism, ncs, organism_group[i], organism_subgroup[i]])
            self.progress_2(self.Progressbar_2, longueur)
            self.progress_label_2.configure(text=f"{i+1}/{len(organism_name)}")
        # Pour un NC donné, extraction et écriture des séquences dans les fichiers par régions
        # Récupération du gene via id

        print(f"Fin de la recherche des NC pour {kingdom_name} {group_name} {subgroup_name}".center(80,"-"))
        print("\n","Début d'extraction".center(80, "-"))
        
        longueur_2 = sum([len(x[1]) for x in nc_by_organism])
        compteur_nc = 0
        for j, organism in enumerate(nc_by_organism):
            prefix = "Results/{}/{}/{}/{}".format(kingdom_name, organism[2], organism[3], organism[0])
            for nc in organism[1]:
                self.progress_2(self.Progressbar_3, longueur_2)
                compteur_nc = compteur_nc + 1
                self.progress_label_3.configure(text=f"{compteur_nc}/{longueur_2}")
                if (nc in df_log['NC'].unique()):
                    continue
                try: 
                    print(f"\nLecture de {nc}")
                    handle = Entrez.efetch(db="nucleotide",id=nc, rettype="gbwithparts", retmode="text")
                    record = SeqIO.read(handle, "genbank")
                    handle.close()
                except KeyboardInterrupt:
                    print("Arret du programme")
                    sys.exit()
                except (ValueError, urllib.error.HTTPError):
                    print(f"Lecture du nc {record.name} impossible")
                    continue
                except http.client.IncompleteRead:
                    print(f"Lecture du nc {record.name} impossible")
                    continue
                else:
                    if(not is_active):
                        print("Mise en pause de l'acquisition")
                        while(self.button.cget("text") != "Stop"):
                            pass
                    print(f"Ecriture des régions pour {record.name}")
                    genome.write_available_feature(record, prefix, regions, kingdom_name, organism[0])
                    df_log.loc[len(df_log)] = [nc, organism[0], kingdom_name]
        is_active = False
        self.button.configure(text = "Démarrer")
        self.progress_3(self.Progressbar_3, 1)
        self.progress_label_3.configure(text=f"{longueur_2}/{longueur_2}")
        print("\n","Fin d'extraction".center(80, "-"),"\n")

# if __name__ == "__main__":
#    interface_main()
