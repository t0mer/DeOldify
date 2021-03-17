# import the necessary packages
import os,sys,requests,ssl, traceback
import torch, time, fastai
from os import path
import telepot
from telepot.loop import MessageLoop

from app_utils import download, generate_random_filename, clean_me, clean_all 
from app_utils import get_model_bin, convertToJPG, create_directory
from loguru import logger

from deoldify.visualize import *
from pathlib import Path

# Set artistik model url - to download if not exixts
artistic_model_url = "https://data.deepai.org/deoldify/ColorizeArtistic_gen.pth"
video_model_url = "https://data.deepai.org/deoldify/ColorizeVideo_gen.pth"


# Handle switch between GPU and CPU
if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
else:
    del os.environ["CUDA_VISIBLE_DEVICES"]

render_factor = os.environ["RENDER_FACTOR"]
BOT_TOKEN  = os.environ["BOT_TOKEN"]

# Set upload directory and create if not exists
upload_directory = '/data/upload'
create_directory(upload_directory)

# Set result images directory and create if not exists
results_img_directory = '/data/result_images'
create_directory(results_img_directory)

# Set data model directory and create if not exists
model_directory = '/data/models'
create_directory(model_directory)


# only get the model binay if it not present in /data/models
get_model_bin(artistic_model_url, os.path.join(model_directory, "ColorizeArtistic_gen.pth"))
image_colorizer = get_image_colorizer(artistic=True)

get_model_bin(video_model_url, os.path.join(model_directory, "ColorizeVideo_gen.pth"))
video_colorizer = get_video_colorizer()
video_colorizer.result_folder = Path(results_img_directory)


def color(file_path,chat_id):
    # set input and outpu file path 
    input_path = file_path
    output_path = os.path.join(results_img_directory, os.path.basename(input_path))

    try:
        # try coloring with out converting the image
        logger.info("Coloring....")
        image_colorizer.plot_transformed_image(path=input_path, figsize=(20,20),
            render_factor=int(render_factor), display_render_factor=True, compare=False)
    except:
        # if coloring failed, convert the image to JPG fromat and retry coloring
        logger.error("Coloring failed, converting image to JPG format.")
        convertToJPG(input_path)
        logger.info("Image converted, Coloring...")
        image_colorizer.plot_transformed_image(path=input_path, figsize=(20,20),
        render_factor=int(render_factor), display_render_factor=True, compare=False)
        
    #Send the colorized image back to user
    logger.info("Reading image data")
    image_data = open(output_path,"rb")
    logger.info("Sending colorized photo back to user")
    bot.sendPhoto(chat_id,image_data)
    
    # Delete the original photo in order to save storage
    if os.path.exists(input_path):
        logger.info("Removing original photo from storage")
        os.remove(input_path)
    
    # Delete the colorized photo in order to save storage
    if os.path.exists(output_path):
        logger.info("Removing colorized photo from storage")
        os.remove(output_path)


def video_color(file_path,chat_id):
    # Coloring Video
    logger.info("Coloring Video....")
    output_path= video_colorizer.colorize_from_file_name(file_path, render_factor=int(render_factor))
    # output_path = os.path.join(results_img_directory, os.path.basename(file_path))
    #Send the colorized image back to user
    video_data = open(output_path,"rb")
    logger.info("Sending colorized video back to user")
    bot.sendVideo(chat_id,video_data)
    
    # Delete the original photo in order to save storage
    if os.path.exists(file_path):
        logger.info("Removing original photo from storage")
        os.remove(input_path)
    
    # Delete the colorized photo in order to save storage
    if os.path.exists(output_path):
        logger.info("Removing colorized photo from storage")
        os.remove(output_path)



 
    
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    try:
        # Check if the mesaage contains photo (Compressed)
        if 'photo' in str(msg):
            logger.info('============ Photo Recived ====================')
            file_id = msg['photo'][-1]['file_id']
            file_path = os.path.join(upload_directory,file_id+".jpg")
            bot.download_file(file_id,file_path)
            bot.sendMessage(chat_id,"Coloring, please wait...")
            color(file_path,chat_id)
    except Exception as e:
        logger.error(str(e))

    try:
        # Check if the mesaage contains photo (Not Compressed)
        if 'document' in str(msg) and 'image' in str(msg):
            logger.info('============  Document Recived ====================')
            file_id = msg['document']['file_id']
            file_path = os.path.join(upload_directory,file_id+".jpg")
            bot.download_file(file_id,file_path)
            bot.sendMessage(chat_id,"Coloring, please wait...")
            color(file_path,chat_id)
           
    except Exception as e:
        logger.error(str(e))



    try:
        # Check if the mesaage contains photo (Compressed)
        if 'video' in str(msg):
            logger.info('============ Video Recived ====================')
            if 'document' in str(msg):
                file_id = msg['document']['file_id']
            else:
                file_id = msg['video']['file_id']
            file_path = os.path.join(upload_directory,file_id+".mp4")
            bot.download_file(file_id,file_path)
            bot.sendMessage(chat_id,"Coloring, please wait...")
            video_color(file_path,chat_id)
    except Exception as e:
        logger.error(str(e))




# Starts the bot
bot = telepot.Bot(BOT_TOKEN)
MessageLoop(bot, handle).run_as_thread()
logger.info('Bot is running!')
 
while 1:
    time.sleep(10)
