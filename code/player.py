import pygame # type: ignore
from settings import *
from support import import_folder
from timer import Timer  # type: ignore

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites):
        super().__init__(group)
        
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        
        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy().inflate((-126,-70))
        self.z = LAYERS['main']
        
        # collision
        self.collision_sprites = collision_sprites
        
        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2()
        self.speed = 200
        
        # timers
        self.timers = {
            'tool use': Timer(350,self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200)
        }
        
        # tool
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        
        # seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        
    def use_tool(self):
        pass
        
    def use_seed(self):
        pass
    
    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'right': [], 'left': [],
                           'up_idle': [], 'down_idle': [], 'right_idle': [], 'left_idle': [],
                           'up_hoe': [], 'down_hoe': [], 'right_hoe': [], 'left_hoe': [],
                           'up_axe': [], 'down_axe': [], 'right_axe': [], 'left_axe': [],
                           'up_water': [],'down_water':[],'right_water': [],'left_water': []}
        for animation in self.animations.keys():
            path = f'../graphics/character/{animation}'
            self.animations[animation] = import_folder(path)
            
    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def get_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.timers['tool use'].active:
            # vertical movement
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
                
            # horizontal movement
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0
                
            # tool use
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
                
            # switch tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index = (self.tool_index + 1) % len(self.tools)
                self.selected_tool = self.tools[self.tool_index]
                
            # seed use
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
                print('use seed')
            
            # switch seed
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index = (self.seed_index + 1) % len(self.seeds)
                self.selected_seed = self.seeds[self.seed_index]
                print(self.selected_seed)
    
    def get_status(self):
        # idle
        if self.direction.magnitude() == 0:
            self.status = f'{self.status.split("_")[0]}_idle'
        
        # tool use
        if self.timers['tool use'].active:
            self.status = f'{self.status.split("_")[0]}_{self.selected_tool}'
    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    
    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox') and sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: # moving right
                        self.hitbox.right = sprite.hitbox.left
                    elif self.direction.x < 0: # moving left
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
                elif direction == 'vertical':
                    if self.direction.y > 0: # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    elif self.direction.y < 0: # moving up
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery
    
    def movement(self, dt):
        # normalizing a vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
            
        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def update(self, dt):
        self.get_input()
        self.get_status()
        self.update_timers()
        self.movement(dt)
        self.animate(dt)