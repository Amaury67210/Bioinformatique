/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package test_christian_michel;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.ArrayList;

/**
 *
 * @author ShiroiMao asus
 */
public class GenomeStats implements Serializable{
    /**
     * 
     */
    private static final long serialVersionUID = -9108962178816134986L;
    private Genome genome;
    private String type = "unknow";
    private String[] hierarchy;
    private String id_nc = "NC_000000";
    private int nbElements = 1; // 1 si objet créé à partir d'un génome, sinon nb de genomeStats fuisionnés
    //Contient le nom des differents trinucléotides et dinucléotides
    private final String[] di_nuc = {
        "aa","ac","ag","at",
        "ca","cc","cg","ct",
        "ga","gc","gg","gt",
        "ta","tc","tg","tt"
    };
    private final String[] tri_nuc = {
        "aaa","aac","aag","aat",    "aca","acc","acg","act", "aga","agc","agg","agt", "ata","atc","atg","att",
        "caa","cac","cag","cat",    "cca","ccc","ccg","cct", "cga","cgc","cgg","cgt", "cta","ctc","ctg","ctt",
        "gaa","gac","gag","gat",    "gca","gcc","gcg","gct", "gga","ggc","ggg","ggt", "gta","gtc","gtg","gtt",
        "taa","tac","tag","tat",    "tca","tcc","tcg","tct", "tga","tgc","tgg","tgt", "tta","ttc","ttg","ttt"
    };
    
    private int nombre_total_trinucleotide = 0;
    private int nombre_total_dinucleotide = 0;
    private int nombre_total_gene_valide = 0;
    private int nombre_total_gene = 0;
    
    //Contient le nombre d'occurence de chaque nucléotide pour l'ensemble des genes valides du genome
    private int[] count_tri_nuc_phase0;
    private int[] count_tri_nuc_phase1;
    private int[] count_tri_nuc_phase2;
    
    private int[] count_di_nuc_phase0;
    private int[] count_di_nuc_phase1;
    
    //Contient la frequence d'appartition de chaque nucleotide pour l'ensemble des genes valides du genome
    private double[] freq_tri_nuc_phase0;
    private double[] freq_tri_nuc_phase1;
    private double[] freq_tri_nuc_phase2;
    
    private double[] freq_di_nuc_phase0;
    private double[] freq_di_nuc_phase1;
    
    //Contient les phase preferenciel
    
    private int[] pref_tri_nuc_phase0;
    private int[] pref_tri_nuc_phase1;
    private int[] pref_tri_nuc_phase2;
    
    private int[] pref_di_nuc_phase0;
    private int[] pref_di_nuc_phase1;

    // méthode readObject, utilisée pour reconstituer un objet sérializé
    private  void readObject(ObjectInputStream ois) throws IOException, ClassNotFoundException {

        this.type = (String) ois.readObject();
        this.hierarchy = (String[]) ois.readObject();
        this.nbElements = ois.readInt();
        this.nombre_total_trinucleotide = ois.readInt();
        this.nombre_total_dinucleotide = ois.readInt();
        this.nombre_total_gene_valide = ois.readInt();
        this.nombre_total_gene = ois.readInt();

        this.count_tri_nuc_phase0 = (int[]) ois.readObject();
        this.count_tri_nuc_phase1 = (int[]) ois.readObject();
        this.count_tri_nuc_phase2  = (int[]) ois.readObject();

        this.count_di_nuc_phase0 = (int[]) ois.readObject();
        this.count_di_nuc_phase1 = (int[]) ois.readObject();

        this.freq_tri_nuc_phase0 = (double[]) ois.readObject();
        this.freq_tri_nuc_phase1 = (double[]) ois.readObject();
        this.freq_tri_nuc_phase2 = (double[]) ois.readObject();

        this.freq_di_nuc_phase0 = (double[]) ois.readObject();
        this.freq_di_nuc_phase1  = (double[]) ois.readObject();

        this.pref_tri_nuc_phase0 = (int[]) ois.readObject();
        this.pref_tri_nuc_phase1  = (int[]) ois.readObject();
        this.pref_tri_nuc_phase2 = (int[]) ois.readObject();

        this.pref_di_nuc_phase0 = (int[]) ois.readObject();
        this.pref_di_nuc_phase1 = (int[]) ois.readObject();
   }

