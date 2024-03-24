import database_methods
import datetime
import requests

server_url = "http://localhost:8080" #change to the IP address of the server

#The following tests are for the test suite for project 2

def file_name_check():
    file = database_methods.get_bd_filename() #get the file name
    assert file == "totally_not_my_privateKeys.db" #check if the file name is correct
    result = True #set the result to true
    return result #return the result

def table_schema_check():
    result = database_methods.table_schema_check() #check the table schema
    assert result[0] != None #check if the first column is not null
    assert result[1] != None #check if the second column is not null
    assert result[2] != None #check if the third column is not null
    result = True #set the result to true
    return result #return the result

def test_create_private_test_key():
    key = database_methods.create_private_test_key() #create a test key
    date = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) #set the date to the epoch
    time_since = datetime.datetime.now(datetime.timezone.utc) - date #get the time since the epoch
    seconds = int(time_since.total_seconds()) #convert the time since the epoch to seconds
    assert key[1] > seconds #check if the key is unexpired
    result = True #set the result to true
    return result #return the result

def expired_key_check():
    key = database_methods.create_expired_test_key() #create an expired key
    date = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) #set the date to the epoch
    time_since = datetime.datetime.now(datetime.timezone.utc) - date #get the time since the epoch
    seconds = int(time_since.total_seconds()) #convert the time since the epoch to seconds
    assert key[1] < seconds #check if the key is expired
    result = True #set the result to true
    return result #return the result

def JWT_check():
    response = requests.get(server_url + "/.well-known/jwks.json") #get the JWKS
    if response.status_code == 200: #check if the response is 200
        result = True #set the result to true
    return result #return the result

def JWKS_get():
    response = requests.post(server_url + "/auth") #post to the server
    if response.status_code == 200: #check if the response is 200
        result = True #set the result to true
    return result #return the result

#the following tests are for manual testing purposes as the server was being developed and are not run by the test suite

def test_create_expired_test_key():
    key = database_methods.create_expired_test_key() #create an expired key
    assert key[1] < datetime.datetime.now(datetime.UTC) #check if the key is expired
    print ("Running test_create_expired_test_key") #print the results
    print ("PEM: ") #print the PEM
    print (key[0]) #print the PEM
    print ("Expiration: ") #print the expiration
    print (key[1]) #print the expiration
    print ("End test_create_expired_test_key") #end the test

def test_save_and_get_db():
    key = database_methods.create_private_test_key() #create a test key
    database_methods.save_private_key_to_db(key[0], key[1]) #save the test key to the database
    result = database_methods.get_private_key_from_db() #get the test key from the database
    print ("Running test_save_and_get_db") #print the results
    print ("PEM: ") #print the PEM
    print (result[0]) #print the PEM
    print ("Expiration: ") #print the expiration
    print (result[1]) #print the expiration
    print ("Kid: ") #print the kid
    print (result[2]) #print the kid
    print ("End test_save_and_get_db") #end the test

def test_get_unexpired_keys():
    key = database_methods.create_private_test_key() #create a test key
    key2 = database_methods.create_private_test_key() #create a test key
    expkey1 = database_methods.create_expired_test_key() #create an expired test key
    expkey2 = database_methods.create_expired_test_key() #create an expired test key
    database_methods.save_private_key_to_db(key[0], key[1]) #save the test key to the database
    database_methods.save_private_key_to_db(key2[0], key2[1]) #save the test key to the database
    database_methods.save_private_key_to_db(expkey1[0], expkey1[1]) #save the expired test key to the database
    database_methods.save_private_key_to_db(expkey2[0], expkey2[1]) #save the expired test key to the database
    result = database_methods.get_unexpired_keys() #get the unexpired keys from the database
    print ("Running test_get_unexpired_keys") #print the results
    for row in result: #for each row in the result
        print(row[0]) #print the PEM 
    for row in result: #for each row in the result
        print(row[1]) #print the expiration
    for row in result: #for each row in the result  
        print(row[2]) #print the kid
    print ("End test_get_unexpired_keys") #end the test

#The following code runs the test suite

if __name__ == "__main__":
    total_tests = 6 #total number of tests
    passed_tests = 0 #number of tests passed
    print("Running tests for Brian Vaughn's project 2 test suite...") #print that the tests are starting

    test1 = file_name_check() #run the file name check test
    print ("Checking file name") #print the results
    if test1 == True: #if the test passes
        print ("File name is correct") #print that the file name is correct
        passed_tests += 1 #increment the number of tests passed

    test2 = table_schema_check() #run the table schema check test
    print ("Checking table schema") #print the results
    if test2 == True: #if the test passes
        print ("Table schema is correct") #print that the table schema is correct
        passed_tests += 1 #increment the number of tests passed

    test3 = test_create_private_test_key() #run the create private test key test
    print ("Checking if the database methods can create an unexpired key") #print the results
    if test3 == True: #if the test passes
        print ("Key is unexpired") #print that the key is unexpired
        passed_tests += 1 #increment the number of tests passed

    test4 = expired_key_check() #run the expired key check test
    print ("Checking if the database methods can create an expired key") #print the results
    if test4 == True: #if the test passes
        print ("Key is expired") #print that the key is expired
        passed_tests += 1 #increment the number of tests passed

    test5 = JWT_check() #run the JWT check test
    print ("Checking if the server can return a JWT") #print the results
    if test5 == True: #if the test passes
        print ("Server returned a JWT") #print that the server returned a JWT
        passed_tests += 1 #increment the number of tests passed

    test6 = JWKS_get() #run the JWKS get test
    print ("Checking if the server can return JWKS") #print the results
    if test6 == True: #if the test passes
        print ("Server returned JWKS") #print that the server returned JWKS
        passed_tests += 1 #increment the number of tests passed
    
    print("Passed " + str(passed_tests) + " out of " + str(total_tests) + " tests.") #print the number of tests passed
    print("Coverage Percent:" + str((passed_tests/total_tests)*100) + "%" ) #print the coverage percentage
    if passed_tests == total_tests: #if all tests pass
        print("All tests for Brian Vaughn's project 2 functions have passed!") #print that all tests have passed