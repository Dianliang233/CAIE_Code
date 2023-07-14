from sys import exit
import platform

VERSION = 'v0.1.0'
PLATFORM = f'[ {platform.python_implementation()} {platform.python_version()} ] on {platform.system()}'

show_tree = False
debug = False
show_time = False

def standard_output():
    print(f'CAIE Pseudocode Interpreter {VERSION}')
    print(f'Base on {PLATFORM}')
    print('Submit issues at https://github.com/iewnfod/CAIE_Code/issues/new')
    print('Copyright (c) 2023 Iewnfod. ')
    print('All Rights Reserved. ')

def open_debug():
    global debug
    debug = True

def version():
    print('Version:', VERSION)
    exit(0)

def help():
    standard_output()

    print()

    print('Usage: \033[1mcpc\033[0m [file_path] [options]')

    print()

    print('Options:')
    arguments.sort()
    for i in arguments:
        print('\t\033[1m', i[0], '\t', i[1], '\033[0m\t', i[3])

    exit(0)

def get_tree():
    global show_tree
    show_tree = True

def get_time():
    global show_time
    show_time = True

def show_keywords():
    from src.lex import reserved
    keywords = sorted(reserved)
    l = {}
    for k in keywords:
        if k[0] in l.keys():
            l[k[0]].append(k)
        else:
            l[k[0]] = [k]

    print('Keywords:')
    for v in l.values():
        print(' '.join(v))

    exit(0)

arguments = [  # 输入参数: (参数简写, 参数全称, 运行函数, 描述)
    ('-gt', '--get-tree', get_tree, 'To show the tree of the program after being parsed'),
    ('-v', '--version', version, 'To show the version of this interpreter'),
    ('-h', '--help', help, 'To show this help page'),
    ('-d', '--debug', open_debug, 'To show debug information during running'),
    ('-t', '--time', get_time, 'To show the time for the script to run'),
    ('-k', '--keywords', show_keywords, 'To show all the keywords'),
]
