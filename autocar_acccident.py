from vpython import *
import random
import math

scene2 = canvas(title = 'Simulation', width = 600, height = 200, center = vector(0,0,0), background = color.black)
random.seed(8)

#define constant
STOP = 0
CONSTANT = 1
INCREASE = 2
DECREASE = 3
ACCIDENT = 4
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

#define parameter
Time = 100
Len = 60
Initspd = 10
Accel = 10
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
            car = ellipsoid(TYPE = TYPE, STAT = CONSTANT, size = vec(CAR_LEN, CAR_WIDTH, 1 ), pos = vec(frontpos - AUTODIS - random.random() * CAR_LEN, 10 - LANE_WIDTH * i, 0), v = vec(Initspd, 0, 0))
        else:
            car = box(TYPE = TYPE, STAT = CONSTANT, length = CAR_LEN, width = 1, height = CAR_WIDTH, pos = vec(frontpos - SAFEDIS - random.random() * CAR_LEN, 10 - LANE_WIDTH * i, 0), v = vec(Initspd, 0, 0))

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

    for i in range(0, LANE_NUM):
        if accident == 0 and counttime > 3:
            accident = 1
        for j in range(firstcar[i], len(car_list[i])):
        
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
                accident_backcar = (i, j - 1)
                
#ifdef accident happened
            if accident == 3:
                if car_list[i][j].TYPE == ACCIDENT: 
                    car_list[i][j].rotate(axis = vec(0, 1, -1), angle = 0.01)
                
                if i == accident_lane and car_list[i][j].pos.x < accident_pos.x:
               #     car_list[i][j].rotate(axis = vec(0, 1, -1), angle = 0.01)
                    if car_list[i][j].pos.x > accident_pos.x - 20 and car_list[i][j].STAT == STOP:
                        transfer_pos[i][j] = vec(car_list[i][j].pos.x + LANE_WIDTH / math.tan(TURN_ANGLE), 10 - transfer_lane * LANE_WIDTH, 0)
                        transfer_index = box(pos = transfer_pos[i][j], length = 3, width = 3, height = 3, color = color.white)
                        
                if i == transfer_lane and car_list[i][j].pos.x < accident_pos.x:
                    for k in range(len(transfer_pos[accident_lane])):
                        if transfer_pos[accident_lane][k].x != math.inf:
                            if car_list[i][j].pos.x + (car_list[i][j].v.x ** 2) / (2 * Accel) <= (transfer_pos[accident_lane][k].x - 20):
                                if car_list[i][j].STAT != STOP:
                                    car_list[i][j].STAT = DECREASE
                                    next_state = DECREASE
                                else:
                                    next_state = STOP
                

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


            if car_list[i][j].pos.x >= Len:
                car_list[i][j].visible = False


        if nexttype[i] == AUTO and car_list[i][newcarindex[i] - 1].pos.x > -Len + AUTODIS + random.random() * AUTODIS:
            frontv = car_list[i][newcarindex[i] - 1].v.x
            frontstat = car_list[i][newcarindex[i] - 1].STAT
            frontcolor = car_list[i][newcarindex[i] - 1].color
            car = ellipsoid(TYPE = nexttype[i], STAT = frontstat, size = vec(CAR_LEN, CAR_WIDTH, 1), pos = vec(-Len, 10 - LANE_WIDTH * i, 0), v = vec(frontv, 0, 0), color = frontcolor)
            car_list[i].append(car)
            transfer_pos[i].append(vec(math.inf, math.inf, math.inf))
            Carnum = Carnum + 1
            newcarindex[i] = newcarindex[i] + 1
            if random.random() * 100 > Percent:
                nexttype[i] = HUMAN
            else:
                nexttype[i] = AUTO

        if nexttype[i] == HUMAN and car_list[i][newcarindex[i] - 1].pos.x > -Len + SAFEDIS + random.random() * SAFEDIS:
            if accident == 1 and i == 0:
                accident = 2
                frontv = car_list[i][newcarindex[i] - 1].v.x
                forntstat = car_list[i][newcarindex[i] - 1].STAT
                frontcolor = car_list[i][newcarindex[i] - 1].color
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
                frontv = car_list[i][newcarindex[i] - 1].v.x
                frontstat = car_list[i][newcarindex[i] - 1].STAT
                frontcolor = car_list[i][newcarindex[i] - 1].color
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

    
    
