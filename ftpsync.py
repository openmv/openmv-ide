#!/usr/bin/env python
""" A bidirectional tool to synchronize remote and local directory trees using FTP.

For usage information, run ``ftpsync.py --help``.

Homepage: http://ftpsync2d.googlecode.com
"""
# Author: Pearu Peterson
# Created: April 2008
# License: BSD

__version__ = '1.1-svn'

import sys
import time
import os
import shutil
from urlparse import urlparse
from getpass import getpass
from ftplib import FTP, error_perm
import cPickle as pickle
from cStringIO import StringIO
from optparse import OptionParser
from posixpath import normpath

gtkpresence = None
try:
    import gnomekeyring
    import gtk
    gtkpresence = True
except ImportError:
    pass

trash_dir = '.trash_local'
ftp_trash_dir = '.trash_remote'

def ignore_filename(filename):
    root, ext = os.path.splitext(filename)
    basename = os.path.basename(filename)
    if ext in ['.pyc', '.pyo', '.backup', '.aux'] \
           or ext.endswith('~') or ext.endswith('#') or basename.startswith('.'):
        return True
    return False

def fix_dirs(dirs):
    if 'CVS' in dirs: dirs.remove('CVS')
    if '.svn' in dirs: dirs.remove('.svn')
    if '.bzr' in dirs: dirs.remove('.bzr')
    if trash_dir in dirs: dirs.remove(trash_dir)
    if ftp_trash_dir in dirs: dirs.remove(ftp_trash_dir)

