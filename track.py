#Ran with Python 3.8.2
#When the button or box is typed, it needs to call a function to make actions (within the parameter)


import imaplib
import os
import re
import email
from email.parser import HeaderParser
import subprocess
from bs4 import BeautifulSoup
###############################################

import tkinter as tk
from tkinter import ttk
from tkinter import *


root = tk.Tk()
root.title("TRACKER")
v = tk.IntVar()


black_email=[]
black_state =[]
black_domain =[]
email_selected = tk.BooleanVar(value=False)
state_selected = tk.BooleanVar(value=False)
domain_selected = tk.BooleanVar(value=False)

def blacklist_add():
    blk_list = rules_black_entry.get()
    if str(v.get()) == '1':
        black_email.append(blk_list)
        rules_list_email.insert('end',blk_list)
    elif str(v.get()) =='2':
        black_domain.append(blk_list)
        rules_list_domain.insert('end',blk_list)
    elif str(v.get()) == '3':
        black_state.append(blk_list)
        rules_list_state.insert('end',blk_list)

def blacklist_remove():
    blk_list = rules_black_entry.get()
    if str(v.get()) == '1':
        black_email.remove(blk_list)
        idx = rules_list_email.get(0, tk.END).index(blk_list)
        rules_list_email.delete(idx)
        
    elif str(v.get()) =='2':
        black_domain.remove(blk_list)
        idx = rules_list_domain.get(0, tk.END).index(blk_list)
        rules_list_domain.delete(idx)

    elif str(v.get()) == '3':
        black_state.remove(blk_list)
        idx = rules_list_state.get(0, tk.END).index(blk_list)
        rules_list_state.delete(idx)
    
