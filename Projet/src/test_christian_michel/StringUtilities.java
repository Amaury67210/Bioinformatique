/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package test_christian_michel;

import java.util.ArrayList;

/**
 *
 * @author ShiroiMao asus
 */
public class StringUtilities {
    //Methode pour renverser une String
    public static String reverseString(String input){
        StringBuilder input1 = new StringBuilder(); 
        // append a string into StringBuilder input1 
        input1.append(input); 
        // reverse StringBuilder input1 
        input1 = input1.reverse(); 
        // print reversed String 
        return input1.toString();
    }
    
        //Verifie que 0 < borne_inf <= borne_supp <= taille genome
    public static boolean isBorneExist(int borne_inf,int borne_supp,int taille_genome){
        //System.out.println("Bornes : "+borne_inf+","+borne_supp+" taille adn :"+this.adn.length());
        //System.out.println("taille adn : "+this.taille_adn);
        boolean test = (0 < borne_inf) && (borne_inf <= borne_supp) && (borne_supp <= taille_genome);
        if(test==false){
            System.out.println("Gene invalide : borne invalide :"+borne_inf+".."+borne_supp);
        }
        return test;
    }
    
    //Renvoit le gene correspondant a un cds de la forme 656757..656778
    public static String simple(String cds, ArrayList<String> genome,int tailleGenome,int tailleStringGenome){
        //System.out.println(cds);
        String gene = "";
        String[] tab_id = cds.split("\\.\\.");
        //System.out.println(tab_id[0]+' '+tab_id[1]);
        if(tab_id.length != 2){
            //System.out.println("genome.simple : erreur nombre de borne aprÃ¨s split = "+tab_id.length);
            System.exit(1);
        }
        //ATTENTION !!!!!!!!!!!!! Conversion d'indice allant de 1 Ã  N vers 0 -> N-1
        int nb1 = Integer.parseInt(tab_id[0]);
        int nb2 = Integer.parseInt(tab_id[1]);
        if(isBorneExist(nb1,nb2,tailleGenome)){
            gene=GenomeUtilities.getGeneSeqFromAdn(nb1-1,nb2,genome,tailleStringGenome);
        }
        else{
            System.out.println("Bornes rincees"+nb1+" " + nb2+ " " + tailleGenome);
            
            return null;
        }
        return gene.toLowerCase();
    }
    
        //#############Creation et assemblage des different genes valides###########################
    //Prend en entree une chaine de la forme 266462..288648,26726763..6426648,..,26726763..6426648
    //renvoit null si les bornes sont fausses
    public static String join(String cds, ArrayList<String> genome,int tailleGenome,int tailleStringGenome){
        int lastborne=0;
        String gene="";
        String[] result = cds.split(",");
        for (int i=0; i<result.length; i++) {
            String[] tab_id = result[i].split("\\.\\.");
            if(tab_id.length != 2){
                System.out.println("genome.join : erreur nombre de borne après split = "+tab_id.length);
                System.exit(1);
            }
            //ATTENTION !!!!!!!!!!!!! Conversion d'indice allant de 1 Ã  N vers 0 -> N-1
            int nb1 = Integer.parseInt(tab_id[0]);
            int nb2 = Integer.parseInt(tab_id[1]);
            if(isBorneExist(nb1,nb2,tailleGenome) && (nb1 > lastborne)){
                lastborne = nb2;
                gene=gene+GenomeUtilities.getGeneSeqFromAdn(nb1-1,nb2,genome,tailleStringGenome);
            }
            else{
                //System.out.println("genome.join : erreur succession bornes "+tab_id.length);
                return null;
            }
        }
        return gene.toLowerCase();
    }
    
    //Renvoit le gene correspondant Ã  un cds de la forme complement(656757..656778)
    public static String  complement(String cds, ArrayList<String> genome,int tailleGenome,int tailleStringGenome){
        String gene = "";
        String[] tab_id = cds.split("\\.\\.");
        if(tab_id.length != 2){
            System.out.println("genome.complement : erreur nombre de borne aprÃ¨s split = "+tab_id.length);
            System.exit(1);
        }
        //ATTENTION !!!!!!!!!!!!! Conversion d'indice allant de 1 Ã  N vers 0 -> N-1
        int nb1 = Integer.parseInt(tab_id[0]);
        int nb2 = Integer.parseInt(tab_id[1]);
        if(isBorneExist(nb1,nb2,tailleGenome)){
            gene=GenomeUtilities.getGeneSeqFromAdn(nb1-1,nb2,genome,tailleStringGenome);
            gene=reverseString(gene);
        }
        else {
            System.out.println("genome.complement : bornes injuste"+tab_id.length);
            return null;
        }
        return gene.toLowerCase();
    }
    
    //Renvoit le gene correspondant Ã  un cds de la forme complement(join(656757..656778,........,76286..786767))
    public static String complementJoin(String cds, ArrayList<String> Genome, int tailleGenome,int tailleStringGenome){
        String result = join(cds,Genome,tailleGenome,tailleStringGenome);
        return reverseString(result);
    }
    
}