    // méthode writeObject, utilisée lors de la sérialization
    private  void writeObject(ObjectOutputStream oos) throws IOException {
//      oos.writeObject(genome);
        oos.writeObject(type);
        oos.writeObject(hierarchy);
        oos.writeInt(nbElements);
        oos.writeInt(nombre_total_trinucleotide);
        oos.writeInt(nombre_total_dinucleotide);
        oos.writeInt(nombre_total_gene_valide);
        oos.writeInt(nombre_total_gene);
        
        oos.writeObject(count_tri_nuc_phase0);
        oos.writeObject(count_tri_nuc_phase1);
        oos.writeObject(count_tri_nuc_phase2);

        oos.writeObject(count_di_nuc_phase0);
        oos.writeObject(count_di_nuc_phase1);
        
        oos.writeObject(freq_tri_nuc_phase0);
        oos.writeObject(freq_tri_nuc_phase1);
        oos.writeObject(freq_tri_nuc_phase2);
        
        oos.writeObject(freq_di_nuc_phase0);
        oos.writeObject(freq_di_nuc_phase1);

        oos.writeObject(pref_tri_nuc_phase0);
        oos.writeObject(pref_tri_nuc_phase1);
        oos.writeObject(pref_tri_nuc_phase2);

        oos.writeObject(pref_di_nuc_phase0);
        oos.writeObject(pref_di_nuc_phase1);

   }
    
