"""
debug_analyzer.py
25. January 2024

Analyzes the runtimes of amoginatorium

Author:
Nilusink
"""
import matplotlib.pyplot as plt
import json


data = json.load(open("debug.json", "r"))

pygame_xs = []
pygame_ys = []
for value in data["pygame"]:
    pygame_xs.append(value[0])
    pygame_ys.append(value[1] * 1000)


logic_xs = []
logic_ys = []
for value in data["logic"][2:]:  # anything before 2 gives weiredly high results
    logic_xs.append(value[0])
    logic_ys.append(value[1] * 1000)


comms_xs = []
comms_ys = []
for value in data["comms"]:
    comms_xs.append(value[0])
    comms_ys.append(value[1] * 1000)

plt.plot(pygame_xs, pygame_ys, label="pygame")
plt.plot(logic_xs, logic_ys, label="logic")
plt.plot(comms_xs, comms_ys, label="comms")

plt.legend()
plt.xlabel("time since start in s")
plt.ylabel("loop time in ms")

plt.show()