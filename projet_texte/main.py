# coding: utf-8

from asyncore import write
from cgitb import handler
from fileinput import filename
from re import sub
import genome
import interface
from time import process_time
import urllib.request
import requests
import time

import sys
import os
from Bio import Entrez
from Bio import SeqIO

# *Always* tell NCBI who you are
Entrez.email = "jeanlucphan84@gmail.com"
Entrez.api_key = "81005b6f8a9fdffc555ad15df06c18bcd409"

if __name__ == "__main__":
    app = interface.InterfaceManager()
