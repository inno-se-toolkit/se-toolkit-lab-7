"""
Inline keyboard button definitions for the Telegram bot.

These buttons appear below bot messages and let users quickly access common actions
without typing commands.
"""

from typing import Any


def get_start_keyboard() -> list[list[dict[str, Any]]]:
    """Return inline keyboard for /start message.
    
    Shows common actions that new users might want.
    """
    return [
        [
            {"text": "📚 Available Labs", "callback_data": "labs"},
            {"text": "💊 Health Check", "callback_data": "health"},
        ],
        [
            {"text": "📊 My Scores", "callback_data": "scores_help"},
            {"text": "❓ Help", "callback_data": "help"},
        ],
    ]


def get_help_keyboard() -> list[list[dict[str, Any]]]:
    """Return inline keyboard for /help message."""
    return [
        [
            {"text": "📚 Browse Labs", "callback_data": "labs"},
            {"text": "💊 Health", "callback_data": "health"},
        ],
        [
            {"text": "💬 Ask a Question", "callback_data": "ask_help"},
        ],
    ]


def get_labs_keyboard(labs: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Return inline keyboard with lab buttons.
    
    Args:
        labs: List of lab dicts with 'lab_id' and 'lab_name'
    """
    keyboard = []
    row = []
    
    for lab in labs[:6]:  # Limit to 6 buttons
        lab_id = lab.get("lab_id", "")
        lab_name = lab.get("lab_name", lab_id)
        row.append({
            "text": f"📋 {lab_id}",
            "callback_data": f"scores_{lab_id}",
        })
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    return keyboard


def keyboard_to_telegram_format(keyboard: list[list[dict[str, Any]]]) -> Any:
    """Convert keyboard definition to aiogram InlineKeyboardMarkup format.
    
    This function will be used when the Telegram bot is fully implemented.
    For now, it returns the structure that aiogram expects.
    """
    try:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        
        for row in keyboard:
            for button_data in row:
                builder.button(
                    text=button_data["text"],
                    callback_data=button_data["callback_data"],
                )
        
        return builder.as_markup()
    except ImportError:
        # aiogram not available (test mode)
        return keyboard
