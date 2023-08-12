package test_christian_michel;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
//import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import static java.util.Map.entry;    

public class Main {

	public static void main(String[] args) {
	
		Stocker S = new Stocker();
		Fenetre f = new Fenetre(S);

		protoRecursiveGlobalStats("Tmp/", f);
		
        String[] idsArray = new String[] {  "Viruses","Eukaryota", "Archaea", "Bacteria", "Mito_metazoa", "Phages", "Plasmids", "Samples", "Viroids", "dsDNA_Viruses" } ;
        Hashtable<String,  ArrayList<String>> allNcs;

        ArrayList<String> done = new ArrayList<String>();
		ArrayList<String> allreadyDone = new ArrayList<String>();
		ArrayList<String> doneInSpecie = new ArrayList<String>();
		FileWriter doneFileWriter = null;
		String donePath = "./done.txt";
		try {
			File doneFile = new File(donePath);
			doneFile.createNewFile();
			allreadyDone = new ArrayList<String>(Arrays.asList(new String(
								Files.readAllBytes(Paths.get(donePath))).split("\n")));
			doneFileWriter =  new FileWriter(donePath, true);
		} catch (IOException e1) {
			e1.printStackTrace();
		}

        List<String> blackL = Arrays.asList("NC_031807");
		String[] hierarchy ;
		String[] anc_hierarchy = null;

		Map<String, ArrayList<GenomeStats>> allGS =  Map.ofEntries(
			    entry("Chromosome", new ArrayList<GenomeStats>()),
			    entry("Mitochondrion", new ArrayList<GenomeStats>()),
			    entry("Chloroplast", new ArrayList<GenomeStats>()),
			    entry("DNA", new ArrayList<GenomeStats>()),
			    entry("RNA", new ArrayList<GenomeStats>()),
			    entry("Plasmid", new ArrayList<GenomeStats>())
			);

		f.log("Waiting for go.");
		
		while(S.is_pause==true) {
        	try {
				Thread.sleep(100);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
        }
		
        f.log("Getting all ids.");
        allNcs = getAllNcs(idsArray);
        int nbOfNcs = 0;
        for (String i : idsArray) { nbOfNcs += allNcs.get(i).size(); }
        f.initBarre(nbOfNcs);
        f.log("Done. ("+nbOfNcs+")");		
        f.log("Working on hierarchies.");
        ArrayList<String> human =  new ArrayList<String>(Arrays.asList("NC_000001", "NC_000010", "NC_000011", "NC_000012", "NC_000013", "NC_000014", "NC_000015", "NC_000016", "NC_000017", "NC_000018", "NC_000019", "NC_000002", "NC_000020", "NC_000021", "NC_000022", "NC_000003", "NC_000004", "NC_000005", "NC_000006", "NC_000007", "NC_000008", "NC_000009", "NC_012920", "NC_000023", "NC_000024", "NC_011137", "NC_013993"));
        
        for (String ids : idsArray) {
	        f.log("Working on " + ids);
	        
	        ArrayList<String> allNcIDS = allNcs.get(ids);
	        if (ids ==  "Eukaryota") {
	        	human.addAll(allNcIDS);
	        	allNcIDS = (ArrayList<String>) human ;
	        }

			for (String nc : allNcIDS) {
				try {
		        	f.doneBarre(1);
		        	if (blackL.contains(nc)) {
//		        		f.log(nc + " blacklisted ");
		        		continue;
		        	}
		        	if(allreadyDone.contains(nc)) {
//		        		f.log(nc + " deja passé ");
		        		continue;
		        	}
		        	
//		        	System.out.println(nc);
		        	f.logProgress(nc);
		        	Genome gen = getGenome(nc);
		        	if(gen == null) {
		        		f.log("Error @ "+nc);
		        		continue;
		        	}
		        	hierarchy = gen.getHierarchy();

		    		if(!(Arrays.equals(hierarchy,anc_hierarchy))) {
		    			for(String i : doneInSpecie) {
		    				doneFileWriter.write(i+"\n");
		    				doneFileWriter.flush();
		    			}
		    			done.addAll(doneInSpecie);
		    			doneInSpecie = new ArrayList<String>();
                		f.workingOn( hierarchy );
                 		if (anc_hierarchy != null ) {	 // on exclue le premier qui est init à {}
                			f.isGood(anc_hierarchy);
                			
                			Map<String, GenomeStats> statsGlobArray = new HashMap<String, GenomeStats>();
                			statsGlobArray.put("Chromosome", GenomeStats.mergeStats(allGS.get("Chromosome")));
                			statsGlobArray.put("Mitochondrion", GenomeStats.mergeStats(allGS.get("Mitochondrion")));
                			statsGlobArray.put("Chloroplast", GenomeStats.mergeStats(allGS.get("Chloroplast")));
                			statsGlobArray.put("DNA", GenomeStats.mergeStats(allGS.get("DNA")));
                			statsGlobArray.put("RNA", GenomeStats.mergeStats(allGS.get("RNA")));
                			statsGlobArray.put("Plasmid", GenomeStats.mergeStats(allGS.get("Plasmid")));
                		    
                			
                			String fileSerialize = "./Tmp/"+String.join("/", anc_hierarchy) +".save";
                			File tmp = new File(fileSerialize);
                			tmp.getParentFile().setWritable(true);
                			tmp.getParentFile().mkdirs();

    						FileOutputStream fos = new FileOutputStream(tmp);
    			            ObjectOutputStream oos = new ObjectOutputStream(fos);
    			            oos.writeObject(statsGlobArray);
    			            oos.close();
    			            fos.close();
    						
    						
    						try {
    							ExcelUtilities.createExcelOrganism(statsGlobArray, hierarchy, allGS);
    						
    						} catch (IOException e) {
    							f.log("Error @ "+nc+" : "+e.getMessage());
    							e.printStackTrace();
    						}
					
    						allGS =  Map.ofEntries(
    							    entry("Chromosome", new ArrayList<GenomeStats>()),
    							    entry("Mitochondrion", new ArrayList<GenomeStats>()),
    							    entry("Chloroplast", new ArrayList<GenomeStats>()),
    							    entry("DNA", new ArrayList<GenomeStats>()),
    							    entry("RNA", new ArrayList<GenomeStats>()),
    							    entry("Plasmid", new ArrayList<GenomeStats>())
    							);
                		}
                		anc_hierarchy = hierarchy;
                	}
		    		doneInSpecie.add(nc);
		    		try {
			    		switch(gen.getGenomeType()) {
			    			case "DNA":
			    				allGS.get("DNA").add(new GenomeStats(gen));
			    				break;
			    			case "RNA":
			    				allGS.get("RNA").add(new GenomeStats(gen));
			    				break;
			    			case "mitochondrion":
			    				allGS.get("Mitochondrion").add(new GenomeStats(gen));
			    				break;
			    			case "chloroplast":
			    				allGS.get("Chloroplast").add(new GenomeStats(gen));
			    				break;
			    			case "chromosome":
			    				allGS.get("Chromosome").add(new GenomeStats(gen));
			    				break;
			    			case "plasmid":
			    				allGS.get("Plasmid").add(new GenomeStats(gen));
			    				break;
			    			default:
			    				System.out.println("Not found "+gen.getGenomeType());
			    		}
		    		} catch (Exception e) {
		    			f.log("Error GenomeStat @ "+nc+" "+e.getMessage());
		    			e.printStackTrace();
		    		}
		         		
			} catch(Exception e) {
				e.printStackTrace();
			}
		}
		protoRecursiveGlobalStats("Tmp/", f);
        }
        try {
			doneFileWriter.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	static void protoRecursiveGlobalStats(String path, Fenetre f) {
		try {
			File[] directories = new File(path).listFiles(File::isDirectory);
			for (File d : directories) {
				f.log("Working on global stats for : "+d.getName());
				recursiveGlobalStats(d.getPath(), 0);
				
			}			
		} catch (NullPointerException e) {
			f.log("Pas de stats globales à faire.");	
		}
	}
	
	@SuppressWarnings("unchecked")
	static Map<String, GenomeStats> recursiveGlobalStats(String path, int depth) {
		File[] directories = new File(path).listFiles(File::isDirectory);
		List<Map<String, GenomeStats>> multipleGlobStats = new ArrayList<Map<String, GenomeStats>> ();
		if (directories.length == 0) {			// pas de sous doss, on est donc aux feuilles
			FileInputStream fis;
			ObjectInputStream ois;
			if (!(new File(path).listFiles() == null)) {
				for(File f: new File(path).listFiles()) {
					try {
						fis = new FileInputStream(f);
						ois = new ObjectInputStream(fis);
						multipleGlobStats.add((Map<String,GenomeStats>)ois.readObject());
					} catch (IOException e) {
						e.printStackTrace();
					} catch (ClassNotFoundException e) {
						e.printStackTrace();
					}
				}
			}
		}
		else {
			for (File d : directories) {
				multipleGlobStats.add(recursiveGlobalStats(d.getPath(), depth+1));
			}
		}

		Map<String, GenomeStats> merged = mergeHashMapsGenomesStats(multipleGlobStats);
		try {
			ExcelUtilities.createExcelGlob(merged, path);
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		// creer le excel ad-hoc ....
		return merged;
	}
	
	static Map<String, GenomeStats> mergeHashMapsGenomesStats( List<Map<String, GenomeStats>> allStatsGlobArray ){
		Map<String, GenomeStats> ret = new HashMap<String, GenomeStats>();
		String[] allTypes = { "Chromosome","Mitochondrion","Chloroplast","DNA","RNA","Plasmid"  };
		Map<String, ArrayList<GenomeStats>> tmp ;
		tmp =  Map.ofEntries(
			    entry("Chromosome", new ArrayList<GenomeStats>()),
			    entry("Mitochondrion", new ArrayList<GenomeStats>()),
			    entry("Chloroplast", new ArrayList<GenomeStats>()),
			    entry("DNA", new ArrayList<GenomeStats>()),
			    entry("RNA", new ArrayList<GenomeStats>()),
			    entry("Plasmid", new ArrayList<GenomeStats>())
			);
		for (Map<String, GenomeStats> i : allStatsGlobArray) {
			for(String t : allTypes) {
				if (i.get(t) != null) {
					tmp.get(t).add(i.get(t));
				}
			}
		}
		for(String t : allTypes) {
			ret.put(t, GenomeStats.mergeStats(tmp.get(t)));
		}
		return ret;
	}
	
	static Genome getGenome(String nc) {
		int essais = 1;
		while(essais<4) {
			try {
				return new Genome(nc);
			} catch(IOException ex) {
				essais++;
				try { Thread.sleep(1000); } catch (InterruptedException e) { e.printStackTrace(); }
			}			
		}
//		System.out.println("timeout "+nc);
		return null;
	}
		
	static Hashtable<String,  ArrayList<String>> getAllNcs(String[] idsArray) {
        Hashtable<String,  ArrayList<String>> allNcs = new Hashtable<String,  ArrayList<String>>();
        for(String i : idsArray) {
        	allNcs.put(i, new ArrayList<String>());
        }
        URL url;
        String base = "ftp://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/IDS/";
        String queue=".ids";
        for (String ids : idsArray) {    
        	String urlString = base+ids+queue;
            try {
	        	url = new URL(urlString);
	            BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));
	            String line;
	            Pattern pattern_NC = Pattern.compile("NC_\\d{6}");
	            ArrayList<String> listToAdd = allNcs.get(ids);
	            while ((line = reader.readLine()) != null){    	
	                //On cherche le numero NC dans la ligne
	                Matcher m0 = pattern_NC.matcher(line);
	                if(m0.find()) {
	                	String nc = m0.group();
	                	listToAdd.add(nc);
	                }
	            }
	            reader.close();
            } catch (MalformedURLException e) {
            	e.printStackTrace();
            }
            catch (IOException e) {
				e.printStackTrace();
			}
        }
        return allNcs;
		
	}

}
