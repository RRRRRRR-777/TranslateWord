import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import webbrowser
import glob


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        # 生成されるCSVファイルのパス指定
        self.filename = 'Translated.csv'

        # データフレームの生成
        if not glob.glob(self.filename):
            self.df = pd.DataFrame(columns=['Source', 'Translate'])
            self.df.to_csv(self.filename, index=False, encoding='shift-jis')

        # tkinterの設定
        self.master.title("TransrateWord")
        self.master.geometry("360x125")

        # エンターキー、スペースキーで検索
        root.bind('<Return>', self.translate_word) \
            and root.bind('<space>', self.translate_word) \
            and root.bind('<Button-3>', self.translate_word)

        # ソースラベル
        self.source_label = tk.Label(
            self.master, text='', font=('', '20', 'bold'))
        self.source_label.pack()

        # ラベル
        self.label = tk.Label(self.master, text='')
        self.label2 = tk.Label(self.master, text='')
        self.label3 = tk.Label(self.master, text='')
        self.label.pack()
        self.label2.pack()
        self.label3.pack()

        # チェックボックス 最前面
        self.check_value_excude = tk.BooleanVar(self.master, value=True)
        self.check = tk.Checkbutton(
            self.master, text='Always on top',
            variable=self.check_value_excude, command=self.excute)
        self.check.pack(side='left')
        root.attributes("-topmost", True)

        # チェックボックス csv
        self.check_value = tk.BooleanVar(self.master, value=True)
        self.check = tk.Checkbutton(
            self.master, text='Input to CSV', variable=self.check_value)
        self.check.pack(fill='x', padx=20, side='left')

        # サーチボタン
        self.entry_button = tk.Button(
            self.master, text='Search', command=self.search)
        self.entry_button.pack()

    # EditBoxの中身
    def translate_word(self, master):
        self.error_flag = 0
        self.source_word = root.clipboard_get()
        self.source_word = self.source_word.replace(' ', '').lower()
        self.source_label.config(text=self.source_word)
        url = 'https://ejje.weblio.jp/content/'+self.source_word
        trans_res = requests.get(url).text
        soup = BeautifulSoup(trans_res, 'html.parser')
        try:
            self.trans_word = soup.select_one('span.content-explanation').text
            self.trans_word = self.trans_word \
                .replace('\n', '').replace(' ', '')
        except AttributeError:
            root.attributes("-topmost", True)
            messagebox.showinfo(
                message='英和・和英辞典で「'+self.source_word+'」に一致する見出し語は見つかりませんでした')
            if not self.check_value_excude.get():
                root.attributes("-topmost", False)
            self.source_label.config(text='Word_Error')
            self.label.config(text='')
            self.label2.config(text='')
            self.label3.config(text='')
            self.error_flag = 1

        if self.error_flag == 0:
            if len(self.trans_word) > 58:
                self.label.config(text=self.trans_word[:29])
                self.label2.config(text=self.trans_word[29:58])
                self.label3.config(text=self.trans_word[58:])
            elif len(self.trans_word) > 29:
                self.label.config(text=self.trans_word[:29])
                self.label2.config(text=self.trans_word[29:])
                self.label3.config(text='')
            else:
                self.label.config(text=self.trans_word)
                self.label2.config(text='')
                self.label3.config(text='')

            if self.check_value.get():
                self.repalace_word = [
                    '三人称単数現在', '過去形、または過去分詞', '現在分詞', '複数形', '過去形・過去分詞'
                    ]
                for i in range(len(self.repalace_word)):
                    if self.trans_word.find(self.repalace_word[i]) != -1:
                        self.word = self.trans_word[
                            :self.trans_word.find(self.repalace_word[i])]
                        self.trans_word = self.trans_word \
                            .replace(self.word, '')
                self.df = pd.read_csv(self.filename, encoding='shift-jis')
                self.df = self.df.append(
                    {'Source': self.source_word, 'Translate': self.trans_word},
                    ignore_index=True)
                self.df = self.df.drop_duplicates()
                self.df.to_csv(
                    self.filename, index=False, encoding='shift-jis')

            self.check_value.set(True)

    # weblio検索
    def search(self):
        try:
            source_word = root.clipboard_get().lower()
        finally:
            url = 'https://ejje.weblio.jp/content/'+source_word
            webbrowser.open(url)

    # 最前面
    def excute(self):
        if self.check_value_excude.get():
            root.attributes("-topmost", True)
        else:
            root.attributes("-topmost", False)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
