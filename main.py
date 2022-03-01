import time
import pyautogui
import cv2
import mss
import numpy
import threading
import math

BEAT_MONITOR={"top": 500, "left": 1470, "width": 1080, "height": 1}
RED=numpy.array((40,71,243))
BLUE=numpy.array((187,189,101))
WHITE=numpy.array((224,239,247))
BLACK=numpy.array((0,0,0))
GOLDEN=numpy.array((0,181,243))
ORANGE=numpy.array((0,119,248))

GREY=numpy.array((189,189,189))

BUFFER=100
def same_color(c1,c2):
    if c1[0]==c2[0]:
        if c1[1]==c2[1]:
            if c1[2]==c2[2]:
                return True
    return False
def similar_color(c1,c2):
    if c1[0]>=c2[0]-BUFFER and c1[0]<=c2[0]+BUFFER:
        if c1[1]>=c2[1]-BUFFER and c1[1]<=c2[1]+BUFFER:
            if c1[2]>=c2[2]-BUFFER and c1[2]<=c2[2]+BUFFER:
                return True
def press_keys(keys_stack):
    pyautogui.write(keys_stack)
    return
def save_debug_img(img):
    global frame_count
    img_display=img.copy()
    img_display=cv2.resize(img_display,(530,100))
    cv2.imwrite(f"./samples/{frame_count}.png",img_display)
    frame_count+=1
    return
frame_count=0
last_time = time.time()
delta_time=0
last_beat_line_position=0
average_skipped_pixals_count=0
with mss.mss() as sct:
    while "Screen capturing":
        last_time = time.time()
        beat_img=numpy.array(sct.grab(BEAT_MONITOR))
        beat_row=beat_img[0]
        seen_white=False
        holding_color=BLACK
        keys_stack=[]
        position=0
        skipped_pixals_count=0
        for pixal in beat_row:
            if same_color(pixal,GREY):
                beat_line_position=position
                skipped_pixals_count=beat_line_position-last_beat_line_position
                last_beat_line_position=beat_line_position
                break
            position+=1
            pass
        
        if skipped_pixals_count<0:
            average_skipped_pixals_count=math.floor((average_skipped_pixals_count*10+skipped_pixals_count)/11)
            # print(average_difference_beat_pixal)
        monitor = {"top": 590, "left": 702+average_skipped_pixals_count,
                    "width": 100-math.floor(average_skipped_pixals_count*1.25), "height": 1}
        taiko_img = numpy.array(sct.grab(monitor))
        taiko_row=taiko_img[0]
        for pixal in taiko_row:
            if same_color(pixal,ORANGE):
                if len(keys_stack)<20:
                    keys_stack.append("f")
                    keys_stack.append("j")
            if same_color(pixal,GOLDEN):
                if len(keys_stack)<10:
                    keys_stack.append("f")
                    keys_stack.append("j")
            if same_color(pixal,RED):
                holding_color=RED
                seen_white=False
            if same_color(pixal,BLUE):
                holding_color=BLUE
                seen_white=False
            if similar_color(pixal,WHITE):
                seen_white=True
            if similar_color(pixal,BLACK):
                if seen_white:
                    seen_white=False
                    if same_color(holding_color,RED):
                        keys_stack.append("f")
                        # keys_stack.append("j")
                        # save_debug_img(taiko_img)
                    if same_color(holding_color,BLUE):
                        keys_stack.append("d")
                        # keys_stack.append("k")
                        # save_debug_img(taiko_img)
        if len(keys_stack)>0:    
            x = threading.Thread(target=press_keys, args=(keys_stack,))
            x.start()
        delta_time=time.time()-last_time
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break