    public GenomeStats(){
        this.genome = new Genome();
        this.type = genome.getGenomeType();
        this.hierarchy = genome.getHierarchy();
        String gene = "";
        ArrayList<String> geneValide = new ArrayList<>();
        nombre_total_trinucleotide = 0;
        nombre_total_dinucleotide = 0;
        
        count_tri_nuc_phase0 = new int[64];
        count_tri_nuc_phase1 = new int[64];
        count_tri_nuc_phase2 = new int[64];
        for(int i = 0;i<64;i++){
            count_tri_nuc_phase0[i]=0;
            count_tri_nuc_phase1[i]=0;
            count_tri_nuc_phase2[i]=0;
        }   
        count_di_nuc_phase0 = new int[16];
        count_di_nuc_phase1 = new int[16];
        for(int i = 0;i<16;i++){
            count_di_nuc_phase0[i]=0;
            count_di_nuc_phase1[i]=0;
        }
        
        //Gestion des frequences
        freq_tri_nuc_phase0= new double[64];
        freq_tri_nuc_phase1= new double[64];
        freq_tri_nuc_phase2= new double[64];
        
        freq_di_nuc_phase0= new double[16];
        freq_di_nuc_phase1= new double[16];
        
        
        for(int j = 0; j < 64;j++){
            freq_tri_nuc_phase0[j] = 0;
            freq_tri_nuc_phase1[j] = 0;
            freq_tri_nuc_phase2[j] = 0;
        }
        for(int j = 0; j < 16;j++){
            freq_di_nuc_phase0[j] = 0;
            freq_di_nuc_phase1[j] = 0;
        }
        //Gestion des phase pref
        pref_tri_nuc_phase0 = new int[64];
        pref_tri_nuc_phase1 = new int[64];
        pref_tri_nuc_phase2 = new int[64];
        for(int i = 0;i<64;i++){
            pref_tri_nuc_phase0[i]=0;
            pref_tri_nuc_phase1[i]=0;
            pref_tri_nuc_phase2[i]=0;
        }   
        pref_di_nuc_phase0 = new int[16];
        pref_di_nuc_phase1 = new int[16];
        for(int i = 0;i<16;i++){
            pref_di_nuc_phase0[i]=0;
            pref_di_nuc_phase1[i]=0;
        }
        
    }

    
    public GenomeStats(Genome g){
        this.genome = g;
        this.type = genome.getGenomeType();
        this.id_nc = g.getNC();
        String gene = "";
        ArrayList<String> geneValide = genome.getGeneValide();
        nombre_total_trinucleotide = 0;
        nombre_total_dinucleotide = 0;
        nombre_total_gene = genome.getNombreGene();
        nombre_total_gene_valide = genome.getNombreGeneValide();
        
        
        //Gestion des occurence et comptage du nombre total de nucléotide et definition des phases prefs
        //Initialisation des tableaux
        //Count
        count_tri_nuc_phase0 = new int[64];
        count_tri_nuc_phase1 = new int[64];
        count_tri_nuc_phase2 = new int[64];
        for(int i = 0;i<64;i++){
            count_tri_nuc_phase0[i]=0;
            count_tri_nuc_phase1[i]=0;
            count_tri_nuc_phase2[i]=0;
        }   
        count_di_nuc_phase0 = new int[16];
        count_di_nuc_phase1 = new int[16];
        for(int i = 0;i<16;i++){
            count_di_nuc_phase0[i]=0;
            count_di_nuc_phase1[i]=0;
        }
        //Phase pref
        pref_tri_nuc_phase0 = new int[64];
        pref_tri_nuc_phase1 = new int[64];
        pref_tri_nuc_phase2 = new int[64];
        for(int i = 0;i<64;i++){
            pref_tri_nuc_phase0[i]=0;
            pref_tri_nuc_phase1[i]=0;
            pref_tri_nuc_phase2[i]=0;
        }   
        pref_di_nuc_phase0 = new int[16];
        pref_di_nuc_phase1 = new int[16];
        for(int i = 0;i<16;i++){
            pref_di_nuc_phase0[i]=0;
            pref_di_nuc_phase1[i]=0;
        }

        //Pour chaque gène
        for(int i = 0; i < genome.getNombreGeneValide(); i++){
            gene=geneValide.get(i);
            InterfaceStatTrinucleotide statTri = new InterfaceStatTrinucleotide(gene);
            InterfaceStatDinucleotide statDi = new InterfaceStatDinucleotide(gene);
            
            //Pour un gène contient le count de chaque nuc
            int tri_occ_P0[] = statTri.getAllOccurencePhase0();
            int tri_occ_P1[] = statTri.getAllOccurencePhase1();
            int tri_occ_P2[] = statTri.getAllOccurencePhase2();
            
            /*
            System.out.println(gene);
            for(int w = 0;w < 64;w++){
                System.out.println(tri_nuc[w]+" "+tri_occ_P0[w]+" "+tri_occ_P1[w]+" "+tri_occ_P2[w]);
            }*/

            int di_occ_P0[] = statDi.getAllOccurencePhase0();
            int di_occ_P1[] = statDi.getAllOccurencePhase1();
            
            //Gestion des occurences et phase pref des trinucleotide
            nombre_total_trinucleotide += gene.length()/3;
            for(int j = 0; j < 64;j++){ 
                count_tri_nuc_phase0[j] = count_tri_nuc_phase0[j]+tri_occ_P0[j];
                count_tri_nuc_phase1[j] = count_tri_nuc_phase1[j]+tri_occ_P1[j];
                count_tri_nuc_phase2[j] = count_tri_nuc_phase2[j]+tri_occ_P2[j];

                //Phase pref
                // >>
                if((tri_occ_P0[j] > tri_occ_P1[j]) && (tri_occ_P0[j] > tri_occ_P2[j]))
                    pref_tri_nuc_phase0[j]+=1;
                else if((tri_occ_P1[j] > tri_occ_P0[j]) && (tri_occ_P1[j] > tri_occ_P2[j]))
                    pref_tri_nuc_phase1[j]+=1;
                else if((tri_occ_P2[j] > tri_occ_P0[j]) && (tri_occ_P2[j] > tri_occ_P1[j]))
                    pref_tri_nuc_phase2[j]+=1;
                // == 
                else if((tri_occ_P2[j] == tri_occ_P0[j]) && (tri_occ_P2[j] == tri_occ_P1[j])){
                    if(tri_occ_P2[j] != 0){
                        pref_tri_nuc_phase0[j]+=1;
                        pref_tri_nuc_phase1[j]+=1;
                        pref_tri_nuc_phase2[j]+=1;
                    }
                }
                //>=
                else if((tri_occ_P0[j] == tri_occ_P1[j]) && (tri_occ_P0[j] > tri_occ_P2[j])){
                    pref_tri_nuc_phase1[j]+=1;
                    pref_tri_nuc_phase1[j]+=1;
                }
                else if((tri_occ_P1[j] == tri_occ_P2[j]) && (tri_occ_P1[j] > tri_occ_P0[j])){
                    pref_tri_nuc_phase1[j]+=1;
                    pref_tri_nuc_phase2[j]+=1;
                }
                else if((tri_occ_P0[j] == tri_occ_P2[j]) && (tri_occ_P0[j] > tri_occ_P1[j])){
                    pref_tri_nuc_phase0[j]+=1;
                    pref_tri_nuc_phase2[j]+=1;
                }
                else{
                    System.out.println("Erreur condition non prevue phase pref trinuc");
                    System.out.println(tri_occ_P0[j]);
                    System.out.println(tri_occ_P1[j]);
                    System.out.println(tri_occ_P2[j]);
                    System.exit(1);
                }
            }

            //Gestion des occurences et phase pref des dinucleotide
            nombre_total_dinucleotide += gene.length()/2;
            for(int j = 0; j < 16;j++){
                count_di_nuc_phase0[j] = count_di_nuc_phase0[j]+di_occ_P0[j];
                count_di_nuc_phase1[j] = count_di_nuc_phase1[j]+di_occ_P1[j];

                if(di_occ_P0[j] > di_occ_P1[j])
                    pref_di_nuc_phase0[j]+=1;
                else if (di_occ_P0[j] < di_occ_P1[j])
                    pref_di_nuc_phase1[j]+=1;
                else if (di_occ_P0[j] == di_occ_P1[j]){
                	if (di_occ_P0[j] != 0) {
                		pref_di_nuc_phase0[j]+=1;
                		pref_di_nuc_phase1[j]+=1;
                	}
                }
                else{
                    System.out.println("Erreur condition non prevue phase pref dinuc");
                    System.out.println(di_occ_P0[j]);
                    System.out.println(di_occ_P1[j]);
                    System.exit(1);
                }
            }
        }

        
        //Gestion des frequences
        //Initialisation
        freq_tri_nuc_phase0= new double[64];
        freq_tri_nuc_phase1= new double[64];
        freq_tri_nuc_phase2= new double[64];
        
        freq_di_nuc_phase0= new double[16];
        freq_di_nuc_phase1= new double[16];
        
        for(int j = 0; j < 64;j++){
            if(nombre_total_trinucleotide > 0){
                freq_tri_nuc_phase0[j] = (double)count_tri_nuc_phase0[j]/nombre_total_trinucleotide;
                freq_tri_nuc_phase1[j] = (double)count_tri_nuc_phase1[j]/nombre_total_trinucleotide;
                freq_tri_nuc_phase2[j] = (double)count_tri_nuc_phase2[j]/nombre_total_trinucleotide;
            }
            else{
                freq_tri_nuc_phase0[j] = 0;
                freq_tri_nuc_phase1[j] = 0;
                freq_tri_nuc_phase2[j] = 0;
            }
        }
        for(int j = 0; j < 16;j++){
            if(nombre_total_dinucleotide > 0){
                freq_di_nuc_phase0[j] = (double)count_di_nuc_phase0[j]/nombre_total_dinucleotide;
                freq_di_nuc_phase1[j] = (double)count_di_nuc_phase1[j]/nombre_total_dinucleotide;
            }
            else{
                freq_di_nuc_phase0[j] = 0;
                freq_di_nuc_phase1[j] = 0;
            }
        }
        
    }
    public void afficherStats(){
        double freq_total_trinuc = 0;
        double freq_total_dinuc = 0;
        System.out.println("Statistiques dinucleotides :");
        for(int i = 0; i < 16;i++){
            freq_total_dinuc += freq_di_nuc_phase0[i];
            System.out.println(di_nuc[i]+" __Count__ : "+count_di_nuc_phase0[i]+" "+count_di_nuc_phase1[i]+" __Freq__ : "+freq_di_nuc_phase0[i]+" "+freq_di_nuc_phase1[i]+" __Pref__ "+pref_di_nuc_phase0[i]+" "+pref_di_nuc_phase1[i]);
        }
        System.out.println("Somme total freq dinuc :"+freq_total_dinuc);
        System.out.println("----------------------------------------------------");
        System.out.println("Statistiques trinucleotides :");


        for(int i = 0; i < 64;i++){
            freq_total_trinuc += freq_tri_nuc_phase0[i];
            System.out.println(tri_nuc[i]+" __Count__ "+count_tri_nuc_phase0[i]+" "+count_tri_nuc_phase1[i]+" "+count_tri_nuc_phase2[i]+" __Freq__ "+freq_tri_nuc_phase0[i]+" "+freq_tri_nuc_phase1[i]+" "+freq_tri_nuc_phase2[i]+" __Pref__ "+pref_tri_nuc_phase0[i]+" "+pref_tri_nuc_phase1[i]+" "+pref_tri_nuc_phase2[i]);
        
        }
        System.out.println("Somme total freq trinuc :"+freq_total_trinuc);

        
    }
    
