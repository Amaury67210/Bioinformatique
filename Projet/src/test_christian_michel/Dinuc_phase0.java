/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package test_christian_michel;

public class Dinuc_phase0 {
	protected float[] freq;
	public String[] di_nuc;
	int[] compteur;
        
	public Dinuc_phase0(String test)
	{
                String substring = "";
		if(test.length()%2==1)
		{
			substring=test.substring(0,test.length()-3);
		}
		else
		{
			substring=test.substring(0,test.length()-4);
		}       
                String[] result = phase0(substring);
                this.count_phase0(result);
	}
        
	private String[] phase0 (String genome)
	{
		String[] resultat=new String[genome.length()/2];
		int i=0;
		for(int j=0;j<genome.length();j++)
		{ 
			if(j%2==0 && j<genome.length()-1)
			{
				resultat[i]=""+genome.charAt(j)+genome.charAt(j+1);
				i++;
			}
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
	private void count_phase0(String[] result)	// erreur ici (init des tableaux)
	{
//		DecimalFormat df= new DecimalFormat("0.00");
		di_nuc= new String[16];
		compteur=new int[16];
		freq=new float[16];
                //Initialisation
                for(int i = 0;i <16;i++){
                    compteur[i]=0;
                    freq[i]=0;
                    di_nuc[i]="";
                }
		for (int i=0;i<result.length;i++)
		{
			for(int j=0;j<di_nuc.length;j++)
			{
				if(result[i].equals(di_nuc[j]))
				{
					compteur[j]++;
					break;
				}
				else if (di_nuc[j]=="")
				{	
					di_nuc[j]=""+result[i];
					compteur[j]=1;
					break;
				}		
			}
		}
		for (int i=0;i<di_nuc.length;i++)
		{
			freq[i]=compteur[i]/(float)(result.length);
			if(di_nuc[i]!=null) {
			//System.out.println(di_nuc[i]);
			//System.out.println("compteur : "+compteur[i]);
			//System.out.println("freq : "+df.format(freq[i]));
			//System.out.println("longueur : "+(float)(result.length));
			}
		}	
	}
        public int[] getOcc(){
            return compteur;
        }
        public String[] getNuc(){
            return di_nuc;
        }
        public String getNuc(int i){
            return di_nuc[i];
        }
        public int getOcc(int i){
            return compteur[i];
        }        public void setOcc(int[] i){
            compteur = i;
        }
}
