# NOTE: when running the example, it must be run with root privileges in order to access the USB device.
# If you receive errors when installing the aduhid Python module on Linux, check that udev is installed (on Debian/Ubuntu: sudo apt-get install libudev1 libudev-dev)
import hid

VENDOR_ID = 0x0a07 # OnTrak Control Systems Inc. vendor ID
PRODUCT_ID = 200 # ADU200 Device product name - change this to match your product

def write_to_adu(dev, msg_str):
    print('Writing command: {}'.format(msg_str))

    # message structure:
    #   message is an ASCII string containing the command
    #   8 bytes in length
    #   0th byte must always be 0x01 (decimal 1)
    #   bytes 1 to 7 are ASCII character values representing the command
    #   remainder of message is padded to 8 bytes with character code 0

    byte_str = chr(0x01) + msg_str + chr(0) * max(7 - len(msg_str), 0)

    try:
        num_bytes_written = dev.write(byte_str.encode())
    except IOError as e:
        print ('Error writing command: {}'.format(e))
        return None 

    return num_bytes_written

def read_from_adu(dev, timeout):
    try:
        # read a maximum of 8 bytes from the device, with a user specified timeout
        data = dev.read(8, timeout)
    except IOError as e:
        print ('Error reading response: {}'.format(e))
        return None

    byte_str = ''.join(chr(n) for n in data[1:]) # construct a string out of the read values, starting from the 2nd byte

    result_str = byte_str.split('\x00',1)[0] # remove the trailing null '\x00' characters

    if len(result_str) == 0:
        return None

    return result_str 

# Uncomment if you wish to print out information related to connected ADU devices
# print('Connected ADU devices:')
# for d in hid.enumerate(VENDOR_ID):
#     print('    Product ID: {}'.format(d['product_id']))
# print('')

try:
    device = hid.device()
    device.open(VENDOR_ID, PRODUCT_ID)
    print('Connected to ADU{}\n'.format(PRODUCT_ID))

    bytes_written = write_to_adu(device, 'RK0') # set relay 0, note: device does not send a response for this
    bytes_written = write_to_adu(device, 'SK0') # reset relay 0

    bytes_written = write_to_adu(device, 'RPA') # request the status of PORT A in binary format

    data = read_from_adu(device, 200) # read the response from above PA request
    if data != None:
        print('Received string: {}'.format(data))
        # data_int = int(data) # if you wish to work with the data in integer format
        # print( 'Received int: {}'.format(data_int))

    device.close()
except IOError as e:
    print(e)
    print('Verify that the device has the proper PRODUCT_ID defined as is currently connected.')
    print('Your device should appear in the enumeration printout. Please use a product number from that list.')

