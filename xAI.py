from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import aiohttp
import nest_asyncio
import asyncio
import os


# מאפשר הרצת לולאות אירועים מקוננות
nest_asyncio.apply()

# טוקנים ישירות בקוד
TELEGRAM_TOKEN = "7869749116:AAEbJFSd5U0o2XsHZpBQuUpuKoGB5Rs59is"
XAI_API_KEY = "xai-htor14ifL7G77BDo4JATKmEW8Nq0YHCnlUjuZWsM6y3xkxmGeiM0utKXwkB1oFaZD9nmN6iiwVdZLnjA"

# פונקציה לשמירת נתונים בקובץ JSON
def save_to_json(data, filename='data.json'):
    try:
        file_path = os.path.abspath(filename)  # שמירה עם נתיב מוחלט
        with open(file_path, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write("\n")  # כל אובייקט JSON ייכתב בשורה נפרדת
        print(f"Data saved successfully to {file_path}")  # הדפסת ההצלחה
    except Exception as e:
        print(f"Error saving data to JSON: {str(e)}")  # הדפסת השגיאה אם יש

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("שלום! אני בוט AI. איך אוכל לעזור לך?")

async def get_xai_response(message: str) -> str:
    async with aiohttp.ClientSession() as session:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {XAI_API_KEY}"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "model": "grok-beta",
            "stream": False,
            "temperature": 0.7
        }
        
        try:
            async with session.post("https://api.x.ai/v1/chat/completions", 
                                headers=headers, 
                                json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                return "מצטער, אירעה שגיאה בקבלת התשובה."
        except Exception as e:
            return f"Аירעה שגיאה: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = await get_xai_response(user_message)
    
    # יצירת מבנה נתונים לשמירה
    data_to_save = {
        "user_message": user_message,
        "response": response,
        "chat_id": update.message.chat.id,
        "username": update.message.from_user.username,
        "timestamp": update.message.date.isoformat()  # זמן ההודעה בפורמט ISO
    }
    
    # שמירת הנתונים בקובץ JSON
    save_to_json(data_to_save)
    
    # שליחת תשובה למשתמש
    await update.message.reply_text(response)

def main():
    # יצירת אפליקציה
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # הוספת handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # הפעלת הבוט
    print("הבוט מתחיל לרוץ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

