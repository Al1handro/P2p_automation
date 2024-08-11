import time
from collections import defaultdict
from io import BytesIO

from PIL import Image
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = 'TOKEN'

# Словарь для хранения загруженных изображений
user_images = defaultdict(list)


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Отправь мне несколько изображений, и я склею их вместе.')


async def sex(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Красавчик 😎')


async def pizda_tebe(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Проверь блять, собака сутулая 👿')


async def handle_image(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    photo_file = await update.message.photo[-1].get_file()
    image_stream = BytesIO()
    await photo_file.download_to_memory(out=image_stream)

    image = Image.open(image_stream)
    user_images[user_id].append(image)

    await update.message.reply_text('Изображение получено. Отправь еще или напиши /merge для склеивания. Напиши /fuck если проебался и отправил не то фото.')


async def merge_images2(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_images[user_id] = []
    await update.message.reply_text('Буфер обмена бота почищен.')


async def merge_images(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_images or not user_images[user_id]:
        await update.message.reply_text('Сначала отправьте мне изображения для склеивания.')
        return

    images = user_images[user_id]
    total_width = sum(image.width for image in images)
    max_height = max(image.height for image in images)

    merged_image = Image.new('RGB', (total_width, max_height))

    current_x = 0
    for image in images:
        merged_image.paste(image, (current_x, 0))
        current_x += image.width

    merged_image_stream = BytesIO()
    merged_image.save(merged_image_stream, format='PNG')
    merged_image_stream.seek(0)

    await update.message.reply_photo(photo=InputFile(merged_image_stream, filename='merged_image.png'))
    time.sleep(5)
    await update.message.reply_text('Эй, чушпан, ты проверил все пред тем как переводить? /yes or /no')

    user_images[user_id] = []


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CommandHandler("merge", merge_images))
    application.add_handler(CommandHandler("fuck", merge_images2))
    application.add_handler(CommandHandler("yes", sex))
    application.add_handler(CommandHandler("no", pizda_tebe()))
    application.run_polling()


if __name__ == '__main__':
    main()
