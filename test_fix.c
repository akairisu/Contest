#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<windows.h>
#include<time.h>
#define STOP 0
#define CONSTANT 1
#define INCREASE 2
#define DECREASE 3
#define AUTO 0
#define HUMAN 1
#define CAR_LEN (double)4
#define INITDEN 1
#define SPD_per_Second(speed) (speed * 1000 / 3600)
#define MIN(a, b) (a < b ? a : b)
#define MAX(a, b) (a > b ? a : b)
#define GRAPHIC

int TIME;
double INITSPD;
int LEN;
double Accel;
int PERCENT;
int RedLight;
int GreenLight;
int totaltime;

typedef struct Car{
	double pos;
	double spd;
	int stat;
	int alt;
	int accel_time;
	double accel_spd;
	struct Car *prev;
	struct Car *next;
	double next_dis;
	int delay;
}car;

typedef struct Road{
	car *car_list;
	double end;
}road;

car *Init_Car(double position, double speed, int status, int random, int percent){//新增一台車
	car *new_car = (car*)malloc(sizeof(car));
	new_car->pos = position;
	new_car->spd = SPD_per_Second(speed);
	new_car->stat = status;
	new_car->alt = (random <= percent ? AUTO : HUMAN);
	new_car->next = NULL;
	new_car->prev = NULL;
	new_car->accel_time = 0;
	new_car->next_dis = 0.5 + 0.1 * (rand() % 5);
	new_car->delay = rand() % 3 + 1;
	return new_car;
}

void Init(){//設定變數值
	printf("Experiment time(second): ");
	scanf("%d", &TIME);
	printf("Road Length(meter, > 100): ");
	scanf("%d", &LEN);
	printf("Speed(km/hr, > 0): ");
	scanf("%lf", &INITSPD);
	printf("Accelrate(km/hr^2, > 0): ");
	scanf("%lf", &Accel);
	Accel = SPD_per_Second(Accel);
	printf("Autonomous Rate(%%):");
	scanf("%d", &PERCENT);
	printf("Redlight time(s, > 10): ");
	scanf("%d", &RedLight);
	printf("Greenlight time(s, > 10): ");
	scanf("%d", &GreenLight);
	totaltime = RedLight * 100 + GreenLight * 100;
	return;
}

void Init_Road(road *road_list[]){//設定道路起始車輛
	for(int i = 0; i < 4; i++){
		road_list[i] = (road*)malloc(sizeof(road));
		road_list[i]->car_list = Init_Car(-20, 20, DECREASE, 100, 100);
		road_list[i]->car_list->accel_time = 5;
		int initial = rand() % 10;
		car *head = road_list[i]->car_list;
		double cur_pos = 0;
		for(int j = 0; j <= initial; j++){
			road_list[i]->car_list->next = Init_Car(cur_pos, 0, STOP, (rand() % 100) + 1, PERCENT);
			if(road_list[i]->car_list->next->alt == AUTO && cur_pos != 0){
				road_list[i]->car_list->next->pos = road_list[i]->car_list->pos + CAR_LEN + 0.2;
				cur_pos = road_list[i]->car_list->next->pos;
			}
			road_list[i]->car_list->next->prev = road_list[i]->car_list;
			road_list[i]->end = cur_pos + CAR_LEN + INITSPD / 2;
			cur_pos = cur_pos + CAR_LEN + road_list[i]->car_list->next->next_dis;
			road_list[i]->car_list = road_list[i]->car_list->next;
		}
		head->prev = road_list[i]->car_list;
		road_list[i]->car_list->next = head;
		road_list[i]->car_list = head;
	}
	return;
}

