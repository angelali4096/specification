
# For getting the arguments directly from command line
import sys
import os
import string
import datetime


boldWordsC = {"void", "int", "const", "size_t", "short", "ptrdiff_t", "long", "TYPE", "shmem_global_exit(int"}
boldWordsF = {"INTEGER", "CALL", "POINTER", "LOGICAL", "INTEGER*4",
				"INTEGER*8", "REAL*4", "REAL*8", "CHARACTER"}

def writeTH(functionName):
	titleHeader = ".TH " + functionName.upper() + " 3 " \
					 + "" + " " \
					 + "\"Open Source Software Solutions, Inc.\"" + " " \
					 + "\"OpenSHEMEM Library Documentation\"" + "\n"
	return titleHeader

def generalReplacements(tex):
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
	tex = tex.replace("\\activeset ", "\n.I \"Active set\"\n")
	tex = tex.replace("\\dest.", "\n.IR \"dest\" .\n")
	tex = tex.replace("\\source.", "\n.IR \"source\" .\n")
	tex = tex.replace("\\dest{} ", "\n.I \"dest\"\n")
	tex = tex.replace("\\source{}", "\n.I \"source\"\n")
	return tex

def funcReplacements(tex):
	while (tex.find("\FUNC{") != -1):
		beg = tex.find("\FUNC{")
		brace = tex.find("}", beg)
		if(tex[brace + 1] == "."):
			tex = tex[:beg] + "\n.BR \"" + tex[beg+len("\FUNC{"):brace] \
								+  "\" .\n" + tex[brace+2:]
		else:
			if(tex[brace + 1] == " "):
				tex = tex[:beg] + "\n.B " + tex[beg+len("\FUNC{"):brace] \
								+ "\n" + tex[brace+2:]
			else:
				tex = tex[:beg] + "\n.B " + tex[beg+len("\FUNC{"):brace] \
								+ "\n" + tex[brace+1:]
	return tex

def varReplacements(tex):
	while (tex.find("\VAR") != -1):
		beg = tex.find("\VAR")
		sbrace = tex.find("{", beg)
		ebrace = tex.find("}", sbrace)
		if (tex[ebrace + 1] != "."):
			tex = tex[:beg] + "\n.I " + tex[sbrace+1:ebrace] \
					    	+ "\n" + tex[ebrace+1:]
		else:
			tex = tex[:beg] + "\n.IR \"" + tex[sbrace+1:ebrace] \
					    	+ "\" .\n" + tex[ebrace+1:]
	return tex

def mBoxReplacements(tex):
	while (tex.find("|\mbox") != -1):
		beg = tex.find("|\mbox")
		sbrace = tex.find("{", beg)
		ebrace = tex.find("}", sbrace)
		ebar = tex.find("|", sbrace)
		tex = tex[:beg] + tex[sbrace+1:ebrace] \
					    + tex[ebar+1:]
	return tex

def boldReplacements(tex):
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
	while (tex.find("\\textit{") != -1):
		beg = tex.find("\\textit{")
		sbrace = tex.find("{", beg)
		ebrace = tex.find("}", sbrace)
		tex = tex[:beg] + tex[sbrace+1:ebrace] \
				    	+ tex[ebrace+1:]
	return tex

def oprReplacements(tex):
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
	while (tex.find("\\CONST") != -1):
		beg = tex.find("\\CONST")
		sBrace = tex.find("{", beg)
		eBrace = tex.find("}", sBrace)
		tex = tex[:beg] + tex[sBrace+1:eBrace] + tex[eBrace+1:]
	return tex


