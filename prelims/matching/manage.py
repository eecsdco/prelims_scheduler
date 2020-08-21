import get_data_from_google as gdg 
from pulp import *
TOL = 0.0001
ENSURE_NUM_AVAIL = 2
MIN_MEETINGS_PER_STUD = 2

def lp_assignment(fac_avail, student_rankings, slots, RANK = 5):
	facs = fac_avail.keys()
	stus = student_rankings.keys()
	prob = LpProblem("Meeting assignment", LpMinimize)
	lp_assmnts = LpVariable.dicts("Assignment", (facs, stus, slots), 0, 1)

	# objective function
	rank_weights = [-10, -5, -2, -1, -1, -1, -1, -1, -1]
	slot_weights = {}
	mult = 0.95
	for ind, slot in enumerate(sorted(slots)):
		slot_weights[slot] = (mult ** ind) * (1.7 ** (1 - (ind % 2)))

	tuples = []

	for stu in stus:		
		for i in range(len(student_rankings[stu])):
			for slot in slots:
				tuples.append((lp_assmnts[student_rankings[stu][i]][stu][slot], slot_weights[slot] * rank_weights[i]))

	prob += LpAffineExpression(tuples), "preference-weighted"

	# TIme constraint
	for slot in slots:
		for fac in facs:
			if fac_avail[fac] is None: continue
			if fac_avail[fac][slot]:
				# faculty meets only one person
				prob += lpSum([lp_assmnts[fac][stu][slot] for stu in stus]) <= 1, ""
			else:
				# faculty is busy
				prob += lpSum([lp_assmnts[fac][stu][slot] for stu in stus]) <= 0, ""
		for stu in stus:
			# each students meets only one faculty per slot
			prob += lpSum([lp_assmnts[facc][stu][slot] for facc in facs]) <= 1, ""

	# no student wants to meet the same person twice
	for fac in facs:
		for stu in stus:
			prob += lpSum([lp_assmnts[fac][stu][slot] for slot in slots]) <= 1, ""

	# every student should meet with at least MIN_MEETINGS_PER_STUD faculty members
	for stu in stus:
		prob += lpSum([lp_assmnts[fac][stu][slot] for fac in facs for slot in slots]) >= MIN_MEETINGS_PER_STUD, ""

	# To ensure some flexibility, we ensure that each faculty member has at least some open slots
	for fac in facs:
		totslots = sum(fac_avail[fac].values()) - ENSURE_NUM_AVAIL
		if totslots < 2:
			continue
		# print fac
		# print totslots
		prob += lpSum([lp_assmnts[fac][stu][slot]
						for stu in stus
						for slot in slots]) <= totslots, ""

	prob.writeLP('assignment.lp')
	prob.solve()
	print LpStatus[prob.status]
#	prob.roundSolution()

	# import pdb; pdb.set_trace()

	for v in prob.variables():
		if v.varValue >= TOL:
			print "Var %s has val %f" % (v.getName(), v.varValue)
			if v.varValue < 0.99:
				print "============================="
				print "=====FOUND NONINT VALUE======"
				print "============================="

	assmnts = {}
	for fac in facs:
		assmnts[fac] = {slot : None for slot in slots}
	 	for slot in slots:
	 		if fac_avail[fac][slot]:
		 		assmnts[fac][slot] = ""
		 		for stu in stus:
			 		if value(lp_assmnts[fac][stu][slot]) == 1:
		 				assmnts[fac][slot] = stu
		 	else:
		 		assmnts[fac][slot] = "Busy"


	return assmnts

def write_to_csv(assments, fac_avail, slots):
	# writer = csv.writer(open(CSV_FILENAME, 'w'), dialect='excel')
	# for slot in sorted(slots):
	# 	writer.writerow
	import pickle
	addresses = pickle.load(open('address_data.pkl'))
	names_map,uniqnames = gdg.read_fac_name_map()
	with open('assignment.csv', 'wb') as csvfile:
		import csv
		myslots = ['faculty name', 'office' ] + slots
		writer = csv.DictWriter(csvfile, myslots)
		writer.writeheader()
		for fac in sorted(fac_avail.keys()):
			row = {slt:assments[fac][slt].replace("Busy","---").split(" <")[0] for slt in slots}
			row['faculty name'] = names_map.get(fac)
			row['office'] = addresses.get(fac)
			writer.writerow(row)


def slot_to_var(slot):
    return 't' + slot.replace(':','')

def stu_to_name(stu):
    return stu[0:stu.find("<")-1]
    
