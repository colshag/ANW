/*
 * LaunchPreferences.java
 *
 * Created on May 28, 2007, 9:26 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package com.armadanetwars;

import com.armadanetwars.LaunchProfile;
import java.awt.Dimension;
import java.io.File;
import java.util.Map;

/**
 *
 * @author kundertk
 */
public class LaunchPreferences {
    
    private Dimension resolution;
    private File pathToPython;
    private Map<String, LaunchProfile> launchProfiles;
    /** Creates a new instance of LaunchPreferences */
    public LaunchPreferences() {
        
    }
    
}
