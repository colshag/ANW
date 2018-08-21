/*
 * LaunchProfile.java
 *
 * Created on May 28, 2007, 9:31 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */
package com.armadanetwars;

import java.awt.Dimension;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

/**
 * 
 * @author kundertk
 */
public class LaunchProfile {

    private String separator = System.getProperty("file.separator");
    private String game = "ANW1";
    private int empire = 1;
    private String password = "putpasswordhere";
    private String description = "Profile";
    private Dimension resolution = new Dimension(1280, 800);

    @Override
    public String toString() {
        return this.description;
    }
    private String url = "http://www.armadanetwars.com:8000";

    public String getUrl() {
        return url;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getGame() {
        return game;
    }

    public void setGame(String game) {
        this.game = game;
    }

    public int getEmpire() {
        return empire;
    }

    public void setEmpire(int empire) {
        this.empire = empire;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public Dimension getResolution() {
        return resolution;
    }

    public void setResolution(Dimension resolution) {
        this.resolution = resolution;
    }

    public boolean isFullscreen() {
        return fullscreen;
    }

    public void setFullscreen(boolean fullscreen) {
        this.fullscreen = fullscreen;
    }

    public boolean isSound() {
        return sound;
    }

    public void setSound(boolean sound) {
        this.sound = sound;
    }

    public boolean isPsyco() {
        return psyco;
    }

    public void setPsyco(boolean psyco) {
        this.psyco = psyco;
    }
    private boolean fullscreen = false;
    private boolean sound = true;
    private boolean psyco = false;

    public LaunchProfile(String url, String game, int empire, String password,
            String description, Dimension resolution, boolean fullscreen,
            boolean sound, boolean psyco) {
        this.url = url;
        this.game = game;
        this.empire = empire;
        this.password = password;
        this.description = description;
        this.resolution = resolution;
        this.fullscreen = fullscreen;
        this.sound = sound;
        this.psyco = psyco;
    }

    public LaunchProfile() {
    }

    public void writeLaunchInfo(String installPath) throws IOException {
        String basePath = installPath + separator + "anw" + separator + "Client" + separator;
        String connectPath = basePath + "connect.ini";
        String resolutionPath = basePath + "data" + separator + "config.prc";
        BufferedWriter connectWriter = new BufferedWriter(new FileWriter(connectPath));
        BufferedWriter resolutionWriter = new BufferedWriter(new FileWriter(resolutionPath));

        connectWriter.write(this.getUrl() + "\n");
        connectWriter.write(this.getGame() + "\n");
        connectWriter.write("" + this.getEmpire() + "\n");
        connectWriter.write(this.getPassword() + "\n");
        connectWriter.write(this.getDescription() + "\n");
        connectWriter.flush();
        connectWriter.close();

        resolutionWriter.write("fullscreen " + (this.isFullscreen() == true ? "1" : "0") + "\n");
        resolutionWriter.write("sound " + (this.isSound() == true ? "1" : "0") + "\n");
        resolutionWriter.write("psyco " + (this.isPsyco() == true ? "1" : "0") + "\n");
        resolutionWriter.write("win-size " + this.getResolution().width + " " + this.getResolution().height + "\n");
        resolutionWriter.write("win-origin      100 100\n");
        resolutionWriter.write("window-title Armada Net Wars\n");
        resolutionWriter.write("show-frame-rate-meter f\n");
        if( System.getProperty("os.name").startsWith("Windows") || System.getProperty("os.name").startsWith("Mac")) {
            resolutionWriter.write("audio-library-name p3fmod_audio\n");
        } else {
            resolutionWriter.write("audio-library-name p3openal_audio\n");
    	}
        resolutionWriter.write("load-display pandagl\n");
        resolutionWriter.write("aux-display pandadx9\n");
        resolutionWriter.write("aux-display pandadx8\n");
        resolutionWriter.write("aux-display tinydisplay\n");
        resolutionWriter.flush();
        resolutionWriter.close();

    }
}
