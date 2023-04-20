# Acknowledgement:
# This is a command line version of article written by Krzysztof Kwiecinski
# https://betterprogramming.pub/how-to-know-zip-content-without-downloading-it-87a5b30be20a

import boto3
import io
import struct
import zipfile
import argparse

s3 = boto3.client('s3')

EOCD_RECORD_SIZE = 22
ZIP64_EOCD_RECORD_SIZE = 56
ZIP64_EOCD_LOCATOR_SIZE = 20

MAX_STANDARD_ZIP_SIZE = 4_294_967_295

def view_zip(event):
    bucket = event['bucket']
    key = event['key']
    zip_file = get_zip_file(bucket, key)
    print_zip_content(zip_file)

def get_zip_file(bucket, key):
    file_size = get_file_size(bucket, key)
    eocd_record = fetch(bucket, key, file_size - EOCD_RECORD_SIZE, EOCD_RECORD_SIZE)
    if file_size <= MAX_STANDARD_ZIP_SIZE:
        cd_start, cd_size = get_central_directory_metadata_from_eocd(eocd_record)
        central_directory = fetch(bucket, key, cd_start, cd_size)
        return zipfile.ZipFile(io.BytesIO(central_directory + eocd_record))
    else:
        zip64_eocd_record = fetch(bucket, key,
                                  file_size - (EOCD_RECORD_SIZE + ZIP64_EOCD_LOCATOR_SIZE + ZIP64_EOCD_RECORD_SIZE),
                                  ZIP64_EOCD_RECORD_SIZE)
        zip64_eocd_locator = fetch(bucket, key,
                                   file_size - (EOCD_RECORD_SIZE + ZIP64_EOCD_LOCATOR_SIZE),
                                   ZIP64_EOCD_LOCATOR_SIZE)
        cd_start, cd_size = get_central_directory_metadata_from_eocd64(zip64_eocd_record)
        central_directory = fetch(bucket, key, cd_start, cd_size)
        return zipfile.ZipFile(io.BytesIO(central_directory + zip64_eocd_record + zip64_eocd_locator + eocd_record))


def get_file_size(bucket, key):
    head_response = s3.head_object(Bucket=bucket, Key=key)
    return head_response['ContentLength']

def fetch(bucket, key, start, length):
    end = start + length - 1
    response = s3.get_object(Bucket=bucket, Key=key, Range="bytes=%d-%d" % (start, end))
    return response['Body'].read()

def get_central_directory_metadata_from_eocd(eocd):
    cd_size = parse_little_endian_to_int(eocd[12:16])
    cd_start = parse_little_endian_to_int(eocd[16:20])
    return cd_start, cd_size

def get_central_directory_metadata_from_eocd64(eocd64):
    cd_size = parse_little_endian_to_int(eocd64[40:48])
    cd_start = parse_little_endian_to_int(eocd64[48:56])
    return cd_start, cd_size

def parse_little_endian_to_int(little_endian_bytes):
    format_character = "i" if len(little_endian_bytes) == 4 else "q"
    return struct.unpack("<" + format_character, little_endian_bytes)[0]

def print_zip_content(zip_file):
    for zi in zip_file.filelist:
        print(zi.filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=__file__)
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('path', help='example s3://mybucket/archive.zip', type=str)
    args = parser.parse_args()
    path = args.path

    bucket = path[5:].split('/')[0]
    key = '/'.join(path[5:].split('/')[1:])

    view_zip({
        'bucket': bucket, 
        'key': key
        })