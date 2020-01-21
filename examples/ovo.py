import json
import os
import argparse

try:
    from OvoAPI import(Client, __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from OvoAPI import(
        Client, __version__ as client_version)


if __name__ == '__main__':

    phone_number = '' #example +6281213031087


    print('Client version: {0!s}'.format(client_version))

    api = Client(phone_number)

    #  Example command:
    #  python examples/example.py
    # result = api.login()
    # result = api.verify(otp='9731', ref_id='17c7245f5c714c358d6293878b291d48')
    # result = api.verify_security_code(security_code=12345, update_access_token='213cd0b7747f4c4a8f82a65330da980c')



    print(result)
    

    print('All ok')


