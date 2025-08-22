from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    calories = models.FloatField(help_text="Калории на 100 г")
    protein = models.FloatField(help_text="Белки (на 100 г)")
    fat = models.FloatField(help_text="Жиры (на 100 г)")
    carbs = models.FloatField(help_text="Углеводы (на 100 г)")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

