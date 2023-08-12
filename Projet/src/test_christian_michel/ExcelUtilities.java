package test_christian_michel;

import java.io.*;
import java.util.ArrayList;

//import org.apache.poi.openxml4j.exceptions.InvalidFormatException;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellStyle;
import org.apache.poi.ss.usermodel.Row;
//import org.apache.poi.ss.usermodel.Sheet;
//import org.apache.poi.ss.usermodel.Workbook;
//import org.apache.poi.ss.usermodel.WorkbookFactory;

import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.util.Map;
import java.util.HashMap;
import static java.util.Map.entry;  


public class ExcelUtilities {
	
	public static void createExcelOrganism(Map<String, GenomeStats> globStats, 
										String[] hierarchy, 
										Map<String, ArrayList<GenomeStats>> allGenomeStats) throws IOException {
		// Si le nom de l'organisme est vide (dû à une erreur HTTP 'Too many requests')
		// on ne crée pas d'excel 
		if (hierarchy[5].isBlank())
			return;
			
		// Initialisations
		int nbCDS = 0;
		int nbInvalidCDS = 0;
		HashMap<String, Integer> nbOfElements = new HashMap<>( Map.ofEntries(
			    entry("Chromosome", 0),
			    entry("Mitochondrion", 0),
			    entry("Chloroplast", 0),
			    entry("DNA", 0),
			    entry("RNA", 0),
			    entry("Plasmid", 0)
			));
		
        XSSFWorkbook workbook = new XSSFWorkbook();
        XSSFSheet sheet;
        XSSFSheet general = workbook.createSheet("General Information");
        
        CellStyle cellStyle = workbook.createCellStyle();
        cellStyle.setDataFormat(
            workbook.getCreationHelper().createDataFormat().getFormat("0.00"));
        
		// Remplissage des onglets Sum_<type>
		for (Map.Entry<String, GenomeStats> entry : globStats.entrySet()) {
			String type = entry.getKey();
    		GenomeStats s = entry.getValue();
        	if (s == null) {
        		continue;
        	}
        	sheet = workbook.createSheet("Sum_" + type);
        	
        	nbOfElements.put(type, s.getNbElements());
        	nbCDS += s.getNombreGene();
			nbInvalidCDS += (s.getNombreGene() - s.getNombreGeneValide());
			
            writeSheetWithStats(sheet, s, cellStyle);
		}
		// onglets de type Chromosome_NC_000000
		for (Map.Entry<String, ArrayList<GenomeStats>> entry : allGenomeStats.entrySet()) {
			String type = entry.getKey();
    		ArrayList<GenomeStats> listStats = entry.getValue();
			for (GenomeStats gs : listStats) {
				sheet = workbook.createSheet(type + "_" + gs.getIdNC());
				writeSheetWithStats(sheet, gs, cellStyle);
			}
		}
         
        // Remplissage de l'onglet General Information
		writeGeneralInfoSheet(general, hierarchy[5], nbOfElements, nbCDS, nbInvalidCDS, cellStyle);

        // Création de répertoires et écriture du fichier
        String path = "Results/";
		for (int i = 0; i < 5; i++)
			if (!hierarchy[i].isEmpty())
				path += hierarchy[i] + "/";
        File f = new File(path);
        f.mkdirs();

        path += hierarchy[5] + ".xlsx";
        try (FileOutputStream outputStream = new FileOutputStream(path)) {
            workbook.write(outputStream);
        }
        workbook.close();
	}
	
	public static void createExcelGlob(Map<String, GenomeStats> stats, String path)
	// ex de param : path = "Eukaryota/Animals/", taxonName = "Mammals" 
	throws IOException {
		// Initialisations
		int nbCDS = 0;
		int nbInvalidCDS = 0;
/*
		Map<String, Integer> nbOfElements =  Map.ofEntries(
			    entry("Chromosome", 0),
			    entry("Mitochondrion", 0),
			    entry("Chloroplast", 0),
			    entry("DNA", 0),
			    entry("RNA", 0),
			    entry("Plasmid", 0)
			);
*/
		Map<String, Integer> nbOfElements = new HashMap<String, Integer>();
        XSSFWorkbook workbook = new XSSFWorkbook();
        
        XSSFSheet sheet;
        XSSFSheet general = workbook.createSheet("General Information");
        
        CellStyle cellStyle = workbook.createCellStyle();
        cellStyle.setDataFormat(
            workbook.getCreationHelper().createDataFormat().getFormat("0.00"));
        
		// Remplissage des onglets Sum_<type>
		for (Map.Entry<String, GenomeStats> entry : stats.entrySet()) {
			String type = entry.getKey();
    		GenomeStats s = entry.getValue();
        	if (s == null) {
        		continue;
        	}
        	sheet = workbook.createSheet("Sum_" + type);
        	
        	nbOfElements.put(type, s.getNbElements());
        	nbCDS += s.getNombreGene();
			nbInvalidCDS += (s.getNombreGene() - s.getNombreGeneValide());
			
            writeSheetWithStats(sheet, s, cellStyle);
		}
		
		String[] hierarchy = path.split("\\\\");
         
		// Remplissage de l'onglet General Information
		writeGeneralInfoSheet(general, hierarchy[hierarchy.length-1], nbOfElements, nbCDS, nbInvalidCDS, cellStyle);
        
        // Création de répertoires et écriture du fichier
		String fullPath = "Results/";
		for (int i = 1; i < hierarchy.length-1; i++)
			fullPath += hierarchy[i] + "/";
        File f = new File(fullPath);
        f.mkdirs();
        fullPath += "Total_" + hierarchy[hierarchy.length-1] + ".xlsx";
        try (FileOutputStream outputStream = new FileOutputStream(fullPath)) {
            workbook.write(outputStream);
        }
        workbook.close();
	}
	
