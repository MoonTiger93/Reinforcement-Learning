import sys
import gym
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pylab as pylab
import random
import numpy as np
from collections import deque
from keras.layers import Dense
from keras.optimizers import Adam
from keras.models import Sequential
from functools import reduce

EPISODES = 1000 #Maximum number of episodes

#DQN Agent for the Cartpole
#Q function approximation with NN, experience replay, and target network
class DQNAgent:
    #Constructor for the agent (invoked when DQN is first called in main)
    def __init__(self, state_size, action_size,df,lr,ms,uf,hn,hl,search_space_string):
        self.search_space=search_space_string;
        self.check_solve = False	#If True, stop if you satisfy solution confition
        self.render = False        #If you want to see Cartpole learning, then change to True

        #Get size of state and action
        self.state_size = state_size
        self.action_size = action_size

################################################################################
################################################################################
        #Set hyper parameters for the DQN. Do not adjust those labeled as Fixed.
        self.discount_factor = df
        self.learning_rate = lr
        self.epsilon = 0.02 #Fixed
        self.batch_size = 32 #Fixed
        self.memory_size = ms
        self.train_start = 1000 #Fixed
        self.target_update_frequency = uf
        self.hidden_nodes=hn;
        self.hidden_layers=hl;
################################################################################
################################################################################

        #Number of test states for Q value plots
        self.test_state_no = 10000

        #Create memory buffer using deque
        self.memory = deque(maxlen=self.memory_size)

        #Create main network and target network (using build_model defined below)
        self.model = self.build_model()
        self.target_model = self.build_model()

        #Initialize target network
        self.update_target_model()

    #Approximate Q function using Neural Network
    #State is the input and the Q Values are the output.
###############################################################################
###############################################################################
        #Edit the Neural Network model here
        #Tip: Consult https://keras.io/getting-started/sequential-model-guide/
    def build_model(self):
        model = Sequential()
        model.add(Dense(self.hidden_nodes, input_dim=self.state_size, activation='relu',
                        kernel_initializer='he_uniform'))
        for i in range(self.hidden_layers-1):
            model.add(Dense(self.hidden_nodes, activation='relu',
                        kernel_initializer='he_uniform'))



        model.add(Dense(self.action_size, activation='linear',
                        kernel_initializer='he_uniform'))
        model.summary()
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model
###############################################################################
###############################################################################

    #After some time interval update the target model to be same with model
    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    #Get action from model using epsilon-greedy policy
    def get_action(self, state):
###############################################################################
###############################################################################
        #Insert your e-greedy policy code here
        #Tip 1: Use the random package to generate a random action.
        #Tip 2: Use keras.model.predict() to compute Q-values from the state.
        if np.random.uniform(0,1)<self.epsilon:
            action = random.randrange(self.action_size)
        else:
           action= np.argmax(self.model.predict(state));
        return action
###############################################################################
###############################################################################
    #Save sample <s,a,r,s'> to the replay memory
    def append_sample(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) #Add sample to the end of the list

    #Sample <s,a,r,s'> from replay memory
    def train_model(self):
        if len(self.memory) < self.train_start: #Do not train if not enough memory
            return
        batch_size = min(self.batch_size, len(self.memory)) #Train on at most as many samples as you have in memory
        mini_batch = random.sample(self.memory, batch_size) #Uniformly sample the memory buffer
        #Preallocate network and target network input matrices.
        update_input = np.zeros((batch_size, self.state_size)) #batch_size by state_size two-dimensional array (not matrix!)
        update_target = np.zeros((batch_size, self.state_size)) #Same as above, but used for the target network
        action, reward, done = [], [], [] #Empty arrays that will grow dynamically

        for i in range(self.batch_size):
            update_input[i] = mini_batch[i][0] #Allocate s(i) to the network input array from iteration i in the batch
            action.append(mini_batch[i][1]) #Store a(i)
            reward.append(mini_batch[i][2]) #Store r(i)
            update_target[i] = mini_batch[i][3] #Allocate s'(i) for the target network array from iteration i in the batch
            done.append(mini_batch[i][4])  #Store done(i)

        target = self.model.predict(update_input) #Generate target values for training the inner loop network using the network model
        target_val = self.target_model.predict(update_target) #Generate the target values for training the outer loop target network

        #Q Learning: get maximum Q value at s' from target network
###############################################################################
###############################################################################
        #Insert your Q-learning code here
        #Tip 1: Observe that the Q-values are stored in the variable target
        #Tip 2: What is the Q-value of the action taken at the last state of the episode?0
        for i in range(self.batch_size): #For every batch
            if done[i]:
                target[i][action[i]]=0;
            else:
                target[i][action[i]] = reward[i]+self.discount_factor*np.amax(target_val[i])


