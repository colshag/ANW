/*
 * Progress.java
 *
 * Created on May 25, 2007, 6:45 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package com.armadanetwars.installer;

import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import javax.swing.JLabel;
import javax.swing.JProgressBar;
import javax.swing.SwingUtilities;

/*
 class progress:
    def __init__(self):
        self.message = ""
        self.progress = 0
        self.bytes = 0
        self.error = []
        

    def updateProgress(self, message, progress, bytes):
        self.message = message
        self.progress = progress
        self.bytes = bytes
        print self.message, progress, bytes

    def getProgress(self):
        return self.progress

    def getMessage(self):
        return self.message

    def getByteCount(self):
        return self.bytes

    def addError(self, errorMsg):
        self.error.append(errorMsg)

    def getError(self):
        return self.error

    */

/**
 *
 * @author kundertk
 */
public class Progress {
    private AtomicReference<String> message = new AtomicReference<String>("");
    private AtomicInteger progress = new AtomicInteger(0);
    private AtomicInteger bytes = new AtomicInteger(0);
    private ConcurrentLinkedQueue<String> error = new ConcurrentLinkedQueue<String>();
    private JProgressBar progressBar = null;
    private JLabel bytesLabel = null;
    /** Creates a new instance of Progress */
    public Progress() {
    }

    public void updateProgress(String mess, int prog, int byt) {
        this.message.set(mess);
        this.progress.set(prog);
        this.bytes.set(byt);
        //        System.out.println("Message: " + this.message.get() + " Progress: " + this.progress.get() + " bytes downloaded: " + this.bytes.get());
        if( this.progressBar != null ){
            SwingUtilities.invokeLater(new Runnable() {
                public void run() {
                    progressBar.setString(message.get());
                    progressBar.setValue(progress.get());
                }
            });
        }
        if( this.bytesLabel != null ){
            SwingUtilities.invokeLater(new Runnable() {
                public void run() {
                    bytesLabel.setText(Integer.toString(bytes.get()));
                }
            });
        }
    }
    public Integer getProgress() {
        return this.progress.get();
    }
    public String getMessage() {
        return this.message.get();
    }
    public Integer getByteCount() {
        return this.bytes.get();
    }
    public void addError(String errorMessage) {
        this.error.add(errorMessage);
    }
    public boolean isError() {
        return !this.error.isEmpty();
    }
    public String getNextError() {
        return this.error.poll();
    }
    public void setProgressBar(JProgressBar progress) {
        this.progressBar = progress;
    }
    public void setBytesLabel(JLabel bytes) {
        this.bytesLabel = bytes;
    }
}