void Print_Road(road *road_list[], double second){//印路
	HANDLE  hConsole;
	hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
	if(second >= 0){
		for(int i = 0; i < 90; i += 10){
			printf("%2d", i);
			for(int j = 0; j < 18; j++){
				printf("_");
			}
		}
		printf("\n");
		for(int i = 0; i < 4; i++){
			car *cur = road_list[i]->car_list->next;
			for(double j = 0; j < 90; j += 0.5){
				printf("_");
			}
			printf("\n");
			for(double j = 0; j < 90; j += 0.5){
				if(j >= cur->pos){
					if(cur->stat == STOP){
						SetConsoleTextAttribute(hConsole, 14);
					}
					else if(cur->stat == CONSTANT){
						SetConsoleTextAttribute(hConsole, 9);
					}
					else if(cur->stat == INCREASE){
						SetConsoleTextAttribute(hConsole, 10);
					}
					else if(cur->stat == DECREASE){
						SetConsoleTextAttribute(hConsole, 12);
					}
					if(j - 0.5 <= cur->pos){
						printf("[");
						j += 0.5;
					}
					if(cur->alt == AUTO){
						SetConsoleTextAttribute(hConsole, 11);
					}
					else{
						SetConsoleTextAttribute(hConsole, 6);
					}
					int count = 0;
					while(j < 90 && count < 6 && j <= (cur->pos + CAR_LEN - 0.5)){
						printf("|");
						j += 0.5;
						count++;
					}
					if(cur->stat == STOP){
						SetConsoleTextAttribute(hConsole, 14);
					}
					else if(cur->stat == CONSTANT){
						SetConsoleTextAttribute(hConsole, 9);
					}
					else if(cur->stat == INCREASE){
						SetConsoleTextAttribute(hConsole, 10);
					}
					else if(cur->stat == DECREASE){
						SetConsoleTextAttribute(hConsole, 12);
					}
					if(j < 90 && j < (cur->pos + CAR_LEN)){
						printf("]");
					}
					SetConsoleTextAttribute(hConsole, 7);
					cur = cur->next;
					if(cur == road_list[i]->car_list){
						j += 0.5;
						while(j < 90){
							printf("_");
							j += 0.5;
						}
					}
				}
				else{
					if(j < 90){
						printf("_");
					}
				}
			}
			printf("\n");
			for(double j = 0; j < 90; j += 0.5){
				printf("_");
			}
			printf("\n");
		}
	}
	return;
}

double Increase_dis(double speed, double target_speed){//加速時移動距離
	if((speed + ((double)Accel) / 4) > target_speed){
		return (speed + target_speed) / 8;
	}
	return (2 * speed + ((double)Accel) / 4) / 8;
}

double Decrease_dis(double speed){//減速時移動距離
	if((speed - ((double)Accel) / 4) < 0){
		return speed / 8;
	}
	return (2 * speed - ((double)Accel) / 4) / 8;
}

#ifdef DATA
	void add_dis(double time, double distance){//計算數據用
		if(((int)(time * 100) % totaltime) >= (RedLight * 100)){
			avg[number] += distance;
		}
	}
#endif

void Increasing(car *cur, double time){//加速
	cur->pos -= Increase_dis(cur->spd, cur->accel_spd);
	if(cur->accel_time > 0){
		cur->accel_time -= 1;
	}
	cur->spd = MIN(cur->spd + ((double)Accel / 4), cur->accel_spd);
	if(cur->spd == cur->accel_spd){
		cur->stat = CONSTANT;
	}
}

void Decreasing(car *cur, double time){//減速
	cur->pos -= Decrease_dis(cur->spd);
	if(cur->accel_time > 0){
		cur->accel_time -= 1;
	}
	cur->spd = MAX(cur->spd - ((double)Accel / 4), 0);
	if(cur->spd == 0){
		cur->stat = STOP;
	}
	return;
}

