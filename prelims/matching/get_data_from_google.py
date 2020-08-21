
import gspread
import getpass
import pickle

GEMAIL = 'jakeyboy@gmail.com'
SSHT_URL = 'https://docs.google.com/a/umich.edu/spreadsheet/ccc?key=0AsY0MoR7nxqgdEl3RlNlNFhiNGFpY1Mwcm91a05QaVE'
DOCID = '0AsY0MoR7nxqgdEl3RlNlNFhiNGFpY1Mwcm91a05QaVE'
FAC_NAME_HEAD = 'fac_name'
STUD_NAME_HEAD = 'student_name'
RANK_NUM = 5

STUD_RANKINGS_URL = 'https://docs.google.com/a/umich.edu/spreadsheet/ccc?key=0AjRxYn1fw92tdDA4Si02S05kRDFVQzhxTVg2cUwzcmc&usp=drive_web#gid=0'


STUD_RANK_DOCID = '0AjRxYn1fw92tdDA4Si02S05kRDFVQzhxTVg2cUwzcmc'
STUD_EMAIL_KEY = 'Please enter your email address:'
STUD_NAME_KEY = 'What is your name?'
STUD_RANK_KEYS = [
  'Who is first on your list of CSE Faculty to meet with?',
  'Who is second on your list of CSE Faculty to meet with?',
  'Who is third on your list of CSE Faculty to meet with?',
  'Who is fourth on your list of CSE Faculty to meet with?',
  'Who is fifth on your list of CSE Faculty to meet with?',
  'Who is sixth on your list of CSE Faculty to meet with?',
  'Who is seventh on your list of CSE Faculty to meet with?'
]

FAC_AVAIL_DOCID = '0AjRxYn1fw92tdGVGMDhfOWZnb1pRZ1Q2N09pb1VjSnc'
FAC_AVAIL_TIMES_KEY = 'When are you available on FRIDAY March 14?'
FAC_UNIQ_KEY = 'Username'

FAC_AVAIL_TIMES = ['1:30-2pm',
 '2-2:30pm',
 '2:30-3pm',
 '3-3:30pm',
 '3:30-4pm',
 '4-4:30pm',
 '4:30-5pm',
 '5-5:30pm',
 '5:30-6pm',
 '6-6:30pm']

SLOTS = range(20)

SLOT_NAMES = [
	"1:30",
	"1:45",
	"2:00",
	"2:15",
	"2:30",
	"2:45",
	"3:00",
	"3:15",
	"3:30",
	"3:45",
	"4:00",
	"4:15",
	"4:30",
	"4:45",
	"5:00",
	"5:15",
	"5:30",
	"5:45",
	"6:00",
	"6:15"
]

PKL_DATA_FNAME = "google_data_for_processing.pkl"

def make_open(): 
	return { '1:30': 1,'1:45': 1,'2:00': 1,'2:15': 1,'2:30': 1,'2:45': 1,'3:00': 1,
	'3:15': 1,'3:30': 1,'3:45': 1,'4:00': 1,'4:15': 1,'4:30': 1,'4:45': 1,'5:00': 1,
	'5:15': 1,'5:30': 1,'5:45': 1,'6:00': 1,'6:15': 1}

def make_closed(): 
	return { '1:30': 0,'1:45': 0,'2:00': 0,'2:15': 0,'2:30': 0,'2:45': 0,'3:00': 0,
	'3:15': 0,'3:30': 0,'3:45': 0,'4:00': 0,'4:15': 0,'4:30': 0,'4:45': 0,'5:00': 0,
	'5:15': 0,'5:30': 0,'5:45': 0,'6:00': 0,'6:15': 0}

def read_fac_name_map():
	table = {}
	uniqnames = set([])
	with open("faculty_uniqname_name.txt") as f:
	    for line in f:
	        uniq, name = line.encode("ascii",'ignore').replace("  ", " ").strip().split("\t")
	        table[uniq] = name
	        table[name] = uniq
	        uniqnames.add(uniq)
	return table, uniqnames

TABLE, UNIQS = read_fac_name_map()

def get_sheet_records_from_docid(docid):
	_user = 'jakeyboy@gmail.com'
	_pw = getmypass()
	g = gspread.login(_user, _pw)
	return g.open_by_key(docid).sheet1.get_all_records()

