import pygame
import neat
import time
import os
import random
pygame.font.init()


#height and width of the window
WIN_WIDTH =600
WIN_HEIGHT =800

GEN = 0

#storing the images
BIRD_IMGS =[pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG =pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG =pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG =pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT =pygame.font.SysFont("comicsans",50)

#BIRD CLASS WITH ITS FUNCTION / METHODS
class Bird:
    IMGS=BIRD_IMGS
    MAX_ROTATION=25
    ROT_VEL=20
    ANIMATION_TIME=5
    
    def __init__(self,x,y):
        self.x = x #X,Y ARE STARTING POSITION
        self.y = y
        self.tilt=0 #HOW MUCH TITLED THE BIRD WILL BE 
        self.tick_count=0 
        self.vel=0  #ITS NOT MOVING AT FIRST
        self.height=self.y #Y AXIS WILL BE THE HIEGHT
        self.img_count=0 # WHICH BIRD WE WILL SHOW  
        self.img=self.IMGS[0] #BIRD IMAGES
        
    def jump(self):
        self.vel=-10.5 #going up -> negative velocity and going down positive velocity 
        self.height==self.y  #where the bird jumped from
        self.tick_count=0 #track of when we last jumped 
        
    def move(self):
        self.tick_count+=1
        
        d=self.vel*self.tick_count + 1.5*self.tick_count**2    #how many pixels are morving up and own in a frame
        if d>=16: 
            d=16     
        if d<0: 
            d-=2   
            
        self.y=self.y+d #adding the dsiplacement to current to current y position to update it 
        
        if d<0  or self.y<self.height+50:
            if self.tilt<self.MAX_ROTATION:
                self.tilt=self.MAX_ROTATION
        else:
            if self.tilt>-90:
                self.tilt-=self.ROT_VEL
        
    def draw(self,win):
        self.img_count+=1
        if self.img_count<=self.ANIMATION_TIME:
            self.img=self.IMGS[0]
            
        elif self.img_count<=self.ANIMATION_TIME*2:
            self.img=self.IMGS[1]
            
        elif self.img_count<=self.ANIMATION_TIME*3:
            self.img=self.IMGS[2]
            
        elif self.img_count<=self.ANIMATION_TIME*4:
            self.img=self.IMGS[1]
            
        elif self.img_count==self.ANIMATION_TIME*4 +1:
            self.img=self.IMGS[0]
            self.img_count=0
        #this is basically for changing the birds images to make it feel like flying 
        #first img 0 (up)-> img1 (mid) then -> img 2(down)->img1(mid)->img0(up) 
        if self.tilt<= -80:
            self.img=self.IMGS[1]
            self.img_count=self.ANIMATION_TIME*2      
            
        rotated_image= pygame.transform.rotate(self.img,self.tilt) #when the bird will fal it will rortate by 90 degres so this is funtion for rotating the bird 
        new_rect=rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x,self.y)).center)   
        win.blit(rotated_image,new_rect.topleft)
        
    def get_mask(self): #mask method for colliding objects
        return pygame.mask.from_surface(self.img)


#PIPE CLASS WITH ITS FUNCTIONS  
class Pipe:
    GAP=200    
    VEL=5
    
    def __init__(self,x):
        self.x=x
        self.height=0
        
        
        self.top=0
        self.bottom=0
        
        #here basically we are flipping the pipe upside dowwn and storing int he class
        self.PIPE_TOP=pygame.transform.flip(PIPE_IMG,False,True)
        self.PIPE_BOTTOM=PIPE_IMG
        
        self.passed=False #for indiccaing the bird has passed by this pipe or not  
        self.set_height()
        
    def set_height(self):
        self.height=random.randrange(50,450 ) #where the top of the pipe will be on the screen 
        self.top=self.height-self.PIPE_TOP.get_height() #finding the co ordinate of top of the pipe 
        self.bottom=self.height+self.GAP #similarly for getting the bottom of the pipe 
        
    def move(self):  #moving the pipe as the pipes will move and the bird will be still
        self.x -=self.VEL #basically the pipes are moving along x axis 
        
        
    def draw(self,win):#this is for drawing the pipes on the screen
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))
        
    def collide(self,bird): #this is used to find if the bird collied with the pipes or not 
        #here basically we used mask method colliding objects are masked 
        #and all the points or pixels inside the mask are stored in a array 
        #if they collied there wil be a intersection if not no intersection 
        bird_mask = bird.get_mask() 
        top_mask=pygame.mask.from_surface(self.PIPE_TOP) #masking the top of the pipe 
        bottom_mask=pygame.mask.from_surface(self.PIPE_BOTTOM) #masking the bottom of the pipe
        
        top_offset=( self.x -bird.x, self.top- round(bird.y))
        bottom_offset=( self.x -bird.x, self.bottom- round(bird.y))
        
        b_point=bird_mask.overlap(bottom_mask,bottom_offset) # the overlapping points - bottom
        t_point=bird_mask.overlap(top_mask,top_offset) # the overlapping points - top
        
        if(t_point or b_point): #if b collides with t return true else false 
            return True
        
        return False
        
