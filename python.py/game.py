import pygame
from player import Player
from house import House
from house import StartingHouse
from upgrade import GuardDog, FriendlyNeighbor, HouseCleaner, Gardener, HouseRepair, Garage
import time
import random

screen_width, screen_height = 1000, 700
FPS = 60


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Estate Clicker")

        self.upgrades  = [
            GuardDog(),
            FriendlyNeighbor(),
            HouseCleaner(),
            Gardener(),
            HouseRepair(),
            Garage()]
        for upgrade in self.upgrades:
            upgrade.load_images()

        font_path = "C:/Users/g1230/Downloads/zekton-free/zekton rg.otf"

        self.font_small = pygame.font.SysFont("Arial Black", 12)
        self.font = pygame.font.SysFont("Arial Black", 18)
        self.outline_font = pygame.font.SysFont("Arial Black", 30)
        # self.font = pygame.font.Font(font_path, 20)
        ### Background ###
        self.background_image = pygame.image.load("C:/Projektai/Estate Clicker/gui/background.webp").convert()
        self.background_image = pygame.transform.scale(self.background_image, (screen_width, screen_height))

        ### Board ###
        self.board_image = pygame.image.load("C:/Projektai/Estate Clicker/gui/title_for_board.png")
        board_width, board_height = 280, 70
        self.board_image = pygame.transform.scale(self.board_image, (board_width, board_height))
        self.bl_center_x = 50
        self.bl_center_y = 100
        self.left_board = self.board_image.get_rect(topleft=(self.bl_center_x, self.bl_center_y))
        self.br_center_x = screen_width - board_width - 50
        self.br_center_y = 100
        self.right_board = self.board_image.get_rect(topleft=(self.br_center_x, self.br_center_y))


        ### Arrow ###
        arr_width, arr_height = 50, 30

        r_arr_x = (board_width - arr_width) / 2 + (screen_width - board_width - 50)
        r_arr_up_y = self.br_center_y - 35
        r_arr_down_y = screen_height - r_arr_up_y - 35

        l_arr_x = 50 + (board_width - arr_width) /2
        l_arr_up_y = self.br_center_y - 35
        l_arr_down_y = screen_height - l_arr_up_y - 35


        self.arrow_down_image = pygame.image.load("C:/Projektai/Estate Clicker/gui/arrow_down.png")
        self.arrow_down_image = pygame.transform.scale(self.arrow_down_image, (arr_width, arr_height))
        self.right_arrow_down = self.arrow_down_image.get_rect(topleft=(r_arr_x, r_arr_down_y))
        self.left_arrow_down = self.arrow_down_image.get_rect(topleft=(l_arr_x, l_arr_down_y))

        self.arrow_up_image = pygame.image.load("C:/Projektai/Estate Clicker/gui/arrow_up.png")
        self.arrow_up_image = pygame.transform.scale(self.arrow_up_image, (50, 30))
        self.right_arrow_up = self.arrow_up_image.get_rect(topleft=(r_arr_x, r_arr_up_y))
        self.left_arrow_up = self.arrow_up_image.get_rect(topleft=(l_arr_x, l_arr_up_y))


        ### Starting House ###
        self.starting_house = StartingHouse()

        self.player = Player(self.starting_house)
        self.clock = pygame.time.Clock()
        self.blink = False
        self.hover = False
        self.running = True

        self.money = 0
        self.show_money_sign = False
        self.money_sign_position = (400, 500)
        self.money_sign_start_time = None
        self.money_sign_duration = 2000
        self.money_signs = []

        self.displayed_houses_start_index = 0  # Pirmo rodomo namo indeksas sąraše
        self.max_displayed_houses = 6  # Maksimalus vienu metu rodomų namų skaičius




    def update_money(self, amount):
        # Atnaujinti pinigų kiekį
        self.money += amount


    def draw_money_text(self):
        money_text = f"${self.money}"
        text_surface = self.outline_font.render(money_text, True, (24,74,46,255))

        text_rect = text_surface.get_rect(center=(self.screen.get_rect().centerx, 50))
        self.screen.blit(text_surface, text_rect)

    def draw_window(self, hover, blink):
        self.screen.blit(self.background_image, (0, 0))

        if self.hover:
            highlighted_img = self.starting_house.apply_highlight()
            self.screen.blit(highlighted_img, self.starting_house.position)
        else:
            self.screen.blit(self.starting_house.image, self.starting_house.position)

        if self.blink:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_blink_time < 200:  # Mirksėjimo trukmė 0.5 sekundės
                if (current_time - self.last_blink_time) // 100 % 2 == 0:
                    pass
                else:
                    self.screen.blit(self.starting_house.image, self.starting_house.position)
            else:
                self.blink = False

        right_board_texts_houses = [house.name for house in self.player.houses]

        # Nupieškite eiles lentų kairėje ir užrašykite tekstą
        for i, upgrade in enumerate(self.upgrades):
            y_pos = self.bl_center_y + i * 85
            self.screen.blit(self.board_image, (self.bl_center_x, y_pos))

            # Tikriname, ar žaidėjas turi pakankamai pinigų patobulinimui
            if self.money >= upgrade.base_cost:
                # Žaidėjas turi pakankamai pinigų, rodyti patobulinimo paveikslėlį be pakeitimų
                self.screen.blit(upgrade.image, (self.bl_center_x + 10, y_pos + 5))
            else:
                # Žaidėjas neturi pakankamai pinigų, rodyti patamsintą patobulinimo paveikslėlį
                dimmed_image = upgrade.image.copy()  # Sukuriame paveikslėlio kopiją
                # Taikome permatomumo efektą (alpha) paveikslėliui
                dimmed_image.fill((100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(dimmed_image, (self.bl_center_x + 10, y_pos + 5))

            upgrade_name_text = upgrade.name
            name_text = self.font.render(upgrade_name_text, True, (252, 252, 252))
            self.screen.blit(name_text, (self.bl_center_x + 80, y_pos + 15))

            upgrade_cost_text = f"${upgrade.base_cost}"
            cost_text = self.font_small.render(upgrade_cost_text, True, (24, 74, 46, 255))
            self.screen.blit(cost_text, (self.bl_center_x + 80, y_pos + 35))


        current_time = pygame.time.get_ticks()
        self.money_signs = [sign for sign in self.money_signs if
                            current_time - sign['start_time'] < self.money_sign_duration]
        for sign in self.money_signs:
            money_sign_text = self.font.render("+$1", True, (24,74,46,255))
            self.screen.blit(money_sign_text, sign['position'])




        self.screen.blit(self.arrow_down_image, self.left_arrow_down)
        self.screen.blit(self.arrow_down_image, self.right_arrow_down)
        self.screen.blit(self.arrow_up_image, self.left_arrow_up)
        self.screen.blit(self.arrow_up_image, self.right_arrow_up)



        self.draw_money_text()
        self.draw_houses()

        pygame.display.update()


    def draw_houses(self):
        # Apskaičiuojame, kiek namų galime rodyti, remiantis sąrašo dydžiu ir maksimaliu rodomų namų skaičiumi
        displayed_houses = self.player.houses[self.displayed_houses_start_index:self.displayed_houses_start_index + self.max_displayed_houses]

        for i, house in enumerate(displayed_houses):
            y_pos = self.br_center_y + i * 85
            self.screen.blit(self.board_image, (self.br_center_x, y_pos))
            self.screen.blit(house.mini_image, (self.br_center_x, y_pos - 5))
            # Render white text
            text_surface = self.font.render(house.name, True, (252, 252, 252))
            self.screen.blit(text_surface, (self.br_center_x + 90, y_pos + 20))

    def scroll_houses_up(self):
        # Slenkame namų sąrašą aukštyn, jei įmanoma
        if self.displayed_houses_start_index > 0:
            self.displayed_houses_start_index -= 1

    def scroll_houses_down(self):
        # Slenkame namų sąrašą žemyn, jei įmanoma
        if self.displayed_houses_start_index < len(self.player.houses) - self.max_displayed_houses:
            self.displayed_houses_start_index += 1



    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.starting_house.image.get_rect(topleft=self.starting_house.position).collidepoint(event.pos):
                        # Įjungiame mirksėjimą ir +$1 ženklo rodymą
                        self.update_money(1)
                        self.blink = True
                        self.last_blink_time = pygame.time.get_ticks()
                        new_sign = {
                            'position': (self.starting_house.position[0] + random.randint(40, 240),
                                         self.starting_house.position[1] - random.randint(-100, 200)),
                            'start_time': pygame.time.get_ticks()
                        }
                        self.money_signs.append(new_sign)
                        if event.button == 4:
                            self.scroll_houses_up()
                            # Pelės ratuko slinkimas žemyn
                        elif event.button == 5:
                            self.scroll_houses_down()

                elif event.type == pygame.MOUSEMOTION:
                    self.hover = self.starting_house.image.get_rect(topleft=self.starting_house.position).collidepoint(event.pos)

            self.draw_window(self.hover, self.blink)
            self.clock.tick(FPS)


        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
