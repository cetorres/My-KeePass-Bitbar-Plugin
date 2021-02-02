#!/usr/bin/env LC_ALL=en_US.UTF-8 python3
# -*- coding: UTF-8 -*-
# <bitbar.title>My KeePass</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Carlos Torres</bitbar.author>
# <bitbar.author.github>cetorres</bitbar.author.github>
# <bitbar.desc>KeePass password manager.</bitbar.desc>
# <bitbar.dependencies>python3,pykeepass</bitbar.dependencies>

# Install
# Before using, please install the dependencies needed for this script.
# pip3 install pykeepass

import os
import subprocess
import sys
import json
import base64
try:
    from pykeepass import PyKeePass
except ImportError:
	print('You need to "pip3 install pykeepass"')

# Global vars
config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.mykeepass.cfg')
config = { 'showPass': False, 'dbFile': '', 'userPass': '' }
icon = 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABG0lEQVQ4T73UzypFURTH8c8tZeAJZGBiaiIhMfEAlBAjr2DiKUzuGxhKpHgAExJS8gAGBvIEysBAS/vUvcfd589Nd01Ou732d//277c6Hf9cnRreGDaxnPrucIHv3Lkq4DROMYvnBJjDC3bxNgiaA4ayW3xhDx/p8CROMI7VQUpzwB0cY6YHVggK6Cv2cVZWmQN2MY+VjFeh/gkHTYHnqXErA8zulxUeYhFLmMJ7Bljs3eMBR0VfLzCedzPkWEZAYYNeYDzvj8kNL9jGrw0jAxaehKdRdetKhY8pmACF4VERVG69gErgJ9YS4Dp9q9YTdcCGOfS1jSaUdVwOIw8buCqPTXgRnoXJbSpCDI/D+745bAPJ9tb9sVtf8gOPHToV03R01QAAAABJRU5ErkJggg=='
kp = None

def addToClipBoard(text):
    command = "echo '" + text.strip() + "' | base64 --decode | pbcopy"
    os.system(command)

def read_config_file():
    global config
    if not os.path.isfile(config_file):
        write_config_file()
        return False
    else:
        with open(config_file, 'rt') as f:
            data = f.read()
            if data and len(data) > 0:
                config = json.loads(data)                
                if config['dbFile'] == '' or config['dbFile'] == 'None' or config['userPass'] == '' or config['userPass'] == 'None':
                    return False
                return True
            else:                
                return False    

def write_config_file():
    global config
    with open(config_file, 'wt') as f:
        f.write(json.dumps(config))

def encode_base64(text):
    encodedBytes = base64.b64encode(text.encode("utf-8"))
    return str(encodedBytes, "utf-8")

def decode_base64(data):
    decoded = base64.b64decode(data)
    return decoded.decode("utf-8")

def createEntriesList(entries):
    for entry in entries:
        print(entry.title)
        print('--Click to copy:\n')
        print('--User: ' + entry.username + '| terminal=false bash=' + sys.argv[0] + ' param1=copy param2=' + encode_base64(entry.username.strip()) + ' terminal=false' + '\n')
        
        passw = entry.password
        if config['showPass'] == False:
            passw = '**********'
        print('--Password: ' + passw + '| terminal=false bash=' + sys.argv[0] + ' param1=copy param2=' + encode_base64(entry.password.strip()) + ' terminal=false' + '\n')
        if entry.url:
            dots = ''
            if len(entry.url) > 30:
                dots = '...'
            print('--URL: ' + entry.url[:30] + dots + '\n')
            print('----Open | href=' + entry.url.strip() + ' \n')
            print('----Copy | terminal=false bash=' + sys.argv[0] + ' param1=copy param2=' + encode_base64(entry.url.strip()) + ' terminal=false \n')
        if entry.notes:
            print('-----')
            print('--Notes:\n')
            print('--' + entry.notes.replace('\n','\n--') + '\n')
            print('--Copy notes| terminal=false bash=' + sys.argv[0] + ' param1=copy param2=' + encode_base64(entry.notes.strip()) + ' terminal=false' + '\n')
        print('-----')
        print('--✕ Delete | color=red terminal=false bash=' + sys.argv[0] + ' param1=delete_password param2=' + encode_base64(entry.title.strip()) + ' param3=' + encode_base64(entry.username.strip()) + ' refresh=true terminal=false' + '\n')

