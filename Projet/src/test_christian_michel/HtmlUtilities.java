/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package test_christian_michel;

import java.io.*;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;
//import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * @author ShiroiMao asus
 * Classe relative à tout ce qui touche au web et au téléchargement des données
 * Téléchargement du génome complet
 * Téléchargement des cds
 *
 */
public class HtmlUtilities {
    //Fonction qui renvoit le contenue d'une page htlm sous la forme d'une string
    //Attention une page html ne contient pas les données Json
    public static String getHTMLToString(String urlString) throws IOException {
        URL url;
        String str = "";
        try {
            url = new URL(urlString);
            BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));
            String line;
            while ((line = reader.readLine()) != null){
                str=str+line;
                //System.out.println(line);
            }
            reader.close();
        } catch (MalformedURLException ex) {
            Logger.getLogger(Genome.class.getName()).log(Level.SEVERE, null, ex);     
        }
        return str;
    }
    
    //##################################################################################################################
    //Recupere toute la sequence adn dans un vecteur sous la forme de string de taille taille_max_tab_adn
    //https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_007788&rettype=fasta&retmode=text
    
    public static ArrayList<String> getGenomeFromGenbank(String nucoreId,int taille_max_tab_adn) throws IOException{
        ArrayList<String> adn;
        adn = new ArrayList<String>();
        URL url;
        String str = "";
        String base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=";
        String queue = "&rettype=fasta&retmode=text";
        //String str = getHTMLToString(base+nucoreId+queue); Ne supporte pas les fchiers de grande taille
        String urlString = base+nucoreId+queue;
        boolean firstRow = true;
        try {
            //On va lire les données de l'API comme une input stream
            url = new URL(urlString);
            BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));
            String line;
            
            //Compteur compte le nombre de charactere de la string en train d'etre remplie
            int compteur = 0;
            //Tant qu'il y  a quelque chose à  lire:
            while ((line = reader.readLine()) != null){
                //La première ligne est une entête, donc on l'ignore
                if(firstRow){
                    firstRow = false;
                }
                else{
                    //Si la string n'a pas dÃ©passÃ© le nombre de caractÃ¨re spÃ©cifiÃ© par taille_max_tab_adn
                    if(compteur+line.length()<taille_max_tab_adn){
                        //System.out.println(line.length() + " " + str.length() );
                        str=str+line;
                        compteur = compteur + line.length();
                    }
                    //Si la line est juste Ã  la bonne taille pour rentrer entiÃ¨rement dans la string
                    else if(compteur+line.length()==taille_max_tab_adn){
                        str=str+line;
                        adn.add(str);
                        compteur = 0;
                        str="";
                    }
                    //Si la line est trop grande pour etre mise entiÃ¨rement dans la string
                    else if(compteur+line.length()>taille_max_tab_adn){
                        //Calcul de la taille de ce qui depasse
                        int taille_surplux = compteur+line.length()-taille_max_tab_adn;
                        //On va enlever ce qui depasse
                        str=str+line.substring(0,line.length()-taille_surplux);
                        adn.add(str);
                        //On va rajouter la partie qui depasse dans une nouvelle string (nouvelle case du tableau)
                        str=line.substring((line.length()-taille_surplux),line.length());
                        compteur = str.length();     
                    }
                    //Si j'ai oubliÃ© un cas
                    else{
                        System.out.println("Erreur condition non prevue init adn");
                        System.exit(1);
                    }
                }
                //System.out.println(line);
            }
            
            //Ajout de la derniÃ¨re ligne lue :
            //Si il y a eu un surplus avant il n'a pas encore Ã©tÃ© ajoutÃ© au tableau
            if(compteur > 0){
               adn.add(str);
            }
            reader.close();
        } catch (MalformedURLException ex) {
            Logger.getLogger(Genome.class.getName()).log(Level.SEVERE, null, ex);
        }
        return adn;
    }
    
    
    //RecupÃ¨re le fichier contenant les CDS en le lisant comme un input stream
    //utilise des regex sur le stream pour extraire les CDS sur 4 type : simple, join, complement et complement join
    //Pour chaque expression trouvÃ©, forme la sequence correspndante et regarde Ã§a validitÃ©
    //Si la sequence est valide, la met dans tab_gene_valide
    //JE N'AI PAS RELU CETTE FONCTION UNE DEUXIEME FOIS CONTRAIREMENT AU RESTE
    //Retourne tous les gènes valides
    public static ArrayList<String> getGeneFromGenbank(String nuccoreId, ArrayList<String> Genome,int tailleGenome,int tailleStringGenome) throws IOException {
        ArrayList<String> tab_gene;
        tab_gene = new ArrayList<String>();
        
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

            while ((line = reader.readLine()) != null){
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
        return tab_gene;
    }
    
    public static String[] getHierarchyFromGenbank(String nuccoreId) {
        
        String[] hierarchy = new String[] {"", "", "", "", "", ""};
        URL url;
        String base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=";
        String queue="&rettype=gbwithparts&retmode=text";
        String urlString = base+nuccoreId+queue;
        boolean hierarchyTrouve = false;
        try {
            url = new URL(urlString);
            BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));
            String line;

            Pattern pattern_hierarchy = Pattern.compile("\\s+ORGANISM\\s+");
            Pattern pattern_dot = Pattern.compile("[^\\.]*\\.");

            while (((line = reader.readLine()) != null)&& (!hierarchyTrouve)){
                //on cherche une ligne commenÃ§ant par "ORGANISME" (contient le nom de lorganisme)
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
                    hierarchyTrouve = true;
                } 
            }
            reader.close();
        } catch (MalformedURLException ex) {
            Logger.getLogger(Genome.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(Genome.class.getName()).log(Level.SEVERE, null, ex);
        }
        return hierarchy;
    }
    
    
      //Cherche si le genome est celui d'un chromozome, un motochndrion, un DNA ou un plasmid
    public static String getGenomeTypeFromGenbank(String nuccoreId){
        //lien complet :https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_007788.2&rettype=gbwithparts&retmode=text
        String genomeType = "";
        URL url;
        String base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=";
        String queue="&rettype=gbwithparts&retmode=text";
        String urlString = base+nuccoreId+queue;
        
        //On va lire seulement le dÃ©but du fichier : 100 premiÃ¨re ligne
        try {
            url = new URL(urlString);
            BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));
            String line;
            
            //Pour une version propre supprimer ces patern dÃ©geulasse et en trouver des bons
               
            Pattern patern_chromosome = Pattern.compile("DEFINITION.*chromosome");
            Pattern patern_DNA = Pattern.compile("=.*DNA");
            Pattern patern_mitochondrion = Pattern.compile("DEFINITION.*mitochondrion");
            Pattern patern_chloroplast = Pattern.compile("chloroplast");
            Pattern patern_plasmid = Pattern.compile("DEFINITION.*plasmid");
            Pattern patern_RNA = Pattern.compile("=.*RNA");
          
            int compteur = 0;
            while ((compteur < 100) && ((line = reader.readLine()) != null)){

                //On regarde s'il y  a un CDS dans la ligne
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
                    break;
                }
                if(m2.find()){
                    //System.out.println(line);
        //            System.out.println("mitochondrion");
                    genomeType="mitochondrion";
                    break;
                }
                if(m3.find()){
                    //System.out.println(line);
             //       System.out.println("chloroplast");
                    genomeType="chloroplast";
                    break;
                }
                if(m4.find()){
                    //System.out.println(line);
           //         System.out.println("plasmid");
                    genomeType="plasmid";
                    break;
                }
                if(m1.find()){
                    //System.out.println(line);
           //         System.out.println("DNA");
                    genomeType="DNA";
                    break;
                }
                if(m5.find()){
                    //System.out.println(line);
       //             System.out.println("RNA");
                    genomeType="RNA";
                    break;
                }
                compteur = compteur +1;
            }
            reader.close();
        } catch (MalformedURLException ex) {
            Logger.getLogger(Genome.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
//            Logger.getLogger(Genome.class.getName()).log(Level.SEVERE, null, ex);
        }
        return genomeType;
    }
}
