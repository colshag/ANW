/*
 * Launcher.java
 *
 * Created on May 28, 2007, 8:53 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package com.armadanetwars.launcher;

import java.awt.Frame;
import java.io.BufferedInputStream;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

import javax.swing.SwingUtilities;
import javax.swing.SwingWorker;

import com.armadanetwars.installer.ui.OutputDialog;

/**
 *
 * @author kundertk
 */
public class Launcher {
    
    private List<String> arguments;
    private Map<String, String> environment;
    private String workingDirectory;
    private StringBuilder stringBuilder = new StringBuilder();
    private Thread thread;
    private OutputDialog outputDialog;
    private AtomicBoolean launchComplete = new AtomicBoolean(false);
    private AtomicInteger returnCode = new AtomicInteger(0);
    
    /** Creates a new instance of Launcher */
    public Launcher(List<String> arguments, Map<String, String> environment, String workingDirectory) {
        this.arguments = arguments;
        this.environment = environment;
        this.workingDirectory = workingDirectory;
    }
    
    public int launch(Frame parent) throws IOException, InterruptedException {
        
        final ProcessBuilder pb = new ProcessBuilder(arguments);
        pb.directory(new File(workingDirectory));
        if( this.environment != null ) {
        	Map<String, String> env = pb.environment();
        	env.clear();
            for( String var : this.environment.keySet() ) {
            	env.put(var, this.environment.get(var));
            }
        }
        System.out.println("Working directory: " + workingDirectory);
        System.out.println("Environment: " + environment);
        System.out.println("Command: " + arguments);
        //Process p = runtime.exec(args, envs, new File(workingDirectory));
        pb.redirectErrorStream(true);
        AtomicInteger retVal = new AtomicInteger(-1);
        if( parent != null ) {
        	this.outputDialog = new OutputDialog(parent, false, "");
	    	this.outputDialog.setVisible(true);

        	this.thread = new Thread( new Runnable() {
        		


				@Override
				public void run() {
					System.out.println("Do in background");
			        Process p = null;
					try {
						p = pb.start();
					} catch (IOException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
						return;
					}
			    	final BufferedInputStream bis = new BufferedInputStream(p.getInputStream());
					byte buffer[] = new byte[1024];
			        int read = 0;
			        try {
						while( (read = bis.read(buffer, 0, 1024)) >= 0 ) {
							final String result = new String(buffer, 0, read);
							SwingUtilities.invokeAndWait(new Runnable() {
								@Override
								public void run() {
									outputDialog.updateDialog(result);
								}
							});
						}
						returnCode.set(p.waitFor());
						launchComplete.set(true);
					} catch (IOException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					} catch (InvocationTargetException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
					
				}
        	});
        	thread.start();
        }
        System.out.println("Swingworker should be running");
        return 0;
    }
    
    public String getOutput() {
    	return this.stringBuilder.toString();
    }
    
    public boolean isLaunchComplete() {
    	return this.launchComplete.get();
    }
    
    public int getReturnCode() {
    	return this.returnCode.get();
    }
    
    public static void main(String[] args) {
        List<String> list = new LinkedList<String>();
        list.add("touch");
        list.add("randomFile");
        Launcher launcher = new Launcher(list, new HashMap<String, String>(), "/tmp");
        try {
            System.out.println("Results of execution: " + launcher.launch(null));
        } catch (IOException ex) {
            ex.printStackTrace();
        } catch (InterruptedException ex) {
            ex.printStackTrace();
        }
    }
}
