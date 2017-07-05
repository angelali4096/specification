#!/usr/bin/env python

import sys
import os
import string
import argparse

# boldWordsC and boldWordsF are a set of the key words that will be
# bolded in the man page
boldWordsC = {"void", "int", "const", "size_t", "short", "ptrdiff_t", 
			"long", "TYPE", "shmem_global_exit(int"}
boldWordsF = {"INTEGER", "CALL", "POINTER", "LOGICAL", "INTEGER*4",
				"INTEGER*8", "REAL*4", "REAL*8", "CHARACTER"}


def writePageHeader(functionName):
	# Write the page header for the man page. Takes in the form of:
	# .TH [name of program] [section number] [center footer] [left footer] 
	# 	  [center header]
	titleHeader = ".TH " + functionName.upper() + " 3 " \
					 + "" + "" \
					 + "\"Open Source Software Solutions, Inc.\"" + "" \
					 + "\"OpenSHEMEM Library Documentation\"" + "\n"
	return titleHeader

##########################################################################
##							MACRO REPLACEMENTS 							##
##########################################################################

def funcReplacements(tex):
	# Convert every FUNC macro with the bolded argument string 
	#(.B <argument>).
	# -- Special consideration to any periods after the macro, since a 
	# period at the beginning of a line denotes a comment and the 
	# entire line will not appear.
	# (.BR <argument> .)

	# .B at the start of a line will bold all text until the next "\n"
	# .BR will alternate between bold and regular font. For example:
	# 
	# .BR "A" "B" "C"
	#
	# will have "A" and "C" as bolded and "B" will be regular.
	macro = "\FUNC{"
	while (tex.find(macro) != -1):
		beg = tex.find(macro)
		brace = tex.find("}", beg)
		if(tex[brace + 1] == "."):
			tex = tex[:beg] + "\n.BR \"" + tex[beg+len(macro):brace] \
								+  "\" .\n" + tex[brace+2:]
		else:
			if(tex[brace + 1] == " "):
				tex = tex[:beg] + "\n.B " + tex[beg+len(macro):brace] \
								+ "\n" + tex[brace+2:]
			else:
				tex = tex[:beg] + "\n.B " + tex[beg+len(macro):brace] \
								+ "\n" + tex[brace+1:]
	return tex

def varReplacements(tex, keyString):
	# Convert every VAR/VARTH macro with the bolded argument string 
	#(.I <argument>).
	# -- Special consideration to any periods after the macro, since a 
	# period at the beginning of a line denotes a comment and the 
	# entire line will not appear.
	# (.IR <argument> .)
	# -- Special consideration to any argument of "VARTH", which will 
	# require appending "th" to the argument string.

	# .I at the start of a line will underline/italicize all text until
	# the next "\n"
	# .IR will alternate between bold and regular font. For example:
	# 
	# .IR "A" "B" "C"
	#
	# will have "A" and "C" as italicized and "B" will be regular.
	while (tex.find(keyString) != -1):
		beg = tex.find(keyString)
		sbrace = tex.find("{", beg)
		ebrace = tex.find("}", sbrace)
		innerText = tex[sbrace+1:ebrace]
		if keyString == "\VARTH{":
			innerText += "th"
		if (tex[ebrace + 1] != "."):
			tex = tex[:beg] + "\n.I " + innerText \
					    	+ "\n" + tex[ebrace+1:]
		else:
			tex = tex[:beg] + "\n.IR \"" + innerText \
					    	+ "\" .\n" + tex[ebrace+1:]
	return tex

def variableReplacements(tex):
	tex = varReplacements(tex, "\VAR{")
	tex = varReplacements(tex, "\VARTH{")
	return tex

def mBoxReplacements(tex):
	# Replace the Latex command "|mbox{<argument>}|" with just 
	# argument
	while (tex.find("|\mbox") != -1):
		beg = tex.find("|\mbox")
		sbrace = tex.find("{", beg)
		ebrace = tex.find("}", sbrace)
		ebar = tex.find("|", sbrace)
		tex = tex[:beg] + tex[sbrace+1:ebrace] \
					    + tex[ebar+1:]
	return tex

