import os.path, pygame
from pygame.locals import RLEACCEL


#return loaded img surface and its rect 
def load_image(name, destsize):
    fullname = os.path.join("img/", name)
    try:
        image = pygame.image.load(fullname)
    except: 
        pygame.error
        print("Cannot load image: ", fullname)
        raise SystemExit
    image = image.convert()
    colorkey = image.get_at((0,0)) #the color of top left pixel is considered the transparent color 
    image.set_colorkey(colorkey, RLEACCEL)
    image = pygame.transform.scale(image, destsize)

    return image, image.get_rect()


# matrix transposition: return matrix_transpose(a)
def matrix_transpose(a):
    assert(a[0] and a)
    return [[a[i][j] for i in range(len(a))] for j in range(len(a[0]))]

# from a string "aaa, bbb, ccc", return the int list [aaa, bbb, ccc] that can be used as a color
def color_from_string(str):
    rgb = str.split(',')
    assert(len(rgb) == 3)
    assert(((int)(rgb[i]) < 256) for i in range(len(rgb)))
    return [((int) (rgb[i])) for i in range(len(rgb))] 
