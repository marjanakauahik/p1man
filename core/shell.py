#
# shell.py - the p1marjana main shell
#
# This file if part of p1man project
#
# See 'LICENSE' file for copying
#

import sys
import os
from core.complete import complete
from core.complete import array
from core.config import __version__
from core.config import __framework_version__
from core.config import __codename__
from core.misc import printt
from core.misc import print_help
from core.misc import print_help_option
from core.config import url
from core.config import action_url
from core.config import port
from core.config import user_agent
from core.config import html_file
from core.config import external_js
from core.config import quiet_mode
from core.config import say
from core.httpd import weeman
from core.framework import framework

def print_startup():
    """
        Print the startup banner
    """
    print("\033[H\033[J") # Clear the screen
    print("\033[01;31m")
    sys.stdout.write(open("core/logo.txt", "r").read()[:-1])
    print("\033[00m")
    sys.stdout.write("\033[01;33m\t  :[ %s-%s | Framework: %s]:\n\033[00m" %(__version__,  __codename__, __framework_version__))

def profile_getkey(profile_file, key):
    try:
        profile = open(profile_file, "r").readlines()
    except Exception as e:
        return 0
    if profile == None:
        return 0
    for line in profile:
        if line.startswith("\n") or line.startswith("#"):
            pass

        else:
            (skey,value) = line.split(" = ")
            if skey == key:
                return str(value[:-1])

    return 0

def shell_noint(profile_file):
    global url
    global port
    global action_url
    global user_agent
    global html_file
    global external_js

    try:
        url = profile_getkey(profile_file, "url")
        action_url = profile_getkey(profile_file, "action_url")
        port = int(profile_getkey(profile_file, "port"))
        user_agent = profile_getkey(profile_file, "user_agent")
        html_file = profile_getkey(profile_file, "html_file")
        external_js = profile_getkey(profile_file, "external_js")

        print_startup()
        s = weeman(url,port)
        s.clone()
        s.serve()

    except ValueError:
        printt(3, "Error: your profile file looks bad.")
    except KeyboardInterrupt:
        s = weeman(url,port)
        s.cleanup()
        print("\nInterrupt ...")
    except IndexError:
        if prompt[0] == "help" or prompt[0] == "?":
            print_help()
        else:
            printt(3, "Error: please provide option for \'%s\'." %prompt[0])
    except Exception as e:
        printt(3, "Error: (%s)" %(str(e)))

def shell():
    """
        The shell, parse command line args,
        and set variables.
    """
    global url
    global port
    global action_url
    global user_agent
    global html_file
    global external_js

    print_startup()

    if os.path.exists("history.log"):
        if  os.stat("history.log").st_size == 0:
            history = open("history.log", "w")
        else:
            history = open("history.log", "a")
    else:
        history = open("history.log", "w")

    while True:
        try:
            # for Re-complete
            complete(array)
            an = raw_input("\033[01;37m>>> \033[00m") or "help"
            prompt = an.split()
            if not prompt:
                print("Error: What? try help.")
            elif prompt[0] == ";" or prompt[0] == "clear":
                print("\033[H\033[J")
            elif prompt[0] == "q" or prompt[0] == "quit":
                printt(2,"bye bye!")
                break;
            elif prompt[0] == "help" or prompt[0] == "?":
                if prompt[1]:
                    print_help_option(str(prompt[1]))
                else:
                    print_help()
            elif prompt[0] == "show":
                l = 20
                sys.stdout.write("\033[01;37m\t")
                print("-" * l)
                print("\turl          : %s " %url)
                print("\tport         : %d " %(port))
                print("\taction_url   : %s " %(action_url))
                print("\tuser_agent   : %s " %(user_agent))
                print("\thtml_file    : %s " %(html_file))
                print("\texternal_js  : %s " %(external_js))
                sys.stdout.write("\t")
                print("-" * l)
                sys.stdout.write("\033[01;00m")
            elif prompt[0] == "set":
                if prompt[1] == "port":
                    port = int(prompt[2])
                    ## Check if port == 80 and not running as root
                    if port == 80 and os.getuid() != 0:
                        printt(2, "Permission denied, to bind port 80, you need to run weeman as root.");
                    history.write("port = %s\n" %port)
                if prompt[1] == "url":
                    url = str(prompt[2])
                    history.write("url = %s\n" %url)
                if prompt[1] == "action_url":
                    action_url = str(prompt[2])
                    history.write("action_url = %s\n" %action_url)
                if prompt[1] == "user_agent":
                    prompt.pop(0)
                    u = str()
                    for x in prompt:
                        u+=" "+x
                    user_agent = str(u.replace("user_agent", ""))
                    history.write("user_agent = %s\n" %user_agent)
                if prompt[1] == "html_file":
                    html_file = str(prompt[2])
                if prompt[1] == "external_js":
                    external_js = str(prompt[2])
                    history.write("external_js = %s\n" %external_js)
            elif prompt[0] == "run" or prompt[0] == "r":
                if not url:
                    printt(3, "Error: \'url\' can't be \'None\', please use \'set\'.")
                elif not action_url:
                    printt(3, "Error: \'action_url\' can't be \'None\', please use \'set\'.")
                else:
                    # Here we start the server (:
                    s = weeman(url,port)
                    s.clone()
                    s.serve()
            elif prompt[0] == "banner" or prompt[0] == "b":
                print_startup()
            elif prompt[0] == "framework":
                fw = framework()
                fw.shell()
            else:
                print("Error: \'%s\' What? try help." %prompt[0])

        except KeyboardInterrupt:
            s = weeman(url,port)
            s.cleanup()
            print("\nInterrupt ...")
        except IndexError:
            if prompt[0] == "help" or prompt[0] == "?":
                print_help()
            else:
                printt(3, "Error: please provide option for \'%s\'." %prompt[0])
        except Exception as e:
            printt(3, "Error: (%s)" %(str(e)))
