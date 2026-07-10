import sys
import os
from datetime import datetime
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QDialog, QFrame, QGridLayout,
    QLineEdit, QComboBox, QDateEdit, QMessageBox, QTableWidget, QTableWidgetItem,
    QProgressBar
)
from PyQt6.QtCore import Qt, QSize, QRect, QDate, QPointF
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPainterPath, QPen, QBrush, QLinearGradient

import database

# --- DYNAMIC CATEGORIES AND SUBCATEGORIES MAP ---
CATEGORIES_MAP = {
    "Income": {
        "Active Income": ["Jobs", "Freelance", "Businesses"],
        "Passive Income": ["Dividends", "Interest from savings accounts", "Rental income", "Bonds", "Mutual funds", "SIP"],
        "Other": ["Gifts", "Refunds", "Cashback", "Pension", "Govt benefits"]
    },
    "Expense": {
        "Housing": ["Rent", "Mortgage", "Repairs"],
        "Food": ["Groceries", "Dining out"],
        "Transport": ["Fuel", "Cab rides", "Public transport"],
        "Utilities": ["Electricity", "Water", "Internet", "Mobile bills"],
        "Healthcare": ["Medicines", "Doctor visit"],
        "Shopping": ["Clothes", "Electronics"],
        "Entertainment": ["Streaming services", "Games", "Movies"],
        "Financial": ["Loan payments", "Taxes", "Investments"],
        "Insurance": [],
        "Family and Personal": [],
        "Gifts and Donations": [],
        "Pets": [],
        "Miscellaneous": []
    }
}

# --- DATE RANGE MATCHING HELPER ---
def is_in_date_range(date_str, range_option):
    if range_option == "All Time":
        return True
    try:
        tx_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        if range_option == "Today":
            return tx_date == today
        elif range_option == "This Week":
            tx_year, tx_week, _ = tx_date.isocalendar()
            today_year, today_week, _ = today.isocalendar()
            return tx_year == today_year and tx_week == today_week
        elif range_option == "This Month":
            return tx_date.year == today.year and tx_date.month == today.month
        elif range_option == "This Year":
            return tx_date.year == today.year
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
    return False

# --- MODERN DARK THEME QSS STYLESHEET WITH HIGH-CONTRAST VISUAL & FONT FIXES ---
QSS_STYLESHEET = """
/* Standard global overrides to prevent point-size warnings */
QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QDateEdit, QTableWidget, QHeaderView, QProgressBar, QAbstractItemView, QListView {
    font-size: 13px;
}

QMainWindow {
    background-color: #121212;
    font-size: 13px;
}
QWidget#centralWidget {
    background-color: #121212;
    font-size: 13px;
}

/* Navigation Bar */
QWidget#navBar {
    background-color: #131313;
    border-bottom: 1px solid #353534;
    font-size: 13px;
}
QLabel#brandLabel {
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: bold;
    color: #59de9b;
    margin-right: 32px;
}
QPushButton.navButton {
    background-color: transparent;
    color: #bccabe;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    border: none;
    padding: 10px 16px;
    margin: 0 4px;
}
QPushButton.navButton:hover {
    color: #59de9b;
    font-size: 13px;
}
QPushButton.navButton[active="true"] {
    color: #59de9b;
    border-bottom: 2px solid #59de9b;
    font-size: 13px;
}

/* Floating Action Button (FAB) */
QPushButton#fab {
    background-color: #00a86b;
    color: #ffffff;
    border-radius: 28px;
    font-family: 'Inter', sans-serif;
    font-size: 28px;
    font-weight: bold;
    border: none;
    padding: 0px;
    text-align: center;
}
QPushButton#fab:hover {
    background-color: #59de9b;
    font-size: 28px;
}
QPushButton#fab:pressed {
    background-color: #006d43;
    font-size: 28px;
}

/* Cards (Dashboard / Budget) */
QFrame.card {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 6px;
    font-size: 13px;
}
QFrame.card:hover {
    border: 1px solid #00A86B;
    font-size: 13px;
}
QLabel.cardTitle {
    color: #bccabe;
    font-family: 'Geist', sans-serif;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
}
QLabel.cardValue {
    color: #e5e2e1;
    font-family: 'Geist', sans-serif;
    font-size: 24px;
    font-weight: bold;
}
QLabel.cardMeta {
    color: #59de9b;
    font-family: 'Inter', sans-serif;
    font-size: 11px;
}
QLabel.cardMetaError {
    color: #ffb4ab;
    font-family: 'Inter', sans-serif;
    font-size: 11px;
}

/* Page Common Styles */
QLabel.pageTitle {
    color: #e5e2e1;
    font-family: 'Inter', sans-serif;
    font-size: 24px;
    font-weight: bold;
}
QLabel.pageSubtitle {
    color: #bccabe;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}

/* Input Fields & Dialog Elements */
QDialog {
    background-color: #1e1e1e;
    border: 1px solid #333333;
    font-size: 13px;
}
QLabel.dialogLabel {
    color: #bccabe;
    font-family: 'Geist', sans-serif;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
}
QLineEdit, QComboBox, QDateEdit {
    background-color: #131313;
    color: #E0E0E0;
    border: 1px solid #353534;
    border-radius: 4px;
    padding: 6px 10px;
    min-height: 24px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #59de9b;
    font-size: 13px;
}

/* Styled dropdown list visibility items */
QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    color: #E0E0E0;
    border: 1px solid #353534;
    selection-background-color: #00a86b;
    selection-color: #ffffff;
    font-size: 13px;
}
QComboBox QAbstractItemView::item {
    font-size: 13px;
}

QPushButton.dialogButton {
    background-color: #00a86b;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: bold;
    border-radius: 4px;
    padding: 10px 16px;
    border: none;
}
QPushButton.dialogButton:hover {
    background-color: #59de9b;
    font-size: 13px;
}
QPushButton.cancelButton {
    background-color: #2a2a2a;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: bold;
    border-radius: 4px;
    padding: 10px 16px;
    border: none;
}
QPushButton.cancelButton:hover {
    background-color: #353534;
    font-size: 13px;
}

/* Table Design (Ledger) */
QTableWidget {
    background-color: #1e1e1e;
    color: #e5e2e1;
    gridline-color: #333333;
    border: 1px solid #333333;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
}
QHeaderView::section {
    background-color: #131313;
    color: #bccabe;
    font-family: 'Geist', sans-serif;
    font-size: 11px;
    font-weight: bold;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #333333;
}
QTableWidget::item {
    padding: 8px;
    font-size: 13px;
}
QTableWidget::item:hover {
    background-color: #252525;
    font-size: 13px;
}

/* Budget Progress Bars - base properties */
QProgressBar {
    border: 1px solid #333333;
    border-radius: 4px;
    background-color: #131313;
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: #ffffff;
    height: 16px;
}
"""