	public static void writeGeneralInfoSheet(XSSFSheet general, String taxonName, Map<String, Integer> nbOfElements,
											int nbCDS, int nbInvalidCDS, CellStyle cellStyle) {
		Object[] rowData;
		for (int rowCount = 1; rowCount <= 11; rowCount++) {
            Row row = general.createRow(rowCount);
            
            if (rowCount == 1)
            	rowData = new Object[] {"Information"};
            else if (rowCount == 3)
            	rowData = new Object[] {"Name", taxonName, "", "", "", "Genome"};
            else if (rowCount == 4)
            	rowData = new Object[] {"", "", "", "", "", "Chromosome", nbOfElements.get("Chromosome")};
            else if (rowCount == 5)
            	rowData = new Object[] {"Modification Date", "", "", "", "", "Mitochondrion", nbOfElements.get("Mitochondrion")};
            else if (rowCount == 6)
            	rowData = new Object[] {"", "", "", "", "", "Chloroplast", nbOfElements.get("Chloroplast")};
            else if (rowCount == 7)
            	rowData = new Object[] {"Number of CDS sequences", nbCDS, "", "", "", "DNA", nbOfElements.get("DNA")};
            else if (rowCount == 8)
            	rowData = new Object[] {"", "", "", "", "", "RNA", nbOfElements.get("RNA")};
            else if (rowCount == 9)
            	rowData = new Object[] {"Number of invalid CDS", nbInvalidCDS, "", "", "", "Plasmid", nbOfElements.get("Plasmid")};
            else if (rowCount == 11)
            	rowData = new Object[] {"Number of Organisms", 1};
            else rowData = new Object[0];
            
            putRowDataInRow(row, rowData, cellStyle); 
        }
	}
	
