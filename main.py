import random
import string
import io
from PIL import Image, ImageDraw, ImageFont
import telebot


bot = telebot.TeleBot('TOKEN')
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Выбери тип пароля:", reply_markup=get_keyboard_markup())

def get_keyboard_markup():
    keyboard_markup = telebot.types.InlineKeyboardMarkup()
    keyboard_buttons = [
        ['1. Только цифры'],
        ['2. Только буквы'],
        ['3. Цифры и буквы'],
        ['4. Цифры, буквы и символы']
    ]
    for row in keyboard_buttons:
        keyboard_markup.row(*[telebot.types.InlineKeyboardButton(text, callback_data=text) for text in row])
    return keyboard_markup

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    bot.answer_callback_query(callback_query_id=call.id, text="Выбери длину пароля")
    bot.send_message(call.message.chat.id, "Отправь мне длину пароля, который ты хочешь сгенерировать.")
    bot.register_next_step_handler(call.message, generate_password, call.data)

def generate_password(message, password_type):
    try:
        length = int(message.text)
        if length < 4 or length > 100:
            bot.reply_to(message, "Длина пароля должна быть не менее 4 и не более 100 символов.")
            bot.register_next_step_handler(message, generate_password, password_type)
            return

        if password_type == '1. Только цифры':
            chars = string.digits
        elif password_type == '2. Только буквы':
            chars = string.ascii_letters
        elif password_type == '3. Цифры и буквы':
            chars = string.ascii_letters + string.digits
        else:
            chars = string.ascii_letters + string.digits + string.punctuation

        password = ''.join(random.choice(chars) for i in range(length))
        image = create_image_with_snowflakes(password)
        bot.send_photo(message.chat.id, image, caption=f"Сгенерированный пароль \n{password}:")
    except ValueError:
        bot.reply_to(message, "Пожалуйста, отправь мне целое число.")
        bot.register_next_step_handler(message, generate_password, password_type)

def create_image_with_snowflakes(password):
    font_size = 36
    font = ImageFont.truetype("arial.ttf", font_size)

    img_width, img_height = font.getbbox(password)[2:]

    img_width += 100
    img_height += 100

    image = Image.new("RGB", (img_width, img_height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    x = (img_width - font.getbbox(password)[2]) / 2
    y = (img_height - font.getbbox(password)[3]) / 2

    draw.text((x, y), password, font=font, fill=(0, 0, 0))

    for _ in range(100):
        x = random.randint(0, img_width)
        y = random.randint(0, img_height)
        draw.point((x, y), fill=(255, 255, 255))

    image_buffer = io.BytesIO()
    image.save(image_buffer, format="JPEG")
    image_buffer.seek(0)

    return image_buffer


bot.polling()

