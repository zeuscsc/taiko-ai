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
FAILED_BLUE=numpy.array((249,127,71))

def same_color(c1,c2):
    if c1[0]==c2[0]:
        if c1[1]==c2[1]:
            if c1[2]==c2[2]:
                return True
    return False
def similar_color(c1,c2,buffer):
    if c1[0]>=c2[0]-buffer and c1[0]<=c2[0]+buffer:
        if c1[1]>=c2[1]-buffer and c1[1]<=c2[1]+buffer:
            if c1[2]>=c2[2]-buffer and c1[2]<=c2[2]+buffer:
                return True
    return False
def press_keys(keys_stack,delay=0,interval=0):
    if math.fabs(delay)>0:
        # print(delay)
        time.sleep(math.fabs(delay))
    pyautogui.write(keys_stack,math.fabs(interval))
    return
def save_debug_img(img):
    global frame_count
    img_display=img.copy()
    img_display=cv2.resize(img_display,(530,100))
    cv2.imwrite(f"./samples/{frame_count}.png",img_display)
    frame_count+=1
    return
SAMPLE_SIZE=10
frame_count=0
last_time = time.time()
delta_time=0
average_delta_time=0
last_beat_line_position=0
average_skipped_pixals_count=0
velocity=0
left_beat=True
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
            average_skipped_pixals_count=\
                math.floor((average_skipped_pixals_count*SAMPLE_SIZE+skipped_pixals_count)/(SAMPLE_SIZE+1))
            # print(average_difference_beat_pixal)
        monitor_width=180#120
        # if monitor_width<average_skipped_pixals_count:
        #     monitor_width=average_skipped_pixals_count
        # if 120+math.fabs(average_skipped_pixals_count)<180:
        border_width=30
        monitor_width=120-average_skipped_pixals_count+border_width
        # print(monitor_width)
        # if average_skipped_pixals_count<0:
        #     print(average_skipped_pixals_count)
        #640
        monitor = {"top": 590, "left": 640-(border_width*2)-average_skipped_pixals_count,
                    "width": monitor_width, "height": 1}
        taiko_img = numpy.array(sct.grab(monitor))
        taiko_row=taiko_img[0]
        distance_pixal=0
        last_distance_pixal=0
        delay=0
        interval=0
        interval_threshold=0
        if velocity<0:
            interval_threshold=(average_skipped_pixals_count-border_width)/velocity
        for pixal in taiko_row:
            if same_color(pixal,ORANGE):
                if len(keys_stack)<50 and distance_pixal>30:
                    keys_stack.append("f")
                    keys_stack.append("j")
                    seen_white=False
            if same_color(pixal,GOLDEN) and distance_pixal>30:
                if len(keys_stack)<10:
                    keys_stack.append("f")
                    keys_stack.append("j")
                    seen_white=False
            if same_color(pixal,RED):
                holding_color=RED
                seen_white=False
            if same_color(pixal,BLUE):
                holding_color=BLUE
                seen_white=False
            if similar_color(pixal,WHITE,30):
                seen_white=True
            if similar_color(pixal,BLACK,60):
                if seen_white:
                    seen_white=False
                    if same_color(holding_color,RED):
                        if left_beat:
                            keys_stack.append("f")
                            left_beat=False
                        else:
                            keys_stack.append("j")
                            left_beat=True
                        if velocity<0:
                            if delay==0:
                                delay=(distance_pixal-30)/velocity
                            interval=(distance_pixal-last_distance_pixal)/velocity
                            last_distance_pixal=distance_pixal
                            pass
                        # keys_stack.append("j")
                        # save_debug_img(taiko_img)
                    if same_color(holding_color,BLUE):
                        if left_beat:
                            keys_stack.append("d")
                            left_beat=False
                        else:
                            keys_stack.append("k")
                            left_beat=True
                        if velocity<0:
                            if delay==0:
                                delay=(distance_pixal-30)/velocity
                            interval=(distance_pixal-last_distance_pixal)/velocity
                            last_distance_pixal=distance_pixal
                            pass
                        # keys_stack.append("k")
                        # save_debug_img(taiko_img)
                    pass
            distance_pixal+=1
        # monitor = {"top": 450, "left": 699,
        #             "width": 1, "height": 1}
        # fail_check_img = numpy.array(sct.grab(monitor))
        # if similar_color(fail_check_img[0][0],FAILED_BLUE,40):
        #     save_debug_img(taiko_img)
        if len(keys_stack)>0:
            # print(velocity,delay,interval)
            # velocity=0
            delay=0
            if math.fabs(interval)>math.fabs(interval_threshold):
                interval=0
            x = threading.Thread(target=press_keys, args=(keys_stack,delay,interval))
            x.start()
        delta_time=time.time()-last_time
        average_delta_time=(average_delta_time*SAMPLE_SIZE+delta_time)/(SAMPLE_SIZE+1)
        if average_skipped_pixals_count<0:
            velocity=average_skipped_pixals_count/average_delta_time
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break