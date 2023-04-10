#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class User(object):

    def __init__(self, pseudo):
        self.pseudo = pseudo
        self.history = []
        self.myCaps = []


    def __repr__(self):
        return(f'{self.pseudo} is drunk with {len(self.history)} beers')


    def get_beers(self):
        return(self.history)


    def new_drink(self, new):
        self.history.append(new)
        if new.got_cap(): self.myCaps.append(new.beer)
        return(self.history)


    def banner(self):
        pass


    def stats(self, year=False):
        if year:
            styles = set([i.style for i in self.history])
            return(f'Last year stats : {len(self.history)} beers | {len(styles)} styles | {len(self.myCaps)} caps')
        else: 
            styles = set([i.style for i in self.history])
            return(f'Global stats : {len(self.history)} beers | {len(styles)} styles | {len(self.myCaps)} caps')


    def generate_banner(self, text='Beers I drank:\n\n- Heineken (Netherlands, 2022-03-31)\n- Guinness (Ireland, 2022-03-30)\n- Chimay (Belgium, 2022-03-29)'):
        bg_img = Image.open('banner_background.jpeg')
        bg_width, bg_height = bg_img.size
        bg_img = bg_img.resize((bg_width*3, bg_height*3))
        
        img = Image.new('RGB', (bg_img.size), color='white')
        img.paste(bg_img, (0, 0))
        font = ImageFont.truetype('arial.ttf', size=30)
        bold_font = ImageFont.truetype('arialbd.ttf', size=30)
        draw = ImageDraw.Draw(img)
        text_size = draw.textsize(text, font=font)

        x = 50
        y = (bg_height - text_size[1]) // 2 + 80

        lines = text.split('\n')
        for line in lines:
            if 'Beers I drank' in line or '-' not in line:
                draw.text((x, y), line, font=font, fill='#F7C331')
            else:
                draw.text((x, y+20), line, font=bold_font, fill='white')
            y += font.getsize(line)[1]

        user_font = ImageFont.truetype('arial.ttf', size=40)
        user_text_size = draw.textsize(self.pseudo, font=user_font)
        user_x = 50
        user_y = bg_height*3 - user_text_size[1] - 50
        draw.text((user_x, user_y), self.pseudo, font=user_font, fill='#F7C331')

        #img.save('beers.png')
        return(img)



class Degustation(object):
    def __init__(self, title, beer, style, loc=None, rating=None, comments=None, media=None, cap=False, quantity=1):
        self.time = datetime.now()
        self.style = style
        self.title = title
        self.beer = beer
        self.loc = loc
        self.rating = rating
        self.comments = comments
        self.media = media
        self.cap=cap
        self.quantity=quantity

    def __repr__(self):
        return(f'Enjoying a good {self.beer} under the sun {self.time}')

    def got_cap(self):
        return(self.cap)