# -*- coding: utf-8 -*-
from message import generate_uid


def change_hidden_uid(message, event):
    """
        Generate a new uid if the message is deactivated
    """
    if event.action == 'disactivate':
        message.hidden_uid = generate_uid()