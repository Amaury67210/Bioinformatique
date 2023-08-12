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
 * Classe qui va servir à télécharger le genome en entier et à en extraire les gènes valides
 */
public class GenomeUtilities {

    //Le tableau adn, attribut de la classe Genome,contient l'integralite de la sequence adn sous la forme d'un tableau
    //de Strings de taille : taille_max_tab_adn (sauf pour la derniere string du tableau qui peut etre un peu plus petite)
    //Cette fonction renvoit la sequence adn allant de borne_inf(incluse) à  borne_supp(excluse)
    //La fonction part du principe que les indice vont de 0 a  N-1
    //NOTE : substring : les indices vont de 0 a  n-1
    //       substring(2,N) 2 inclus, N exclus
    public static String getGeneSeqFromAdn(int borne_inf,int borne_supp,ArrayList<String> genome,int taille_max_tab_adn){
        if(borne_inf >= borne_supp){
            return null;
        }
        String str = "";
        //On recupere l'indice de la ligne correspondant a chaque borne
        int indiceTabBorneInf = borne_inf/taille_max_tab_adn;
        int indiceTabBorneSupp = borne_supp/taille_max_tab_adn;
        //Si c'est la meme ligne
        if(indiceTabBorneInf == indiceTabBorneSupp){
            str = genome.get(indiceTabBorneInf).substring(borne_inf%taille_max_tab_adn,(borne_supp)%taille_max_tab_adn);
        }
        //Si c'est des lignes differentes
        else{
            //Ajout première ligne
            str = genome.get(indiceTabBorneInf).substring(borne_inf%taille_max_tab_adn,genome.get(indiceTabBorneInf).length());
            //Ajout lignes intermÃ©diares
            indiceTabBorneInf++;
            while(indiceTabBorneInf<indiceTabBorneSupp){
                str = str + genome.get(indiceTabBorneInf);
                indiceTabBorneInf++;
            }
            //Ajout ligne finale
            str =str+genome.get(indiceTabBorneInf).substring(0,(borne_supp)%taille_max_tab_adn);
            
        }
        return str;
    }
    
    
    
    
}
