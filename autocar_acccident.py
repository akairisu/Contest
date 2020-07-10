from vpython import *
import random
import math
import copy

scene2 = canvas(title = 'Simulation', width = 600, height = 200, center = vector(0,0,0), background = color.black)
random.seed(8)

#define constant
STOP = 0
CONSTANT = 1
INCREASE = 2
DECREASE = 3
ACCIDENT = 4
TRANSFER = 5
AUTO = 0
HUMAN = 1
CAR_LEN = 4.5
CAR_WIDTH = 1.8
INITDEN = 1
LANE_NUM = 2
REFLECT = 0.75
LANE_WIDTH = 3.65
TURN_ANGLE = radians(45)
SAFEDIS = 15
AUTODIS = 5  #AUTODIS denotes the distance between AUTOCAR and its front car
WAITDIS = 20
ROTATETIME = 200


#define parameter
Time = 100
Len = 60
Initspd = 10
Accel = 10
transfer_accel = 10
Percent = 50
RedLight = 10
GreenLight = 10
Carnum = 10
accident = 0
dt = 0.001

#define often-used function
def SPD_per_Second(speed):
    return (speed * 1000 / 3600)

def reflec():
    t = 0.75 * random.random() + 1.25
    return t

def random_type():
	if random.random() * 100 > Percent:
		return HUMAN
	else:
		return AUTO

def is_red(nowtime):
    if (math.floor(nowtime * 100) % (RedLight * 100 + GreenLight * 100)) / 100 >= GreenLight:
        return True
    else:
        return False

def LANE_POS(i):
    return 10 - LANE_WIDTH * i
    
    
    
#Initial State

car_list = []
newcarindex = []
firstcar = []
transfer_pos = []

for i in range(0, LANE_NUM):
	newcarindex.append(Carnum)
	firstcar.append(0)

for i in range(0, LANE_NUM):
    car_list.append([])
    transfer_pos.append([])
    for j in range(0, Carnum):
        TYPE = random_type()

        if j != 0:
            frontpos = car_list[i][j - 1].pos.x
        else:
            frontpos = Len - random.random() * CAR_LEN

        if TYPE == AUTO:
            car = ellipsoid(TYPE = TYPE, STAT = CONSTANT, size = vec(CAR_LEN, CAR_WIDTH, 1 ), pos = vec(frontpos - AUTODIS - random.random() * CAR_LEN, LANE_POS(i), 0), v = vec(Initspd, 0, 0))
        else:
            car = box(TYPE = TYPE, STAT = CONSTANT, length = CAR_LEN, width = 1, height = CAR_WIDTH, pos = vec(frontpos - SAFEDIS - random.random() * CAR_LEN, LANE_POS(i), 0), v = vec(Initspd, 0, 0))

        car.color = color.blue
        car_list[i].append(car)
        transfer_pos[i].append(vec(math.inf, math.inf, math.inf))
        
wall = box(length = 4, width = 1, height = 40, pos = vec(Len + 1, 0, 0), color = color.red)

carindex = []
for i in range(0, LANE_NUM):
    car = box(length = CAR_LEN, width = 1, height = 2, pos = vec(Len, 12 - LANE_WIDTH * i, 0), v = vec(Initspd, 0, 0), color = color.white)
    carindex.append(car)

nexttype = []
for i in range(0, LANE_NUM):
    TYPE = random_type()
    nexttype.append(TYPE)

decrease_time = {}
increase_time = {}
counttime = 0
accident_time = 0
accident_lane = -1
accident_pos = vec(math.inf, math.inf, math.inf)
acctdent_front_pos = vec(math.inf, math.inf, math.inf) 
transfer_lane = -1
corresponding = (math.inf, math.inf)
corresponding_return = (math.inf, math.inf)
finish_insert = 0
finish_return = 0
trans_lane_pos = math.inf
cur_lane_pos = math.inf