class Base: #a class for the base only x axis will move 
    VEL=5
    WIDTH=BASE_IMG.get_width()
    IMG=BASE_IMG
    
    def __init__(self,y):
        self.y=y
        self.x1=0
        self.x2=self.WIDTH
        
    def move(self): #two bas eimages of full screen width are conncted in a cyclic way so one 
                    #one comes on the screen and another goes behind it and comes again just
                    #after it and thus the cycle repeats 
        self.x1-=self.VEL
        self.x2-=self.VEL
        
        if self.x1+self.WIDTH<0:
            self.x1=self.x2+self.WIDTH #x2 comes after x1
        if self.x2+self.WIDTH<0:
            self.x2=self.x1+self.WIDTH #x1 comes after x2
    
    def draw(self,win):  #drawing the base
        win.blit(self.IMG, (self.x1,self.y))  #drawing the base 
        win.blit(self.IMG, (self.x2,self.y))
         
        
        
    
    
#functions under no class - in general functions    
def draw_window(win,birds,pipes,base,score,gen): #blit() means draw 
    win.blit(BG_IMG,(0,0)) #in the window we are basically drawing the background image 
    
    for pipe in pipes : #drawing the pipe
        pipe.draw(win)
    text=STAT_FONT.render("Score: " + str(score),1,(255,255,255))  #for showing th score 
    win.blit(text,(WIN_WIDTH-10-text.get_width(),10)) # printing the score 
    
    
    text=STAT_FONT.render("Gen: " + str(gen),1,(255,255,255))  #for showing th score 
    win.blit(text,(10,10)) # printing the score 
    
    
    base.draw(win) #drawing base
    for bird in birds:
        bird.draw(win) # drawing the bird
        
    pygame.display.update() #updating the display 
                
def main(genomes,config ): #genomes are neural networks with nodes and genes
    global GEN
    GEN +=1
    nets=[] #
    ge=[] #
    birds=[]#for the bird
    
    
    for _,g in genomes: #genome is tupple actually
        net=neat.nn.FeedForwardNetwork.create(g,config) #setting up the neural network 
        nets.append(net)
        birds.append(Bird(230,350)) #standard bird object starting at the point
        #implementing the genome at same position of the bird object to track the fitness
        g.fitness=0 #initial fitness 0 
        ge.append(g)
        
        
    base=Base(730)
    pipes=[Pipe(700)]
    win= pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))  #for displaying the window 
    
    clock=pygame.time.Clock()
    score=0
    run=True
    while run:
        clock.tick(30)  #this is basically the clock for controlling time taken to fall  higher tick smaller time 
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                pygame.quit()
                quit()
                
        #incase of getting two pipes in a the way 
        #if len(bird)>1 then if x co ordinate of 
        # ird is more than the first pipe the switch to the 2nd pipe
        pipe_ind=0        
        if len(birds):
            if len(pipes)>1 and birds[0].x> pipes[0].x+ pipes[0].PIPE_TOP.get_width():
                pipe_ind=1
        else:
            run=False
            break
         
       
       
        # to mobve birds along with them giving some fitness for reaching this far
        # then having the output of the neural network which takes input of
        #birds y co ordinate
        #difference between bird y and upper pipe 
        #difference between bird y and lower pipe 
        #if o/p >0.5 the bird have to jump we have set it such as this 0.5 is specific value 
        for x, bird in enumerate(birds):
            
            ge[x].fitness+=0.1    
            bird.move()    
            
            output=nets[x].activate((bird.y,abs(bird.y-pipes[pipe_ind].height),abs(bird.y-pipes[pipe_ind].bottom)))
            if output[0]>0.5:  #output is actually a list
                bird.jump()
        
        add_pipe=False
        rem=[]
        for pipe in pipes:
            for x, bird in enumerate(birds): #to get the position of the bird in the list
                if pipe.collide(bird):
                    ge[x].fitness -=1 #if the bird hits the pipe the fitnes score decreases by 1
                    birds.pop(x) #remove the bird from the list
                    nets.pop(x) #remove the neural network associated with the bird
                    ge.pop(x) #remove the genome of that bird
            
                if not pipe.passed and pipe.x <bird.x:
                    pipe.passed=True
                    add_pipe=True
            if pipe.x+pipe.PIPE_TOP.get_width()<0:
                rem.append(pipe)
            pipe.move()
            
        if add_pipe:
            score+=1
            for g in ge:
                 g.fitness+=5 #if the birds made throgh the pipe in that case increase fitness by 5 points
            pipes.append(Pipe(600))
        
          
        for r in rem:
            pipes.remove(r)
        
        
        #chehck if birds hits the ground 
        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >=730 or  bird.y<0:
               
                birds.pop(x) #remove the bird from the bird which hits the ground
                nets.pop(x)#remove the neural network
                ge.pop(x) #remove genome
        
        
        base.move()
        draw_window (win, birds, pipes, base, score,GEN)
        
    
    

        
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)  #including sub heading we used in.txt file 
    p=neat.Population(config)  #setting up population input
    
    p.add_reporter(neat.StdOutReporter(True))
    stats= neat.StatisticsReporter()
    p.add_reporter(stats)  #the output
    
    
    winner=p.run(main,50) #fitness function 
    
if __name__ == "__main__":
    local_dir=os.path.dirname(__file__) #path to the directory we are currently in 
    config_path=os.path.join(local_dir,"config-feedforward.txt") #this basically joins our .txt file with the directory
    run(config_path)
    