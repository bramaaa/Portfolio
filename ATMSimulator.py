import tkinter as tk
from tkinter import messagebox, font
from datetime import datetime
import sqlite3
import hashlib

bg_color = 'blue'
fg_color = 'gold'
btn_color = 'gold'
btn_text_color = 'blue'
entry_bg = 'white'
font_name = 'Arial'


class ATMSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title('ATM')
        self.root.geometry('500x700')
        self.root.configure(bg=bg_color)

        self.title_font = font.Font(family=font_name, size=18, weight='bold')
        self.label_font = font.Font(family=font_name, size=12)
        self.btn_font = font.Font(family=font_name, size=12, weight='bold')

        self.current_user = None
        self.attempts = 3
        self.init_db()
        self.create_login_screen()

    def init_db(self):
        self.conn = sqlite3.connect('atm.db')
        self.c = self.conn.cursor()

        self.c.execute('''
        CREATE TABLE IF NOT EXISTS users(
            card_number TEXT PRIMARY KEY,
            pin_hash TEXT,
            balance REAL
        )
        ''')

        self.c.execute('''
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_number TEXT,
            operation TEXT,
            amount REAL,
            timestamp TEXT
        )
        ''')

        pin_hash = hashlib.sha256('1234'.encode()).hexdigest()
        self.c.execute(
            'INSERT OR IGNORE INTO users VALUES (?, ?, ?)',
            ('1234', pin_hash, 15000.0)
        )
        self.conn.commit()

    def create_login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text='ATMachine', font=self.title_font,
                 bg=bg_color, fg=fg_color).pack(pady=30)

        card_frame = tk.Frame(self.root, bg=bg_color)
        card_frame.pack(pady=10)
        tk.Label(card_frame, text='Card number(1234):', font=self.label_font,
                 bg=bg_color, fg=fg_color).pack(side='left')
        self.card_entry = tk.Entry(card_frame, font=self.label_font, bg=entry_bg)
        self.card_entry.pack(side='left', padx=10)

        pin_frame = tk.Frame(self.root, bg=bg_color)
        pin_frame.pack(pady=10)
        tk.Label(pin_frame, text='PIN code(1234):', font=self.label_font,
                 bg=bg_color, fg=fg_color).pack(side='left')
        self.pin_entry = tk.Entry(pin_frame, show='*',
                                  font=self.label_font, bg=entry_bg)
        self.pin_entry.pack(side='left', padx=10)

        tk.Button(self.root, text='Login', font=self.btn_font,
                  bg=btn_color, fg=btn_text_color,
                  command=self.check_pin, width=15).pack(pady=20)

    def check_pin(self):
        card_number = self.card_entry.get().strip()
        entered_pin = self.pin_entry.get()

        self.c.execute(
            'SELECT pin_hash, balance FROM users WHERE card_number=?',
            (card_number,)
        )
        result = self.c.fetchone()

        if result and hashlib.sha256(entered_pin.encode()).hexdigest() == result[0]:
            self.current_user = {
                'card_number': card_number,
                'balance': result[1]
            }
            self.attempts = 3
            self.create_main_menu()
            return

        self.attempts -= 1
        messagebox.showerror(
            'Error', f'Wrong PIN! Attempts left: {self.attempts}'
        )
        if self.attempts <= 0:
            self.root.destroy()

    def create_main_menu(self):
        self.clear_screen()

        tk.Label(
            self.root,
            text=f'Card: ****{self.current_user["card_number"][-4:]}',
            font=self.label_font,
            bg=bg_color, fg=fg_color
        ).pack(pady=20)

        buttons = [
            ('Check balance', self.show_balance),
            ('Cash withdraw', self.withdraw_menu),
            ('Transfer to card', self.transfer_menu),
            ('Payment for services', self.purchase_menu),
            ('Operations history', self.show_history),
            ('Change PIN code', self.change_pin_menu),
            ('Exit', self.create_login_screen)
        ]

        for text, cmd in buttons:
            tk.Button(
                self.root, text=text,
                font=self.btn_font,
                bg=btn_color, fg=btn_text_color,
                command=cmd, width=25
            ).pack(pady=5)

    def show_balance(self):
        self.clear_screen()

        tk.Label(self.root, text='Your balance:',
                 font=self.title_font,
                 bg=bg_color, fg=fg_color).pack(pady=30)

        tk.Label(self.root,
                 text=f"{self.current_user['balance']} UAH",
                 font=('Arial', 24, 'bold'),
                 bg=bg_color, fg=fg_color).pack(pady=20)

        self.add_receipt_option('Check balance')

        tk.Button(self.root, text='Back',
                  font=self.btn_font,
                  bg=btn_color, fg=btn_text_color,
                  command=self.create_main_menu).pack(pady=20)

    def withdraw_menu(self):
        self.clear_screen()
        tk.Label(self.root, text='Choose amount',
                 font=self.title_font,
                 bg=bg_color, fg=fg_color).pack(pady=20)

        for amount in [100, 200, 500, 1000, 2000]:
            tk.Button(
                self.root,
                text=f'{amount} UAH',
                font=self.btn_font,
                bg=btn_color, fg=btn_text_color,
                command=lambda a=amount: self.process_withdrawal(a),
                width=20
            ).pack(pady=5)

        tk.Button(self.root, text='Back',
                  font=self.btn_font,
                  bg=btn_color, fg=btn_text_color,
                  command=self.create_main_menu).pack(pady=20)

    def process_withdrawal(self, amount):
        if amount > self.current_user['balance']:
            messagebox.showerror('Error', 'Not enough balance')
            return

        self.current_user['balance'] -= amount
        self.c.execute(
            'UPDATE users SET balance=? WHERE card_number=?',
            (self.current_user['balance'], self.current_user['card_number'])
        )

        self.c.execute(
            'INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)',
            (self.current_user['card_number'],
             'Withdraw', amount,
             datetime.now().strftime('%Y-%m-%d %H:%M'))
        )
        self.conn.commit()

        messagebox.showinfo('Success', f'Withdrawn {amount} UAH')
        self.create_main_menu()

    def transfer_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="Enter recipient card number", bg=bg_color).pack()
        self.recipient_entry = tk.Entry(self.root, font=self.label_font, bg=entry_bg)
        self.recipient_entry.pack(pady=10)
        tk.Label(self.root, text="Enter the amount you need to transfer", bg=bg_color).pack()
        self.amount_entry = tk.Entry(self.root, font=self.label_font, bg=entry_bg)
        self.amount_entry.pack(pady=10)

        tk.Button(self.root, text='Send',
                  font=self.btn_font,
                  bg=btn_color, fg=btn_text_color,
                  command=self.process_transfer).pack(pady=20)

        tk.Button(self.root, text='Back',
                  font=self.btn_font,
                  bg=btn_color, fg=btn_text_color,
                  command=self.create_main_menu).pack()

    def process_transfer(self):
        try:
            amount = float(self.amount_entry.get())
        except:
            messagebox.showerror('Error', 'Wrong amount')
            return

        recipient = self.recipient_entry.get().strip()

        self.c.execute(
            'SELECT 1 FROM users WHERE card_number=?',
            (recipient,)
        )
        if not self.c.fetchone():
            messagebox.showerror('Error', 'Recipient not found')
            return

        if amount > self.current_user['balance']:
            messagebox.showerror('Error', 'Not enough balance')
            return

        self.c.execute(
            'UPDATE users SET balance=balance-? WHERE card_number=?',
            (amount, self.current_user['card_number'])
        )
        self.c.execute(
            'UPDATE users SET balance=balance+? WHERE card_number=?',
            (amount, recipient)
        )

        self.c.execute(
            'INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)',
            (self.current_user['card_number'], 'Transfer',
             amount, datetime.now().strftime('%Y-%m-%d %H:%M'))
        )
        self.conn.commit()

        self.current_user['balance'] -= amount
        messagebox.showinfo('Success', 'Transfer completed')
        self.create_main_menu()

    def purchase_menu(self):
        self.clear_screen()
        for name, price in [('Mobile', 100), ('Internet', 300), ('Charity', 500)]:
            tk.Button(
                self.root,
                text=f'{name} - {price} UAH',
                font=self.btn_font,
                bg=btn_color, fg=btn_text_color,
                command=lambda p=price, n=name: self.process_purchase(p, n),
                width=30
            ).pack(pady=5)

        tk.Button(self.root, text='Back',
                  font=self.btn_font,
                  bg=btn_color, fg=btn_text_color,
                  command=self.create_main_menu).pack(pady=20)

    def process_purchase(self, amount, name):
        if amount > self.current_user['balance']:
            messagebox.showerror('Error', 'Not enough balance')
            return

        self.current_user['balance'] -= amount
        self.c.execute(
            'UPDATE users SET balance=? WHERE card_number=?',
            (self.current_user['balance'], self.current_user['card_number'])
        )

        self.c.execute(
            'INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)',
            (self.current_user['card_number'],
             f'Purchase {name}', -amount,
             datetime.now().strftime('%Y-%m-%d %H:%M'))
        )
        self.conn.commit()

        messagebox.showinfo('Success', f'{name} paid')
        self.create_main_menu()

    def show_history(self):
        self.clear_screen()

        self.c.execute(
            'SELECT operation, amount, timestamp FROM transactions '
            'WHERE card_number=? ORDER BY timestamp DESC LIMIT 10',
            (self.current_user['card_number'],)
        )

        for op, amount, time in self.c.fetchall():
            tk.Label(
                self.root,
                text=f'{time} | {op}: {amount:+} UAH',
                font=self.label_font,
                bg=bg_color, fg=fg_color
            ).pack(anchor='w')

        tk.Button(self.root, text='Back',
                  font=self.btn_font,
                  bg=btn_color, fg=btn_text_color,
                  command=self.create_main_menu).pack(pady=20)

    def change_pin_menu(self):
        self.clear_screen()

        tk.Label(self.root, text="Enter old PIN", bg=bg_color).pack()
        self.old_pin_entry = tk.Entry(self.root, show='*', bg=entry_bg)
        self.old_pin_entry.pack(pady=5)
        tk.Label(self.root, text="Enter new PIN", bg=bg_color).pack()
        self.new_pin_entry = tk.Entry(self.root, show='*', bg=entry_bg)
        self.new_pin_entry.pack(pady=5)
        tk.Label(self.root, text="Confirm new PIN", bg=bg_color).pack()
        self.confirm_pin_entry = tk.Entry(self.root, show='*', bg=entry_bg)
        self.confirm_pin_entry.pack(pady=5)

        tk.Button(self.root, text='Change PIN',
                  font=self.btn_font,
                  bg=btn_color, fg=btn_text_color,
                  command=self.process_pin_change).pack(pady=20)

        tk.Button(self.root, text='Back',
                  font=self.btn_font,
                  bg=btn_color, fg=btn_text_color,
                  command=self.create_main_menu).pack()

    def process_pin_change(self):
        old_pin = self.old_pin_entry.get()
        new_pin = self.new_pin_entry.get()
        confirm = self.confirm_pin_entry.get()

        self.c.execute(
            'SELECT pin_hash FROM users WHERE card_number=?',
            (self.current_user['card_number'],)
        )

        if hashlib.sha256(old_pin.encode()).hexdigest() != self.c.fetchone()[0]:
            messagebox.showerror('Error', 'Wrong current PIN')
            return

        if new_pin != confirm or not new_pin.isdigit() or len(new_pin) != 4:
            messagebox.showerror('Error', 'Invalid new PIN')
            return

        self.c.execute(
            'UPDATE users SET pin_hash=? WHERE card_number=?',
            (hashlib.sha256(new_pin.encode()).hexdigest(),
             self.current_user['card_number'])
        )
        self.conn.commit()

        messagebox.showinfo('Success', 'PIN changed')
        self.create_main_menu()

    def add_receipt_option(self, operation):
        frame = tk.Frame(self.root, bg=bg_color)
        frame.pack(pady=10)

        tk.Button(frame, text='Print receipt',
                  command=lambda: self.print_receipt(operation)).pack()

    def print_receipt(self, operation):
        messagebox.showinfo(
            'Receipt',
            f'{datetime.now().strftime("%d.%m.%Y %H:%M")}\n'
            f'Operation: {operation}\n'
            f'Balance: {self.current_user["balance"]} UAH'
        )

    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    ATMSimulator(root)
    root.mainloop()