    public int getNbElements() {
        return this.nbElements;
    }
    public String getIdNC() {
        return this.id_nc;
    }
    //Stat de base sur le NC
    public int getNombreGene(){
        return nombre_total_gene;
    }
    public int getNombreGeneValide(){
        return nombre_total_gene_valide;
    }
    public String getType(){
        return type;
    }
    public String[] getHierarchy(){
        return hierarchy;
    }
    
    //Stat de base sur les nucleotides
    public int getNombreDinuc(){
        return this.nombre_total_dinucleotide;
    }
    
    public int getNombreTrinuc(){
        return this.nombre_total_trinucleotide;
    }
    
    public String[] getDinucName(){
        return di_nuc;
    }
    public String[] getTrinucName(){
        return tri_nuc;
    }
    
    //Occurence
    public int[] getStatsDinucPhase0Occ(){
        return count_di_nuc_phase0;
    }
    public int[] getStatsDinucPhase1Occ(){
        return count_di_nuc_phase1;
    }
    public int[] getStatsTrinucPhase0Occ(){
        return count_tri_nuc_phase0;
    }
    public int[] getStatsTrinucPhase1Occ(){
        return count_tri_nuc_phase1;
    }
        public int[] getStatsTrinucPhase2Occ(){
        return count_tri_nuc_phase2;
    }
        