def boldReplacements(tex):
	# SPECIFIC TO shmem_reductions:
	# Replace the Latex command "\textbf{<NAME>} ...\newline...\bigskip" 
	while (tex.find("\\textbf{") != -1):
		beg = tex.find("\\textbf{")
		sbrace = tex.find("{", beg)
		ebrace = tex.find("}", sbrace)
		fnewline = tex.find("\\newline", ebrace)
		snewline = tex.find("\\newline", fnewline + 1)
		clean = tex[fnewline + len("\\newline"):snewline]
		clean = macroReplacements(clean)
		tex = tex[:beg] + "\n.SH " + tex[sbrace+1:ebrace] \
				    	+ "\n" + clean \
				    	+ tex[snewline + len("\\newline"):]
	tex = tex.replace("\\bigskip", "")
	return tex

def italReplacements(tex):
	# Replace the Latex command "\textit{<argument>}" with just 
	# argument
	while (tex.find("\\textit{") != -1):
		beg = tex.find("\\textit{")
		sbrace = tex.find("{", beg)
		ebrace = tex.find("}", sbrace)
		tex = tex[:beg] + tex[sbrace+1:ebrace] \
				    	+ tex[ebrace+1:]
	return tex

def oprReplacements(tex):
	# Convert every OPR macro with the bolded argument string 
	#(.I <argument>).
	# -- Special consideration to any periods after the macro, since a 
	# period at the beginning of a line denotes a comment and the 
	# entire line will not appear.
	# (.IR <argument> .)
	# -- Special consideration to any argument of "VARTH", which will 
	# require appending "th" to the argument string.

	# .I at the start of a line will underline/italicize all text until
	# the next "\n"
	# .IR will alternate between bold and regular font. For example:
	# 
	# .IR "A" "B" "C"
	#
	# will have "A" and "C" as italicized and "B" will be regular.
	while (tex.find("\\OPR") != -1):
		beg = tex.find("\\OPR")
		sbrace = tex.find("{", beg)
		ebrace = tex.find("}", beg)
		if (tex[ebrace + 1] != "."):
			tex = tex[:beg] + "\n.I " + tex[sbrace+1:ebrace] \
					    	+ "\n" + tex[ebrace+1:]
		else:
			tex = tex[:beg] + "\n.IR \"" + tex[sbrace+1:ebrace] \
					    	+ "\" .\n" + tex[ebrace+1:]
	return tex

def constReplacements(tex):
	# Replace the Latex command "\CONST{<argument>}" with just 
	# argument
	while (tex.find("\\CONST") != -1):
		beg = tex.find("\\CONST")
		sBrace = tex.find("{", beg)
		eBrace = tex.find("}", sBrace)
		tex = tex[:beg] + tex[sBrace+1:eBrace] + tex[eBrace+1:]
	return tex

def generalReplacements(tex):
	# Replace the common Latex macros that take in no arguments
	tex = tex.replace("\openshmem{}", "OpenSHMEM")
	tex = tex.replace("\openshmem", "OpenSHMEM")
	tex = tex.replace("\\acp{PE}", "PEs")
	tex = tex.replace("\\ac{PE}", "PE")
	tex = tex.replace("\\ac{MPI}", "MPI")
	tex = tex.replace("\\acp{AMO}", "AMOs")
	tex = tex.replace("\\ac{AMO}", "AMO")
	tex = tex.replace("\\ac{API}", "API")
	tex = tex.replace("\\acp{RMA}", "RMAs")
	tex = tex.replace("\\ac{RMA}", "RMA")
	tex = tex.replace("\\CorCpp{}", " C/C++")
	tex = tex.replace("\\CorCpp", " C/C++")
	tex = tex.replace("\\Fortran{}", "Fortran")
	tex = tex.replace("\\Fortran", "Fortran")
	tex = tex.replace("\\Cstd", "C")
	tex = tex.replace("\\PUT{}", "PUT")
	tex = tex.replace("\\GET{}", "GET")
	tex = tex.replace("\\SIZE{}", "SIZE")
	tex = tex.replace("\\activeset.", "\n.IR \"Active set\" .\n")
	tex = tex.replace("\\activeset{}", "\\activeset")
	tex = tex.replace("\\activeset", "\n.I \"Active set\"\n")
	tex = tex.replace("\\activeset ", "\n.I \"Active set\"\n")
	tex = tex.replace("\\dest.", "\n.IR \"dest\" .\n")
	tex = tex.replace("\\source.", "\n.IR \"source\" .\n")
	tex = tex.replace("\\dest{}", "\n.I \"dest\"\n")
	tex = tex.replace("\\source{}", "\n.I \"source\"\n")
	tex = tex.replace("\\TYPE{}", "TYPE")
	tex = tex.replace("\\TYPENAME{}", "TYPENAME")
	return tex

