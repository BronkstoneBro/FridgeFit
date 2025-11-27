from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('meat', 'Мясо и птица'),
        ('fish', 'Рыба и морепродукты'),
        ('dairy', 'Молочные продукты'),
        ('eggs', 'Яйца'),
        ('cereals', 'Крупы и злаки'),
        ('bread', 'Хлеб и выпечка'),
        ('vegetables', 'Овощи'),
        ('fruits', 'Фрукты'),
        ('nuts', 'Орехи и семена'),
        ('oils', 'Масла и жиры'),
        ('legumes', 'Бобовые'),
        ('sweets', 'Сладости'),
        ('beverages', 'Напитки'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other', help_text="Категория продукта")
    calories = models.FloatField(help_text="Калории на 100 г")
    protein = models.FloatField(help_text="Белки (на 100 г)")
    fat = models.FloatField(help_text="Жиры (на 100 г)")
    carbs = models.FloatField(help_text="Углеводы (на 100 г)")
    fiber = models.FloatField(default=0, help_text="Клетчатка (на 100 г)")

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self) -> str:
        return self.name

