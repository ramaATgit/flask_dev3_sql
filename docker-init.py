#!/usr/bin/env python3

"""
Database initialization script for Docker deployment
"""

import os
from main import app, db, seed_database

if __name__ == "__main__":
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Seed the database if it's empty
        try:
            seed_database()
            print("Database seeded successfully!")
        except Exception as e:
            print(f"Note: Database may already contain data. Error: {e}")
            
        print("Initialization complete!")