def clean_assignment(assments, fac_avail, slots, fac_namemap):
    table_str = ''
    for slot in slots:
        table_str += '\\hline ' + slot + ' & ' + '{' + slot_to_var(slot) + '} \\\ ' + '\n'

    template = """\\documentclass{{article}}
    \\title{{ Meeting schedule }}
    \\begin{{document}}
    \\thispagestyle{{empty}}    
    \\begin{{center}}
    \\Huge   {facname} \\\\
    \\Large
    {address} \\\\
    \\vspace{{0.4in}}
    \\bigskip
    """
    template += "\\begin{{tabular}}{{|c|c|}}"
    template += table_str
    template += """\\hline
    \\end{{tabular}}
    \\end{{center}}
    \\end{{document}}"""

    import pickle
    addresses = pickle.load(open('address_data.pkl'))
        
    st_assments = {}
    for fac in sorted(fac_avail.keys()):
        info = {'facname': fac_namemap.get(fac, fac),
                'address': addresses.get(fac, '-')}
        for slot in slots:
            stu = assments[fac][slot]
            info[slot_to_var(slot)] = stu
            if stu not in st_assments:
                st_assments[stu] = {}
            st_assments[stu][slot] = fac
        towrite = template.format(**info)
        towrite = towrite.replace("<", "(")
        towrite = towrite.replace(">", ")")
        with open("facs/" + fac + ".tex", "wb") as text_file:
            text_file.write(towrite)
            
            
            
    # students
    stu_template = """\\documentclass{{article}}
    \\title{{ Meeting schedule }}
    \\begin{{document}}
    \\thispagestyle{{empty}}    
    \\begin{{center}}
    \\Huge   {stuname} \\\\
    \\Large
    \\vspace{{0.4in}}
    \\bigskip
    """
    stu_template += "\\begin{{tabular}}{{|c|c|}}"
    stu_template += table_str
    stu_template += """\\hline
    \\end{{tabular}}
    \\end{{center}}
    \\end{{document}}"""
    for stu in sorted(st_assments.keys()):
        stu_name = stu_to_name(stu)
        info = {'stuname': stu_name}
        for slot in slots:
           fac = st_assments[stu].get(slot, " ")
           facinfo =            fac_namemap.get(fac, fac)
           if fac in addresses:
               facinfo += " (" + addresses[fac] + ")"
           info[slot_to_var(slot)] = facinfo
        towrite = stu_template.format(**info)
        towrite = towrite.replace("<", "(")
        towrite = towrite.replace(">", ")")
        towrite = towrite.replace("Beyster Bldg.", "Beyster")

        with open("stus/" + stu_name.replace(" ", "") + ".tex", "wb") as text_file:
            text_file.write(towrite)

        
def greedy_assignment(fac_avail, student_rankings, slots):
	assmnts = {}
	faculty = fac_avail.keys()
	students = student_rankings.keys()
	student_avail = {stud: set() for stud in students}

	for fac in faculty: 
		# By default, the assmnts[fac] is a hash with:
		#     None entries when not assigned and 
		#     N/A entries when unavailable
		assmnts[fac] = {slot : None for slot in slots}
		for slot in slots:
			if fac_avail[fac][slot] == 0:
				assmnts[fac][slot] = "N/A"


	def assign(stud,fac):
		# tries to assign the student to one of the faculty slots
		# if possible, returns success=True and the slot that was found
		success = False		
		for slot in slots:
			# Check necessary conditions if we can assign this student to this fac member
			is_fac_avail = fac_avail[fac][slot]
			is_slot_avail = assmnts[fac][slot] is None 
			is_stud_avail = (slot in student_avail[stud])
			slot = None
			if is_fac_avail and is_stud_avail and is_slot_avail:
				assmnts[fac][slot] = stud 
				success = True 
				break
		return success, slot 

	notdone = True
	while notdone: 
		# we loop until we were unable to fill any slots for any student
		notdone = False
		
		for stud in students:
			if student_rankings[stud]:
				# Get the next faculty member on the student's list
				# Then try to assign this fac to the student
				# If success, record the assignment
				# make sure to pop this fac off the student's list
				fac = student_rankings[stud][0]
				success,slot = assign(stud,fac)
				if success: student_avail[stud].add(slot)
				student_rankings[stud].remove(fac)
				notdone = notdone or success

	return assmnts


if __name__ == '__main__':
	# Get the faculty availability and student ranking data from google
	# import pickle
	# pkl_file = open('data.pkl', 'rb')
	# fac_avail = pickle.load(pkl_file)
	# student_rankings = pickle.load(pkl_file)
	# slots = pickle.load(pkl_file)
	# [fac_avail, student_rankings, slots] = gdg.get_faculty_and_student_data()
		# pprint.pprint(data1)
	# data2 = pickle.load(pkl_file)
	# pprint.pprint(data2)
	# # Do the greedy assignment
	assmnts = lp_assignment(fac_avail, student_rankings, slots)

#	print assmnts

	# with open('assignment.csv', 'wb') as csvfile:
	# 	import csv
	# 	slots.insert(0, 'name')
	# 	writer = csv.DictWriter(csvfile, slots)
	# 	writer.writeheader()
	# 	for fac in fac_avail.keys():
	# 		import copy

	# 		row = copy.deepcopy(assmnts[fac])
	# 		row['name'] = fac
	# 		writer.writerow(row)

#	print assmnts
	
	# # Upload the results to google
	print "uploading to google"
	gdg.upload_assignments(assmnts,slots)



