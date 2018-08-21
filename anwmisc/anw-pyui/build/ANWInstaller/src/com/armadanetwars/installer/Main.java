/*
 * Main.java
 *
 * Created on May 25, 2007, 4:45 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package com.armadanetwars.installer;

import com.armadanetwars.installer.ui.ANWInstaller;

/**
 *
 * @author kundertk
 */
public class Main {
    
    /** Creates a new instance of Main */
    public Main() {
        ANWInstaller installer = new ANWInstaller();
        installer.setVisible(true);
    }
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // TODO code application logic here
        Main m = new Main();
    }
    
}