##########################################################################
##							SECTION REPLACEMENTS 						##
##########################################################################

def descrReplacements(tex):
	# 
	sArg = tex.find("\\apidescription{")
	eArg = findMatchingBrace(tex, tex.find("{", sArg))
	clean = cleanText(tex[sArg:eArg])
	clean = macroReplacements(clean)
	tex = tex[:sArg] + "./ sectionStart\n" + "\n.SS API Description\n" + \
			clean + "\n./ sectionEnd\n" + tex[eArg+1:]
	tex = tex.replace("\\apidescription{", "")
	return tex

def retReplacements(tex):
	sArg = tex.find("\\apireturnvalues{")
	eArg = findMatchingBrace(tex, tex.find("{", sArg))
	clean = cleanText(tex[sArg:eArg])
	clean = macroReplacements(clean)
	tex = tex[:sArg] + "./ sectionStart\n" + "\n.SS Return Values\n" + \
			clean + "\n./ sectionEnd\n" + tex[eArg + 1:]
	tex = tex.replace("\\apireturnvalues{", "")
	return tex

def notesReplacements(tex):
	sArg = tex.find("\\apinotes{")
	eArg = findMatchingBrace(tex, tex.find("{", sArg))
	clean = cleanText(tex[sArg:eArg])
	clean = macroReplacements(clean)
	tex = tex[:sArg] + "./ sectionStart\n" + "\n.SS API Notes\n" + \
			clean + "\n./ sectionEnd\n" + tex[eArg + 1:]
	tex = tex.replace("\\apinotes{", "")
	return tex

def impnotesReplacements(tex):
	sArg = tex.find("\\apiimpnotes{")
	eArg = findMatchingBrace(tex, tex.find("{", sArg))
	clean = cleanText(tex[sArg:eArg])
	clean = macroReplacements(clean)
	tex = tex[:sArg] + "./ sectionStart\n" + ".SS Note to implementors\n" + \
				clean + "\n./ sectionEnd\n" + tex[eArg + 1:]
	tex = tex.replace("\\apiimpnotes{", "")
	return tex

def sumReplacements(tex, functionName):
	sArg = tex.find("\\apisummary{")
	eArg = findMatchingBrace(tex, tex.find("{", sArg))
	clean = cleanText(tex[sArg:eArg])
	clean = clean.replace("\n", " ")
	clean = macroReplacements(clean)
	tex = tex[:sArg] + "./ sectionStart\n" + ".SH NAME\n" + functionName + " \- " \
			+ clean + "\n./ sectionEnd\n" + tex[eArg+1:]
	tex = tex.replace("\\apisummary{", "")
	return tex

##########################################################################
##							TABLE REPLACEMENTS	 						##
##########################################################################

def descTReplacements(tex):
	arg = tex.find("\\apidesctable{")
	fsArg = tex.find("{", arg)
	feArg = findMatchingBrace(tex, fsArg)
	ssArg = tex.find("{", feArg)
	seArg = findMatchingBrace(tex, ssArg)
	tsArg = tex.find("{", seArg)
	teArg = findMatchingBrace(tex, tsArg)
	text = tex[arg:teArg+1]
	clean = cleanText(text)
	clean = clean.replace("\n", " ")
	clean = macroReplacements(clean)
	beg = tex.find("\\apidesctable{")
	fsBrace = clean.find("{")
	feBrace = clean.find("}", fsBrace)
	ssBrace = clean.find("{", feBrace)
	seBrace = clean.find("}", ssBrace)
	tsBrace = clean.find("{", seBrace)
	teBrace = clean.find("}", tsBrace)
	tex = tex[:arg] + "\n./ sectionStart\n" + clean[fsBrace+1:feBrace] + \
			"\n.TP 20\n" + clean[ssBrace+1:seBrace] + "\n" + \
			clean[tsBrace+1:teBrace] + "\n./ sectionEnd\n" + tex[teArg+1:]
	return tex

