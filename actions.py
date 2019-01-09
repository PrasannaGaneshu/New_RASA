from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from rasa_core.agent import Agent
from pymongo import MongoClient
#===================API KEYS=============================
goog_api_key = 'AIzaSyBxxrPmnsEdulz7tVLY6PR8rKtZeOMRNWo'
openweather_api_key = 'ada46595eac2c9447738e2ba95f0bd2d'
#========================================================

import json
import requests
import urllib.request
import datetime
import urllib3
from datetime import datetime

client = MongoClient('10.50.72.77', 27018) # OFFICE CONNECT WITH PORT
db = client.convai

res=[]
http=urllib3.PoolManager()
data_list=[]
upcoming_list=[]
sr_list=[]
dmp_list=[]

iMob_API_1 = "10.158.2.81:7005/amaze/rest/api/"
iMob_API_3 = "?RRN=123123&CHANNEL=abc&MOBILE=1234567890&USERID="


#=======================================================
#         1.0--GET WEATHER 
#=======================================================
class ActionWeather(Action):
	def name(self):
		return 'action_weather'
		
	def run(self, dispatcher, tracker, domain):
		weat_loc = tracker.get_slot('location');
		owm_url = 'https://api.openweathermap.org/data/2.5/weather?units=metric'
		if ( weat_loc == 'default'):
			cursor = db.cva_user_loc.find({"userid":"shreeramuniq139"}).sort("epochdatetime", -1).limit(1);
			rev_geo_url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='+ str(cursor[0]['lat']) + ',' + str(cursor[0]['lon']) + '&key=AIzaSyBxxrPmnsEdulz7tVLY6PR8rKtZeOMRNWo';
			rev_geo_req = requests.get(rev_geo_url);
			rev_geo_response = rev_geo_req.json();
			rev_geo_comp_code = rev_geo_response['plus_code']['compound_code']
			weat_loc = (rev_geo_comp_code.split(",")[0]).split(" ",1)[1]
			
		owm_param = {'q':weat_loc,'appid':openweather_api_key}
		owm_request = requests.get(owm_url,params=owm_param)
		owm_response = owm_request.json()
		response = "Temperature currently is " + str(owm_response['main']['temp']) + " degree celsius. You can expect " + str(owm_response['weather'][0]['description'])
		dispatcher.utter_message("^GETWET^~" + weat_loc + "~" + response)
		return [SlotSet('location',weat_loc), SlotSet('pickup_location',weat_loc)]


#=======================================================
#         2.0 -- SEARCH RESTAURANT
#=======================================================
class ActionGetRestaurant(Action):
	def name(self):
		return 'action_restaurant'
     
	def run(self, dispatcher, tracker, domain):
		res_loc = tracker.get_slot('location')
		res_cuisine = tracker.get_slot('cuisine')

		if ( res_loc == 'default' ):
			cursor = db.cva_user_loc.find({"userid":"shreeramuniq139"}).sort("epochdatetime", -1).limit(1);
			lat_long = str(cursor[0]['lat']) + ',' + str(cursor[0]['lon'])
			rev_geo_url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='+ lat_long + '&key=AIzaSyBxxrPmnsEdulz7tVLY6PR8rKtZeOMRNWo';
			rev_geo_req = requests.get(rev_geo_url);
			rev_geo_response = rev_geo_req.json();
			rev_geo_comp_code = rev_geo_response['plus_code']['compound_code']
			res_loc = (rev_geo_comp_code.split(",")[0]).split(" ",1)[1]
			
		elif ( res_loc != 'default' ):
			geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
			geocode_params = {'address': res_loc, 'key':goog_api_key}
			geocode_req = requests.get(geocode_url, params=geocode_params)
			geocode_response = geocode_req.json()   
			geodata = dict()
			geocode_result = geocode_response['results'][0]
			geodata['lat'] = geocode_result['geometry']['location']['lat']
			geodata['lon'] = geocode_result['geometry']['location']['lng']
			lat_long = str('{lat}, {lon}'.format(**geodata))
			
		goog_place_param = {'type':'restaurant', 'key':goog_api_key, 'location':lat_long,'radius':1000}
		goog_place_url='https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
		goog_request= requests.get(goog_place_url, params=goog_place_param)
		goog_response = goog_request.json()
		restlist=[]
		for i in goog_response['results'][:5]: 
			restlist.append(json.dumps({"rest_id":i['id'],"name":i['name'],"addr":i['vicinity']}))
		dispatcher.utter_message("^GETRES^~" + res_loc + "~" + str(restlist))            
		return[SlotSet('location',res_loc)]		
		

#=========================================================
#  	  3.0 -- CAPTURE USER ID
#=========================================================
class ActionCaptureUserID(Action):
	def name(self):
		return 'action_storeuseid'
		
	def run(self, dispatcher, tracker, domain):
		juser_id = tracker.get_slot('user_id')
		ucuser = juser_id.upper();
		user_id = ucuser.replace('LLLLLLLLLLLL0000000000000>','')
		return[SlotSet('user_id',user_id), SlotSet('SR_flag', 'firstimenothing'),SlotSet('location', 'default'), SlotSet('drop_location','default'), SlotSet('pickup_location','default')]
		
