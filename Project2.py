from http.server import BaseHTTPRequestHandler, HTTPServer
from Crypto.PublicKey import RSA
from urllib.parse import urlparse, parse_qs
import base64
import json
import jwt
import datetime
import sqlite3
import database_methods

host_name = "localhost" # change to IP address of server
port_num = 8080 # change to port number of server

def convert_int_to_base64(int_value): 
    hex_value = format(int_value, 'x') # convert to hex
    if len(hex_value) % 2 == 1: # if odd number of characters, add a leading 0
        hex_value = '0' + hex_value # add leading 0
    byte_value = bytes.fromhex(hex_value) # convert to bytes
    enc = base64.urlsafe_b64encode(byte_value).rstrip(b'=') # convert to base64
    return enc.decode('utf-8') # convert to string

database_methods.create_database() # create the database
key1 = database_methods.create_private_test_key() # create a test key
expkey1 = database_methods.create_expired_test_key() # create an expired test key
database_methods.save_private_key_to_db(key1[0], key1[1]) # save the test key to the database
database_methods.save_private_key_to_db(expkey1[0], expkey1[1]) # save the expired test key to the database

class Server(BaseHTTPRequestHandler): 
    def do_GET(self): 
        if self.path == "/.well-known/jwks.json": # if the path is /.well-known/jwks.json
            self.send_response(200) # send a 200 OK response
            self.send_header("Content-type", "application/json") # send the content type header
            keys = database_methods.get_unexpired_keys() # get the unexpired keys from the database
            issued_keys = {
                "keys": [

                        ] # create a dictionary to store the keys
                         } # create a dictionary to store the keys
            for key in keys: # for each key
                RSA_key = RSA.import_key(key[0]) # import the key
                kid_data = key[2] # get the key ID
                kid_string = str(kid_data) # convert the key ID to a string
                modulus = RSA_key.n # get the modulus
                exponent = RSA_key.e # get the exponent
                header = { 
                            "alg": "RS256", # create the algorithm in header
                            "kty": "RSA", # create the key type in header
                            "use": "sig", # create the use value in header
                            "kid": kid_string, # create the key ID in header
                            "n": base64.urlsafe_b64encode(modulus.to_bytes((modulus.bit_length() + 7) // 8, byteorder='big')).decode(), # create the n value in header
                            "e": base64.urlsafe_b64encode(exponent.to_bytes((exponent.bit_length() + 7) // 8, byteorder='big')).decode(),  # create the e value in header
                        } # create the header
                issued_keys["keys"].append(header) # append the header to the keys dictionary
            self.end_headers() # end the headers
            self.wfile.write(bytes(json.dumps(issued_keys), "utf-8")) # write the keys to the response
            return

        self.send_response(405) # send a 405 Method Not Allowed response
        self.end_headers() # end the headers
        return

    def do_POST(self):
        path = urlparse(self.path) # parse the path
        parameters = parse_qs(path.query) # parse the query string
        if path.path == "/auth": # if the path is /auth
            exp_key = database_methods.get_private_key_from_db(expired=False) # get the unexpired key from the database
            if 'expired' in parameters: # if the expired parameter is in the query string
                exp_key = database_methods.get_private_key_from_db(expired=True) # get the expired key from the database
                kid_data = exp_key[2] # get the key ID
                kid_string = str(kid_data) # convert the key ID to a string
                header = {
                    "kid": kid_string # create the key ID in header
                } # create the header

                payload = {
                "user": "username", # create the payload
                "exp": exp_key[1] # create the payload
                } # create the payload
            else:
                exp_key = database_methods.get_private_key_from_db(expired=False) # get the unexpired key from the database
                kid_data = exp_key[2] # get the key ID
                kid_string = str(kid_data)  # convert the key ID to a string
                header = {
                    "kid": kid_string # create the key ID in header
                } # create the header
                payload = {
                "user": "username", # create the payload
                "exp": exp_key[1] # create the payload
                } # create the payload
            pem = exp_key[0] # get the key
            ej = jwt.encode(payload, pem, algorithm="RS256", headers=header) # encode the payload
            self.send_response(200) # send a 200 OK response
            self.end_headers() # end the headers
            self.wfile.write(bytes(ej, "utf-8")) # write the encoded payload to the response
            return
        
        self.send_response(405) # send a 405 Method Not Allowed response
        self.end_headers() # end the headers
        return 

if __name__ == "__main__":
    server = HTTPServer((host_name, port_num), Server) # create the server
    try: # try to run the server
        server.serve_forever() # run the server
    except KeyboardInterrupt: # if the server is interrupted
        pass # do nothing
    server.server_close() # close the server
