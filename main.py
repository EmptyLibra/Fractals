# Программа рисует аттрактор (фрактал) методом хаоса в многоугольнике с заданным количеством вершин,
# начиная с заданной начальной точки.
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, RiseInTransition, CardTransition, \
    SlideTransition
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
import math
import random

from kivymd.uix.screen import MDScreen

Builder.load_string("""
<MainMenu>:
    FitImage:
        source: 'MenuImage.jpg'
    MDBoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 10
        
        MDLabel:
            size_hint: 1, 0.2
            valign: 'top'
            halign: 'center'
            text: 'Ф р а к т а л ы'
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: 'H3'
            italic: True
        
        Widget:
            size_hint: 1, 0.25
        
        MDRaisedButton:
            pos_hint:{"center_x": 0.5, "center_y": 0.5}
            size_hint: 0.2, 0.1
            text: "Начать"
            text_color: 1, 1, 1, 1
            md_bg_color: .43, .43, .43, 0.7
            on_release: 
                root.manager.transition.direction = 'up'
                root.manager.current = 'fractals'
        
        MDRaisedButton:
            pos_hint:{"center_x": 0.5, "center_y": 0.5}
            size_hint: 0.2, 0.1
            text: "Выход"
            text_color: 1, 1, 1, 1
            md_bg_color: .43, .43, .43, 0.7
            on_release: exit()
        Widget:
            size_hint: 1, 0.25

<SelectionFractalsMenu>:
    FitImage:
        source: 'Menu2.jpg'
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 30
        
        MDRaisedButton:
            pos_hint:{"center_x": 0.5, "center_y": 0.5}
            size_hint: 0.5, 0.1
            text: "Метод хаоса"
            text_color: 0, 0, 0, 1
            md_bg_color: .95, .87, .60, 0.7
            on_release: 
                root.manager.transition.direction = 'right'
                root.manager.current = 'chaos'
        
        MDRaisedButton:
            pos_hint:{"center_x": 0.5, "center_y": 0.5}
            size_hint: 0.5, 0.1
            text: "Формула Таппера"
            text_color: 0, 0, 0, 1
            md_bg_color: .95, .87, .60, 0.7
        
        MDRaisedButton:
            pos_hint:{"center_x": 0.5, "center_y": 0.5}
            size_hint: 0.5, 0.1
            text: "Coming soon..."
            text_color: 0, 0, 0, 1
            md_bg_color: .95, .87, .60, 0.7
        
        MDRaisedButton:
            pos_hint:{"center_x": 0.5, "center_y": 0.5}
            size_hint: 0.5, 0.1
            text: "В главное меню"
            text_color: 0, 0, 0, 1
            md_bg_color: .95, .87, .60, 0.7
            on_release: 
                root.manager.transition.direction = 'down'
                root.manager.current = 'menu'
    
""")

labelText = '''Вас приветствует программа по рисованию фракталов или, как высказывался М.Барнсли - игра в хаос!
    Возьмём треугольник, выберем внутри или снаружи этого треугольника произвольным образом начальную точку.
    Бросим теперь игральную кость, представляющую собой кубик, на 6 гранях которого проставлены буквы А, В и С. 
    Пусть каждая буква присутствует на двух из них, тогда вероятность выпадания любой буквы одинакова и равна 1/3.
    Поставим нувоую точку ровно по средине между нашей точкой и выбранной вершиной. Теперь эта точка будет начальной.
    Повторим процесс много раз. Спрашивается, как распределятся внутри треугольника эти точки после достаточно большого числа шагов? 
    Нажмите на кнопку и узнате.
    '''
spiransTriangle = '''По мере увеличения числа точек все явственнее проступает структура треугольника Серпинского.
Полученная фигура является фракталом - самоподобное множество (объект, в точности или приближённо совпадающий с частью себя самого, то есть целое имеет ту же форму, что и одна или более частей)
или, как называют это в теории хаоса - Аттрактор.
Видно, что, хотя каждый раз выбор вершины треугольника происходит чисто случайным образом, возникающее множество точек на плоскости отнюдь не случайно и обладает ярко выраженной фрактальной структурой. 
По сути, т.к. мы двигаемся на половину расстояния до вершины, то все эти треугольники представляют собой геометрическое место точек, которые находятся на половине расстояния до соответствующих вершин от точек большого центрального треугольника.
Попробуйте теперь с другой фигурой (другим количеством вершин) или другим количеством итераций. Интересно, что если поставить точку в другом месте, итоговый рисунок не поментяеся.
'''

class MainMenu(MDScreen):
    pass

class SelectionFractalsMenu(MDScreen):
    pass

class ChaosMethod(MDScreen):
    def __init__(self, *args, **kwargs):
        MDScreen.__init__(self, *args, **kwargs)
        self.box_widget.idLabel.text = labelText

    # Рисует начальную точку, вершины многоугольника и сам аттрактор методом хаоса
    def start_drawing(self):
        # Берём координаты точки, количество углов и количесвто итераций из слайдеров
        point = (self.box_widget.slider_x.value, self.box_widget.slider_y.value)
        countAngels = self.box_widget.slider_a.value
        iterations = self.box_widget.slider_c.value

        # Очищает поле для рисование (если вдруг там было что-то нарисовано)
        self.float_widget.canvas.after.clear()

        # Координаты центра многогранника и радиус описанной окружности
        # высчитываются исходя из текущих размеров окна
        x, y = list(), list()
        xC, yC = self.float_widget.width//2, self.float_widget.height // 2
        R = min(self.float_widget.width, self.float_widget.height) // 2

        # Рассчитываем координаты вершин многогранника
        for i in range(countAngels):
            x.append(xC + R * math.cos(math.pi/2 + (2*math.pi*i) / countAngels))
            y.append(yC + R * math.sin(math.pi/2 + (2 * math.pi*i) / countAngels))
        with self.float_widget.canvas.after:
            # Рисуем исходную точку
            Color(0, 1, 0, 1, mode='rgba')
            Rectangle(pos=point, size=(4, 4))

            # Рисуем все вершины многогранника
            Color(1, 0, 0, 1, mode='rgba')
            for i in range(countAngels):
                Rectangle(pos=(x[i], y[i]), size=(5, 5))
            Color(1, 1, 1, 1, mode='rgba')

        # На какую часть длины до вершины двигаться и
        # множитель для многоугольников с количеством вершин больше 3
        part_of_segment, multiplier = (2, 1) if countAngels == 3 else (3, 2)

        # Рисуем все оставшиеся точки
        cur_x, cur_y = point[0], point[1]
        angels = list(range(countAngels))
        for i in range(iterations):
            p = random.choice(angels)
            cur_x = (cur_x + x[p]) / part_of_segment
            cur_y = (cur_y + y[p]) / part_of_segment
            with self.float_widget.canvas.after:
                Rectangle(pos=(cur_x*multiplier, cur_y*multiplier), size=(2, 2))

        # Выводить текст о треугольнике Серпинского
        if countAngels == 3:
            self.box_widget.idLabel.text = spiransTriangle
        else:
            self.box_widget.idLabel.text = labelText

class DrawingWindowApp(MDApp):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MainMenu(name='menu'))
        sm.add_widget(SelectionFractalsMenu(name='fractals'))
        sm.add_widget(ChaosMethod(name='chaos'))
        return sm


DrawingWindowApp().run()
