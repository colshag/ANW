/*
 * Launcher.java
 *
 * Created on May 28, 2007, 8:53 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package com.armadanetwars.launcher;

import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.LinkedList;
import java.util.List;
import java.util.Vector;

/**
 *
 * @author kundertk
 */
public class Launcher {
    
    private List<String> arguments;
    private List<String> environment;
    private String workingDirectory;
    
    /** Creates a new instance of Launcher */
    public Launcher(List<String> arguments, List<String> environment, String workingDirectory) {
        this.arguments = arguments;
        this.environment = environment;
        this.workingDirectory = workingDirectory;
    }
    
    public int launch() throws IOException, InterruptedException {
        Runtime runtime = Runtime.getRuntime();
        
        String[] args = null;
        if( this.arguments != null ) {
            args = new String[this.arguments.size()];
            int x = 0;
            for( String arg : this.arguments) {
                args[x] = arg;
                x++;
            }
        }
        
        String[] envs = null;
        if( this.environment != null ) {
            envs = new String[this.environment.size()];
            int x = 0;
            for( String env : this.environment ) {
                envs[x] = env;
                x++;
            }
        }
        System.out.println("Working directory: " + workingDirectory);
        System.out.println("Environment: " + environment);
        System.out.println("Command: " + arguments);
        Process p = runtime.exec(args, envs, new File(workingDirectory));
        return p.waitFor();
    }
    
    public static void main(String[] args) {
        List<String> list = new LinkedList<String>();
        list.add("touch");
        list.add("randomFile");
        Launcher launcher = new Launcher(list, new LinkedList<String>(), "/tmp");
        try {
            System.out.println("Results of execution: " + launcher.launch());
        } catch (IOException ex) {
            ex.printStackTrace();
        } catch (InterruptedException ex) {
            ex.printStackTrace();
        }
    }
}
