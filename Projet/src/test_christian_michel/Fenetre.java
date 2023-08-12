package test_christian_michel;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JProgressBar;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTree;
import javax.swing.WindowConstants;
import javax.swing.text.BadLocationException;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeCellRenderer;
import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;

import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.TreeNode;


public class Fenetre extends JFrame {
  
	/**
	 * 
	 */
	private static final long serialVersionUID = -5285602033430483872L;
	private JPanel 		pan = 		new JPanel();
	private JButton 	bouton =	new JButton("Go");
	private JTextArea	textLog	=	new JTextArea(65, 30);
	private JProgressBar barre =	new JProgressBar();
	private JTree tree;
	
	
	private DefaultMutableTreeNode root  = new DefaultMutableTreeNode("root");
  
	private int nbLogs = 0;
	
	public Fenetre(Stocker S){

		this.setTitle("GenBank");
		this.setSize(500, 350);
		this.setLocationRelativeTo(null);
		this.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);

		JScrollPane scoll = new JScrollPane(textLog);
		textLog.setEditable(false);
		this.log("====DEBUT====\n");
 
	    tree = new JTree(root);
		tree.setCellRenderer(new DefaultTreeCellRenderer() {	
			/**
			 * 
			 */
			private static final long serialVersionUID = -7857980626261996475L;
			URL url = ClassLoader.getSystemClassLoader().getResource("icon-orange.png");
			private Icon loadIcon =  new ImageIcon(new ImageIcon(url).getImage().getScaledInstance(10, 10,  java.awt.Image.SCALE_SMOOTH));
			URL url2 = ClassLoader.getSystemClassLoader().getResource("icon-red.png");
	        private Icon badIcon =  new ImageIcon(new ImageIcon(url2).getImage().getScaledInstance(10, 10,  java.awt.Image.SCALE_SMOOTH));
			URL url3 = ClassLoader.getSystemClassLoader().getResource("icon-green.png");
	        private Icon goodIcon =  new ImageIcon(new ImageIcon(url3).getImage().getScaledInstance(10, 10,  java.awt.Image.SCALE_SMOOTH));
	       	        
	        @Override
	        public Component getTreeCellRendererComponent(JTree tree,
	                Object value, boolean selected, boolean expanded,
	                boolean isLeaf, int row, boolean focused) {
	            Component c = super.getTreeCellRendererComponent(tree, value,
	                    selected, expanded, isLeaf, row, focused);
	            if (isLeaf ) {
	            	if (value instanceof DefaultMutableTreeNode) {
	            		Object userObj = ((DefaultMutableTreeNode) value).getUserObject();
	            		if(userObj instanceof Mleaf) {
		            		if( (int)((Mleaf)userObj).attr == 0) {
		            			setIcon(loadIcon);
		            		}
		            		else if( (int)((Mleaf)userObj).attr == -1) {
		            			setIcon(badIcon);
		            		}
		            		else if( (int)((Mleaf)userObj).attr == 1) {
		            			setIcon(goodIcon);
		            		}
	            		}
	            	}
	            }
	            return c;
	        }
	    });

	    bouton.addActionListener(new ActionListener(){
		      public void actionPerformed(ActionEvent event){			
		    	  S.is_pause=false;
		    	  bouton.setEnabled(false);
		      }
	    });

	    pan.setLayout(new BoxLayout(pan, BoxLayout.PAGE_AXIS));

