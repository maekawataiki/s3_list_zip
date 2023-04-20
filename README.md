# S3 List Zip

List content of zip archive in S3.

## usage
### command line
```
$ python listzip.py s3://<bucket>/<key>

usage: listzip.py path

required arguments:
  path                 example s3://mybucket/archive.zip

```

## Demo

```
$ ls archive.zip
archive.zip

$ unzip -Z archive.zip
Archive:  archive.zip
Zip file size: 306 bytes, number of entries: 2
-rw-r--r--  3.0 unx        0 bx stor 23-Apr-20 10:34 aaa.txt
-rw-r--r--  3.0 unx        0 bx stor 23-Apr-20 10:34 bbb.txt
2 files, 0 bytes uncompressed, 0 bytes compressed:  0.0%

$ aws s3 cp archive.zip s3://mybucket/archive.zip
$ aws s3 ls s3://mybucket/archive.zip
2023-04-20 10:35:41        306 archive.zip

$ python listzip.py s3://mybucket/archive.zip
aaa.txt
bbb.txt
```