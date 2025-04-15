# Malgrange Closure Algorithm App

This application implements the Malgrange algorithm for finding direct and inverse transitive closures of a directed graph, visualizes the steps, and clusters nodes by closure intersections.

## Features
- Input: square adjacency matrix (0/1)
- Step-by-step computation of direct/inverse transitive closures and their intersections
- Visualization of the final graph with clusters
- Web/mobile-friendly UI (Streamlit)
- Can be compiled to .exe (PyInstaller)

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```
3. To build .exe (Windows):
   ```bash
   pyinstaller --onefile --add-data "templates;templates" app.py
   ```

## Mobile/web version
Just open the Streamlit app in your browser (works well on mobile).

---

**Author:**
Cascade AI
