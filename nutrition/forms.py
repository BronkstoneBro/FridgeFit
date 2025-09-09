from django import forms


class NutritionCalcForm(forms.Form):
    first_name = forms.CharField(
        label="Имя",
        max_length=100,
        required=False,
        help_text="По желанию",
    )
    last_name = forms.CharField(
        label="Фамилия",
        max_length=100,
        required=False,
        help_text="По желанию",
    )
    height = forms.IntegerField(
        label="Ваш рост (см)",
        min_value=100,
        max_value=250,
        help_text="Например, 175",
    )
    weight_kg = forms.IntegerField(
        label="Ваш вес (кг)",
        min_value=30,
        max_value=300,
        help_text="Например, 70",
    )
    weight_grams = forms.IntegerField(
        label="Граммы",
        min_value=0,
        max_value=999,
        initial=0,
        help_text="От 0 до 999 г",
    )
    age = forms.IntegerField(
        label="Ваш возраст (лет)",
        min_value=10,
        max_value=100,
        help_text="Например, 30",
    )
    gender = forms.ChoiceField(
        label="Пол",
        choices=[("male", "Мужчина"), ("female", "Женщина")],
        widget=forms.RadioSelect,
    )
    activity_level = forms.ChoiceField(
        label="Уровень активности",
        choices=[
            (1.1, "Минимальная активность, сидячий образ жизни"),
            (1.375, "Легкая активность, спорт 2-3 раза в неделю"),
            (1.55, "Активный спорт 4-5 раз в неделю"),
            (1.725, "Высокая активность, спорт каждый день")
        ],
    )
    goal = forms.ChoiceField(
        label="Цель",
        choices=[
            ('weight_loss', 'Снижение жира'),
            ('maintenance', 'Поддержание веса'),
            ('weight_gain', 'Набор массы')
        ],
        widget=forms.RadioSelect,
    )

