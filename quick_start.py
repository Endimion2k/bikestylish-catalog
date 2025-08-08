#!/usr/bin/env python3
"""
BikeStylish FastAPI - Pornire Rapidă
Pornește direct serverul FastAPI fără menu
"""

import uvicorn
import sys
import os

def main():
    print("🚴‍♂️ BikeStylish FastAPI - Pornire Rapidă")
    print("=" * 45)
    
    # Verifică datele
    if not os.path.exists("data"):
        print("❌ Directorul 'data' nu există!")
        print("   Asigură-te că ești în directorul bikestylish-catalog")
        return
    
    print("🚀 Pornesc FastAPI pe http://localhost:8000")
    print("📚 Documentație: http://localhost:8000/docs")
    print("💡 Pentru oprire: Ctrl+C")
    print("=" * 45)
    
    try:
        # Pornește direct cu uvicorn
        uvicorn.run(
            "fastapi_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Auto-reload la schimbări
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n✅ Server oprit cu succes!")
    except Exception as e:
        print(f"❌ Eroare: {e}")
        print("🔧 Asigură-te că ai instalat: pip install fastapi uvicorn")

if __name__ == "__main__":
    main()
