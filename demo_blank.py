import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

P0, P1, P2, P3 = (0,0), (0.25, 0.1), (0.25,1.0), (1,1)

def calculateBox(center:list, size:list):
    # size: h,w
    # center: x0,y0
    _ret = [center[0]-(size[0]/2), center[1]-(size[1]/2), center[0]+(size[0]/2), center[1]+(size[1]/2)] # x1,y1,x2,y2
    swap = [3,2,1,0]
    _ret = [_ret[i] for i in swap]
    return list(map(int, _ret))

def time_eq(norm_distance):
    if norm_distance > 1:
        return 1.0
    else:
        return (norm_distance/(norm_distance+1)) + 0.5

def __ease__(a,b,c,d,t):
    return (((1-t)**3)*a) + ( ((1-t)**2)*(3*t)*b ) + ( (1-t)*(3*(t**2))*c ) + ((t**3)*d)

def calculateBox(center:list, size:list):
    # size: h,w
    # center: x0,y0
    _ret = [center[0]-(size[0]/2), center[1]-(size[1]/2), center[0]+(size[0]/2), center[1]+(size[1]/2)] # x1,y1,x2,y2
    swap = [3,2,1,0]
    _ret = [_ret[i] for i in swap]
    return list(map(int, _ret))

def no_slope_pan(old, new, distance_y, length, viz=False):
    _ease_pos = []
    _ease_pos_x = []
    _ease_pos_y = []
    
    #print("===========")
    #print(old, new, length)
    #print("===========")

    for i in range(length):
        # percentage done (time):
        j = i/length
        percent_dx = __ease__(P0[1], P1[1], P2[1], P3[1], j) # percentage distance change
        new_y = old[1] + ( percent_dx * distance_y )
        #print(percent_dx, new_y)

        _ease_pos.append( [old[0], new_y] )
        _ease_pos_x.append(old[0])
        _ease_pos_y.append(new_y)

    if viz:
        plt.figure()
        #print(old, new)
        plt.scatter(_ease_pos_x, _ease_pos_y)
        plt.scatter(new[0], new[1])
        plt.scatter(old[0], old[1])
        plt.scatter(new[0], new[1], label='new')
        plt.scatter(old[0], old[1], label='old')
        plt.legend()
        plt.show()

    return _ease_pos

def pan(old, new, fps, canvas_size, viz=False):
    # timing function:
    #new = [366, 980]
    h,w = canvas_size
    old_pos_n = [old[0]/w, old[1]/h]
    new_n = [new[0]/w, new[1]/h]
    distance = np.sqrt((old[0]-new[0])**2 + (old[1]-new[1])**2)
    distance_x = new[0]-old[0]
    distance_y = new[1]-old[1]
    distance_n = np.sqrt((old_pos_n[0]-new_n[0])**2 + (old_pos_n[1]-new_n[1])**2)
    _time = time_eq(distance_n)
    # number of frames (entries) to generate 
    length = int(np.round(fps*_time))
    #print("len:", length)

    direction = 1
    #if new[1] < old[1] or new[0] < old[0]:
    #    direction = -1

    # linear equation:
    if (new[0]-old[0] == 0):
        # vertical line:
        return no_slope_pan(old, new, distance_y, length, viz=viz)

    m = (new[1]-old[1])/(new[0]-old[0])
    b = (new[1]-(m*new[0]))

    # y=mx+b -> y1=mx1 + b -> b = y1-(m*x1)

    # ease function:
    _ease_pos = []
    _ease_pos_x = []
    _ease_pos_y = []
    
    for i in range(length):
        # percentage done (time):
        j = i/length
        percent_dx = __ease__(P0[1], P1[1], P2[1], P3[1], j) # percentage distance change
        #print(percent_dx, old[0])
        new_x = old[0]+( direction*(distance_x*percent_dx) ) # adding to old pos x
        new_y = (m*new_x)+b
        new_x = int(np.round(new_x))
        new_y = int(np.round(new_y))
        _ease_pos.append( [new_x, new_y])
        _ease_pos_x.append(new_x)
        _ease_pos_y.append(new_y)

    if viz:
        plt.figure()
        #print(old, new)
        plt.scatter(_ease_pos_x, _ease_pos_y)
        plt.scatter(new[0], new[1], label='new')
        plt.scatter(old[0], old[1], label='old')
        plt.legend()
        plt.show()

    return _ease_pos

def initializeVideo(videoName, videoSize, fps:int):
    height, width = videoSize 
    videoWriter = cv2.VideoWriter(videoName,cv2.VideoWriter_fourcc(*"MP4V"), fps, (width, height))
    return videoWriter

if __name__ == '__main__':
    canvas_size = (1080,1920) # h,w
    fps = 30
    videoWriter = initializeVideo("test.mp4", canvas_size, fps)
    box0 = (300,300)
    box0_wh = (300,300)
    box1 = (1000,1000)
    box1_wh = (100,100)
    
    box_wh = pan(box0_wh, box1_wh, fps, canvas_size) # width/height progression
    box_pos = pan(box0, box1, fps, canvas_size, viz=True)

    # animation variables:
    intermediate_idx = 0

    max_idx = max(len(box_wh), len(box_pos))

    for i in range(max_idx):
        _canvas = np.zeros((canvas_size[0], canvas_size[1], 3), dtype=np.uint8)
        if i >= len(box_wh): _size = box_wh[-1]
        else: _size = box_wh[i]
        _size = list(map(int, _size))

        if i >= len(box_pos): _pos = box_pos[-1]
        else: _pos = box_pos[i]
        _pos = list(map(int, _pos))

        box = calculateBox(_pos, _size)
        print(box)
        cv2.rectangle(_canvas, (box[0], box[1]), (box[2], box[3]),(0,0,255), thickness=2)
        #cv2.rectangle(frame0, (_box2[0], _box2[1]), (_box2[2], _box2[3]),(0,255,0), thickness=2)
        cv2.circle(_canvas, (_pos[1], _pos[0]), 5, (0,0,255), thickness=-1)

        cv2.imshow('test', _canvas)
        cv2.waitKey(10)
        videoWriter.write(_canvas)
    videoWriter.release()