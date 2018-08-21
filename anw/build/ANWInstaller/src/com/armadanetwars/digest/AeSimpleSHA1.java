package com.armadanetwars.digest;

import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class AeSimpleSHA1 {
	MessageDigest messageDigest;

	static final byte[] HEX_CHAR_TABLE = { (byte) '0', (byte) '1', (byte) '2',
			(byte) '3', (byte) '4', (byte) '5', (byte) '6', (byte) '7',
			(byte) '8', (byte) '9', (byte) 'a', (byte) 'b', (byte) 'c',
			(byte) 'd', (byte) 'e', (byte) 'f' };

	public static String getHexString(byte[] raw)
			throws UnsupportedEncodingException {
		byte[] hex = new byte[2 * raw.length];
		int index = 0;

		for (byte b : raw) {
			int v = b & 0xFF;
			hex[index++] = HEX_CHAR_TABLE[v >>> 4];
			hex[index++] = HEX_CHAR_TABLE[v & 0xF];
		}
		return new String(hex, "ASCII");
	}

	public AeSimpleSHA1() throws NoSuchAlgorithmException {
		this.messageDigest = MessageDigest.getInstance("SHA-1");

	}

	public void update(byte b) {
		this.messageDigest.update(b);
	}

	public void update(byte[] b, int start, int finish) {
		this.messageDigest.update(b, start, finish);
	}

	public String digest() {
		try {
			return getHexString(this.messageDigest.digest());
		} catch (Exception e) {
			return "FAILED HEX CONVERT";
		}
	}

}
