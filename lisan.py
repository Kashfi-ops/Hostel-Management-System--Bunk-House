from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector

lisan_bp = Blueprint("lisan", __name__)

# Same DB connection settings as app.py
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "bunk_house"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)
