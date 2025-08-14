from django import forms


class NutritionCalcForm(forms.Form):
    weight = forms.FloatField(
        label="Ваш вес (кг)",
        min_value=1,
        help_text="Например, 70",
    )
    calorie_limit = forms.IntegerField(
        label="Дневная норма калорий (ккал)",
        min_value=500,
        help_text="Например, 2200",
    )
    items_text = forms.CharField(
        label="Продукты и граммы",
        widget=forms.Textarea(attrs={"rows": 6, "placeholder": "Каждая строка: название, граммы (например: Куриная грудка, 200)"}),
        help_text=(
            "Укажите по одной записи на строку: 'название, граммы'. Название должно совпадать с продуктом в базе."
        ),
    )