class FtpSession(object):

    def __init__(self, server_url, skip_dirs = []):
        if not server_url.startswith('ftp://'):
            server_url = 'ftp://' + server_url
        o = urlparse(server_url)
        assert o.scheme=='ftp',`o`
        self.server = o.hostname
        self._username = o.username
        self._password = o.password
        remote_path = normpath(o[2] or '/')
        if remote_path.startswith('//'):
            remote_path = remote_path[1:]
        assert remote_path.startswith('/'),`remote_path`
        self.remote_path = remote_path
        self._ftp = None
        self.clock_offset = 0
        self.skip_dirs = skip_dirs or []

    @property
    def server_url(self):
        return 'ftp://%s@%s' % (self.username, self.server, self.remote_path)

    @property
    def username(self):
        n = self._username
        if n is None:
            while 1:
                n = raw_input('Enter username for ftp://%s: ' % (self.server))
                if n:
                    break
            self._username = n
        return n

    @property
    def password(self):
        n = self._password
        if n is None:
            if gtkpresence:
                try:
                    keyring = gnomekeyring.get_default_keyring_sync()
                    keyring_info = gnomekeyring.get_info_sync(keyring)
                    if keyring_info.get_is_locked():
                        nof_tries = 3
                        for i in range(nof_tries):
                            keyring_pass = getpass('Enter password to unlock your default keychain: ')
                            try:
                                gnomekeyring.unlock_sync(keyring, keyring_pass)
                                break
                            except gnomekeyring.DeniedError:
                                if i+1==nof_tries:
                                    sys.stderr.write('\nFailed to unlock keychain (%s times)\n' % (i+1))
                                else:
                                    sys.stderr.write("\nInvalid password, try again...\n")
                    items = gnomekeyring.find_items_sync(gnomekeyring.ITEM_NETWORK_PASSWORD,
                                                         {"server": self.server,
                                                          "protocol": "ftp",
                                                          "user": self.username})
                    if len(items) > 0:
                        n = items[0].secret
                except gnomekeyring.DeniedError:
                    sys.stderr.write("\nGnome keyring error : Access denied ..\n")
                except gnomekeyring.NoMatchError:
                    sys.stderr.write("\nGnome keyring error : No credential for %s..\n" % self.server)
                except Exception, msg:
                    sys.stderr.write("\nGnome keyring error : %s\n" % (msg))
                sys.stderr.flush()
            if n is None:
                n = getpass('Enter password for ftp://%s@%s: ' % (self.username, self.server))
            self._password = n
        return n

    @property
    def ftp(self):
        c = self._ftp
        if c is None:
            sys.stdout.write('<connecting to %s..' % (self.server))
            sys.stdout.flush()
            self._ftp = c = FTP(self.server, self.username, self.password)
            self.clock_offset = self.clocksync()
            sys.stdout.write('clock offset: %s> ' % (self.clock_offset))
            sys.stdout.flush()
        return c

    def abspath(self, *paths):
        filename = os.path.join(*(paths or ('',)))
        if not os.path.isabs(filename):
            filename = os.path.join(self.remote_path, filename)
        return filename

    def get_mtime(self, name):
        """ Return modification time of the file in ftp server.

        If the file does not exist, return None.
        If the name refers to a directory, return 0.

        To get the local modification time, use
        ``get_mtime()-clock_offset``.
        """
        filename = self.abspath(name)
        try:
            resp = self.ftp.sendcmd('MDTM ' + filename.replace('\\', '/'))
        except error_perm, msg:
            s = str(msg)
            if s.startswith('550 I can only retrieve regular files'):
                # filename is directory
                return 0
            if s.startswith('550 Can\'t check for file existence'):
                # file with filename does not exist
                return None
            raise
        assert resp[:3]=='213', `resp, filename`
        modtime = int(time.mktime(time.strptime(resp[3:].strip(), '%Y%m%d%H%M%S')))
        return modtime

    def clocksync(self):
        fn = '.ftpsync.clocksync'
        rfn = self.abspath(fn)
        if not os.path.isfile(fn):
            f = open(fn,'w')
            f.write('temporary file created by ftpsync.py')
            f.close()
        self.makedirs(os.path.dirname(rfn))
        f = open(fn, 'rb')
        self.ftp.storbinary('STOR ' + rfn.replace('\\', '/'), f, 1024)
        f.close()
        local_time1 = time.time()
        remote_time = self.get_mtime(rfn)
        local_time2 = time.time()
        self.ftp.delete(rfn.replace('\\', '/'))
        os.remove(fn)
        if local_time2 < remote_time: # remote is in future
            sync_off = int(remote_time - local_time2)
        elif local_time1 > remote_time: # remote is in past or equal
            sync_off = int(remote_time - local_time1)
        else:
            sync_off = 0
        return sync_off

    def get_listing_map(self, path):
        filename = self.abspath(path, '.listing')
        l = []
        self.ftp.retrbinary('RETR ' + filename.replace('\\', '/'), l.append, 8*1024)
        l = ''.join(l)
        func = lambda fn, mtime: (fn, int(mtime))
        return dict([func(*line.rsplit(':', 1)) for line in l.splitlines()])

    def upload_listing_map(self, path, d):
        filename = self.abspath(path, '.listing')
        fp = StringIO('\n'.join(['%s:%s' % item for item in d.iteritems()]))
        try:
            self.ftp.storbinary('STOR ' + filename.replace('\\', '/'), fp, 8*1024)
        except error_perm:
            return 0
        return 1

    def get_remote_files(self, directory='', verbose=True, listing=True,
                         update_listing=False):
        """ Return a {files:modification times} map of the ftp directory.

        If listing is True then .listing files are used to accelerate
        getting the map information. When .listing file does not exist,
        it will be created.

        When uploading a file or a directory then the uploader is
        responsible for removing .listing file from the parent
        directory of the uploaded file or directory. The .listing file
        should also be removed when removing a file, this is not
        necessary when removing a directory, though.  The above will
        ensure that .listing will be kept up-to-date.

        Note that for directories the modification times is set to 0,
        and for .listing files it is -1, in the returned map. The
        modification time is using the clock in ftp server.

        The paths to files correspond to absolute paths in the ftp
        server.
        """
        r = {}
        dirs = []
        wd = self.abspath(directory)
        if wd in self.skip_dirs:
            return r
        r[wd] = 0 # directories have 0 mtime.
        if verbose:
            sys.stdout.write('listing directory %r ' % (wd))
            sys.stdout.flush()
        lst = filter(lambda n: n not in ['.', '..'], self.ftp.nlst(wd.replace('\\', '/')))
        if verbose:
            sys.stdout.write('[%s items]: ' % (len(lst)))
            sys.stdout.flush()

        if listing:
            lstfn = os.path.join(wd, '.listing')
            r[lstfn] = -1 # the mtime of .listing file is not used
            if '.listing' in lst and not update_listing:
                d = self.get_listing_map(wd)
                dirnames = set([os.path.dirname(fn) for fn, mtime in d.items() if mtime>0]\
                               + [dn for dn, mtime in d.items() if mtime==0])
                if verbose:
                    sys.stdout.write('<checking integrity [%s directories]> ' % (len(dirnames)))
                    sys.stdout.flush()
                for dn in dirnames:
                    if verbose:
                        sys.stdout.write('+')
                        sys.stdout.flush()
                    fn = os.path.join(dn, '.listing')
                    if self.get_mtime(fn) is None:
                        sys.stdout.write(' <missing %r, forcing regeneration of %r>\n' % (fn, lstfn))
                        sys.stdout.flush()
                        d = None
                        break
                if d is not None:
                    if verbose:
                        sys.stdout.write(' <using %r>\n' % (lstfn))
                        sys.stdout.flush()
                    return d

        for n in lst:
            path = os.path.join(wd, n)
            mtime = self.get_mtime(path)
            if mtime==0:
                dirs.append(path)
                if verbose:
                    sys.stdout.write('d')
                    sys.stdout.flush()
            else:
                r[path.replace('\\', '/')] = mtime
                if verbose:
                    sys.stdout.write('.')
                    sys.stdout.flush()
        if verbose:
            sys.stdout.write('\n')
            sys.stdout.flush()
        for path in dirs:
            r.update(**self.get_remote_files(path, verbose=verbose, listing=listing,
                                             update_listing=update_listing))

        if listing:
            if self.upload_listing_map(wd, r):
                if verbose:
                    sys.stdout.write('<uploaded %r>\n' % (lstfn))
                    sys.stdout.flush()
            else:
                sys.stderr.write('<failed to upload %r>\n' % (lstfn))
                sys.stderr.flush()
        return r

    def fix_local_mtime(self, filename, local, verbose=True):
        fullname = self.abspath(filename)
        rmtime = self.get_mtime(fullname)
        lmtime = int(os.path.getmtime(local))
        mtime = rmtime - self.clock_offset
        if verbose:
            sys.stdout.write('<adjusting local mtime: %s secs>' % (lmtime - mtime))
            sys.stdout.flush()
        os.utime(local, (mtime, mtime))
        #print local, mtime, rmtime, lmtime, int(os.path.getmtime(local))

    def get_files(self, update_listing=False):
        """ Return a {files:modification times} map of the ftp
        directory where files are relative to remote_path and
        modification times are relative to local clock.
        """
        if self.remote_path=='/':
            n = 0
        else:
            assert not self.remote_path.endswith('/'), `self.remote_path`
            n = len(self.remote_path)
        files = {}
        for rfn, mtime in self.get_remote_files(update_listing=update_listing).items():
            if mtime==0:
                #skip directories
                continue
            if os.path.basename(rfn).startswith('.'):
                continue
            assert rfn[n:n+1] in ['/',''],``rfn,n``
            fn = rfn[n+1:]
            files[fn] = mtime - self.clock_offset
            #print rfn, mtime, files[fn]
        return files

    def download(self, filename, target, verbose=True):
        if verbose:
            sys.stdout.write('downloading %r..' % (filename))
            sys.stdout.flush()
        fullname = self.abspath(filename)
        targetdir = os.path.dirname(target)
        if not os.path.exists(targetdir):
            os.makedirs(targetdir)
        f = open(target, 'wb')
        try:
            self.ftp.retrbinary('RETR '+fullname.replace('\\', '/'), f.write, 8*1024)
        except error_perm, msg:
            if verbose:
                sys.stdout.write('FAILED: %s\n' % (msg))
                sys.stdout.flush()
            else:
                sys.stderr.write('FAILED to download %r: %s\n' % (filename, msg))
                sys.stderr.flush()
            f.close()
            os.remove(target)
            return 0
        f.close()
        self.fix_local_mtime(filename, target)
        if verbose:
            sys.stdout.write(' ok [%s bytes]\n' % (os.path.getsize(target)))
            sys.stdout.flush()
        return 1

    def makedirs(self, path, rm_local_listing = False, verbose=True, _cache=[]):
        fullpath = self.abspath(path)
        if fullpath in _cache:
            return
        _cache.append(fullpath)
        parent = os.path.dirname(fullpath)
        name = os.path.basename(fullpath)
        if parent!='/':
            self.makedirs(parent, verbose=verbose)
        lst = self.ftp.nlst(parent.replace('\\', '/'))
        if name and name not in lst:
            if verbose:
                sys.stdout.write('<creating directory %r>' % (fullpath))
                sys.stdout.flush()
            self.ftp.mkd(fullpath.replace('\\', '/'))
            if '.listing' in lst:
                listing = os.path.join(parent, '.listing')
                if verbose:
                    sys.stdout.write('<removing %r>' % (listing))
                    sys.stdout.flush()
                self.ftp.delete(listing.replace('\\', '/'))
        if rm_local_listing:
            lst = self.ftp.nlst(fullpath.replace('\\', '/'))
            if '.listing' in lst:
                listing = os.path.join(fullpath, '.listing')
                if verbose:
                    sys.stdout.write('<removing %r>' % (listing))
                    sys.stdout.flush()
                self.ftp.delete(listing.replace('\\', '/'))


    def upload(self, filename, source, mk_backup=True, verbose=True):
        fullname = self.abspath(filename)
        if verbose:
            sys.stdout.write('uploading %r [%s]..' % (filename, os.path.getsize(source)))
            sys.stdout.flush()
        self.makedirs(os.path.dirname(fullname), rm_local_listing=True, verbose=verbose)
        if mk_backup:
            if verbose:
                sys.stdout.write('<creating %r>' % (filename+'.backup'))
                sys.stdout.flush()
            self.ftp.rename(fullname.replace('\\', '/'), fullname.replace('\\', '/') + '.backup')
        f = open(source, 'rb')
        if verbose:
            sys.stdout.write('<storing>')
        try:
            self.ftp.storbinary('STOR '+fullname.replace('\\', '/'), f, 8*1024)
        except error_perm, msg:
            if verbose:
                sys.stdout.write('FAILED: %s\n' % (msg))
                sys.stdout.flush()
            else:
                sys.stderr.write('FAILED to upload %r: %s\n' % (filename, msg))
                sys.stderr.flush()
            f.close()
            if mk_backup:
                if verbose:
                    sys.stdout.write('<restoring from %r>' % (filename+'.backup'))
                    sys.stdout.flush()
                self.ftp.rename(fullname.replace('\\', '/') + '.backup', fullname.replace('\\', '/'))
            return 0
        f.close()
        if mk_backup:
            if verbose:
                sys.stdout.write('<cleaning up %r>' % (filename+'.backup'))
                sys.stdout.flush()
            self.ftp.delete(fullname.replace('\\', '/') + '.backup')
        self.fix_local_mtime(filename, source)
        if verbose:
            sys.stdout.write(' ok\n')
            sys.stdout.flush()
        return 1

    def remove(self, filename, verbose=True):
        fullname = self.abspath(filename)
        if verbose:
            sys.stdout.write('<removing %r..' % (filename))
            sys.stdout.flush()
        try:
            self.ftp.delete(fullname.replace('\\', '/'))
        except error_perm, msg:
            if verbose:
                sys.stdout.write('FAILED: %s>' % (msg))
                sys.stdout.flush()
            else:
                sys.stderr.write('FAILED to remove %r: %s\n' % (filename, msg))
                sys.stderr.flush()
            return
        dname = os.path.dirname(fullname)
        lst = self.ftp.nlst(dname.replace('\\', '/'))
        if '.listing' in lst:
            listing = os.path.join(dname, '.listing')
            if verbose:
                sys.stdout.write('<removing %r>' % (listing))
                sys.stdout.flush()
            self.ftp.delete(listing.replace('\\', '/'))
        if verbose:
            sys.stdout.write('ok>')
            sys.stdout.flush()

    def remove_directory(self, path, verbose=True):
        fullname = self.abspath(path)
        if verbose:
            sys.stdout.write('<removing %r..' % (path))
            sys.stdout.flush()
        lst = self.ftp.nlst(fullname.replace('\\', '/'))
        for n in lst:
            if n in ['.', '..']:
                continue
            fn = os.path.join(fullname, n)
            mtime = self.get_mtime(fn)
            if mtime==0:
                self.remove_directory(fn, verbose=verbose)
            elif mtime:
                if verbose:
                    sys.stdout.write('<removing %r>' % (fn))
                    sys.stdout.flush()
                self.ftp.delete(fn.replace('\\', '/'))
        try:
            self.ftp.rmd(fullname.replace('\\', '/'))
        except error_perm, msg:
            if verbose:
                sys.stdout.write('FAILED: %s>' % (msg))
                sys.stdout.flush()
            else:
                sys.stderr.write('FAILED to remove %r: %s\n' % (path, msg))
                sys.stderr.flush()
            return
        dname = os.path.dirname(fullname)
        lst = self.ftp.nlst(dname.replace('\\', '/'))
        if '.listing' in lst:
            listing = os.path.join(dname, '.listing')
            if verbose:
                sys.stdout.write('<removing %r>' % (listing))
                sys.stdout.flush()
            self.ftp.delete(listing.replace('\\', '/'))
        if verbose:
            sys.stdout.write('ok>')
            sys.stdout.flush()

