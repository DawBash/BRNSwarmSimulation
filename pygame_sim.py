from pickle import FALSE
import pygame, sys
import numpy as np 
import random 
from scipy.special import expit
'''constants'''
BLACK = (0, 0, 0)
WHITE = (255,255,255)
BLUE = (0,100,255)
GREEN = (0,255,0)
RED = (255,0,0)

BACKGROUND = WHITE
HAZARDOUS_REGIONS_XY = [ (400, 400), (300, 150), (250, 300), (300, 450) ]
#HAZARDOUS_REGIONS_XY = [(100,100)]

class Agent(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        color = None,
        radius = 5,
        velocity = [0,0],
    ):
        super().__init__()
        self.image = pygame.Surface(
            [radius * 2, radius * 2])
        self.image.fill(BACKGROUND)
        pygame.draw.circle(
            self.image, color, (radius, radius), radius
        )
        
        self.rect = self.image.get_rect()
        self.pos = np.array([x,y], dtype = np.float64)
        self.vel = np.asarray(velocity, dtype = np.float64)

        self.WIDTH = width 
        self.HEIGHT = height 

        self.deactivated = False
        self.energy = 100
        self.fitness = 0
        self.food_list = []
        self.steps_taken = 0
        self.moving_average_list = []
        self.BRN_list = []
        self.norm_BRN_list = []
        self.energy_list = []
        self.x_val = 0
        self.current_BRN_val = random.randint(0,100)
        print(self.current_BRN_val)
        self.m = random_floats(-9.99, 9.99, 2)
        self.c = random_floats(-9.99, 9.99, 2)
        self.energy = 500
        self.in_danger = False
        self.eaten = False
    
    def closest_agent(self):
        '''detects if agent is too close'''
        '''TODO: migrate to general sensor method that I will implement'''
        closest_agent = min([i for i in agent_container if i is not self], key=lambda i: pow(i.rect.x-self.rect.x, 2) + pow(i.rect.y-self.rect.y, 2))
        dist = pygame.math.Vector2(closest_agent.rect.x, closest_agent.rect.y).distance_to((self.rect.x, self.rect.y))
        return dist

    def is_food(self):
        '''detects if food is close enough'''
        '''TODO: migrate to general sensor method that I will implement'''
        closest_food = min([i for i in food_container], key=lambda i: pow(i.rect.x-self.rect.x, 2)+ pow(i.rect.y-self.rect.y, 2))
        dist = pygame.math.Vector2(closest_food.rect.x, closest_food.rect.y).distance_to((self.rect.x, self.rect.y))
        closest_food_coord = closest_food.rect.x, closest_food.rect.y
        return dist, closest_food_coord

    def is_hazard(self):
        '''detects if a hazard is close by'''
        '''TODO: migrate to general sensor method that I will implement'''
        closest_hazard = min ([i for i in hazardous_region_container], key=lambda i : pow(i.rect.x-self.rect.x,2) + pow(i.rect.y -self.rect.y,2))
        dist = pygame.math.Vector2(closest_hazard.rect.x, closest_hazard.rect.y).distance_to((self.rect.x, self.rect.y))
        closest_hazard_coord = closest_hazard.rect.x, closest_hazard.rect.y
        return dist

    def is_deactivated(self):
        '''detects if energy is below threshold and removes agent from simulation (and sprite group) '''
        if self.energy <= 0:
            self.deactivated = True
            self.kill()
    
    def in_hazardous_region(self):
        '''checks whether an agent is within the hazardous region by looking at the x and y ranges'''
        for i,j in HAZARDOUS_REGIONS_XY:
            if((i <= self.pos[0] <= i+50) and (j <= self.pos[1] <= j+50)):
                self.in_danger = True
            else:
                self.in_danger = False
    
    '''TODO: add reset method for new generation '''
    '''TODO: add utility method to aid in setting parameters from a file'''


        

    def update(self):
        
        avoiding = False
        self.eaten = False
        self.in_danger = False
        self.is_deactivated()
        self.in_hazardous_region()
        


        self.pos += self.vel 

        x, y = self.pos
        '''keeps agents within the 'walls' of the simulation'''
        if x < 0:
            self.vel[0] = -self.vel[0]
        
        if x > self.WIDTH-10:
            self.vel[0] = -self.vel[0]

        if y < 0:
            self.vel[1] = -self.vel[1]

        if y > self.HEIGHT-10:
            self.vel[1] = -self.vel[1]

        self.rect.x = x
        self.rect.y = y
        '''will be edited once sensor is added, the detection distances should all be the same and not alter
            depending on what is being sensed. This is slightly tricky using L2 norm due to the coords of the regions 
            being defined by the leftmost corner (by pygame), so for now I used 70 as that covers all of the square (it's
            basically the length of the hypotenuse of the two right-angled triangles which make up the square)'''

        '''checks probability, first line ensures that agents can leave region once they have entered'''
    
        if self.is_hazard() < 70:
            
            if not self.in_danger:
                if self.current_BRN_val >= probability():
                    pass
            
            elif self.in_danger:
                pass
            else:
                self.vel = -self.vel
                avoiding = True
       
        '''moves away from closest agent should they reach the distance threshold- will alter once the actual sensor method is added'''
        if len(agent_container) >1:
            if self.closest_agent() < 15:
                self.vel = -self.vel
                avoiding = True
        '''makes sure that the agent isn't avoiding anything and then goes to the closest food item within range,
        this method needs improvement once the sensor is added (and it may be better for the agent to follow a vector towards it rather 
        than 'jumping' to the coords'''
        if avoiding == False: 
            closest_food = self.is_food()
            if closest_food[0] < 15:
          
      
                self.rect.x = closest_food[1][0]
                self.rect.y = closest_food[1][1]
                self.eaten = True
                self.energy +=5
                self.food_list.append(1)
                print('EATEN')
        '''normalises the velocity if it goes over a certain threshold'''
        vel_norm = np.linalg.norm(self.vel)
        if vel_norm > 5:
            self.vel /= vel_norm
        '''alters the velocity to enable to random walk behaviour '''
        self.vel += np.random.rand(2) * 2 - 1
        if not self.eaten:
            self.energy -= 1
            self.food_list.append(0)
        

        if self.in_danger:
            self.energy -= 3
            print('IN DANGER')
       
        '''BRN method and updating of food and energy lists'''
        self.energy_list.append(self.energy)
        '''burn in period and max num of iterations '''
        if len(self.food_list) >= 20 and self.steps_taken < T:
            '''calculate moving average list'''
            self.moving_average_list = moving_average(self.food_list,20)
            '''normalised x value (via the time window) at current time step'''
            self.x_val = (self.moving_average_list[-1]/20)
            '''append boldness value at each timestep to list'''
            self.BRN_list.append(BRN(self.m, self.x_val, self.c))
            '''normalise the boldness value at current timestep'''
            self.current_BRN_val = expit(self.BRN_list[-1])
            '''append to normalised BRN list'''
            self.norm_BRN_list.append(self.current_BRN_val)
            print(self.moving_average_list)
        
        self.steps_taken += 1
   