def tablReplacements(tex):
	while(tex.find("\\apitablerow") != -1):
		arg = tex.find("\\apitablerow")
		fsArg = tex.find("{", arg)
		feArg = findMatchingBrace(tex, fsArg)
		ssArg = tex.find("{", feArg)
		seArg = findMatchingBrace(tex, ssArg)
		text = tex[arg:seArg+1]

		clean = cleanText(text)
		clean = clean.replace("\n", " ")
		clean = macroReplacements(clean)
		beg = clean.find("\\apitablerow")
		fsBrace = clean.find("{", beg)
		feBrace = clean.find("}", fsBrace)
		ssBrace = clean.find("{", feBrace)
		seBrace = clean.find("}", ssBrace)
		if (clean[fsBrace+1:feBrace] != ""):
			tex = tex[:arg] + "\n./ sectionStart\n.TP 20\n" + clean[fsBrace+1:feBrace] + \
				"\n" + clean[ssBrace+1:seBrace] + "\n./ sectionEnd\n" + tex[seArg+1:]
		else:
			tex = tex[:arg] + "\n" + "\n./ sectionStart" +\
				"\n" + clean[ssBrace+1:seBrace] + "\n./ sectionEnd\n" + tex[seArg+1:]
	return tex

def parseTable(tableTex):
	startIdx = tableTex.find("\\hline")
	endIdx = tableTex.find("\\end{tabular}")
	table = cleanText(tableTex[startIdx + len("\\hline"):endIdx])
	# print(table)
	text = ""
	count = 0
	while(table.find("\\hline") >= 0):
		line = table[:table.find("\\hline")]
		firstCol = line[:line.find("&")]
		secondCol = line[line.find("&")+1:line.find("\\\\")].strip()
		if (count == 0):
			text += ".TP 20\n" + ".B " + firstCol + "\n.B " + secondCol + "\n"
		else:
			text += ".TP\n" + firstCol + "\n" + secondCol + "\n"
		table = table[table.find("\\hline") + len("\\hline"):]
		count += 1
	return text


def table(tableID, directory):
	if tableID == 1:
		tableTex = open(directory + "/stdrmatypes.tex", "r").read()
	elif tableID == 2: 
		tableTex = open(directory + "/stdamotypes.tex", "r").read()
	elif tableID == 3:
		tableTex = open(directory + "/extamotypes.tex", "r").read()
	elif tableID == 4:
		tableTex = open(directory + "/bitamotypes.tex", "r").read()
	else:
		tableTex = open(directory + "/p2psynctypes.tex", "r").read()
	captionIdx = tableTex.find("\\caption{")
	startBrace = captionIdx + len("\\caption{")
	endBrace = findMatchingBrace(tableTex, startBrace)

	caption = generalReplacements(tableTex[startBrace:endBrace])
	text = ".SS Table " + str(tableID) + ":\n" + caption + "\n" + \
			parseTable(tableTex)
	return text

##########################################################################
##							CODE REPLACEMENTS	 						##
##########################################################################

