def for_fusion(date):
    day = date.strftime("%-d")
    month = date.strftime("%b")
    year = date.strftime("%Y")
    return f"{month} {day}, {year}"

def for_sms(date):
    weekday = date.strftime("%A")
    month = date.strftime("%B")
    day = date.strftime("%-d")
    return f"{weekday}, {month} {day}"