def argReplacements(tex):
	sArg = tex.find("\\begin{apiarguments}")
	eArg = tex.find("\\end{apiarguments}")
	clean = cleanText(tex[sArg:eArg])
	
	clean = macroReplacements(clean)
	tex = tex[:sArg] + clean + tex[eArg:]
	while(tex.find("\\apiargument") != -1):
		beg = tex.find("\\apiargument")
		fsBrace = tex.find("{", beg)
		feBrace = tex.find("}", fsBrace)
		ssBrace = feBrace + 1
		seBrace = tex.find("}", ssBrace)
		tsBrace = seBrace + 1
		teBrace = tex.find("}", tsBrace)
		if (tex[fsBrace+1:feBrace] == "None."):
			tex = tex[:beg] + ".B None." + tex[tsBrace+1:teBrace] + tex[teBrace+1:]
		else:
			tex = tex[:beg] + "\n.BR \"" + tex[fsBrace+1:feBrace] \
							+ " \" -" + "\n.I " + tex[ssBrace+1:seBrace] \
							+ "\n- " + tex[tsBrace+1:teBrace] + tex[teBrace+1:]
	sArg = tex.find("\\begin{apiarguments}")
	eArg = tex.find("\\end{apiarguments}")
	clean = tex[sArg:eArg]
	clean = clean.replace("\n ", "\n")
	while(clean.find("\n\n") != -1):
		clean = clean.replace("\n\n", "\n")
	clean = clean.replace(".BR \"IN \"", "\n.BR \"IN \"")
	clean = clean.replace(".BR \"OUT \"", "\n.BR \"OUT \"")
	clean = clean.replace(".BR \"INOUT \"", "\n.BR \"INOUT \"")
	tex = tex[:sArg] + "\n.SH DESCRIPTION\n.SS Arguments\n" + clean + tex[eArg:]
	tex = tex.replace("\\begin{apiarguments}", "")
	tex = tex.replace("\\end{apiarguments}", "")
	return tex

def descrReplacements(tex):
	sArg = tex.find("\\apidescription{")
	eArg = tex.find("}\n\n", sArg)
	clean = cleanText(tex[sArg:eArg])
	clean = macroReplacements(clean)
	tex = tex[:sArg] + "\n.SS API Description\n" + clean + tex[eArg+1:]
	tex = tex.replace("\\apidescription{", "")
	return tex

def retReplacements(tex):
	sArg = tex.find("\\apireturnvalues{")
	eArg = tex.find("}\n\n", sArg)
	clean = cleanText(tex[sArg:eArg])
	clean = macroReplacements(clean)
	tex = tex[:sArg] + "\n.SS Return Values\n" + clean + tex[eArg + 1:]
	tex = tex.replace("\\apireturnvalues{", "")
	return tex

def notesReplacements(tex):
	sArg = tex.find("\\apinotes{")
	eArg = tex.find("}\n\n", sArg)
	clean = cleanText(tex[sArg:eArg])
	clean = macroReplacements(clean)
	tex = tex[:sArg] + "\n.SS API Notes\n" + clean + tex[eArg + 1:]
	tex = tex.replace("\\apinotes{", "")
	return tex

def impnotesReplacements(tex):
	sArg = tex.find("\\apiimpnotes{")
	eArg = tex.find("}\n\n", sArg)
	clean = cleanText(tex[sArg:eArg])
	clean = macroReplacements(clean)
	tex = tex[:sArg] + "\n.SS Note to implementors\n" + clean + tex[eArg + 1:]
	tex = tex.replace("\\apiimpnotes{", "")
	return tex

def sumReplacements(tex, functionName):
	sArg = tex.find("\\apisummary{")
	eArg = tex.find("}\n\n", sArg)
	clean = cleanText(tex[sArg:eArg])
	clean = clean.replace("\n", "")
	clean = macroReplacements(clean)
	tex = tex[:sArg] + functionName + " \- " \
			+ clean + tex[eArg+1:]
	tex = tex.replace("\\apisummary{", "")
	return tex

def macroReplacements(clean):
	clean = varReplacements(clean)
	clean = generalReplacements(clean)
	clean = constReplacements(clean)
	clean = oprReplacements(clean)
	clean = funcReplacements(clean)
	clean = italReplacements(clean)
	# clean = clean.replace("\n\n", "\n")
	clean = clean.replace("\n ", "\n")
	clean = clean.replace("\n\n.BR ", "\n.BR ")
	clean = clean.replace("\n\n.B ", "\n.B ")
	clean = clean.replace("\n\n.I ", "\n.I ")
	clean = clean.replace("\n\n.IR ", "\n.IR ")
	return clean


def refRMAReplacements(tex):
	if (tex.find("\\ref{stdrmatypes}") != -1):
		while(tex.find("\\ref{stdrmatypes}") != -1):
			index = tex.find("\\ref{stdrmatypes}")
			enter = 0
			last = 0
			while (enter < index):
				last = enter
				enter = tex.find("\n", enter + 1)
			period = tex.find(".", index)
			sentence = tex[last + 1: period + 1]
			tex = tex[:last + 1] + \
				"* For details on TYPE and TYPENAME, please refer to Table 1 below." +\
				tex[period + 1:]
		return (tex, True)
	else:
		return (tex, False)

