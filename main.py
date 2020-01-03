import pygame
import json


class Day:
    def __init__(self, name):
        self.name = name
        self.classes = []
        self.hours_of_classes = 0

    def add_classes(self, class_list):
        for university_class in class_list:
            if self.name in university_class.days:
                self.classes.append(university_class)
        self.hours_of_classes = self.calculate_length()
        self.classes.sort()

    def calculate_length(self):
        total = 0
        for university_class in self.classes:
            total += university_class.get_length()
        return total


class UniversityClass:
    def __init__(self, name, json_data):
        self.name = name
        self.time_strings = json_data["time"]
        self.time = (self.convert_time_string(self.time_strings[0]),
                     self.convert_time_string(self.time_strings[1]))
        self.days = json_data["days"]

    def get_length(self):
        return self.time[1] - self.time[0]

    @staticmethod
    def convert_time_string(string):
        sections = string.split(":")
        minutes = float(sections[1]) * 100 / 60
        return int(sections[0]) + minutes / 100

    def __lt__(self, other):
        return self.time[0] < other.time[0]


class DaySlot:
    width = 220
    height = 600
    font_size = 24

    def __init__(self, day):
        self.day = day
        self.class_slots = []
        for university_class in self.day.classes:
            self.class_slots.append(ClassSlot(university_class))
        self.image = pygame.Surface((self.width, self.height))
        self.draw()

    def draw(self):
        pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 2)
        title_label = create_label(self.day.name, self.font_size)
        self.image.blit(title_label, (calculate_x_for_centering(title_label, self.image), 20))
        y = 60
        separation = 20
        for class_slot in self.class_slots:
            self.image.blit(class_slot.image, (calculate_x_for_centering(class_slot.image, self.image), y))
            y += class_slot.image.get_height() + separation
        total_time_label = create_label(format_hours_from_float(self.day.hours_of_classes), 24)
        self.image.blit(total_time_label, (calculate_x_for_centering(total_time_label, self.image), 550))


class ClassSlot:
    width = 190
    height = 70
    font_size = 18

    def __init__(self, university_class):
        self.university_class = university_class
        self.image = pygame.Surface((self.width, self.height))
        self.draw()

    def draw(self):
        pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 2)
        class_label = create_label(self.university_class.name, self.font_size)
        time_label = create_label(self.format_class_time(), self.font_size)
        self.image.blit(class_label, (calculate_x_for_centering(class_label, self.image), 10))
        self.image.blit(time_label, (calculate_x_for_centering(time_label, self.image), 35))

    def format_class_time(self):
        return self.university_class.time_strings[0] + " - " + self.university_class.time_strings[1]


def create_label(text, font_size):
    font = pygame.font.SysFont("Consolas", font_size)
    return font.render(text, True, (255, 255, 255))


def load_classes(term):
    file = term + ".json"

    classes = []
    with open(file) as json_file:
        json_data = json.load(json_file)
        for class_name, class_info in json_data.items():
            classes.append(UniversityClass(class_name, class_info))
    return classes


def load_days(class_list):
    days = [Day("Monday"), Day("Tuesday"), Day("Wednesday"), Day("Thursday"), Day("Friday")]
    for day in days:
        day.add_classes(class_list)
    return days


def draw_timetable(days, screen):
    total_hours = 0
    separation = 20
    total_width = DaySlot.width * len(days) + separation * len(days)
    x = screen.get_width() / 2 - total_width / 2
    y = 20
    for day in days:
        total_hours += day.hours_of_classes
        day_slot = DaySlot(day)
        screen.blit(day_slot.image, (x, y))
        x += day_slot.image.get_width() + separation
    total_hours_label = create_label(format_hours_from_float(total_hours), 24)
    screen.blit(total_hours_label, (calculate_x_for_centering(total_hours_label, screen), 650))


def calculate_x_for_centering(element_surface, background_surface):
    return background_surface.get_width() / 2 - element_surface.get_width() / 2


def format_hours_from_float(hours_float):
    hours = int(hours_float // 1)
    minutes = (hours_float % 1) / 100 * 60
    minutes = int(minutes * 100)
    minutes_string = str(minutes)
    if minutes == 0:
        minutes_string += "0"
    return str(hours) + ":" + minutes_string + " hours"


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    classes = load_classes("spring")
    days = load_days(classes)
    draw_timetable(days, screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        pygame.display.flip()


if __name__ == "__main__":
    main()