class Food(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        color = GREEN,
        radius = 4.5,
    ):
        super().__init__()
        self.image = pygame.Surface(
            [radius * 2, radius * 2])
        self.image.fill(BACKGROUND)
        pygame.draw.circle(
            self.image, color, (radius, radius), radius
        )
        self.rect = self.image.get_rect()
        self.pos = np.array([x,y], dtype = np.float64)


        self.WIDTH = width
        self.HEIGHT = height 

    def update(self):
        
        x,y = self.pos

        self.rect.x = x
        self.rect.y = y
        self.is_eaten()
            
    
    def is_eaten(self):
        ''' food items are removed on collision- eaten'''
        if pygame.sprite.spritecollideany(self, agent_container):
            self.kill()

class Hazardous_Regions(pygame.sprite.Sprite):
    def __init__(self,
                 x,
                 y,
                 width,
                 height,
                 color = RED
                 ):
        super().__init__()
        self.image = pygame.Surface((width,height))
        self.image.fill(color)
        pygame.draw.rect(
            self.image, color, (x,y,width,height)
        )
        self.rect = self.image.get_rect()
        self.pos = np.array([x,y], dtype = np.float64)

    def update(self):
        
        x,y = self.pos

        self.rect.x = x
        self.rect.y = y

def probability():
    prob = random.randint(0,100)
    return prob

def moving_average(sensory_list, w):
        return (np.convolve(sensory_list, np.ones(w), 'valid') / w)

def BRN(m, moving_average_point, c):
    boldness = (m*moving_average_point) + c
    return boldness 

def random_floats(lower, upper, decimal_places):
    value = round(random.uniform(lower, upper),decimal_places)
    return value


WIDTH = 500
HEIGHT = 500
pygame.init()
screen = pygame.display.set_mode(
    [WIDTH, HEIGHT]
)

agent_container = pygame.sprite.Group()

for i in range(10):
    x = np.random.randint(0,WIDTH+1)
    y = np.random.randint(0, HEIGHT+1)
    vel = np.random.rand(2) * 2 -1
    agent = Agent(x,y, WIDTH, HEIGHT, color = BLUE, velocity = vel)
    agent_container.add(agent)

food_container = pygame.sprite.Group()

for i in range(200):
    x = np.random.randint(0,WIDTH+1)
    y = np.random.randint(0, HEIGHT+1)
    food = Food(x,y,WIDTH, HEIGHT)
    food_container.add(food)

hazardous_region_container = pygame.sprite.Group()

for i,j in HAZARDOUS_REGIONS_XY:
    x = i
    y = j
    hazard = Hazardous_Regions(x,y, 50, 50)
    hazardous_region_container.add(hazard)



T = 500

clock = pygame.time.Clock()

for i in range(T):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    '''TODO: add another loop which allows for generational iterations (can be copied from previous code)'''

    
    food_container.update()
    hazardous_region_container.update()
    agent_container.update()

    screen.fill(BACKGROUND)

    
    hazardous_region_container.draw(screen)
    food_container.draw(screen)
    agent_container.draw(screen)

    pygame.display.flip()
    
    clock.tick(30)

pygame.quit()