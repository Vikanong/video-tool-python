import cx_Freeze


build_exe_options = {'packages': ['encodings']}

executables = [cx_Freeze.Executable("main.py", icon="favicon.ico")]

cx_Freeze.setup(
    name='video-tool',
    version='0.1',
    description='video-tool-python',
    executables=executables,
    options={'build_exe': build_exe_options}
)