def synCReplacements(tex, keyString):
	while (tex.find("\\begin{" + keyString + "}") != -1):
		sArg = tex.find("\\begin{" + keyString + "}")
		eArg = tex.find("\\end{" + keyString + "}")
		text = tex[sArg + len("\\begin{" + keyString + "}"):eArg]
		coll = "";
		while(text.find(";") != -1):
			s = text.find("\n") + len("\n")
			e = text.find(";", s) + len(";")
			line = text[s:e]
			wordList = line.split()
			for i in xrange(len(wordList)):
				if(i < 2):
					wordList[i] = "\n.B " + wordList[i]
				else:
					if (wordList[i] in boldWordsC):
						wordList[i] = "\n.B " + wordList[i]
					else:
						if (wordList[i].find(")") != -1):
							wordList[i] = "\n.I " + wordList[i][: wordList[i].find(")")] \
											+ "\n.B )$\n"
						elif (wordList[i].find(",") != -1):
							wordList[i] = "\n.IB \"" + wordList[i][: wordList[i].find(",")] \
											+ "\" ,"
						else:
							wordList[i] = "\n.I " + wordList[i]
			line = "".join(wordList)
			coll = coll + "__@@__" + line
			text = text[e:]
		coll = coll.replace("$", ";")

		if (keyString == "C11synopsis"):
			header = ".SS C11:\n"
		elif (keyString == "Csynopsis"):
			header = ".SS C/C++:\n"
		else:
			header = ""

		tex = tex[:sArg] + "\n./ sectionStart\n" + header + coll  + \
				 "\n./ sectionEnd\n" + tex[eArg + len("\\end{" + keyString + "}"):]
	return tex

def synFReplacements(tex):
	while (tex.find("\\begin{Fsynopsis}") != -1):
		sArg = tex.find("\\begin{Fsynopsis}")
		eArg = tex.find("\\end{Fsynopsis}")
		text = tex[sArg + len("\\begin{Fsynopsis}\n"):eArg]
		text = "\n" + text.replace("\n", ";\n")
		last = 0;
		while(text.find(";") != -1):
			s = text.find("\n", last) + len("\n")
			e = text.find(";", s) + len(";")
			line = text[s:e]
			line = line.replace(";", "")
			wordList = line.split()
			if(wordList[0] in boldWordsF):
				line = ".BR \"" + wordList[0] + " \" \"" + \
						" ".join(wordList[1:]) + "\""
			text = text[:s] + line + text[e:]
			last = s
		tex = tex[:sArg ] + "\n./ sectionStart\n" + ".SS Fortran:\n" + "\n.nf\n" + text + "\n.fi\n" +\
				 "\n./ sectionEnd\n" + tex[eArg + len("\\end{Fsynopsis}"):]
	return tex

def codeReplace(tex):
	tex = synCReplacements(tex, "C11synopsis")
	tex = synCReplacements(tex, "Csynopsis")
	tex = synCReplacements(tex, "CsynopsisCol")
	tex = synFReplacements(tex)
	return tex

##########################################################################
##							HELPER FUNCTIONS	 						##
##########################################################################

def cleanText(text):
	text = text.replace("\t", "")
	
	while(text.find("  ") != -1):
		text = text.replace("  ", " ")
	text = text.replace("\n ", "\n")
	text = text.split("\n\n")
	# text = text.replace("\n\n", "__@@__")
	return text

def macroReplacements(clean):
	clean = variableReplacements(clean)
	clean = generalReplacements(clean)
	clean = constReplacements(clean)
	clean = oprReplacements(clean)
	clean = funcReplacements(clean)
	clean = italReplacements(clean)
	clean = clean.replace("\n ", "\n")
	clean = clean.replace("\n\n.BR ", "\n.BR ")
	clean = clean.replace("\n\n.B ", "\n.B ")
	clean = clean.replace("\n\n.I ", "\n.I ")
	clean = clean.replace("\n\n.IR ", "\n.IR ")
	return clean

def generateRoutineList(TOC):
	count = 0;
	routineList = []
	while(TOC.find("\\subsubsection{\\textbf", count) > 0):
		currIdx = TOC.find("\\subsubsection{\\textbf", count)
		startBrace = TOC.find("\\textbf", currIdx) + len("\\textbf")
		endBrace = TOC.find("}", startBrace)
		func = TOC[startBrace+1:endBrace]
		if (func.find(",") != -1):
			func = func[:func.find(",")]
		name = func.lower().replace("\\", "")
		routineList.append(name)
		count = currIdx + len("\\subsubsection{\\textbf")
	return routineList

def findMatchingBrace(tex, ind):
	count = 1
	ptr = ind
	while(count != 0):
		ptr = ptr + 1
		if(tex[ptr] == "{"):
			count = count + 1
		if(tex[ptr] == "}"):
			count = count - 1
	return ptr

