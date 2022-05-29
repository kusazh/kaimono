import os

import cv2
import numpy as np
from PIL import Image


TEMPLATE_DIV = '''<div class="item">
            <img src="images/{path}">
            <div class="desc">
                <p>{dt}</p>
                <p>{title}</p>
            </div>
        </div>
        '''

TARGET_IMAGE_SIZE = 250


def genarate_content():
    content = ''
    images = os.listdir('images')
    segment_list = []
    for path in images:
        if '|' not in path:
            continue
        path = convert_image(path)
        dt, title = path.split('.')[0].split('|')
        dt = dt.replace('-', '/')
        title = title.replace(':', '/')
        content += TEMPLATE_DIV.format(path=path, dt=dt, title=title)
    return content

def convert_image(path):
    name = path.split('.')[0]
    im = Image.open('images/%s' % path)
    x, y = im.size
    if x <= TARGET_IMAGE_SIZE and y <= TARGET_IMAGE_SIZE:
        im.save('out/images/%s.png' % name, format='png')
        path = '%s.png' % name
    if x >= y:
        new_x = TARGET_IMAGE_SIZE
        new_y = y * new_x // x
    else:
        new_y = TARGET_IMAGE_SIZE
        new_x = x * new_y // y
    new_im = im.resize((new_x, new_y), resample=Image.LANCZOS)
    new_im.save('out/images/%s.png' % name, format='png')
    path = '%s.png' % name
    if im.mode != 'RGBA':
        segment_image(path)
    return path

def segment_image(path):
    '''
    refer to: https://stackoverflow.com/a/63003020
    '''

    # load image
    img = cv2.imread('out/images/' + path)

    # convert to graky
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # threshold input image as mask
    mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)[1]

    # negate mask
    mask = 255 - mask

    # apply morphology to remove isolated extraneous noise
    # use borderconstant of black since foreground touches the edges
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # anti-alias the mask -- blur then stretch
    # blur alpha channel
    mask = cv2.GaussianBlur(mask, (0,0), sigmaX=2, sigmaY=2, borderType = cv2.BORDER_DEFAULT)

    # linear stretch so that 127.5 goes to 0, but 255 stays 255
    mask = (2*(mask.astype(np.float32))-255.0).clip(0,255).astype(np.uint8)

    # put mask into alpha channel
    result = img.copy()
    result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = mask

    # save resulting masked image
    cv2.imwrite('out/images/' + path, result)


if __name__ == '__main__':
    with open('templete.html', 'r') as f:
        html = f.read()

    with open('out/index.html', 'w') as f:
        f.write(html.replace('{content}', genarate_content()))
