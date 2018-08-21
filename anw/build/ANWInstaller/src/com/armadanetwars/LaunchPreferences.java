/*
 * LaunchPreferences.java
 *
 * Created on May 28, 2007, 9:26 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package com.armadanetwars;

import java.awt.Dimension;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * 
 * @author kundertk
 */
public class LaunchPreferences {

	private List<LaunchProfile> launchProfiles = new ArrayList<LaunchProfile>();

	/** Creates a new instance of LaunchPreferences */
	public LaunchPreferences(int number) {
		for( int x = 0; x < number; x++ ) {
			launchProfiles.add(new LaunchProfile());
		}
	}

	public void setProfile(int index, LaunchProfile launchProfile) {
		this.launchProfiles.set(index, launchProfile);
	}

	public LaunchProfile getProfile(int index) {
		return this.launchProfiles.get(index);
	}

}
