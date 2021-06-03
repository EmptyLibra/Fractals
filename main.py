# Программа реализует GUI для двух методов рисования фракталов. Первый - это метод хаоса, а второй - папоротник Барнсли

from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivy.graphics.vertex_instructions import Point
from kivy.graphics.context_instructions import Color
from kivy.lang import Builder
import random
import numpy as np
import math
from kivy.graphics.transformation import Matrix

class MainMenu(MDScreen):
    pass

class SelectionFractalsMenu(MDScreen):
    pass

# Класс реализующий всё поведение для метода Хаоса
class ChaosMethod(MDScreen):
    def __init__(self, **kwargs):
        self.labelText = '''        Вас приветствует программа по рисованию фракталов методом хаоса или, как \
высказывался М.Барнсли - игра в хаос! Возьмём треугольник, выберем внутри или снаружи этого треугольника произвольным \
образом начальную точку. Бросим теперь игральную кость, представляющую собой кубик, на 6 гранях которого проставлены \
буквы А, В и С. Пусть каждая буква присутствует на двух из них, тогда вероятность выпадения любой буквы одинакова и \
равна 1/3. Поставим нувую точку ровно по средине между нашей точкой и выбранной вершиной. Теперь эта точка будет \
начальной. Повторим процесс много раз.
        По мере увеличения числа точек все явственнее будет проступать структура треугольника Серпинского. Полученная \
фигура будет является фракталом - самоподобное множество (объект, в точности или приближённо совпадающий с частью себя \
самого, то есть целое имеет ту же форму, что и одна или более частей) или, как называют это в теории хаоса - Аттрактор.
        Хотя каждый раз выбор вершины треугольника будет происходить чисто случайным образом, возникающее \
множество точек на плоскости отнюдь не случайно и будет обладать ярко выраженной фрактальной структурой. По сути, т.к. \
мы двигаемся на половину расстояния до вершины, то все эти треугольники представляют собой геометрическое место точек, \
которые находятся на половине расстояния до соответствующих вершин от точек большого центрального треугольника. \
Перейдите теперь в раздел настроек и протестируйте программу сами.
        Причём при другом количестве углов будет получаться иная картина, но даже, если переместить начальную точку в \
любое другое место, исходная картинка не поменяется.'''
        super().__init__(**kwargs)

    # Рисует начальную точку, вершины многоугольника и сам аттрактор методом хаоса
    def start_drawing(self, *kw):
        # Очищает поле для рисование (если вдруг там было что-то нарисовано)
        self.ids.floatL.canvas.after.clear()

        # Координаты центра многогранника и радиус описанной окружности
        # высчитываются исходя из текущих размеров окна
        x, y = list(), list()
        xC, yC = self.ids.floatL.width // 2, self.ids.floatL.height // 2
        R = min(self.ids.floatL.width, self.ids.floatL.height) // 2

        # Рассчитываем координаты вершин многогранника, количество углов берём из слайдера
        countAngels = self.ids.slider_a.value
        for i in range(countAngels):
            x.append(xC + R * math.cos(math.pi / 2 + (2 * math.pi * i) / countAngels))
            y.append(yC + R * math.sin(math.pi / 2 + (2 * math.pi * i) / countAngels))

        # Рисуем исходную точку и все вершины многогранника, координаты точки из слайдера
        point = [self.ids.slider_x.value, self.ids.slider_y.value]
        with self.ids.floatL.canvas.after:
            Color(0, 1, 0, mode='rgb')
            Point(points=point, pointsize=2)

            Color(1, 1, 1, mode='rgb')
            for i in range(countAngels):
                Point(points=[x[i], y[i]], pointsize=3)

        # На какую часть длины до вершины двигаться и
        # множитель для многоугольников с количеством вершин больше 3
        part_of_segment, multiplier = (2, 1) if countAngels == 3 else (3, 2)

        # Рисуем все оставшиеся точки, количество итераций из слайдера
        cur_x, cur_y = point[0], point[1]
        angels = list(range(countAngels))
        iterations = self.ids.slider_count.value
        for i in range(iterations):
            p = random.choice(angels)
            cur_x = (cur_x + x[p]) / part_of_segment
            cur_y = (cur_y + y[p]) / part_of_segment
            with self.ids.floatL.canvas.after:
                Point(points=[cur_x * multiplier, cur_y * multiplier], pointsize=1)

