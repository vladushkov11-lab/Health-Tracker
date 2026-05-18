from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from database.dao_app import get_metrics_by_user_id
from database.dao_stats import get_all_metrics_stats
from api.logging_config import logger

async def get_user_stats(x_user_id: str, user_data: Optional[Dict[str, Any]] = None, days: int = 10) -> Dict[str, Any]:
    """
    Собирает полную статистику по пользователю с рекомендациями.
    Объединяет данные из БД (dao_stats) и аналитику (тренды, волатильность).
    """
    # 1. Получаем сырые метрики из БД
    try:
        metrics = await get_metrics_by_user_id(x_user_id=x_user_id, limit=days)
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        metrics = []
    
    # 2. Получаем агрегированную статистику из БД
    try:
        db_stats = await get_all_metrics_stats(x_user_id=x_user_id, days=days)
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        db_stats = {}
    
    # 3. Если метрик нет, возвращаем пустой результат
    if not metrics:
        return {
            "total_metrics": 0,
            "period_days": 0,
            "db_stats": db_stats,
            "insights": ["Нет данных для анализа. Добавьте метрики."]
        }
    
    # 4. Конвертируем значения и сортируем по дате
    converted_metrics = []
    for m in metrics:
        converted_m = {k: float(v) if isinstance(v, (int, float)) else (0 if v is None else v) for k, v in m.items()}
        converted_metrics.append(converted_m)
    
    metrics_sorted = sorted(converted_metrics, key=lambda x: x.get("date", ""))
    
    # 5. Расчёт периода
    dates = [m["date"] for m in metrics_sorted if m.get("date")]
    period_days = (max(dates) - min(dates)).days + 1 if dates else len(metrics_sorted)
    
    # 6. Расчёт средних и сумм (дублируем для аналитики)
    numeric_fields = ["steps", "calories", "distance", "sleep_hours", "sleep_score", "calories_intake", "water_ml", "mood", "stress_level"]
    field_values = {field: [float(m.get(field, 0) or 0) for m in metrics_sorted] for field in numeric_fields}
    averages = {field: round(sum(values) / len(values), 2) for field, values in field_values.items() if values}
    totals = {field: sum(values) for field, values in field_values.items() if values}
    
    # 7. Тренды (линейная регрессия)
    trends = {}
    for field, values in field_values.items():
        if len(values) >= 2:
            n = len(values)
            sum_x = sum(range(n))
            sum_y = sum(values)
            sum_xy = sum(i * v for i, v in enumerate(values))
            sum_x2 = sum(i ** 2 for i in range(n))
            denominator = n * sum_x2 - sum_x ** 2
            slope = round((n * sum_xy - sum_x * sum_y) / denominator, 2) if denominator != 0 else 0
            trends[field] = {"slope": slope, "direction": "up" if slope > 0.01 else "down" if slope < -0.01 else "flat"}
    
    # 8. Волатильность
    volatility = {}
    for field, values in field_values.items():
        if len(values) >= 2:
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std_dev = round(variance ** 0.5, 2)
            cv = round((std_dev / mean) * 100, 2) if mean != 0 else 0
            volatility[field] = {"std_dev": std_dev, "cv": cv, "level": "high" if cv > 30 else "medium" if cv > 15 else "low"}
    
    # 9. Генерация рекомендаций
    insights = generate_insights(averages, trends, volatility, user_data, db_stats)
    
    return {
        "total_metrics": len(metrics_sorted),
        "period_days": period_days,
        "averages": averages,
        "totals": totals,
        "trends": trends,
        "volatility": volatility,
        "user_profile": build_user_profile(user_data, averages) if user_data else {},
        "db_stats": db_stats,
        "insights": insights
    }


def build_user_profile(user_data: Dict[str, Any], averages: Dict[str, float]) -> Dict[str, Any]:
    """Строит профиль пользователя с BMI и целями."""
    height = float(user_data.get("height", 0)) if user_data.get("height") else 0
    weight = float(user_data.get("weight", 0)) if user_data.get("weight") else 0
    target_weight = float(user_data.get("target_weight", 0)) if user_data.get("target_weight") else 0
    daily_step_goal = int(user_data.get("daily_step_goal", 0)) if user_data.get("daily_step_goal") else 0
    gender = str(user_data.get("gender", "")) if user_data.get("gender") else ""
    birth_date = user_data.get("birth_date", None)
    
    profile = {
        "height": height,
        "weight": weight,
        "target_weight": target_weight,
        "daily_step_goal": daily_step_goal,
        "gender": gender
    }
    
    # BMI
    if height > 0 and weight > 0:
        bmi = round(weight / ((height / 100) ** 2), 2)
        profile["bmi"] = bmi
        profile["bmi_category"] = "underweight" if bmi < 18.5 else "normal" if bmi < 25 else "overweight" if bmi < 30 else "obese"
    
    # Прогресс по весу
    if weight > 0 and target_weight > 0:
        profile["weight_progress"] = {
            "difference": round(target_weight - weight, 2),
            "percentage": round(((weight - target_weight) / weight) * 100, 2) if weight > 0 else 0
        }
    
    # Достижение цели по шагам
    if daily_step_goal > 0:
        avg_steps = averages.get("steps", 0)
        profile["step_goal_achievement"] = {
            "goal": daily_step_goal,
            "average": avg_steps,
            "percentage": round((avg_steps / daily_step_goal) * 100, 2),
            "status": "achieved" if avg_steps >= daily_step_goal else "below_goal"
        }
    
    # BMR
    age = None
    if birth_date:
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.fromisoformat(birth_date)
            age = (datetime.now(timezone.utc) - birth_date).days // 365
        except:
            age = 30
    
    if age and weight and height:
        if gender == "male" or gender == "мужской":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        profile["bmr"] = round(bmr, 2)
        profile["recommended_calories"] = round(bmr * 1.375, 2)
    
    return profile