def get_local_files(local_root, verbose=True):
    r = {}
    wd = os.path.abspath(os.path.normpath(local_root))
    n = len(wd)
    if n==1: n = 0
    for root, dirs, files in os.walk(wd):
        fix_dirs(dirs)
        for f in files:
            if ignore_filename(f):
                continue
            fn = os.path.join(root, f)
            mtime = int(os.path.getmtime(fn))
            assert fn[n:n+1] in ['/','','\\'],`fn, n`
            r[fn[n+1:]] = mtime
            #print fn, mtime
    return r

def compute_task(local_files, remote_files, remove_paths, mtime_tol=5):
    """ Return (download_list, upload_list, new_upload_list).

    The ``local_files`` and ``remote_files`` are dictionaries of
    ``{<filenames>: <modification times>}``.

    The ``require_download_list`` contains filenames that needs
    to be downloaded (i.e. they are newer than local versions).

    The ``require_upload_list`` contains filenames that needs to
    be uploaded (i.e. they are newer that remote versions).

    The ``mtime_tol`` determines maximal difference of modification times
    for considering the local and remote files to have equal
    modification times. Default is 5 seconds.
    """
    download_list, upload_list, new_upload_list, remove_list = [], [], [], []
    remove_dir_list = []
    for path in remove_paths:
        if path in remote_files:
            remove_list.append(path)
        elif path in local_files:
            remove_list.append(path)
        else:
            flag = False
            for fn, mt in remote_files.items():
                if fn.startswith(path):
                    flag = True
                    remove_list.append(fn)
            remove_dir_list.append(path)
    for filename, rmtime in remote_files.items():
        if filename in remove_list:
            continue
        if filename in local_files:
            lmtime = local_files[filename]
            #print filename, rmtime, lmtime, rmtime-lmtime
            if abs(rmtime - lmtime) < mtime_tol:
                continue
            if rmtime < lmtime:
                upload_list.append(filename)
            else:
                download_list.append(filename)
        else:
            download_list.append(filename)
    for filename, lmtime in local_files.items():
        if filename in remove_list:
            continue
        if filename in remote_files:
            continue
        new_upload_list.append(filename)
    return sorted(download_list), sorted(upload_list), sorted(new_upload_list), sorted(remove_list), sorted(remove_dir_list)

