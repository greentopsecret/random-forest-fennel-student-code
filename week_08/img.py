from PIL import Image
import numpy as np

if __name__ == '__main__':
    market = np.array(Image.open('resources/supermarket.png'))
    tiles = np.array(Image.open('resources/tiles.png'))

    x = 4 * 32  # 5th column starting from 0
    y = 1 * 32  # 2nd row
    apple = tiles[y:y + 32, x:x + 32]

    tx = 13 * 32
    ty = 2 * 32
    market[ty:ty + 32, tx:tx + 32] = apple

    im = Image.fromarray(market)
    im.save('output/supermarket_filled.png')