from random import randrange
import json
import math
import sys

e = open("events.json")
p = open("players.json")
events = json.load(e)
players = json.load(p)
e.close()
p.close()

for player in players:
  player["kills"] = 0
  for bond in players:
    if not (player["name"] == bond["name"] or bond["name"] in player["bond"]):
      player["bond"][bond["name"]] = 0

class Event:
  def __init__(self, number, t, text, conditional, bond_conditional, player_conditional, injury, killer, killed, items, bond, count):
    self.tributes = number
    self.t = t
    self.text = text
    self.conditional = conditional
    self.bond_conditional = bond_conditional
    self.player_conditional = player_conditional
    self.injury = injury
    self.killer = killer
    self.killed = killed
    self.items = items
    self.bond = bond
    self.count = count

alive = players[:]
involved = []
day = 1

delay = True

def find_acceptable_events(temp_players, involved):

  def combine_matches(event, a, b):
    combined = []
    for g in range(event.tributes - 1):
      if a == "-" or a[g] == "-":
        if b == "-" or b[g] == "-":
          combined.append("-")
        else:
          combined.append(b[g])
      else:
        if b == "-" or b[g] == "-":
          combined.append(a[g])
        else:
          combined.append([val for val in a[g] if val in b[g]])
    return combined[:]
  
  def combine_lists(a, b):
    if a == "-":
      if b == "-":
        return "-"
      else:
        return b
    else:
      if b == "-":
        return a
      else:
        return [val for val in a if val in b]

  def conditional_valid(compare, a, b):
    if compare == "==":
      return a == b
    if compare == ">":
      return a > b
    if compare == "<":
      return a < b
    if compare == ">=":
      return a >= b
    if compare == "<=":
      return a <= b
    if compare == "contains":
      return b in a
    if compare == "notContains":
      return not b in a

  acceptable_events = []
  player_matches = []

  for ev in events:

    event = Event(ev["#"], ev["t"], ev["text"], ev.get("conditional"), ev.get("bondConditional"),
      ev.get("playerConditional"), ev.get("injury"), ev.get("killer"), ev.get("killed"),
      ev.get("items"), ev.get("bond"), ev.get("count"))

    if len(temp_players) + 1 < event.tributes:
      continue
    
    if day % 2 == 1:
      if event.t[0] == "0":
        continue
    else:
      if event.t[1] == "0":
        continue

    # conditional events

    passes_conditional = True
    if event.conditional is not None:
      for conditional in event.conditional:
        if conditional[0] == "day":
          if not conditional_valid(conditional[1], day, conditional[2]):
            passes_conditional = False
        elif conditional[0] == "alive":
          if not conditional_valid(conditional[1], len(alive), conditional[2]):
            passes_conditional = False

    if event.player_conditional is not None:
      for conditional in event.player_conditional[0]:
        if conditional[0] == "bondTotal":
          if not conditional_valid(conditional[1], sum(involved[0]["bond"].values()), conditional[2]):
            passes_conditional = False
        else:
          if not conditional_valid(conditional[1], involved[0][conditional[0]], conditional[2]):
            passes_conditional = False
        
    if not passes_conditional:
      continue

    # fatal events

    if event.killed is not None:
      if 1 in event.killer:
        if involved[0]["pacifist"]:
          continue
    
    # item events

    if event.items is not None:
      a = True
      for item in event.items:
        if 1 in item["lose"] and not item["item"] in involved[0]["items"]:
          a = False
      if not a:
        continue
    
    # find player matches

    conditional_matches = "-"
    bond_matches = "-"
    item_matches = "-"

    if event.tributes > 1:
      if event.player_conditional is not None:
        conditional_matches = []
        for n in range(2, event.tributes + 1):
          number_matches = []
          for player in temp_players:
            a = True
            for conditional in event.player_conditional[n - 1]:
              if conditional[0] == "bondTotal":
                if not conditional_valid(sum(player["bond"].values())):
                  a = False
              else:
                if not conditional_valid(conditional[1], player[conditional[0]], conditional[2]):
                  a = False
            if a: number_matches.append(player)
          conditional_matches.append(number_matches)
        if [] in conditional_matches:
          continue

      if event.bond_conditional is not None:
        bond_matches = []
        for n in range(2, event.tributes + 1): 
          number_matches = []
          for player in temp_players:
            a = True
            for conditional in event.bond_conditional:
              if n == conditional[0]:
                if not conditional_valid(conditional[1], involved[0]["bond"][player["name"]], conditional[2]):
                  a = False
            if a: number_matches.append(player)
          bond_matches.append(number_matches)
        if [] in bond_matches:
          continue

      if event.items is not None:
        item_matches = []
        for n in range(2, event.tributes + 1):
          number_matches = []
          for player in temp_players:
            a = True
            for item in event.items:
              if len(item["lose"]) > 0:
                if len(item["lose"]) > 1 or not 1 in item["lose"]:
                  if n in item["lose"]:
                    if item["lose"].count(n) > player["items"].count(item["item"]):
                      a = False
            if a: number_matches.append(player)
          item_matches.append(number_matches)
        if [] in item_matches:
          continue
    
    # combine player matches

    combined_a = combine_matches(event, conditional_matches, bond_matches)
    combined = combine_matches(event, item_matches, combined_a)

    if [] in combined:
      continue

    total = "-"
    for n in combined:
      total = combine_lists(total, n if type(n) is list else "-")
    if total == "-":
      total = temp_players
    if 1 < len(total) < event.tributes:
      continue

    count = event.count if event.count is not None else 1

    for c in range(count):
      player_matches.append(combined)
      acceptable_events.append(event)
  
  return acceptable_events, player_matches

