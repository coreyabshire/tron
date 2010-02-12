// Comm.java
// Author: Jeff Cameron (jeff@jpcameron.com)
//
// This code is for dealing with client programs. Starting a client program,
// sending it an ASCII representation of the map, collecting the client's
// decision, enforcing time limits, it's all here.

import java.io.*;

class Comm {
    // The process to be used to host the client program.
    Process process;

    // Input, output, and error streams for the client program.
    InputStream inputStream = null;
    InputStream errorStream = null;
    OutputStream outputStream = null;

    public Comm(String programName) throws Exception {
	try {
	    process = Runtime.getRuntime().exec(programName);
	    inputStream = process.getInputStream();
	    errorStream = process.getErrorStream();
	    outputStream = process.getOutputStream();
	} catch (Exception e) {
	    throw new Exception("Problem while starting client program: " + e);
	}
    }

    public void Destroy() {
	try {
	    inputStream.close();
	    errorStream.close();
	    outputStream.close();
	    process.destroy();	    
	} catch (Exception e) {
	    // Do nothing.
	}
    }

    // Gets a move from a client program.
    public int GetMove(Map map, int maxTimeInSeconds) {
	int decision = -1;
	try {
	    try {
		map.WriteToStream(outputStream);
	    } catch (Exception e) {
		System.err.println(e);
		throw e;
	    }
	    long startTime = System.currentTimeMillis();
	    while (System.currentTimeMillis() - startTime <
		   maxTimeInSeconds * 1000) {
		while (errorStream.available() > 0) {
		    System.out.print((char)errorStream.read());
		}
		if (inputStream.available() > 0) {
		    int c = inputStream.read();
		    if (c >= '1' && c <= '4') {
			decision = c - 48;
			break;
		    }
		}
		Thread.sleep(1);
	    }
	} catch (Exception e) {
	    decision = -1;
	}
	return decision;
    }
}
