import pygame
import json

#pylint: disable=too-many-function-args
#pylint: disable=no-member


"""
Loads json data from a given file
Interprents the json data to figure out what classes you have
Figures out how many hours of classes you have per day, and how many for the week
Creates a column for each day, each containing boxes for each class, with class info in each
Displays these columns in a nice easy-to-read format
"""

class Day:
    """ Holds classes for the day and calculates how many hour of classes """

    def __init__(self, name, class_list):
        """ Create an empty day of given name """
        self.name = name
        self.classes = []
        self.class_time_h = 0
        self.class_time_m = 0
        self.add_classes(class_list)

    def add_classes(self, class_list):
        """ Add classes from class_list which happen on this day """
        for university_class in class_list:
            if self.name in university_class.days:
                self.classes.append(university_class)
        self.calculate_length()
        self.classes.sort()

    def calculate_length(self):
        """ Adds the length of all classes that happen on this day """
        for university_class in self.classes:
            self.class_time_h += university_class.length_h
            self.class_time_m += university_class.length_m
            while self.class_time_m >= 60:
                self.class_time_h += 1
                self.class_time_m -= 60


class UniversityClass:
    """ An enrolled class """

    def __init__(self, name, json_data):
        """ Create a class of given name and get class times from json_data """
        self.name = name
        self.time_strings = json_data["time"]
        self.start_time = json_data["time"][0]
        self.end_time = json_data["time"][1]
        self.days = json_data["days"]

        self.start_time_float = self.time_string_to_float(self.start_time)
        self.end_time_float = self.time_string_to_float(self.end_time)
        self.length_h, self.length_m = self.calculate_length()

    def calculate_length(self):
        """ Returns the length in hours, minutes """
        diff = self.end_time_float - self.start_time_float
        string = self.float_to_time_string(diff)
        h, m = string.split(":")
        return int(h), int(m)

    @staticmethod
    def time_string_to_float(string):
        """ Converts a time in the format hh:mm into a float """
        sections = string.split(":")
        minutes = float(sections[1]) * 100 / 60  # Convert from m/60 to f/100
        return int(sections[0]) + minutes / 100

    @staticmethod
    def float_to_time_string(f):
        """ Converts a time as a float into a string in the format hh:mm """
        hours  = str(int(f // 1))  # Just the integer part
        minutes_f = (f % 1) / 100 * 60  # Convert from f/100 to m/60
        minutes = str(round(minutes_f * 100))  # 
        if minutes_f == 0.0:
            minutes += "0"
        elif len(minutes) == 1:
            minutes = "0" + minutes
        return hours + ":" + minutes

    def __lt__(self, other):
        return self.start_time_float < other.start_time_float


class DayColumn:
    width = 220
    height = 600
    title_y = 20
    hour_y = 525
    minute_y = 550
    font_size = 32
    separation = 20
    border_color = (89, 193, 53)
    border_width = 4
    background_color = (51, 57, 65)

    def __init__(self, day):
        """ A graphical box representing a day that holds the class boxes and displays total hours of classes """
        self.day = day
        self.class_slots = []
        for university_class in self.day.classes:
            self.class_slots.append(ClassSlot(university_class))
        self.image = pygame.Surface((self.width, self.height))
        self.create_image()

    def create_image(self):
        """ Create box with title, classes, and total hours/minutes """
        self.draw_box()
        self.draw_classes()
        self.draw_labels()

    def draw_box(self):
        """ Draw the box containing everything """
        self.image.fill(self.background_color)
        pygame.draw.rect(self.image, self.border_color, self.image.get_rect(), self.border_width)
        

    def draw_classes(self):
        """ Draw the classes inside the box """
        y = 60
        for class_slot in self.class_slots:
            self.image.blit(class_slot.image, (center_x(class_slot.image, self.image), y))
            y += class_slot.image.get_height() + self.separation

    def draw_labels(self):
        """ Draw the title label and hours/minutes """
        title_label = create_label(self.day.name, self.font_size)
        self.image.blit(title_label, (center_x(title_label, self.image), self.title_y))

        hour_label = create_label(str(self.day.class_time_h) + " hours", self.font_size)
        minute_label = create_label(str(self.day.class_time_m) + " minutes", self.font_size)
        self.image.blit(hour_label, (center_x(hour_label, self.image), self.hour_y))
        self.image.blit(minute_label, (center_x(minute_label, self.image), self.minute_y))


class ClassSlot:
    width = 190
    height = 70
    font_size = 22
    background_color = (36, 34, 52)
    border_color = (89, 193, 53)
    border_width = 4
    title_y = 14
    time_y = 40

    def __init__(self, university_class):
        """ A graphical box that shows info about a class """
        self.university_class = university_class
        self.image = pygame.Surface((self.width, self.height))
        self.create_image()
    
    def create_image(self):
        """ Create box with title and time """
        self.draw_box()
        self.draw_labels()

    def draw_box(self):
        """ Draw the box containing the info """
        self.image.fill(self.background_color)
        pygame.draw.rect(self.image, self.border_color, self.image.get_rect(), self.border_width)

    def draw_labels(self):
        """ Draw the class name and time labels """
        class_label = create_label(self.university_class.name, self.font_size)
        time_label = create_label(self.format_class_time(), self.font_size)
        self.image.blit(class_label, (center_x(class_label, self.image), self.title_y))
        self.image.blit(time_label, (center_x(time_label, self.image), self.time_y))

    def format_class_time(self):
        """ Put time in format of hh:mm - hh:mm """
        return self.university_class.start_time + " - " + self.university_class.end_time


class TimeTable:
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    day_separation = 20
    total_width = len(week_days) * DayColumn.width + (len(week_days) - 1) * day_separation
    top = 20
    font_size = 32
    hour_y  = 650
    minute_y = 675
    background_color = (36, 34, 52)
    line_color = (255, 255, 255)
    line_edge_offset = 20
    line_center_offset = 100
    line_top = hour_y - 10
    line_y = minute_y

    def __init__(self, file_path):
        """ A graphical display of a week-long timetable created from a json file """
        self.classes = []
        self.days = []
        self.total_h = 0
        self.total_m = 0
        self.load_classes(file_path)
        self.load_days()
        self.calculate_total_time()

    def load_classes(self, file_path):
        """ Create a list of UniversityClass's from the json file """
        with open(file_path) as json_file:
            json_data = json.load(json_file)
            for class_name, class_info in json_data.items():
                self.classes.append(UniversityClass(class_name, class_info))

    def load_days(self):
        """ Create and fill Day's from list of week days """
        for name in self.week_days:
            self.days.append(Day(name, self.classes))

    def calculate_total_time(self):
        """ Calculate how many hours of classes for the week """
        for day in self.days:
            self.total_h += day.class_time_h
            self.total_m += day.class_time_m
        while self.total_m >= 60:
            self.total_h += 1
            self.total_m -= 60

    def draw(self, screen):
        """ Draw the timetable to the screen """
        self.fill_background(screen)
        self.draw_days(screen)
        self.draw_labels(screen)
        self.draw_lines(screen)

    def fill_background(self, screen):
        """ Fill the background of the screen with background_color """
        screen.fill(self.background_color)

    def draw_days(self, screen):
        """ Draw all the day columns """
        x = int(screen.get_width() / 2 - self.total_width / 2)
        y = self.top
        for day in self.days:
            day_column = DayColumn(day)
            screen.blit(day_column.image, (x, y))
            x += DayColumn.width + self.day_separation

    def draw_labels(self, screen):
        """ Draw the hour and minute labels """
        hour_label = create_label(str(self.total_h) + " hours", self.font_size)
        minute_label = create_label(str(self.total_m) + " minutes", self.font_size)
        screen.blit(hour_label, (center_x(hour_label, screen), self.hour_y))
        screen.blit(minute_label, (center_x(minute_label, screen), self.minute_y))

    def draw_lines(self, screen):
        """ Draw the encapsulating lines """
        line_offset = int(self.total_width / 2 - self.line_edge_offset)
        left_x = int(screen.get_width() / 2 - line_offset)
        right_x = int(screen.get_width() / 2 + line_offset)
        inner_left_x = int(screen.get_width() / 2 - self.line_center_offset)
        inner_right_x = int(screen.get_width() / 2 + self.line_center_offset)
        left_points = [(left_x, self.line_top), (left_x, self.line_y), (inner_left_x, self.minute_y)]
        right_points = [(right_x, self.line_top), (right_x, self.line_y), (inner_right_x, self.line_y)]

        pygame.draw.lines(screen, self.line_color, False, left_points, 2)
        pygame.draw.lines(screen, self.line_color, False, right_points, 2)


def create_label(text, font_size, color=(255, 255, 255)):
    """ Render text of given size """
    font = pygame.font.SysFont("Consolas", font_size)
    return font.render(text, True, color)
    

def center_x(element_surface, background_surface):
    """ Determine the x position of the element so it is centered """
    return int(background_surface.get_width() / 2 - element_surface.get_width() / 2)


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Timetable")
    timetable = TimeTable("fall.json")
    timetable.draw(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        pygame.display.flip()


if __name__ == "__main__":
    main()
