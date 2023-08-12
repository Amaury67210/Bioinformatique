/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package test_christian_michel;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * @author ShiroiMao asus
 */


//Problème : des fois ya 4 fois le meme CDS avec un nom de gene identique mais un des nombres qui change

public class Genome {
    private String genomeType = "inconnu";
    private String id_NC = "";
    
    //Contient la hierarchie
    private String[] hierarchy;
    
    //Contient toute la sequence adn du chromosome
    private ArrayList<String> genome;
    private int tailleMaxStringGenome = 10000;
    
    //Contient les genes
    private ArrayList<String> tab_gene;
    
    //Contient les genes valides
    private ArrayList<String> tab_gene_valide;
   
    
    

//Constructeurs et accesseurs et affichage
    
    public Genome(){
        this.hierarchy = new String[] {"", "", "", "", "", ""};
        this.genomeType = "unknow";
        genome = new ArrayList<String>();
        tab_gene = new ArrayList<String>();
        tab_gene_valide = new ArrayList<String>();
    }
    public Genome(String id_NC) throws IOException{
        //Initialisation
        this.id_NC=id_NC;
        genome = new ArrayList<String>();
        this.tab_gene_valide = new ArrayList<String>();
        this.hierarchy = new String[] {"", "", "", "", "", ""};
        
        //Téléchargement des données
        //this.genomeType=HtmlUtilities.getGenomeTypeFromGenbank(id_NC);
        //System.out.println("Obtention du type :"+genomeType);
        //this.hierarchy=HtmlUtilities.getHierarchyFromGenbank(id_NC);
        /*System.out.println("Obtention hierarchie :"+hierarchy[0]+"/"+hierarchy[1]+"/"+
                hierarchy[2]+"/"+hierarchy[3]+"/"+hierarchy[4]+"/"+hierarchy[5]);*/
        //Telechargement genome
        this.genome=HtmlUtilities.getGenomeFromGenbank(id_NC, this.tailleMaxStringGenome);
        // System.out.println("Telechargement genome termine");
        //Telechargement cds et parsing
        int tailleGenome = 0;
        for(int i = 0;i<genome.size();i++){
            tailleGenome=tailleGenome + genome.get(i).length();
        }
        //this.tab_gene=HtmlUtilities.getGeneFromGenbank(id_NC, genome, tailleGenome, tailleMaxStringGenome);
        //System.out.println("Telechargment et parsing gene termine");
        this.tab_gene=this.getGeneFromGenbankV2(id_NC, genome, tailleGenome, tailleMaxStringGenome);
        
        
        //Extraction des gènes valides
        for(int i = 0;i<tab_gene.size();i++){
            if(GeneUtilities.isValide(tab_gene.get(i))){
                tab_gene_valide.add(tab_gene.get(i));
            }
        }

    }
    public void getInfo(){
        System.out.println(this.id_NC+ " : ");
        System.out.println("Type : "+this.genomeType);
        System.out.println("Obtention hierarchie :"+hierarchy[0]+"/"+hierarchy[1]+"/"+
                hierarchy[2]+"/"+hierarchy[3]+"/"+hierarchy[4]+"/"+hierarchy[5]);
        System.out.println("Nombre gene : "+tab_gene.size());
        System.out.println("Nombre gene valide : "+tab_gene_valide.size()+" ("+(tab_gene_valide.size()*100)/tab_gene.size()+"%)");
    }
    
    public int getNombreGene(){
        return tab_gene.size();
    }

    public String getNC(){
        return this.id_NC;
    }
    
    public int getNombreGeneValide(){
        return tab_gene_valide.size();
    }
    
    public ArrayList<String> getGeneValide(){
        return this.tab_gene_valide;
    }
    
    public void afficherGenome(){
        System.out.println("Genome complet ::: ");
        for(int i = 0; i < this.genome.size(); i++) {
            System.out.println(genome.get(i)); 
        } 
    }
    
    public void afficherGene(){
        for(int i = 0; i < tab_gene.size(); i++) {
            System.out.println("Taille gene : " +tab_gene.get(i).length());
            System.out.println(tab_gene.get(i)); 
        }
    }
    
    public void afficherGeneValide(){
        for(int i = 0; i < tab_gene_valide.size(); i++) {
            System.out.println("Taille gene : " +tab_gene_valide.get(i).length());
            System.out.println(tab_gene_valide.get(i)); 
        }
    }
    
    public String[] getHierarchy() {
        return this.hierarchy;
    }

    String getGenomeType(){
        return this.genomeType; 
    }

