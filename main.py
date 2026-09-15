import json
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle


Window.size = (420, 780)


class ScheduleApp(App):

    # Цвета приложения
    BG_COLOR = (1.0, 0.92, 0.96, 1)
    PINK = (1.0, 0.35, 0.60, 1)
    DARK_PINK = (0.85, 0.18, 0.42, 1)
    LIGHT_PINK = (1.0, 0.75, 0.85, 1)
    WHITE = (1, 1, 1, 1)
    TEXT_COLOR = (0.25, 0.10, 0.17, 1)
    GRAY = (0.45, 0.35, 0.40, 1)

    def build(self):
        self.title = "Моё расписание"

        # Дни недели
        self.days = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье"
        ]

        # Сокращения дней
        self.day_short = {
            "Понедельник": "ПН",
            "Вторник": "ВТ",
            "Среда": "СР",
            "Четверг": "ЧТ",
            "Пятница": "ПТ",
            "Суббота": "СБ",
            "Воскресенье": "ВС"
        }

        # Текущий день
        self.current_day = "Понедельник"

        # Кнопки дней
        self.day_buttons = {}

        # Шрифт Arial
        windows_font = os.path.join(
            os.environ.get("WINDIR", r"C:\Windows"),
            "Fonts",
            "arial.ttf"
        )

        if os.path.exists(windows_font):
            self.font_name = windows_font
        else:
            self.font_name = "Roboto"

        # Файл расписания
        self.data_file = os.path.join(
            self.user_data_dir,
            "schedule.json"
        )

        # Загружаем расписание
        self.schedule = self.load_schedule()

        # Главное окно
        main = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        # Фон
        with main.canvas.before:
            Color(*self.BG_COLOR)

            self.main_background = RoundedRectangle(
                pos=main.pos,
                size=main.size,
                radius=[dp(15)]
            )

        main.bind(
            pos=self.update_main_background,
            size=self.update_main_background
        )

        # Заголовок
        title = Label(
            text="Моё расписание",
            font_name=self.font_name,
            font_size=dp(29),
            bold=True,
            color=self.DARK_PINK,
            size_hint_y=None,
            height=dp(55)
        )

        main.add_widget(title)

        # Дни недели
        days_scroll = ScrollView(
            size_hint_y=None,
            height=dp(55),
            do_scroll_y=False,
            bar_width=0
        )

        self.days_layout = BoxLayout(
            orientation="horizontal",
            spacing=dp(6),
            size_hint_x=None
        )

        self.days_layout.bind(
            minimum_width=self.days_layout.setter("width")
        )

        for day in self.days:

            button = Button(
                text=self.day_short[day],
                font_name=self.font_name,
                font_size=dp(16),
                bold=True,
                size_hint_x=None,
                width=dp(50),
                background_normal="",
                background_color=self.LIGHT_PINK,
                color=self.DARK_PINK
            )

            button.bind(
                on_press=lambda btn, d=day:
                self.change_day(d)
            )

            self.day_buttons[day] = button

            self.days_layout.add_widget(button)

        days_scroll.add_widget(self.days_layout)

        main.add_widget(days_scroll)

        # Название текущего дня
        self.day_label = Label(
            text=self.current_day,
            font_name=self.font_name,
            font_size=dp(23),
            bold=True,
            color=self.TEXT_COLOR,
            size_hint_y=None,
            height=dp(45)
        )

        main.add_widget(self.day_label)

        # Список уроков
        self.scroll = ScrollView(
            bar_width=dp(5)
        )

        self.lessons_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=(0, dp(3))
        )

        self.lessons_layout.bind(
            minimum_height=self.lessons_layout.setter(
                "height"
            )
        )

        self.scroll.add_widget(
            self.lessons_layout
        )

        main.add_widget(self.scroll)

        # Кнопка добавления
        add_button = Button(
            text="+  Добавить урок",
            font_name=self.font_name,
            font_size=dp(19),
            bold=True,
            size_hint_y=None,
            height=dp(58),
            background_normal="",
            background_color=self.PINK,
            color=self.WHITE
        )

        add_button.bind(
            on_press=self.open_add_lesson
        )

        main.add_widget(add_button)

        self.update_day_buttons()
        self.update_lessons()

        return main

    # =================================================
    # ФОН
    # =================================================

    def update_main_background(self, instance, value):
        self.main_background.pos = instance.pos
        self.main_background.size = instance.size

    # =================================================
    # ЗАГРУЗКА
    # =================================================

    def load_schedule(self):

        if os.path.exists(self.data_file):

            try:

                with open(
                    self.data_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(file)

                # Добавляем новые дни,
                # если их ещё нет в старом файле
                for day in self.days:

                    if day not in data:
                        data[day] = []

                # Добавляем время окончания
                # старым урокам
                for day in data:

                    for lesson in data[day]:

                        if "end_time" not in lesson:
                            lesson["end_time"] = ""

                return data

            except Exception:
                pass

        return {
            day: []
            for day in self.days
        }

    # =================================================
    # СОХРАНЕНИЕ
    # =================================================

    def save_schedule(self):

        try:

            os.makedirs(
                os.path.dirname(self.data_file),
                exist_ok=True
            )

            with open(
                self.data_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.schedule,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

        except Exception as error:

            print(
                "Ошибка сохранения:",
                error
            )

    # =================================================
    # СОХРАНЕНИЕ ПРИ ЗАКРЫТИИ
    # =================================================

    def on_stop(self):
        self.save_schedule()

    # =================================================
    # СМЕНА ДНЯ
    # =================================================

    def change_day(self, day):

        self.current_day = day

        self.day_label.text = day

        self.update_day_buttons()

        self.update_lessons()

    # =================================================
    # ПОДСВЕТКА ДНЯ
    # =================================================

    def update_day_buttons(self):

        for day, button in self.day_buttons.items():

            if day == self.current_day:

                button.background_color = self.PINK
                button.color = self.WHITE

            else:

                button.background_color = self.LIGHT_PINK
                button.color = self.DARK_PINK

    # =================================================
    # ОТОБРАЖЕНИЕ УРОКОВ
    # =================================================

    def update_lessons(self):

        self.lessons_layout.clear_widgets()

        lessons = self.schedule.get(
            self.current_day,
            []
        )

        # Сортируем по времени начала
        lessons = sorted(
            lessons,
            key=lambda x: x.get("time", "")
        )

        # Если уроков нет
        if not lessons:

            empty_label = Label(
                text="На этот день уроков нет",
                font_name=self.font_name,
                font_size=dp(18),
                color=self.GRAY,
                size_hint_y=None,
                height=dp(80)
            )

            self.lessons_layout.add_widget(
                empty_label
            )

            return

        # Создаём карточки
        for index, lesson in enumerate(lessons, start=1):

            lesson_box = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(115),
                spacing=dp(6),
                padding=(
                    dp(12),
                    dp(8)
                )
            )

            # Белый фон карточки
            with lesson_box.canvas.before:

                Color(
                    1,
                    1,
                    1,
                    1
                )

                background = RoundedRectangle(
                    pos=lesson_box.pos,
                    size=lesson_box.size,
                    radius=[dp(14)]
                )

            lesson_box.bind(
                pos=lambda instance, value,
                bg=background:
                self.update_card_background(
                    instance,
                    bg
                ),

                size=lambda instance, value,
                bg=background:
                self.update_card_background(
                    instance,
                    bg
                )
            )

            # Время
            start_time = lesson.get(
                "time",
                ""
            )

            end_time = lesson.get(
                "end_time",
                ""
            )

            if end_time:

                time_text = (
                    f"{start_time} - "
                    f"{end_time}"
                )

            else:

                time_text = start_time

            # Информация
            information = (
                f"{index}.  "
                f"{time_text}\n"
                f"{lesson.get('subject', '')}\n"
                f"Учитель: "
                f"{lesson.get('teacher', '—')}\n"
                f"Кабинет: "
                f"{lesson.get('room', '—')}"
            )

            label = Label(
                text=information,
                font_name=self.font_name,
                font_size=dp(14),
                color=self.TEXT_COLOR,
                halign="left",
                valign="middle"
            )

            label.bind(
                size=lambda instance, value:
                setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            lesson_box.add_widget(
                label
            )

            # Кнопка изменения
            edit_button = Button(
                text="Изм.",
                font_name=self.font_name,
                font_size=dp(13),
                bold=True,
                size_hint_x=None,
                width=dp(52),
                background_normal="",
                background_color=self.LIGHT_PINK,
                color=self.DARK_PINK
            )

            edit_button.bind(
                on_press=lambda btn,
                l=lesson:
                self.open_edit_lesson(l)
            )

            lesson_box.add_widget(
                edit_button
            )

            # Кнопка удаления
            delete_button = Button(
                text="Удал.",
                font_name=self.font_name,
                font_size=dp(12),
                bold=True,
                size_hint_x=None,
                width=dp(52),
                background_normal="",
                background_color=(
                    1,
                    0.55,
                    0.68,
                    1
                ),
                color=self.WHITE
            )

            delete_button.bind(
                on_press=lambda btn,
                l=lesson:
                self.confirm_delete(l)
            )

            lesson_box.add_widget(
                delete_button
            )

            self.lessons_layout.add_widget(
                lesson_box
            )

    # =================================================
    # ФОН КАРТОЧКИ
    # =================================================

    def update_card_background(
        self,
        instance,
        background
    ):

        background.pos = instance.pos
        background.size = instance.size

    # =================================================
    # ДОБАВЛЕНИЕ
    # =================================================

    def open_add_lesson(self, instance):

        self.open_lesson_popup(
            title="Добавить урок",
            lesson=None
        )

    # =================================================
    # РЕДАКТИРОВАНИЕ
    # =================================================

    def open_edit_lesson(self, lesson):

        self.open_lesson_popup(
            title="Редактировать урок",
            lesson=lesson
        )

    # =================================================
    # ОКНО ДОБАВЛЕНИЯ / РЕДАКТИРОВАНИЯ
    # =================================================

    def open_lesson_popup(
        self,
        title,
        lesson=None
    ):

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        # Время начала
        time_input = TextInput(
            hint_text="Начало, например 08:30",
            text=(
                lesson.get("time", "")
                if lesson
                else ""
            ),
            multiline=False,
            font_name=self.font_name,
            font_size=dp(17),
            padding=(
                dp(10),
                dp(10)
            )
        )

        # Время окончания
        end_time_input = TextInput(
            hint_text="Окончание, например 09:15",
            text=(
                lesson.get("end_time", "")
                if lesson
                else ""
            ),
            multiline=False,
            font_name=self.font_name,
            font_size=dp(17),
            padding=(
                dp(10),
                dp(10)
            )
        )

        # Предмет
        subject_input = TextInput(
            hint_text="Предмет",
            text=(
                lesson.get("subject", "")
                if lesson
                else ""
            ),
            multiline=False,
            font_name=self.font_name,
            font_size=dp(17),
            padding=(
                dp(10),
                dp(10)
            )
        )

        # Учитель
        teacher_input = TextInput(
            hint_text="Учитель",
            text=(
                lesson.get("teacher", "")
                if lesson
                and lesson.get("teacher") != "—"
                else ""
            ),
            multiline=False,
            font_name=self.font_name,
            font_size=dp(17),
            padding=(
                dp(10),
                dp(10)
            )
        )

        # Кабинет
        room_input = TextInput(
            hint_text="Кабинет",
            text=(
                lesson.get("room", "")
                if lesson
                and lesson.get("room") != "—"
                else ""
            ),
            multiline=False,
            font_name=self.font_name,
            font_size=dp(17),
            padding=(
                dp(10),
                dp(10)
            )
        )

        # Добавляем поля
        layout.add_widget(
            time_input
        )

        layout.add_widget(
            end_time_input
        )

        layout.add_widget(
            subject_input
        )

        layout.add_widget(
            teacher_input
        )

        layout.add_widget(
            room_input
        )

        # Кнопки
        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(52),
            spacing=dp(8)
        )

        cancel_button = Button(
            text="Отмена",
            font_name=self.font_name,
            font_size=dp(16),
            background_normal="",
            background_color=self.LIGHT_PINK,
            color=self.DARK_PINK
        )

        save_button = Button(
            text="Сохранить",
            font_name=self.font_name,
            font_size=dp(16),
            bold=True,
            background_normal="",
            background_color=self.PINK,
            color=self.WHITE
        )

        buttons.add_widget(
            cancel_button
        )

        buttons.add_widget(
            save_button
        )

        layout.add_widget(
            buttons
        )

        # Окно
        popup = Popup(
            title=title,
            title_font=self.font_name,
            title_size=dp(20),
            content=layout,
            size_hint=(0.92, 0.78),
            separator_color=self.PINK
        )

        # Отмена
        cancel_button.bind(
            on_press=popup.dismiss
        )

        # Сохранение
        save_button.bind(
            on_press=lambda btn:
            self.save_lesson_from_popup(
                time_input.text,
                end_time_input.text,
                subject_input.text,
                teacher_input.text,
                room_input.text,
                lesson,
                popup
            )
        )

        popup.open()

    # =================================================
    # СОХРАНЕНИЕ УРОКА
    # =================================================

    def save_lesson_from_popup(
        self,
        time,
        end_time,
        subject,
        teacher,
        room,
        lesson,
        popup
    ):

        # Убираем пробелы
        time = time.strip()
        end_time = end_time.strip()
        subject = subject.strip()
        teacher = teacher.strip()
        room = room.strip()

        # Проверяем обязательные поля
        if not time or not end_time or not subject:

            self.show_message(
                "Ошибка",
                "Введите начало, окончание и название предмета."
            )

            return

        # Редактирование
        if lesson is not None:

            lesson["time"] = time

            lesson["end_time"] = end_time

            lesson["subject"] = subject

            lesson["teacher"] = (
                teacher
                or "—"
            )

            lesson["room"] = (
                room
                or "—"
            )

        # Новый урок
        else:

            new_lesson = {
                "time": time,
                "end_time": end_time,
                "subject": subject,
                "teacher": teacher or "—",
                "room": room or "—"
            }

            if self.current_day not in self.schedule:

                self.schedule[
                    self.current_day
                ] = []

            self.schedule[
                self.current_day
            ].append(
                new_lesson
            )

        # Сохраняем
        self.save_schedule()

        # Закрываем окно
        popup.dismiss()

        # Обновляем список
        self.update_lessons()

    # =================================================
    # ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ
    # =================================================

    def confirm_delete(self, lesson):

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        # Текст
        text = Label(
            text=(
                "Вы действительно хотите "
                "удалить этот урок?\n\n"
                f"Время: "
                f"{lesson.get('time', '')} - "
                f"{lesson.get('end_time', '')}\n"
                f"Предмет: "
                f"{lesson.get('subject', '')}\n"
                f"Учитель: "
                f"{lesson.get('teacher', '—')}\n"
                f"Кабинет: "
                f"{lesson.get('room', '—')}"
            ),
            font_name=self.font_name,
            font_size=dp(17),
            bold=False,
            color=self.WHITE,
            halign="center",
            valign="middle"
        )

        text.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        layout.add_widget(
            text
        )

        # Кнопки
        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8)
        )

        cancel = Button(
            text="Отмена",
            font_name=self.font_name,
            font_size=dp(16),
            background_normal="",
            background_color=self.LIGHT_PINK,
            color=self.DARK_PINK
        )

        delete = Button(
            text="Удалить",
            font_name=self.font_name,
            font_size=dp(16),
            bold=True,
            background_normal="",
            background_color=self.PINK,
            color=self.WHITE
        )

        buttons.add_widget(
            cancel
        )

        buttons.add_widget(
            delete
        )

        layout.add_widget(
            buttons
        )

        # Окно
        popup = Popup(
            title="Удаление урока",
            title_font=self.font_name,
            title_size=dp(20),
            content=layout,
            size_hint=(0.90, 0.52),
            separator_color=self.PINK
        )

        cancel.bind(
            on_press=popup.dismiss
        )

        delete.bind(
            on_press=lambda btn:
            self.delete_lesson(
                lesson,
                popup
            )
        )

        popup.open()

    # =================================================
    # УДАЛЕНИЕ
    # =================================================

    def delete_lesson(
        self,
        lesson,
        popup
    ):

        if self.current_day in self.schedule:

            if lesson in self.schedule[
                self.current_day
            ]:

                self.schedule[
                    self.current_day
                ].remove(
                    lesson
                )

        self.save_schedule()

        popup.dismiss()

        self.update_lessons()

    # =================================================
    # СООБЩЕНИЕ
    # =================================================

    def show_message(
        self,
        title,
        message
    ):

        content = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        label = Label(
            text=message,
            font_name=self.font_name,
            font_size=dp(16),
            color=self.TEXT_COLOR,
            halign="center",
            valign="middle"
        )

        label.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        button = Button(
            text="Хорошо",
            font_name=self.font_name,
            font_size=dp(16),
            background_normal="",
            background_color=self.PINK,
            color=self.WHITE,
            size_hint_y=None,
            height=dp(50)
        )

        content.add_widget(
            label
        )

        content.add_widget(
            button
        )

        popup = Popup(
            title=title,
            title_font=self.font_name,
            title_size=dp(20),
            content=content,
            size_hint=(0.85, 0.35),
            separator_color=self.PINK
        )

        button.bind(
            on_press=popup.dismiss
        )

        popup.open()


# =====================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =====================================================

if __name__ == "__main__":
    ScheduleApp().run()