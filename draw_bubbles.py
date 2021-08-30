import sys
from PIL import Image, ImageDraw, ImageFont
from string import ascii_uppercase

width = 200
height = 200
color_rgb = (255, 255, 255)
fnt = ImageFont.truetype("arial.ttf", 80)

#generates sprite imgs for part A
for i in range(25):
   img = Image.new(mode="RGB", size=(width, height), color=color_rgb)
   draw_object = ImageDraw.Draw(img)

   draw_object.arc([(3,3),(197,197)], 0, 360, fill=(0,0,0), width=10)
   draw_object.pieslice([(13,13),(187,187)], 0, 360, fill=(135,206,250), width=10)
   if i<9:
       draw_object.text((80, 60), f"{i+1}", fill=(0,0,0), font=fnt)
   else:
       draw_object.text((55, 60), f"{i+1}", fill=(0,0,0), font=fnt)

   img.save("bubble" + f"{i+1}" + "_hit" ".jpeg", "JPEG")


#generates Letter sprite imgs for part B:
# for i in range(12):
#     img = Image.new(mode="RGB", size=(width, height), color=color_rgb)
#     draw_object = ImageDraw.Draw(img)

#     draw_object.arc([(3,3),(197,197)], 0, 360, fill=(0,0,0), width=10)
#     draw_object.pieslice([(13,13),(187,187)], 0, 360, fill=(135,206,250), width=10)
#     draw_object.text((80, 60), f"{ascii_uppercase[i]}", fill=(0,0,0), font=fnt)

#     img.save("bubble" + f"{ascii_uppercase[i]}" + "_hit" + ".jpeg", "JPEG")