    //Fonction dégeu qui :
    //Retourne tous les gènes valides
    //Chope le type
    //Chope la hierarchie
    public ArrayList<String> getGeneFromGenbankV2(String nuccoreId, ArrayList<String> Genome,int tailleGenome,int tailleStringGenome) throws IOException{
        ArrayList<String> tab_gene;
        tab_gene = new ArrayList<String>();
        String[] hierarchy = new String[] {"", "", "", "", "", ""};
        String genomeType = "";
        
        URL url;
        String base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=";
        String queue="&rettype=gbwithparts&retmode=text";
        String urlString = base+nuccoreId+queue;
        try {
            url = new URL(urlString);
            BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));
            String line;
            
            //Pour l'affichage
            Pattern patern_rien_aff = Pattern.compile("CDS\\s+(\\d+\\.\\.\\d+)");
            Pattern patern_complement_aff = Pattern.compile("CDS\\s+(complement\\((\\d+\\.\\.\\d+,)*\\d+\\.\\.\\d+\\))");
            Pattern patern_join_aff = Pattern.compile("CDS\\s+(join\\((\\d+\\.\\.\\d+,)+\\d+\\.\\.\\d+\\))");
            Pattern patern_complement_join_aff = Pattern.compile("CDS\\s+(complement\\(join\\((\\d+\\.\\.\\d+,)+\\d+\\.\\.\\d+\\)\\))");
                
            //Pour le code
            Pattern patern_CDS = Pattern.compile("CDS\\s+((\\d+\\.\\.\\d+)|(join)|(complement))");
            Pattern patern_gene = Pattern.compile(".*=.*");//Peu etre pas la plus solide des idÃ©es mais Ã§a fonctionne
            Pattern patern_rien = Pattern.compile("CDS\\s+(\\d+\\.\\.\\d+)");
            Pattern patern_complement = Pattern.compile("CDS\\s+complement\\(((\\d+\\.\\.\\d+,)*\\d+\\.\\.\\d+)\\)");
            Pattern patern_join = Pattern.compile("CDS\\s+join\\(((\\d+\\.\\.\\d+,)+\\d+\\.\\.\\d+)\\)");
            Pattern patern_complement_join = Pattern.compile("CDS\\s+complement\\(join\\(((\\d+\\.\\.\\d+,)+\\d+\\.\\.\\d+)\\)\\)");

            //Pour le type:
            boolean type_founded = false;
            Pattern patern_chromosome = Pattern.compile("DEFINITION.*chromosome");
            Pattern patern_DNA = Pattern.compile("=.*DNA");
            Pattern patern_mitochondrion = Pattern.compile("DEFINITION.*mitochondrion");
            Pattern patern_chloroplast = Pattern.compile("chloroplast");
            Pattern patern_plasmid = Pattern.compile("DEFINITION.*plasmid");
            Pattern patern_RNA = Pattern.compile("=.*RNA");
            
            //Pour la hierarchy
            boolean hierarchy_founded = false;
            Pattern pattern_hierarchy = Pattern.compile("\\s+ORGANISM\\s+");
            Pattern pattern_dot = Pattern.compile("[^\\.]*\\.");
            