# --- UTILITY TO CREATE LABELS SAFELY IN PYQT6 ---
def make_label(text, style_class=None):
    lbl = QLabel(text)
    if style_class:
        lbl.setProperty("class", style_class)
    return lbl


# --- CUSTOM REAL SPENDING LINE GRAPH WIDGET WITH DYNAMIC CONDITIONAL COLORING ---
class CustomSpendingChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points_data = []  # List of tuple (date_str, running_balance)
        self.setMinimumHeight(240)

    def set_data(self, points):
        """points is a list of tuple (date_str, running_balance_float)"""
        self.points_data = points
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Drawing box boundary background card
        width = self.width()
        height = self.height()
        
        # Outer bounds padding
        padding_left = 60
        padding_right = 30
        padding_top = 30
        padding_bottom = 40

        # Draw grid background horizontal lines
        grid_pen = QPen(QColor("#333333"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        
        num_grid_lines = 4
        for i in range(num_grid_lines + 1):
            y = padding_top + int((height - padding_top - padding_bottom) * (i / num_grid_lines))
            painter.drawLine(padding_left, y, width - padding_right, y)

        if not self.points_data or len(self.points_data) < 2:
            # Draw helpful informational placeholder if no transactions
            no_data_font = QFont("Inter", 12)
            no_data_font.setBold(True)
            painter.setFont(no_data_font)
            painter.setPen(QColor("#869489"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Graph requires at least two transaction history records.")
            return

        # Extract values
        dates = [p[0] for p in self.points_data]
        values = [p[1] for p in self.points_data]

        min_val = min(values)
        max_val = max(values)
        
        # We always want the zero line to be visible or referenceable, so incorporate 0 in range
        min_val = min(0.0, min_val)
        max_val = max(0.0, max_val)
        
        val_range = max_val - min_val
        if val_range == 0:
            val_range = 1.0

        # Add 10% padding to range top and bottom
        min_val -= 0.1 * abs(val_range)
        max_val += 0.1 * abs(val_range)
        val_range = max_val - min_val

        # Map points to pixel coordinates
        pixels = []
        chart_w = width - padding_left - padding_right
        chart_h = height - padding_top - padding_bottom
        num_points = len(self.points_data)

        for i, val in enumerate(values):
            x = padding_left + (i / (num_points - 1)) * chart_w
            y = padding_top + chart_h - ((val - min_val) / val_range) * chart_h
            pixels.append(QPointF(x, y))

        # Split segments cleanly based on zero crossings
        # Each segment contains points and a flag if it is positive (>=0) or negative (<0)
        segments = []
        
        for i in range(num_points - 1):
            v1 = values[i]
            v2 = values[i+1]
            p1 = pixels[i]
            p2 = pixels[i+1]
            
            is_pos1 = (v1 >= 0.0)
            is_pos2 = (v2 >= 0.0)
            
            if is_pos1 == is_pos2:
                # No crossing, continuous segment
                segments.append({
                    "points": [p1, p2],
                    "is_positive": is_pos1
                })
            else:
                # Zero crossing detected! Find exact interpolation fraction t
                denom = v2 - v1
                if denom == 0:
                    t = 0.5
                else:
                    t = -v1 / denom
                
                # Calculate screen coordinates of crossing point
                xc = p1.x() + t * (p2.x() - p1.x())
                yc = p1.y() + t * (p2.y() - p1.y())
                p_cross = QPointF(xc, yc)
                
                # Split segment 1
                segments.append({
                    "points": [p1, p_cross],
                    "is_positive": is_pos1
                })
                # Split segment 2
                segments.append({
                    "points": [p_cross, p2],
                    "is_positive": is_pos2
                })

        # Render Area Fills first so lines render cleanly on top
        for segment in segments:
            pts = segment["points"]
            is_pos = segment["is_positive"]
            
            area_path = QPainterPath()
            area_path.moveTo(pts[0])
            for pt in pts[1:]:
                area_path.lineTo(pt)
            area_path.lineTo(pts[-1].x(), padding_top + chart_h)
            area_path.lineTo(pts[0].x(), padding_top + chart_h)
            area_path.closeSubpath()
            
            area_gradient = QLinearGradient(0, padding_top, 0, padding_top + chart_h)
            if is_pos:
                # Emerald Green fill
                area_gradient.setColorAt(0.0, QColor(0, 168, 107, 40))
                area_gradient.setColorAt(1.0, QColor(0, 168, 107, 0))
            else:
                # Bright Glowing Red fill
                area_gradient.setColorAt(0.0, QColor(231, 76, 60, 40))
                area_gradient.setColorAt(1.0, QColor(231, 76, 60, 0))
                
            painter.fillPath(area_path, QBrush(area_gradient))

        # Render Glowing Accent Lines
        for segment in segments:
            pts = segment["points"]
            is_pos = segment["is_positive"]
            
            line_path = QPainterPath()
            line_path.moveTo(pts[0])
            for pt in pts[1:]:
                line_path.lineTo(pt)
                
            if is_pos:
                line_pen = QPen(QColor("#00a86b"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            else:
                line_pen = QPen(QColor("#e74c3c"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                
            painter.setPen(line_pen)
            painter.drawPath(line_path)

        # Draw Date labels along the bottom
        text_font = QFont("Geist", 8)
        painter.setFont(text_font)
        painter.setPen(QColor("#bccabe"))

        label_step = max(1, num_points // 5)
        for i in range(0, num_points, label_step):
            pt = pixels[i]
            date_str = dates[i]
            painter.drawText(
                int(pt.x() - 30), int(padding_top + chart_h + 20),
                60, 20,
                Qt.AlignmentFlag.AlignCenter, date_str
            )

        # Draw Value labels along Y-Axis
        for i in range(num_grid_lines + 1):
            ratio = i / num_grid_lines
            val = max_val - ratio * val_range
            y = padding_top + int(chart_h * ratio)
            val_str = f"${val:,.0f}"
            painter.drawText(
                5, y - 10,
                padding_left - 15, 20,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, val_str
            )


# --- ADD TRANSACTION POPUP DIALOG ---
class AddTransactionDialog(QDialog):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.setWindowTitle("Record Transaction")
        self.setFixedSize(450, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Title
        title_label = QLabel("Record Transaction")
        title_font = QFont("Inter", 18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #e5e2e1; margin-bottom: 8px;")
        layout.addWidget(title_label)

        grid = QGridLayout()
        grid.setSpacing(10)

        # Type Select (Income / Expense)
        grid.addWidget(make_label("Type", "dialogLabel"), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Expense", "Income"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        grid.addWidget(self.type_combo, 0, 1)

        # Amount Input
        grid.addWidget(make_label("Amount (USD)", "dialogLabel"), 1, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        grid.addWidget(self.amount_input, 1, 1)

        # Main Category
        grid.addWidget(make_label("Category", "dialogLabel"), 2, 0)
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self.populate_subcategories)
        grid.addWidget(self.category_combo, 2, 1)

        # Subcategory (Dynamic Dropdown!)
        grid.addWidget(make_label("Subcategory", "dialogLabel"), 3, 0)
        self.subcategory_combo = QComboBox()
        grid.addWidget(self.subcategory_combo, 3, 1)

        # Description / Payee
        grid.addWidget(make_label("Payee / Desc", "dialogLabel"), 4, 0)
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("e.g. Amazon, Work Salary")
        grid.addWidget(self.desc_input, 4, 1)

        # Date
        grid.addWidget(make_label("Date", "dialogLabel"), 5, 0)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        grid.addWidget(self.date_input, 5, 1)

        # Tag
        grid.addWidget(make_label("Custom Tag", "dialogLabel"), 6, 0)
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("e.g. fixed, variable, leisure")
        grid.addWidget(self.tag_input, 6, 1)

        # Recurring Payment
        grid.addWidget(make_label("Recurring", "dialogLabel"), 7, 0)
        self.recurring_combo = QComboBox()
        self.recurring_combo.addItems(["None", "Daily", "Weekly", "Monthly"])
        grid.addWidget(self.recurring_combo, 7, 1)

        layout.addLayout(grid)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setContentsMargins(0, 16, 0, 0)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "cancelButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "dialogButton")
        save_btn.clicked.connect(self.save_transaction)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Initial loading triggers
        self.populate_categories()

    def on_type_changed(self, text):
        self.populate_categories()

    def populate_categories(self):
        tx_type = self.type_combo.currentText()
        self.category_combo.clear()
        categories = list(CATEGORIES_MAP[tx_type].keys())
        self.category_combo.addItems(categories)
        self.populate_subcategories()

    def populate_subcategories(self):
        tx_type = self.type_combo.currentText()
        category = self.category_combo.currentText()
        self.subcategory_combo.clear()
        if category in CATEGORIES_MAP[tx_type]:
            subs = CATEGORIES_MAP[tx_type][category]
            if subs:
                self.subcategory_combo.addItems(subs)
                self.subcategory_combo.setEnabled(True)
            else:
                self.subcategory_combo.addItem("None")
                self.subcategory_combo.setEnabled(False)

    def save_transaction(self):
        try:
            amount_str = self.amount_input.text().strip()
            if not amount_str:
                raise ValueError("Amount is required")
            
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be a positive number")

            tx_type = self.type_combo.currentText()
            category = self.category_combo.currentText()
            
            sub_val = self.subcategory_combo.currentText()
            subcategory = sub_val if sub_val != "None" else None
            
            description = self.desc_input.text().strip() or "Unspecified"
            date_str = self.date_input.date().toString("yyyy-MM-dd")
            tag = self.tag_input.text().strip() or None
            
            recur_val = self.recurring_combo.currentText().lower()
            repeating_interval = recur_val if recur_val != "none" else "none"

            if tx_type == "Income":
                database.insert_income(amount, category, subcategory, description, date_str)
            else:
                database.insert_expense(amount, category, subcategory, description, date_str, tag, repeating_interval)

            if self.callback:
                self.callback()

            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Entry", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save transaction: {e}")


# --- BASE SKELETON CLASSES FOR STACKED PAGES ---
class BasePage(QWidget):
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 24, 32, 24)
        self.layout.setSpacing(20)

        # Page Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "pageTitle")
        header_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setProperty("class", "pageSubtitle")
        header_layout.addWidget(self.subtitle_label)

        self.layout.addLayout(header_layout)

    def refresh(self):
        """Override to update page content dynamically"""
        pass


class DashboardPage(BasePage):
    def __init__(self):
        super().__init__("Financial Performance Dashboard", "A real-time overview of your budget, spending velocity, and savings rate.")
        self.init_ui()

    def init_ui(self):
        # 1. Summary Metrics Layout (Top bento cards)
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(16)

        # Balance Card
        self.card_balance = QFrame()
        self.card_balance.setProperty("class", "card")
        cb_layout = QVBoxLayout(self.card_balance)
        cb_layout.setContentsMargins(20, 20, 20, 20)
        cb_layout.addWidget(make_label("Current Balance", "cardTitle"))
        self.lbl_balance = QLabel("$0.00")
        self.lbl_balance.setProperty("class", "cardValue")
        cb_layout.addWidget(self.lbl_balance)
        cb_layout.addWidget(make_label("+2.4% vs last month", "cardMeta"))
        metrics_grid.addWidget(self.card_balance, 0, 0)

        # Monthly Income Card
        self.card_income = QFrame()
        self.card_income.setProperty("class", "card")
        ci_layout = QVBoxLayout(self.card_income)
        ci_layout.setContentsMargins(20, 20, 20, 20)
        ci_layout.addWidget(make_label("Monthly Income", "cardTitle"))
        self.lbl_income = QLabel("$0.00")
        self.lbl_income.setProperty("class", "cardValue")
        ci_layout.addWidget(self.lbl_income)
        ci_layout.addWidget(make_label("Expected: $8,000.00", "cardMeta"))
        metrics_grid.addWidget(self.card_income, 0, 1)

        # Monthly Expenses Card
        self.card_expenses = QFrame()
        self.card_expenses.setProperty("class", "card")
        ce_layout = QVBoxLayout(self.card_expenses)
        ce_layout.setContentsMargins(20, 20, 20, 20)
        ce_layout.addWidget(make_label("Monthly Expenses", "cardTitle"))
        self.lbl_expenses = QLabel("$0.00")
        self.lbl_expenses.setProperty("class", "cardValue")
        ce_layout.addWidget(self.lbl_expenses)
        ce_layout.addWidget(make_label("12% higher than average", "cardMetaError"))
        metrics_grid.addWidget(self.card_expenses, 0, 2)

        # Savings Rate Card
        self.card_savings = QFrame()
        self.card_savings.setProperty("class", "card")
        cs_layout = QVBoxLayout(self.card_savings)
        cs_layout.setContentsMargins(20, 20, 20, 20)
        cs_layout.addWidget(make_label("Savings Rate", "cardTitle"))
        self.lbl_savings = QLabel("0.0%")
        self.lbl_savings.setProperty("class", "cardValue")
        cs_layout.addWidget(self.lbl_savings)
        cs_layout.addWidget(make_label("Target: 60.0%", "cardMeta"))
        metrics_grid.addWidget(self.card_savings, 0, 3)

        self.layout.addLayout(metrics_grid)

        # 2. Dynamic Real Spending Graph
        chart_card = QFrame()
        chart_card.setProperty("class", "card")
        pc_layout = QVBoxLayout(chart_card)
        pc_layout.setContentsMargins(24, 24, 24, 24)
        
        lbl_chart_header = QLabel("Net Balance Over Time")
        chart_title_font = QFont("Inter", 13)
        chart_title_font.setBold(True)
        lbl_chart_header.setFont(chart_title_font)
        lbl_chart_header.setStyleSheet("color: #e5e2e1;")
        pc_layout.addWidget(lbl_chart_header)

        self.chart_widget = CustomSpendingChart()
        pc_layout.addWidget(self.chart_widget)
        
        self.layout.addWidget(chart_card, stretch=1)
        self.refresh()

    def refresh(self):
        try:
            balances = database.calculate_current_balances()
            self.lbl_balance.setText(f"${balances['net_balance']:,.2f}")
            self.lbl_income.setText(f"${balances['total_income']:,.2f}")
            self.lbl_expenses.setText(f"${balances['total_expenses']:,.2f}")
            
            rate = 0.0
            if balances['total_income'] > 0:
                rate = (balances['net_balance'] / balances['total_income']) * 100
            self.lbl_savings.setText(f"{max(0.0, rate):.1f}%")

            # Load chronologically mapped portfolio running points
            transactions = database.fetch_all_transactions()
            # Sort oldest to newest
            transactions.sort(key=lambda x: (x['date'], x['id']))
            
            dates = []
            points = []
            current_balance = 0.0
            
            for tx in transactions:
                amount = tx['amount']
                if tx['type'] == 'income':
                    current_balance += amount
                else:
                    current_balance -= amount
                
                try:
                    dt = datetime.strptime(tx['date'], "%Y-%m-%d")
                    date_str = dt.strftime("%b %d")
                except:
                    date_str = tx['date']
                    
                dates.append(date_str)
                points.append(current_balance)
                
            self.chart_widget.set_data(list(zip(dates, points)))
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")


class IncomePage(BasePage):
    def __init__(self):
        super().__init__("Income Directory", "Manage and audit all internal and revenue streams.")
        self.init_ui()

    def init_ui(self):
        summary_card = QFrame()
        summary_card.setProperty("class", "card")
        sc_layout = QHBoxLayout(summary_card)
        sc_layout.setContentsMargins(24, 24, 24, 24)
        
        lbl_total = QLabel("Total Registered Income: $0.00")
        total_font = QFont("Inter", 16)
        total_font.setBold(True)
        lbl_total.setFont(total_font)
        lbl_total.setStyleSheet("color: #59de9b;")
        self.lbl_total = lbl_total
        
        sc_layout.addWidget(lbl_total)
        self.layout.addWidget(summary_card)

        # Replicated Filter and Sort Row
        filter_card = QFrame()
        filter_card.setProperty("class", "card")
        fc_layout = QHBoxLayout(filter_card)
        fc_layout.setContentsMargins(16, 12, 16, 12)
        fc_layout.setSpacing(16)

        fc_layout.addWidget(make_label("Filter Category:", "dialogLabel"))
        self.filter_category_combo = QComboBox()
        self.filter_category_combo.addItem("All Categories")
        self.filter_category_combo.addItems(list(CATEGORIES_MAP["Income"].keys()))
        self.filter_category_combo.currentTextChanged.connect(self.refresh)
        fc_layout.addWidget(self.filter_category_combo)

        fc_layout.addWidget(make_label("Date Filter:", "dialogLabel"))
        self.date_filter_combo = QComboBox()
        self.date_filter_combo.addItems(["All Time", "Today", "This Week", "This Month", "This Year"])
        self.date_filter_combo.currentTextChanged.connect(self.refresh)
        fc_layout.addWidget(self.date_filter_combo)

        fc_layout.addWidget(make_label("Sort By:", "dialogLabel"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Date Descending", "Date Ascending", "Amount High-to-Low"])
        self.sort_combo.currentTextChanged.connect(self.refresh)
        fc_layout.addWidget(self.sort_combo)
        
        fc_layout.addStretch()
        self.layout.addWidget(filter_card)

        # Income details table layout
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Category", "Subcategory", "Payee", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        try:
            balances = database.calculate_current_balances()
            self.lbl_total.setText(f"Total Registered Income: ${balances['total_income']:,.2f}")
            
            txs = [t for t in database.fetch_all_transactions() if t['type'] == 'income']
            
            # Category Filtering
            cat_filter = self.filter_category_combo.currentText()
            if cat_filter != "All Categories":
                txs = [t for t in txs if t['category'] == cat_filter]
                
            # Date Filtering
            date_filter = self.date_filter_combo.currentText()
            txs = [t for t in txs if is_in_date_range(t['date'], date_filter)]
            
            # Sort Options
            sort_by = self.sort_combo.currentText()
            if sort_by == "Date Descending":
                txs.sort(key=lambda x: (x['date'], x['id']), reverse=True)
            elif sort_by == "Date Ascending":
                txs.sort(key=lambda x: (x['date'], x['id']), reverse=False)
            elif sort_by == "Amount High-to-Low":
                txs.sort(key=lambda x: x['amount'], reverse=True)

            self.table.setRowCount(0)
            for row_idx, tx in enumerate(txs):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(tx['date']))
                self.table.setItem(row_idx, 1, QTableWidgetItem(tx['category']))
                self.table.setItem(row_idx, 2, QTableWidgetItem(tx['subcategory'] or "-"))
                self.table.setItem(row_idx, 3, QTableWidgetItem(tx['description'] or "-"))
                
                amount_item = QTableWidgetItem(f"+${tx['amount']:,.2f}")
                amount_item.setForeground(QtGui.QBrush(QColor("#59de9b")))
                self.table.setItem(row_idx, 4, amount_item)
        except Exception as e:
            print(f"Error refreshing income directory: {e}")


class ExpensesPage(BasePage):
    def __init__(self):
        super().__init__("Expenses Register", "Record, sort, filter, and organize custom transactional payments.")
        self.init_ui()

    def init_ui(self):
        # Outflow Display Box
        summary_card = QFrame()
        summary_card.setProperty("class", "card")
        sc_layout = QHBoxLayout(summary_card)
        sc_layout.setContentsMargins(24, 24, 24, 24)
        
        lbl_total = QLabel("Total Monthly Outflow: $0.00")
        total_font = QFont("Inter", 16)
        total_font.setBold(True)
        lbl_total.setFont(total_font)
        lbl_total.setStyleSheet("color: #ffb4ab;")
        self.lbl_total = lbl_total
        sc_layout.addWidget(lbl_total)
        self.layout.addWidget(summary_card)

        # Filter and Sort Row
        filter_card = QFrame()
        filter_card.setProperty("class", "card")
        fc_layout = QHBoxLayout(filter_card)
        fc_layout.setContentsMargins(16, 12, 16, 12)
        fc_layout.setSpacing(16)

        fc_layout.addWidget(make_label("Filter Category:", "dialogLabel"))
        self.filter_category_combo = QComboBox()
        self.filter_category_combo.addItem("All Categories")
        self.filter_category_combo.addItems(list(CATEGORIES_MAP["Expense"].keys()))
        self.filter_category_combo.currentTextChanged.connect(self.refresh)
        fc_layout.addWidget(self.filter_category_combo)

        fc_layout.addWidget(make_label("Date Filter:", "dialogLabel"))
        self.date_filter_combo = QComboBox()
        self.date_filter_combo.addItems(["All Time", "Today", "This Week", "This Month", "This Year"])
        self.date_filter_combo.currentTextChanged.connect(self.refresh)
        fc_layout.addWidget(self.date_filter_combo)

        fc_layout.addWidget(make_label("Sort By:", "dialogLabel"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Date Descending", "Date Ascending", "Amount High-to-Low"])
        self.sort_combo.currentTextChanged.connect(self.refresh)
        fc_layout.addWidget(self.sort_combo)
        
        fc_layout.addStretch()
        self.layout.addWidget(filter_card)

        # Expense register details table (Added Subcategory column back securely)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Date", "Category", "Subcategory", "Description", "Tag", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        try:
            balances = database.calculate_current_balances()
            self.lbl_total.setText(f"Total Monthly Outflow: ${balances['total_expenses']:,.2f}")
            
            txs = [t for t in database.fetch_all_transactions() if t['type'] == 'expense']
            
            # Category Filtering
            cat_filter = self.filter_category_combo.currentText()
            if cat_filter != "All Categories":
                txs = [t for t in txs if t['category'] == cat_filter]
                
            # Date Filtering
            date_filter = self.date_filter_combo.currentText()
            txs = [t for t in txs if is_in_date_range(t['date'], date_filter)]
            
            # Sort Options
            sort_by = self.sort_combo.currentText()
            if sort_by == "Date Descending":
                txs.sort(key=lambda x: (x['date'], x['id']), reverse=True)
            elif sort_by == "Date Ascending":
                txs.sort(key=lambda x: (x['date'], x['id']), reverse=False)
            elif sort_by == "Amount High-to-Low":
                txs.sort(key=lambda x: x['amount'], reverse=True)

            self.table.setRowCount(0)
            for row_idx, tx in enumerate(txs):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(tx['date']))
                self.table.setItem(row_idx, 1, QTableWidgetItem(tx['category']))
                self.table.setItem(row_idx, 2, QTableWidgetItem(tx['subcategory'] or "-"))
                self.table.setItem(row_idx, 3, QTableWidgetItem(tx['description'] or "-"))
                self.table.setItem(row_idx, 4, QTableWidgetItem(tx['tag'] or "-"))
                
                amount_item = QTableWidgetItem(f"-${tx['amount']:,.2f}")
                amount_item.setForeground(QtGui.QBrush(QColor("#ffb4ab")))
                self.table.setItem(row_idx, 5, amount_item)
        except Exception as e:
            print(f"Error refreshing expenses register: {e}")


class BudgetPage(BasePage):
    def __init__(self):
        super().__init__("Budget Management System", "Set limits per transactional category.")
        self.init_ui()

    def init_ui(self):
        # Configure budget form card
        form_card = QFrame()
        form_card.setProperty("class", "card")
        form_layout = QGridLayout(form_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(12)

        form_layout.addWidget(make_label("Category", "dialogLabel"), 0, 0)
        self.cat_combo = QComboBox()
        self.cat_combo.addItems(list(CATEGORIES_MAP["Expense"].keys()))
        form_layout.addWidget(self.cat_combo, 1, 0)

        form_layout.addWidget(make_label("Allocated Amount (USD)", "dialogLabel"), 0, 1)
        self.alloc_input = QLineEdit()
        self.alloc_input.setPlaceholderText("0.00")
        form_layout.addWidget(self.alloc_input, 1, 1)

        save_budget_btn = QPushButton("Save Budget Target")
        save_budget_btn.setProperty("class", "dialogButton")
        save_budget_btn.clicked.connect(self.save_budget)
        form_layout.addWidget(save_budget_btn, 1, 2)

        self.layout.addWidget(form_card)

        # Budgets table view with Progress bar column
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Category", "Allocated Target", "Actual Spending", "Progress"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        self.refresh()

    def save_budget(self):
        try:
            category = self.cat_combo.currentText()
            allocated = float(self.alloc_input.text().strip() or 0.0)
            if allocated <= 0:
                raise ValueError("Allocated target must be positive.")
            
            database.set_budget(category, allocated)
            self.alloc_input.clear()
            self.refresh()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Budget Entry", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def refresh(self):
        try:
            budgets = database.fetch_all_budgets()
            spending = database.fetch_category_spending_totals()
            
            self.table.setRowCount(0)
            for idx, (cat, limit) in enumerate(budgets.items()):
                self.table.insertRow(idx)
                self.table.setItem(idx, 0, QTableWidgetItem(cat))
                self.table.setItem(idx, 1, QTableWidgetItem(f"${limit:,.2f}"))
                
                spent = spending.get(cat, 0.0)
                spent_item = QTableWidgetItem(f"${spent:,.2f}")
                if spent > limit:
                    spent_item.setForeground(QtGui.QBrush(QColor("#ffb4ab")))
                else:
                    spent_item.setForeground(QtGui.QBrush(QColor("#59de9b")))
                self.table.setItem(idx, 2, spent_item)

                # Embed Modern Styled Progress Bar Widget
                progress_bar = QProgressBar()
                progress_bar.setRange(0, 100)
                
                if limit > 0:
                    percentage = int((spent / limit) * 100)
                else:
                    percentage = 0
                
                progress_bar.setValue(min(100, percentage))
                progress_bar.setFormat(f"{percentage}%")

                # Dynamic progress bar selection chunk colors:
                # - If progress is between 0% and 74%, set the selection chunk color to Green (#2ECC71).
                # - If progress is between 75% and 89%, set the selection chunk color to Orange (#F39C12).
                # - If progress is 90% or above, set the selection chunk color to Red (#E74C3C).
                if percentage < 75:
                    chunk_color = "#2ECC71"
                elif percentage < 90:
                    chunk_color = "#F39C12"
                else:
                    chunk_color = "#E74C3C"

                progress_bar.setStyleSheet(f"""
                    QProgressBar::chunk {{
                        background-color: {chunk_color};
                        border-radius: 3px;
                    }}
                """)

                self.table.setCellWidget(idx, 3, progress_bar)
        except Exception as e:
            print(f"Error refreshing budget layout: {e}")


class LedgerPage(BasePage):
    def __init__(self):
        super().__init__("Universal Financial Ledger", "Double-entry style audit trail of all transactions.")
        self.init_ui()

    def init_ui(self):
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(make_label("Audit Ledger Trail Table (Sorted Chronologically)", "pageSubtitle"))
        self.layout.addLayout(filter_layout)

        # Full Ledger Transaction Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Category", "Description / Payee", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        try:
            txs = database.fetch_all_transactions()
            self.table.setRowCount(0)
            for idx, tx in enumerate(txs):
                self.table.insertRow(idx)
                self.table.setItem(idx, 0, QTableWidgetItem(tx['date']))
                
                type_item = QTableWidgetItem(tx['type'].upper())
                type_font = QFont("Geist", 10)
                type_font.setBold(True)
                type_item.setFont(type_font)
                if tx['type'] == 'income':
                    type_item.setForeground(QtGui.QBrush(QColor("#59de9b")))
                else:
                    type_item.setForeground(QtGui.QBrush(QColor("#ffb4ab")))
                self.table.setItem(idx, 1, type_item)
                
                self.table.setItem(idx, 2, QTableWidgetItem(tx['category']))
                self.table.setItem(idx, 3, QTableWidgetItem(tx['description'] or "-"))
                
                amount = tx['amount']
                if tx['type'] == 'income':
                    amount_item = QTableWidgetItem(f"+${amount:,.2f}")
                    amount_item.setForeground(QtGui.QBrush(QColor("#59de9b")))
                else:
                    amount_item = QTableWidgetItem(f"-${amount:,.2f}")
                    amount_item.setForeground(QtGui.QBrush(QColor("#ffb4ab")))
                self.table.setItem(idx, 4, amount_item)
        except Exception as e:
            print(f"Error refreshing universal ledger: {e}")


# --- MAIN CORE WINDOW ---
class BudgetAssistWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BudgetAssist | Mission Control Console")
        self.setMinimumSize(1024, 768)
        self.init_ui()

    def init_ui(self):
        # Central widget configuration
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)

        # Core layout structure
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Custom Horizontal Navigation Bar (Top)
        self.nav_bar = QWidget()
        self.nav_bar.setObjectName("navBar")
        self.nav_bar.setFixedHeight(64)
        
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(32, 0, 32, 0)
        nav_layout.setSpacing(8)

        # Brand / Logo
        brand_label = QLabel("BudgetAssist")
        brand_label.setObjectName("brandLabel")
        nav_layout.addWidget(brand_label)

        # Navigation buttons mapping (Analytics completely streamlined/removed)
        self.nav_buttons = []
        self.pages_info = [
            ("Dashboard", DashboardPage),
            ("Income", IncomePage),
            ("Expenses", ExpensesPage),
            ("Budget", BudgetPage),
            ("Ledger", LedgerPage)
        ]

        # Stacked Pages manager
        self.stacked_widget = QStackedWidget()

        for idx, (title, page_class) in enumerate(self.pages_info):
            btn = QPushButton(title)
            btn.setProperty("class", "navButton")
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

            # Instantiating page skeleton
            page_instance = page_class()
            self.stacked_widget.addWidget(page_instance)

        # Push elements to the left, fill remaining gap
        nav_layout.addStretch()
        self.main_layout.addWidget(self.nav_bar)

        # Content stack area
        self.main_layout.addWidget(self.stacked_widget)

        # Set default startup page
        self.switch_page(0)

        # Permanent Floating Action Button (FAB) Setup
        self.fab = QPushButton("+", self)
        self.fab.setObjectName("fab")
        self.fab.setFixedSize(56, 56)
        self.fab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fab.clicked.connect(self.open_add_transaction_dialog)

        # Ensure FAB is always on top
        self.fab.raise_()

    def switch_page(self, page_index):
        # Update styling state of button list to show highlighted state
        for idx, btn in enumerate(self.nav_buttons):
            if idx == page_index:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.stacked_widget.setCurrentIndex(page_index)
        
        # Refresh target page layout to retrieve data updates
        current_page_widget = self.stacked_widget.currentWidget()
        if hasattr(current_page_widget, "refresh"):
            current_page_widget.refresh()

    def open_add_transaction_dialog(self):
        dialog = AddTransactionDialog(self, callback=self.on_transaction_saved)
        dialog.exec()

    def on_transaction_saved(self):
        # Refresh current active view state
        current_page_widget = self.stacked_widget.currentWidget()
        if hasattr(current_page_widget, "refresh"):
            current_page_widget.refresh()

    def resizeEvent(self, event):
        # Handle scaling boundary positioning for Floating Action Button
        super().resizeEvent(event)
        margin = 32
        self.fab.move(
            self.width() - self.fab.width() - margin,
            self.height() - self.fab.height() - margin
        )


def main():
    # Database Initialization
    database.init_db()

    app = QApplication(sys.argv)
    
    # Global visual styling injection
    app.setStyleSheet(QSS_STYLESHEET)

    window = BudgetAssistWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