def refP2PReplacements(tex):
	if (tex.find("\\ref{p2psynctypes}") != -1):
		while(tex.find("\\ref{p2psynctypes}") != -1):
			index = tex.find("\\ref{p2psynctypes}")
			enter = 0
			last = 0
			while (enter < index):
				last = enter
				enter = tex.find("\n", enter + 1)
			period = tex.find(".", index)
			sentence = tex[last + 1: period + 1]
			tex = tex[:last + 1] + \
				"* TYPE is one of the point-to-point synchronization types. For details, please refer to Table 5 below." +\
				tex[period + 1:]
		return (tex, True)
	else:
		return (tex, False)

def refAMOReplacements(tex):
	if (tex.find("\\ref{extamotypes}") != -1):
		while(tex.find("\\ref{extamotypes}") != -1):
			index = tex.find("\\ref{extamotypes}")
			enter = 0
			last = 0
			while (enter < index):
				last = enter
				enter = tex.find("\n", enter + 1)
			period = tex.find(".", index)
			sentence = tex[last + 1: period + 1]
			tex = tex[:last + 1] + \
				"* TYPE is one of the extended AMO types. For details, please refer to Table 3 below." +\
				tex[period + 1:]
		return (tex, True)
	else:
		return (tex, False)

def refSTDReplacements(tex):
	if (tex.find("\\ref{stdamotypes}") != -1):
		while(tex.find("\\ref{stdamotypes}") != -1):
			index = tex.find("\\ref{stdamotypes}")
			enter = 0
			last = 0
			while (enter < index):
				last = enter
				enter = tex.find("\n", enter + 1)
			period = tex.find(".", index)
			sentence = tex[last + 1: period + 1]
			tex = tex[:last + 1] + \
				"* TYPE is one of the standard AMO types. For details, please refer to Table 2 below." +\
				tex[period + 1:]
		return (tex, True)
	else:
		return (tex, False)

def refBITReplacements(tex):
	if (tex.find("\\ref{bitamotypes}") != -1):
		while(tex.find("\\ref{bitamotypes}") != -1):
			index = tex.find("\\ref{bitamotypes}")
			enter = 0
			last = 0
			while (enter < index):
				last = enter
				enter = tex.find("\n", enter + 1)
			period = tex.find(".", index)
			sentence = tex[last + 1: period + 1]
			tex = tex[:last + 1] + \
				"* TYPE is one of the bitwise AMO types. For details, please refer to Table 4 below." +\
				tex[period + 1:]
		return (tex, True)
	else:
		return (tex, False)

def refMEMReplacements(tex):
	if (tex.find("\\ref{subsec:memory_model}") != -1):
		while(tex.find("\\ref{subsec:memory_model}") != -1):
			index = tex.find("\\ref{subsec:memory_model}")
			enter = 0
			last = 0
			while (enter < index):
				last = enter
				enter = tex.find("\n", enter + 1)
			period = tex.find(".", index)
			sentence = tex[last + 1: period + 1]
			tex = tex[:last + 1] + \
				"Please refer to the subsection on the Memory Model for the" + \
				" definition of the term \"remotely accessible\"." + \
				tex[period + 1:]
	return tex

def sizeReplacements(tex):
	if (tex.find("\\SIZE") != -1):
		while(tex.find("\\SIZE") != -1):
			index = tex.find("\\SIZE")
			enter = 0
			last = 0
			while (enter < index):
				last = enter
				enter = tex.find("\n", enter + 1)
			period = tex.find(".", index)
			clean = tex[last + 1: period + 1]
			clean = generalReplacements(clean)
			clean = constReplacements(clean)
			tex = tex[:last + 1] + \
				 clean + \
				tex[period + 1:]
	return tex

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
			coll = coll + "\n" + line
			text = text[e:]
		coll = coll.replace("$", ";")

		if (keyString == "C11synopsis"):
			header = ".SS C11:\n"
		elif (keyString == "Csynopsis"):
			header = ".SS C/C++:\n"
		else:
			header = ""

		tex = tex[:sArg] + header + coll  +\
				 tex[eArg + len("\\end{" + keyString + "}"):]
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
		text = text.replace("$", "")
		tex = tex[:sArg + len("\n")] + ".SS Fortran:\n" + "\n.nf\n" + text + "\n.fi\n" +\
				 tex[eArg + len("\\end{Fsynopsis}"):]
	return tex