#=========================================================
#  	  3.0 -- FALL BACK
#=========================================================		
class ActionDefaultFallback(Action):
    def name(self):
        return 'action_default_fallback'

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("I did not get that")

#=======================================================
class ActionResetSRslot(Action):
    def name(self):
        return 'action_reset_sr'

    def run(self, dispatcher, tracker, domain):
        return[SlotSet('SR_flag','firstimenothing'),SlotSet('ccblock_flag','nothing'),SlotSet('ccunblock_flag','nothing')]
				

#==============================================================================================
#     13.0 -- GOING OUT
#===========================================================================================
class ActionGoingOut(Action):
	def name(self):
		return 'action_goingout'
	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message("^GOINGOUT^~")	        
        
#==============================================================================================
#     12.0 -- SHOW MENU
#===========================================================================================
class ActionShowMenu(Action):
	def name(self):
		return 'action_showmenu'
	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message("^SHOWMENU^~")	
        
#==============================================================================================
#     11.0 -- CAN I AFFORD
#===========================================================================================
class ActionCanIAfford(Action):
	def name(self):
		return 'action_caniafford'
	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message("^CANIAFFORD^~")	
#========================================================
#      10.0--CHECK BOOK REQUEST
#========================================================

class ActionCheckbookReq(Action):
	def name(self):
		return 'action_getcheckbook'

	def run(self, dispatcher, tracker, domain):
		juser_id = tracker.get_slot('user_id')
		ucuser = juser_id.upper();
		user_id = ucuser.replace('LLLLLLLLLLLL0000000000000>','')
		user_id_upper = user_id.upper()
		SR_flag = tracker.get_slot('SR_flag')
		if(SR_flag == "firstimenothing"):
			info = db.rasa_account_det.find_one({"USER_ID":user_id_upper})
			unused_leaves = info['UNUSED_LVS']
			if(info != '(None)'):
				if (unused_leaves != '(None)'):
					if (unused_leaves <=6):
						dispatcher.utter_message("^GETCHKBK^~You have only " +str(info['UNUSED_LVS']) + " leaves left. Can I go ahead & create a request?")
					elif unused_leaves >6:
						dispatcher.utter_message("^GETCHKBK^~You already have " + str(info['UNUSED_LVS'])+" unused leaves. Do you still want to apply?")
			elif (unused_leaves == '(None)'):
				dispatcher.utter_message("^GETCHKBK^~Will raise an SR for checkbook. You can track the same from iMobile App. Can I go ahead?")
			SR_flag = "cheque book"
		elif(SR_flag == "cheque book"):
			dispatcher.utter_message("^GETCHKBK^~SR12345678 for "+SR_flag+" request has been raised. You can track the status directly from iMobile App")
			SR_flag ="firstimenothing"
		return [SlotSet('user_id',user_id), SlotSet('SR_flag',SR_flag)]


#===============================================================================================
#               9.0--UPCOMING EXPENSES
#===============================================================================================
class ActionGetUpcomingExpense(Action):
	def name(self):
		return 'action_upcomingexpense'
		
	def run(self, dispatcher, tracker, domain):
		juser_id = tracker.get_slot('user_id')
		ucuser = juser_id.upper();
		user_id = ucuser.replace('LLLLLLLLLLLL0000000000000>','')
		dispatcher.utter_message("^UPCMNG^~")
		return[SlotSet('user_id',user_id)]

#=====================================================================================================


##-------------------------------------------------------------------------------------------
#			8.0-- ACCOUNT BALANCE
##--------------------------------------------------------------------------------------------
class ActionGetBalance(Action):
	def name(self):
		return 'action_accntbal'
		
	def run(self, dispatcher, tracker, domain):
		user_id = tracker.get_slot('user_id')
		user_id_upper = user_id.upper()
		info = db.rasa_account_det.find_one({"$and":[{"USER_ID":user_id_upper},{"OUTSTANDING_AMOUNT":{"$ne":"(null)"}}]})
		print("=========",info)
		dispatcher.utter_message("^GETEODBAL^~Your current balance is INR."+str(info['OUTSTANDING_AMOUNT']))
		#dispatcher.utter_message("^GETEODBAL~^Your current balance is INR.")

