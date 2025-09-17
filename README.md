# ♟️ Chess Game (Python + Pygame)

A simple **chess game built with Python and Pygame** where:  
- You play as **White**.  
- The computer plays as **Black** (makes random valid moves).  
- Supports **pawn promotion**, **castling**, **checkmate**, and **stalemate detection**.  

This is a beginner–friendly project that demonstrates **game development, GUI rendering with Pygame, and implementing chess rules in Python**.

---

## 🎮 Features
- ✅ Full chess board setup (pieces placed in correct starting positions).  
- ✅ Legal move validation for all pieces:
  - Pawns (single, double moves, diagonal captures, promotion).  
  - Rooks, Bishops, Knights, Queens, Kings.  
  - Castling move for King + Rook.  
- ✅ Turn-based play (White → Black → White …).  
- ✅ Random-move computer opponent.  
- ✅ Endgame detection:
  - Checkmate (win/lose).  
  - Stalemate (draw).  
- ✅ Simple **GUI chessboard** using Pygame with piece icons.  
- ✅ Highlight possible moves when selecting a piece.  


## ⚙️ Requirements
- Python **3.8+**  
- Pygame  

You can install the required library with:
```bash
pip install -r requirements.txt