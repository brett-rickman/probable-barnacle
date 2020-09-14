import gzip, tarfile, os, argparse, re

parser = argparse.ArgumentParser()
parser.add_argument("--db_in", default="database.bak", help="Name of NIOS backup file")
parser.add_argument("--db_out", default="db_fixed.tar.gz", help="Name of backup with reset admin password")
parser.add_argument("--work_dir", default="db", help="Directory to extract backup into")
parser.add_argument("--admin_pwd", default="infoblox", help="Builtin admin user password")
args = parser.parse_args()

# Extract db_in to work_dir, creating the directory if necessary
if (os.path.isdir(args.work_dir) is False):
    os.mkdir(args.work_dir)

with (tarfile.open(args.db_in, "r:gz")) as tf:
    tf.extractall(path = args.work_dir)

# Reset the admin user's password to admin_pwd
onedb_file = os.path.join(args.work_dir, "onedb.xml")
onedb_fixed = os.path.join(args.work_dir, "onedb_fixed.xml")
onedb_out = open(onedb_fixed, 'w')
with (open(onedb_file, 'r', encoding = 'utf8')) as onedb:
    for rtxml in onedb:
        if (re.search('VALUE="admin"', rtxml)):
            rtxml_out = re.sub('PROPERTY NAME="password" VALUE=".+"/>', 'PROPERTY NAME="password" VALUE="infoblox"/>', rtxml)
            print(rtxml_out)
        else:
            rtxml_out = rtxml 
        onedb_out.write(rtxml_out)
onedb_out.close