void Move(car *cur, car *prev, double time, double legal_speed){
	if(cur->pos < -5){
		prev->next = cur->next;
		cur->next->prev = prev;
		free(cur);
		return;
	}
	switch(cur->alt){
		case AUTO:
			//檢查快紅燈時是否要減速
			if(((int)(time * 100) % totaltime) >= (totaltime - 300) && cur->stat == CONSTANT){
				if(cur->pos >= cur->spd * (90 - ((double)((int)(time * 100) % totaltime) / 100)) && prev->stat == CONSTANT && cur->pos <= (cur->spd * cur->spd) / (2 * Accel) + cur->spd * 0.25){					 
					cur->stat = DECREASE;
					cur->accel_time = rand() % 3 + 2;
					cur->delay == 5;
				}
			}
			//如果要減速的話
			if(cur->delay == 5){
				Decreasing(cur, time);
				if(cur->stat == STOP){
					if(cur->pos != 0){
						cur->pos = 0;
						cur->delay = rand() % 3 + 1;							
					}
				}
				return;
			}
			//跟著前車
			if(prev->pos != -20 && cur->delay != 0){
				cur->stat = prev->stat;
				cur->pos = prev->pos + CAR_LEN + 0.2;
				cur->spd = prev->spd;
				cur->accel_spd = prev->accel_spd;
				cur->accel_time = prev->accel_time;
			}
			//如果跟前車差很遠的話
			if(cur->delay == 0){
				if(((int)(time * 100) % totaltime) < (RedLight * 100) && cur->pos != prev->pos + CAR_LEN){
					//檢查是否要開始減速
					if(cur->stat == CONSTANT && cur->pos <= prev->pos + CAR_LEN + (cur->spd * cur->spd) / (2 * Accel) + cur->spd * 0.25){
						cur->stat = DECREASE;
						cur->accel_time = rand() % 3 + 2;
					}
					//減速
					if(cur->stat == DECREASE){
						Decreasing(cur, time);
						if(cur->stat == STOP){
							if(cur->pos != prev->pos + CAR_LEN){
								cur->pos = prev->pos + CAR_LEN;
								cur->delay = rand() % 3 + 1;							
							}
						}
					}
					//等速
					else{
						cur->pos -= cur->spd * 0.25;
					}
				}
				else{
					cur->delay = rand() % 3 + 1;
				}
			}
			//如果沒有前車
			if(prev->pos == -20){
				int flag = (((int)time * 100) % totaltime) < (RedLight * 100) ? 0 : 1;
				switch(flag){
					case 0://紅燈
						if(cur->pos != 0){
							if(cur->stat == CONSTANT){
								if(cur->pos <= (cur->spd * cur->spd) / (2 * Accel) + cur->spd * 0.25){
									cur->stat = DECREASE;
									cur->accel_time = rand() % 3 + 2;
								}
								cur->pos -= cur->spd * 0.25;
								return;
							}
							if(cur->stat == INCREASE){
								Increasing(cur, time);
								return;
							}
							if(cur->stat == DECREASE){
								Decreasing(cur, time);
								return;
							}
						}
						if(cur->stat == STOP && cur->pos != 0){
							cur->pos = 0;
						}
						break;
					case 1://綠燈
						if(cur->stat == STOP){
							cur->stat = INCREASE;
							cur->accel_spd = SPD_per_Second(legal_speed);
							cur->accel_time = rand() % 3 + 4;
							Increasing(cur, time);
							return;
						}
						if(cur->stat == CONSTANT){
							cur->pos -= cur->spd * 0.25; 
							return;
						}
						if(cur->stat == DECREASE){
							Decreasing(cur, time);
							return;
						}
						if(cur->stat == INCREASE){
							Increasing(cur, time);
							return;
						}
						break;
				}
			}
			break;
		case HUMAN:
			if(cur->pos > (prev->pos + CAR_LEN + prev->next_dis)){
				switch(cur->stat){
					case STOP:
						//第一台車在綠燈時出發
						if(((int)(time * 100) % totaltime) == (RedLight * 100) && prev->pos == -20){
							cur->stat = INCREASE;
							cur->accel_spd = SPD_per_Second(legal_speed);
							cur->accel_time = rand() % 3 + 4;
						}
						//如果前車沒動但兩車距離過大
						if(prev->stat == STOP){
							cur->stat = INCREASE;
							cur->accel_spd = sqrt((double)Accel * (cur->pos - prev->pos - CAR_LEN - prev->next_dis));
							cur->accel_time = MIN(rand() % 3 + 2, (cur->accel_spd / Accel) * 4 + rand() % 2);
							if(cur->accel_spd < 0.000001){
								cur->stat = STOP;
								cur->accel_time = 0;
							}
						}
						//前車在加速
						if(prev->accel_time == 0){
							if(prev->stat == INCREASE){
								cur->stat = INCREASE;
								cur->accel_spd = prev->accel_spd;
								cur->accel_time = sqrt((double)Accel * (cur->pos - prev->pos - CAR_LEN - prev->next_dis)) + rand() % 2;
							}
						}
						break;
					case CONSTANT:
						//檢查快紅燈時是否要減速
						if(((int)(time * 100) % totaltime) >= (totaltime - 300)){
							if(cur->pos >= cur->spd * ((90 - (double)((int)(time * 100) % totaltime)) / 100) && prev->stat == CONSTANT && cur->pos <= (cur->spd * cur->spd) / (2 * Accel) + cur->spd * 0.25){					 
								cur->stat = DECREASE;
								cur->accel_time = rand() % 3 + 2;
								cur->pos -= cur->spd * 0.25;
								return;
							}
						}
						//檢查第一台車要不要開始減速
						if(prev->pos == -20 && ((int)(time * 100) % totaltime) < (RedLight * 100) && cur->pos <= (cur->spd * cur->spd) / (2 * Accel) + cur->spd * 0.25){
							cur->stat = DECREASE;
							cur->accel_time = rand() % 3 + 2;
						}
						//前車開始減速且兩車距離很近
						if(prev->stat == DECREASE && prev->accel_time == 0 && (cur->pos - prev->pos) < CAR_LEN + prev->next_dis + (cur->spd * cur->spd) / (2 * Accel) + cur->spd * 0.25){
							cur->stat = DECREASE;
							cur->accel_time = rand() % 3 + 2;
						}
						//前車沒動檢查是否要開始減速
						else if(prev->stat == STOP){
							if((cur->pos - prev->pos) < CAR_LEN + prev->next_dis + ((cur->spd * cur->spd) / (2 * Accel)) + cur->spd * 0.25){
								cur->stat = DECREASE;
								cur->accel_time = rand() % 3 + 2;
							}
						}
						//兩車等速移動(偷懶)
						else if(prev->stat == CONSTANT && (cur->pos - cur->spd * 0.25 > prev->pos + CAR_LEN + legal_speed / 2) && (cur->pos - cur->spd * 0.5 < prev->pos + CAR_LEN + legal_speed / 2)){
							cur->pos = prev->pos + CAR_LEN + legal_speed / 2 + cur->spd * 0.25;
						}
						cur->pos -= cur->spd * 0.25;
						break;
					case INCREASE:
						Increasing(cur, time);
						break;
					case DECREASE:
						Decreasing(cur, time);
						break;
				}
			}
			if(cur->pos <= (prev->pos + CAR_LEN + prev->next_dis) || (cur->pos - prev->pos - CAR_LEN - prev->next_dis) < 0.000001){
					cur->pos = prev->pos + CAR_LEN + prev->next_dis;
					cur->stat = STOP;
					cur->spd = 0;
			}
			if(prev->pos == -20 && cur->stat == STOP){
				cur->pos = 0;
			}
			break;
	}
	return;
}

