"""
debug_analyzer.py
25. January 2024

Analyzes the runtimes of amoginatorium

Author:
Nilusink
"""
import matplotlib.pyplot as plt
import json

red = 'tab:red'
data = json.load(open("debug.json", "r"))

pygame_xs = []
pygame_ys = []
for value in data["pygame"]:
    pygame_xs.append(value[0])
    pygame_ys.append(value[1] * 1000)


logic_xs = []
logic_ys = []
# anything before 2 gives weiredly high results
for value in data["logic"][2:]:
    logic_xs.append(value[0])
    logic_ys.append(value[1] * 1000)


comms_xs = []
comms_ys = []
for value in data["comms"]:
    comms_xs.append(value[0])
    comms_ys.append(value[1] * 1000)


bullets_xs = []
n_bullets = []
bullets_ys = []
for value in data["bullets"]:
    bullets_xs.append(value[0])
    n_bullets.append(value[1])
    y_val = value[2]
    if y_val is not None:
        y_val *= 1000
    bullets_ys.append(y_val)

# calculate average loop time per bullet
av_bullets_ys_tmp = [None] * (max(n_bullets) + 1)
for n_bullet, loop_time in zip(n_bullets, bullets_ys):
    if av_bullets_ys_tmp[n_bullet] is None:
        av_bullets_ys_tmp[n_bullet] = []

    av_bullets_ys_tmp[n_bullet].append(loop_time)

av_bullet_ys: list[float] = [None] * (max(n_bullets) + 1)
for n_bullet in range(len(av_bullets_ys_tmp)):
    times = av_bullets_ys_tmp[n_bullet]

    if len(times) > 0:
        av = sum(times) / len(times)
        print(f"\n\n{n_bullet}:\t", times, av)
        av_bullet_ys[n_bullet] = av

# print(av_bullets_ys_tmp)
print(av_bullet_ys)


ax1 = plt.subplot(2, 1, 1)
ax2 = plt.subplot(2, 1, 2)

# per bullet
ax2.scatter(n_bullets, bullets_ys, label="loop times")
ax2.plot(
    list(range(len(av_bullet_ys))),
    av_bullet_ys,
    label="average",
    color=red
)
ax2.set_xlabel("n (bullets)")
ax2.set_ylabel("t per iteration (ms)")
ax2.legend()
ax2.grid()

ax1.plot(pygame_xs, pygame_ys, label="pygame")
ax1.plot(logic_xs, logic_ys, label="logic")
ax1.plot(comms_xs, comms_ys, label="comms")

ax1.set_xlabel("time since start in s")
ax1.set_ylabel("loop time in ms")
ax1.legend()
ax1.grid()

ax1_1 = ax1.twinx()

ax1_1.set_ylabel('n (bullets)', color=red)
ax1_1.plot(bullets_xs, n_bullets, color=red, label="n bullets")
ax1_1.tick_params(axis='y', labelcolor=red)


plt.tight_layout()
plt.show()