def runmail():

    org_email = log_email_org.get()
    from_pwd = log_pass.get()
    num_emails = int(log_email_num.get())

    def extract_body(payload):
        
        if isinstance(payload,str):
            return payload
        else:
            return '\n'.join([extract_body(part.get_payload()) for part in payload])
    #establish connection with the server(we can make advance tab so yousers can specify their mail server
    #simplified version could have a button to choose between gmail,outlook,yahoo or whatever
    #we can just leave gmail button for now(if user clicks gmail app fills the  bellow variables accordingly
    #leave this for later...just throwing ideas... you dont have to deal with this
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    #this is what user(simple view) is supposed to provide(gmail address) and password
    conn.login(org_email, from_pwd)
    conn.select()
    
    #once connection established con.search will search for all UNSEEN email(unread)
    #this is what you have to play around with
    #UNSEEN is one of the option
    #we need if else statements so user can specify different mailboxes
    #UNSEEN is one of them, I would assume that you can change this to ALL which fetches all emails
    #but you have to look for options(argument) that you can pass to conn(imaplib object btw) so that we have 
    #user specified emails in data var
    typ, data = conn.search(None, 'UNSEEN')
    ids = data[0]
    id_list = ids.split()
    latest_id = int(id_list[-1])
    
    try:
        for num in range(latest_id,latest_id - num_emails, -1 ):
            typ, msg_data = conn.fetch(str(num).encode() , '(RFC822)')
            
            for response_part in msg_data:
        #this for loop i did not quite understand(I
                if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1].decode('UTF-8'))
                        #msg is apparently some sort of hash table or a dictionary and you just specify
                        #what you need from email(subject,from, etc...)
                        subject=msg['subject']
                        header_ret_path=msg['return-path']
                        header_from=msg['from']
                        header_received=msg['received']
                        

                        log_textBox.insert(END,"\nFROM:\n"+str(header_from))
                        log_textBox.insert(END,"\nRETURN_PATH:\n"+str(header_ret_path))
                        log_textBox.insert(END, "\nRECEIVED:\n" + str(header_received))
                        #log_textBox.insert(END,"\n====================================SUBJECT=======================================\n")
                        #log_textBox.insert(END,"SUBJECT:\n"+str(subject))
                        #log_textBox.insert(END,"\n====================================END SUBJECT===================================\n")
                        #payload = msg.get_payload()
                        #body = extract_body(payload)
                        #log_textBox.insert(END,"\n====================================BEGIN BODY====================================\n")
                        #log_textBox.insert(END,"BODY:\n"+str(body))

                        ### We ll use curl to look up the domain to which we are sending to and print some results and maybe draw a map
                        if(re.match(
                            "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",
                            header_from)):
                            domainOrIPtoCheck=header_from
                        elif('@' in header_from):
                            domainOrIPtoCheck = header_from[header_from.find("@") + 1: header_from.find('>')]
                        else:

                            print("\nUnrecognized form of IP or Domain\n")
                            #break


                        curl_cmd='curl -d \"ipAddress='+domainOrIPtoCheck+'&press=Go " https://www.ultratools.com/tools/ipWhoisLookupResult'

                        proc = subprocess.Popen([curl_cmd], stdout=subprocess.PIPE, shell=True)
                        (response, err) = proc.communicate()

                        
                        response_trimmed = BeautifulSoup(response, "html.parser")
                        
                        values = response_trimmed.find_all(class_="value")
                        tempList=[]
                        for i in values:

                            temp=re.findall(">.+</",str(i))
                            for j in temp:
                                values_trimmed=re.sub("(</)|>",'',str(j))
                                tempList.append(str(values_trimmed))
                                #print(values_trimmed)
                            #log_textBox.insert(END,values_trimmed)

                            #maps_textBox.insert(END,' State/Province:'+ str(values_trimmed[values_trimmed.find('State/Province:  ')+1 : values_trimmed.find('P')]))
                        for val in tempList:
                            maps_textBox.insert(END,'\n'+str(val)+'\n')

                            #values_trimmed is a list of strings that contain the values:

                            #so what needs to be done is to output these values and put location if possible on map
                        #curl_out=subprocess.run(cmd2)
                        #""" curl -d "ipAddress=[mail183.atl241.mcsv.net]&press=Go " https://www.ultratools.com/tools/ipWhoisLookupResult | grep "class=\"value\"" """
                        tf = False
                        if email_selected.get() == True:
                            for emails in black_email:
                                if str(header_from[header_from.find("<") + 1 : header_from.find('>')]) == emails:
                                    if tf == True:
                                        return
                                    else:
                                        tf= True
                                    

                        if state_selected.get() == True:
                            for states in black_state:
                                if str(values_trimmed[values_trimmed.find('State/Province:  ')+1 : values_trimmed.find('P')]) == states :
                                    if tf == True:
                                        return
                                    else:
                                        tf= True
                                    
                        if domain_selected.get()== True:
                            for domains in black_domain:
                                if str(header_from[header_from.find("@") + 1 : header_from.find('>')]) == domains:
                                    if tf == True:
                                        return
                                    else:
                                        tf= True
                        if tf == False:
                            log_textBox.insert(END,'\nTrust: Safe')
                        else:
                            log_textBox.insert(END,'\nTrust: Unsafe')

                        


                        log_textBox.insert(END,"\n\n=======================================================================\n")

                        maps_textBox.insert(END,'\nFrom: ' + str(header_ret_path[header_ret_path.find("<") + 1 : header_ret_path.find('>')]))
                        if tf == False:
                            maps_textBox.insert(END,'\nTrust: Safe \n')
                        else:
                            maps_textBox.insert(END,'\nTrust: Unsafe \n')

                        maps_textBox.insert(END, '\n===============================================================================\n')
                typ, response = conn.store(str(num), '+FLAGS', r'(\Seen)')
    finally:
        try:
            conn.close()
        except:
            pass
        conn.logout()




#**************** LOGO // do not change or it will mess up the print indents************************************************************#
intro = Label(root, text='''.::: .::::::     .:::::::               .:                .::        .::   .::       .::::::::     .:::::::    
     .::         .::    .::            .: ::           .::   .::     .::  .::        .::           .::    .::  
     .::         .::    .::           .:  .::         .::            .:: .::         .::           .::    .::  
     .::         .: .::              .::   .::        .::            .: .:           .::::::       .: .::      
     .::         .::  .::           .:::::: .::       .::            .::  .::        .::           .::  .::    
     .::         .::    .::        .::       .::       .::   .::     .::   .::       .::           .::    .::  
     .::         .::      .::     .::         .::        .::::       .::     .::     .::::::::     .::      .::
                                                                                                               ''')
