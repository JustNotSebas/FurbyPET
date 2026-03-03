import os
from io import BytesIO  # part of standard library
from petpetgif import petpet as petting  # pip install petpetgif
from PIL import Image  # pip install Pillow
import yaml  # pip install pyyaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)


def petpet_gen(avatar_bytes: bytes) -> BytesIO:
    source = BytesIO(avatar_bytes)
    dest = BytesIO()
    try:
        petting.make(source, dest)
        dest.seek(0)
    except Exception as e:
        raise Exception(f"Failed to generate petpet GIF: {e}") from e
    finally:
        source.close()  # always runs, success or not
    return dest


def bonk_gen(avatar_bytes: bytes) -> BytesIO:
    image = background = overlay = composite = None
    try:
        image = Image.open(BytesIO(avatar_bytes)).convert(
            "RGBA")  # avatar from discord
        background = Image.new('RGB', (512, 512), "white")  # create a white bg
        overlay = Image.open(config['bonk']['overlay'])  # bonk overlay image
        target_size = config['bonk']['target_size']  # avatar size
        squished_height = int(target_size * 0.4)  # adjust float as wanted

        image = image.resize((target_size, squished_height),
                             Image.Resampling.LANCZOS)  # resize to squish

        x = config['bonk']['position']['x'] - target_size // 2
        y = config['bonk']['position']['y'] + \
            (target_size - squished_height) // 2
        input_position = (x, y)  # coordinates in img

        composite = background.copy()
        composite.paste(image, input_position, image)  # paste avatar
        composite.paste(overlay, (0, 0), overlay)  # paste bonk overlay
        output = BytesIO()  # output container
        composite.save(output, format="PNG")  # save as PNG
        output.seek(0)  # reset pointer to start
    except Exception as e:
        raise Exception(f"Failed to generate bonk image: {e}") from e
    finally:
        for obj in [image, background, overlay, composite]:
            if obj:
                obj.close()
    return output


def explosion_gen(avatar_bytes: bytes) -> BytesIO:
    image = avatar = explosion_gif = explosion_frame = None
    frames = []
    try:
        image = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
        avatar = image.resize((200, 200), Image.Resampling.LANCZOS)
        explosion_gif = Image.open(
            config['explosion']['overlay'])  # open gif (explosion)
        durations = []

        # I kinda understand what this does now
        try:
            while True:
                duration = explosion_gif.info.get('duration', 170)
                durations.append(duration)
                explosion_frame = explosion_gif.copy()
                if explosion_frame.mode != 'RGBA':
                    explosion_frame = explosion_frame.convert('RGBA')
                explosion_frame = explosion_frame.resize(
                    (300, 300), Image.Resampling.LANCZOS)  # Adjust 300 to taste
                left = (300 - 200) // 2
                top = (300 - 200) // 2
                explosion_frame = explosion_frame.crop(
                    (left, top, left + 200, top + 200))
                composite = avatar.copy()
                composite = Image.alpha_composite(composite, explosion_frame)
                frames.append(composite)
                explosion_gif.seek(explosion_gif.tell() + 1)
        except EOFError:
            pass  # End of frames

        # Save as gif
        output = BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            optimize=False,  # Disable optimization to preserve colors
            disposal=2
        )
        output.seek(0)

    except Exception as e:
        raise Exception(f"Failed to generate explosion overlay: {e}") from e
    finally:
        for obj in [image, avatar, explosion_gif, explosion_frame] + frames:
            if obj:
                obj.close()
    return output