def main():
    usage = "usage: %prog [options] <remote path> <local path>"
    parser = OptionParser(usage=usage,
                          version="%prog "+__version__,
                          description='''\

%prog is tool to synchronize remote and local directory trees using
FTP protocol (see http://ftpsync2d.googlecode.com/ for updates). Both
directions are supported. Write access to FTP server is required.

To skip processing remote directories that one does not have read or
write access, use --skip option. When a new file was added to FTP
server by other means than using %prog, use --listing to update
.listing files.

Remote path must be given in the following form:
[ftp://][username[:password]@]hostname[<remote directory>]
'''
                          )
    parser.add_option("-u", "--upload", dest="upload_files",
                      action="store_true", default=False,
                      help="enable uploading files")
    parser.add_option("-d", "--download", dest="download_files",
                      action="store_true", default=False,
                      help="enable downloading files")
    parser.add_option("-s", "--skip", dest="skip_path",
                      default = [], action="append",
                      help="skip listing specified remote (absolute) path")
    parser.add_option("-l", "--listing", dest="update_listing",
                      action="store_true", default=False,
                      help="update remote .listing files")
    parser.add_option("-r", "--remove", dest="remove_paths",
                      default=[], action="append",
                      help="remove specified files and directories")

    (options, args) = parser.parse_args()
    if len(args)!=2:
        parser.error("incorrect number of arguments")

    start_time = time.time()
    remote_path, local_path = args
    local_files = get_local_files(local_path)

    session = FtpSession(remote_path)
    session.skip_dirs.extend(options.skip_path)
    remote_files = session.get_files(update_listing=options.update_listing)

    download_list, upload_list, new_upload_list, remove_list, remove_dir_list = compute_task(local_files, remote_files, options.remove_paths)

    removed_files = 0
    for path in remove_list:
        lpath = os.path.join(local_path, path)
        if os.path.exists(lpath):
            print 'moving %r to %r' % (lpath, trash_dir)
            target = os.path.join(trash_dir, lpath)
            target_dir = os.path.dirname(target)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if os.path.exists(target):
                os.remove(target)
            shutil.move(lpath, target)
        mtime = session.get_mtime(path)
        if mtime:
            rpath = session.abspath(path)
            print 'moving %r to %r' % (rpath, ftp_trash_dir)
            target = os.path.join(ftp_trash_dir, rpath[1:] if rpath.startswith('/') else rpath)
            target_dir = os.path.dirname(target)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            status = session.download(path, target)
            if status:
                session.remove(path)

    for path in remove_dir_list:
        lpath = os.path.join(local_path, path)
        if os.path.exists(lpath):
            print 'moving %r to %r' % (lpath, trash_dir)
            if not os.path.exists(trash_dir):
                os.makedirs(trash_dir)
            target = os.path.join(trash_dir, lpath)
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.move(lpath, target)
        mtime = session.get_mtime(path)
        if mtime==0:
            rpath = session.abspath(path)
            print 'moving %r to %r' % (rpath, ftp_trash_dir)
            target = os.path.join(ftp_trash_dir, rpath[1:] if rpath.startswith('/') else rpath)
            target_dir = os.path.dirname(target)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            session.remove_directory(path)

    downloaded_files = 0
    if options.download_files:
        for filename in download_list:
            target = os.path.join(local_path, filename)
            status = session.download(filename, target)
            if status:
                downloaded_files += 1
    else:
        n = len(download_list)
        if n:
            print "Skipping downloading",n,"files (see --download option):"
            for filename in download_list:
                print filename


    uploaded_files = 0
    if options.upload_files:
        for filename in upload_list:
            source = os.path.join(local_path, filename)
            status = session.upload(filename, source, mk_backup=True)
            if status:
                uploaded_files += 1

        for filename in new_upload_list:
            source = os.path.join(local_path, filename)
            status = session.upload(filename, source, mk_backup=False)
            if status:
                uploaded_files += 1
    else:
        n = len(upload_list) + len(new_upload_list)
        if n:
            print "Skipping uploading",n,"files (see --upload option):"
            for filename in upload_list + new_upload_list:
                print filename

    if downloaded_files:
        print '# downloaded files:', downloaded_files

    if uploaded_files:
        print '# uploaded files:', uploaded_files
    print 'done [%s seconds]' % (int(time.time()-start_time))

if __name__ == "__main__":
    main()
