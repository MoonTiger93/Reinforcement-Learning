import numpy as np
import os;
import time
import math
import copy
import matplotlib.pyplot as plt
#𓃰

# TODO check that state transitions probs add to one


T = 15
minotaur_can_stay = True;

STAY = np.array([0, 0])
UP = np.array([0, 1])
RIGHT = np.array([1, 0])
DOWN = np.array([0, -1])
LEFT = np.array([-1, 0])

Stay = 0
Up = -6
Right = 1
Down = 6
Left = -1

N_STATES = 901
ACTIONS = [Stay, Up, Right, Down, Left]
N_ACTIONS = len(ACTIONS)


def rc2idx(rc):
	return rc[0] * 6 + rc[1]


def idx2rc(idx):
	return np.array([idx // 6, idx % 6])


def rc_exists(rc):
	return -1 < rc[0] < 5 and -1 < rc[1] < 6

walls = []

# define walls
walls.append([rc2idx([0, 1]), rc2idx([0, 2])])
walls.append([rc2idx([1, 1]), rc2idx([1, 2])])
walls.append([rc2idx([2, 1]), rc2idx([2, 2])])

walls.append([rc2idx([1, 3]), rc2idx([1, 4])])
walls.append([rc2idx([2, 3]), rc2idx([2, 4])])

walls.append([rc2idx([1, 4]), rc2idx([2, 4])])
walls.append([rc2idx([1, 5]), rc2idx([2, 5])])

walls.append([rc2idx([3, 1]), rc2idx([4, 1])])
walls.append([rc2idx([3, 2]), rc2idx([4, 2])])
walls.append([rc2idx([3, 3]), rc2idx([4, 3])])
walls.append([rc2idx([3, 4]), rc2idx([4, 4])])

walls.append([rc2idx([4, 3]), rc2idx([4, 4])])

access_list = [[]] * 5 * 6

for idx in range(0, 6 * 5):
	rc = idx2rc(idx)
	moves = np.array([STAY, UP, RIGHT, DOWN, LEFT])
	new_rcs = filter(rc_exists, rc + moves)
	access_list[idx] = [rc2idx(p) for p in new_rcs]


player_list = copy.deepcopy(access_list)
minotaur_list = copy.deepcopy(access_list)


# player can't traverse walls
for wall in walls:
	player_list[wall[0]].remove(wall[1])
	player_list[wall[1]].remove(wall[0])


# minotaur can't stay in place
if not minotaur_can_stay:
	for m_idx, mi in enumerate(minotaur_list):
		mi.remove(m_idx)


PLAYER_ACCESS = player_list
MINOTAUR_ACCESS = minotaur_list


def print_acess_list():
# check acess lists
	for m_idx, m in enumerate(MINOTAUR_ACCESS):
		print("at " + str(m_idx) + " minotaur can access :" + str(m))

	for p_idx, p in enumerate(PLAYER_ACCESS):
		print("at " + str(p_idx) + " player 1 can access :" + str(p))
	return 


########################## INTERESTING PART #################
##
def stpf(s, a):
	tp = np.zeros(N_STATES)
	# if end -> end
	if s == 900:
		tp[900] = 1
	else:
		p = s % 30
		m = s // 30
		# if win/die -> end
		if p == m or p == 28:
			tp[900] = 1
		else:
			p_try = p + a
			p_new = p_try if p_try in PLAYER_ACCESS[p] else p
			n_m_new = len(MINOTAUR_ACCESS[m])
			for m_new in MINOTAUR_ACCESS[m]:
				tp[p_new + 30 * m_new] = 1 / n_m_new
	return tp


def reward(s, a):
		# end state gives 0 reward
	if s == 900:
		return 0
	# end maze without dying gives 1
	elif s % 30 == 28 and s // 30 != 28:
		return 1
	else:
		return 0


def print_board(p, m):
	
	board_strings = [["𓐍", "   ", "_", " | ", "_", "   ", "_", "   ", "_", "   ", "_"],
					 ["", "   ", " ", "   ", " ", "   ", " ", "   ", " ", "   ", " "],
					 ["_", "   ", "_", " │ ", "_", "   ", "_", " │ ", "_", "   ", "_"],
					 [" ", "   ", " ", "   ", " ", "   ", " ", "   ", " ", "   ", " "],
					 ["_", "   ", "_", " │ ", "_", "   ", "_", " │ ", "_", "   ", "_"],
					 [" ", "   ", " ", "   ", " ", "   ", " ", "   ", " ", "   ", " "],
					 ["_", "   ", "_", "   ", "_", "   ", "_", "   ", "_", "   ", "_"],
					 [" ", "   ", " ", "   ", " ", "   ", " ", "   ", " ", "   ", " "],
					 ["_", "   ", "_", " │ ", "_", "   ", "_", " │ ", "𓊓", "   ", "_"]]



	pr, pc = idx2rc(p)
	mr, mc = idx2rc(m)
	out = board_strings.copy()
	out[pr * 2][pc * 2] = "𓁆"
	out[mr * 2][mc * 2] = "𓃾"
	if m == p:
		out[mr * 2][mc * 2] = "✞"
	elif p == 28:
		out[pr * 2][pc * 2] = "𓀠"

	print("___________________________________________")
	for l in out:
		print("".join(l))
	print("___________________________________________")
	return

def clear():
    os.system( 'clear' )

def try_policy(policy, T,_print=False):
	p = 0
	m = 28
	for t in range(0, T):
		if np.random.uniform(0,1)<1/30:
			return False,t
		else:
			if _print:
				print("at "+str(t))
				print_board(p, m)
			# print(reward(p+m*30,"nothing"));
			if p == m:
				return False,t
			elif p == 28:
				return True,t
			#print("player is at :" + str(p))
			#print("minotaur is at :" + str(m))
			state = p + m * 30
			a_idx = policy[state]
			p = p + ACTIONS[a_idx] if p + ACTIONS[a_idx] in PLAYER_ACCESS[p] else p
			m = MINOTAUR_ACCESS[m][math.floor(
				np.random.uniform(0, len(MINOTAUR_ACCESS[m])))]
	return False,t

def clear():
    os.system( 'clear' )

def play(policy,T):
	p = 0
	m = 28
	for t in range(0, T):
		clear()
		print_board(p, m)
		# print(reward(p+m*30,"nothing"));
		if p == m:
			return False
		elif p == 28:
			return True
		#print("player is at :" + str(p))
		#print("minotaur is at :" + str(m))
		state = p + m * 30
		a_idx = policy[state,t]
		p = p + ACTIONS[a_idx] if p + ACTIONS[a_idx] in PLAYER_ACCESS[p] else p
		m_action_index=get_minotaur_action();
		m_try=m+ACTIONS[m_action_index];
		m=m_try if m_try in MINOTAUR_ACCESS[m] else m;
	return False

def get_minotaur_action():
	valid_input=["","w","d","s","a"];
	if not minotaur_can_stay:
		valid_input.remove("");
	key="dummy";
	while key not in valid_input:
		key = input("Type next move!");

	action_index=valid_input.index(key);
	if not minotaur_can_stay:
		action_index+=1;
	return action_index;



def display_policy(policy, m):

	policy_wrt_m = policy[m * 30:m * 30 + 30]
	action_icons = ["⧖", "⥣", "⥤", "⥥", "⥢"]
	minotaur_icon = "𓃾"
	policy_str = [action_icons[a] for a in policy_wrt_m]
	policy_str[m] = minotaur_icon
	for r in range(0, 5):
		print('  '.join(policy_str[r * 6:r * 6 + 6]))
	return


# precompute transition probability matrix.
stps = np.zeros((N_STATES, N_STATES, N_ACTIONS))
for a_idx, action in enumerate(ACTIONS):
	for state in range(0, N_STATES):
		stps[state, :, a_idx] = stpf(state, action)

rewards = np.zeros((N_STATES, N_ACTIONS))

# precompute rewards
for state in range(0, N_STATES):
	for a_idx, action in enumerate(ACTIONS):
		rewards[state, a_idx] = reward(state, action)


DISCOUNT_FACTOR=(1-1/30)

def howards_policy_iteration(stps,rewards):
	new_policy=np.random.randint(0,N_ACTIONS,size=N_STATES);
	policy=np.zeros(N_STATES,dtype=np.int8);
	V=np.zeros(N_STATES);
	u=np.zeros((N_STATES,N_ACTIONS))
	while not np.array_equal(new_policy, policy):
		print("running howards_policy_iteration..",end="\r")
		policy=new_policy;
		for s_idx in range(N_STATES):
			V[s_idx]=rewards[s_idx,policy[s_idx]]+DISCOUNT_FACTOR*(stps[s_idx,:,policy[s_idx]]@V);
		for s_idx in range(0, N_STATES):
				for a_idx in range(0, N_ACTIONS):
					u[s_idx, a_idx] = DISCOUNT_FACTOR*np.sum(stps[s_idx, :, a_idx]@V) + rewards[s_idx, a_idx]
		new_policy=np.argmax(u,1);
	return policy


policy=howards_policy_iteration(stps,rewards)

try_policy(policy, T, True)
#play(policy,T)


for m in range(1,30,5):
	print("\n")
	print("t = {},m_pos = {}".format(0,m))
	display_policy(policy,m);



N=10000
wins=0;
wins_per_time=np.zeros(T);
for i in range(N):
	isWin,time=try_policy(policy,T)
	if isWin:
		wins+=1;
		wins_per_time[time]+=1;




print("won "+str(wins)+" out of "+str(N)+" games! ("+str(100*wins/N)+"%)")

plt.plot(wins_per_time);
plt.show();

