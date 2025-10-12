import os
from io import BytesIO # part of standard library
from petpetgif import petpet as petting # pip install petpetgif
from PIL import Image # pip install Pillow
import yaml # pip install pyyaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Output directories
os.makedirs(config['avatar']['petpet']['output_dir'], exist_ok=True)
os.makedirs(config['avatar']['bonk']['output_dir'], exist_ok=True)
os.makedirs(config['avatar']['explosion']['output_dir'], exist_ok=True)

def petpet_gen(avatar_bytes: bytes, user_id: int) -> BytesIO:
    # Uses the petpetgif library to generate a petpet GIF
    source = BytesIO(avatar_bytes)
    dest = BytesIO()
    try:
        petting.make(source, dest)
        dest.seek(0)
    except Exception as e:
        # Error handler that catches any and all exceptions.
        # Specific exceptions have proven to be unnecessary.
        # This applies to all image processing functions.
        source.close()
        dest.close()
        raise Exception(f"Failed to generate petpet GIF: {e}")
    source.close()
    return dest


def bonk_gen(avatar_bytes: bytes, user_id: int) -> BytesIO:
    # Pillow sets the avatar_bytes as a squished image with the bat overlay on top.
    try:
        image = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
        background = Image.open(config['avatar']['templates']['bonk_background'])
        overlay = Image.open(config['avatar']['templates']['bonk_overlay'])
        target_size = config['avatar']['bonk']['target_size']
        squished_height = int(target_size * 0.5)
        x = config['avatar']['bonk']['position']['x'] - target_size // 2
        y = config['avatar']['bonk']['position']['y'] + (target_size - squished_height) // 2
        input_position = (x, y)

        image = image.resize((target_size, target_size))
        image = image.resize((target_size, squished_height))

        composite = background.copy()
        composite.paste(image, input_position, image)
        composite.paste(overlay, (0, 0), overlay)
        output = BytesIO()
        composite.save(output, format="PNG")
        output.seek(0)

        # Cleanup
        image.close()
        background.close()
        overlay.close()
        composite.close()
    except Exception as e:
        # Error handler
        raise Exception(f"Failed to generate bonk image: {e}")
    return output

def explosion_gen(avatar_bytes: bytes, user_id: int) -> BytesIO:
    # Uses Pillow to overlay an explosion GIF on top of the avatar.
    try:
        image = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
        avatar = image.resize((200, 200), Image.Resampling.LANCZOS)
        gif_path = config['avatar']['templates']["explosion_overlay"]
        explosion_gif = Image.open(gif_path)
        
        frames = []
        durations = []

        # Extract frames from explosion_gif
        try:
            while True:
                duration = explosion_gif.info.get('duration', 100)
                durations.append(duration)
                explosion_frame = explosion_gif.copy()
                if explosion_frame.mode != 'RGBA':
                    explosion_frame = explosion_frame.convert('RGBA')
                explosion_frame = explosion_frame.resize((200, 200), Image.Resampling.LANCZOS)
                composite = avatar.copy()
                composite = Image.alpha_composite(composite, explosion_frame)
                frames.append(composite)
                explosion_gif.seek(explosion_gif.tell() + 1)
        except EOFError:
            pass
        
        # If no frames were extracted, create a single frame
        if not frames:
            explosion_frame = explosion_gif.copy()
            if explosion_frame.mode != 'RGBA':
                explosion_frame = explosion_frame.convert('RGBA')
            explosion_frame = explosion_frame.resize((200, 200), Image.Resampling.LANCZOS)
            composite = Image.alpha_composite(avatar, explosion_frame)
            frames = [composite]
            durations = [100]
        
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

        # Cleanup
        for frame in frames:
            frame.close()
        image.close()
        avatar.close()
        explosion_gif.close()
        if 'explosion_frame' in locals():
            explosion_frame.close()

    except Exception as e:
        # Error handler
        raise Exception(f"Failed to generate explosion overlay: {e}")
    return output