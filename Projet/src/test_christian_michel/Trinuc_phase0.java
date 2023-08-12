//Travail sur les trinuclÃ©otides en phase 0 (analyse statistique 1)
package test_christian_michel;
import java.text.DecimalFormat;
public class Trinuc_phase0 {
	public float[] freq;
	public String[] tri_nuc;
	int[] compteur;
	public Trinuc_phase0(String test)
	{
		String substring =test.substring(0,test.length()-3); //on coupe le genome pour ne conserver que la phase0
                /*System.out.println("Phase 0__ :");
                System.out.println(substring);*/
                String[] result = phase0(substring);
                this.count_phase0(result);
                /*
                for(int i = 0;i<64;i++){
                    System.out.print(result[i]+" ");
                    System.out.print(compteur[i]+"  ");
                }
                System.out.println("");*/

	}
	private String[] phase0 (String genome)
	{
		String[] resultat=new String[genome.length()/3];
		int i=0;
		for(int j=0;j<genome.length();j++)
			if(j%3==0 && j!=genome.length())
			{
				resultat[i]=""+genome.charAt(j)+genome.charAt(j+1)+genome.charAt(j+2); //on crÃ©e des groupes de 3 pour avoir un tableau de trinuclÃ©otides 
				i++;
			}
		return resultat;
	}
	public void affichage(String[] result) //fonctions d'affichage pour tester
	{
		for (int i=0;i<result.length;i++)
			System.out.println(result[i]);
	}
	public void affichage2(int[] result)
	{
		for (int i=0;i<result.length;i++)
			System.out.println(result[i]);
	}
	
	//ANAYLYSE STATISTIQUE 1
	private void count_phase0(String[] result) //compter le nombre d'occurence de chaque trinuclÃ©otide dans un gÃ¨ne donnÃ©
	{
		DecimalFormat df= new DecimalFormat("0.00");
		tri_nuc= new String[64];
		compteur=new int[64];
		freq=new float[64];
                //Initialisation
                for(int i = 0;i <64;i++){
                    compteur[i]=0;
                    freq[i]=0;
                    tri_nuc[i]=""; //Tableau des "aaa,aac"
                }
		for (int i=0;i<result.length-1;i++)
		{
			for(int j=0;j<tri_nuc.length-1;j++)
			{
				if(result[i].equals(tri_nuc[j])) //si le trinuc courant est dÃ©ja dans le tableau, on incrÃ©mente le compteur correspondant
				{
					compteur[j]++;
					break;
				}
				else if (tri_nuc[j]=="") //sinon, on l'ajoute au tableau et initialise le compteur correspondant Ã  1
				{	
					tri_nuc[j]=""+result[i];
					compteur[j]=1;
					break;
				}
					
					
			}
		}
		for (int i=0;i<tri_nuc.length;i++) //affichage de longueur, frÃ©quence et occurences pour tester
		{
			freq[i]=compteur[i]/(float)(result.length-1); //on calcule la frÃ©quence d'apparition de chaque trinuclÃ©otide dans le gÃ¨ne
		/*
			if(tri_nuc[i]!=null) {
			System.out.println(tri_nuc[i]);
			System.out.println("compteur : "+compteur[i]);
			System.out.println("freq : "+df.format(freq[i]));
			System.out.println("longueur : "+(float)(result.length-1));
			}
			*/
		}
		
	}
        public int[] getOcc(){
            return compteur;
        }
        public String[] getNuc(){
            return tri_nuc;
        }
        public String getNuc(int i){
            return tri_nuc[i];
        }
        public int getOcc(int i){
            return compteur[i];
        }        
        public void setOcc(int[] i){
            this.compteur = i;
        }
}
