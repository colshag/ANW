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
	private JLabel statusLabel = null;
	long timeStarted = System.currentTimeMillis();

	/** Creates a new instance of Progress */
	public Progress() {
	}

	public void updateProgress(String mess, int prog, int byt) {
		this.message.set(mess);
		this.progress.set(prog);
		this.bytes.set(byt);
		final long elapsed = System.currentTimeMillis() - timeStarted;
		if (prog == 0) {
			prog = 1;
		}
		final long total = ((elapsed) * 100 / prog) / 1000;
		if (this.progressBar != null) {
			SwingUtilities.invokeLater(new Runnable() {
				public void run() {
					// progressBar.setString("Elapsed: " + (elapsed/1000) +
					// "s Remaining: "+ (total-(elapsed/1000)) + "s");
					progressBar.setString("Elapsed: " + (elapsed / 1000) + "s");
					progressBar.setValue(progress.get());

				}
			});
		}

		if (this.bytesLabel != null) {
			SwingUtilities.invokeLater(new Runnable() {
				public void run() {
					int b = bytes.get();
					long elapsed = (System.currentTimeMillis() - timeStarted) / 1000;
					double mb = (double) b / (1024 * 1024);
					double kb = (double) b / 1024;
					String speed = "? KB/sec";
					if (elapsed != 0) {
						speed = String.format("Speed: %,d KB/sec",
								(int) (kb / elapsed));
					}
					if (b >= 1024 * 1024) {
						bytesLabel.setText(String.format("%.2f MB %s", mb,
								speed));
					} else {
						bytesLabel.setText(String.format("%.2f KB %s", kb,
								speed));
					}
				}
			});
		}
		if (this.statusLabel != null) {
			SwingUtilities.invokeLater(new Runnable() {
				public void run() {
					statusLabel.setText(message.get());
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

	public void setStatusLabel(JLabel status) {
		this.statusLabel = status;
	}
}