    //Frequence
    public double[] getStatsDinucPhase0Freq(){
        return freq_di_nuc_phase0;
    }
    public double[] getStatsDinucPhase1Freq(){
        return freq_di_nuc_phase1;
    }
    public double[] getStatsTrinucPhase0Freq(){
        return freq_tri_nuc_phase0;
    }
    public double[] getStatsTrinucPhase1Freq(){
        return freq_tri_nuc_phase1;
    }
    public double[] getStatsTrinucPhase2Freq(){
        return freq_tri_nuc_phase2;
    }
    
    //PhasePref
    public int[] getStatsDinucPhase0Pref(){
        return pref_di_nuc_phase0;
    }
    public int[] getStatsDinucPhase1Pref(){
        return pref_di_nuc_phase1;
    }
    public int[] getStatsTrinucPhase0Pref(){
        return pref_tri_nuc_phase0;
    }
    public int[] getStatsTrinucPhase1Pref(){
        return pref_tri_nuc_phase1;
    }
    public int[] getStatsTrinucPhase2Pref(){
        return pref_tri_nuc_phase2;
    }
    /*    
    //PhasePref
    public int[] getStatsDinucPhase0Pref(){
        return count_di_nuc_phase0;
    }
    public int[] getStatsDinucPhase1Pref(){
        return count_di_nuc_phase1;
    }
    public int[] getStatsTrinucPhase0Pref(){
        return count_tri_nuc_phase0;
    }
    public int[] getStatsTrinucPhase1Pref(){
        return count_tri_nuc_phase1;
    }
    public int[] getStatsTrinucPhase2Pref(){
        return count_tri_nuc_phase2;
    }
*/    
    
