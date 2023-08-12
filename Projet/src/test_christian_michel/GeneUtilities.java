/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package test_christian_michel;

/**
 *
 * @author ShiroiMao asus
 * Classe relative à tout ce qui touche au traitement des gènes
 */
public class GeneUtilities {
    
    public static boolean verifCodonStartStop(String gene){
        String[] init_seq = {"atg","ctg","ttg","gtg","ata","atc","att","tta"};
        String[] stop_seq = {"taa","tag,","tga","tta"};
        String gene_start = gene.substring(0,3);
        String gene_stop =gene.substring(gene.length()-3, gene.length());
        //System.out.println("Codon start && codon stop : "+gene_start+" "+gene_stop);
        
        boolean test1 = (
                gene_start.equals(init_seq[0]) 
                || gene_start.equals(init_seq[1])
                || gene_start.equals(init_seq[2])
                || gene_start.equals(init_seq[3])
                || gene_start.equals(init_seq[4])
                || gene_start.equals(init_seq[5])
                || gene_start.equals(init_seq[6])
                || gene_start.equals(init_seq[7])
                );
        boolean test2 = (
                gene_stop.equals(stop_seq[0])
                || gene_stop.equals(stop_seq[1])
                || gene_stop.equals(stop_seq[2])
                || gene_stop.equals(stop_seq[3])
                );
        
        if(test1==false){
            //System.out.println("Gene invalide : codon START missing : "+gene_start);
        }
        if(test2==false){
            //System.out.println("Gene invalide : codon STOP missing : "+gene_stop);
        }
        return (test1 && test2);
    }
    
    public static boolean isGeneMultipleDeTrois(String gene){
        boolean test = (gene.length()%3)==0;
        if(test==false){
            //System.out.println("Gene invalide : taille :"+gene.length()+"%3 = "+gene.length()%3);
        }
        return test;
    }
    
    public static boolean noIsVide(String gene){
        boolean test = (gene!=null);
        if(test==false){
            //System.out.println("Gene invalide : Gene null");
        }
        return test;
    }
    //Manque la vérification des lettres
    public static boolean isValide(String gene){
        if((noIsVide(gene) && isGeneMultipleDeTrois(gene) && verifCodonStartStop(gene))){
            //System.out.println("---------------Gene VALIDE------------------------");
        }
        
        return (noIsVide(gene) && isGeneMultipleDeTrois(gene) && verifCodonStartStop(gene));
    }
}