	public static void writeSheetWithStats(XSSFSheet sheet, GenomeStats s, CellStyle cellStyle) {
		Object[] rowData;
		Object[] headers = {"", "Phase 0", "Freq Phase 0", 
    			"Phase 1", "Freq Phase 1", 
    			"Phase 2", "Freq Phase 2", 
    			"Pref Phase 0", "Pref Phase 1", "Pref Phase 2",
    			"", "STATISTIQUES DINUCLEOTIDES", 
    			"", "Phase 0", "Freq Phase 0", 
    			"Phase 1", "Freq Phase 1",
				"Pref Phase 0", "Pref Phase 1"};
				
		String[] trinucName = s.getTrinucName();
		String[] dinucName = s.getDinucName();

		for (int rowCount = 0; rowCount <= 65; rowCount++) {
			Row row = sheet.createRow(rowCount);
			if (rowCount == 0)
				rowData = headers;
			else if (rowCount >= 1 && rowCount <= 16)
				rowData = new Object[] {trinucName[rowCount-1], 
						s.getStatsTrinucPhase0Occ(rowCount-1), s.getStatsTrinucPhase0Freq(rowCount-1),
						s.getStatsTrinucPhase1Occ(rowCount-1), s.getStatsTrinucPhase1Freq(rowCount-1),
						s.getStatsTrinucPhase2Occ(rowCount-1), s.getStatsTrinucPhase2Freq(rowCount-1),
						s.getStatsTrinucPhase0Pref(rowCount-1),
						s.getStatsTrinucPhase1Pref(rowCount-1),
						s.getStatsTrinucPhase2Pref(rowCount-1),
						"", "",
						dinucName[rowCount-1], 
						s.getStatsDinucPhase0Occ(rowCount-1), s.getStatsDinucPhase0Freq(rowCount-1),
						s.getStatsDinucPhase1Occ(rowCount-1), s.getStatsDinucPhase1Freq(rowCount-1),
						s.getStatsDinucPhase0Pref(rowCount-1),
						s.getStatsDinucPhase1Pref(rowCount-1)
						};
			else if (rowCount == 17)
				rowData = new Object[] {trinucName[rowCount-1], 
						s.getStatsTrinucPhase0Occ(rowCount-1), s.getStatsTrinucPhase0Freq(rowCount-1),
						s.getStatsTrinucPhase1Occ(rowCount-1), s.getStatsTrinucPhase1Freq(rowCount-1),
						s.getStatsTrinucPhase2Occ(rowCount-1), s.getStatsTrinucPhase2Freq(rowCount-1),
						s.getStatsTrinucPhase0Pref(rowCount-1),
						s.getStatsTrinucPhase1Pref(rowCount-1),
						s.getStatsTrinucPhase2Pref(rowCount-1),
						"", "", "Total",
						s.getNombreDinuc(), 100, 
						s.getNombreDinuc(), 100
						};
			else if (rowCount == 19)
				rowData = new Object[] {trinucName[rowCount-1], 
						s.getStatsTrinucPhase0Occ(rowCount-1), s.getStatsTrinucPhase0Freq(rowCount-1),
						s.getStatsTrinucPhase1Occ(rowCount-1), s.getStatsTrinucPhase1Freq(rowCount-1),
						s.getStatsTrinucPhase2Occ(rowCount-1), s.getStatsTrinucPhase2Freq(rowCount-1),
						s.getStatsTrinucPhase0Pref(rowCount-1),
						s.getStatsTrinucPhase1Pref(rowCount-1),
						s.getStatsTrinucPhase2Pref(rowCount-1),
						"", "Informations"
						};
			else if (rowCount == 20)
				rowData = new Object[] {trinucName[rowCount-1], 
						s.getStatsTrinucPhase0Occ(rowCount-1), s.getStatsTrinucPhase0Freq(rowCount-1),
						s.getStatsTrinucPhase1Occ(rowCount-1), s.getStatsTrinucPhase1Freq(rowCount-1),
						s.getStatsTrinucPhase2Occ(rowCount-1), s.getStatsTrinucPhase2Freq(rowCount-1),
						s.getStatsTrinucPhase0Pref(rowCount-1),
						s.getStatsTrinucPhase1Pref(rowCount-1),
						s.getStatsTrinucPhase2Pref(rowCount-1),
						"", "Number of CDS sequences", s.getNombreGene()
						};
			else if (rowCount == 21)
				rowData = new Object[] {trinucName[rowCount-1], 
						s.getStatsTrinucPhase0Occ(rowCount-1), s.getStatsTrinucPhase0Freq(rowCount-1),
						s.getStatsTrinucPhase1Occ(rowCount-1), s.getStatsTrinucPhase1Freq(rowCount-1),
						s.getStatsTrinucPhase2Occ(rowCount-1), s.getStatsTrinucPhase2Freq(rowCount-1),
						s.getStatsTrinucPhase0Pref(rowCount-1),
						s.getStatsTrinucPhase1Pref(rowCount-1),
						s.getStatsTrinucPhase2Pref(rowCount-1),
						"", "Number of invalid CDS", s.getNombreGene() - s.getNombreGeneValide()
						};
			else if (rowCount >= 22 && rowCount <= 64 || rowCount == 18)
				rowData = new Object[] {trinucName[rowCount-1], 
						s.getStatsTrinucPhase0Occ(rowCount-1), s.getStatsTrinucPhase0Freq(rowCount-1),
						s.getStatsTrinucPhase1Occ(rowCount-1), s.getStatsTrinucPhase1Freq(rowCount-1),
						s.getStatsTrinucPhase2Occ(rowCount-1), s.getStatsTrinucPhase2Freq(rowCount-1),
						s.getStatsTrinucPhase0Pref(rowCount-1),
						s.getStatsTrinucPhase1Pref(rowCount-1),
						s.getStatsTrinucPhase2Pref(rowCount-1)
						};
			else 
				rowData = new Object[] {"Total",
						s.getNombreTrinuc(), 100,
						s.getNombreTrinuc(), 100, 
						s.getNombreTrinuc(), 100
						};
			putRowDataInRow(row, rowData, cellStyle);
		}
	}

	public static void putRowDataInRow(Row row, Object[] rowData, CellStyle cellStyle) {
		int columnCount = 0;
		for (Object field : rowData) {
				Cell cell = row.createCell(++columnCount);
				if (field instanceof String) {
					cell.setCellValue((String) field);
				} else if (field instanceof Integer) {
					cell.setCellValue((Integer) field);
				} else if (field instanceof Double) {
					cell.setCellValue((Double) field * 100);
					cell.setCellStyle(cellStyle);
				}
			}
	}
 
}
