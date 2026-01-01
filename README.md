# 🧮 Gematria Calculator

An advanced Streamlit application for computing Hebrew and English Gematria values instantly. This project is designed to be fast, beautiful, and easy to use on both desktop and mobile devices.

## ✨ Key Features

### 🇮🇱 Hebrew Gematria
*   **Standard (Mispar Gadol):** Calculates standard values (Aleph=1...Tav=400).
*   **Final Letters:** Uses standard values (Khaf Sofit=20, Mem Sofit=40, etc.) following the common method.
*   **Niqqud Support:** Automatically filters out vowel points (Niqqud) and computes only the letters.
*   **Breakdown:** Displays the value of each letter individually in a detailed table.
*   **Display:** Full Right-to-Left (RTL) support with a deep blue color theme.

### 🇺🇸 English Gematria
*   **English Ordinal:** A=1, B=2... (Standard alphanumeric order).
*   **Full Reduction:** Reduces values to a single digit (Pythagorean 1-9 system).
*   **Reverse Ordinal:** Reverse order values (Z=1, A=26).
*   **Reverse Reduction:** Reduced values in reverse order.
*   **Design:** Gold/Orange color theme.

### 🚀 Additional Functionality
*   **History:** Tracks the last 5 calculations in the current session.
*   **Sharing:** URL parameters automatically update to allow sharing of specific results.
*   **Performance:** Instant calculation (under 100ms) even for long texts.

## 🛠️ Installation & Usage

The project is built with Python and Streamlit.

1.  **Install Requirements:**
    Ensure you have Python installed, then run the following command in your terminal:
    ```bash
    pip install streamlit pandas
    ```

2.  **Run the App:**
    Launch the calculator using:
    ```bash
    streamlit run app.py
    ```

The browser will open automatically at your local address (usually `http://localhost:8501`).

## 📂 File Structure
All code is contained within a single file, `app.py`, which includes the logic, graphical interface (UI), and styling (CSS).

---
Built with ❤️ using Streamlit
