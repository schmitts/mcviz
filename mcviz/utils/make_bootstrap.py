#! /usr/bin/env python

import virtualenv, textwrap

output = virtualenv.create_bootstrap_script(textwrap.dedent("""
    import os, subprocess
    from os import symlink
    def after_install(options, home_dir):
        
        os.system("git submodule update --init mcviz.examples")
        os.system("git submodule update --init mcviz.jet")
        try:
            symlink("mcviz.examples/mcviz/examples/inputs", "examples")
        except OSError:
            pass

        ret = subprocess.call([join(home_dir, 'bin', 'pip'), 'install', '-e', '.'])
        
        try:
            symlink("env/bin/mcviz", "mcv")
        except OSError:
            pass
        
        if not ret:
            print "Finished! Now to run mcviz, type ./mcv"
    
    def adjust_options(options, args):
        options.use_distribute = True
        options.never_download = False
        options.search_dirs.append("dist/")
        args[:] = ["env"]
"""))
f = open('mcviz_bootstrap.py', 'w').write(output)