            while ((line = reader.readLine()) != null){
                //Hierachy
                if(!hierarchy_founded){
                    Matcher m_h = pattern_hierarchy.matcher(line);
                    if (m_h.find()) {
                        hierarchy[5] = m_h.replaceFirst("");
                        //System.out.println(this.hierarchy[5]);
                        line = reader.readLine();
                        //on lit les lignes suivantes pour extraire toute l'hiÃ©rarchie
                        Matcher m_dot = pattern_dot.matcher(line);
                        while (!m_dot.find()) {
                            String linesupp = reader.readLine();
                            line += linesupp;
                            m_dot = pattern_dot.matcher(linesupp);
                        }
                        line = line.replaceAll("\\s", "");
                        //On rÃ©cupÃ¨re les 5 premiers
                        String[] splitArray = line.split(";", 6);
                        for (int i = 0; (i<5) && (i<splitArray.length); i++){
                            hierarchy[i] = splitArray[i];
                        //System.out.println(i + " " + this.hierarchy[i]);
                        }
                        hierarchy_founded = true;
                    }
                }
                
                //Type
                if(!type_founded){
                    Matcher m0 = patern_chromosome.matcher(line);
                    Matcher m1 = patern_DNA.matcher(line);
                    Matcher m2 = patern_mitochondrion.matcher(line);
                    Matcher m3 = patern_chloroplast.matcher(line);
                    Matcher m4 = patern_plasmid.matcher(line);
                    Matcher m5 = patern_RNA.matcher(line);

                    if(m0.find()){
                        //System.out.println(line);
                //        System.out.println("chromosome");
                        genomeType="chromosome";
                        type_founded = true;
                    }
                    if(m2.find()){
                        //System.out.println(line);
            //            System.out.println("mitochondrion");
                        genomeType="mitochondrion";
                        type_founded = true;
                    }
                    if(m3.find()){
                        //System.out.println(line);
                 //       System.out.println("chloroplast");
                        genomeType="chloroplast";
                        type_founded = true;
                    }
                    if(m4.find()){
                        //System.out.println(line);
               //         System.out.println("plasmid");
                        genomeType="plasmid";
                        type_founded = true;
                    }
                    if(m1.find()){
                        //System.out.println(line);
               //         System.out.println("DNA");
                        genomeType="DNA";
                        type_founded = true;
                    }
                    if(m5.find()){
                        //System.out.println(line);
           //             System.out.println("RNA");
                        genomeType="RNA";
                        type_founded = true;
                    }
                }
                
                //Partie CDS
                //On regarde s'il y  a un CDS dans la ligne
                Matcher m0 = patern_CDS.matcher(line);
                if(m0.find()){
                    Matcher m02 = patern_gene.matcher(line);
                    
                    //On ajoute les ligne suivante pour obtenir toute l'information du CDS : on lit jusqu'à \gene
                    //System.out.println(line);
                    String linesupp = "";
                    
                    boolean mybreaktest = false;
                    while (!mybreaktest && !m02.find()){
                        if((linesupp = reader.readLine()) != null){
                            //System.out.println("linesupp : "+linesupp);
                            linesupp = linesupp.replaceAll("\\s", "");
                            line += linesupp;
                            m02 = patern_gene.matcher(linesupp);
                        }
                        else{
                            mybreaktest = true;
                        }
                    }
                    
                    
                    //System.out.println(line); Interessant pour voir qu'il y a en fait plusieurs fois le meme cds dans le fichier
                    //Affichage
                    /*
                    Matcher aff_1 = patern_rien_aff.matcher(line);
                    Matcher aff_2 = patern_complement_aff.matcher(line);
                    Matcher aff_3 = patern_join_aff.matcher(line);
                    Matcher aff_4 = patern_complement_join_aff.matcher(line);
                    */

                    Matcher m1 = patern_rien.matcher(line);
                    Matcher m2 = patern_complement.matcher(line);
                    Matcher m3 = patern_join.matcher(line);
                    Matcher m4 = patern_complement_join.matcher(line);

                    //Affichage
                    /*
                    while (aff_1.find()){ System.out.print(aff_1.group(1)+"\n");}
                    while (aff_2.find()){ System.out.print(aff_2.group(1)+"\n");}
                    while (aff_3.find()){ System.out.print(aff_3.group(1)+"\n");}
                    while (aff_4.find()){ System.out.print(aff_4.group(1)+"\n");}
                    */
                    while (m1.find()){
                        
                        //System.out.println("Trouve :"+m1.group(1));
                        String s = StringUtilities.simple(m1.group(1),Genome,tailleGenome,tailleStringGenome);
                        //System.out.println(s);
                        if(s != null){
                            //System.out.println("Gene valide trouvÃ©.");
                            //System.out.println(s);
                            
                            tab_gene.add(s);
                        }
                    }
                    while (m2.find()){
                        //System.out.println("Trouve :"+m2.group(1));
                        String s = StringUtilities.complement(m2.group(1),Genome,tailleGenome,tailleStringGenome);
                        //System.out.println(s);
                        if(s != null){
                            //System.out.println("Gene valide trouvÃ©.");
                            //System.out.println(s);
                            tab_gene.add(s);
                        }
                    }
                    while (m3.find()){
                        String s = StringUtilities.join(m3.group(1),Genome,tailleGenome,tailleStringGenome);
                        //System.out.println(s);
                        if(s != null){
                            //System.out.println("Gene valide trouvÃ©.");
                            //System.out.println(s);
                            tab_gene.add(s);
                        }
                    }   
                    while (m4.find()){
                        String s = StringUtilities.complementJoin(m4.group(1),Genome,tailleGenome,tailleStringGenome);
                        //System.out.println(s);
                        if(s != null){
                            //System.out.println("Gene valide trouvÃ©.");
                            //System.out.println(s);
                            tab_gene.add(s);
                        }
                    }
                }
            }
            reader.close();
        } catch (MalformedURLException ex) {
            Logger.getLogger(Genome.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        for (int i=0; i<hierarchy.length; i++) {	// gestion des problèmes dans les hierarchies
        	if(hierarchy[i]=="")
        		hierarchy[i]="unknown";
        	else {
        		hierarchy[i]= hierarchy[i].replace("\\", "_").replace(".", "_").replace("/", "_").replace(":", "_").replace("[", "_").replace("]", "_");
        	}
        }

        this.hierarchy = hierarchy;
        this.genomeType = genomeType;
        return tab_gene;
    }
}

