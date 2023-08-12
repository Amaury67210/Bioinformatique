//PRINCIPE IDENTIQUE A PHASE 0 MAIS POUR LA PHASE 1
package test_christian_michel;
import java.text.DecimalFormat;
public class Trinuc_phase1 {
	public float[] freq;
	String[] tri_nuc;
	int[] compteur;
	public Trinuc_phase1(String test)
	{
		String substring = test.substring(1,test.length()-2);
                /*System.out.println("Phase 1__ :");
                System.out.println(substring);*/
                String[] result = phase1(substring);
                
                this.count_phase1(result);
                /*
                for(int i = 0;i<64;i++){
                    System.out.print(result[i]+" ");
                    System.out.print(compteur[i]+"  ");
                }
                System.out.println("");*/
	}
	private String[] phase1 (String genome)
	{
		String[] resultat=new String[genome.length()/3];
		int i=0;
		for(int j=0;j<genome.length();j++)
			if(j%3==0 && j!=genome.length())
			{
				resultat[i]=""+genome.charAt(j)+genome.charAt(j+1)+genome.charAt(j+2);
				i++;
			}
		return resultat;
	}
	public void affichage(String[] result)
	{
		for (int i=0;i<result.length;i++)
			System.out.println(result[i]);
	}
	public void affichage2(int[] result)
	{
		for (int i=0;i<result.length;i++)
			System.out.println(result[i]);
	}
	private void count_phase1(String[] result)
	{
		DecimalFormat df= new DecimalFormat("0.00");
		tri_nuc= new String[64];
		compteur=new int[64];
		freq=new float[64];
                //Initialisation
                for(int i = 0;i <64;i++){
                    compteur[i]=0;
                    freq[i]=0;
                    tri_nuc[i]="";
                }
		for (int i=0;i<result.length;i++)
		{
			for(int j=0;j<tri_nuc.length;j++)
			{
				if(result[i].equals(tri_nuc[j]))
				{
					compteur[j]++;
					break;
				}
				else if (tri_nuc[j]=="")
				{	
					tri_nuc[j]=""+result[i];
					compteur[j]=1;
					break;
				}
					
					
			}
		}
		for (int i=0;i<tri_nuc.length;i++)
		{
			freq[i]=compteur[i]/(float)(result.length);
			/*
			if(tri_nuc[i]!=null) {
			System.out.println(tri_nuc[i]);
			System.out.println("compteur : "+compteur[i]);
			System.out.println("freq : "+df.format(freq[i]));
			System.out.println("longueur : "+(float)(result.length));
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
            compteur = i;
        }
}