# Класс для особого поведения текстовых полей
class MyMDTextField(MDTextField):
    max_characters = NumericProperty(6)
    characters = ListProperty(['.', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
    greater_one = ListProperty(['2', '3', '4', '5', '6', '7', '8', '9'])

    def on_focus(self, *args):
        try:
            if abs(float(self.text)) >= 2:
                self.text = self.helper_text
        except ValueError:
            pass
        if self.text == '':
            self.text = self.helper_text
        super().on_focus(self, *args)

    def insert_text(self, substring, from_undo=False):
        # Ограничение максимум на 6 символов, и на сами символы
        if len(self.text) >= self.max_characters > 0 or substring not in self.characters:
            substring = ""
        # Ограничение на количество точек и минусов в тексте
        elif (substring == '.' and '.' in self.text) or (substring == '-' and '-' in self.text):
            substring = ""
        if self.text == '' and substring in self.greater_one:
            substring = ""
        if self.text != '':
            try:
                if abs(float(self.text[:self.cursor[0]] + substring + self.text[self.cursor[0]:])) >= 2:
                    substring = ""
            except ValueError:
                substring = ""
        MDTextField.insert_text(self, substring, from_undo)

# Класс реализующий всё поведение для папоротника Барнсли
class BarnsleyFern(MDScreen):
    def __init__(self, **kwargs):
        # Текст для Label в разделе теории, список с объектами текстовых полей, содержащих коэффициенты,
        # номер текущего загружаемого папортника
        self.labelText = '''        Папоротник Барнсли - фрактал, названный в честь Майкла Барнсли, \
британского математика, который первым описал его в своей книге "Фракталы Повсюду". Является одним из основных \
примеров "самоподобных" множеств, т.е. представляет собой математически генерируемый "шаблон", воспроизводимый при \
любом увеличении или уменьшении количества итераций. 
        Папоротник Барнсли строится при помощи 4-х аффинных преобразований, подобных тому, что представлено на рисунке \
1. По сути, берутся начальные координаты x, y = (0,0), и затем с определённой вероятностью выбирается одно из этих \
преобразований. С его помощью получаются координаты новой точки и процесс повторяется. Из-за особенностей \
преобразования, чтобы картинка была целой понадобится несколько десятков тысяч операций!
        Барнсли, в частности, придумал свои 4 преобразования, которые для удобства записал в виде матрицы, в последнем \
столбце которой указал вероятности, с которыми надо выбирать именно это преобразование.
        Так, коэффициенты в первой строчки матрицы отвечает за отрисовку стебля папоротника, во второй за маленькие \
листочки, а в третьей и четвёртой за большие листья слева и справа от стебля. Изменяя эти коэффициенты и вероятности, \
с которыми выбирается то или иное преобразование, можно получать совершенно различные рисунки. Главное, чтобы не все \
коэффициенты были нулевыми, а сумма вероятностей (последний столбец матрицы с коэффициентами) равнялась единице.
        Поэкспериментируйте с коэффициентами самостоятельно или загрузите один из предложенных вариантов, нажав на \
кнопку \'Выбор папоротника\'.
'''
        self.text_fields = list()
        self.fern_num = 1
        super().__init__(**kwargs)
        self.functions = [self.f1, self.f2, self.f3, self.f4]
        # Добавление лэйблов и текстовых полей, образующих матрицы с коэффициентами
        my_widgets = {'TF1': 0, 'TF2': 0, 'TF3': 0, 'TF4': 0.16, 'TF5': 0, 'TF6': 0, 'TF7': 0.01, 'L11': 'Стебель',
                      'TF8': 0.85, 'TF9': 0.04, 'TF10': -0.04, 'TF11': 0.85, 'TF12': 0, 'TF13': 1.6,
                      'TF14': 0.85, 'L13': 'Маленькие листочки',
                      'TF15': 0.2, 'TF16': -0.26, 'TF17': 0.23, 'TF18': 0.22, 'TF19': 0, 'TF20': 1.6,
                      'TF21': 0.07,
                      'L15': 'Большие листочки слева',
                      'TF22': -0.15, 'TF23': 0.28, 'TF24': 0.26, 'TF25': 0.24, 'TF26': 0, 'TF27': 0.44,
                      'TF28': 0.07, 'L17': 'Большие листочки справа'}
        for key in my_widgets:
            if key[0] == 'L':
                Lb = MDLabel(text=my_widgets[key], font_style='Caption', text_size=self.size, size_hint=(1.0, 1.0),
                             halign="left", valign="bottom", theme_text_color="Custom", text_color=(1, 1, 1, 1),)
                Lb.padding_y = 15
                Lb.bind(size=Lb.setter('text_size'))
                self.ids.settings_layout.add_widget(Lb)
            else:
                TF = MyMDTextField(text=str(my_widgets[key]), helper_text_mode="on_focus")
                TF.helper_text = str(my_widgets[key])
                TF.id = key
                self.ids[key] = TF
                self.ids.settings_layout.add_widget(TF)
                self.text_fields.append(TF)

    # Функции, выпалняющие аффинные преобразования
    def f1(self, x, y):
        return self.coef[0] * x + self.coef[1] * y + self.coef[4], \
               self.coef[2] * x + self.coef[3] * y + self.coef[5]

    def f2(self, x, y):
        return self.coef[7] * x + self.coef[8] * y + self.coef[11], \
               self.coef[9] * x + self.coef[10] * y + self.coef[12]

    def f3(self, x, y):
        return self.coef[14] * x + self.coef[15] * y + self.coef[18], \
               self.coef[16] * x + self.coef[17] * y + self.coef[19]

    def f4(self, x, y):
        return self.coef[21] * x + self.coef[22] * y + self.coef[25], \
               self.coef[23] * x + self.coef[24] * y + self.coef[26]

    # Преобразет список координат вида [x1, y1, x2, y2...] под размеры окна
    def convert(self, xy_list):
        old_max_x, old_min_x = max(xy_list[::2]), min(xy_list[::2])
        old_max_y, old_min_y = max(xy_list[1::2]), min(xy_list[1::2])
        old_range = old_max_x - old_min_x, old_max_y - old_min_y
        newRange = self.ids.draw_SL.width, self.ids.draw_SL.height
        if old_range[0] == 0 or old_range[1] == 0:
            self.dialog = MDDialog(text="При расчёте коэффициентов произошла ошибка! Слишком много нулей "
                                        "в таблице данных!", size_hint=(0.4, 0.3),
                                   buttons=[MDFlatButton(text='OK', on_release=self.dialog_close)])
            self.dialog.open()
            return list()
        for i, v in enumerate(xy_list):
            if i % 2 == 0:
                xy_list[i] = ((v - old_min_x) * newRange[0]) / old_range[0]
            else:
                xy_list[i] = ((v - old_min_y) * newRange[1]) / old_range[1]
        return xy_list

    # Генерирует координаты по заданным вероятностям и коэффициентам и конвертирует их под размеры окна
    def generate_convert_xy(self, points):
        xy_list = list()
        x, y = 0, 0
        probabilities = [float(self.ids.TF7.text), float(self.ids.TF14.text), float(self.ids.TF21.text),
                         float(self.ids.TF28.text)]
        for i in range(points):
            function = np.random.choice(self.functions, p=probabilities)
            x, y = function(x, y)
            xy_list.append(x)
            xy_list.append(y)
        return self.convert(xy_list)

    # Функция, рисующая папоротник
    def drawing_fern(self, *kw):
        points = self.ids.slider_p.value
        self.coef = [float(TF.text) for TF in self.text_fields]

        # Генерируем координаты точек и преобразовываем их под размеры окна
        xy_list = self.generate_convert_xy(points)
        self.ids.draw_SL.content.canvas.after.clear()
        with self.ids.draw_SL.content.canvas.after:
            Color(0, 1, 0, mode='rgb')
            # Класс Point позволяет рисовать только по 32766 точки
            for i in range(len(xy_list) // 32766):
                Point(points=xy_list[32766 * i: 32766 * (i + 1)], pointsize=1)
            Point(points=xy_list[32766 * (len(xy_list) // 32766):], pointsize=1)

    def dialog_close(self, *args):
        self.dialog.dismiss(force=True)

    # Проверка значений и запуск рисования папоротника
    def check_values_and_draw(self):
        if float(self.ids.TF7.text) + float(self.ids.TF14.text) + float(self.ids.TF21.text) + \
                float(self.ids.TF28.text) != 1:
            self.dialog = MDDialog(text="Сумма вероятностей (в столбике \'p\') должна равняться 1.00",
                                   size_hint=(0.4, 0.3),
                                   buttons=[MDFlatButton(text='OK', on_release=self.dialog_close)])
            self.dialog.open()
        elif sum([float(TF.text) for TF in self.text_fields if int(TF.id[2:]) % 7 != 0]) == 0:
            self.dialog = MDDialog(text="Все строки данных не мог быть равны нулю!",
                                   size_hint=(0.4, 0.3),
                                   buttons=[MDFlatButton(text='OK', on_release=self.dialog_close)])
            self.dialog.open()
        else:
            # Переключаемся на экран с холстом, возвращаем ScatterLayout
            # в изначальное положение и рисуем новую картинку (рисуем с помощью Clock, чтобы Scatter успел прогрузиться)
            self.ids.bottom_nav_barnsley.switch_tab('screen 3')
            trans = Matrix().scale(1, 1, 1)
            self.ids['draw_SL'].transform = trans
            Clock.schedule_once(self.drawing_fern)

    # Выбор другого папортника
    def fern_selection(self, button):
        ferns = [
            ['Папоротник Барнсли',
                [  0,    0,     0,    0.16, 0, 0,    0.01,
                   0.85, 0.04, -0.04, 0.85, 0, 1.6,  0.85,
                   0.2, -0.26,  0.23, 0.22, 0, 1.6,  0.07,
                  -0.15, 0.28,  0.26, 0.24, 0, 0.44, 0.07]],
            ['Папоротник Cyclosorus',
                 [ 0,      0,      0,     0.25,  0,    -0.4,  0.02,
                   0.95,   0.005, -0.005, 0.93, -0.002, 0.5,  0.84,
                   0.035, -0.2,    0.16,  0.04, -0.09,  0.02, 0.07,
                  -0.04,   0.2,    0.16,  0.04,  0.083, 0.12, 0.07]],
            ['Модиф. Барнсли',
                 [ 0,      0,      0,     0.2,   0, -0.12, 0.01,
                   0.845, 0.035, -0.035, 0.82,  0,  1.6,  0.85,
                   0.2,   -0.31,   0.255, 0.245, 0,  0.29, 0.07,
                  -0.15,   0.24,   0.25,  0.2,   0,  0.68, 0.07]],
            ['Папоротник Culcita',
                 [ 0,     0,     0,    0.25, 0, -0.14, 0.02,
                   0.85,  0.02, -0.02, 0.83, 0,  1,    0.84,
                   0.09, -0.28,  0.3,  0.11, 0,  0.6,  0.07,
                  -0.09,  0.28,  0.3,  0.09, 0,  0.7,  0.07]],
            ['Рыбья кость',
                 [ 0,      0,      0,     0.25,  0,    -0.4,   0.02,
                   0.95,   0.002, -0.002, 0.93, -0.002, 0.5,   0.84,
                   0.035, -0.11,   0.27,  0.01, -0.05,  0.005, 0.07,
                  -0.04,   0.11,   0.27,  0.01,  0.047, 0.06,  0.07]],
            ['Фрактальное дерево',
                 [0,     0,     0,    0.5,  0, 0,   0.05,
                  0.42, -0.42,  0.42, 0.42, 0, 0.2, 0.4,
                  0.42,  0.42, -0.42, 0.42, 0, 0.2, 0.4,
                  0.1,   0,     0,    0.1,  0, 0.2, 0.15]]
        ]
        button.text = ferns[self.fern_num][0]
        for i, TF in enumerate(self.text_fields):
            TF.text = str(ferns[self.fern_num][1][i])
        # Перейти к следующему папоротнику
        self.fern_num = (self.fern_num + 1) % 8 if self.fern_num != 5 else 0

# Загружаем kv файлы и создаём окна программы
class DrawingWindowApp(MDApp):
    '''def set_background(self, *args):
        self.root_window.bind(size=self.do_resize)
        with self.root_window.canvas.before:
            self.bg = Rectangle(source='background.jpg', pos=(0, 0), size=(self.root_window.size))

    def do_resize(self, *args):
        self.bg.size = self.root_window.size'''

    def build(self):
        Builder.load_file('MainMenu.kv')
        Builder.load_file('SelectionFractalsMenu.kv')
        Builder.load_file('ChaosMethod.kv')
        Builder.load_file('BarnsleyFern.kv')

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MainMenu(name='menu'))
        sm.add_widget(SelectionFractalsMenu(name='fractals'))
        sm.add_widget(ChaosMethod(name='chaos'))
        sm.add_widget(BarnsleyFern(name='fern'))
        #Clock.schedule_once(self.set_background, 0)
        return sm


if __name__ == '__main__':
    DrawingWindowApp().run()