def prompt(text='', defaultAnswer='', icon='note', title='', buttons=('Cancel', 'OK'), defaultButton=1, hidden=False):
    try:
        d = locals()
        d['buttonsStr'] = ', '.join('"%s"' % button for button in buttons)
        d['defaultButtonStr'] = isinstance(defaultButton, int) and buttons[defaultButton] or defaultButton
        d['hiddenStr'] = 'true' if hidden else 'false'
        return subprocess.check_output(['osascript', '-l', 'JavaScript', '-e', '''
            const app = Application.currentApplication()
            app.includeStandardAdditions = true
            const response = app.displayDialog("{text}", {{
                defaultAnswer: "{defaultAnswer}",
                withTitle: "{title}",
                withIcon: "{icon}",
                buttons: [{buttonsStr}],
                defaultButton: "{defaultButtonStr}",
                hiddenAnswer: {hiddenStr}
            }})
            response.textReturned
        '''.format(**d)]).rstrip().decode()        
    except subprocess.CalledProcessError:
        pass

def prompt_for_file(text='Please select a database file:'):   
    try:
        d = locals()
        res = subprocess.check_output(['osascript', '-e', '(choose file with prompt "{text}") as string'.format(**d)]).rstrip().decode()
        # Clean file path
        result = res.replace(':','/')
        parts = result.split('/')
        first_part = parts[0]
        first_part = first_part.replace(' ', '')
        parts[0] = first_part
        result = '/'.join(parts)
        result = '/Volumes/' + result
        return result
    except subprocess.CalledProcessError:
        pass

def confirm(text='', title=''):
    return os.system("osascript -e 'display dialog \"" + text + "\" with title \"" + title + "\" with icon caution buttons {\"Cancel\", \"OK\"} default button 2'")

def alert(text='', title=''):
    os.system("osascript -e 'display dialog \"" + text + "\" with with icon info title \"" + title + "\" buttons {\"OK\"} default button 1'")    

def notify(text, title, sound='Glass'):
    os.system('osascript -e \'display notification "{}" with title "{}" sound name "{}"\''.format(text, title, sound))

def add_entry():    
    title = prompt('Title', title='New Entry', buttons=('Cancel', 'Continue'))
    if title != '':
        username = prompt('User name', title='New Entry', buttons=('Cancel', 'Continue'))
        if username != '':
            password = prompt('Password', title='New Entry', hidden=True, buttons=('Cancel', 'Continue'))
            if password != '':
                url = prompt('URL', title='New Entry', buttons=('Cancel', 'Continue'))
                notes = prompt('Notes', title='New Entry', buttons=('Cancel', 'Finish'))
                kp.add_entry(kp.root_group, title, username, password, url=url, notes=notes)
                kp.save()
                alert('Entry added successfully.\nTitle: ' + str(title) + '\n' + 'User: ' + str(username), 'New Entry')

def delete_password(title, username):
    t = decode_base64(title).strip()
    u = decode_base64(username).strip()
    res = confirm('Confirm delete this password?\n' + t + '\nUser: ' + u, 'Delete Entry')
    if res == 0:
        entry = kp.find_entries(title=t, username=u, first=True)
        if entry:
            kp.delete_entry(entry)
            kp.save()
            alert('Entry deleted successfully.', 'Delete Entry')

def set_config(is_change=False):
    try:        
        path = prompt_for_file('Enter KeePass database file (.kdbx)')        
        if path != '':        
            passwd = prompt('Enter the database password', title='My KeePass Settings', hidden=True)
            if passwd != '':
                config['dbFile'] = str(path)
                config['userPass'] = str(passwd)
                write_config_file()
                return True
    except:
        read_config_file()
        pass

    return False