def generate_insights(averages: Dict[str, float], trends: Dict[str, Any], 
                        volatility: Dict[str, Any], user_data: Dict[str, Any], 
                        db_stats: Dict[str, Any]) -> List[str]:
    """Генерирует рекомендации на основе средних значений, трендов и профиля."""
    insights = []
    
    # Сон
    if averages.get("sleep_hours", 0) < 7:
        insights.append("💤 Вы спите меньше 7 часов в сутки.")
    elif averages.get("sleep_hours", 0) > 9:
        insights.append("💤 Вы спите больше 9 часов в сутки.")
    else:
        insights.append("💤 Продолжительность сна в норме (7-9 часов).")
    
    # Шаги
    if averages.get("steps", 0) < 5000:
        insights.append("👟 Активность низкая (<5000 шагов).")
    elif averages.get("steps", 0) < 10000:
        insights.append("👟 Средняя активность (5000-10000 шагов).")
    else:
        insights.append("👟 Отличная активность! Вы проходите более 10000 шагов.")
    
    # Цель по шагам
    if user_data and user_data.get("daily_step_goal"):
        goal = user_data["daily_step_goal"]
        avg_steps = averages.get("steps", 0)
        percentage = round((avg_steps / goal) * 100, 2) if goal > 0 else 0
        if avg_steps >= goal:
            insights.append(f"✅ Цель по шагам достигнута ({percentage}% от {goal}).")
        else:
            insights.append(f"🎯 Недостигнута цель по шагам: {percentage}% от {goal}.")
    
    # Тренд активности
    if trends.get("steps", {}).get("direction") == "up":
        insights.append("📈 Активность растёт — так держать!")
    elif trends.get("steps", {}).get("direction") == "down":
        insights.append("📉 Активность снижается.")
    
    # Волатильность
    if volatility.get("steps", {}).get("level") == "high":
        insights.append("⚠️ Высокая волатильность активности — старайтесь быть более последовательны.")
    
    # Вода
    if averages.get("water_ml", 0) < 1500:
        insights.append("💧 Вы пьёте мало воды (<1.5 л).")
    elif averages.get("water_ml", 0) >= 2000:
        insights.append("💧 Отличное потребление воды!")
    
    # Настроение
    if averages.get("mood", 0) < 3:
        insights.append("😊 Ваше настроение ниже среднего.")
    elif averages.get("mood", 0) >= 4:
        insights.append("😊 Ваше настроение в норме или выше.")
    
    # Стресс
    if averages.get("stress_level", 0) >= 4:
        insights.append("😰 Уровень стресса высокий.")
    else:
        insights.append("😰 Уровень стресса под контролем.")
    
    # BMI
    if user_data:
        height = float(user_data.get("height", 0)) if user_data.get("height") else 0
        weight = float(user_data.get("weight", 0)) if user_data.get("weight") else 0
        if height > 0 and weight > 0:
            bmi = round(weight / ((height / 100) ** 2), 2)
            category = "underweight" if bmi < 18.5 else "normal" if bmi < 25 else "overweight" if bmi < 30 else "obese"
            category_text = {"underweight": "недостаточный вес", "normal": "нормальный вес", "overweight": "избыточный вес", "obese": "ожирение"}
            insights.append(f"📊 Ваш BMI: {bmi} ({category_text.get(category, 'неизвестно')}).")
    
    # Дефицит калорий
    if "calories_intake" in averages and "calories" in averages:
        deficit = averages["calories"] - averages["calories_intake"]
        if deficit > 0:
            insights.append(f"🔥 Вы создаёте дефицит калорий ({round(deficit)} ккал/день).")
        elif deficit < 0:
            insights.append(f"⚠️ Профицит калорий ({round(abs(deficit))} ккал/день).")
    
    return insights