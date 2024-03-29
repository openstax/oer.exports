
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.io.UnsupportedEncodingException;
import java.util.Scanner;
import java.lang.Thread;
import java.util.Set;
import net.sf.saxon.Transform;

/*
 A wrapper to saxon's transform class to allow for 
 continuious processing of xml strings without blocking
 */

public class SaxonTransformWrapper {


	public static void main(String args[]) throws UnsupportedEncodingException {
		String newArgs[] = new String[args.length - 1];
		String deliminatorPattern = null;
		int index = 0;
                Transform saxTransform = new Transform();
                PrintStream consoleError = System.err;
                PrintStream consoleOutput = System.out;
		InputStream consoleInput = System.in;
                ByteArrayOutputStream transformOutputBuffer = new ByteArrayOutputStream();
                ByteArrayOutputStream transformErrorBuffer = new ByteArrayOutputStream();
                PrintStream transformOutput = new PrintStream(transformOutputBuffer);
                PrintStream transformError = new PrintStream(transformErrorBuffer);
		Scanner sc = new Scanner(consoleInput);
		String xml;
                int start_thread_count = Thread.activeCount();

                // extract the deliminator from the command line args
		for (int i = 0; i < args.length; i++) {
			if (args[i].contains("deliminator")) {
                                try{
				  deliminatorPattern = args[i].split(":")[1];
                                } catch (java.lang.ArrayIndexOutOfBoundsException e){
                                  System.err.println("deliminator value cannot be null");
                                  System.exit(2);
                                }
			} else {
				newArgs[index] = args[i];
				index = index + 1;
			}
		}
		args = newArgs;

		sc.useDelimiter(deliminatorPattern);

                // loop until stdin is closed. 
		while (sc.hasNext()) {
	                transformErrorBuffer.reset();
                        transformOutputBuffer.reset();
	
			xml = sc.next();

                        System.setOut(transformOutput);

                        System.setErr(transformError);	

			System.setIn(new ByteArrayInputStream(xml.getBytes("UTF-8")));

			saxTransform.doTransform(args, "java net.sf.saxon.Transform");



                        System.err.flush();
                        System.setErr(consoleError);
                        System.err.println(transformErrorBuffer);
                        System.err.println("\n"+deliminatorPattern+"\n");
                        System.err.flush();

                        System.out.flush();
                        System.setOut(consoleOutput);
                        System.out.println(transformOutputBuffer);
			System.out.println("\n"+deliminatorPattern+"\n");
                        System.out.flush();

		}

	}

}
