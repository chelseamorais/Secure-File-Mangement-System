from Crypto.Cipher import AES

AES_KEY = b'\xc1\xce\x9d\x7f\xbfy\n\xa0\x1f\xe4]\x9b\x0c\xe8D\x04'
AES_NONCE = AES_KEY

"""
Encrypt the plaintext filename, then turn it into unreadable format
to do file lookup
"""
def filename_mapping(plaintext):

    # encrypt filename
    cipher = AES.new(AES_KEY, AES.MODE_EAX, AES_NONCE)
    ciphertext = cipher.encrypt(plaintext.encode('utf-8'))
    
    filename = ""
    for i,n in enumerate(ciphertext):
        if i == 0:
            # str(n): 123 --> "123"
            filename += str(n)
        else:
            filename += "-" + str(n)
    return filename

def filename_unmapping(mapped_filename):
    list_of_str_bytes = mapped_filename.split("-")
    bs = b''
    for str_b in list_of_str_bytes:

        int_b = int(str_b)
        b = int_b.to_bytes(1, "big")
        bs += b

    cipher = AES.new(AES_KEY, AES.MODE_EAX, AES_NONCE)
    plaintext = cipher.decrypt(bs).decode('ISO-8859-1')
    return plaintext