def print_message(event):
  message = event.text

  message = message.replace("{i:", "\u001b[38;5;214m")
  message = message.replace("{h:", "\u001b[38;5;62;1m")

  for num in range(len(involved)):
    if event.killed is not None and num + 1 in event.killed:
      message = message.replace(f"{{name{num + 1}}}", ("\u001b[38;5;203m" + involved[num]["name"] + "\u001b[0m"))
    else:
      message = message.replace(f"{{name{num + 1}}}", ("\u001b[38;5;122m" + involved[num]["name"] + "\u001b[0m"))
    if involved[num]["gender"] == "M":
      message = message.replace(f"{{he/she{num + 1}}}", "he")
      message = message.replace(f"{{He/She{num + 1}}}", "He")
      message = message.replace(f"{{his/her{num + 1}}}", "his")
      message = message.replace(f"{{His/Her{num + 1}}}", "His")
      message = message.replace(f"{{him/her{num + 1}}}", "him")
      message = message.replace(f"{{himself/herself{num + 1}}}", "himself")
    elif involved[num]["gender"] == "F":
      message = message.replace(f"{{he/she{num + 1}}}", "she")
      message = message.replace(f"{{He/She{num + 1}}}", "She")
      message = message.replace(f"{{his/her{num + 1}}}", "her")
      message = message.replace(f"{{His/Her{num + 1}}}", "Her")
      message = message.replace(f"{{him/her{num + 1}}}", "her")
      message = message.replace(f"{{himself/herself{num + 1}}}", "herself")
          
  message = message.replace("}", "\u001b[0m")

  print(message)

rank = []