def get_student_rankings():
	records = get_sheet_records_from_docid(STUD_RANK_DOCID)
	student_rankings = {}
	for dat in records:
		name, email = dat[STUD_NAME_KEY], dat[STUD_EMAIL_KEY]
		nameemail = "%s <%s>" % (name,email)
		if len(name) < 3:
			print "NO NAME: %s" % name
			continue
		print "NAME: %s\tEMAIL: %s" % (name, email)
		ranking = []
		for key in STUD_RANK_KEYS:
			fac_name = dat[key].encode("ascii",'ignore')
			if fac_name == "": continue
			fac_uniqname = TABLE.get(fac_name)
			if fac_uniqname is None:
				print "----NAME NOT RECOGNIZED %s" % fac_name
			else:
				print "==> %s" % fac_uniqname
				ranking.append(fac_uniqname)
		student_rankings[nameemail] = ranking
	return student_rankings

def get_faculty_availability():
	records = get_sheet_records_from_docid(FAC_AVAIL_DOCID)
	fac_avail = {}
	for fac in UNIQS: fac_avail[fac] = make_closed()
	for dat in records:
		uniqname = dat[FAC_UNIQ_KEY].replace("@umich.edu","")
		times = dat[FAC_AVAIL_TIMES_KEY].replace(" ","").split(",")
		if len(uniqname) < 3:
			print "NO NAME: %s" % uniqname
			continue
		print "NAME: %s\tTIMES: %s" % (uniqname, "/".join(times))
		avail_hash = {}
		for timeind,timekey in enumerate(FAC_AVAIL_TIMES):
			val = 1 if timekey in times else 0
			avail_hash[SLOT_NAMES[2*timeind]] = val
			avail_hash[SLOT_NAMES[2*timeind + 1]] = val
		fac_avail[uniqname] = avail_hash
	return fac_avail

def get_and_save_all_data():
	data = {
		'fac_avail' : get_faculty_availability(),
		'student_rankings' : get_student_rankings(),
		'slots' : SLOT_NAMES,
		'uniqnames' : UNIQS
	}
	pickle.dump(data, open(PKL_DATA_FNAME, 'w+'))

def load_all_data():
	data = pickle.load(open(PKL_DATA_FNAME))
	return data

global _pswd 
_pswd = None

def getmypass():
	global _pswd
	if _pswd is None:
		_pswd = getpass.getpass()
	return _pswd

def full_login_and_get_ss(docid):
	# _user = raw_input('Account name: ')
	_user = 'jakeyboy@gmail.com'
	_pw = getmypass()

	g = gspread.login(_user, _pw)
	#SSHT_URL = 'https://docs.google.com/a/umich.edu/spsht/ccc?key=0AsY0MoR7nxqgdEl3RlNlNFhiNGFpY1Mwcm91a05QaVE'
	spsht = g.open_by_key(docid)
	return spsht

def login_and_get_ss():
	# Login and return the spreadsheet of interest
	gc = gspread.login(GEMAIL, _pw)
	spsht = gc.open_by_url(SSHT_URL)
	return spsht

def get_faculty_and_student_data():
	# Grab the google spreadsheet data and clean up
	spsht = full_login_and_get_ss(DOCID)
	[facsht,studsht,asssht] = spsht.worksheets()
	fac_avail = {}
	slots = None
	for avail_hash in facsht.get_all_records():
		fac_name = avail_hash.pop(FAC_NAME_HEAD)
		if slots is None:
			slots = avail_hash.keys()
			slots.sort()
		fac_avail[fac_name] = avail_hash

	student_rankings = {}

	recs = studsht.get_all_records()

	# import pdb; pdb.set_trace()

	for rank_hash in recs:
		student_name = rank_hash.pop(STUD_NAME_HEAD)
		student_rankings[student_name] = [rank_hash[str(ind)] for ind in range(1,RANK_NUM+1) if rank_hash.get(str(ind))]

	return [fac_avail, student_rankings, slots]


def upload_assignments(assmnts,slots):
	spsht = full_login_and_get_ss(DOCID)
	[facsht,studsht,asssht] = spsht.worksheets()
	faculty = assmnts.keys()
	faculty.sort()
	cells = []
	def lup(row,col,val):
		asssht.update_cell(row,col,val)
		# cell = asssht.cell(row,col)
		# cell.value = val
		# cells.append(cell)
	for sind,slot in enumerate(slots):
		lup(1,sind+2,slot)

	for ind,fac in enumerate(faculty):
		row = ind + 2
		lup(row,1,fac)
		for sind,slot in enumerate(slots):
			if assmnts[fac][slot] is not None: val = assmnts[fac][slot]
			else: val = ""
			lup(row,sind+2,val)

	# asssht.update_cells(cells)

def main():
	[fac_avail, student_rankings, slots] = get_faculty_and_student_data()

	import pprint, pickle
	pkl_file = open('data.pkl', 'wb')

	pickle.dump(fac_avail, pkl_file, -1)
	pickle.dump(student_rankings, pkl_file, -1)
	pickle.dump(slots, pkl_file, -1)
	pkl_file.close()


if __name__ == '__main__':
	get_and_save_all_data()
	# pass


