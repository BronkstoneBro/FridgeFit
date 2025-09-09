from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from django.db.models import QuerySet
from django.shortcuts import render
from django.http import JsonResponse
import json

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


def calculate_ideal_weight(height, gender):
    """
    Расчет идеального веса по формуле Девина
    """
    if gender == "male":
        # Мужчины: 50 кг + 2.3 кг за каждый см выше 152 см
        ideal_weight = 50 + 2.3 * (height - 152) / 2.54 if height > 152 else 50
    else:
        # Женщины: 45.5 кг + 2.3 кг за каждый см выше 152 см
        ideal_weight = 45.5 + 2.3 * (height - 152) / 2.54 if height > 152 else 45.5
    
    return round(ideal_weight, 1)


def calculate_bmr_and_calories(height, weight_kg, weight_grams, age, gender, activity_level, goal):
    """
    Расчет BMR, TDEE и калорий в зависимости от цели
    """
    total_weight = weight_kg + (weight_grams / 1000)
    
    # Расчет BMR по формуле Миффлина-Сан Жеора
    if gender == "male":
        bmr = 10 * total_weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * total_weight + 6.25 * height - 5 * age - 161
    
    # Расчет TDEE
    tdee = bmr * float(activity_level)
    
    # Расчет калорий в зависимости от цели
    if goal == "weight_loss":
        # Дефицит 15% для похудения
        target_calories = int(tdee * 0.85)
    elif goal == "weight_gain":
        # Профицит 15% для набора массы
        target_calories = int(tdee * 1.15)
    else:
        # Поддержание веса
        target_calories = int(tdee)
    
    return int(bmr), int(tdee), target_calories


def calculate_macros(target_calories, total_weight):
    """
    Расчет БЖУ по пропорциям
    Белки: 1.5 г/кг
    Жиры: 0.9 г/кг
    Углеводы: остальное
    """
    # Белки: 1.5 г/кг
    protein_grams = round(1.5 * total_weight, 1)
    protein_calories = protein_grams * 4
    
    # Жиры: 0.9 г/кг
    fat_grams = round(0.9 * total_weight, 1)
    fat_calories = fat_grams * 9
    
    # Углеводы: остальное
    carbs_calories = target_calories - protein_calories - fat_calories
    carbs_grams = round(carbs_calories / 4, 1) if carbs_calories > 0 else 0
    
    return {
        'protein': {'grams': protein_grams, 'calories': int(protein_calories)},
        'fat': {'grams': fat_grams, 'calories': int(fat_calories)},
        'carbs': {'grams': carbs_grams, 'calories': int(carbs_calories)}
    }


def calculate_water_intake(total_weight):
    """
    Расчет нормы воды: 1 кг + 30 мл
    """
    return round(total_weight * 30, 0)


def search_products(request):
    """
    AJAX endpoint для поиска продуктов с автозаполнением
    """
    if request.method == 'GET' and 'query' in request.GET:
        query = request.GET.get('query', '').strip()
        if len(query) >= 2:  # Поиск только при вводе минимум 2 символов
            products = Product.objects.filter(
                name__icontains=query
            ).order_by('name')[:10]  # Ограничиваем 10 результатами
            
            results = [
                {
                    'id': product.id,
                    'name': product.name,
                    'calories': product.calories,
                    'protein': product.protein,
                    'fat': product.fat,
                    'carbs': product.carbs
                }
                for product in products
            ]
            return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})