def codeReplace(tex):
	tex = synCReplacements(tex, "C11synopsis")
	tex = synCReplacements(tex, "Csynopsis")
	tex = synCReplacements(tex, "CsynopsisCol")
	tex = synFReplacements(tex)
	return tex

def descTReplacements(tex):
	sArg = tex.find("\\apidesctable{")
	eArg = tex.find("}\n\n", sArg)
	text = tex[sArg:eArg+1]
	clean = cleanText(text)
	clean = clean.replace("\n", "")
	clean = macroReplacements(clean)
	beg = clean.find("\\apidesctable{")
	fsBrace = clean.find("{")
	feBrace = clean.find("}", fsBrace)
	ssBrace = clean.find("{", feBrace)
	seBrace = clean.find("}", ssBrace)
	tsBrace = clean.find("{", seBrace)
	teBrace = clean.find("}", tsBrace)
	tex = tex[:sArg] + "\n" + clean[fsBrace+1:feBrace] + \
			"\n.TP 20\n" + clean[ssBrace+1:seBrace] + "\n" + \
			clean[tsBrace+1:teBrace] + tex[eArg+1:]
	return tex

def tablReplacements(tex):
	while(tex.find("\\apitablerow") != -1):
		sArg = tex.find("\\apitablerow")
		eArg = tex.find("}\n", sArg)
		text = tex[sArg:eArg+1]
		clean = cleanText(text)
		clean = clean.replace("\n", " ")
		clean = macroReplacements(clean)
		beg = clean.find("\\apitablerow")
		fsBrace = clean.find("{", beg)
		feBrace = clean.find("}", fsBrace)
		ssBrace = clean.find("{", feBrace)
		seBrace = clean.find("}", ssBrace)
		if (clean[fsBrace+1:feBrace] != ""):
			tex = tex[:sArg] + "\n.TP 20\n" + clean[fsBrace+1:feBrace] + \
				"\n" + clean[ssBrace+1:seBrace] + tex[eArg+1:]
		else:
			tex = tex[:sArg] + "\n" + \
				"\n" + clean[ssBrace+1:seBrace] + tex[eArg+1:]
	return tex

def table1():
	return ".SS Table 1: \n" + \
	".TP 20\n" + \
	".B TYPE\n" + \
	".B TYPENAME\n" + \
	".TP\n" + \
	"float\n" + \
	"float\n" + \
	".TP\n" + \
	"double\n" + \
	"double\n" + \
	".TP\n" + \
	"long double\n" + \
	"longdouble\n" + \
	".TP\n" + \
	"char\n" + \
	"char\n" + \
	".TP\n" + \
	"signed char\n" + \
	"schar\n" + \
	".TP\n" + \
	"short\n" + \
	"short\n" + \
	".TP\n" + \
	"int\n" + \
	"int\n" + \
	".TP\n" + \
	"long\n" + \
	"long\n" + \
	".TP\n" + \
	"long long\n" + \
	"longlong\n" + \
	".TP\n" + \
	"unsigned char\n" + \
	"uchar\n" + \
	".TP\n" + \
	"unsigned short\n" + \
	"ushort\n" + \
	".TP\n" + \
	"unsigned int\n" + \
	"uint\n" + \
	".TP\n" + \
	"unsigned long\n" + \
	"ulong\n" + \
	".TP\n" + \
	"unsigned long long\n" + \
	"ulonglong\n" + \
	".TP\n" + \
	"int8_t\n" + \
	"int8\n" + \
	".TP\n" + \
	"int16_t\n" + \
	"int16\n" + \
	".TP\n" + \
	"int32_t\n" + \
	"int32\n" + \
	".TP\n" + \
	"int64_t\n" + \
	"int64\n" + \
	".TP\n" + \
	"uint8_t\n" + \
	"uint8\n" + \
	".TP\n" + \
	"uint16_t\n" + \
	"uint16\n" + \
	".TP\n" + \
	"uint32_t\n" + \
	"uint32\n" + \
	".TP\n" + \
	"uint64_t\n" + \
	"uint64\n" + \
	".TP\n" + \
	"size_t\n" + \
	"size\n" + \
	".TP\n" + \
	"ptrdiff_t\n" + \
	"ptrdiff\n" 

