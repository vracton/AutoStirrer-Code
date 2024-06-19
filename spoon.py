import digitalio
import board
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
    ]
motor = digitalio.DigitalInOut(board.GP19)
motor.direction = digitalio.Direction.OUTPUT
for i in dig1:
    i.direction = digitalio.Direction.OUTPUT
for i in dig2:
    i.direction = digitalio.Direction.OUTPUT
btn = digitalio.DigitalInOut(board.GP27)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP

def setDig(pins, num):
    global digits
    for i in range(len(digits[num])):
        pins[i].value = bool(int(digits[num][i]))

btnWasDown = False
actionDone = False
btnDownTime = 0
timerStart = 0

state = "main"
dig1[7].value = True
dig2[7].value = True
dig1[8].value = True
dig2[8].value = True
setDig(dig2,10)
setDig(dig1,10)

while True:
    if not btn.value:
        if not btnWasDown:
            btnWasDown = True
            actionDone = False
            btnDownTime = time.monotonic()
        elif time.monotonic()-btnDownTime > 1 and not actionDone:
            actionDone = True
            if state == "main":
                state="timer"
                setDig(dig1,0)
                setDig(dig2,2)
                timerStart = time.monotonic()
    elif btnWasDown:
        btnWasDown = False
        if not actionDone:
            downTime = time.monotonic()-btnDownTime
            print(downTime)
    if state == "timer":
        timeDur = time.monotonic()-timerStart
        if timeDur < 14*60: #minutes display
            dig1[7].value = math.floor((timeDur))%2==0
            clockTime = 2 - math.floor((time.monotonic()-timerStart)/60)
            setDig(dig1, math.floor(clockTime/10))
            setDig(dig2, clockTime%10)
        else #seconds display
            dig1[7].value = True
            clockTime = 60 - math.floor((time.monotonic()-timerStart-14*60))
            setDig(dig1, math.floor(clockTime/10))
            setDig(dig2, clockTime%10)
  