#Start Simulation
while True:
    rate(1 / dt)    # set animation rate = 1 / dt
    counttime = counttime + dt
    if counttime >= Time:
    	break
    if (is_red(counttime) == True):
        wall.color = color.red
    else:
        wall.color = color.green
        
    if GreenLight - (math.floor(counttime * 100) % (RedLight * 100 + GreenLight * 100)) / 100 > 0:
        nextredt = GreenLight - (math.floor(counttime * 100) % (RedLight * 100 + GreenLight * 100)) / 100
    else:
        nextredt = 0
    
    if finish_insert == 1:
        
        temp_dict = {}
        for k in decrease_time.keys():
            if k[0] == accident_lane and k[1] > corresponding[0]:
                temp_dict[(k[0], k[1] - 1)] = decrease_time[k]
            if k[0] == transfer_lane and k[1] > corresponding[1]:
                temp_dict[(k[0], k[1] + 1)] = decrease_time[k]
        decrease_time = copy.deepcopy(temp_dict)
        temp_dict = {}
        for k in increase_time.keys():
            if k[0] == accident_lane and k[1] > corresponding[0]:
                temp_dict[(k[0], k[1] - 1)] = increase_time[k]
            if k[0] == transfer_lane and k[1] > corresponding[1]:
                temp_dict[(k[0], k[1] + 1)] = increase_time[k]
        increase_time = copy.deepcopy(temp_dict)
        
        car_list[accident_lane][corresponding[0]].rotate(axis = vec(0, 1, -1), angle = -TURN_ANGLE)
        
        
        car_list[transfer_lane].insert(corresponding[1], car_list[accident_lane][corresponding[0]])
        transfer_pos[transfer_lane].insert(corresponding[1], vec(math.inf, math.inf, math.inf))
        
        del car_list[accident_lane][corresponding[0]]
        del transfer_pos[accident_lane][corresponding[0]]
        
        corresponding = (math.inf, math.inf)
        
        finish_insert = 0
        
        
    if finish_return == 2:
        
        temp_dict = {}
        for k in decrease_time.keys():
            if k[0] == transfer_lane and k[1] > corresponding_return[0]:
                temp_dict[(k[0], k[1] - 1)] = decrease_time[k]
            if k[0] == accident_lane and k[1] > corresponding_return[1]:
                temp_dict[(k[0], k[1] + 1)] = decrease_time[k]
        decrease_time = copy.deepcopy(temp_dict)
        temp_dict = {}
        for k in increase_time.keys():
            if k[0] == transfer_lane and k[1] > corresponding_return[0]:
                temp_dict[(k[0], k[1] - 1)] = increase_time[k]
            if k[0] == accident_lane and k[1] > corresponding_return[1]:
                temp_dict[(k[0], k[1] + 1)] = increase_time[k]
        increase_time = copy.deepcopy(temp_dict)
        if corresponding != (math.inf, math.inf):
            corresponding = (corresponding[0] + 1, corresponding[1] - 1)
        
        car_list[transfer_lane][corresponding_return[0]].rotate(axis = vec(0, 1, -1), angle = TURN_ANGLE)
        
        
        car_list[accident_lane].insert(corresponding_return[1], car_list[transfer_lane][corresponding_return[0]])
        transfer_pos[accident_lane].insert(corresponding_return[1], vec(math.inf, math.inf, math.inf))
        
        del car_list[transfer_lane][corresponding_return[0]]
        del transfer_pos[transfer_lane][corresponding_return[0]]
        
        corresponding_return = (math.inf, math.inf)
        accident_backcar = (accident_backcar[0], accident_backcar[1] + 1)
        
        finish_return = 0

    
    for i in range(0, LANE_NUM):
        if accident == 0 and counttime > 3:
            accident = 1
        num_of_cars = len(car_list[i])
        for j in range(firstcar[i], num_of_cars):
        
            next_state = -1
            
            frontcarindex = j - 1
            if j != 0 and car_list[i][frontcarindex].visible == False:
                frontcarindex = -1
            
            if accident == 2 and frontcarindex != -1 and car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x < CAR_LEN:
                accident = 3
                car_list[i][frontcarindex].TYPE = car_list[i][j].TYPE = ACCIDENT
                car_list[i][frontcarindex].STAT = car_list[i][j].STAT = STOP
                car_list[i][frontcarindex].color = car_list[i][j].color = color.orange
                car_list[i][frontcarindex].v.x = car_list[i][j].v.x = 0
                accident_time = counttime
                accident_lane = i
                transfer_lane = i + 1
                accident_pos = car_list[i][j].pos
                accident_front_pos = car_list[i][j - 1].pos
                accident_backcar = (i, j + 1)

