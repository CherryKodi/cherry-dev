# -*- coding: UTF-8 -*-
import os
import sys
import re
import zipfile

# Compatibility with 3.0, 3.1 and 3.2 not supporting u"" literals
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x
 
class Generator:
    def __init__( self ):
        self._generate_zip_file()
        print("Finished zipping")

    def zipdir(self, path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    def _generate_zip_file( self ):
        if not os.path.exists("zip"):
            os.makedirs("zip")
        folder = "zip"
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)
                continue
        addons = os.listdir( "." )
        for addon in addons:
            try:
                if ( not os.path.isdir( addon ) or addon == ".svn" or addon == ".git" ): continue
                _path = os.path.join( addon, "addon.xml" )
                xml = open( _path, "r" ).read()
                version = re.findall("""version=\"(.*[0-9])\"""", xml)[1]
                zipf = zipfile.ZipFile("zip/"+ addon + "-" + version + ".zip", 'w', zipfile.ZIP_DEFLATED)
                self.zipdir(addon, zipf)
                zipf.close()
            except:
                pass

if ( __name__ == "__main__" ):
    # start
    Generator()