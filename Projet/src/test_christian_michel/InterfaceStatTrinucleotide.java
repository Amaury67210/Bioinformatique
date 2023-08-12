/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package test_christian_michel;

/**
 *
 * @author ShiroiMao asus
 */

//Classe permetant d'effectuer les stats sur les Trinucléotide d'un gène
public class InterfaceStatTrinucleotide {
    private Trinuc_phase0 statphase0;
    private Trinuc_phase1 statphase1;
    private Trinuc_phase2 statphase2;
    
    private final String[] trinucName = {
            "aaa","aac","aag","aat",    "aca","acc","acg","act", "aga","agc","agg","agt", "ata","atc","atg","att",
            "caa","cac","cag","cat",    "cca","ccc","ccg","cct", "cga","cgc","cgg","cgt", "cta","ctc","ctg","ctt",
            "gaa","gac","gag","gat",    "gca","gcc","gcg","gct", "gga","ggc","ggg","ggt", "gta","gtc","gtg","gtt",
            "taa","tac","tag","tat",    "tca","tcc","tcg","tct", "tga","tgc","tgg","tgt", "tta","ttc","ttg","ttt"
        };          
    
    public InterfaceStatTrinucleotide(String gene){
        statphase0 = new Trinuc_phase0(gene);
        statphase1 = new Trinuc_phase1(gene);
        statphase2 = new Trinuc_phase2(gene);
        rangerLesTrinucleotides();
    }
    
    
    //Phase 1 :
    //Retourne le nombre d'apparition de chaque nucléotide
    public int[] getAllOccurencePhase0(){
        return statphase0.getOcc();
    }
    
    //rectoune le nombre d'apparition d'un nucleotide en particulier
    public int getOccurenceTrinucPhase0(String Trinucleotide){
        int i = 0;
        while(i<64 && !Trinucleotide.equals(statphase0.tri_nuc[i])){
            i++;
        }
        if(i==64){
            System.out.println("Erreur nucleotide non trouvé");
            return 0;
        }
        return statphase0.getOcc(i);
    }
    
    //Retourne la frequence d'appartition de chaque nucleotide
    public float[] getAllFreqPhase0(){
        return statphase0.freq;
    }
    
    //Retourne la frequence d'apparition d'un nucleotide en particulier
    public float getFreqTrinucPhase0(String Trinucleotide){
        int i = 0;
        while(i<64 && !Trinucleotide.equals(statphase0.tri_nuc[i])){
            i++;
        }
        if(i==64){
            System.out.println("Erreur nucleotide non trouvé");
            return 0;
        }
        return statphase0.freq[i];
    }
    
    //Phase 1
    //Retourne le nombre d'apparition de chaque nucléotide
    public int[] getAllOccurencePhase1(){
        return statphase1.getOcc();
    }
    
    //rectoune le nombre d'apparition d'un nucleotide en particulier
    public int getOccurenceTrinucPhase1(String Trinucleotide){
        int i = 0;
        while(i<64 && !Trinucleotide.equals(statphase1.tri_nuc[i])){
            i++;
        }
        if(i==64){
            System.out.println("Erreur nucleotide non trouvé");
            return 0;
        }
        return statphase1.getOcc(i);
    }
    
    //Retourne la frequence d'appartition de chaque nucleotide
    public float[] getAllFreqPhase1(){
        return statphase1.freq;
    }
    
    //Retourne la frequence d'apparition d'un nucleotide en particulier
    public float getFreqTrinucPhase1(String Trinucleotide){
        int i = 0;
        while(i<64 && !Trinucleotide.equals(statphase1.tri_nuc[i])){
            i++;
        }
        if(i==64){
            System.out.println("Erreur nucleotide non trouvé");
            return 0;
        }
        return statphase1.freq[i];
    }
    
    //Phase 2
    //Retourne le nombre d'apparition de chaque nucléotide
    public int[] getAllOccurencePhase2(){
        return statphase2.getOcc();
    }
    
    //rectoune le nombre d'apparition d'un nucleotide en particulier
    public int getOccurenceTrinucPhase2(String Trinucleotide){
        int i = 0;
        while(i<64 && !Trinucleotide.equals(statphase2.tri_nuc[i])){
            i++;
        }
        if(i==64){
            System.out.println("Erreur nucleotide non trouvé");
            return 0;
        }
        return statphase2.getOcc(i);
    }
    
    //Retourne la frequence d'appartition de chaque nucleotide
    public float[] getAllFreqPhase2(){
        return statphase2.freq;
    }
    
    //Retourne la frequence d'apparition d'un nucleotide en particulier
    public float getFreqTrinucPhase2(String Trinucleotide){
        int i = 0;
        while(i<64 && !Trinucleotide.equals(statphase2.tri_nuc[i])){
            i++;
        }
        if(i==64){
            System.out.println("Erreur nucleotide non trouvé");
            return 0;
        }
        return statphase2.freq[i];
    }
    
    
    public String[] getTrinucName(){
        return trinucName;
    }
    
    //Les nucléotides ne sont pas rangé dans le meme ordre à cause de l'implementation de Trinuc_phase0 etc...
    //On va les mettre dans un ordre absolut
    private void rangerLesTrinucleotides(){
        int tabtmpphase0[] = new int[64];
        int tabtmpphase1[] = new int[64];
        int tabtmpphase2[] = new int[64];
  
        for(int i = 0 ; i < 64 ; i++){
            String trinuc = trinucName[i];
            int j0 = 0;
            int j1 = 0;
            int j2 = 0;
            while((j0<64) && (!trinuc.equals(statphase0.getNuc(j0)))){
                j0++;
            }
            while((j1<64) && (!trinuc.equals(statphase1.getNuc(j1)))){
                j1++;
            }
            while((j2<64) && (!trinuc.equals(statphase2.getNuc(j2)))){
                j2++;
            }
            
            if(j0>=64){
                tabtmpphase0[i]=0;
            }
            else{
                tabtmpphase0[i]=statphase0.getOcc(j0);
            }
            
            if(j1>=64){
                tabtmpphase1[i]=0;
            }
            else{
                tabtmpphase1[i]=statphase1.getOcc(j1);
            }
            
            if(j2>=64){
                tabtmpphase2[i]=0;
            }
            else{
                tabtmpphase2[i]=statphase2.getOcc(j2);
            }
        }
        /*
         System.out.println("Avant set:");
        for(int w = 0;w < 64;w++){
            System.out.println(trinucName[w]+" "+statphase0.getOcc(w)+" "+statphase1.getOcc(w)+" "+statphase2.getOcc(w));
        }*/
        statphase0.setOcc(tabtmpphase0);
        statphase1.setOcc(tabtmpphase1);
        statphase2.setOcc(tabtmpphase2);
        
        /*
        System.out.println("Après set");
        System.out.println("set:");
        for(int w = 0;w < 64;w++){
            System.out.println(trinucName[w]+" "+statphase0.getOcc(w)+" "+statphase1.getOcc(w)+" "+statphase2.getOcc(w));
        }
        System.out.println("voulu:");
        for(int w = 0;w < 64;w++){ 
            System.out.println(trinucName[w]+" "+tabtmpphase0[w]+" "+tabtmpphase1[w]+" "+tabtmpphase2[w]);
        }*/
        
    }
}

