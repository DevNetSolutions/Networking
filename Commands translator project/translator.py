import paramiko
import sqlite3
import os
import threading
import time
import hashlib
from llama_cpp import Llama
from urllib.request import urlretrieve
from http.server import HTTPServer, SimpleHTTPRequestHandler


#ASCII logo 
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
RESET = "\033[0m"

website = ("https://www.devnetsolutions.net")
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
print(GREEN + website + RESET)
print (" ")
print (RED, "[~~]For listing configurations from database type 'read_configs", RESET)
print (RED, "[~~]For switching between manual and AI assisted mode, type 'automate' or 'deepseek' in the command prompt", RESET)
print (" ")


#deepseek-coder download and verify
print("[~~]Downloading model, please wait...")
try:
    url = ("https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF/resolve/main/deepseek-coder-1.3b-instruct.Q5_K_M.gguf")
    model_name = ("deepseek-coder-1.3b-instruct.Q5_K_M.gguf")
    model_licence = ("https://raw.githubusercontent.com/deepseek-ai/deepseek-coder/refs/heads/main/LICENSE-MODEL")
    model_licence_name = ("LICENSE-MODEL")
    gguf_sha = ("d5dcc2a484498b412b8bf5821b0ef2a7ea2e1984b37d15e14344259068d19a31")
    if model_name not in os.listdir():
        urlretrieve(url, model_name)
        print(RED, "[~~]Model downloaded successfully", RESET)
    else:
        print(RED, "[~~]Model already exists", RESET)
    if model_licence_name not in os.listdir():
        urlretrieve(model_licence, model_licence_name)
        print(RED, "[~~]Model licence downloaded successfully", RESET)
    else:
        print(RED, "[~~]Model licence already exists", RESET)
    file_check = hashlib.sha256(open(model_name, "rb").read()).hexdigest()
    if str(file_check) == (gguf_sha):
        print(GREEN, "[~~]Model integrity verified", RESET)
    else:
        print(RED, "[~~]Model integrity verification failed, removing file...", RESET)
        os.remove(model_name)
except Exception as e:
    print(RED, "[~~]Connection error", RESET)

print(" ")
print ("[~~]Initializing ssh connection:")


#Auth, commands file and connection settings
host = input("[~~]Host: ")
username = input("[~~]Username: ")
password = input("[~~]Password: ")
cisco_cmd = []
found = False
cleaned = None
dev_ip = []
con = sqlite3.connect("networks.db")
cur = con.cursor()
networks_db = ("""CREATE TABLE IF NOT EXISTS Configurations(id_config INTEGER PRIMARY KEY AUTOINCREMENT, device_model TEXT, config TEXT, created_on DATE)""")
con.execute(networks_db)
con.commit()
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
llm = Llama(
    model_path="deepseek-coder-1.3b-instruct.Q5_K_M.gguf",
    n_ctx=4096,
    n_threads=8,     
#   n_gpu_layers=35   #USE THIS IF FOR USING GPU, COMMENT OUT IF USING CPU ONLY
)

try:
    ssh.connect(hostname = host , port=22, username = username, password = password, timeout=3)
except Exception as e:
    print("[~~]Failed to connect to " + host, e)
    exit()


#open mikrotik and cisco commands
def read():
    print ("[~~]Available commands files: ")
    print(RED, "[~~]mikrotik / juniper / aruba_hp / huawei_vrp", RESET)
    choose_file = input("[~~]Commands file: ")
    path  = os.path.join("Commands files/", choose_file + ".txt")
    with open(path) as cisco_read:
        for res in cisco_read:
            cisco_cmd.append(res.strip())
        return cisco_cmd


def automate_read():
    config_file_path = os.path.join("Commands files/", "config.txt")
    with open(config_file_path) as automate_read:
        configuration = automate_read.read()
        return configuration


def automate():
    file = automate_read()
    prompt = (f"Translate the configuration in {file} to mikrotik syntax ")
    response = llm(prompt)
    translated_config = response['choices'][0]['text'].strip()
    return translated_config


