# IRC Chat App

A simple, minimal IRC-style chat application built with Flask and Socket.IO.

## Features

- Real-time messaging with Socket.IO
- Simple nickname system (no registration required)
- Multiple chat rooms
- IRC-style commands (/help, /nick, /join, /me, etc.)
- Message persistence with SQLite
- Simple, terminal-inspired UI

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   ```
   http://localhost:5000
   ```

## Environment Variables

Create a `.env` file or set these environment variables:

- `SECRET_KEY` - Flask secret key (change in production!)
- `DEBUG` - Enable debug mode (True/False)
- `DATABASE_URL` - Database path (default: sqlite:///chat.db)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 5000)
- `MAX_MESSAGE_LENGTH` - Max message length (default: 500)
- `DEFAULT_ROOM` - Default chat room (default: general)

## IRC Commands

- `/help` - Show available commands
- `/nick <new_name>` - Change nickname
- `/join <room>` - Join a different room
- `/users` - List users in current room
- `/me <action>` - Send action message

## Project Structure

```
├── app.py              # Main application
├── config.py           # Configuration
├── database.py         # Database management
├── templates/
│   └── chat.html      # Chat interface
├── requirements.txt   # Dependencies
└── README.md          # This file
```

## License

MIT License - feel free to use this for your own projects!