def convertFile(functionName, directory, gen_dir):
	filename = directory + '/' + functionName + ".tex"
	texFile = open(filename, "r")
	if not os.path.exists(gen_dir):
	    os.makedirs(gen_dir)
	manFile = open(gen_dir + '/' + functionName + ".3", "w")
	titleHeader = writePageHeader(functionName)
	manFile.write(titleHeader)

	tex = texFile.read()
	tex = tex.replace("\\begin{DeprecateBlock}", "")
	tex = tex.replace("\\end{DeprecateBlock}", "")
	tex = tex.replace("\\begin{apidefinition}\n", 
				"./ sectionStart\n.SH   SYNOPSIS\n./ sectionEnd")
	tex = sumReplacements(tex, functionName)
	tex = mBoxReplacements(tex)
	tex = argReplacements(tex)
	tex = descrReplacements(tex)
	tex = notesReplacements(tex)
	tex = retReplacements(tex)
	tex = boldReplacements(tex)
	tex = codeReplace(tex)
	if (tex.find("\\apiimpnotes{") != -1):
		tex = impnotesReplacements(tex)
	while(tex.find("\\apidesctable{") != -1):
		tex = descTReplacements(tex)
	tex = tablReplacements(tex)
	tex = refMEMReplacements(tex)
	if (tex.find("\\begin{apiexamples}") != -1):
		tex = exampleReplacements(tex, directory)
	(tex, tables) = refTextReplacements(tex)
	if (tables[0]):
		tex = tex + table(1, directory)
	if (tables[1]):
		tex = tex + table(2, directory)
	if (tables[2]):
		tex = tex + table(3, directory)
	if (tables[3]):
		tex = tex + table(4, directory)
	if (tables[4]):
		tex = tex + table(5, directory)
	tex = tex.replace("\\begin{apidefinition}", "")
	tex = tex.replace("\\end{apidefinition}", "")
	text = tex[:tex.find(".SS Examples")]
	while(text.find("\n\n") != -1):
		text = text.replace("\n\n", "\n")
	while(text.find("\n ") != -1):
		text = text.replace("\n ", "\n")
	text = text.replace("\\\\", "\n")
	text = text.replace("$", "")
	tex = text + tex[tex.find(".SS Examples"):]
	tex = tex.replace("__@@__", "\n\n")
	tex = tex.replace("\n ", "\n")
	manFile.write(tex.replace("\\n", "\\\\" + "n"))
	print("Finished converting " + functionName + ".tex")
	manFile.close()
	texFile.close()

def main():
	parser = argparse.ArgumentParser(description='Generate OpenSHMEM manpages')
	parser.add_argument('-d', '--directory', type=str, required=False,
                        help='OpenSHMEM specification LaTeX directory path')
	parser.add_argument('-o', '--output-directory', type=str, required=False, default="./man",
                        help='Output directory for generated manpages')
	parser.add_argument('-f', '--filename', type=str, required=False,
                        help='LaTeX file path for an OpenSHMEM routine')
	args = parser.parse_args()

	if (args.directory == None) and (args.filename == None):
		parser.print_usage()
		exit(1)

	if args.directory != None:
		if not os.path.realpath(args.directory):
			print("Error: input directory, " + args.directory + ", does not appear to exist")
			exit(1)
		else:
			print("Dir found")
			TOC = open(args.directory + "../main_spec.tex").read()
			routineList = generateRoutineList(TOC)
			for routine in routineList:
				if routine + ".tex" not in os.listdir(args.directory):
					print("Error: " + routine + ".tex is not in the given directory")
					exit(1)
				else:
					convertFile(routine, args.directory, args.output_directory)
	else:
		if not os.path.isfile(args.filename):
			print("Error: input file, " + args.filename + ", does not appear to exist.")
			exit(1)
		else:
			per = args.filename.find(".tex")
			last = 0;
			# print(args.filename.find("/", last))
			while (args.filename.find("/", last) >= 0):
				last = args.filename.find("/", last) + 1
				# print(last)
			functionName = args.filename[last:per]
			# print(functionName)
			if functionName not in routineList:
				print("WARNING: This function is not in the list of parsable routines. May result in undefined behavior.")
			convertFile(functionName, args.filename[:last], args.output_directory)

if __name__== "__main__":
    main()