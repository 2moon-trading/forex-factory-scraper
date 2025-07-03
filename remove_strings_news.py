import json

# El actual, previus y forecast deben ser floats
def _format_float(value):
    if value is None:
        return None
    try:
        """Format a value to float, returning None if the value is not a number."""
        value = str(value).strip().replace('<', '').replace('%', '').replace('>', '')

        partes = value.split("-")

        # Caso 2: "x-y" → si x no está vacío, devolver "0"
        if len(partes) == 2 and partes[0] != "":
            return "0"

        # Caso 3: "-x" → conservar
        if len(partes) == 2 and partes[0] == "":
            return value

        # Caso 1: "x-y-x..." → eliminar ceros y unir sin guiones
        if len(partes) >= 3:
            partes = [p for p in partes if p != "0"]
            if not partes:
                return "0"
            return "".join(partes)

        # Caso 4: si solo contiene ceros o está vacía
        if not partes or all(p == "0" for p in partes):
            return "0"

        # En cualquier otro caso (por si acaso)
        value = "".join(partes)

        value = value.replace('K', '000').replace('M', '000000').replace('B', '000000000').replace('T', '000000000000')
        value = value.replace('k', '000').replace('m', '000000').replace('b', '000000000').replace('t', '000000000000')
        return float(value)
    except ValueError as e:
        print(f"Error converting value '{value}' to float: {e}")
        exit

# Se debe poner la fecha (2020-12-17) de la noticia a dia ej, Monday, Tuesday, etc.
def _format_day(value):
    if value is None:
        return None
    try:
        """Format a date string to a day of the week."""
        from datetime import datetime
        date = datetime.strptime(value, '%Y-%m-%d')
        return date.strftime('%A')
    except ValueError as e:
        print(f"Error converting date '{value}' to day: {e}")
        exit

with open(f'noticias.json', 'r', encoding='utf-8') as file:
    news_old = json.load(file)
news_new = []

last_time = None

for new in news_old:
    # El actual, previus y forecast deben ser floats
    actual = new.get('actual', None)
    actual = _format_float(actual)
    new['actual'] = actual

    previous = new.get('previous', None)
    previous = _format_float(previous)
    new['previous'] = previous

    forecast = new.get('forecast', None)
    forecast = _format_float(forecast)
    new['forecast'] = forecast

    # Se debe poner la fecha (2020-12-17) de la noticia a dia ej, Monday, Tuesday, etc.
    date = new.get('date', None)
    day = _format_day(date)
    new['day'] = day

    # Si la noticia no tiene hora, se pone la hora de la noticia anterior
    time = new.get('time', None)
    if time is None or time == '':
        time = last_time
    else:
        last_time = time
    new['time'] = time

    news_new.append(new)

with open("news_new.json", "w", encoding="utf-8") as file:
    json.dump(news_new, file, indent=4, ensure_ascii=False)