    public static GenomeStats mergeStats(ArrayList<GenomeStats> l){
        if (l.isEmpty())
            return null;
        GenomeStats fusion = new GenomeStats();
        //Recupération des stats générales
        fusion.type = l.get(0).getType();
        fusion.hierarchy = l.get(0).getHierarchy();
        fusion.nbElements = l.size();
        for(int i = 0; i < l.size(); i++){
            fusion.nombre_total_dinucleotide += l.get(i).nombre_total_dinucleotide;
            fusion.nombre_total_trinucleotide += l.get(i).nombre_total_trinucleotide;
            fusion.nombre_total_gene += l.get(i).getNombreGene();
            fusion.nombre_total_gene_valide += l.get(i).getNombreGeneValide();
        }
        
        //Trinuc
        for(int i = 0 ; i  < 64; i++){
            int count_phase0 = 0;
            int count_phase1 = 0;
            int count_phase2 = 0;
            int pref_phase0 = 0;
            int pref_phase1 = 0;
            int pref_phase2 = 0;
            for(int j = 0 ; j < l.size();j++){
                count_phase0 += l.get(j).count_tri_nuc_phase0[i];
                count_phase1 += l.get(j).count_tri_nuc_phase1[i];
                count_phase2 += l.get(j).count_tri_nuc_phase2[i];
                pref_phase0 += l.get(j).pref_tri_nuc_phase0[i];
                pref_phase1 += l.get(j).pref_tri_nuc_phase1[i];
                pref_phase2 += l.get(j).pref_tri_nuc_phase2[i];
            }
            //Count
            fusion.count_tri_nuc_phase0[i]=count_phase0;
            fusion.count_tri_nuc_phase1[i]=count_phase1;
            fusion.count_tri_nuc_phase2[i]=count_phase2;
            //Freq
            if(count_phase0 > 0){
                fusion.freq_tri_nuc_phase0[i]=(double)count_phase0/fusion.nombre_total_trinucleotide;
            }
            if(count_phase1 > 0){
                fusion.freq_tri_nuc_phase1[i]=(double)count_phase1/fusion.nombre_total_trinucleotide;
            }
            if(count_phase2 > 0){
                fusion.freq_tri_nuc_phase2[i]=(double)count_phase2/fusion.nombre_total_trinucleotide;
            }
            //Phase pref
            fusion.pref_tri_nuc_phase0[i]=pref_phase0;
            fusion.pref_tri_nuc_phase1[i]=pref_phase1;
            fusion.pref_tri_nuc_phase2[i]=pref_phase2;   
        }
        
        //Dinuc
        for(int i = 0 ; i  < 16; i++){
            int count_phase0 = 0;
            int count_phase1 = 0;
            int pref_phase0 = 0;
            int pref_phase1 = 0;
            for(int j = 0 ; j < l.size();j++){
                count_phase0 += l.get(j).count_di_nuc_phase0[i];
                count_phase1 += l.get(j).count_di_nuc_phase1[i];
                pref_phase0 += l.get(j).pref_di_nuc_phase0[i];
                pref_phase1 += l.get(j).pref_di_nuc_phase1[i];
            }
            //Count
            fusion.count_di_nuc_phase0[i]=count_phase0;
            fusion.count_di_nuc_phase1[i]=count_phase1;
            //Freq
            if(count_phase0 > 0){
                fusion.freq_di_nuc_phase0[i]=(double)count_phase0/fusion.nombre_total_dinucleotide;
            }
            if(count_phase1 > 0){
                fusion.freq_di_nuc_phase1[i]=(double)count_phase1/fusion.nombre_total_dinucleotide;
            }
            //Pref
            fusion.pref_di_nuc_phase0[i]=pref_phase0;
            fusion.pref_di_nuc_phase1[i]=pref_phase1;
        }
        return fusion;
    }

    // Getters avec l'accès à un seul élt pour faciliter l'écriture de l'excel
    //Occurence
    public int getStatsDinucPhase0Occ(int i){
        return count_di_nuc_phase0[i];
    }
    public int getStatsDinucPhase1Occ(int i){
        return count_di_nuc_phase1[i];
    }
    public int getStatsTrinucPhase0Occ(int i){
        return count_tri_nuc_phase0[i];
    }
    public int getStatsTrinucPhase1Occ(int i){
        return count_tri_nuc_phase1[i];
    }
        public int getStatsTrinucPhase2Occ(int i){
        return count_tri_nuc_phase2[i];
    }
    //Frequence
    public double getStatsDinucPhase0Freq(int i){
        return freq_di_nuc_phase0[i];
    }
    public double getStatsDinucPhase1Freq(int i){
        return freq_di_nuc_phase1[i];
    }
    public double getStatsTrinucPhase0Freq(int i){
        return freq_tri_nuc_phase0[i];
    }
    public double getStatsTrinucPhase1Freq(int i){
        return freq_tri_nuc_phase1[i];
    }
    public double getStatsTrinucPhase2Freq(int i){
        return freq_tri_nuc_phase2[i];
    }
        
    //PhasePref
    public int getStatsDinucPhase0Pref(int i){
        return pref_di_nuc_phase0[i];
    }
    public int getStatsDinucPhase1Pref(int i){
        return pref_di_nuc_phase1[i];
    }
    public int getStatsTrinucPhase0Pref(int i){
        return pref_tri_nuc_phase0[i];
    }
    public int getStatsTrinucPhase1Pref(int i){
        return pref_tri_nuc_phase1[i];
    }
    public int getStatsTrinucPhase2Pref(int i){
        return pref_tri_nuc_phase2[i];
    }
}