intro.pack()
#**************** LOGO // do not change or it will mess up the print indents************************************************************#

tabcontrol = ttk.Notebook(root)

#*********Tabs for different Frames*******#
logs = ttk.Frame(tabcontrol)              #
tabcontrol.add(logs, text="Logs")         #
tabcontrol.pack(expand=1,fill="both")     #
#*****************************************#
maping = ttk.Frame(tabcontrol)            #
tabcontrol.add(maping, text="Map")        #
tabcontrol.pack(expand=1,fill="both")     #
#*****************************************#
settings = ttk.Frame(tabcontrol)          #
tabcontrol.add(settings, text="Settings") #
tabcontrol.pack(expand=1,fill="both")     #
#*****************************************#
rules = ttk.Frame(tabcontrol)             #
tabcontrol.add(rules, text="Rules")       #
tabcontrol.pack(expand=1,fill="both")     # 
###########################################

# Logs         ###############################################################

log_textBox = tk.Text(logs,height=10,width=80)
log_textBox.pack(expand=True,fill='both')


#log_label_email_from = tk.Label(logs, text="Inbox")
#log_label_email_from.pack()

#log_email_from = tk.Entry(logs)
#log_email_from.pack()

log_label_email_org = tk.Label(logs, text="Email address")
log_label_email_org.pack()

log_email_org = tk.Entry(logs)
log_email_org.pack()

log_label_pass = tk.Label(logs, text="Password")
log_label_pass.pack()

log_pass = tk.Entry(logs)
log_pass.pack()

log_label_email_num = tk.Label(logs, text="Emails To Check")
log_label_email_num.pack()

log_email_num = tk.Entry(logs)
log_email_num.pack()

#log_label_port = tk.Label(logs, text="Port Number")
#log_label_port.pack()

#log_port =tk.Entry(logs)
#log_port.pack()



log_button = tk.Button(logs, text="Listen", command =runmail)
log_button.pack()

# Maps         ################################################################
# Should to print all the IP logs basically

maps_textBox = tk.Text(maping)
maps_textBox.pack()


# Settings     ################################################################
# Confirm what kind of settings we need for

confrim_email = tk.Checkbutton(settings, text='Email',var = email_selected)
confrim_email.pack(side='left')

confrim_domain = tk.Checkbutton(settings, text='Domain',var = domain_selected)
confrim_domain.pack(side='left')

confrim_state = tk.Checkbutton(settings, text='State',var = state_selected)
confrim_state.pack(side='left')

# Rules       #################################################################

rules_black_list = tk.Label(rules,text="Black List")
rules_black_list.pack(side='left',anchor ='w')

rules_black_entry = tk.Entry(rules)
rules_black_entry.pack(side='left',anchor ='w')

rules_action_apply = tk.Button(rules,text="add" ,command = blacklist_add )
rules_action_apply.pack(side='left',anchor ='w')

rules_action_remove = tk.Button(rules,text="remove",command= blacklist_remove)
rules_action_remove.pack(side='left',anchor ='w')


rules_list_email = tk.Listbox(rules)
rules_list_email.pack(side='left',anchor ='center')

rules_button_email = tk.Radiobutton(rules,text='email',variable=v, value =1)
rules_button_email.pack(side='left',anchor ='center')

rules_list_domain = tk.Listbox(rules)
rules_list_domain.pack(side='left')

rules_button_domain = tk.Radiobutton(rules,text='domain',variable=v, value =2)
rules_button_domain.pack(side='left')

rules_list_state = tk.Listbox(rules)
rules_list_state.pack(side='left')

rules_button_state = tk.Radiobutton(rules,text='state',variable=v, value = 3)
rules_button_state.pack(side='left')




# END of Program ##################################################################                                                                                                      
root.mainloop()