	    JPanel elementsSups = new JPanel();
	    elementsSups.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10)); 
	    elementsSups.setLayout(new BoxLayout(elementsSups, BoxLayout.LINE_AXIS));
	    elementsSups.add(new JScrollPane(tree));
	    elementsSups.add(Box.createHorizontalStrut(30)); // quick'n'dirty
	    elementsSups.add(scoll);

	    
	    pan.add(elementsSups);
	    pan.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10)); 
	    
	    barre.setPreferredSize(new Dimension(500, 20));
	    barre.setStringPainted(true);
	    
	    JPanel elementsMids = new JPanel();
	    elementsMids.add(barre);
	    pan.add(elementsMids);
	    
	    JPanel elementsBas = new JPanel();
	    elementsBas.add(bouton);
	    pan.add(elementsBas);    

	    pan.add(elementsBas);
	    this.setContentPane(pan);
	    this.setVisible(true);

	}
  
	/*
	 * Called when we start to work on a new entity.
	 * Take two parameteres : racines, that is hierarchical division of this entity, as a string, ex: "Procaryotes;Animaux;Mamif�re;"
	 * 						nom that is the name of the entity ex: "Formica Rufa"
	 * Insert it in the JTree, with the ad-hoc icon (TODO)
	 */
	public void workingOn(String[] gen) {
		java.awt.EventQueue.invokeLater(new Runnable() {
		    @Override
		        public void run() {
		    	String nom = gen[5];
				DefaultTreeModel model = (DefaultTreeModel) tree.getModel();
				DefaultMutableTreeNode tmp_root = (DefaultMutableTreeNode) tree.getModel().getRoot();
				for(String nodeName :  Arrays.copyOfRange(gen, 0, 5)) {			
					for(TreeNode t : Collections.list(tmp_root.children())) {
						if(t.toString().equals(nodeName)) {
							tmp_root = (DefaultMutableTreeNode)t;
							break;
						}
					}
					if(tmp_root.toString().equals(nodeName)) {
						continue;
					}
					//	System.out.println("creating new node @ "+tmp_root);
						DefaultMutableTreeNode newNode = new DefaultMutableTreeNode(nodeName);
						model.insertNodeInto(newNode, tmp_root, 0);
						tmp_root = newNode;
				}
				
				DefaultMutableTreeNode addedTreeNode = new DefaultMutableTreeNode( nom );
				addedTreeNode.setUserObject(new Mleaf(nom, 0));

				model.insertNodeInto(addedTreeNode, tmp_root, 0);
				model.reload(root);

				tree.setModel(model);
				for (int i = 0; i < tree.getRowCount(); i++) {
				    tree.expandRow(i);
				}
				pan.setVisible(false); 
				pan.setVisible(true);
		        }
		    });
	}

	/*
	 * Called when we are done working on a species for good (we created a excel file) or bad (for whatever reason)
	 */
	public void isBad(String racines, String nom) {
		java.awt.EventQueue.invokeLater(new Runnable() {
		    @Override
		        public void run() {
				DefaultMutableTreeNode root = (DefaultMutableTreeNode) tree.getModel().getRoot();
				ArrayList<String> it = new ArrayList<String>();
				it.addAll(Arrays.asList(racines.split(";")));
				it.add(nom);
				for(String nodeName : it ) {
					for(TreeNode t : Collections.list(root.children())) {
						if(t.toString().equals(nodeName)) {
							root = (DefaultMutableTreeNode)t;
							break;
						}
					}
				}
				Mleaf userObj = (Mleaf) root.getUserObject();
				userObj.attr=-1;
				root.setUserObject(userObj);
				pan.setVisible(false); 
				pan.setVisible(true);
		    }
		});	
	}
	
	public void isGood(String[] gen) {

		java.awt.EventQueue.invokeLater(new Runnable() {
		    @Override
		        public void run() {
					DefaultMutableTreeNode root = (DefaultMutableTreeNode) tree.getModel().getRoot();
					for(String nodeName : gen ) {
						for(TreeNode t : Collections.list(root.children())) {
							if(t.toString().equals(nodeName)) {
								root = (DefaultMutableTreeNode)t;
								break;
							}
						}
					}
					Mleaf userObj = (Mleaf) root.getUserObject();
					userObj.attr=1;
					root.setUserObject(userObj);
					pan.setVisible(false); 
					pan.setVisible(true);	

		    	}
			});		
	}
	
	/*
	 *  We write a log on the TextArea.
	 *  Limited to 60 lines, removed 10 by 10
	 */
	public void log(String log) {
		this.textLog.append(log + '\n');
		this.nbLogs++;
		if(nbLogs > 60) {
			try {
				this.textLog.replaceRange(null, 0, this.textLog.getLineEndOffset(9));
				nbLogs-=10; 
			} 
			catch (BadLocationException e) {
				System.out.println("Error at removing first lines of logs...");
				e.printStackTrace();
			}
		}
	}

	public void logProgress(String prog) {
		barre.setString(prog);
	}
	
	
	/*
	 * set the max of the advancement bar
	 * 	in mb, gb, file, whatever u want
	 */
	public void initBarre(int max) {
		this.barre.setMaximum(max);		
	}
	
	/*
	 * add a value to the progression bar
	 */
	
	public void doneBarre(int val) {
		this.barre.setValue(this.barre.getValue()+val);
		this.barre.setVisible(false);
		this.barre.setVisible(true);
	}
	
}






