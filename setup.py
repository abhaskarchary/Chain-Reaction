import cx_Freeze
import os
os.environ['TCL_LIBRARY'] = "C:\\Users\\A Bhaskar Chary\\AppData\\Local\\Programs\\Python\\Python36\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "C:\\Users\\A Bhaskar Chary\\AppData\\Local\\Programs\\Python\\Python36\\tcl\\tk8.6"
executables = [cx_Freeze.Executable("chain reaction 2.4.py")]

cx_Freeze.setup(
    name = "Chain Reaction 2.4",
    options = {"build_exe":{"packages":["pygame"],"include_files":["images/","Spins/","Button/"]}},
    description = "Chain Reaction 2.4",
    executables = executables
    )
               
