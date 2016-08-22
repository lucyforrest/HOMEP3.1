# Name: straln.py
# Language: python3
# Libraries: 
# Description: Runs the structural alignments needed for HOMEP
# Author: Edoardo Sarti
# Date: Aug 17 2016

import os, sys, multiprocessing, subprocess, re, time

def FrTMjob(data):
	locations, target, exelist = data
	
	superfamily_path = locations['mainpath'] + target[0] + '/' target[1] + '/'
	sequence_path = superfamily_path + 'alignments/fasta/seq_' + target[2] + '.dat'
	structure_path = superfamily_path + 'alignments/str_alns/str__' + target[2] + '.dat'

	# Checks for needed locations:
	# Superfamily path
	if not os.path.exists(superfamily_path):
		raise NameError("ERROR: Superfamily {0} not found in path {1}".format(target[0]+' '+target[1]), superfamily_path)
	# structure/ folder
	if not os.path.exists(superfamily_path + 'structures/'):
		raise NameError("ERROR: structures/ folder not found in path {0}".format(superfamily_path)
	# Main pdb file
	if not os.path.exists(superfamily_path + 'structures/' + target[2] + '.pdb'):
		raise NameError("ERROR: File {0} not found in {1}".format(target[2] + '.pdb', superfamily_path + 'structures/')
	# Secondary pdb files
	for chain in exelist:
		if not os.path.exists(superfamily_path + 'structures/' + chain + '.pdb'):
			raise NameError("ERROR: File {0} not found in {1}".format(chain + '.pdb', superfamily_path + 'structures/')
	
	# Creates, if needed, the alignment locations
	if not os.path.exists(superfamily_path + 'alignments/'):
		os.mkdir(superfamily_path + 'alignments/')
	if not os.path.exists(superfamily_path + 'alignments/fasta/'):
		os.mkdir(superfamily_path + 'alignments/fasta/')
	if not os.path.exists(superfamily_path + 'alignments/str_alns/'):
		os.mkdir(superfamily_path + 'alignments/str_alns/')

	# Checks if the main sequence file already exists. If it does, checks again if none of the alignments in exelist
	# is contained in the file. Cancels from exelist any found alignment.
	if os.path.exists(sequence_path):
		sequence_file = open(sequence_path, 'r')
		text = sequence_file.read().split('\n')
		for line in text:
			if 'CHAIN_2:' in line and field[1] in exelist:
				logmsg = "Update repository with {0}_{1} sequence alignment".format(exelist[2], field[1])
				update_repository.append(field[1])
				exelist.remove[field[1]]
		sequence_file.close()

	# Checks if the main structure file already exists. If it does, checks again if none of the alignments in exelist
	# is contained in the file. Cancels from exelist any found alignment.
	if os.path.exists(structure_path):
		structure_file = open(structure_path, 'r')
		text = structure_file.read().split('\n')
		for line in text:
			if 'CHAIN_2:' in line and field[1] in exelist:
				logmsg = "Update repository with {0}_{1} alignment".format(exelist[2], field[1])
				update_repository.append(field[1])
				exelist.remove[field[1]]
		structure_file.close()
	
	# Creates the temporary folder for sequence alignments
	aln_tmpfolder_path = superfamily_path + 'alignments/fasta/tmp_' target[2] + '/'
	if not os.path.exists(aln_tmpfolder_path):
		os.mkdir(aln_tmpfolder_path)

	# Creates the temporary folder for structure alignments
	straln_tmpfolder_path = superfamily_path + 'alignments/str_alns/tmp_' target[2] + '/'
	if not os.path.exists(straln_tmpfolder_path):
		os.mkdir(straln_tmpfolder_path)

	pdb1_filename = superfamily_path + 'structures/' + target[2] + '.pdb'
	for chain in exelist:
		# Defines filenames
		pdb2_filename = superfamily_path + 'structures/' + chain + '.pdb'
		seq_output_filename = aln_tmpfolder_path + 'aln_' target[2] + '_' + chain + '.tmp'
		str_output_filename = 'straln_' + target[2] + '_' + chain + '.tmp' # This filename is without path for a constraint on flags length of frtmalign (see below)
		stdout_filename = aln_tmpfolder_path + 'output_' + target[2] + '_' + chain + '.tmp'

		# Fr-TM-align call
		# The Fr-TM-align command cannot exceed a certain length. Thus, we are compelled to run it locally into structures/
		# The stdout file from Fr-TM-align can go directly to the right temporary folder (but needs to be cleaned)
		stdout_file = open(stdout_filename, 'w')
		fnull = open(os.devnull, 'w')
		p = subprocess.Popen([target[3], file_1, file_2, '-o', str_output_filename], stdout=stdout_file, stderr=fnull, cwd=superfamily_path+'structures/')
		fnull.close()
		p.wait()
		stdout_file.close()

		# Moves the Fr-TM-align output file into the structure temporary folder
		os.rename(superfamily_path + 'structures/' + str_output_filename, straln_tmpfolder_path + str_output_filename)

		# Reads and then removes the stdout file from Fr-TM-align
		stdout_file = open(stdout_filename, 'r')
		text = stdout_file.read().split('\n')
		stdout_file.close()
		os.remove(stdout_filename)
		
		# From the stdout file from Fr-TM-align, it takes the RMSD, TM-score and the two aligned sequences
		chkaln = -1000
		if "Aligned length" in text[nl]:
			fields = re.split('=|,|\s',text[nl])
			fields = list(filter(None, fields))
			RMSD = float(fields[4])
			TMscore = float(fields[6])
		elif chkaln+1 == nl:
			seq_1 = text[nl]
		elif chkaln+3 == nl:
			seq_2 = text[nl]
		elif "denotes the residue pairs of distance" in text[nl]:
			chkaln = nl
		
		# Creates a sequence temporary file already correctly formatted
		seq_output_file = open(seq_output_filename, 'w')
		seq_output_file.write(">" + chain_1 + "\n" + seq_1.replace('\x00', '') + "\n>" + chain_2 + "\n" + seq_2.replace('\x00', '') + "\n\nRMSD\t{0:.2f}\nTM-score\t{1:.5f}\n\n".format(RMSD, TMscore))
		seq_output_file.close()

	# Writes on the main sequence file. Each alignment begins with a "BEGIN" line, followed by two lines reporting the two chain names
	# (format: CHAIN_X: chain_name, where X={1,2}), and ends with and "END" line.
	sequence_file = open(sequence_path, 'a')
	for tmp_filename in sorted(os.listdir(aln_tmpfolder_path)):
		sequence_file.write("BEGIN \nCHAIN_1: " + target[2]  + "\nCHAIN_2: " + tmp_filename[-10:-4])
		tmp_file = open(aln_tmpfolder_path + tmp_filename)
		text = tmp_file.read().split('\n')
		tmp_file.close()
		for line in text:
			sequence_file.write(line+'\n')
		sequence_file.write("END\n\n\n")
		os.remove(aln_tmpfolder_path + tmp_filename)
	time.sleep(1)
	os.rmdir(aln_tmpfolder_path)
	sequence_file.close()

	# Writes on the main structure file. Each alignment begins with a "BEGIN" line, followed by two lines reporting the two chain names
	# (format: CHAIN_X: chain_name, where X={1,2}), and ends with and "END" line.
	structure_file = open(structure_path, 'a')
	for tmp_filename in sorted(os.listdir(straln_tmpfolder_path)):
		structure_file.write("BEGIN \nCHAIN_1: " + target[2]  + "\nCHAIN_2: " + tmp_filename[-10:-4])
		tmp_file = open(straln_tmpfolder_path + tmp_filename)
		text = tmp_file.read().split('\n')
		tmp_file.close()
		for line in text:
			structure_file.write(line+'\n')
		structure_file.write("END\n\n\n")
		os.remove(straln_tmpfolder_path + tmp_filename)
	time.sleep(1)
	os.rmdir(straln_tmpfolder_path)
	structure_file.close()
	

def structure_alignment(locations, aligner_path, np):
	already_processed = []
	hidden_repository_filename = locations['mainpath'] + '.structure_alignments.dat'
	if os.path.exists(hidden_repository_filename):
		hidden_repository_file = open(hidden_repository_filename, 'r')
		text = hidden_repository_file.read().split("\n")
		for line in text:
			fields = line.split()
			already_processed.append((fields[2], fields[3]))
	
	superfamilies = []
	for ss in 'alpha', 'beta':
		for i in os.listdir(locations['mainpath'] + ss + '/'):
			if re.match('^\d*$', str(i)):
				superfamilies.append(ss, i)

	exelist = {}
	for sf in superfamilies:
		structs = [x for x in os.listdir(locations['mainpath'] + sf[0] + '/' + sf[1] + '/') if x[-4:] == '.pdb']
		if len(structs) > 1:
			for s1 in structs:
				exelist[s1] = []
				for s2 in structs:
					if s1 == s2 or (s1[-4:], s2[-4:]) in already_processed:
						continue
					exelist[s1].append((sf[0], sf[1], s1, s2))

	for i in list(exelist.keys()):
		data.append((locations, (exelist[i][0], exelist[i][1], exelist[i][2], aligner_path), exelist[i][3]))

	pool = multiprocessing.Pool(processes=np)
	pool_outputs = pool.map(FrTMjob, data)
