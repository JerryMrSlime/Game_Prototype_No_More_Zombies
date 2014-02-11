import pygame as py
from pygame.locals import QUIT, K_j, K_a, K_w, K_d, K_RIGHT, K_UP, K_LEFT, K_k
from random import randrange

SCALE = 8
WIDTH = 64 * SCALE
HEIGHT = 18 * SCALE
SCREENSIZE = (WIDTH, HEIGHT)
FPS = 60
GROUND = HEIGHT - 4 * SCALE
CLEAR = (116, 109, 199)
BULLETSPEED = 5


class CollisionManager(object):
    
    def __init__(self, player, zombiesManager, projectilesManager, particlesManager):
        self.player = player
        self.zManager = zombiesManager
        self.pManager = projectilesManager
        self.ptManager = particlesManager
        self.coll = Collision()
        
    def Update(self):
        self.ZombiesBullets()
        self.ZombiesPlayer()
    
    def ZombiesPlayer(self):
        for zombie in self.zManager.zombies:
            if self.coll.Check(self.player, zombie) and zombie.canAttack:
                zombie.canAttack = False
                x = self.player.x + self.player.width / 2
                y = self.player.y + self.player.height / 2
                self.ptManager.AddEmitter(ParticlesEmitter(x, y, 0, -8, 20, 255, 0, 0, 2))
                
    def ZombiesBullets(self):
        for zombie in self.zManager.zombies:
            for projectile in self.pManager.projectiles:
                if self.coll.Check(zombie, projectile):
                    self.zManager.zombies.remove(zombie)
                    self.pManager.projectiles.remove(projectile)
                    
                    x = projectile.x
                    
                    if zombie.direction == 1:
                        x -= SCALE
                    else:
                        x += SCALE
                        
                    self.ptManager.AddEmitter(ParticlesEmitter(x, projectile.y, -1 * 6 * projectile.direction, -6, 20, 255, 0, 0, 2))
                    
                    
class Collision(object):
    
    def Check(self, ob1, ob2):
        if (ob1.x > ob2.x + ob2.width or
            ob1.y > ob2.y + ob2.height or
            ob1.x + ob1.width < ob2.x or
            ob1.y + ob1.height < ob2.y):
            return False
        else:
            return True

class ZombiesManager(object):
    
    def __init__(self, graphics):
        self.normalZombie_img = graphics.subsurface(6 * SCALE, 0, 5 * SCALE, 5 * SCALE)
        self.zombieDog_img = graphics.subsurface(11 * SCALE, 0, 7 * SCALE, 5 * SCALE)
        self.bigZombie_img = graphics.subsurface(18 * SCALE, 0, 6 * SCALE, 10 * SCALE)
        
        self.groundNormalZombie = HEIGHT - 4 * SCALE - self.normalZombie_img.get_height()
        self.groundZombieDog = HEIGHT - 4 * SCALE - self.zombieDog_img.get_height()
        self.groundBigZombie = HEIGHT - 4 * SCALE - self.bigZombie_img.get_height()
        
        self.zombies = [NormalZombie(self.normalZombie_img, 100, self.groundNormalZombie, 1)]
        
    def Render(self, screen):
        for zombie in self.zombies:
            zombie.Render(screen)
            
    def Update(self):
        for zombie in self.zombies:
            zombie.Update()
            if not zombie.alive:
                self.zombies.remove(zombie)
    
    
class Entity(object):
    def __init__(self, img, x, y, direction):
        self.img = img
        self.flipped = py.transform.flip(self.img, True, False)
        self.imgs = [self.img, self.flipped]
        self.x, self.y = x, y
        self.width, self.height = self.img.get_width(), self.img.get_height()
        self.vx = 2 * direction
        self.alive = True
        self.lifes = 3
        self.direction = direction
        self.canAttack = True
        self.attackDelay = 500
        self.attackTimer = 0
        
    def Render(self, screen):
        if self.vx < 0:
            screen.blit(self.imgs[1], (self.x, self.y))
        else:
            screen.blit(self.imgs[0], (self.x, self.y))
        
    def Update(self):
        self.x += self.vx
        
        if self.x < 0 or self.x + self.width > WIDTH:
            self.vx *= -1
            
        if self.lifes <= 0:
            self.alive = False
        
        self.AttackTimer()
            
    def AttackTimer(self):
        if py.time.get_ticks() - self.attackTimer > self.attackDelay:
            self.attackTimer = py.time.get_ticks()
            self.canAttack = True

class NormalZombie(Entity):
    def __init__(self, img, x, y, direction):
        Entity.__init__(self, img, x, y, direction)            


class Particle(object):
    
    def __init__(self, x, y, vx, vy, r, g, b, scale):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = (r, g, b)
        self.scale = scale
        self.alive = True
        self.gravity = 1
    
    def Render(self, screen):
        py.draw.rect(screen, self.color, (self.x, self.y, self.scale, self.scale))
        
    def Update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.alive = False
        
