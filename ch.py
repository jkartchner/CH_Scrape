#! python 3
# ch.py - scrapes denvercourt/themis for criminal 
# history for a given defendant w/DOB

# TODO: show open cases (nxt court date set in noCos tab); sentence; FTAs

import requests, sys, time, datetime, bs4, subprocess
from tqdm import tqdm
def now_milliseconds():
	return int(time.time() * 1000)


bool_Emergency = False

###### ENTRY POINT TO FUNCTIONING CODE  ######

input_first_name = input("Def First Name: ").upper() # todo: string verify
if "EMERGENCY" in input_first_name:
	bool_Emergency = True
	print("OK, I'll hurry.\n")
	input_first_name = input("Def First Name: ").upper() # todo: string verify
input_last_name = input("Def Last Name: ").upper() # todo: string verify
input_DOB = input("Def DOB: ") # todo: string format/date verify

##### OPEN FILE HANDLE  ########################
f = open("C:\\Users\\XXXXXX\\Downloads\\defendant.txt", 'w')


# COCOURTS VARIABLES
# Get webpage
# The URL for the authentication page for main website
# url = 'https://www.jbits.courts.state.co.us/pas/pubaccess/index.cfm'  # no longer needed
url_splash = 'https://www.jbits.courts.state.co.us/pas/pubaccess/action.cfm'
url_terms = 'https://www.jbits.courts.state.co.us/pas/pubaccess/user/terms.cfm'
url_personsearch_splash = 'https://www.jbits.courts.state.co.us/pas/pubaccess/user/person.cfm'
url_personsearch = 'https://www.jbits.courts.state.co.us/pas/pubaccess/user/search.cfm'

payload_login = {'actionType':'Login',
                 'username'  :'XXXXXXX@xxxxxx.xxx',
                 'password'  :'XXXXXXXXXXXX' }
payload_terms = {'commit'    :'1',
                 'acceptButton.x':'61',
                 'acceptButton.y':'16'          }
payload_personsearch = {
                 'searchType'   :'person',
                 'locationCodes':'CO_DCY_*',
                 'caseTypeCR'   :'CR',
                 'casetypeJV'   :'JV',
                 'casetypeTR'   :'TR',
                 'lastname1'    :input_last_name,
                 'firstname1'   :input_first_name,
                 'middlename1'  :'',
                 'dob1'         :input_DOB,
                 'lastname2'    :'',
                 'firstname2'   :'',
                 'middlename2'  :'',
                 'dob2'         :'',
                 'lastname3'    :'',
                 'firstname3'   :'',
                 'middlename3'  :'',
                 'dob3'         :'',
                 'lastname4'    :'',
                 'firstname4'   :'',
                 'middlename4'  :'',
                 'dob4'         :'',
                 'lastname5'    :'',
                 'firstname5'   :'',
                 'middlename5'  :'',
                 'dob5'         :'',
                 'dateBegin'    :'',
                 'dateEnd'      :'',
                 'includeAlias' :'1',
                 'x'            :'59',
                 'y'            :'9'    }




# THEMIS VARIABLES
# The URL for the authentication page for main website
url = 'http://denvercourt.dcc.dnvr/courtnet/login.aspx'
# The URL for the get request to search a name
get_url = 'http://denvercourt.dcc.dnvr/courtnet/name_search.aspx?_'
# The URL for the get request to search a case
casesearch_url = 'http://denvercourt.dcc.dnvr/courtnet/court_result.aspx?caseNo='

# payload info generated from dev tools, Network tab after submitting request
# was able to find form data in the head tab and used that directly
payload = {'__LASTFOCUS':'',
	   '__EVENTTARGET':'',
	   '__EVENTARGUMENT':'',
	   '__VIEWSTATE':'/wEPDwUJNjQyODUzNDYyD2QWAmYPZBYCAgMPZBYCAgUPZBYCAgUPD2QWAh4Fc3R5bGUFGXRleHQtdHJhbnNmb3JtOnVwcGVyY2FzZTtkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBSJjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJGNiX0FncmVlWbd1tFkrgCyhC18H9VpiFgelE+k=', 
	   '__VIEWSTATEGENERATOR':'355B8235',
	   '__EVENTVALIDATION':'/wEWBQK90dzODALJ4fq4BwL90KKTCALC4Iy6CgK8haTMDE41xwE2XedmDLm1WF64yqlP/gCC',
	   'ctl00$ContentPlaceHolder1$txtUserName':'XXXX',
	   'ctl00$ContentPlaceHolder1$txtPassword':'XXXXXX',
	   'ctl00$ContentPlaceHolder1$cb_Agree':'on',
	   'ctl00$ContentPlaceHolder1$cmdEnter':'Enter'}