def calculator_view(request):
    products_qs: QuerySet[Product] = Product.objects.all()
    context: dict = {"available_products": products_qs}

    if request.method == "POST":
        form = NutritionCalcForm(request.POST)
        # Получаем выбранные продукты из POST данных - делаем это до проверки валидации
        selected_products = request.POST.getlist('selected_products[]')
        selected_portions = request.POST.getlist('selected_portions[]')
        
        if form.is_valid():
            height = form.cleaned_data["height"]
            weight_kg = form.cleaned_data["weight_kg"]
            weight_grams = form.cleaned_data["weight_grams"]
            age = form.cleaned_data["age"]
            gender = form.cleaned_data["gender"]
            activity_level = form.cleaned_data["activity_level"]
            
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            goal = form.cleaned_data["goal"]
            
            # Расчет идеального веса
            ideal_weight = calculate_ideal_weight(height, gender)
            
            # Расчет BMR, TDEE и калорий
            bmr, tdee, target_calories = calculate_bmr_and_calories(
                height, weight_kg, weight_grams, age, gender, activity_level, goal
            )
            total_weight = weight_kg + (weight_grams / 1000)

            portions: List[ProductPortion] = []
            not_found: List[str] = []

            # Обрабатываем выбранные продукты и создаем данные для восстановления состояния
            selected_products_data = []
            for i, product_id in enumerate(selected_products):
                if i < len(selected_portions):
                    try:
                        grams = float(selected_portions[i])
                        if grams <= 0:
                            continue
                        
                        product = Product.objects.filter(id=product_id).first()
                        if not product:
                            continue
                        
                        # Сохраняем данные для восстановления состояния в JS
                        selected_products_data.append({
                            'id': product.id,
                            'name': product.name,
                            'calories': product.calories,
                            'protein': product.protein,
                            'fat': product.fat,
                            'carbs': product.carbs,
                            'grams': grams
                        })
                            
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
                    except (ValueError, TypeError):
                        continue

            totals = {
                "calories": round(sum(p.calories for p in portions), 2),
                "protein": round(sum(p.protein for p in portions), 2),
                "fat": round(sum(p.fat for p in portions), 2),
                "carbs": round(sum(p.carbs for p in portions), 2),
            }

            # Расчет БЖУ по пропорциям
            target_macros = calculate_macros(target_calories, total_weight)
            
            # Расчет нормы воды
            water_intake = calculate_water_intake(total_weight)
            
            remaining = round(target_calories - totals["calories"], 2)

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

            goal_labels = {
                'weight_loss': 'Снижение жира',
                'maintenance': 'Поддержание веса',
                'weight_gain': 'Набор массы'
            }
            
            context.update(
                {
                    "form": form,
                    "first_name": first_name,
                    "last_name": last_name,
                    "portions": portions,
                    "totals": totals,
                    "total_weight": total_weight,
                    "ideal_weight": ideal_weight,
                    "height": height,
                    "age": age,
                    "gender": "Мужчина" if gender == "male" else "Женщина",
                    "goal": goal_labels[goal],
                    "bmr": bmr,
                    "tdee": tdee,
                    "target_calories": target_calories,
                    "target_macros": target_macros,
                    "water_intake": water_intake,
                    "remaining": remaining,
                    "meals": meals,
                    "not_found": not_found,
                    "selected_products_json": json.dumps(selected_products_data),
                }
            )
            return render(request, "nutrition/calculator.html", context)
        else:
            context["form"] = form
            # Сохраняем выбранные продукты даже при ошибках валидации
            selected_products_data = []
            for i, product_id in enumerate(selected_products):
                if i < len(selected_portions):
                    try:
                        grams = float(selected_portions[i])
                        if grams <= 0:
                            continue
                        
                        product = Product.objects.filter(id=product_id).first()
                        if product:
                            selected_products_data.append({
                                'id': product.id,
                                'name': product.name,
                                'calories': product.calories,
                                'protein': product.protein,
                                'fat': product.fat,
                                'carbs': product.carbs,
                                'grams': grams
                            })
                    except (ValueError, TypeError):
                        continue
            
            context["selected_products_json"] = json.dumps(selected_products_data)
            return render(request, "nutrition/calculator.html", context)

    # GET
    context["form"] = NutritionCalcForm()
    context["selected_products_json"] = "[]"  # Пустой массив для GET запросов
    return render(request, "nutrition/calculator.html", context)

