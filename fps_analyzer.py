import json
import math

data = json.load(open("debug.json", "r"))


fpss = sorted([1 / value[1] for value in data["pygame"]])
lo_1 = fpss[:math.ceil(len(fpss) * .01)]
hi_1 = fpss[::-1][:math.ceil(len(fpss) * .01)]

av_fps = sum(fpss) / len(fpss)
lo_1_fps = sum(lo_1) / len(lo_1)
hi_1_fps = sum(hi_1) / len(hi_1)

print(f"""FPS Result ({len(fpss)} frames total):
Average: {round(av_fps, 2)}
1% low: {round(lo_1_fps, 2)}
1% high: {round(hi_1_fps, 2)}
""")
