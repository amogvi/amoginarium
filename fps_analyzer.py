import json

data = json.load(open("debug.json", "r"))


fpss = sorted([1 / value[1] for value in data["pygame"]])
lo_1 = fpss[:int(len(fpss) * .01)+1]
hi_1 = fpss[::-1][:int(len(fpss) * .01)+1]

av_fps = sum(fpss) / len(fpss)
lo_1_fps = sum(lo_1) / len(lo_1)
hi_1_fps = sum(hi_1) / len(hi_1)

print(f"""FPS Result:
Average: {round(av_fps, 2)}
1% low: {round(lo_1_fps, 2)}
1% high: {round(hi_1_fps, 2)}
""")
