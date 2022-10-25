# Convert all .ui files in all subdirectories of the current script
import os
import sys

def run(main, name, *args):
    saved_argv = sys.argv
    sys.argv = [name, *args]
    try:
        main()
    except SystemExit as exc:
        if exc.code != 0:
            raise RuntimeError(f"\"{name} {' '.join(args)}\" exited with {exc.code}")
        return exc.code
    finally:
        sys.argv = saved_argv
        pass
    return 0

def pyrrc(in_file, out_file):
    """
    Run the qt resource compiler
    """
    # from PySide2.pyrcc_main import main
    # run(main, "pyrcc", in_file, "-o", out_file)
    # rcc -g python application.qrc > application_rc.py
    run_line = f"rcc -g python {in_file} > {out_file}"
    os.system(run_line)

def pyuic(in_file, out_file):
    """
    Run the qt UI compiler
    """
    #from PySide2.uic.pyuic import main
    # pyside2-uic -x mainwindow.ui -o desktop.py
    #main = "pyside2-uic"
    #run(main, "pyuic", "-o", out_file, in_file)
    in_file2 = os.path.abspath(in_file) #.encode('unicode_escape').decode()
    out_file2 = os.path.abspath(out_file) #.encode('unicode_escape').decode()
    #exec(f"pyside2-uic {in_file2} -o {out_file2}")
    run_line = "pyside2-uic " + in_file2 + " -o " + out_file2
    # exec(run_line, globals(), locals())
    os.system(run_line)

def file_in_newer(file_in, file_out):
    """
    Check whether file_in is newer than file_out, if file_out exists.

    Returns True if file_in is newer, or if file_out doesn't exist; False
    otherwise.
    """
    try:
        out_stat = os.stat(file_out)
    except OSError:
        # file_out does not exist
        return True

    in_stat = os.stat(file_in)

    # simple comparison of modification time
    return in_stat.st_mtime >= out_stat.st_mtime

# look for .ui files
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".ui"):
            file_in = os.path.join(root, file)
            file_out = os.path.splitext(file_in)[0]+'.py'
            if file_in_newer(file_in, file_out):
                print("Generating " + file_out + " ...")
                pyuic(file_in, file_out)

# RC file in UI directory
execute_root = os.path.split(sys.modules[__name__].__file__)[0]
ui_root = os.path.join(execute_root, 'UI')
rc_file = 'main_resources.qrc'
out_file = 'main_resources_rc.py'

in_file = os.path.join(ui_root, rc_file)
out_file = os.path.join(ui_root, out_file)

if file_in_newer(in_file, out_file):
    print("Generating " + out_file + " ...")
    pyrrc(in_file, out_file)

# Images
images_root = os.path.join(execute_root, 'images')
out_root = os.path.join(execute_root, 'UI')
rc_file = 'images.qrc'
out_file = 'images_rc.py'

in_file = os.path.join(images_root, rc_file)
out_file = os.path.join(ui_root, out_file)

if file_in_newer(in_file, out_file):
    print("Generating " + out_file + " ...")
    pyrrc(in_file, out_file)