while len(alive) > 1:
  print("\u001b[38;5;62;1m", end="")
  print(f"{'DAY' if day % 2 == 1 else 'NIGHT'} {math.ceil(day / 2) if day % 2 == 1 else day // 2}")
  print("\u001b[0m", end="")

  temp_players = alive[:]

  while not len(temp_players) == 0:

    # choose a player and create event list

    involved.clear()
    involved.append(temp_players.pop(randrange(0, len(temp_players))))

    accepted_events, player_matches = find_acceptable_events(temp_players, involved)
    if len(accepted_events) == 0:
      print("There are no events that meet the criteria.")
      sys.exit()
    
    event = accepted_events[randrange(0, len(accepted_events))]

    matches = []
    for match in player_matches[accepted_events.index(event)]:
      if match == "-":
        matches.append(temp_players[:])
      else:
        matches.append(match)
    
    # choose other players and print event

    for g in range(event.tributes - 1):
      tribute = matches[g][randrange(0, len(matches[g]))]
      while tribute in involved:
        tribute = matches[g][randrange(0, len(matches[g]))]
      m = matches[g].pop(matches[g].index(tribute))
      involved.append(temp_players.pop(temp_players.index(m)))

    print_message(event)

    # list changes

    if event.items is not None:
      for player in involved:
        for item in event.items:
          for lose in item["lose"]:
            if lose == involved.index(player) + 1:
              players[players.index(player)]["items"].remove(item["item"])
          for gain in item["gain"]:
            if gain == involved.index(player) + 1:
              players[players.index(player)]["items"].append(item["item"])
    
    if event.injury is not None:
      for i in range(len(involved)):
        players[players.index(involved[i])]["injury"] += event.injury[i]
    
    if event.bond is not None:
      for i in range(len(involved)):
        b = event.bond[i]
        for h in range(len(involved)):
          if str(h + 1) in b:
            if type(b[str(h + 1)]) is int:
              players[players.index(involved[i])]["bond"][involved[h]["name"]] = b[str(h + 1)]
            elif type(b[str(h + 1)]) is str:
              players[players.index(involved[i])]["bond"][involved[h]["name"]] += int(b[str(h + 1)])

    if event.killed is not None:
      for i in range(len(involved)):
        if i + 1 in event.killer:
          players[players.index(involved[i])]["kills"] += len(event.killed)
        if i + 1 in event.killed:
          rank.insert(0, alive[alive.index(involved[i])]["name"])
          alive.pop(alive.index(involved[i]))
    
    if len(alive) <= 1:
      break
  
  # delay

  day += 1
  if delay and len(alive) > 1:
    input("")
    print("\033[F\033[2K")
  else:
    print("")

if len(alive) == 1: rank.insert(0, alive[0]["name"])

print("\u001b[38;5;62;1m", end="")
print(f"{alive[0]['name']} is the victor!" if len(alive) == 1 else "There is no victor. Everyone died.")
print("")

max_name_length = 6
for player in players:
  max_name_length = max(max_name_length, len(player["name"]))

typed = ""
print("(default, rank, name, kills, items, or injury)")
while not typed in ["default", "rank", "name", "kills", "items", "injury"]:
  typed = input("SORT BY: ")
  print("\033[F\033[2K", end="")
print("\033[F\033[2K(yes/y to accept)")
print_items = input("PRINT ITEMS? ")
print("\033[F\033[2K\033[F\033[2K", end="")

# sort players

if not typed == "default":
  if typed == "name":
    players.sort(reverse=False, key=lambda x : x["name"])
  elif typed == "rank":
    players.sort(reverse=False, key=lambda x : rank.index(x["name"]))
  elif typed == "kills":
    players.sort(reverse=True, key=lambda x : x["kills"])
  elif typed == "items":
    players.sort(reverse=True, key=lambda x : len(x["items"]))
  elif typed == "injury":
    players.sort(reverse=False, key=lambda x : x["injury"])

# print stats

print(f"NAME\033[{max_name_length - 2}CRANK\033[2CKILLS\033[2CINJURY\033[2CITEMS\u001b[0m")
for player in players:
  print(
    f"{player['name']}\033[{max_name_length + 2 - len(player['name'])}C" + 
    f"{rank.index(player['name']) + 1}\033[{6 - len(str(rank.index(player['name']) + 1))}C" +
    f"{player['kills']}\033[{7 - len(str(player['kills']))}C" + 
    f"{player['injury']}\033[{8 - len(str(player['injury']))}C" +
    f"{len(player['items'])}" + 
    f"{': ' + ', '.join(player['items']) if print_items.lower() in ['y', 'yes'] else ''}"
  )