import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime


class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter + Crypto")
        self.root.geometry("600x600")

        self.dark_mode = False
        self.set_theme()

        self.currencies_data = {
            "UAH": {"name": "Hryvnia", "type": "fiat"},
            "USD": {"name": "US Dollar", "type": "fiat"},
            "EUR": {"name": "Euro", "type": "fiat"},
            "GBP": {"name": "British Pound", "type": "fiat"},
            "PLN": {"name": "Zloty", "type": "fiat"},
            "DKK": {"name": "Danish Krone", "type": "fiat"},
            "NOK": {"name": "Norwegian Krone", "type": "fiat"},
            "SEK": {"name": "Swedish Krona", "type": "fiat"},
            "TRY": {"name": "Turkish Lira", "type": "fiat"},
            "BTC": {"name": "Bitcoin", "type": "crypto"},
            "ETH": {"name": "Ethereum", "type": "crypto"},
        }

        self.all_currencies = list(self.currencies_data.keys())
        self.rates = {}

        self.create_widgets()
        self.update_rates()

    def create_widgets(self):
        title_label = tk.Label(
            self.root, text="Currency Converter + Crypto",
            font=("Arial", 18, "bold"), bg=self.bg_color, fg=self.fg_color
        )
        title_label.pack(pady=10)

        self.theme_btn = tk.Button(
            self.root, text="Dark Theme", font=("Arial", 10),
            bg=self.button_bg, fg="white", command=self.toggle_theme
        )
        self.theme_btn.pack(pady=5)


        rates_frame = tk.Frame(self.root, bg=self.frame_bg, relief="raised", bd=2)
        rates_frame.pack(padx=20, pady=10, fill="x")

        tk.Label(
            rates_frame, text="Current rates:", font=("Arial", 12, "bold"),
            bg=self.frame_bg, fg=self.fg_color
        ).pack(pady=5)

        self.rates_label = tk.Label(
            rates_frame, text="Loading rates...", font=("Arial", 10),
            bg=self.frame_bg, fg=self.fg_color
        )
        self.rates_label.pack(pady=5)


        converter_frame = tk.Frame(self.root, bg=self.bg_color)
        converter_frame.pack(pady=20, padx=20, fill="x")

        tk.Label(converter_frame, text="Amount:", font=("Arial", 11),
                 bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w")

        self.amount_entry = tk.Entry(converter_frame, font=("Arial", 12),
                                     width=25, bg=self.entry_bg)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=2)
        self.amount_entry.insert(0, "100")


        tk.Label(converter_frame, text="From currency:", font=("Arial", 11),
                 bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, sticky="w", pady=5)

        from_frame = tk.Frame(converter_frame, bg=self.bg_color)
        from_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.from_currency = ttk.Combobox(
            from_frame, values=self.all_currencies, font=("Arial", 11),
            width=8, state="readonly"
        )
        self.from_currency.pack(side="left")
        self.from_currency.set("USD")
        self.from_currency.bind("<<ComboboxSelected>>", self.update_currency_names)

        self.from_currency_name = tk.Label(
            from_frame, text="US Dollar", font=("Arial", 9),
            bg=self.bg_color, fg="darkblue"
        )
        self.from_currency_name.pack(side="left", padx=5)


        tk.Label(converter_frame, text="To currency:", font=("Arial", 11),
                 bg=self.bg_color, fg=self.fg_color).grid(row=2, column=0, sticky="w", pady=5)

        to_frame = tk.Frame(converter_frame, bg=self.bg_color)
        to_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.to_currency = ttk.Combobox(
            to_frame, values=self.all_currencies, font=("Arial", 11),
            width=8, state="readonly"
        )
        self.to_currency.pack(side="left")
        self.to_currency.set("UAH")
        self.to_currency.bind("<<ComboboxSelected>>", self.update_currency_names)

        self.to_currency_name = tk.Label(
            to_frame, text="Hryvnia", font=("Arial", 9),
            bg=self.bg_color, fg="darkblue"
        )
        self.to_currency_name.pack(side="left", padx=5)

        convert_btn = tk.Button(
            converter_frame, text="Convert", font=("Arial", 12, "bold"),
            bg=self.button_bg, fg="white", command=self.convert_currency, width=15
        )
        convert_btn.grid(row=3, column=0, columnspan=2, pady=15)


        result_frame = tk.Frame(self.root, bg=self.result_bg, relief="sunken", bd=2)
        result_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(result_frame, text="Result:", font=("Arial", 12, "bold"),
                 bg=self.result_bg, fg=self.fg_color).pack(pady=5)

        self.result_label = tk.Label(
            result_frame, text="Enter amount and choose currencies",
            font=("Arial", 12), bg=self.result_bg, fg="green"
        )
        self.result_label.pack(pady=10)

        update_btn = tk.Button(
            self.root, text="Refresh rates", font=("Arial", 10),
            bg="gray", fg="white", command=self.update_rates
        )
        update_btn.pack(pady=10)

        self.update_time_label = tk.Label(
            self.root, text="", font=("Arial", 8),
            bg=self.bg_color, fg="darkgray"
        )
        self.update_time_label.pack()


    def set_theme(self):
        if self.dark_mode:
            self.bg_color = "navy"
            self.fg_color = "white"
            self.frame_bg = "darkblue"
            self.entry_bg = "lightgray"
            self.button_bg = "royalblue"
            self.result_bg = "darkgreen"
        else:
            self.bg_color = "lightblue"
            self.fg_color = "navy"
            self.frame_bg = "lightcyan"
            self.entry_bg = "white"
            self.button_bg = "royalblue"
            self.result_bg = "palegreen"

        self.root.configure(bg=self.bg_color)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.set_theme()
        self.theme_btn.config(text="Light Theme" if self.dark_mode else "Dark Theme")

    def update_rates(self):
        try:
            response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.rates = {"UAH": 1.0}

                for currency in data:
                    code = currency.get("cc")
                    if code in self.currencies_data:
                        self.rates[code] = float(currency.get("rate", 0))

                self.get_crypto_rates()
                self.display_rates()
                self.update_time_label.config(text=f"Last Update: {datetime.now():%d.%m.%Y %H:%M:%S}")
            else:
                messagebox.showwarning("Error", "Failed to load rates from NBU.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update rates: {e}")

    def get_crypto_rates(self):
        try:
            crypto_ids = {"BTC": "bitcoin", "ETH": "ethereum"}
            response = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd",
                timeout=10
            )
            if response.status_code == 200:
                crypto_data = response.json()
                usd_rate = self.rates.get("USD", 0)
                for code, cid in crypto_ids.items():
                    if cid in crypto_data and "usd" in crypto_data[cid]:
                        self.rates[code] = crypto_data[cid]["usd"] * usd_rate
        except Exception:
            pass

    def display_rates(self):
        if not self.rates:
            self.rates_label.config(text="Rates not available")
            return

        rates_text = []
        for currency in ["USD", "EUR", "GBP"]:
            if currency in self.rates:
                rate = self.rates[currency]
                rates_text.append(f"1 {currency} = {rate:.2f} UAH")

        crypto_text = []
        for crypto in ["BTC", "ETH"]:
            if crypto in self.rates:
                rate = self.rates[crypto]
                crypto_text.append(f"1 {crypto} = {rate:,.0f} UAH".replace(",", " "))

        self.rates_label.config(text=" | ".join(rates_text) + "\n" + " | ".join(crypto_text))

    def convert_currency(self):
        try:
            amount = float(self.amount_entry.get().replace(",", "."))
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()

            if from_curr not in self.rates or to_curr not in self.rates:
                messagebox.showwarning("Warning", "Rates are not loaded yet!")
                return

            if from_curr == to_curr:
                result = amount
            else:
                result = amount * self.rates[from_curr] / self.rates[to_curr]

            # Format result
            if to_curr in ["BTC", "ETH"]:
                formatted = f"{result:.8f}".rstrip("0").rstrip(".")
            elif result >= 1000:
                formatted = f"{result:,.0f}".replace(",", " ")
            else:
                formatted = f"{result:.2f}"

            self.result_label.config(
                text=f"{amount} {from_curr} = {formatted} {to_curr}"
            )
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def update_currency_names(self, event=None):
        self.from_currency_name.config(text=self.currencies_data[self.from_currency.get()]["name"])
        self.to_currency_name.config(text=self.currencies_data[self.to_currency.get()]["name"])


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