abbre_dict = {	'disturbing the peace':'disturb peace',
		'court supervised probation':'Crt Sup Probation',
		'jail time imposed':'jail',
		'driving under restraint':'DUR',
		'jail time susp cond.':'suspend',
		'concurrent jail sent':'concurrent',
		'consecutive jail sent':'consecutive',
		'threats to person/property':'threats',
		'interference w/ police officer':'interference',
		'destruction of private property':'destruction (priv)',
		'destruction private property':'destruction (priv)',
		'supervised probation':'probation',
		'fine/costs credit for jail':'jail credit for fine',
		'pub consumption of alcohol':'public alcohol',
		'urinating in public':'urin in public',
		'poss drug paraphernalia':'drug paraph'}

count_FTA = 0

list_toWrite = list()
str_toWrite = ""

#### COCOURTS SEARCH ############################################################
with requests.Session() as ses:
    f.write("COLORADO COURTS\n")
    p2 = ses.post(url_splash, data=payload_login)
    p3 = ses.post(url_terms, data=payload_terms)
    p4 = ses.get(url_personsearch_splash)
    p5 = ses.post(url_personsearch, data=payload_personsearch)
    parser_HTML = bs4.BeautifulSoup(p5.text, "html.parser")
    list_coCrts_caseNos = parser_HTML.select('#resultsSet a')
    list_coCrts_openCases = parser_HTML.select('#resultsSet td')
    for openCase in list_coCrts_openCases:
        if "Open" in openCase.getText().strip():
            f.write("Defendant has open cases. Check CoCourts!\n")
            break
    del list_coCrts_caseNos[:9]
    print("Searching Colorado Courts for " + str(len(list_coCrts_caseNos)) + " listed cases")
    for caseNo in tqdm(list_coCrts_caseNos):
        p6 = ses.get(caseNo["href"])
        parser_conviction_HTML = bs4.BeautifulSoup(p6.text, "html.parser")
        list_coCrts_convictionData = parser_conviction_HTML.select('td')
        for data_index in range(len(list_coCrts_convictionData)):
            if "Disposition: Guilty" in list_coCrts_convictionData[data_index].getText():
                f.write(caseNo.getText() + " -- ") 
                for data_check_string in range(15):
                    if "Class: " in list_coCrts_convictionData[data_index - data_check_string - 1].getText():
                        f.write(list_coCrts_convictionData[data_index - data_check_string - 1].getText().replace("Class: ", '')[:2] + " ")
                    if "Charge: " in list_coCrts_convictionData[data_index - data_check_string - 1].getText():
                        f.write(list_coCrts_convictionData[data_index - data_check_string - 1].getText().replace("Charge: ", '').strip())
                for data_check_string in range(8):
                    if "Jail" in list_coCrts_convictionData[data_index + data_check_string].getText() or "Probation" in list_coCrts_convictionData[data_index + data_check_string].getText() or "Department of Corrections" in list_coCrts_convictionData[data_index + data_check_string].getText():
                        list_sentencing_data = bs4.BeautifulSoup(str(list_coCrts_convictionData[data_index + data_check_string]), "html.parser").select('td') # Get all tds in the sentencing mini table
                        for data_check_jail_string in range(1, len(list_sentencing_data)):
                            if "Jail" in list_sentencing_data[data_check_jail_string].getText() and "Cost" not in list_sentencing_data[data_check_jail_string].getText() or "Department of Corrections" in list_sentencing_data[data_check_jail_string].getText():
                                f.write(" -- " + list_sentencing_data[data_check_jail_string].getText() + " " + list_sentencing_data[data_check_jail_string + 1].getText() + " " + list_sentencing_data[data_check_jail_string + 2].getText() + " " + list_sentencing_data[data_check_jail_string + 3].getText()) 
                            if "Probation" in list_sentencing_data[data_check_jail_string].getText() and "Fee" not in list_sentencing_data[data_check_jail_string].getText():
                                f.write(" -- " + list_sentencing_data[data_check_jail_string].getText() + " " + list_sentencing_data[data_check_jail_string + 1].getText() + " " + list_sentencing_data[data_check_jail_string + 2].getText() + " " + list_sentencing_data[data_check_jail_string + 3].getText()) 
                f.write(" -- " + list_coCrts_convictionData[2].getText().replace("Location: ",'') + '\n')
        if bool_Emergency ==  False:
            time.sleep(2.0) # BE POLITE TO SCRAPED SERVER
    f.write("\nNumber of cases in Colorado Courts: " + str(len(list_coCrts_caseNos)) + '\n')




