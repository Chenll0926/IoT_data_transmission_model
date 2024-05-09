import asyncio
from aiocoap import *
from data_send import Get_data
import os
import threading

# file_path = Get_data.miniute_path['Sleep']
sleep_file = [os.path.join('dataset/sleep', file) for file in os.listdir('dataset/sleep') if file.endswith('.csv')]

def thread_function(file):
    uri = 'coap://100.81.240.82:5683/raspberry'
    asyncio.run(Get_data.coap_send_sleep_data(uri, file))

def main():
    threads = []
    for file in sleep_file:
        thread = threading.Thread(target=thread_function, args=(file, ))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

# async def main():

#     uri = 'coap://100.81.240.82:5683/raspberry'

#     await Get_data.coap_send_sleep_data(uri, file_path)
    

if __name__ == "__main__":
    # asyncio.run(main())
    main()