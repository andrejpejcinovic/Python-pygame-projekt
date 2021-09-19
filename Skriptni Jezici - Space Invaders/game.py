import pygame
import random
import time
import os
pygame.font.init()

WIDTH = 800
HEIGHT = 750
PROZOR = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skriptni jezici - SPACE INVADERS")


CRVENI = pygame.image.load(os.path.join("slike", "crveni.png"))
ZELENI = pygame.image.load(os.path.join("slike", "zeleni.png"))
PLAVI = pygame.image.load(os.path.join("slike", "plavi.png"))
IGRAC = pygame.image.load(os.path.join("slike", "igrac.png"))

CRVENI_LASER = pygame.image.load(os.path.join("slike", "crveni_laser.png"))
ZELENI_LASER = pygame.image.load(os.path.join("slike", "zeleni_laser.png"))
PLAVI_LASER = pygame.image.load(os.path.join("slike", "plavi_laser.png"))
RAKETA = pygame.image.load(os.path.join("slike", "raketa.png"))

POZADINA = pygame.transform.scale(
    pygame.image.load(os.path.join("slike", "pozadina.jpg")), (WIDTH, HEIGHT)
)


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def sudar(self, obj):
        return collide(self, obj)


class Brod:
    COOLDOWN = 20

    def __init__(self, x, y, hp=100):
        self.x = x
        self.y = y
        self.hp = hp
        self.brod_img = None
        self.laser_img = None
        self.laseri = []
        self.cool_down_counter = 0

    def draw(self, window):
        PROZOR.blit(self.brod_img, (self.x, self.y))
        for laser in self.laseri:
            laser.draw(window)

    def move_laseri(self, vel, obj):
        self.cooldown()
        for laser in self.laseri:
            laser.move(vel)
            if laser.off_screen(HEIGHT):                
                self.laseri.remove(laser) # ako izade iz granica igrice brise se laser
            elif laser.sudar(obj):  # ako pogodi laser u objekt(igraca)
                obj.hp -= 10  # uništi enemy
                self.laseri.remove(laser)  # obrisi laser
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1  # ako je veće od nule i nije u cd, inkrementiraj

    def shoot(self):
        if self.cool_down_counter == 0:  # ako nije na cd, onda pucaj
            laser = Laser(self.x + 10  , self.y, self.laser_img)# sa -20 centriramo izlazak lasera iz protivnika,dodaj laser na trenutnu lokaciju
            self.laseri.append(laser)  # dodaj u laser listu
            self.cool_down_counter = 1  # dodaj cd na 1

    def get_width(self):
        return self.brod_img.get_width()

    def get_height(self):
        return self.brod_img.get_height()


class Player(Brod):
    def __init__(self, x, y, hp=100):
        super().__init__(x, y, hp)
        self.brod_img = IGRAC
        self.laser_img = RAKETA
        self.mask = pygame.mask.from_surface(self.brod_img)
        self.max_hp = hp

    def move_laseri(self, vel, objs):
        self.cooldown()
        for laser in self.laseri:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.laseri.remove(laser) # ako izade iz granica igrice brise se laser
            else:
                for obj in objs:
                    if laser.sudar(obj):  # ako pogodi laser u objekt(igraca)
                        objs.remove(obj)  # uništi enemy
                        if laser in self.laseri:
                            self.laseri.remove(laser)  # obrisi laser


    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.brod_img.get_height() + 10, self.brod_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.brod_img.get_height() + 10, self.brod_img.get_width() * (self.hp/self.max_hp), 10))


class Enemy(Brod):
    COLOR_MAP = {
        "crvena": (CRVENI, CRVENI_LASER),
        "zelena": (ZELENI, ZELENI_LASER),
        "plava": (PLAVI, PLAVI_LASER),
    }

    def __init__(self, x, y, color, hp=100):
        super().__init__(x, y, hp)
        self.brod_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.brod_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.laseri.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):  # preklapanje piksela, sudari
    offset_x = obj2.x - obj1.x  # gornji lijevi kut se gleda
    offset_y = obj2.y - obj1.y  # sudar maski poklapanja objekata
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    zivoti = 3
    main_font = pygame.font.SysFont("comicsans", 50)
    gameover_font = pygame.font.SysFont("comicsans", 70)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(340, 600) #inicijalizacija objekta i spawn igrača koordinate pixela

    clock = pygame.time.Clock()

    gameover = False
    gameover_count = 0

    def redraw_window():
        PROZOR.blit(POZADINA, (0, 0)) 
        zivoti_label = main_font.render(f"Zivoti: {zivoti}", 1, (0, 250, 250))
        level_label = main_font.render(f"Level: {level}", 1, (0, 250, 250))

        PROZOR.blit(zivoti_label, (10, 10))
        PROZOR.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(PROZOR)

        player.draw(PROZOR)

        if gameover:
            gameover_label = gameover_font.render("Izgubili ste!", 1, (255, 255, 255))
            PROZOR.blit(gameover_label, (WIDTH / 2 - gameover_label.get_width() / 2, 350))
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if zivoti <= 0 or player.hp <= 0:
            gameover = True
            gameover_count += 1

        if gameover:
            if gameover_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(
                random.randrange(50, WIDTH - 100),
                random.randrange(-1500, -100),
                random.choice(["crvena", "plava", "zelena"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_vel > 0:  # lijevo
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # desno
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # gore
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 20 < HEIGHT:  # dole , ovih 20 znači za hpbar da ne može ići ispod gamescreena 
            player.y += player_vel 
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laseri(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:  # ucestalost pucanja protivnika
                enemy.shoot()

            if collide(enemy, player):  # ako se sudare player i enemy
                player.hp -= 10  # oduzmi playeru 10hp
                enemies.remove(enemy)  # unisti enemy

            elif enemy.y + enemy.get_height() > HEIGHT:
                zivoti -= 1
                enemies.remove(enemy)

        # provjera je li udario laser u objekt
        player.move_laseri(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        PROZOR.blit(POZADINA, (0, 0))
        title_label = title_font.render(
            "Klikni mišem za početak igre!", 1, (255, 255, 255))
        PROZOR.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
