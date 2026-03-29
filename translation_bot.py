import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

#=================基础配置=================

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")

#================初始设置==================

logging.basicConfig(level=logging.INFO)  #初始化log
logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)  #初始化Gemini

#================初始函数==================

def translate(message):  #调用Gemini翻译文本
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction='''
            You are a translator that supports Chinese, English, and Japanese.
            Automatically detect the input language. Always translate into Chinese.
            
            For single words, return exactly in this format:
            单词: [word]
            [blank line. If the input is a Japanese word containing kanji, add the hiragana reading in parentheses after the word.]
            释义: [translation in Chinese]
            [blank line]
            解释: [brief explanation in Chinese]
            [blank line]
            例句: [example sentence in the same language as the input]
            
            For sentences: return only the translated sentence, nothing else.
            If the example sentence contains kanji, add the hiragana reading in parentheses after each kanji word.

            Use natural, conversational tone. No markdown, no extra commentary.                        
            ''',
            temperature=0.3,
        )
    )

    return response.text

async def handle_message(update:Update, context:ContextTypes.DEFAULT_TYPE):  
    message=update.message.text
    result=translate(message)  #调用Gemini翻译文本，并把结果储存到变量中
    await update.message.reply_text(result)  #返回给用户

#=================主循环==================

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).proxy(HTTPS_PROXY).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