def table2():
	return ".SS Table 2: \n" + \
	".TP 20\n" + \
	".B TYPE\n" + \
	".B TYPENAME\n" + \
	".TP\n" + \
	"int\n" + \
	"int\n" + \
	".TP\n" + \
	"long\n" + \
	"long\n" + \
	".TP\n" + \
	"long long\n" + \
	"longlong\n" + \
	".TP\n" + \
	"unsigned int\n" + \
	"uint\n" + \
	".TP\n" + \
	"unsigned long\n" + \
	"ulong\n" + \
	".TP\n" + \
	"unsigned long long\n" + \
	"ulonglong\n" + \
	".TP\n" + \
	"int32_t\n" + \
	"int32\n" + \
	".TP\n" + \
	"int64_t\n" + \
	"int64\n" + \
	".TP\n" + \
	"uint32_t\n" + \
	"uint32\n" + \
	".TP\n" + \
	"uint64_t\n" + \
	"uint64\n" + \
	".TP\n" + \
	"size_t\n" + \
	"size\n" + \
	".TP\n" + \
	"ptrdiff_t\n" + \
	"ptrdiff\n" 

def table3():
	return ".SS Table 3: \n" + \
	".TP 20\n" + \
	".B TYPE\n" + \
	".B TYPENAME\n" + \
	".TP\n" + \
	"float\n" + \
	"float\n" + \
	".TP\n" + \
	"double\n" + \
	"double\n" + \
	".TP\n" + \
	"int\n" + \
	"int\n" + \
	".TP\n" + \
	"long\n" + \
	"long\n" + \
	".TP\n" + \
	"long long\n" + \
	"longlong\n" + \
	".TP\n" + \
	"unsigned int\n" + \
	"uint\n" + \
	".TP\n" + \
	"unsigned long\n" + \
	"ulong\n" + \
	".TP\n" + \
	"unsigned long long\n" + \
	"ulonglong\n" + \
	".TP\n" + \
	"int32_t\n" + \
	"int32\n" + \
	".TP\n" + \
	"int64_t\n" + \
	"int64\n" + \
	".TP\n" + \
	"uint32_t\n" + \
	"uint32\n" + \
	".TP\n" + \
	"uint64_t\n" + \
	"uint64\n" + \
	".TP\n" + \
	"size_t\n" + \
	"size\n" + \
	".TP\n" + \
	"ptrdiff_t\n" + \
	"ptrdiff\n" 

def table4():
	return ".SS Table 4: \n" + \
	".TP 20\n" + \
	".B TYPE\n" + \
	".B TYPENAME\n" + \
	".TP\n" + \
	"unsigned int\n" + \
	"uint\n" + \
	".TP\n" + \
	"unsigned long\n" + \
	"ulong\n" + \
	".TP\n" + \
	"unsigned long long\n" + \
	"ulonglong\n" + \
	".TP\n" + \
	"int32_t\n" + \
	"int32\n" + \
	".TP\n" + \
	"int64_t\n" + \
	"int64\n" + \
	".TP\n" + \
	"uint32_t\n" + \
	"uint32\n" + \
	".TP\n" + \
	"uint64_t\n" + \
	"uint64\n"

def table5():
	return ".SS Table 5: \n" + \
		".TP 20\n" + \
		".B TYPE\n" + \
		".B TYPENAME\n" + \
		".TP\n" + \
		"short\n" + \
		"short\n" + \
		".TP\n" + \
		"int\n" + \
		"int\n" + \
		".TP\n" + \
		"long\n" + \
		"long\n" + \
		".TP\n" + \
		"long long\n" + \
		"longlong\n" + \
		".TP\n" + \
		"unsigned int\n" + \
		"uint\n" + \
		".TP\n" + \
		"unsigned short\n" + \
		"ushort\n" + \
		".TP\n" + \
		"unsigned long\n" + \
		"ulong\n" + \
		".TP\n" + \
		"unsigned long long\n" + \
		"ulonglong\n" + \
		".TP\n" + \
		"int32_t\n" + \
		"int32\n" + \
		".TP\n" + \
		"int64_t\n" + \
		"int64\n" + \
		".TP\n" + \
		"uint32_t\n" + \
		"uint32\n" + \
		".TP\n" + \
		"uint64_t\n" + \
		"uint64\n" + \
		".TP\n" + \
		"size_t\n" + \
		"size\n" + \
		".TP\n" + \
		"ptrdiff_t\n" + \
		"ptrdiff\n"

