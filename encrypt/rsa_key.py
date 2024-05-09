from Crypto.PublicKey import RSA

key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

with open('private.pem', 'wb') as pr:
    pr.write(private_key)
with open('public.pem', 'wb') as pu:
    pu.write(public_key)
