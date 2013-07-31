from flask import Flask, request, Response, session, g, redirect, url_for, \
	abort, render_template, flash, send_from_directory, send_file
import os
import StringIO

DEBUG = True
application = Flask(__name__)
application.config.from_object(__name__)

studyFiles=[]
mutationFiles=[]
for file in os.listdir('application/data'):
	if 'header' in file:
		studyFiles.append(open('application/data/'+file, 'r'))
	elif 'dnm' in file:
		mutationFiles.append(open('application/data/'+file, 'r'))

groupsOfStudies = []
for file in studyFiles:
	studyGroup = []
	studyGroupName = None
	for line in file:
		if '##' in line:
			studyGroupName = line.replace('##', '')
		elif not '#' in line:
			studyGroup.append(line.split('\t'))
	studyGroupId = file.name.split('_')
	studyGroup.append(studyGroupName)
	studyGroup.append(studyGroupId[0].replace('application/data/', ''))
	groupsOfStudies.append(studyGroup)

groupsOfMutations = []
triosPerStudyGroup = []
numTrios = 0
for file in mutationFiles:
	mutationGroup =[]
	theGroup = file.name.replace('application/data/', '').split('_')
	mutStudyGroup = 'NA'
	for line in file:
		theMutationInfo = line.split('\t')
		for group in groupsOfStudies:
			if len(group) != 0:
				if theGroup[0] == group[len(group)-1]:
					mutStudyGroup = group[len(group)-2]
					if not 'study' in theMutationInfo[7]:
						theMutationInfo.append(group[int(theMutationInfo[7])])
		mutationGroup.append(theMutationInfo)
	mutationGroup.append(mutStudyGroup)
	groupsOfMutations.append(mutationGroup)
	
for group in groupsOfStudies:
	for study in group:
		if not 'study' in study[0]:
			if not isinstance(study, basestring):
				numTrios += int(study[1])
	triosPerStudyGroup.append(numTrios)
	numTrios = 0
@application.route('/')
def initialize():
	return render_template('GeneLookupNoRPY2.html', geneMutations=None)

downloadableInfo = StringIO.StringIO()
theGene = ''
mutsForFile = []
@application.route('/lookupGene', methods=['POST'])
def lookupGene():
	theGene = request.form['requestedGene']
	theGene = theGene.upper()
	groupsMutsReturn = []
	downloadableInfo = StringIO.StringIO()
	constrainList = open('application/constrained_1003.txt', 'r')
	constrained = False
	for line in constrainList:
		if theGene == line.replace('\n', ''):
			constrained = True
	
	for group in groupsOfMutations:
		groupMut = []
		for mutation in group:
			if mutation[0] == theGene:
				groupMut.append(mutation)
		groupMut.append(group[len(group)-1])
		groupsMutsReturn.append(groupMut)
	
	nonStringIO = theGene+'\n\n'
	
	geneData = open('application/esp6500_ac10_Zdata.txt', 'r')
	allData = geneData.read()
	eachGene = allData.split('\r')
	genesArray = []
	for gene in eachGene:
		genesArray.append(gene.split('\t'))
	geneSuppInfo = None
	for gene in genesArray:
		if gene[1] == theGene:
			geneSuppInfo = gene
			geneSuppInfo[7] = float(geneSuppInfo[7])*2
			geneSuppInfo[8] = float(geneSuppInfo[8])*2
			geneSuppInfo[9] = float(geneSuppInfo[9])*2
			break
	if geneSuppInfo != None:
		if geneSuppInfo[1].lower() == 'gene':
			geneSuppInfo = None
		nonStringIO += 'Chromosome:,'+geneSuppInfo[2]+'\nStart--Stop:,'+geneSuppInfo[3]+'--'+geneSuppInfo[4]+'\n# BasePairs:,'+geneSuppInfo[5]
		nonStringIO += 'Per Trio Probability of Mutation:\n , Synonymous:,'+repr(geneSuppInfo[7])+'\n ,Missense:,'+repr(geneSuppInfo[8])+'\n ,Loss of Function:,'+repr(geneSuppInfo[9])
		nonStringIO += 'Constraint Scores:\n ,Z syn:,'+geneSuppInfo[23]+'\n ,Z mis:,'+geneSuppInfo[24]+'\n ,Z LoF:,'+geneSuppInfo[26]
	if constrained == True:
		nonStringIO += '\n\nThis gene is constrained.\n'
	else:
		nonStringIO += '\n\nThis gene is not constrained.\n'
	for group in groupsMutsReturn:
		nonStringIO += group[len(group)-1]
		nonStringIO += 'Mutation Type, AAchange, Chr, Pos, Ref, Alt, Study, Link to study\n'
		#nonStringIO += 'Gene Name, Mutations, #Lof, Prob(LoF), Prob(LoF+mis), Prob(mis), 2*prob, exp#, ppois, Compared to\n'
		for mut in group:
			if len(mut) >= 9:
				if len(mut[8]) >= 4:
					nonStringIO += mut[0]+','+mut[1]+','+mut[2]+','+mut[3]+','+mut[4]+','+mut[5]+','+mut[6]+','+mut[8][2]+' with '+mut[8][1]+' trios\n'
	holderNumTrios = list(triosPerStudyGroup)
	holderTwoNumTrios = list(triosPerStudyGroup)
	return render_template('GeneLookupNoRPY2.html', geneMutations=groupsMutsReturn, isConstrained = constrained, strForDwnld = nonStringIO, otherGeneInfo = geneSuppInfo, triosPerStudy = holderNumTrios, secondTriosPerStudy = holderTwoNumTrios)

@application.route('/downloadGeneMuts/<downloadString>')
def downloadGeneMuts(downloadString):
	downloadableInfo = StringIO.StringIO()
	downloadableInfo.write(str(downloadString))
	downloadableInfo.seek(0)
	return send_file(downloadableInfo, attachment_filename="GeneMutations.csv", as_attachment=True)

if __name__ == '__main__':
	application.run()