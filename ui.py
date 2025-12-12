# ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import os
from game import CubicGame
from ai_player import AdvancedAIPlayer
from constants import *

class CubicUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cubic 4x4x4 - Advanced AI")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        self.game = CubicGame()
        self.ai_difficulty = 3
        self.ai = AdvancedAIPlayer(PLAYER_O, difficulty=self.ai_difficulty)
        self.ai_thread = None
        self.ai_thinking = False
        self.thinking_start_time = 0
        
        self.setup_ui()
        self.update_status()
        
    def setup_ui(self):
        """إعداد الواجهة"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # إطار المعلومات
        self.setup_info_frame(main_frame)
        
        # إطار التحكم
        self.setup_control_frame(main_frame)
        
        # شبكة اللعبة
        self.setup_game_grid(main_frame)
        
        # إطار الإحصائيات
        self.setup_stats_frame(main_frame)
        
        self.start_time = time.time()
        self.update_timer()
    
    def setup_info_frame(self, parent):
        """إعداد إطار المعلومات"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(
            info_frame, 
            text="Your turn! You are X", 
            font=("Arial", 14, "bold"),
            foreground="darkgreen"
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.timer_label = ttk.Label(
            info_frame, 
            text="Time: 00:00", 
            font=("Arial", 12)
        )
        self.timer_label.pack(side=tk.RIGHT)
        
        self.ai_thinking_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 10),
            foreground="blue"
        )
        self.ai_thinking_label.pack(side=tk.RIGHT, padx=10)
    
    def setup_control_frame(self, parent):
        """إعداد إطار التحكم"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=10)
        
        # صعوبة AI
        ttk.Label(control_frame, text="AI Difficulty:").pack(side=tk.LEFT, padx=5)
        
        self.difficulty_var = tk.IntVar(value=self.ai_difficulty)
        difficulty_combo = ttk.Combobox(
            control_frame, 
            textvariable=self.difficulty_var,
            values=[1, 2, 3, 4, 5],
            state="readonly",
            width=10
        )
        difficulty_combo.pack(side=tk.LEFT, padx=5)
        difficulty_combo.bind('<<ComboboxSelected>>', self.change_difficulty)
        
        # أزرار التحكم
        ttk.Button(
            control_frame, 
            text="New Game", 
            command=self.reset_game
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="Undo Move", 
            command=self.undo_move
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="Save Game", 
            command=self.save_game
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="Load Game", 
            command=self.load_game
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="Cancel AI Thinking", 
            command=self.cancel_ai_thinking
        ).pack(side=tk.LEFT, padx=5)
    
    def setup_game_grid(self, parent):
        """إعداد شبكة اللعبة"""
        grid_container = ttk.Frame(parent)
        grid_container.pack(pady=10)
        
        self.layers = []
        self.buttons = [[[None for _ in range(BOARD_SIZE)] 
                        for _ in range(BOARD_SIZE)] 
                        for _ in range(BOARD_SIZE)]
        
        for z in range(BOARD_SIZE):
            layer_frame = ttk.Frame(
                grid_container, 
                borderwidth=2, 
                relief="solid", 
                padding="5"
            )
            layer_frame.grid(row=0, column=z, padx=5, pady=5)
            self.layers.append(layer_frame)
            
            ttk.Label(
                layer_frame, 
                text=f"Layer {z+1}", 
                font=("Arial", 10, "bold")
            ).grid(row=0, column=0, columnspan=BOARD_SIZE, pady=5)
            
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    btn = ttk.Button(
                        layer_frame,
                        text="",
                        width=6,
                        command=lambda x=x, y=y, z=z: self.human_move(x, y, z)
                    )
                    btn.grid(row=x+1, column=y, padx=2, pady=2)
                    self.buttons[z][x][y] = btn
    
    def setup_stats_frame(self, parent):
        """إعداد إطار الإحصائيات"""
        stats_frame = ttk.LabelFrame(parent, text="Game Statistics", padding="5")
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.moves_label = ttk.Label(
            stats_frame, 
            text="Moves: 0",
            font=("Arial", 10)
        )
        self.moves_label.pack(side=tk.LEFT, padx=10)
        
        self.nodes_label = ttk.Label(
            stats_frame, 
            text="Nodes evaluated: 0",
            font=("Arial", 10)
        )
        self.nodes_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = ttk.Label(
            stats_frame, 
            text="AI time: 0.0s",
            font=("Arial", 10)
        )
        self.time_label.pack(side=tk.LEFT, padx=10)
    
    def human_move(self, x, y, z):
        """معالجة حركة الإنسان"""
        if self.game.game_over:
            return
            
        if self.game.current_player != PLAYER_X or self.ai_thinking:
            return
            
        if self.game.make_move(x, y, z):
            self.update_display()
            self.update_status()
            
            if self.check_game_end():
                return
                
            self.game.switch_player()
            self.start_ai_move()
    
    def start_ai_move(self):
        """بدء حركة AI في خيط منفصل"""
        if self.game.game_over:
            return
        
        self.ai_thinking = True
        self.thinking_start_time = time.time()
        self.update_thinking_time()
        
        def ai_worker():
            move = self.ai.find_best_move(self.game)
            self.root.after(0, self.complete_ai_move, move)
        
        self.ai_thread = threading.Thread(target=ai_worker)
        self.ai_thread.daemon = True
        self.ai_thread.start()
    
    def complete_ai_move(self, move):
        """إكمال حركة AI"""
        self.ai_thinking = False
        self.ai_thinking_label.config(text="")
        
        if move and not self.game.game_over:
            x, y, z = move
            self.game.make_move(x, y, z)
            self.update_display()
            self.update_status()
            self.check_game_end()
            
            # التبديل للاعب بعد حركة AI
            self.game.switch_player()
    
    def update_thinking_time(self):
        """تحديث وقت تفكير AI"""
        if self.ai_thinking:
            thinking_time = time.time() - self.thinking_start_time
            self.ai_thinking_label.config(
                text=f"AI thinking: {thinking_time:.1f}s"
            )
            self.root.after(100, self.update_thinking_time)
    
    def check_game_end(self):
        """فحص نهاية اللعبة"""
        if self.game.game_over:
            if self.game.winner == PLAYER_X:
                self.show_winner(PLAYER_X)
            elif self.game.winner == PLAYER_O:
                self.show_winner(PLAYER_O)
            else:
                self.show_draw()
            return True
        return False
    
    def show_winner(self, player):
        """عرض رسالة الفائز"""
        winning_line = self.game.winning_line
        if winning_line:
            self.highlight_winning_line(winning_line)
        
        if player == PLAYER_X:
            messagebox.showinfo("Congratulations!", "You won! 🎉")
        else:
            messagebox.showinfo("Game Over", "AI won! Try again 💪")
    
    def show_draw(self):
        """عرض رسالة التعادل"""
        messagebox.showinfo("Game Over", "It's a draw! 🤝")
    
    def highlight_winning_line(self, line):
        """تمييز خط الفوز"""
        for x, y, z in line:
            self.buttons[z][x][y].config(style='Winning.TButton')
    
    def update_display(self):
        """تحديث العرض"""
        for z in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    symbol = self.game.board[x][y][z]
                    btn = self.buttons[z][x][y]
                    
                    if symbol == PLAYER_X:
                        btn.config(text="X", style='PlayerX.TButton')
                    elif symbol == PLAYER_O:
                        btn.config(text="O", style='PlayerO.TButton')
                    else:
                        btn.config(text="", style='TButton')
    
    def update_status(self):
        """تحديث الحالة"""
        if self.game.game_over:
            if self.game.winner == PLAYER_X:
                self.status_label.config(text="You won! 🎉", foreground="red")
            elif self.game.winner == PLAYER_O:
                self.status_label.config(text="AI won! 💪", foreground="blue")
            else:
                self.status_label.config(text="Draw! 🤝", foreground="purple")
        else:
            if self.game.current_player == PLAYER_X:
                self.status_label.config(text="Your turn! You are X", foreground="darkgreen")
            else:
                self.status_label.config(text="AI is thinking...", foreground="darkblue")
        
        self.moves_label.config(text=f"Moves: {self.game.move_count}")
        self.nodes_label.config(text=f"Nodes evaluated: {self.ai.nodes_evaluated}")
    
    def change_difficulty(self, event):
        """تغيير صعوبة AI"""
        self.ai_difficulty = self.difficulty_var.get()
        self.ai.set_difficulty(self.ai_difficulty)
    
    def undo_move(self):
        """تراجع عن الحركة"""
        if self.ai_thinking:
            self.cancel_ai_thinking()
        
        if self.game.undo_move():
            # إذا كنا في دور AI، تراجع مرتين
            if self.game.current_player == PLAYER_O:
                self.game.undo_move()
            
            self.update_display()
            self.update_status()
    
    def save_game(self):
        """حفظ اللعبة"""
        filename = "cubic_game_save.pkl"
        self.game.save_game(filename)
        messagebox.showinfo("Game Saved", f"Game saved to {filename}")
    
    def load_game(self):
        """تحميل لعبة"""
        if self.ai_thinking:
            self.cancel_ai_thinking()
        
        filename = "cubic_game_save.pkl"
        self.game.load_game(filename)
        self.update_display()
        self.update_status()
        messagebox.showinfo("Game Loaded", f"Game loaded from {filename}")
    
    def cancel_ai_thinking(self):
        """إلغاء تفكير AI"""
        if self.ai_thinking:
            self.ai.search_cancelled = True
            self.ai_thinking = False
            self.ai_thinking_label.config(text="")
            self.update_status()
    
    def reset_game(self):
        """إعادة تعيين اللعبة"""
        self.cancel_ai_thinking()
        self.game.reset_game()
        self.ai = AdvancedAIPlayer(PLAYER_O, difficulty=self.ai_difficulty)
        self.start_time = time.time()
        self.ai_thinking = False  # التأكد من إعادة تعيين حالة التفكير
        
        # إعادة تعيين جميع الأزرار
        for z in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    self.buttons[z][x][y].config(
                        text="", 
                        style='TButton'
                    )
        
        self.update_status()
    
    def update_timer(self):
        """تحديث المؤقت"""
        if not self.game.game_over:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)

# إنشاء الأنماط
def configure_styles():
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 10))
    style.configure('PlayerX.TButton', foreground='red', font=('Arial', 10, 'bold'))
    style.configure('PlayerO.TButton', foreground='blue', font=('Arial', 10, 'bold'))
    style.configure('Winning.TButton', background='yellow', font=('Arial', 10, 'bold'))

def main():
    root = tk.Tk()
    
    # تكوين الأنماط
    configure_styles()
    
    # إنشاء التطبيق
    app = CubicUI(root)
    
    # إضافة قائمة
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    
    # قائمة Game
    game_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Game", menu=game_menu)
    game_menu.add_command(label="New Game", command=app.reset_game)
    game_menu.add_command(label="Undo Move", command=app.undo_move)
    game_menu.add_separator()
    game_menu.add_command(label="Save Game", command=app.save_game)
    game_menu.add_command(label="Load Game", command=app.load_game)
    game_menu.add_separator()
    game_menu.add_command(label="Exit", command=root.quit)
    
    root.mainloop()

if __name__ == "__main__":
    main()