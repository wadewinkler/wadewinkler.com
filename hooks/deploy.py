import os
from datetime import datetime, timedelta
from time import mktime
from wsgiref.handlers import format_date_time
import logging

import yaml


def deploy(site):
    print 'site', site
    output='output'
    with open('deploy.yaml') as config:
        deploy_config = yaml.load(config)

        if deploy_config['deploy_target'] == 'ftp':
            deploy_to_ftp(
                server=deploy_config['server'],
                username=deploy_config['username'],
                password=deploy_config['password'],
                base=deploy_config['base'],
                output_folder=output,
            )

        if deploy_config['deploy_target'] == 's3':

            deploy_to_s3(
                bucket_name=deploy_config['s3_bucket'],
                access=deploy_config['s3_access_key'],
                secret=deploy_config['s3_secret_key'],
                output_folder=output,
                cache=deploy_config['cache'],
                expires=deploy_config['expires'],
            )


def deploy_to_s3(bucket_name, access, secret, output_folder, cache=False, expires=False):

    # S3 Connection
    try:
        from boto.s3.connection import S3Connection
    except ImportError:
        logging.info('boto library needed for deployment to Amazon S3')
        return

    conn = S3Connection(access,secret)
    bucket = conn.get_bucket(bucket_name)

    for path, dirnames, filenames in os.walk(output_folder):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()[1:]
            filepath=os.path.join(path,filename)
            relpath = os.path.relpath(filepath,output_folder)
            key = bucket.get_key(relpath) or bucket.new_key(relpath)

            with open(filepath) as fp:
                if key.etag and key.etag.strip('"') == key.compute_md5(fp)[0]:
                    print "file %s already in s3" % relpath
                    continue

            if cache and ext in cache.keys():
                headers = {
                    'Cache-Control': 'max-age=%d, public' % cache[ext],
                    'Expires': format_date_time(mktime((datetime.now()+timedelta(expires)).timetuple()))
                }
            else:
                headers = {}
            key.set_contents_from_filename(filepath,headers)
            print "uploaded %s to s3" % relpath


def deploy_to_ftp(server,username,password,base,output_folder):

    import ftplib

    def upload(ftp, file):
        ftp.storbinary("STOR " + os.path.basename(file), open(file, "rb"), 1024)

    ftp = ftplib.FTP(server,username,password)
    home = ftp.pwd()
    for path, dirnames, filenames in os.walk(output_folder):
        ftp.cwd(home)
        ftppath=os.path.join(base,os.path.relpath(path,'output'))
        try:
            ftp.cwd(ftppath)
        except ftplib.error_perm:
            ftp.mkd(ftppath)
            ftp.cwd(ftppath)
        for filename in filenames:
            upload(ftp, os.path.join(path,filename))


