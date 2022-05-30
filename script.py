import os

from rembg import remove
from PIL import Image, ImageChops


TEMPLATE_DIV = '''<div class="item">
            <img src="images/{name}">
            <div class="desc">
                <p>{dt}</p>
                <p>{title}</p>
            </div>
        </div>
        '''

TARGET_IMAGE_SIZE = 400


def genarate_content():
    content = ''
    images = os.listdir('images')
    segment_list = []
    for name in images:
        if '|' not in name:
            continue
        name = convert_image(name)
        dt, title = name.split('.')[0].split('|')
        dt = dt.replace('-', '/')
        title = title.replace(':', '/')
        content += TEMPLATE_DIV.format(name=name, dt=dt, title=title)
    return content

def convert_image(name):
    im = Image.open('images/%s' % name)
    name = name.split('.')[0]
    out_path = 'out/images/%s.png' % name
    im = remove(im)
    im = _crop_image(im)
    x, y = im.size
    if x <= TARGET_IMAGE_SIZE and y <= TARGET_IMAGE_SIZE:
        im.save(out_path, format='png')
    else:
        if x >= y:
            new_x = TARGET_IMAGE_SIZE
            new_y = y * new_x // x
        else:
            new_y = TARGET_IMAGE_SIZE
            new_x = x * new_y // y
        new_im = im.resize((new_x, new_y), resample=Image.LANCZOS)
        new_im.save(out_path, format='png')
    return '%s.png' % name

def _crop_image(img):
     bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
     diff = ImageChops.difference(img, bg)
     diff = ImageChops.add(diff, diff, 0.2, -100)
     bbox = diff.getbbox()
     if bbox:
         return img.crop(bbox)


if __name__ == '__main__':
    with open('templete.html', 'r') as f:
        html = f.read()

    with open('out/index.html', 'w') as f:
        f.write(html.replace('{content}', genarate_content()))