def exampleReplacements(tex):
	sArg = tex.find("\\begin{apiexamples}")
	eArg = tex.find("\\end{apiexamples}")
	text = tex[sArg + len("\\begin{apiexamples}"):eArg]
	clean = cleanText(text)
	clean = clean.replace("\n", "")
	clean = macroReplacements(clean)
	while(clean.find("\\apicexample") != -1):
		beg = clean.find("\\apicexample{")
		fsBrace = clean.find("{", beg)
		feBrace = clean.find("}", fsBrace)
		ssBrace = clean.find("{", feBrace)
		seBrace = clean.find("}", ssBrace)
		tsBrace = clean.find("{", seBrace)
		teBrace = clean.find("}", tsBrace)
		pathS = clean.find("example_code", beg)
		path = clean[pathS:seBrace]
		ex = open(path, "r").read()
		clean = clean[:beg] + "\n" + clean[fsBrace+1:feBrace] + "\n\n.nf\n" + ex \
		+ ".fi\n" + clean[tsBrace+1:teBrace] + clean[teBrace + 1:]
	while(clean.find("\\apifexample") != -1):
		beg = clean.find("\\apifexample{")
		fsBrace = clean.find("{", beg)
		feBrace = clean.find("}", fsBrace)
		ssBrace = clean.find("{", feBrace)
		seBrace = clean.find("}", ssBrace)
		tsBrace = clean.find("{", seBrace)
		teBrace = clean.find("}", tsBrace)
		pathS = clean.find("example_code", beg)
		pathE = clean.find("}", pathS)
		path = clean[pathS:seBrace].strip()
		ex = open(path, "r").read()
		clean = clean[:beg] + "\n" + clean[fsBrace+1:feBrace] + "\n\n.nf\n" + ex \
		+ ".fi\n" + clean[tsBrace+1:teBrace] + clean[teBrace + 1:]
	
	tex = tex[:sArg] + "\n.SS Examples\n" + clean \
				+ tex[eArg + len("\\end{apiexamples}"):]
	return tex


def cleanText(text):
	text = text.replace("\t", "")
	while(text.find("  ") != -1):
		text = text.replace("  ", " ")
	# text = text.replace("\n\n", "\n")
	text = text.replace("\n ", "\n")
	return text

def main():
	if (len(sys.argv) > 2):
		print("Invalid number of arguments. Please only input one file at a time.")
		sys.exit()

	filename = str(sys.argv[1])
	functionName = filename[filename.find("/")+1:filename.find(".")]
	print(functionName)

	texFile = open(filename, "r")
	manFile = open(functionName + ".3", "w")

	titleHeader = writeTH(functionName)
	manFile.write(titleHeader)
	manFile.write(".SH NAME\n")

	tex = texFile.read()
	tex = tex.replace("\\begin{DeprecateBlock}", "")
	tex = tex.replace("\\end{DeprecateBlock}", "")
	tex = tex.replace("\\begin{apidefinition}\n", ".SH   SYNOPSIS")
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
	(tex, rmaTable) = refRMAReplacements(tex)
	(tex, amoTable) = refAMOReplacements(tex)
	(tex, stdTable) = refSTDReplacements(tex)
	(tex, bitTable) = refBITReplacements(tex)
	(tex, p2pTable) = refP2PReplacements(tex)
	tex = tablReplacements(tex)
	tex = refMEMReplacements(tex)
	tex = sizeReplacements(tex)
	if (tex.find("\\begin{apiexamples}") != -1):
		tex = exampleReplacements(tex)
	if (rmaTable):
		tex = tex + table1()
	if (stdTable):
		tex = tex + table2()
	if (amoTable):
		tex = tex + table3()
	if (bitTable):
		tex = tex + table4()
	if (p2pTable):
		tex = tex + table5()
	tex = tex.replace("\\begin{apidefinition}", "")
	tex = tex.replace("\\end{apidefinition}", "")

	tex = tex.replace("$", "")
	tex = tex.replace("\n ", "\n")
	tex = tex.replace("\\\\", "\n")
	manFile.write(tex)
	manFile.close()
	texFile.close()

if __name__== "__main__":
  main()