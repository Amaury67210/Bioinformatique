import os
import sys
import ftplib
import logging
import shutil
from multiprocessing import Pool


INITIAL_PATH = "genomes/GENOME_REPORTS"


def download_ncbi_dist(arg):
    dst, dir, file = arg

    logging.info(f" Downloading'{os.path.join(dir, file)}'...")
    ftp = ftplib.FTP("ftp.ncbi.nlm.nih.gov")
    ftp.login()

    if len(dir):
        ftp.cwd(INITIAL_PATH + "/" + dir)
    else:
        ftp.cwd(INITIAL_PATH)

    with open(os.path.join(dst, dir, file), "wb") as f:
        ftp.retrbinary(f"RETR {file}", f.write)
    logging.info(f" Sucessfuly downloaded '{os.path.join(dir, file)}'.")


def download_ncbi(dst):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    if os.path.exists(dst):
        shutil.remove(dst)
    os.mkdir(dst)
    logging.info(f" Created directory '{dst}'")
    
    if os.path.exists(os.path.join(dst, "IDS")):
        shutil.remove(os.path.join(dst, "IDS"))
    os.mkdir(os.path.join(dst, "IDS"))
    logging.info(f" Created directory '{os.path.join(dst, 'IDS')}'")

    files = [("", "overview.txt"), ("IDS", "Bacteria.ids"), 
             ("IDS", "Eukaryota.ids"), ("IDS", "Archaea.ids"),
             ("IDS", "Viruses.ids")]

    # Adding destination
    files = [(dst,) + f for f in files]

    with Pool(5) as p:
        p.map(download_ncbi_dist, files)
