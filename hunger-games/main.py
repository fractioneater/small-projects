from random import randrange
import json
import math
import re
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
        return "-" # Any, Any
      else:
        return b # Any, Constrained
    else:
      if b == "-":
        return a # Constrained, Any
      else:
        return [val for val in a if val in b] # Constrained, Constrained

  def conditional_valid(compare, a, b):
    if compare == "==": return a == b
    if compare == ">": return a > b
    if compare == "<": return a < b
    if compare == ">=": return a >= b
    if compare == "<=": return a <= b
    if compare == "contains": return b in a
    if compare == "notContains": return not b in a

  acceptable_events = []
  player_matches = []

  for ev in events:
    event = Event(ev["#"], ev["t"], ev["text"], ev.get("conditional"), ev.get("bondConditional"),
      ev.get("playerConditional"), ev.get("injury"), ev.get("killer"), ev.get("killed"),
      ev.get("items"), ev.get("bond"), ev.get("count"))

    # If there aren't enough players for the event, move on.
    if len(temp_players) + 1 < event.tributes:
      continue
    
    # If it's the wrong time of day, move on.
    if day % 2 == 1:
      if event.t[0] == "0": continue
    else:
      if event.t[1] == "0": continue

    # CONDITIONAL EVENTS

    if event.conditional is not None:
      ok = True
      # If any of the conditionals is not satisfied, the event won't work.
      for conditional in event.conditional:
        if conditional[0] == "day":
          if not conditional_valid(conditional[1], day, conditional[2]):
            ok = False; break
        elif conditional[0] == "alive":
          if not conditional_valid(conditional[1], len(alive), conditional[2]):
            ok = False; break
      
      if not ok: continue

    if event.player_conditional is not None:
      ok = True
      # If any of the randomly chosen player's characteristics don't meet the conditions, move on.
      for conditional in event.player_conditional[0]:
        if conditional[0] == "bondTotal":
          if not conditional_valid(conditional[1], sum(involved[0]["bond"].values()), conditional[2]):
            ok = False; break
        else:
          if not conditional_valid(conditional[1], involved[0][conditional[0]], conditional[2]):
            ok = False; break
        
      if not ok: continue

    # FATAL EVENTS

    # If the killer is a pacifist, discard the event.
    if event.killed is not None:
      if 1 in event.killer and involved[0]["pacifist"]:
        continue
    
    # ITEM EVENTS

    # If the player is losing an item that they don't have, that's not good.
    if event.items is not None:
      ok = True
      for item_name, item in event.items.items():
        if 1 in item["lose"] and not item_name in involved[0]["items"]:
          ok = False; break
      if not ok: continue
    
    # FIND PLAYER MATCHES

    # "-" means that any player could fill the slot.
    conditional_matches = "-"
    bond_matches = "-"
    item_matches = "-"

    if event.tributes > 1:
      if event.player_conditional is not None:
        conditional_matches = []
        for n in range(2, event.tributes + 1):
          number_matches = []
          for player in temp_players:
            # Each player slot has their own conditionals, so only the slot being filled matters.
            for conditional in event.player_conditional[n - 1]:
              if conditional[0] == "bondTotal":
                if not conditional_valid(sum(player["bond"].values())):
                  break
              else:
                if not conditional_valid(conditional[1], player[conditional[0]], conditional[2]):
                  break
            else: number_matches.append(player)
          conditional_matches.append(number_matches)
        if [] in conditional_matches: continue

      if event.bond_conditional is not None:
        bond_matches = []
        for n in range(2, event.tributes + 1): 
          number_matches = []
          for player in temp_players:
            for conditional in event.bond_conditional:
              # Only check the conditional if the bond applies to the player slot being filled.
              if n == conditional[0]:
                if not conditional_valid(conditional[1], involved[0]["bond"][player["name"]], conditional[2]):
                  break
            else: number_matches.append(player)
          bond_matches.append(number_matches)
        if [] in bond_matches: continue

      if event.items is not None:
        item_matches = []
        # Find which players can fill each slot needed for the event.
        for n in range(2, event.tributes + 1):
          number_matches = []
          for player in temp_players:
            for item_name, item in event.items.items():
              if n in item["lose"]:
                # If that slot loses the item more times than the player has it,
                # that player won't work for that slot.
                if item["lose"].count(n) > player["items"].count(item_name):
                  break
            else: number_matches.append(player)
          item_matches.append(number_matches)
        if [] in item_matches: continue
    
    # COMBINE PLAYER MATCHES

    combined_a = combine_matches(event, conditional_matches, bond_matches)
    combined = combine_matches(event, item_matches, combined_a)

    if [] in combined: continue

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

    # Replace all pronoun placeholders like "{he/she1}" with the proper pronoun.
    message = re.sub(r"\{([A-Za-z]*)/([A-Za-z]*)" + str(num + 1) + r"\}", r"\1" if involved[num]["gender"] == "M" else r"\2", message)

  message = message.replace("}", "\u001b[0m")

  print(message)

rank = []

while len(alive) > 1:
  print("\u001b[38;5;62;1m", end="")
  print(f"{'DAY' if day % 2 == 1 else 'NIGHT'} {math.ceil(day / 2) if day % 2 == 1 else day // 2}")
  print("\u001b[0m", end="")

  temp_players = alive[:]

  while not len(temp_players) == 0:

    # Choose a player and create a list of events based on that player's status.

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
    
    # Pick the other players from the matches and print out the event.

    for g in range(event.tributes - 1):
      tribute = matches[g][randrange(0, len(matches[g]))]
      while tribute in involved:
        tribute = matches[g][randrange(0, len(matches[g]))]
      m = matches[g].pop(matches[g].index(tribute))
      involved.append(temp_players.pop(temp_players.index(m)))

    print_message(event)

    # Make changes to the player's status based on the event.

    if event.items is not None:
      for player in involved:
        for item_name, item in event.items.items():
          for lose in item["lose"]:
            if lose == involved.index(player) + 1:
              players[players.index(player)]["items"].remove(item_name)
          for gain in item["gain"]:
            if gain == involved.index(player) + 1:
              players[players.index(player)]["items"].append(item_name)
    
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
    
    if len(alive) <= 1: break
  
  day += 1

  # Wait for the user to click enter before advancing.
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
print("(original, rank, name, kills, items, or injury)")
while not typed in ["original", "rank", "name", "kills", "items", "injury"]:
  typed = input("SORT BY: ")
  if typed == "": typed = "rank"
  print("\033[F\033[2K", end="")
print("\033[F\033[2K(yes/y to accept)")
print_items = input("PRINT ITEMS? ")
print("\033[F\033[2K\033[F\033[2K", end="")

# Sort the players
if not typed == "original":
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

# Print out the stats
print(f"NAME\033[{max_name_length - 2}CRANK\033[2CKILLS\033[2CINJURY\033[2CITEMS\u001b[0m")
for player in players:
  print(
    f"{player['name']}\033[{max_name_length + 2 - len(player['name'])}C" + 
    f"{rank.index(player['name']) + 1}\033[{6 - len(str(rank.index(player['name']) + 1))}C" +
    f"{player['kills']}\033[{7 - len(str(player['kills']))}C" + 
    f"{player['injury']}\033[{8 - len(str(player['injury']))}C" +
    f"{', '.join(player['items']) if print_items.lower() in ['y', 'yes'] else len(player['items'])}"
  )
