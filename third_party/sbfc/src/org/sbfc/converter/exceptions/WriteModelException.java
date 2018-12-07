/*
 * $Id: WriteModelException.java 379 2015-07-07 15:33:22Z niko-rodrigue $
 * $URL: svn+ssh://niko-rodrigue@svn.code.sf.net/p/sbfc/code/trunk/src/org/sbfc/converter/exceptions/WriteModelException.java $
 *
 * ==========================================================================
 * This file is part of The System Biology Format Converter (SBFC).
 * Please visit <http://sbfc.sf.net> to have more information about
 * SBFC. 
 * 
 * Copyright (c) 2010-2015 jointly by the following organizations:
 * 1. EMBL European Bioinformatics Institute (EBML-EBI), Hinxton, UK
 * 2. The Babraham Institute, Cambridge, UK
 * 3. Department of Bioinformatics, BiGCaT, Maastricht University
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation. A copy of the license agreement is provided
 * in the file named "LICENSE.txt" included with this software distribution
 * and also available online as 
 * <http://sbfc.sf.net/mediawiki/index.php/License>.
 * 
 * ==========================================================================
 * 
 */

package org.sbfc.converter.exceptions;

/**
 * Exception thrown in case of an error while writing a model
 * 
 * @author jpettit
 *
 */

public class WriteModelException extends Exception {
	
	private static final long serialVersionUID = 393889077432794418L;

	public WriteModelException () { super (); }	
	public WriteModelException (Throwable cause) { super (cause); }	
	public WriteModelException (String msg) { super (msg); }
	public WriteModelException (String msg, Throwable cause) { super (msg, cause); }
}
