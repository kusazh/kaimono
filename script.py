import os

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
    for path in images:
        if '|' not in path:
            continue
        path = resize_image(path)
        dt, title = path.split('.')[0].split('|')
        dt = dt.replace('-', '/')
        title = title.replace(':', '/')
        content += TEMPLATE_DIV.format(path=path, dt=dt, title=title)
    return content

def resize_image(path):
    name = path.split('.')[0]
    im = Image.open('images/%s' % path)
    x, y = im.size
    if x <= TARGET_IMAGE_SIZE and y <= TARGET_IMAGE_SIZE:
        im.save('out/images/%s.png' % name, format='png')
        return '%s.png' % name
    if x >= y:
        new_x = TARGET_IMAGE_SIZE
        new_y = y * new_x // x
    else:
        new_y = TARGET_IMAGE_SIZE
        new_x = x * new_y // y
    new_im = im.resize((new_x, new_y), resample=Image.LANCZOS)
    new_im.save('out/images/%s.png' % name, format='png')
    return '%s.png' % name

if __name__ == '__main__':
    with open('templete.html', 'r') as f:
        html = f.read()

    with open('out/index.html', 'w') as f:
        f.write(html.replace('{content}', genarate_content()))