class ParticlesEmitter(object):
    
    def __init__(self, x, y, vx, vy, maxParticles, r, g, b, particleSize):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.particles = []
        self.max = maxParticles
        self.pSize = particleSize
        self.r = r
        self.g = g
        self.b = b
        self.Generate()
        
    def Generate(self):
        for i in range(self.max):
            x1 = self.x - 2
            x2 = self.x + 2
            y1 = self.y - 2
            y2 = self.y + 2
            vx1 = self.vx - 1
            vx2 = self.vy + 1
            vy1 = self.vy - 1
            vy2 = self.vy + 1
            
            if vx2 < 0:
                vx2 *= -1
            if vy2 < 0:
                vy2 *= -1
                
            if vx1 == vx2:
                vx1 -= 1
            x = randrange(x1, x2)
            y = randrange(y1, y2)
            vx = randrange(vx1, vx2)
            vy = randrange(vy1, vy2)
            
            self.particles.append(Particle(x, y, vx, vy, self.r, self.g, self.b, self.pSize) )
    
    
class BulletBody(object):
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.alive = True
        self.vx = 4 * direction
        self.vy = -5
        self.gravity = 1
    
    def render(self, screen):
        py.draw.rect(screen, (255, 255, 0), (self.x, self.y, 2, 2))
    
    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.alive = False

class ParticlesManager(object):
    def __init__(self):
        self.particles = []
        self.emitters = []
        
    def render(self, screen):
        self.RenderParticles(screen)
        self.RenderEmitters(screen)
    
    def update(self):
        self.UpdateParticles()
        self.UpdateEmitters()
    
    def RenderParticles(self, screen):
        for particle in self.particles:
            particle.render(screen)
    
    def RenderEmitters(self, screen):
        for emitter in self.emitters:
            for particle in emitter.particles:
                particle.Render(screen)
                
    def UpdateParticles(self):
        for particle in self.particles:
            particle.update()
            if not particle.alive:
                self.particles.remove(particle)
                
    def UpdateEmitters(self):
        for emitter in self.emitters:
            for particle in emitter.particles:
                particle.Update()
                if not particle.alive:
                    emitter.particles.remove(particle)
                    
    def Shoot(self, x, y, direction):
        self.particles.append(BulletBody(x, y, direction * -1))
        
    def AddEmitter(self, emitter):
        self.emitters.append(emitter)
        
class ProjectilesManager(object):
    def __init__(self, graphics):
        self.bullet_img = graphics.subsurface(6 * SCALE, 5 * SCALE, SCALE, SCALE)
        self.grenade_img = graphics.subsurface(7 * SCALE, 5 * SCALE, SCALE, SCALE)
        
        self.projectiles = []
        
    def render(self, screen):
            for projectile in self.projectiles:
                projectile.render(screen)
        
    def update(self):
            for projectile in self.projectiles:
                projectile.update()
                if projectile.x + SCALE < 0 or projectile.x > WIDTH:
                    self.projectiles.remove(projectile)
                    
    def Shoot(self, kind, x, y, direction):
            if kind == 1:
                self.projectiles.append(Bullet(self.bullet_img, x, y, direction))
            if kind == 2:
                self.projectiles.append(Grenade(self.grenade_img, x, y, direction))
                

class Grenade(object):
    def __init__(self, img, x, y, direction):
        self.img = img
        self.width = img.get_width()
        self.height = img.get_height()
        self.x = x
        self.y = y
        self.vx = 8 * direction
        self.vy = -10
        self.gravity = 1
        self.direction = direction
        
    def render(self, screen):
        screen.blit(self.img, (self.x, self.y))
        
    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

class Bullet(object):
    def __init__(self, img, x, y, direction):
        self.img = img
        self.width = img.get_width()
        self.height = img.get_height()
        self.x = x
        self.y = y
        self.vx = 8 * direction
        self.direction = direction
        
    def render(self, screen):
        screen.blit(self.img, (self.x, self.y))
        
    def update(self):
        self.x += self.vx

        
class Star(object):
    def __init__(self, img, x, y):
        self.img = img
        self.x = x
        self.y = y
        
    def Render(self, screen):
        screen.blit(self.img, (self.x, self.y))
        

class Background(object):
    def __init__(self, graphics, wallHeight):
        #STARS
        self.star_img = graphics.subsurface(3 * SCALE, 5 * SCALE, 3 * SCALE, 3 * SCALE)
        self.star_img = py.transform.scale(self.star_img, (3, 3))
        self.size = 3
        self.maxStars = 20
        self.stars = []
        self.wallHeight = wallHeight
        self.generateStars()
        #MOON
        self.moonWidth = 3 * SCALE
        self.moonHeight = 6 * SCALE
        self.moon = graphics.subsurface(0, 5 * SCALE, self.moonWidth, self.moonHeight)
        
    def generateStars(self):
        for i in range(self.maxStars):
            x = randrange(0, WIDTH - 3)
            y = randrange(0, HEIGHT - self.wallHeight - 3)
            self.stars.append(Star(self.star_img, x, y))
            
    def render(self, screen):
        screen.blit(self.moon, (WIDTH - self.moonWidth * 4, 2 * SCALE))
        for star in self.stars:
            star.Render(screen)
            
            
