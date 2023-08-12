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

//Classe permetant d'effectuer les stats sur les dinucléotide d'un gène
public class InterfaceStatDinucleotide {
    private Dinuc_phase0 statphase0;
    private Dinuc_phase1 statphase1;
    public String[] dinucName = {
        "aa","ac","ag","at",
        "ca","cc","cg","ct",
        "ga","gc","gg","gt",
        "ta","tc","tg","tt"
    };
    
    public InterfaceStatDinucleotide(String gene){
        statphase0 = new Dinuc_phase0(gene);
        statphase1 = new Dinuc_phase1(gene);
        rangerLesDinucleotides();
    }
    
    
    //Phase 1 :
    
    //Retourne le nombre d'apparition de chaque nucléotide
    public int[] getAllOccurencePhase0(){
        return statphase0.getOcc();
    }
    
    //rectoune le nombre d'apparition d'un nucleotide en particulier
    public int getOccurenceDinucPhase0(String dinucleotide){
        int i = 0;
        while(i<16 && !dinucleotide.equals(statphase0.di_nuc[i])){
            i++;
        }
        if(i==16){
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
    public float getFreqDinucPhase0(String dinucleotide){
        int i = 0;
        while(i<16 && !dinucleotide.equals(statphase0.di_nuc[i])){
            i++;
        }
        if(i==16){
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
    public int getOccurenceDinucPhase1(String dinucleotide){
        int i = 0;
        while(i<16 && !dinucleotide.equals(statphase1.di_nuc[i])){
            i++;
        }
        if(i==16){
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
    public float getFreqDinucPhase1(String dinucleotide){
        int i = 0;
        while(i<16 && !dinucleotide.equals(statphase1.di_nuc[i])){
            i++;
        }
        if(i==16){
            System.out.println("Erreur nucleotide non trouvé");
            return 0;
        }
        return statphase1.freq[i];
    }
    
    public String[] getDinucName(){
        return dinucName;
    }
    
    //Les nucléotides ne sont pas rangé dans le meme ordre à cause de l'implementation de Trinuc_phase0 etc...
    //On va les mettre dans un ordre absolut
    private void rangerLesDinucleotides(){
        int tabtmpphase0[] = new int[16];
        int tabtmpphase1[] = new int[16];
        
        for(int i = 0 ; i < 16 ; i++){
            String dinuc = dinucName[i];
            int j0 = 0;
            int j1 = 0;
            while((j0<16) && (!dinuc.equals(statphase0.getNuc(j0)))){
                j0++;
            }
            while((j1<16) && (!dinuc.equals(statphase1.getNuc(j1)))){
                j1++;
            }
            
            if(j0>=16){
                tabtmpphase0[i]=0;
            }
            else{
                tabtmpphase0[i]=statphase0.getOcc(j0);
            }
            
            if(j1>=16){
                tabtmpphase1[i]=0;
            }
            else{
                tabtmpphase1[i]=statphase1.getOcc(j1);
            }
        }
        statphase0.setOcc(tabtmpphase0);
        statphase1.setOcc(tabtmpphase1);
    }
    
}
