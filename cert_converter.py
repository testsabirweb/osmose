from OpenSSL.crypto import *

passwd = 'password'
p12 = load_pkcs12(open("C:\\Users\\shantanu.dhiman\\Desktop\\Serene IT\\Osmose\\Certificates\\self-cert.pfx", 'rb').read(), passwd)

# If you don't have a password, un-comment the below this:
# p12 = load_pkcs12(open('C:\\Users\\shantanu.dhiman\\Desktop\\Serene IT\\Osmose\\Certificates\\self-cert.pfx', 'rb').read())
pkey = p12.get_privatekey()
open('C:\\Users\\shantanu.dhiman\\Desktop\\Serene IT\\Osmose\\Certificates\\pkey.pem', 'wb').write(dump_privatekey(FILETYPE_PEM, pkey))
cert = p12.get_certificate()
open('C:\\Users\\shantanu.dhiman\\Desktop\\Serene IT\\Osmose\\Certificates\\cert.pem', 'wb').write(dump_certificate(FILETYPE_PEM, cert))
