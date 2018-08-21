/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package com.armadanetwars.download;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

import com.armadanetwars.digest.AeSimpleSHA1;
import com.armadanetwars.installer.Progress;
import java.net.URLConnection;

/**
 * 
 * @author kundertk
 */
public class Downloader {
	private String webroot;
	private Progress progress;
	private String installPath;
	AtomicBoolean canceled = new AtomicBoolean(false);

	public Downloader(Progress prog, String webroot, String installpath) {
		this.webroot = webroot;
		this.progress = prog;
		this.installPath = installpath;
	}

	InputStream getURL(String url) throws MalformedURLException, IOException {
		URL u = new URL(url);
		// System.out.println("Getting url: " + url);
		URLConnection urlc = u.openConnection();
		// urlc.addRequestProperty(url, url)
		InputStream stream = urlc.getInputStream();
		return stream;
	}

	/**
	 * @param hash
	 * @param filename
	 * @return false if hash doesn't match. true otherwise
	 * @throws NoSuchAlgorithmException
	 */
	boolean checkHash(String hash, String filename)
			throws NoSuchAlgorithmException {
		FileInputStream fis = null;
		try {
			try {
				fis = new FileInputStream(filename);
			} catch (FileNotFoundException e) {
				// file will get downloaded now
				return false;
			}
			int characters;
            AeSimpleSHA1 sha1 = new AeSimpleSHA1();
            // 8k buffer
            int buffersize = 1024*8;
			byte[] bytes = new byte[buffersize];
			try {
				while ((characters = fis.read(bytes, 0, buffersize)) != -1) {
					sha1.update(bytes, 0, characters);
				}
			} catch (IOException e) {
				e.printStackTrace();
				return false;
			}
			// System.out.println(filename);
			// System.out.println("Hash: " + hash);

			String calculatedHash = sha1.digest();
			// System.out.println("Calc: " + calculatedHash );
			if (hash.equals(calculatedHash)) {
				return true;
			} else {
				return false;
			}
		} finally {
			if (fis != null) {
				try {
					fis.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}

	int performUpdateAction(String updateLine) throws NoSuchAlgorithmException {
		String[] array = updateLine.split(",");
		if (array.length == 2 && array[0].equals("d")) {
			// directory
			String path = this.installPath + "/" + array[1];
			File d = new File(path);
			if (d.mkdirs() == false) {
				this.progress.addError("Could not create directory path: "
						+ path);
			}
			return 0;
		} else if (array.length == 3 && array[0].equals("f")) {
			// file
			String sha1 = array[2];
			String downloadPath = array[1];

			String filename = this.installPath + "/" + downloadPath;
			downloadPath = this.webroot + "/" + downloadPath;


			if (checkHash(sha1, filename) == false) {
				// download
				// System.out.println("Download");
				FileOutputStream fos;
				InputStream is;
				try {
					is = getURL(downloadPath);
					fos = new FileOutputStream(filename);
				} catch (FileNotFoundException e1) {
					e1.printStackTrace();
					return -1;
				} catch (MalformedURLException e) {
					e.printStackTrace();
					return -1;
				} catch (IOException e) {
					e.printStackTrace();
					return -1;
				}
				int length = 0;
				// byte b;
				try {
					AeSimpleSHA1 sha1confirm = new AeSimpleSHA1();
					byte[] b = new byte[1024];
					int read = 0;
					while ((read = is.read(b)) != -1) {
						fos.write(b, 0, read);
						sha1confirm.update(b, 0, read);
						length += read;
					}
					fos.flush();
					fos.close();
					is.close();
					String digest = sha1confirm.digest();
					if (digest.equals(sha1) == false) {
						System.out.println(filename);
						System.out.println("Downloaded data [" + digest
								+ "] doesn't match expected [" + sha1 + "]");
					}
				} catch (IOException e) {
					e.printStackTrace();
					return -1;
				}
				return length;
			} else {
				// System.out.println("Don't downlaod");
				return 0;
			}
		}
		return -1;
	}

	public void update() {
		System.out.println("Downloader.update");
		try {
			BufferedReader reader = new BufferedReader(new InputStreamReader(
					getURL(webroot + "/listing.txt")));
			int bytes = 0;
			StringBuilder sb = new StringBuilder();
			// sb.
			List<String> lines = new ArrayList<String>();
			for (String l = ""; (l = reader.readLine()) != null;) {
				lines.add(l);
			}
			for (int x = 0; x < lines.size() && canceled.get() == false; ++x) {
				int curBytes = 0;
				// show the current file being downloaded
				this.progress.updateProgress(lines.get(x).split(",")[1],
						100 * x / lines.size(), bytes);
				if ((curBytes = this.performUpdateAction(lines.get(x))) == -1) {
					return;
				} else {
					bytes += curBytes;
					this.progress.updateProgress(lines.get(x).split(",")[1],
							100 * x / lines.size(), bytes);
				}
			}
			this.progress.updateProgress("done",
					100, bytes);
			if (this.canceled.get()) {
				this.progress.updateProgress("Cancelled", 0, bytes);
			} else {
				this.progress.updateProgress("Complete", 100, bytes);
			}
		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NoSuchAlgorithmException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public void cancel() {
		// TODO Auto-generated method stub
		this.canceled.set(true);
	}
}
