/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package test_christian_michel;

import java.io.IOException;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author ShiroiMao asus
 */
public class ParsingGenome {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("\n####test1####\n");
        Genome test;
        ArrayList<GenomeStats> liste = new ArrayList<GenomeStats>(); 
        try {
            test = new Genome("NC_005212");
            test.getInfo();
            GenomeStats teststats = new GenomeStats(test);
            teststats.afficherStats();
            liste.add(teststats);
        } catch (IOException ex) {
            Logger.getLogger(ParsingGenome.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        TimeUnit.SECONDS.sleep(2);
        System.out.println("\n####test2####\n");
        Genome test2;
        try {
            test2 = new Genome("NC_005212");
            test2.getInfo();
            GenomeStats teststats2 = new GenomeStats(test2);
            liste.add(teststats2);
        teststats2.afficherStats();
        } catch (IOException ex) {
            Logger.getLogger(ParsingGenome.class.getName()).log(Level.SEVERE, null, ex);
        }
        

        
        System.out.println("\n####Fusion####\n");
        GenomeStats merge = GenomeStats.mergeStats(liste);
        merge.afficherStats();
        
        
        
        // TODO code application logic here
        
        //Fichier lourd Nombre gene : 11159 --> Nombre gene valide : 19 (0%)
        /*
        Genome test = new Genome("NC_000001");
        test.getInfo();
        test.afficherGeneValide();
        */
        
        /*
        
        Genome test1 = new Genome("NC_000011");
        test1.getInfo();
        */
        
        
        
        //Fichier léger
        //Genome test2 = new Genome("NC_005212");
        //test2.getInfo();
        //test2.afficherGenome();
        //test2.afficherGene();
        //test2.afficherGeneValide();
        
        /*
        Genome test3 = new Genome("NC_016091");
        test3.getInfo();*/
    }
    
}
