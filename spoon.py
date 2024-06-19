import digitalio
import board
import audiomp3
import audiopwmio
import math
import time

dig2 = [
    digitalio.DigitalInOut(board.GP7),#a
    digitalio.DigitalInOut(board.GP8),
    digitalio.DigitalInOut(board.GP10),
    digitalio.DigitalInOut(board.GP11),
    digitalio.DigitalInOut(board.GP12),
    digitalio.DigitalInOut(board.GP5),
    digitalio.DigitalInOut(board.GP4),#g
    digitalio.DigitalInOut(board.GP9),#dp
    digitalio.DigitalInOut(board.GP6),#power
    ]
dig1 = [
    digitalio.DigitalInOut(board.GP2),
    digitalio.DigitalInOut(board.GP3),
    digitalio.DigitalInOut(board.GP14),
    digitalio.DigitalInOut(board.GP16),
    digitalio.DigitalInOut(board.GP17),
    digitalio.DigitalInOut(board.GP1),
    digitalio.DigitalInOut(board.GP0),
    digitalio.DigitalInOut(board.GP13),
    digitalio.DigitalInOut(board.GP15),
    ]
spin = [dig2[0],dig2[1],dig2[2],dig2[3],dig1[7],dig1[3],dig1[4],dig1[5],dig1[0]]
digits = [
    ["0","0","0","0","0","0","1"],
    ["1","0","0","1","1","1","1"],
    ["0","0","1","0","0","1","0"],
    ["0","0","0","0","1","1","0"],
    ["1","0","0","1","1","0","0"],
    ["0","1","0","0","1","0","0"],
    ["0","1","0","0","0","0","0"],
    ["0","0","0","1","1","1","1"],
    ["0","0","0","0","0","0","0"],
    ["0","0","0","0","1","0","0"],
    ["1","1","1","1","1","1","1"],#clear
    ["1","0","0","1","0","0","0"],#H
    ["1","1","1","1","0","0","1"],#I
    #spin
    ["0","0","0","0","1","1","1","1","1"],#13
    ["1","0","0","0","0","1","1","1","1"],
    ["1","1","0","0","0","0","1","1","1"],
    ["1","1","1","0","0","0","0","1","1"],
    ["1","1","1","1","1","0","0","0","0"],
    ["0","1","1","1","1","1","0","0","0"],
    ["0","0","1","1","1","1","1","0","0"],
    ["0","0","0","1","1","1","1","1","0"],#20
    ]
motor = digitalio.DigitalInOut(board.GP19)
motor.direction = digitalio.Direction.OUTPUT
for i in dig1:
    i.direction = digitalio.Direction.OUTPUT
for i in dig2:
    i.direction = digitalio.Direction.OUTPUT
audio = audiopwmio.PWMAudioOut(board.GP18)
decoder = audiomp3.MP3Decoder(open("slow.mp3", "rb"))
btn = digitalio.DigitalInOut(board.GP27)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP

def setDig(pins, num):
    global digits
    for i in range(len(digits[num])):
        pins[i].value = bool(int(digits[num][i]))
spinNum=12
def nextSpin():
    setDig(dig2,10)
    setDig(dig1,10)
    global spinNum
    spinNum+=1
    if spinNum > 20:
        spinNum = 13;
    setDig(spin,spinNum)
#motor.value = True

btnWasDown = False
actionDone = False
btnDownTime = 0
timerStart = 0

state = "main"
dig1[7].value = True
dig2[7].value = True
dig1[8].value = True
dig2[8].value = True
setDig(dig2,12)
setDig(dig1,11)

while True:
    if not btn.value:
        if not btnWasDown:
            btnWasDown = True
            actionDone = False
            btnDownTime = time.monotonic()
        elif time.monotonic()-btnDownTime > 1 and not actionDone:
            actionDone = True
            if state == "main":
                state="spin"
                setDig(dig1,0)
                setDig(dig2,2)
                timerStart = time.monotonic()
                motor.value = True
                while time.monotonic()-timerStart < 2:
                    nextSpin()
                    time.sleep(0.1)
                motor.value = False
                state = "done"
                audio.play(decoder, loop=True)
                timerStart = time.monotonic()
            else:
                state = "main"
                audio.stop()
                setDig(dig2,12)
                setDig(dig1,11)
    elif btnWasDown:
        btnWasDown = False
        if not actionDone:
            downTime = time.monotonic()-btnDownTime
            if state == "done":
                state = "main"
                audio.stop()
                setDig(dig2,12)
                setDig(dig1,11)
    if state == "timer":
        timeDur = time.monotonic()-timerStart
        if timeDur < 1*60:#first dur 8 mins
            dig1[7].value = math.floor((timeDur))%2==0
            clockTime = 3 - math.floor((time.monotonic()-timerStart)/60)#change 1 to 60
            setDig(dig1, math.floor(clockTime/10))
            setDig(dig2, clockTime%10)
        else:
            state = "spin"
            timerStart = time.monotonic()
            motor.value = True
            while time.monotonic()-timerStart <10:
                nextSpin()
                time.sleep(0.1)
            motor.value = False
            state = "timer2"
            timerStart = time.monotonic()
    elif state == "timer2":
        timeDur = time.monotonic()-timerStart
        if timeDur < 1*60:#2nd dur 6mins
            dig1[7].value = math.floor((timeDur))%2==0
            clockTime = 2 - math.floor((time.monotonic()-timerStart)/60)#change 1 to 60
            setDig(dig1, math.floor(clockTime/10))
            setDig(dig2, clockTime%10)
        elif timeDur < 2*60:#3rd dir 1 min
            dig1[7].value = True
            clockTime = 60 - math.floor((time.monotonic()-timerStart-1*60))#change 1 to 60
            setDig(dig1, math.floor(clockTime/10))
            setDig(dig2, clockTime%10)
        else:
            state = "done"
            audio.play(decoder, loop=True)
    elif state == "done":
        dig1[7].value = True
        timeDur = time.monotonic()-timerStart
        setDig(dig1,math.floor((timeDur))%2*10)
        setDig(dig2,math.floor((timeDur))%2*10)