#ifdef accident happened
            if accident == 3:
                if car_list[i][j].TYPE == ACCIDENT: 
                    car_list[i][j].rotate(axis = vec(0, 1, -1), angle = 0.1)
                
                if i == accident_lane and car_list[i][j].pos.x < accident_pos.x and car_list[i][j].STAT != STOP:
                    if car_list[i][j].pos.x + (car_list[i][j].v.x ** 2 ) / (2 * Accel) + car_list[i][j].v.x * 2 * dt > accident_pos.x - 2 * CAR_LEN:
                        car_list[i][j].STAT = DECREASE
                        next_state = DECREASE
                    
                
                if (i, j) == accident_backcar:
               #     car_list[i][j].rotate(axis = vec(0, 1, -1), angle = 0.01)
                    if car_list[i][j].pos.x + (car_list[i][j].v.x ** 2 ) / (2 * Accel) + car_list[i][j].v.x * 2 * dt < accident_pos.x - 2 * CAR_LEN:
                        car_list[i][j].STAT = INCREASE
                        next_state = INCREASE
                    
                    if transfer_pos[i][j].x == math.inf:
                        if car_list[i][j].STAT == STOP:
                            transfer_pos[i][j] = vec(car_list[i][j].pos.x + LANE_WIDTH / math.tan(TURN_ANGLE), 10 - transfer_lane * LANE_WIDTH, 0)
                            for k in range(firstcar[transfer_lane], len(car_list[transfer_lane])):
                                if car_list[transfer_lane][k].pos.x + (car_list[transfer_lane][k].v.x ** 2) / (2 * Accel) <= (transfer_pos[i][j].x - 2 * CAR_LEN):
                                    corresponding = (j, k)
                                    break
                    elif corresponding != (math.inf, math.inf):
                        if transfer_pos[i][j].x <= car_list[transfer_lane][corresponding[1] - 1].pos.x - CAR_LEN:    #when B car pass
                            if car_list[i][j].axis.y >= -2.25 + TURN_ANGLE / ROTATETIME:
                                car_list[i][j].rotate(axis = vec(0, 1, -1), angle = TURN_ANGLE / ROTATETIME)
                            if car_list[i][j].pos.y > LANE_POS(transfer_lane):
                                car_list[i][j].v.x += transfer_accel * math.cos(TURN_ANGLE) * dt
                                car_list[i][j].v.y += transfer_accel * math.sin(-TURN_ANGLE) * dt
                                car_list[i][j].STAT = TRANSFER
                                next_state = TRANSFER
                            else:
                                car_list[i][j].v.y = 0
                                car_list[i][j].STAT = INCREASE
                                next_state = INCREASE
                                finish_insert = 1
                                
                if finish_return == 0:
                    if i == transfer_lane and car_list[i][j].pos.x >= accident_front_pos.x + CAR_LEN and car_list[i][j].pos.x < accident_front_pos.x + 3 * CAR_LEN:
                        if transfer_pos[i][j].x == math.inf:
                            transfer_pos[i][j] = vec(car_list[i][j].pos.x + LANE_WIDTH / math.tan(TURN_ANGLE), 10 - accident_lane * LANE_WIDTH, 0)
                            trans_lane_pos = car_list[accident_lane][accident_backcar[1] - 3].pos.x
                            cur_lane_pos = car_list[i][j - 1].pos.x
                        if trans_lane_pos > cur_lane_pos and trans_lane_pos - 2 * CAR_LEN >= transfer_pos[i][j].x:
                            finish_return = 1
                            corresponding_return = (j, accident_backcar[1] - 2)
                            
                if finish_return == 1 and (i, j) == (transfer_lane, corresponding_return[0]):    
                    if car_list[i][j].axis.y <= 2.25 - TURN_ANGLE / ROTATETIME:
                        car_list[i][j].rotate(axis = vec(0, 1, -1), angle = -TURN_ANGLE / ROTATETIME)
                    if car_list[i][j].pos.y < LANE_POS(accident_lane):
                        instant_v = (car_list[i][j].v.x ** 2 + car_list[i][j].v.y ** 2) ** 0.5 + transfer_accel * dt
                        if instant_v >= Initspd:
                            instant_v = 5
                        car_list[i][j].v.x = instant_v * math.cos(TURN_ANGLE)
                        car_list[i][j].v.y = instant_v * math.sin(TURN_ANGLE)
                        car_list[i][j].STAT = TRANSFER
                        next_state = TRANSFER
                    else:
                        car_list[i][j].v = vec(0, 0, 0)
                        car_list[i][j].STAT = STOP
                        next_state = STOP
                        finish_return = 2                             
                

                if car_list[i][j].TYPE == AUTO:
                    if next_state == -1:
                        if frontcarindex != -1:
                            cardist = car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x
                            if cardist - (car_list[i][j].v.x ** 2 - car_list[i][frontcarindex].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt < AUTODIS:
                                car_list[i][j].STAT = DECREASE
                                next_state = DECREASE
                    if next_state == -1:        
                        if (Len - (car_list[i][j].pos.x + nextredt * car_list[i][j].v.x)) >= 0:
                            lightdist = Len - car_list[i][j].pos.x
                            if lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt < 0:
                                car_list[i][j].STAT = DECREASE
                                next_state = DECREASE

                    if next_state == -1:
                        if frontcarindex != -1:
                            cardist = car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x
                            if cardist - (car_list[i][j].v.x ** 2 - car_list[i][frontcarindex].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= AUTODIS:
                                if (Len - (car_list[i][j].pos.x + nextredt * car_list[i][j].v.x)) < 0:
                                    car_list[i][j].STAT = INCREASE
                                    nexrstate = INCREASE
                                else:
                                    lightdist = Len - car_list[i][j].pos.x
                                    if lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= 0:
                                        car_list[i][j].STAT = INCREASE
                                        nexrstate = INCREASE
                    if next_state == -1:
                        if frontcarindex == -1:
                            if (is_red(counttime) == False):
                                car_list[i][j].STAT = INCREASE
                                nexrstate = INCREASE
                            else:
                                lightdist = Len - car_list[i][j].pos.x
                                if lightdist > CAR_LEN and lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= 0:
                                    car_list[i][j].STAT = INCREASE
                                    nexrstate = INCREASE

                if car_list[i][j].TYPE == HUMAN:

                    if decrease_time.get((i, j)) != None:
                        if counttime >= decrease_time.get((i, j)):
                            car_list[i][j].STAT = DECREASE
                            next_state = DECREASE
                            del decrease_time[(i, j)]
                    if increase_time.get((i, j)) != None:
                        if counttime >= increase_time.get((i, j)):
                            if frontcarindex != -1 and car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x > SAFEDIS:
                                car_list[i][j].STAT = INCREASE
                                next_state = INCREASE
                            del increase_time[(i, j)]

                    if next_state == -1:
                        if frontcarindex != -1:
                            cardist = car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x
                            if car_list[i][frontcarindex].STAT == DECREASE or car_list[i][frontcarindex].STAT == STOP:
                                decrease_time[(i, j)] = counttime + reflec()
                            if  cardist - car_list[i][j].v.x * 2 * dt < SAFEDIS:
                                car_list[i][j].STAT = DECREASE
                                next_state = DECREASE
                        if frontcarindex == -1:
                            if (Len - (car_list[i][j].pos.x + nextredt * car_list[i][j].v.x)) >= 0:
                                lightdist = Len - car_list[i][j].pos.x
                                if lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt < 0:
                                    car_list[i][j].STAT = DECREASE
                                    next_state = DECREASE

                    if next_state == -1:
                        if frontcarindex != -1:
                            cardist = car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x
                            if car_list[i][j].STAT == STOP and (car_list[i][frontcarindex].STAT == INCREASE or car_list[i][frontcarindex].STAT == CONSTANT):
                                increase_time[(i, j)] = counttime + reflec()
                                
                            if cardist - (car_list[i][j].v.x ** 2 - car_list[i][frontcarindex].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= SAFEDIS:
                                if (Len - (car_list[i][j].pos.x + nextredt * car_list[i][j].v.x)) < 0:
                                    car_list[i][j].STAT = INCREASE
                                    nexrstate = INCREASE
                                else:
                                    lightdist = Len - car_list[i][j].pos.x
                                    if lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= 0:
                                        car_list[i][j].STAT = INCREASE
                                        nexrstate = INCREASE
                        if frontcarindex == -1:
                            if (is_red(counttime) == False):
                                car_list[i][j].STAT = INCREASE
                                nexrstate = INCREASE
                            else:
                                lightdist = Len - car_list[i][j].pos.x
                                if lightdist > CAR_LEN and lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= 0:
                                    car_list[i][j].STAT = INCREASE
                                    nexrstate = INCREASE
                
                if i == transfer_lane and j == corresponding[1]:
                    stop_pos = transfer_pos[accident_lane][corresponding[0]].x - 2 * CAR_LEN
                    now_pos = car_list[i][j].pos.x
                    now_v = car_list[i][j].v.x
                    if stop_pos - now_pos - now_v ** 2 / (2 * Accel) - now_v * 2 * dt <= 0:
                        car_list[i][j].STAT = DECREASE
                        next_state = DECREASE

                
#endif accident happened

            if accident != 3:
                if car_list[i][j].TYPE == AUTO:
                    if next_state == -1:
                        if frontcarindex != -1:
                            cardist = car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x
                            if cardist - (car_list[i][j].v.x ** 2 - car_list[i][frontcarindex].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt < AUTODIS:
                                car_list[i][j].STAT = DECREASE
                                next_state = DECREASE
                    if next_state == -1:        
                        if (Len - (car_list[i][j].pos.x + nextredt * car_list[i][j].v.x)) >= 0:
                            lightdist = Len - car_list[i][j].pos.x
                            if lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt < 0:
                                car_list[i][j].STAT = DECREASE
                                next_state = DECREASE

                    if next_state == -1:
                        if frontcarindex != -1:
                            cardist = car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x
                            if cardist - (car_list[i][j].v.x ** 2 - car_list[i][frontcarindex].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= AUTODIS:
                                if (Len - (car_list[i][j].pos.x + nextredt * car_list[i][j].v.x)) < 0:
                                    car_list[i][j].STAT = INCREASE
                                    nexrstate = INCREASE
                                else:
                                    lightdist = Len - car_list[i][j].pos.x
                                    if lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= 0:
                                        car_list[i][j].STAT = INCREASE
                                        nexrstate = INCREASE
                    if next_state == -1:
                        if frontcarindex == -1:
                            if (is_red(counttime) == False):
                                car_list[i][j].STAT = INCREASE
                                nexrstate = INCREASE
                            else:
                                lightdist = Len - car_list[i][j].pos.x
                                if lightdist > CAR_LEN and lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= 0:
                                    car_list[i][j].STAT = INCREASE
                                    nexrstate = INCREASE

                if car_list[i][j].TYPE == HUMAN:

                    if decrease_time.get((i, j)) != None:
                        if counttime >= decrease_time.get((i, j)):
                            car_list[i][j].STAT = DECREASE
                            next_state = DECREASE
                            del decrease_time[(i, j)]
                    if increase_time.get((i, j)) != None:
                        if counttime >= increase_time.get((i, j)):
                            if frontcarindex != -1 and car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x > SAFEDIS:
                                car_list[i][j].STAT = INCREASE
                                next_state = INCREASE
                            del increase_time[(i, j)]

                    if next_state == -1:
                        if frontcarindex != -1:
                            cardist = car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x
                            if car_list[i][frontcarindex].STAT == DECREASE or car_list[i][frontcarindex].STAT == STOP:
                                decrease_time[(i, j)] = counttime + reflec()
                            if cardist - car_list[i][j].v.x * 2 * dt < SAFEDIS:
                                car_list[i][j].STAT = DECREASE
                                next_state = DECREASE
                        if frontcarindex == -1:
                            if (Len - (car_list[i][j].pos.x + nextredt * car_list[i][j].v.x)) >= 0:
                                lightdist = Len - car_list[i][j].pos.x
                                if lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt < 0:
                                    car_list[i][j].STAT = DECREASE
                                    next_state = DECREASE

                    if next_state == -1:
                        if frontcarindex != -1:
                            cardist = car_list[i][frontcarindex].pos.x - car_list[i][j].pos.x
                            if car_list[i][j].STAT == STOP and (car_list[i][frontcarindex].STAT == INCREASE or car_list[i][frontcarindex].STAT == CONSTANT):
                                increase_time[(i, j)] = counttime + reflec()
                            if cardist - (car_list[i][j].v.x ** 2 - car_list[i][frontcarindex].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= SAFEDIS:
                                if (Len - (car_list[i][j].pos.x + nextredt * car_list[i][j].v.x)) < 0:
                                    car_list[i][j].STAT = INCREASE
                                    nexrstate = INCREASE
                                else:
                                    lightdist = Len - car_list[i][j].pos.x
                                    if lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= 0:
                                        car_list[i][j].STAT = INCREASE
                                        nexrstate = INCREASE
                        if frontcarindex == -1:
                            if (is_red(counttime) == False):
                                car_list[i][j].STAT = INCREASE
                                nexrstate = INCREASE
                            else:
                                lightdist = Len - car_list[i][j].pos.x
                                if lightdist > CAR_LEN and lightdist - (car_list[i][j].v.x ** 2) / (2 * Accel) - car_list[i][j].v.x * 2 * dt >= 0:
                                    car_list[i][j].STAT = INCREASE
                                    nexrstate = INCREASE


            if car_list[i][j].STAT == DECREASE:
                car_list[i][j].v.x = car_list[i][j].v.x - Accel * dt
                if car_list[i][j].v.x <= 0:
                    car_list[i][j].v.x = 0
                    car_list[i][j].STAT = STOP
                    car_list[i][j].color = color.red
                else:
                    car_list[i][j].color = color.yellow
            if car_list[i][j].STAT == INCREASE:
                car_list[i][j].v.x = car_list[i][j].v.x + Accel * dt
                if car_list[i][j].v.x >= Initspd:
                    car_list[i][j].v.x = Initspd
                    car_list[i][j].STAT = CONSTANT    
                    car_list[i][j].color = color.blue
                else:
                    car_list[i][j].color = color.green
            
            if car_list[i][j].STAT == TRANSFER:
                car_list[i][j].color = color.cyan

            if car_list[i][j].pos.x >= Len:
                car_list[i][j].visible = False

                
#generate new car
        if nexttype[i] == AUTO and car_list[i][len(car_list[i]) - 1].pos.x > -Len + AUTODIS + random.random() * AUTODIS:
            frontv = car_list[i][len(car_list[i]) - 1].v.x
            frontstat = car_list[i][len(car_list[i]) - 1].STAT
            frontcolor = car_list[i][len(car_list[i]) - 1].color
            car = ellipsoid(TYPE = nexttype[i], STAT = frontstat, size = vec(CAR_LEN, CAR_WIDTH, 1), pos = vec(-Len, 10 - LANE_WIDTH * i, 0), v = vec(frontv, 0, 0), color = frontcolor)
            car_list[i].append(car)
            transfer_pos[i].append(vec(math.inf, math.inf, math.inf))
            Carnum = Carnum + 1
            newcarindex[i] = newcarindex[i] + 1
            if random.random() * 100 > Percent:
                nexttype[i] = HUMAN
            else:
                nexttype[i] = AUTO

        if nexttype[i] == HUMAN and car_list[i][len(car_list[i]) - 1].pos.x > -Len + SAFEDIS + random.random() * SAFEDIS:
            if accident == 1 and i == 0:
                accident = 2
                frontv = car_list[i][len(car_list[i]) - 1].v.x
                frontstat = car_list[i][len(car_list[i]) - 1].STAT
                frontcolor = car_list[i][len(car_list[i]) - 1].color
                car = box(TYPE = ACCIDENT, STAT = frontstat, length = CAR_LEN, width = 1, height = CAR_WIDTH, pos = vec(-Len, 10 - LANE_WIDTH * i, 0), v = vec(Initspd + 2, 0, 0), color = color.orange)
                car_list[i].append(car)
                transfer_pos[i].append(vec(math.inf, math.inf, math.inf))
                Carnum = Carnum + 1
                newcarindex[i] = newcarindex[i] + 1
                if random.random() * 100 > Percent:
                    nexttype[i] = HUMAN 
                else:
                    nexttype[i] = AUTO
            else:
                frontv = car_list[i][len(car_list[i]) - 1].v.x
                frontstat = car_list[i][len(car_list[i]) - 1].STAT
                frontcolor = car_list[i][len(car_list[i]) - 1].color
                car = box(TYPE = nexttype[i], STAT = frontstat, length = CAR_LEN, width = 1, height = CAR_WIDTH, pos = vec(-Len, 10 - LANE_WIDTH * i, 0), v = vec(frontv, 0, 0), color = frontcolor)
                car_list[i].append(car)
                transfer_pos[i].append(vec(math.inf, math.inf, math.inf))
                Carnum = Carnum + 1
                newcarindex[i] = newcarindex[i] + 1
                if random.random() * 100 > Percent:
                    nexttype[i] = HUMAN
                else:
                    nexttype[i] = AUTO
    
    
    for i in range(0, LANE_NUM):
        for j in range(firstcar[i], len(car_list[i])):
            car_list[i][j].pos = car_list[i][j].pos + car_list[i][j].v * dt