def print_icon():
    print('| size=10 templateImage=iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABG0lEQVQ4T73UzypFURTH8c8tZeAJZGBiaiIhMfEAlBAjr2DiKUzuGxhKpHgAExJS8gAGBvIEysBAS/vUvcfd589Nd01Ou732d//277c6Hf9cnRreGDaxnPrucIHv3Lkq4DROMYvnBJjDC3bxNgiaA4ayW3xhDx/p8CROMI7VQUpzwB0cY6YHVggK6Cv2cVZWmQN2MY+VjFeh/gkHTYHnqXErA8zulxUeYhFLmMJ7Bljs3eMBR0VfLzCedzPkWEZAYYNeYDzvj8kNL9jGrw0jAxaehKdRdetKhY8pmACF4VERVG69gErgJ9YS4Dp9q9YTdcCGOfS1jSaUdVwOIw8buCqPTXgRnoXJbSpCDI/D+745bAPJ9tb9sVtf8gOPHToV03R01QAAAABJRU5ErkJggg==\n')
    print('---')

def print_title():
    global config
    print('My KeePass - ' + os.path.basename(config['dbFile']))

def print_about():
    print('---')
    print('About\n')
    print('--Carlos E. Torres | href=https://cetorres.com\n')
    print('--✉️ cetorres@cetorres.com | href=mailto:cetorres@cetorres.com\n')
    print('--🔗 https://cetorres.com | href=https://cetorres.com\n')

def print_enter_settings():
    print_icon()
    print('My KeePass\n')
    print('Please enter the application settings.\n')
    print('⚙︎ Show Settings | terminal=false bash=' + sys.argv[0] + ' param1=show_settings refresh=true terminal=false' + '\n')   

def init_database():
    global kp
    kp = PyKeePass(config['dbFile'], password=config['userPass'])

def print_options():
    global config
    print('---')
    print('＋Add New Entry | terminal=false bash=' + sys.argv[0] + ' param1=add_entry refresh=true terminal=false' + '\n')
    show_pass_icon = '☑︎' if config['showPass'] else '☐'
    print(show_pass_icon + ' Show Passwords | terminal=false bash=' + sys.argv[0] + ' param1=show_pass refresh=true terminal=false' + '\n')
    print('⚙︎ Change Settings | terminal=false bash=' + sys.argv[0] + ' param1=change_settings refresh=true terminal=false' + '\n')

def print_error(text):
    print('---')
    print(text)

# Read config file
read_config = read_config_file()
if not read_config and len(sys.argv) == 1:
    print_enter_settings()
    quit()

# Database
if read_config and len(sys.argv) == 1:
    try:
        init_database()
    except:        
        print_enter_settings()
        print_error('Error: Could not open the database. Please review the settings and try again.')
        quit()

# Check params
if len(sys.argv) > 1:
    if sys.argv[1] == 'copy':
        dataToCopy = sys.argv[2]
        addToClipBoard(dataToCopy)
        quit()
    if sys.argv[1] == 'show_pass':
        config['showPass'] = not config['showPass']
        write_config_file()
        quit()
    if sys.argv[1] == 'add_entry':
        init_database()
        add_entry()
        quit()
    if sys.argv[1] == 'delete_password':
        init_database()
        title = sys.argv[2]
        username = sys.argv[3]
        delete_password(title, username)
        quit()
    if sys.argv[1] == 'show_settings':
        set_config()
        quit()
    if sys.argv[1] == 'change_settings':
        set_config(is_change=True)
        quit()

# Load database
try:
    entries = kp.entries
except:
    print_enter_settings()
    print_error('Error: Could not open the database. Please review the settings and try again.')
    quit()  

# Menu
print_icon()
print_title()
createEntriesList(entries)
print_options()
print_about()