###############################################################################
###############################################################################

        #Train the inner loop network
        self.model.fit(update_input, target, batch_size=self.batch_size,
                       epochs=1, verbose=0)
        return
    #Plots the score per episode as well as the maximum q value per episode, averaged over precollected states.
    def plot_data(self, episodes, scores, max_q_mean,last100means,search_space):
        label="{},eps={}, dscf={}, lr={}, ms={}, uf={}, hn={}, hl={}".format(search_space,EPISODES,self.discount_factor,self.learning_rate,self.memory_size,self.target_update_frequency,self.hidden_nodes,self.hidden_layers)

        fig = pylab.figure(figsize=(20,10))
        pylab.subplots_adjust(left=None, bottom=0.1, right=None, top=None, wspace=None, hspace=0.1)
        pylab.suptitle(label)
        pylab.subplot(3,1,1)
        pylab.title("avg. Q value")
        pylab.plot(episodes, max_q_mean, 'b')
        pylab.ylabel("Average Q Value")

        pylab.subplot(3,1,2)
        pylab.title("scores")
        pylab.plot(episodes, scores, 'b')
        pylab.ylabel("Score")

        pylab.subplot(3,1,3)
        pylab.title("running mean (100)")
        pylab.plot(episodes, last100means, 'b')
        pylab.xlabel("Episodes")
        pylab.ylabel("Mean score")
        pylab.savefig("{}/Figures for {}.png".format(search_space,label))

def main(df,lr,ms,uf,hn,hl,search_space_string):

    #For CartPole-v0, maximum episode length is 200
    env = gym.make('CartPole-v0') #Generate Cartpole-v0 environment object from the gym library
    #Get state and action sizes from the environment
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n

    #Create agent, see the DQNAgent __init__ method for details
    agent = DQNAgent(state_size, action_size, df,lr,ms,uf,hn,hl,search_space_string)

    #Collect test states for plotting Q values using uniform random policy
    test_states = np.zeros((agent.test_state_no, state_size))
    max_q = np.zeros((EPISODES, agent.test_state_no))
    max_q_mean = np.zeros((EPISODES,1))
    last100means=np.zeros((EPISODES,1))

    last100=deque();



    done = True
    for i in range(agent.test_state_no):
        if done:
            done = False
            state = env.reset()
            state = np.reshape(state, [1, state_size])
            test_states[i] = state
        else:
            action = random.randrange(action_size)
            next_state, reward, done, info = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            test_states[i] = state
            state = next_state

    scores, episodes = [], [] #Create dynamically growing score and episode counters
    for e in range(EPISODES):
        done = False
        score = 0
        state = env.reset() #Initialize/reset the environment
        state = np.reshape(state, [1, state_size]) #Reshape state so that to a 1 by state_size two-dimensional array ie. [x_1,x_2] to [[x_1,x_2]]
        #Compute Q values for plotting
        tmp = agent.model.predict(test_states)
        max_q[e][:] = np.max(tmp, axis=1)
        max_q_mean[e] = np.mean(max_q[e][:])

        while not done:
            if agent.render:
                env.render() #Show cartpole animation

            #Get action for the current state and go one step in environment
            action = agent.get_action(state)
            next_state, reward, done, info = env.step(action)
            next_state = np.reshape(next_state, [1, state_size]) #Reshape next_state similarly to state

            #Save sample <s, a, r, s'> to the replay memory
            agent.append_sample(state, action, reward, next_state, done)
            #Training step
            agent.train_model()
            score += reward #Store episodic reward
            state = next_state #Propagate state

            if done:
                if len(last100)>100:
                  last100.popleft();

                last100.append(score)

                last100mean=reduce((lambda x,y:(x+y)),last100)/100;

                last100means[e]=last100mean;

                #At the end of very episode, update the target network
                if e % agent.target_update_frequency == 0:
                    agent.update_target_model()
                #Plot the play time for every episode
                scores.append(score)
                episodes.append(e)

                print("episode:", e, "  score:", score, "mean:", last100mean, " q_value:", max_q_mean[e],"  memory length:",
                      len(agent.memory))

                # if the mean of scores of last 100 episodes is bigger than 195
                # stop training
                if agent.check_solve:
                    if np.mean(scores[-min(100, len(scores)):]) >= 195:
                        print("solved after", e-100, "episodes")
                        agent.plot_data(episodes,scores,max_q_mean[:e+1],search_space_string)
                        sys.exit()
    agent.plot_data(episodes,scores,max_q_mean,last100means,search_space_string)

    #pylab.show();

'''
df = [0.9, 0.95, 0.99]
lr = [0.001, 0.01, 0.05, 0.1]
ms = [500, 5000, 50000]
uf = [1, 4, 16, 64]
hn = [1, 2, 4, 8, 16, 32, 64, 128]
hl = [1, 2, 3, 4, 5, 6, 10, 20]
'''

def hn_search():
  df = 0.95
  lr = 0.005
  ms = 1000
  uf = 1
  hn = [1, 2, 4, 8, 16, 32, 64, 128]
  hl=1;
  for n in hn:
    main(df,lr,ms,uf,n,hl,"HN")



def hl_search():
  df = 0.95
  lr = 0.005
  ms = 1000
  uf = 1
  hn = [2,16,32,64]
  hl=[1, 2, 3, 6, 20]
  for n in hn:
    for l in hl:
      main(df,lr,ms,uf,n,l,"HL,HN")


hl_search()
