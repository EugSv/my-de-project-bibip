import os
from decimal import Decimal

from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        # Превращаем модель в строку
        data = f"{model.id};{model.name};{model.brand}"

        # Записываем в файл, запоминаем номер строки
        path = os.path.join(self.root_directory_path, "models.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                line_number = len(f.readlines())
        else:
            line_number = 0

        with open(path, "a", encoding="utf-8") as f:
            f.write(data + "\n")

        # Обновляем индекс
        index_path = os.path.join(self.root_directory_path, "models_index.txt")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                index = []
                for line in f:
                    line = line.strip()
                    if line:
                        key, num = line.split(";")
                        index.append({"key": key, "line": int(num)})
        else:
            index = []

        index.append({"key": str(model.id), "line": line_number})
        index.sort(key=lambda x: x["key"])

        with open(index_path, "w", encoding="utf-8") as f:
            for item in index:
                f.write(f"{item['key']};{item['line']}\n")

        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        # Превращаем машину в строку
        data = f"{car.vin};{car.model};{car.price};{car.date_start.isoformat()};{car.status}"

        # Записываем в файл, запоминаем номер строки
        path = os.path.join(self.root_directory_path, "cars.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                line_number = len(f.readlines())
        else:
            line_number = 0

        with open(path, "a", encoding="utf-8") as f:
            f.write(data + "\n")

        # Обновляем индекс
        index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                index = []
                for line in f:
                    line = line.strip()
                    if line:
                        key, num = line.split(";")
                        index.append({"key": key, "line": int(num)})
        else:
            index = []

        index.append({"key": car.vin, "line": line_number})
        index.sort(key=lambda x: x["key"])

        with open(index_path, "w", encoding="utf-8") as f:
            for item in index:
                f.write(f"{item['key']};{item['line']}\n")

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        # Записываем продажу в файл
        data = f"{sale.sales_number};{sale.car_vin};{sale.sales_date.isoformat()};{sale.cost}"

        path = os.path.join(self.root_directory_path, "sales.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                line_number = len(f.readlines())
        else:
            line_number = 0

        with open(path, "a", encoding="utf-8") as f:
            f.write(data + "\n")

        # Обновляем индекс продаж
        index_path = os.path.join(self.root_directory_path, "sales_index.txt")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                index = []
                for line in f:
                    line = line.strip()
                    if line:
                        key, num = line.split(";")
                        index.append({"key": key, "line": int(num)})
        else:
            index = []

        index.append({"key": sale.car_vin, "line": line_number})
        index.sort(key=lambda x: x["key"])

        with open(index_path, "w", encoding="utf-8") as f:
            for item in index:
                f.write(f"{item['key']};{item['line']}\n")

        # Меняем статус машины на sold
        cars_index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        with open(cars_index_path, "r", encoding="utf-8") as f:
            cars_index = []
            for line in f:
                line = line.strip()
                if line:
                    key, num = line.split(";")
                    cars_index.append({"key": key, "line": int(num)})

        car_line = None
        for item in cars_index:
            if item["key"] == sale.car_vin:
                car_line = item["line"]
                break

        cars_path = os.path.join(self.root_directory_path, "cars.txt")
        with open(cars_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        raw = lines[car_line].strip()
        vin, model, price, date_start, status = raw.split(";")
        car = Car(
            vin=vin,
            model=int(model),
            price=Decimal(price),
            date_start=date_start,
            status=CarStatus(status),
        )
        car.status = CarStatus.sold

        lines[car_line] = f"{car.vin};{car.model};{car.price};{car.date_start.isoformat()};{car.status}\n"
        with open(cars_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        path = os.path.join(self.root_directory_path, "cars.txt")
        if not os.path.exists(path):
            return []

        result = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                vin, model, price, date_start, car_status = line.split(";")
                if car_status == status:
                    result.append(Car(
                        vin=vin,
                        model=int(model),
                        price=Decimal(price),
                        date_start=date_start,
                        status=CarStatus(car_status),
                    ))

        return result

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        # Ищем машину через индекс
        cars_index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        if not os.path.exists(cars_index_path):
            return None

        car_line = None
        with open(cars_index_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    key, num = line.split(";")
                    if key == vin:
                        car_line = int(num)
                        break

        if car_line is None:
            return None

        cars_path = os.path.join(self.root_directory_path, "cars.txt")
        with open(cars_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        raw = lines[car_line].strip()
        c_vin, c_model, c_price, c_date, c_status = raw.split(";")
        car = Car(
            vin=c_vin,
            model=int(c_model),
            price=Decimal(c_price),
            date_start=c_date,
            status=CarStatus(c_status),
        )

        # Ищем модель через индекс
        models_index_path = os.path.join(self.root_directory_path, "models_index.txt")
        model_line = None
        with open(models_index_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    key, num = line.split(";")
                    if key == str(car.model):
                        model_line = int(num)
                        break

        models_path = os.path.join(self.root_directory_path, "models.txt")
        with open(models_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        raw = lines[model_line].strip()
        m_id, m_name, m_brand = raw.split(";", 2)
        model = Model(id=int(m_id), name=m_name, brand=m_brand)

        # Ищем продажу если машина продана
        sales_date = None
        sales_cost = None
        if car.status == CarStatus.sold:
            sales_index_path = os.path.join(self.root_directory_path, "sales_index.txt")
            sale_line = None
            with open(sales_index_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        key, num = line.split(";")
                        if key == vin:
                            sale_line = int(num)
                            break

            if sale_line is not None:
                sales_path = os.path.join(self.root_directory_path, "sales.txt")
                with open(sales_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                raw = lines[sale_line].strip()
                parts = raw.split(";")
                sales_date_str = parts[2]
                sales_cost = Decimal(parts[3])

                from datetime import datetime
                sales_date = datetime.fromisoformat(sales_date_str)

        return CarFullInfo(
            vin=car.vin,
            car_model_name=model.name,
            car_model_brand=model.brand,
            price=car.price,
            date_start=car.date_start,
            status=car.status,
            sales_date=sales_date,
            sales_cost=sales_cost,
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        # Находим строку машины через индекс
        cars_index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        with open(cars_index_path, "r", encoding="utf-8") as f:
            index = []
            for line in f:
                line = line.strip()
                if line:
                    key, num = line.split(";")
                    index.append({"key": key, "line": int(num)})

        car_line = None
        for item in index:
            if item["key"] == vin:
                car_line = item["line"]
                break

        # Обновляем VIN в файле с машинами
        cars_path = os.path.join(self.root_directory_path, "cars.txt")
        with open(cars_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        raw = lines[car_line].strip()
        c_vin, c_model, c_price, c_date, c_status = raw.split(";")
        car = Car(
            vin=new_vin,
            model=int(c_model),
            price=Decimal(c_price),
            date_start=c_date,
            status=CarStatus(c_status),
        )
        lines[car_line] = f"{car.vin};{car.model};{car.price};{car.date_start.isoformat()};{car.status}\n"

        with open(cars_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        # Обновляем индекс
        for item in index:
            if item["key"] == vin:
                item["key"] = new_vin
                break
        index.sort(key=lambda x: x["key"])

        with open(cars_index_path, "w", encoding="utf-8") as f:
            for item in index:
                f.write(f"{item['key']};{item['line']}\n")

        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        # Ищем продажу по sales_number
        sales_path = os.path.join(self.root_directory_path, "sales.txt")
        with open(sales_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        sale_line_number = None
        car_vin = None
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if parts[0] == sales_number:
                sale_line_number = i
                car_vin = parts[1]
                break

        # Меняем статус машины обратно на available
        cars_index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        with open(cars_index_path, "r", encoding="utf-8") as f:
            cars_index = []
            for line in f:
                line = line.strip()
                if line:
                    key, num = line.split(";")
                    cars_index.append({"key": key, "line": int(num)})

        car_line = None
        for item in cars_index:
            if item["key"] == car_vin:
                car_line = item["line"]
                break

        cars_path = os.path.join(self.root_directory_path, "cars.txt")
        with open(cars_path, "r", encoding="utf-8") as f:
            car_lines = f.readlines()

        raw = car_lines[car_line].strip()
        c_vin, c_model, c_price, c_date, c_status = raw.split(";")
        car = Car(
            vin=c_vin,
            model=int(c_model),
            price=Decimal(c_price),
            date_start=c_date,
            status=CarStatus.available,
        )
        car_lines[car_line] = f"{car.vin};{car.model};{car.price};{car.date_start.isoformat()};{car.status}\n"

        with open(cars_path, "w", encoding="utf-8") as f:
            f.writelines(car_lines)

        # Удаляем из индекса продаж
        sales_index_path = os.path.join(self.root_directory_path, "sales_index.txt")
        with open(sales_index_path, "r", encoding="utf-8") as f:
            sales_index = []
            for line in f:
                line = line.strip()
                if line:
                    key, num = line.split(";")
                    sales_index.append({"key": key, "line": int(num)})

        sales_index = [item for item in sales_index if item["key"] != car_vin]

        with open(sales_index_path, "w", encoding="utf-8") as f:
            for item in sales_index:
                f.write(f"{item['key']};{item['line']}\n")

        # Стираем строку продажи
        lines[sale_line_number] = "\n"
        with open(sales_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        # Читаем индекс машин
        cars_index_path = os.path.join(self.root_directory_path, "cars_index.txt")
        with open(cars_index_path, "r", encoding="utf-8") as f:
            cars_index = []
            for line in f:
                line = line.strip()
                if line:
                    key, num = line.split(";")
                    cars_index.append({"key": key, "line": int(num)})

        cars_path = os.path.join(self.root_directory_path, "cars.txt")
        with open(cars_path, "r", encoding="utf-8") as f:
            car_lines = f.readlines()

        # Считаем продажи по моделям
        stats = {}
        sales_path = os.path.join(self.root_directory_path, "sales.txt")
        with open(sales_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(";")
                sale_car_vin = parts[1]
                sale_cost = Decimal(parts[3])

                car_line = None
                for item in cars_index:
                    if item["key"] == sale_car_vin:
                        car_line = item["line"]
                        break

                if car_line is None:
                    continue

                raw = car_lines[car_line].strip()
                c_vin, c_model, c_price, c_date, c_status = raw.split(";")
                model_id = int(c_model)

                if model_id not in stats:
                    stats[model_id] = {"count": 0, "max_cost": Decimal("0")}
                stats[model_id]["count"] += 1
                if sale_cost > stats[model_id]["max_cost"]:
                    stats[model_id]["max_cost"] = sale_cost

        # Сортируем и берём топ-3
        sorted_stats = sorted(
            stats.items(),
            key=lambda x: (x[1]["count"], x[1]["max_cost"]),
            reverse=True,
        )
        top_3 = sorted_stats[:3]

        # Читаем названия моделей
        models_index_path = os.path.join(self.root_directory_path, "models_index.txt")
        with open(models_index_path, "r", encoding="utf-8") as f:
            models_index = []
            for line in f:
                line = line.strip()
                if line:
                    key, num = line.split(";")
                    models_index.append({"key": key, "line": int(num)})

        models_path = os.path.join(self.root_directory_path, "models.txt")
        with open(models_path, "r", encoding="utf-8") as f:
            model_lines = f.readlines()

        result = []
        for model_id, s in top_3:
            model_line = None
            for item in models_index:
                if item["key"] == str(model_id):
                    model_line = item["line"]
                    break

            raw = model_lines[model_line].strip()
            m_id, m_name, m_brand = raw.split(";", 2)
            result.append(ModelSaleStats(
                car_model_name=m_name,
                brand=m_brand,
                sales_number=s["count"],
            ))

        return result