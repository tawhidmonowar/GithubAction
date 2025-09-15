def calculate_image_tokens(width, height):
    if width <= 384 and height <= 384:
        return 258
    else:
        tiles_width = (width + 767) // 768
        tiles_height = (height + 767) // 768
        return tiles_width * tiles_height * 258


if __name__ == '__main__':
    print(calculate_image_tokens(513,768))