void Change_End(road *cur_road, car *head, car *end, double time, double legal_speed){//更新尾巴距離
	end->next->prev = end;
	end->next->next = head;
	head->prev = end->next;
	Move(head->prev, end, time, legal_speed);
	cur_road->end = head->prev->pos + CAR_LEN + head->prev->next_dis;
}

int main(void){
	Init();
	road *road_list[4];
	double legal_speed = INITSPD;
	Init_Road(road_list);
	double second = 0;
	while(second < TIME){
#ifdef GRAPHIC
#ifndef DEBUG
		system("cls");
#endif
		printf("%.2f :\n", second);
#endif
		for(int i = 0; i < 4; i++){
			car *cur = road_list[i]->car_list->next;
			while(cur != road_list[i]->car_list){
				Move(cur, cur->prev, second, legal_speed);
				cur = cur->next;
			}
			road_list[i]->end = road_list[i]->car_list->prev->pos + CAR_LEN + legal_speed / 2;
		}
		for(int i = 0; i < 4; i++){
			if(road_list[i]->end < LEN){
				road_list[i]->car_list->prev->next = Init_Car(LEN + 0.5 * (rand() % 2), legal_speed, CONSTANT, (rand() % 100) + 1, PERCENT);
				if(road_list[i]->car_list->prev->next->alt == AUTO && second == 0){
					road_list[i]->car_list->prev->next->delay = 0;
				}
				Change_End(road_list[i], road_list[i]->car_list, road_list[i]->car_list->prev, second, legal_speed);
			}
			if(road_list[i]->car_list->prev->stat == STOP && road_list[i]->end <= 3 * LEN){
				road_list[i]->car_list->prev->next = Init_Car(road_list[i]->car_list->prev->pos + CAR_LEN + road_list[i]->car_list->prev->next_dis, 0, STOP, (rand() % 100) + 1, PERCENT);
				Change_End(road_list[i], road_list[i]->car_list, road_list[i]->car_list->prev, second, legal_speed);
			}
		}
#ifdef GRAPHIC
		Print_Road(road_list, second);	
#endif
		second += 0.25;
	}
	return 0;
}