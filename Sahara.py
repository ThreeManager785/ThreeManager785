from microbit import *
import radio
import music

# User Config
# Type: 0 Recipient, 1 Listener (MITM), 2 Sender

endpointUserType = 1
silence = True
radioGroup = 0

# The Message to Send (For Sender Only)
sendPendingMessage = "Whereas recognition of the inherent dignity and of..."
    
def SaharaEncrypt(plaintext, key):
    key = (key * (len(plaintext) // len(key))) + key[:len(plaintext) % len(key)]

    ciphertext = []
    for i in range(len(plaintext)):
        pt_char = plaintext[i]
        key_char = key[i]

        if pt_char.isalpha():
            shift = ord(key_char.lower()) - ord('a') 
            if pt_char.islower():
                encrypted_char = chr(((ord(pt_char) - ord('a') + shift) % 26) + ord('a'))
            else:
                encrypted_char = chr(((ord(pt_char) - ord('A') + shift) % 26) + ord('A'))
            ciphertext.append(encrypted_char)
        else:
            ciphertext.append(pt_char)
    
    return ''.join(ciphertext)


def SaharaDecrypt(cipherText, key):
    key = (key * (len(cipherText) // len(key))) + key[:len(cipherText) % len(key)]

    plaintext = []
    for i in range(len(cipherText)):
        ctChar = cipherText[i]
        keyChar = key[i]

        if ctChar.isalpha():
            shift = ord(keyChar.lower()) - ord('a')
            if ctChar.islower():
                decrypted_char = chr(((ord(ctChar) - ord('a') - shift) % 26) + ord('a'))
            else:
                decrypted_char = chr(((ord(ctChar) - ord('A') - shift) % 26) + ord('A'))
            plaintext.append(decrypted_char)
        else:
            plaintext.append(ctChar)
    
    return ''.join(plaintext)
    
key = "QRcmPtdngqAiyddQDfJFCAXrBiATnFhpNEoRZwWdGBvZNKXkppWDtCHfxWfgvRmEYjNiYiFfHainhdtyHrcUxHBpZMTnoGpsomqc" 


def CaesarDecrypt(text, offset):
    plainText = []
    for i in range(len(text)):
        keyChar = text[i]
        if keyChar.isalpha():
            if keyChar.islower():
                decryptedChar = chr(((ord(keyChar) - ord('a') - offset) % 26) + ord('a'))
            else:
                decryptedChar = chr(((ord(keyChar) - ord('A') - offset) % 26) + ord('A'))
            plainText.append(decryptedChar)
        else:
            plainText.append(keyChar)
    return ''.join(plainText)

def CaesarCrack(text, inputPrefix=""):
    indexScrollSleepingTime = 2500
    
    print("----------------------")
    display.show(Image.DIAMOND)
    if not silence:
        music.pitch(330)
    if inputPrefix=="":
        prefix = text[:3] + "."
    else:
        prefix = inputPrefix

    vowelRatios = {}
    for i in range(26):
        vowelRatios[i] = vowelRatio(CaesarDecrypt(text, i))

    sortedRatios = sorted(vowelRatios.items(), key=lambda item: item[1], reverse=True)

    for key in sortedRatios:
        print("[CaCr][" + prefix + "][" + str(key[0]) + "][" + str(key[1]) + "%]", CaesarDecrypt(text, key[0]))

    onFocusIndex = 0

    sleep(400)
    music.stop()
    display.scroll(str(onFocusIndex) + "!", wait=False)
    sleep(indexScrollSleepingTime)
    display.scroll(CaesarDecrypt(text, sortedRatios[onFocusIndex][0]), wait=False)

    crackingMessageIsChecking = True
    while crackingMessageIsChecking:
        message = radio.receive()
        if message:
            crackingMessageIsChecking = False
            CaesarCrack(message)
        if pin_logo.is_touched():
            crackingMessageIsChecking = False
            display.show(Image.ASLEEP)
        elif button_a.is_pressed():
            onFocusIndex = (onFocusIndex - 1) % 26
            display.scroll(str(onFocusIndex) + "!", wait=False)
            sleep(indexScrollSleepingTime)
            display.scroll(CaesarDecrypt(text, sortedRatios[onFocusIndex][0]), wait=False)
        elif button_b.is_pressed():
            onFocusIndex = (onFocusIndex + 1) % 26
            display.scroll(str(onFocusIndex) + "!", wait=False)
            sleep(indexScrollSleepingTime)
            display.scroll(CaesarDecrypt(text, sortedRatios[onFocusIndex][0]), wait=False)

            

def vowelRatio(text: str) -> float:
    vowels = set("aeiouAEIOU")
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 0.0
    count = sum(ch in vowels for ch in letters)
    ratio = (count / len(letters)) * 100
    return round(ratio, 1)

radio.config(group=radioGroup)
radio.on()
lastDecryptedMessage = ""

if True:
    if endpointUserType==0:
        print("User: RCP (0)")
    elif endpointUserType==1:
        print("User: LST (1)")
    elif endpointUserType==2:
        print("User: SND (2)")
    print("Radio Group:", radioGroup)
    print("Silent:", silence)

    
if endpointUserType != 2:
   while True:
        if (endpointUserType==0) and button_a.is_pressed() and button_b.is_pressed():
            display.scroll(lastDecryptedMessage, wait=False)
        message = radio.receive()
        if message:
            # display.scroll(message)
            print("----------------------")
            if endpointUserType==0:
                print("[RCP][#" + str(radioGroup) + "]:", message)
                display.show(Image.YES)
                if not silence:
                    music.pitch(330)
                lastDecryptedMessage = SaharaDecrypt(message, key)
                sleep(400)
                music.stop()
                print("[RCP][DEC]:", lastDecryptedMessage)
                display.scroll(lastDecryptedMessage, wait=False)
                for i in range(10):
                    print(".")
            elif endpointUserType==1:
                print("[LSN][#" + str(radioGroup) + "]", message)
                CaesarCrack(message)
else:
    print("[SND][#" + str(radioGroup) + "]", sendPendingMessage)
    print("[SND][ENC]", SaharaEncrypt(sendPendingMessage, key))   
    radio.send(SaharaEncrypt(sendPendingMessage, key))
    for i in range(10):
        print(".")
    print("[SND][#" + str(radioGroup) + "] Sent.")

