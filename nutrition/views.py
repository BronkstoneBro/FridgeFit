from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from django.db.models import QuerySet
from django.shortcuts import render

from .forms import NutritionCalcForm
from .models import Product


@dataclass
class ProductPortion:
    name: str
    grams: float
    calories: float
    protein: float
    fat: float
    carbs: float


def _parse_items_text(text: str) -> List[Tuple[str, float]]:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    parsed: List[Tuple[str, float]] = []
    for idx, line in enumerate(lines, start=1):
        # Split by comma or semicolon
        if ";" in line:
            parts = [p.strip() for p in line.split(";")]
        else:
            parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            raise ValueError(f"Строка {idx}: укажите 'название, граммы'")
        name = parts[0]
        grams_str = parts[1].replace(",", ".")
        try:
            grams = float(grams_str)
        except ValueError as exc:
            raise ValueError(f"Строка {idx}: не удалось распознать граммы '{parts[1]}'") from exc
        if grams <= 0:
            raise ValueError(f"Строка {idx}: значение грамм должно быть больше 0")
        parsed.append((name, grams))
    return parsed


def calculator_view(request):
    products_qs: QuerySet[Product] = Product.objects.all()
    context: dict = {"available_products": products_qs}

    if request.method == "POST":
        form = NutritionCalcForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data["weight"]
            calorie_limit = form.cleaned_data["calorie_limit"]
            items_text = form.cleaned_data["items_text"]

            try:
                parsed_items = _parse_items_text(items_text)
            except ValueError as e:
                form.add_error("items_text", str(e))
                context["form"] = form
                return render(request, "nutrition/calculator.html", context)

            portions: List[ProductPortion] = []
            not_found: List[str] = []

            for name, grams in parsed_items:
                product = Product.objects.filter(name__iexact=name).first()
                if not product:
                    not_found.append(name)
                    continue
                factor = grams / 100.0
                portions.append(
                    ProductPortion(
                        name=product.name,
                        grams=grams,
                        calories=round(product.calories * factor, 2),
                        protein=round(product.protein * factor, 2),
                        fat=round(product.fat * factor, 2),
                        carbs=round(product.carbs * factor, 2),
                    )
                )

            totals = {
                "calories": round(sum(p.calories for p in portions), 2),
                "protein": round(sum(p.protein for p in portions), 2),
                "fat": round(sum(p.fat for p in portions), 2),
                "carbs": round(sum(p.carbs for p in portions), 2),
            }

            remaining = round(calorie_limit - totals["calories"], 2)

            # Simple meal split: 30% breakfast, 40% lunch, 30% dinner
            split = [
                ("Завтрак", 0.30),
                ("Обед", 0.40),
                ("Ужин", 0.30),
            ]
            meals = [
                {
                    "name": label,
                    "calories": round(totals["calories"] * ratio, 2),
                    "protein": round(totals["protein"] * ratio, 2),
                    "fat": round(totals["fat"] * ratio, 2),
                    "carbs": round(totals["carbs"] * ratio, 2),
                }
                for (label, ratio) in split
            ]

            context.update(
                {
                    "form": form,
                    "portions": portions,
                    "totals": totals,
                    "weight": weight,
                    "calorie_limit": calorie_limit,
                    "remaining": remaining,
                    "meals": meals,
                    "not_found": not_found,
                }
            )
            return render(request, "nutrition/calculator.html", context)
        else:
            context["form"] = form
            return render(request, "nutrition/calculator.html", context)

    # GET
    context["form"] = NutritionCalcForm()
    return render(request, "nutrition/calculator.html", context)

