import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv



headers = {"User-Agent": "Mozilla/5.0"}

def height_to_inches(height_str):
    feet, inches = height_str.strip().split("'")
    return int(feet) * 12 + int(inches.replace('"', '').strip())

def weight_to_int(weight_str):
    return int(weight_str.replace('lbs.', '').strip())

def reach_to_int(reach_str):
    return int(reach_str.replace('"', '').strip())

def date_to_age(birthdate_str):
    birth_date = datetime.strptime(birthdate_str, '%b %d, %Y')
    today = datetime(2025, 5, 29)
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def time_to_seconds(time_str):
    minutes, seconds = map(int, time_str.strip().split(':'))
    return minutes * 60 + seconds

def parse_record(record_str):
    wins, losses, draws = map(int, record_str.split('-'))
    return [wins, losses, draws]

def stance_to_int(stance):
    mapping = {'Orthodox': 0, 'Southpaw': 1, 'Switch': 2}
    return mapping.get(stance, -1)

def getmatchups(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("tr.js-fight-details-click")

    fight_links = []
    for row in rows:
        link = row.get("onclick")
        if link:
            url = link.split("'")[1]
            fight_links.append(url)

    fighter_links = []
    for a in soup.select("a.b-link.b-link_style_black[href^='http://ufcstats.com/fighter-details/']"):
        fighter_links.append(a["href"].strip())

    grouped = (fighter_links[i:i+2] for i in range(0, len(fighter_links), 2))

    return grouped

def parse_fighter(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    info_box = soup.select_one('.b-list__info-box-left')
    stats_box = soup.select_one('.b-list__info-box-right')

    if not info_box or not stats_box:
        print("[ERROR] Fighter info not found.")
        return None

    raw_data = {}
    for li in info_box.select('li'):
        if ':' in li.text:
            key, val = li.text.strip().split(':', 1)
            raw_data[key.strip()] = val.strip()

    for li in stats_box.select('li'):
        if ':' in li.text:
            key, val = li.text.strip().split(':', 1)
            raw_data[key.strip()] = val.strip()

    try:
        height = height_to_inches(raw_data.get('Height', "0' 0\""))
        weight = weight_to_int(raw_data.get('Weight', '0 lbs.'))
        reach = reach_to_int(raw_data.get('Reach', '0"'))
        stance = stance_to_int(raw_data.get('STANCE', 'Orthodox'))
        age = date_to_age(raw_data.get('DOB', 'Jan 1, 2000'))

        slpm = float(raw_data.get('SLpM', 0))
        str_acc = int(raw_data.get('Str. Acc.', '0').replace('%', ''))
        sapm = float(raw_data.get('SApM', 0))
        str_def = int(raw_data.get('Str. Def.', '0').replace('%', ''))
        td_avg = float(raw_data.get('TD Avg.', 0))
        td_acc = int(raw_data.get('TD Acc.', '0').replace('%', ''))
        td_def = int(raw_data.get('TD Def.', '0').replace('%', ''))
        sub_avg = float(raw_data.get('Sub. Avg.', 0))

        return [height, weight, reach, stance, age,
                slpm, str_acc, sapm, str_def,
                td_avg, td_acc, td_def, sub_avg]
    except Exception as e:
        print(f"[ERROR] Failed to parse: {e}")
        return None


# stats = messwithpart("http://ufcstats.com/event-details/2a898bf9fb7710b3")
# print(stats)
# testmatchup = [['http://ufcstats.com/fighter-details/480779d7f9a424d3', 'http://ufcstats.com/fighter-details/94426bb170c88115']]
matchups = getmatchups("http://ufcstats.com/event-details/8ad022dd81224f61")
data = []


for matchup in matchups:
    print(matchup)
    fightervector = []
    for fighter in matchup:
        vec = parse_fighter(fighter)
        if vec is None:
            break
        fightervector.append(vec)
    
    if len(fightervector) == 2:
        row = fightervector[0] + fightervector[1] + [1]
        data.append(row)
        reversed_row = fightervector[1] + fightervector[0] + [0]
        data.append(reversed_row)

header = [
    "height1", "weight1", "reach1", "stance1", "age1",
    "slpm1", "str_acc1", "sapm1", "str_def1",
    "td_avg1", "td_acc1", "td_def1", "sub_avg1",
    "height2", "weight2", "reach2", "stance2", "age2",
    "slpm2", "str_acc2", "sapm2", "str_def2",
    "td_avg2", "td_acc2", "td_def2", "sub_avg2",
    "result"
]
save_to_csv("training_dat.csv", data, header=header)