class Ground(object):

    def __init__(self, graphics):
        self.wallWidth = 64 * SCALE
        self.wallHeight = 6 * SCALE
        self.wall = graphics.subsurface(0, 12 * SCALE, self.wallWidth, self.wallHeight)

    def render(self, screen):
        screen.blit(self.wall, (0, HEIGHT - self.wallHeight))


class Player(object):
    def __init__(self, graphics, pM):
        self.x, self.y, self.width, self.height = 0, 0, 6 * SCALE, 5 * SCALE
        self.vx, self.vy = 0, 0
        self.speed = 5
        self.jumpSpeed = -15
        self.gravity = 2
        self.onGround = False
        self.img = graphics.subsurface(0, 0, self.width, self.height)
        self.img_flipped = py.transform.flip(self.img, True, False)
        self.imgs = [self.img, self.img_flipped]
        self.direction = 0
        self.pManager = ProjectilesManager(graphics)
        self.particlesManager = pM
        
        self.canShoot = True
        self.shootDelay = 200
        self.shootTimer = 0
        
        self.canThrowGrenade = True
        self.grenadeDelay = 750
        self.grenadeTimer = 0

    def render(self, screen):
        screen.blit(self.imgs[self.direction], (self.x, self.y))
        self.pManager.render(screen)

    def update(self):
        self.Controls()
        self.Move()
        self.pManager.update()
        self.resetShoot()
        
    def Move(self):
        if not self.onGround:
            self.vy += self.gravity
        else:
            self.vy = 0

        self.x += self.vx
        self.y += self.vy

        if self.y + self.height > GROUND:
            self.y = GROUND - self.height
            self.onGround = True

    def Controls(self):
        key = py.key.get_pressed()
        if key[K_RIGHT] or key[K_d]:
            self.vx = 1
            self.direction = 0
        elif key[K_LEFT] or key[K_a]:
            self.vx = -1
            self.direction = 1
        else:
            self.vx = 0
        self.vx *= self.speed

        if key[K_UP] and self.onGround or key[K_w] and self.onGround:
            self.vy = self.jumpSpeed
            self.onGround = False
            
        if key[K_j] and self.canShoot:
            if self.direction == 0:
                self.pManager.Shoot(1, self.x+6*SCALE, self.y+2*SCALE, 1)
                self.particlesManager.Shoot(self.x+self.width-SCALE, self.y+2*SCALE, 1)
            else:
                self.pManager.Shoot(1, self.x-SCALE, self.y+2*SCALE, -1)
                self.particlesManager.Shoot(self.x+SCALE-1, self.y+2*SCALE, -1)
            self.canShoot = False
            
        if key[K_k] and self.canThrowGrenade:
            if self.direction == 0:
                self.pManager.Shoot(2, self.x+6*SCALE, self.y+2*SCALE, 1)
            else:
                self.pManager.Shoot(2, self.x-SCALE, self.y+2*SCALE, -1)
            self.canThrowGrenade = False
                
    def resetShoot(self):
        if py.time.get_ticks() - self.shootTimer > self.shootDelay:
            self.shootTimer = py.time.get_ticks()
            self.canShoot = True
        
        if py.time.get_ticks() - self.grenadeTimer > self.grenadeDelay:
            self.grenadeTimer = py.time.get_ticks()
            self.canThrowGrenade = True
        
def main():
    py.init()
    screen = py.display.set_mode(SCREENSIZE)
    exit = False
    clock = py.time.Clock()
    img = py.image.load("graphics.png").convert_alpha()
    img = py.transform.scale(img, (img.get_width() * SCALE, img.get_height() * SCALE))
    particlesManager = ParticlesManager()
    zombiesManager = ZombiesManager(img)
    player = Player(img, particlesManager)
    ground = Ground(img)
    bg = Background(img, ground.wallHeight)
    collManager = CollisionManager(player, zombiesManager, player.pManager, particlesManager)
    
    while not exit:
        for event in py.event.get():
            if event.type == QUIT:
                exit = True
        screen.fill(CLEAR)
        
        bg.render(screen)
        player.render(screen)
        player.update()
        zombiesManager.Render(screen)
        zombiesManager.Update()
        particlesManager.render(screen)
        particlesManager.update()
        collManager.Update()
        ground.render(screen)
        
        py.display.update()
        clock.tick(FPS)
    return 0

if __name__ == "__main__":
    main()
