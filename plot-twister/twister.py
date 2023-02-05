import sys
import time

builtins = ["-123", "-abc", "-b", "-back", "-r", "-restart", "-d", "-debug", "-q", "-quit", "-⌯"]
symbols = [">", "<", "-", "_", "~", "+", "=", ".", " ", ","]
errors = []
progression = []
options = []
message = []
typed = ""
lower = ""
response = ""
mode = "text"

# format vars

S = 1
M = 4

# find file

try:
	story = sys.argv[1]
except IndexError:
	story = input("load file: ")

try:
	with open(story) as test:
		test.close()
except FileNotFoundError:
	try:
		with open(f"{story}.txt") as test2:
			test2.close()
	except FileNotFoundError:
		print(f"couldn't load {story}")
		sys.exit()
	else:
		story = f"{story}.txt"

# read file

with open(story) as file:
	temp = file.readlines()
	temp = [line.rstrip("\n") for line in temp]
	indents = []
	full = []
	for i in range(len(temp)):
		c = 0
		while temp[i][c] == "\t":
			c += 1
		indents.append(c)
		full.append(temp[i][c:])
	file.close()

print(f"successfully loaded {story}")
print("")

# find the most recent choice

# number = indentation level
# start = place in the list (full)

def choice(number, start):
	i = start
	while not (indents[i] == int(number) - 1 and full[i][S] == "="):
		i -= 1
		if i == 0:
			sys.exit("something's broken\n")
	return full[i - 1][M:].lower()

# create a list of options

def load_options():
	options.clear()
	for i in range(len(full)):
		line = full[i]
		if full[i][0] == " ":
			errors.append(f"indent")
		elif not full[i][S] in symbols:
			errors.append(f"s{line[S]}{i + 1}")
		elif not (full[i][S - 1] == "[" and full[i][S + 1] == "]"):
			errors.append(f"b{i + 1}")
		if (line[S] == ">" or line[S] == "<") and (indents[i] == len(progression)):
			if (len(progression) == 0) or progression[-1] == choice(indents[i], i):
				options.append({
					"lower": line[M:].lower(),
					"real": line[M:],
					"type": line[S],
					"result": full[i + 1][S],
					"line": (i + 1)
				})

# before mainloop

load_options()
print("Look in the \"Plot Twister\" section of README.md for the rules.")
print("")
if len(errors) >= 1:
	print(f"I found some errors in {story}:")
	for m in range(len(errors)):
		if "indent" in errors:
			print(" • use tabs instead of spaces for indentation")
			print("")
			sys.exit()
		elif errors[m][0] == "s":
			print(f" • line {errors[m][2:]} - I don't know what \"{errors[m][1]}\" means")
		elif errors[m][0] == "b":
			print(f" • line {errors[m][1:]} - I expect square brackets before and after the symbol")
	print("")
	sys.exit()
start_key = options[0]["real"]
print(f"Type '{start_key}' to start game")

# print the list of options

def print_options(type):
	display = []
	for i in range(len(options)):
		if options[i]["type"] == type:
			display.append(options[i]["real"])
	if len(display) > 0:
		print(f"[{', '.join(display)}]")

# loop

while not options == []:
	typed = ""
	lower = ""
	response = ""
	load_options()
	if options == []:
		sys.exit()

	accepted = False

	while not accepted:
		if not len(progression) == 0:
			print_options(">")

		typed = input("> ")
		lower = typed.lower()
		if mode == "number":
			if typed.isdigit():
				if int(typed) > 0 and int(typed) <= len(options):
					response = options[int(typed) - 1]["lower"]
				else:
					response = ""
			else:
				response = ""
				if not lower in builtins:
					print("")
					print("please enter a valid number")
					print("")
		elif mode == "text":
			response = lower

		for h in range(len(options)):
			if response == options[h]["lower"]:
				number = h
				accepted = True

		if len(progression) == 0:
			if not accepted:
				if not (response == "-q" or response == "-quit"):
					print(f"Type '{start_key}' to start game")

		# builtins

		def debug():
			print("")
			for o in range(len(options)):
				print("command:", options[o]["real"])
				print("type:", options[o]["type"])
				print("result:", options[o]["result"])
				print("line", options[o]["line"])
				print("")

		if lower in builtins:
			if len(progression) > 0:
				if lower == "-a":
					mode = "text"
					print("switched to text mode")
					print("")
				elif lower == "-#":
					mode = "number"
					print("switched to number mode")
					print("")
			if lower == "-b" or lower == "-back":
				if not len(progression) == 0:
					if len(progression) > 1:
						del progression[-1]
						print("")
						break
					else:
						print("")
						print("Nothing to go back to.")
						print("")
			elif lower == "-r" or lower == "-restart":
				if not len(progression) == 0:
					progression.clear()
					progression.append(full[0][M:])
					print("")
					print(full[1][M:])
					print("")
					load_options()
			elif lower == "-d" or lower == "-debug":
				debug()
			elif lower == "-q" or lower == "-quit":
				print("")
				print("game quit")
				sys.exit()
			elif lower == "-⌯":
				print_options("<")

	# message

	if not lower in builtins:
		progression.append(response)
		# time.sleep(0.3)
		print("")

		def load_message():
			choice = options[number]["line"] - 1
			message.clear()
			scanning = True
			x = 1
			while scanning:
				if len(full) == choice + x:
					return
				if full[choice + x][S] == ">":
					return
				message.append(full[choice + x])
				x += 1

		def print_message():
			for i in range(len(message)):
				if message[i][S] == ".":
					input("...")
					print("\033[A                                                      \033[A")
				if message[i][S] == ",":
					time.sleep(0.1)
				print(message[i][M:])

		if options[number]["result"] == "-":
			del progression[-1]
			print("FAIL")
		elif options[number]["result"] == "~":
			del progression[-1]
		load_message()
		print_message()
		if options[number]["result"] == "_":
			del progression[-1]
			print("FAIL")
		print("")
		time.sleep(0.3)
