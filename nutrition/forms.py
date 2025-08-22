from django import forms


class NutritionCalcForm(forms.Form):
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
            (1.2, "Малоподвижный образ жизни"),
            (1.375, "Легкая активность (1-3 раза в неделю)"),
            (1.55, "Умеренная активность (3-5 раз в неделю)"),
            (1.725, "Высокая активность (6-7 раз в неделю)"),
            (1.9, "Очень высокая активность (2 раза в день)")
        ],
    )
    items_text = forms.CharField(
        label="Продукты и граммы",
        widget=forms.Textarea(attrs={"rows": 6, "placeholder": "Каждая строка: название, граммы (например: Куриная грудка, 200)"}),
        help_text=(
            "Укажите по одной записи на строку: 'название, граммы'. Название должно совпадать с продуктом в базе."
        ),
    )

