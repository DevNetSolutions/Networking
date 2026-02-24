#import paramiko

#ASCII logo 
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
RESET = "\033[0m"

logo = ("""@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@/***************************************************/@@@
@@*********************************************************@
@**********************************************************@
@************&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/**********@
@*********(@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#********@
@*********@@@*****@@@@@*****@@@@@*****@@@@@*****@@@********@
@*********@@@*****@@@@@*****@@@@@*****@@@@@*****@@@********@
@*********@@@*****@@@@@*****@@@@@*****@@@@@*****@@@********@
@*********@@@*****@@@@@*****@@@@@*****@@@@@*****@@@********@
@*********@@@*****@@@@@*****@@@@@*****@@@@@*****@@@********@
@*********@@@*****@@@@@*****@@@@@*****@@@@@*****@@@********@
@*********@@@*****@@@@@*****@@@@@*****@@@@@*****@@@********@
@*********@@@***********************************@@@********@
@*********@@@***********************************@@@********@
@*********@@@***********************************@@@********@
@*********@@@@*********************************&@@@********@
@**********(@@@@@@@***********************@@@@@@@#*********@
@***************@@@***********************@@@/*************@
@***************@@@***********************@@@/*************@
@***************@@@/**********************@@@**************@
@****************@@@@@@@@@@@@@@@@@@@@@@@@@@@***************@
@**********************************************************@
@%*********************************************************@
@@@*******************************************************@@
@@@@@@#**************~DevNet Solutions~***************#@@@@@""")

print(RED + logo + RESET)

print (" ")

#Auth, commands file and connection settings
host = input("[~~]Host: ")
username = input("[~~]Username: ")
password = input("[~~]Password: ")
cisco_cmd = []
found = False
cleaned = None
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(hostname = host , port=22, username = username, password = password, timeout=3)
except Exception as e:
    print("[~~]Failed to connect to " + host, e)
    exit()


#open mikrotik and cisco commands
def read():
    print ("[~~]Available commands files: ")
    print("[~~]mikrotik / juniper / aruba_hp / huawei_vrp")
    choose_file = input("[~~]Commands file: ")
    with open("Commands files/" + choose_file + ".txt") as cisco_read:
        for res in cisco_read:
            cisco_cmd.append(res.strip())
        return cisco_cmd


while True:
    content = input("[~~]Cmd: ")
    file_cmd = []
    found = False
    res = read()

    def clean():
        found_local = False 
        cleaned_local = None
        for rs in res:
            if content in rs:
                file_cmd.append(rs)
                cmd = " ".join(file_cmd)
                cleaned_local = cmd.split("~~")[0].strip()
                found_local = True  
                break
        if found_local:
            return cleaned_local  
        else:
            print ("[~~]Command not found")


    command = clean()
    if command is None:
        command = content
    if content == ("quit") or content == ("Quit"):
        ssh.close()
        break

    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())