def automate_save():
    translate_config_file = os.path.join("Commands files/", "translated_config.txt")
    with open(translate_config_file, "w") as f2:
            f2.write(automate())


def serve_file(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler): 
    os.chdir("Commands files")
    server_ip = input("[~~]Type ip address for serving: ")
    server_address = (server_ip, 8000)
    httpd = server_class(server_address, handler_class)
    print(f"[~~]Serving file at http://{server_ip}:8000/")
    httpd.handle_request()
    httpd.close()


def read_configurations_from_db():
    cur.execute("SELECT * FROM Configurations")
    rows = cur.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Device Model: {row[1]}, Configuration: {row[2]}, Created On: {row[3]}")


def deepseek_prompt():
    print ("[~~]Switching to AI assisted mode...")
    print (" ")
    print ("[~~]Model used: 'deepseek-coder-1.3b-instruct.Q5_K_M'...")
    print (" ")
    print (GREEN, "[~~]Commands:", RESET)
    print (RED, "[~~]'Exit' to quit ai assisted mode", RESET)
    print (RED, "[~~]'conf_dev' for router/switch configuration file creation", RESET)
    print (RED, "[~~]'unx' for Unix/Linux/Bsd configuration file creation", RESET)
    print (" ")
    while True:
        deep_prompt = input("[~~]DeepSeek Prompt: ")
        if "exit" in deep_prompt.lower() or "Exit" in deep_prompt:
            print ("[~~]Switching back to manual mode...")
            break
        response = llm(deep_prompt)
        print (response['choices'][0]['text'].strip())
        if "conf_dev!" in deep_prompt.lower():
            dev_model = input("[~~]Enter device model: ")
            date_created = input("[~~]Enter date: ")
            print ("[~~]Creating configuration file")
            deep_seek_conf_path = os.path.join("Commands files/", "deepseek_config.txt")
            with open(deep_seek_conf_path, "w") as f3:
                f3.write(response['choices'][0]['text'].strip())
            val1 = dev_model
            val2 = response['choices'][0]['text'].strip()
            val3 = date_created
            print ("[~~]Configuration file created: deepseek_config.txt")
            sql_q = ("""INSERT INTO Configurations(device_model, configuration, created_on) VALUES (?, ?, ?)""")
            values = val1, val2, val3
            con.execute(sql_q, values)
            con.commit()
            check_config = input ("Use configuration file? ")
            if check_config == "yes" or check_config == "Yes":
                print ("[~~]Configuring device with DeepSeek's response")
                stdin, stdout, stderr = ssh.exec_command(response['choices'][0]['text'].strip())
                print(stdout.read().decode())
            else:
                print("[~~]Device not configured")
                continue
        elif "unx" in deep_prompt:
            sh_scr_path = os.path.join("Commands files/", "auto_config.sh")
            with open(sh_scr_path, "w") as sh:
                sh.write(response['choices'][0]['text'].strip())
            if sh_scr_path:
                download_and_execute = ("mkdir tmp && cd tmp && wget http://{server_ip}:8000/auto_config.sh && chmod 755 auto_config.sh && ./auto_config.sh")
                serve_file()
                check_before_exec = input("[~~]Download and execute the script on device? ")
                if check_before_exec == "yes" or check_before_exec == "Yes":
                    print ("[~~]Sending configuration file to device")
                    stdin, stdout, stderr = ssh.exec_command(download_and_execute)
                    print("[~~]Device configured")
                    print(stdout.read().decode())
                    print ("[~~]Switching back to manual mode...")
            break


                    
res = read()
while True:
    content = input("[~~]Cmd: ")
    file_cmd = []
    found = False

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
    if content == ("read_configs") or content == ("Read_configs"):
        read_configurations_from_db()
    if content == ("automate") or content == ("Automate"):
        automate_save()
    if content == ("deepseek") or content == ("Deepseek"):
        print ("[~~]Type 'exit' to exit DeepSeek prompt")
        deepseek_prompt()
    elif content == ("quit") or content == ("Quit"):
        ssh.close()
        break

    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())