#### THEMIS SEARCH #############################################################

with requests.Session() as s:
	p = s.post(url, data=payload)
	p2 = s.get(get_url + str(now_milliseconds()) + '&last_name=' + input_last_name + '&first_name=' + input_first_name + '&dob=' + input_DOB)
	searchHTML = bs4.BeautifulSoup(p2.text, "html.parser")
	list_caseNos = searchHTML.select('a')
	list_nxtCourtDates = searchHTML.select('#ContentWrapper td')

	f.write("\nTHEMIS\nOpen Cases\n")
	print("Searching Themis for " + str(int(len(list_nxtCourtDates) / 10)) + " listed cases")
	for k in range(len(list_nxtCourtDates)):
		if (k + 4) % 10 == 0:	# checking every 7th td in the row
			if list_nxtCourtDates[k].getText().strip():
				f.write(list_nxtCourtDates[k - 6].getText().strip() + " - " + list_nxtCourtDates[k].getText().strip() + '\n')
	f.write("\nConvictions\n")

	for caseNo in tqdm(list_caseNos): # tqdm is progress bar
		p3 = s.get(casesearch_url + caseNo.getText() + '&_' + str(now_milliseconds()))
		# print(p3.text)
		searchHTML = bs4.BeautifulSoup(p3.text, "html.parser")
		list_convictions = searchHTML.select('#p_gen_offense td')
		counted_FTAs_Before = False # a variable to check if we've counted FTAs for this case number before
		for index in range(len(list_convictions)):
			if "GUILTY" in list_convictions[index].getText():
				if counted_FTAs_Before == False:
					str_toWrite += caseNo.getText() + " -- "
				else:
					str_toWrite += caseNo.getText() + "*-- "
				str_toWrite += abbre_dict.get(list_convictions[index - 2].getText().strip().lower(), list_convictions[index - 2].getText().strip().lower())
				if counted_FTAs_Before == False: # check for additional info only if this is the first offense for the casenumber
					list_sentence = searchHTML.select('#p_gen_sentence td')
					for i in range(len(list_sentence)):
						if "PROBATION" in list_sentence[i].getText() and "TERMS" not in list_sentence[i].getText() and "JOURNAL" not in list_sentence[i].getText():
							str_toWrite += " -- " + abbre_dict.get(list_sentence[i].getText().strip().lower(), list_sentence[i].getText().strip().lower()) + " " + list_sentence[i + 1].getText().strip() + " " + list_sentence[i + 2].getText().strip().lower() + " " + list_sentence[i + 4].getText().strip().lower() + list_sentence[i - 1].getText().strip()
						if "JAIL" in list_sentence[i].getText() and "CONCURRENT" not in list_sentence[i].getText():
							str_toWrite += " -- " + abbre_dict.get(list_sentence[i].getText().strip().lower(), list_sentence[i].getText().strip().lower()) + " " + list_sentence[i + 1].getText().strip() + " " + list_sentence[i + 2].getText().strip().lower() + " " + list_sentence[i + 4].getText().strip().lower() + list_sentence[i - 1].getText().strip()
					list_actions = searchHTML.select('#p_gen_actions td')
					FTAd_before = False  # bool to make sure we format FTAs to the far right only on the first FTA
					for j in range(len(list_actions)):
						if "FTA" in list_actions[j].getText() and "JUDGE" not in list_actions[j].getText():
							if FTAd_before == False and counted_FTAs_Before == False: # tab a bunch of times only on the first FTA for this case no
								str_toWrite += '\t\t\t\t'
							count_FTA += 1
							str_toWrite += " -- FTAd on " + list_actions[j - 4].getText().strip() # D's CAN have multiple FTAs for one case
							FTAd_before = True
				str_toWrite += '\n' # make sure newline by end
				list_toWrite.append(str_toWrite)
				counted_FTAs_Before = True # counted all case numbers
				str_toWrite = "" # clean out the string once done
		if bool_Emergency ==  False:
			time.sleep(2.0) # BE POLITE TO SCRAPED SERVER

	list_toWrite = sorted(list_toWrite) # , then Sort the list
	for stg_Element in list_toWrite:
		f.write(stg_Element)
	f.write("\nNumber of Cases in Themis: " + str(int(len(list_nxtCourtDates) / 10)))
	f.write("\nFailures to Appear: " + str(count_FTA))
	f.close()
	subprocess.call(['C:\\windows\\system32\\notepad.exe', 'C:\\Users\\XXXXXX\\Downloads\\defendant.txt'])
