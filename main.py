import tkinter as tk
from ui import CubicUI, configure_styles

def main():
    root = tk.Tk()
    
    configure_styles()
    
    app = CubicUI(root)
    
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    
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
