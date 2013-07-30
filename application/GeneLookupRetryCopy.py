from flask import Flask, request, Response, session, g, redirect, url_for, \
	abort, render_template, flash, send_from_directory, send_file
import os

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

studyFiles=[]
mutationFiles=[]
for file in os.listdir('data'):
	#files.append(open('data/'+file, 'r'))
	if 'header' in file:
		studyFiles.append(open('data/'+file, 'r'))
	elif 'dnm' in file:
		mutationFiles.append(open('data/'+file, 'r'))
'''		
files=[]
for file in os.listdir('data'):
	files.append('data/'+file, 'r')

groupsOfStudies = []
groupsOfMutations = []
for file in files:
	if 'dnv' in file:
		for line in file:
			theMutation= file.name.split('_')
			
			groupsOfMutations.append
'''

groupsOfStudies = []
for file in studyFiles:
	studyGroup = []
	studyGroupName = None
	for line in file:
		if '##' in line:
			studyGroupName = line.replace('##', '')
		else:
			studyGroup.append(line.split('\t'))
	studyGroupId = file.name.split('_')
	studyGroup.append(studyGroupName)
	studyGroup.append(studyGroupId[0].replace('data/', ''))
	groupsOfStudies.append(studyGroup)
	#print studyGroup

groupsOfMutations = []
for file in mutationFiles:
	mutationGroup =[]
	theGroup = file.name.replace('data/', '').split('_')
	mutStudyGroup = 'NA'
	for line in file:
		#print '1'
		theMutationInfo = line.split('\t')
		for group in groupsOfStudies:
			#print len(group)
			if len(group) != 0:
				#print '3'
				#print theGroup[0]+" "+group[len(group)-1]
				if theGroup[0] == group[len(group)-1]:
					#print '4'
					mutStudyGroup = group[len(group)-2]
					if not 'study' in theMutationInfo[7]:
						if not 'study' in (group[int(theMutationInfo[7])])[0]:
							#print '5'
							#print "mutinfo "+theMutationInfo[7]
							#print "studyINfo"
							#print (group[int(theMutationInfo[7])])[0]
							try:
								theMutationInfo.append(group[int(theMutationInfo[7])+3])
								#theMutationInfo.append(int((group[int(theMutationInfo[7])])[0])+3)
							except ValueError:
								print "errror passed"
							#print theMutationInfo
		#for file in studyFiles:
		#	if theGroup[0] in file.name:
		#		mutStudyGroup = theGroup[0]
		#theMutationinfo.append(mutStudyGroup)
		mutationGroup.append(theMutationInfo)
	mutationGroup.append(mutStudyGroup)
	#for group in groupsOfStudies:
	#	if theGroup[0] == group.pop():
	#		mutationGroup.append(group.pop())
		

@app.route('/')
def initialize():
	return render_template('GeneLookupRetry.html', geneMutations=None)

@app.route('/lookupGene', methods=['POST'])
def lookupGene():
	theGene = request.form['requestedGene']
	groupsMutsReturn = []
	print groupsOfMutations
	for group in groupsOfMutations:
		groupMut = []
		for mutation in group:
			if mutation[0] == theGene:
				groupMut.append(mutation)
		groupMut.append(group[len(group)-1])
		groupsMutsReturn.append(groupMut)
		print groupMut
	print groupsMutsReturn
	return render_template('GeneLookupRetry.html', geneMutations=groupsMutsReturn)



if __name__ == '__main__':
	app.run()