##-------------------------------------------------------------------------------------------
#			7.0-- CC OUTSTANDING
##--------------------------------------------------------------------------------------------
class ActionCCOutstanding(Action):
	def name(self):
		return 'action_ccoutstanding'
		
	def run(self, dispatcher, tracker, domain):
		user_id = tracker.get_slot('user_id')
		card_num = tracker.get_slot('card_num')
		user_id_upper = user_id.upper()
		info = db.rasa_account_det.find_one({"$and":[{"USER_ID":user_id_upper}]})

		print(".....", info['CARD_OUTSTANDING_AMOUNT'], ".......", info['OUTSTANDING_AMOUNT'])
		if info['ACCOUNT_CARD_NBR'] == "(null)":
		    dispatcher.utter_message("^GETCCOUT^~Hmmm.. I'm not seeing a credit card linked to your account. Why don't you apply for one!")
		elif (info['CARD_OUTSTANDING_AMOUNT'] == "(null)" or int(info['CARD_OUTSTANDING_AMOUNT']) == 0):
		    dispatcher.utter_message("^GETCCOUT^~Looks like you've paid of your latest statement. I'm not seeing an outstanding amount for your card "+str(info['ACCOUNT_CARD_NBR']))
		else:
		    dispatcher.utter_message("^GETCCOUT^~Your outstanding amount for the card "+str(info['ACCOUNT_CARD_NBR'])+" is INR."+str(info['CARD_OUTSTANDING_AMOUNT'])+". And your due date for payment is "+str(str(info['CARD_EMI_STATEMENT_DT']).split()[0]))

#===============================================================================================
#              6.0 -- SR & DELIVERABLES
#===============================================================================================
class ActionGetSRDeliveryStatus(Action):
	def name(self):
		return 'action_srdeliverables'
     
	def run(self,dispatcher, tracker, domain):
		srordmp = str(tracker.get_slot('srdmp'))
		juser_id = tracker.get_slot('user_id')
		ucuser = juser_id.upper();
		user_id = ucuser.replace('LLLLLLLLLLLL0000000000000>','')
		url = iMob_API_1 + "getSRStatus" + iMob_API_3 + user_id
		print(url)
		try:
			data= http.request('GET', url)
			datajson_dict = json.loads(data.data.decode('UTF-8'))
			j=0
			if int(datajson_dict['STATUS'])==200:
				k = len(datajson_dict['SR_DELIVERABLE']['SR'])
				#l = len(datajson_dict['SR_DELIVERABLE']['DMP'])
				if(k):
					for i in datajson_dict['SR_DELIVERABLE']['SR']:
						if j<k:
							#sr_list.append(((j+1),i['TRACKING_NUMBER'],i['REQUEST_DESC'],str(i['STATUS']),str(i['TARGET_CLOSE_DATE']),"SR"))
							sr_list.append( json.dumps({"ID":(j+1), "TRACKING_NUMBER":i['TRACKING_NUMBER'], "REQUEST_DESC":i['REQUEST_DESC'], "STATUS":str(i['STATUS']), "TARGET_CLOSE_DATE":str(i['TARGET_CLOSE_DATE']),"SR":"SR" }) )
							j = j+1
				# if(l):
					# for i in datajson_dict['SR_DELIVERABLE']['DMP']:
						# if j<l:
							# dmp_list.append(((j+1),i['TRACKING_NUMBER'],i['REQUEST_DESC'],str(i['STATUS']),str(i['TARGET_CLOSE_DATE']),"DMP"))
							# j = j+1
				print("==========IF PART===================")
				dispatcher.utter_message("^GETSRDEL^~" + str(sr_list))
				#dispatcher.utter_message("^GETSRDEL^~" + "\n".join(map(str,dmp_list)))
			elif int(datajson_dict['STATUS'])==500:
				print("ELSE PART===================")
				dispatcher.utter_message("^GERSRDEL^~There are no active SRs or Deliverables ")
		except UrlNotAccessible as e:
			dispatcher.utter_message("Not able to access the getSRStatus API. Error: {}. Request content: '{}' ".format(e, content))
		sr_list.clear()
		dmp_list.clear()
		return[SlotSet('user_id',user_id)]



#==============================================================================================
#     3.0 -- BOOK CAB
#===========================================================================================

class ActionBookCab(Action):
	def name(self):
		return 'action_getcab'
     
	def run(self, dispatcher, tracker, domain):
		pick_loc = tracker.get_slot('pickup_location')
		drop_loc = tracker.get_slot('drop_location')
		ifcabbooked = tracker.get_slot('ifcabbooked')
		juser_id = tracker.get_slot('user_id')
		print(pick_loc," , ", drop_loc," , ", ifcabbooked, " , ")
		print(juser_id)
		ucuser = juser_id.upper();
		user_id = ucuser.replace('LLLLLLLLLLLL0000000000000>','')
		dispatcher.utter_message("^GETCAB^~"+pick_loc+"~"+drop_loc+"~Your cab from " + pick_loc+" to "+drop_loc+ " is booked. You can track it in your App")
		return[SlotSet('pickup_location',pick_loc),SlotSet('drop_location',drop_loc),SlotSet('ifcabbooked',True),SlotSet('user_id',user_id),SlotSet('bkd_pickup_location',pick_loc),SlotSet('bkd_drop_location',drop_loc)]

#==============================================================================================
#     2.0 -- GET STATEMENTS
#===========================================================================================
class ActionGetStatement(Action):
	def name(self):
		return 'action_getstatement'
	def run(self, dispatcher, tracker, domain):
		datecon = tracker.get_slot('DATE')
		dispatcher.utter_message("^BNKSTM^~" + str(start(str(datecon))))	
		
