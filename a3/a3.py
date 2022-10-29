import tkinter as tk

from tkinter import messagebox, Toplevel, Menu, filedialog
from PIL import ImageTk, Image

from typing import Callable, Union
from a2_solution import *
from a2_support import UserInterface
from a3_support import AbstractGrid
from constants import *

GAME_TITLE = "MazeRunner"
IMAGE_FILE = "images-custom/"

DEFAULT_PADDING = 10

STATS_COLUMN = 4
STATS_ROW = 2
STATS_TEXT = {
    0: "HP",
    1: "Hunger",
    2: "Thirst"
}

class LevelView(AbstractGrid):
    """ Displays maze tiles and entities on abstract grid. """
    def draw(
        self,
        tiles: list[list[Tile]],
        items: dict[tuple[int, int], Item],
        player_pos: tuple[int, int]
    ) -> None:
        """ Draws maze tiles and entities.

        Parameters:
            tiles: Tile objects to draw.
            items: Item objects to draw.
            player_pos: Position to draw player.
        """
        self.clear()

        num_rows, num_cols = self._dimensions
        for row in range(num_rows):
            for col in range(num_cols):
                pos = (row, col)
                self._draw_tiles(tiles[row][col], pos)

                if pos in items:
                    self._draw_items(items[pos])
        
        self._draw_player(player_pos)

    def _draw_tiles(
        self, 
        tile: Tile,
        pos: tuple[int, int]
    ) -> None:
        """ Draw tile objects on abstract grid.

        Parameters:
            tile: Tile object to draw.
            pos: Position to draw tile.
        """
        cell_bbox = self.get_bbox(pos)
        self.create_rectangle(cell_bbox, fill=TILE_COLOURS[tile.get_id()])

    def _draw_items(
        self,
        item: Item
    ) -> None:
        """ Draw item objects on abstract grid.

        Parameters:
            item: Item object to draw.
        """
        cell_bbox = self.get_bbox(item.get_position())
        self.create_oval(cell_bbox, fill=ENTITY_COLOURS[item.get_id()])
        self.annotate_position(item.get_position(), item.get_id())

    def _draw_player(
        self,
        player_pos: tuple[int, int]
    ) -> None:
        """ Draw player on abstract grid.

        Parameters:
            player_pos: Position to draw player.
        """
        cell_bbox = self.get_bbox(player_pos)
        self.create_oval(cell_bbox, fill=ENTITY_COLOURS[PLAYER])
        self.annotate_position(player_pos, PLAYER)

class StatsView(AbstractGrid):
    """ Displays player stats and coins on abstract grid. """
    def __init__(
        self, 
        master: Union[tk.Tk, tk.Frame], 
        width: int,
        **kwargs
    ) -> None:
        """ Initialises stats view in root window.
        
        Parameters:
            master: Root game window.
            width: wWdth of stat component.
        """
        dimensions = (STATS_ROW, STATS_COLUMN)
        size = (width, STATS_HEIGHT)

        super().__init__(master, dimensions, size, **kwargs)

    def draw_stats(
        self, 
        player_stats: tuple[int, int, int]
    ) -> None:
        """ Draws player stats.

        Parameters:
            player_stats: Current player stats (HP, hunger, thirst)
        """
        for stat_index in range(len(player_stats)):
            # Draw player stats in 0 to 3rd coloumn 
            self._draw_stat_label(
                stat_index, STATS_TEXT[stat_index], 
                player_stats[stat_index]
            )

    def draw_coins(
        self,
        num_coins: int
    ) -> None:
        """ Draws the numbers of coins.

        Parameters:
            num_coins: Number of coins in player inventory.
        """
        # Draw coin stat in 4th coloumn 
        self._draw_stat_label(3, "Coins", num_coins)

    def _draw_stat_label(
        self,
        stat_index: int,
        stat_text: str,
        stat_value: int
    ) -> None:
        """ Draws generic stat label in abstract grid.

        Parameter:
            stat_index: Index of stat to draw. 
                        (0 = HP, 1 = hunger, 2 = thirst, 3 = coins)
            stat_text: Text to draw as stat label header.
            stat_value: Number to draw as stat value.
        """
        # Row 0 is stat header
        stat_header_pos = (0, stat_index)
        self.annotate_position(stat_header_pos, stat_text)

        # Row 1 is stat value
        stat_value_pos = (1, stat_index)
        self.annotate_position(stat_value_pos, stat_value)

class InventoryView(tk.Frame):
    """ Displays player inventory in frame. """
    def __init__(
        self,
        master: Union[tk.Tk, tk.Frame], 
        **kwargs
    ) -> None:
        """ Initialises new inventory view.
        
        Parameters:
            master: Root game window.
        """
        super().__init__(master, width = INVENTORY_WIDTH, **kwargs)

    def set_click_callback(
        self, 
        callback: Callable[[str], None]
    ) -> None:
        """ Sets the function to be called when an item is pressed.

        Parameters:
            callback: Function that is called when inventory item is pressed.
        """
        self._item_callback = callback
        
    def clear(self) -> None:
        """ Clears all child widgets from the inventory view. """
        for item_button in self.winfo_children():
            item_button.destroy()

    def draw_inventory(
        self, 
        inventory: Inventory
    ) -> None:
        """ Draws all non-coin items with their quantities.

        Parameters:
            inventory: Modified player inventory without Coin items.
        """
        self._draw_inventory_header()
        for item, value in inventory.get_items().items():
            item_name = item
            item_count = len(value)

            # Item ID is the same for all elements in list 
            # Therefore, retireve instance 0 
            item_colour = ENTITY_COLOURS[value[0].get_id()]

            self._draw_item(item_name, item_count, item_colour)

    def _draw_item(
        self, 
        name: str, 
        num: int, 
        colour: str
    ) -> None:
        """ Creates inventory view item instance and binds click callback.

        Parameters:
            name: Name of inventory item.
            num: Quantity of item in inventory.
            colour: Item background colour.
        """
        item_label = tk.Label(
            self,
            text = f"{name}: {num}",
            font = TEXT_FONT,
            bg = colour
        )
        item_label.pack(
            side = tk.TOP,
            fill = tk.BOTH
        )
        item_label.bind("<Button>", lambda event: self._item_callback(name))

    def _draw_inventory_header(
        self,
    ) -> None:
        """ Draws inventory header label. """
        header_label = tk.Label(
            self,
            text="Inventory",
            font=HEADING_FONT
        )
        header_label.pack(
            side = tk.TOP,
            fill = tk.BOTH
        )

class GraphicalInterface(UserInterface):
    """ A MazeRunner interface that uses GUI to present information.  """
    def __init__(
        self,
        master: tk.Tk,
    ) -> None:
        """ Initialises GUI view.

        Parameters:
            master: root window for GUI.
        """
        self._master = master
        self._master.title(GAME_TITLE)
        self._create_banner_view()

    def create_interface(
        self, 
        dimensions: tuple[int, int]
    ) -> None:
        """ Creates GUI view components.

        Parameters:
            dimensions: The (row, column) dimensions of the current maze.
        """
        self._create_level_view(dimensions)
        self._create_stats_view()
        self._create_inventory_view()

        if TASK == 2:
            self._create_menu_view()
            self._create_controls_frame()

        self._pack_interface()

        self._restrict_window_resize()

    def _create_banner_view(self) -> None:
        """ Creates title banner GUI object. """
        self._banner_view = tk.Label(
            self._master,
            text = GAME_TITLE,
            font = BANNER_FONT,
            bg = THEME_COLOUR
        )

    def _create_level_view(self, dimensions: tuple[int, int]) -> None:
        """ Creates level view GUI object.
        
        Parameters:
            dimensions: The (row, column) dimensions of the current maze.
        """
        level_size = (MAZE_WIDTH, MAZE_HEIGHT)

        if TASK == 2:
            self._level_view = ImageLevelView(
                self._master,
                dimensions,
                level_size
            )
        else:
            self._level_view = LevelView(
                self._master,
                dimensions,
                level_size
            )

    def _create_stats_view(self) -> None:
        """ Creates stats view GUI object. """
        stats_width = MAZE_WIDTH + INVENTORY_WIDTH
        self._stats_view = StatsView(
            self._master,
            stats_width,
            bg = THEME_COLOUR
        )

    def _create_inventory_view(self) -> None:
        """ Creates ivnentory view GUI object. """
        self._inventory_view = InventoryView(
            self._master
        )

    def _create_controls_frame(self) -> None:
        """ Creates control frame GUI object. """
        self._controls_frame = ControlsFrame(
            self._master,
        )
        self._controls_frame.pack(
            side = tk.BOTTOM,
            fill = tk.BOTH,
            expand = tk.TRUE
        )

        self._controls_frame.draw()

    def _create_menu_view(self) -> None:
        """ Creates menu view bar in game header. """
        self._menu_view = MenuView(
            self._master
        )

    def _pack_interface(self) -> None:
        """ Packs component view GUI interfaces. """
        self._banner_view.pack(
            side = tk.TOP,
            expand = tk.TRUE,   
            fill=tk.BOTH
        )
        self._stats_view.pack(
            side = tk.BOTTOM,
            expand = tk.TRUE,
            fill=tk.BOTH
        )
        self._level_view.pack(
            side = tk.LEFT,
            fill=tk.BOTH
        )
        self._inventory_view.pack(
            side = tk.LEFT,
            expand = tk.TRUE,
            fill=tk.BOTH
        )

    def _restrict_window_resize(self) -> None:
        """ Restricts window resizing to minumum required area. """
        root_min_width = (
            self._level_view.winfo_reqwidth() + 
            self._inventory_view.winfo_reqwidth()
        )
        root_min_height = (
            self._banner_view.winfo_reqheight() + 
            self._level_view.winfo_reqheight() + 
            self._stats_view.winfo_reqheight() 
        )

        self._master.minsize(root_min_width, root_min_height)

    def clear_all(self) -> None:
        """ Clears all elements from component view GUI objects. """
        self._level_view.clear()
        self._inventory_view.clear()
        self._stats_view.clear()

    def set_maze_dimensions(
        self, 
        dimensions: tuple[int, int]
    ) -> None:
        """ Updates the dimensions of the current level view GUI object.

        Parameters:
            dimensions: The (row, column) dimensions of the current maze.
        """
        self._level_view.set_dimensions(dimensions)

    def bind_keypress(
        self, 
        command: Callable[[tk.Event], None]
    ) -> None:
        """ Binds command to general keypress event.

        Parameters:
            command: Function to call when key pressed.
        """
        self._master.bind("<Key>", command)
        
    def set_inventory_callback(
        self, 
        callback: Callable[[str], None]
    ) -> None:
        """ Sets the function to be called when an invenotry item is pressed.

        Parameters:
            callback: Function to call when inventory button pressed.
        """
        self._inventory_view.set_click_callback(callback)

    def set_restart_callback(
        self, 
        callback: Callable[[str], None]
    ) -> None:
        """ Sets function to be called when "Restart game" button is pressed.
        
        Parameters:
            callback: Function to call when button pressed.
        """
        self._controls_frame.set_restart_callback(callback)
        self._menu_view.set_restart_callback(callback)

    def set_new_game_callback(
        self, 
        callback: Callable[[str], None]
    ) -> None:
        """ Sets function to be called when "New game" button is pressed.
        
        Parameters:
            callback: Function to call when button pressed.
        """
        self._controls_frame.set_new_game_callback(callback)

    def set_save_game_callback(
        self, 
        callback: Callable[[str], None]
    ) -> None:
        """ Sets function to be called when "Save game" menu is pressed.
        
        Parameters:
            callback: Function to call when button pressed.
        """
        self._menu_view.set_save_callback(callback)

    def set_load_game_callback(
        self, 
        callback: Callable[[str], None]
    ) -> None:
        """ Sets function to be called when "Load game" menu is pressed.
        
        Parameters:
            callback: Function to call when button pressed.
        """
        self._menu_view.set_load_callback(callback)

    def set_quit_game_callback(
        self, 
        callback: Callable[[str], None]
    ) -> None:
        """ Sets function to be called when "Quit" menu is pressed.
        
        Parameters:
            callback: Function to call when button pressed.
        """
        self._menu_view.set_quit_callback(callback)

    def start_timer(self) -> None:
        """ Start the controls frame timer. """
        self._controls_frame.start_timer()

    def stop_timer(self) -> None:
        """ Stops the controls frame timer. """
        self._controls_frame.stop_timer()

    def reset_time(self) -> None:
        """ Reset the controls frame timer. """
        self._controls_frame.reset_timer()

    def get_time(self) -> int:
        """ Get game time. """
        return self._controls_frame.get_time()

    def set_time(self, time: int) -> None:
        """"""
        self._controls_frame.set_time(time)

    def draw(
        self, 
        maze: Maze, 
        items: dict[tuple[int, int], Item], 
        player_position: tuple[int, int], 
        inventory: Inventory, 
        player_stats: tuple[int, int, int],
    ) -> None:
        self._draw_level(maze, items, player_position)
        self._draw_player_stats(player_stats)
        self._draw_inventory(inventory)

    def draw_inventory(
        self, 
        inventory: Inventory
    ) -> None:
        """ Draws items in inventory.

        Parameters:
            inventory: Current player inventory of items.
        """
        self._draw_inventory(inventory)

    def draw_menu(self) -> None:
        """ Draw menu interface. """
        self._menu_view.create_menus()

    def _draw_level(
        self, 
        maze: Maze, 
        items: dict[tuple[int, int], Item], 
        player_position: tuple[int, int]
    ) -> None:
        self._level_view.draw(maze.get_tiles(), items, player_position)

    def _draw_player_stats(
        self, 
        player_stats: tuple[int, int, int]
    ) -> None:
        self._stats_view.draw_stats(player_stats)

    def _draw_inventory(
        self, 
        inventory: Inventory
    ) -> None:
        coins = 0
        modified_inventory = inventory

        if "Coin" in inventory.get_items():
            modified_items = []
            coins = len(inventory.get_items()["Coin"])

            # Create new list of items with coin removed
            for item_group in inventory.get_items().values():
                for item in item_group:
                    if str(item) != COIN:
                        modified_items.append(item)

            # Create new inventory from modified items
            modified_inventory = Inventory(modified_items)

        self._inventory_view.draw_inventory(modified_inventory)
        self._stats_view.draw_coins(coins)

class GraphicalMazeRunner(MazeRunner):
    """ Graphical controller class for a game of MazeRunner. """
    def __init__(self, game_file: str, root: tk.Tk) -> None:
        self._root = root
        self._game_file = game_file
        self._view = GraphicalInterface(root)
        super().__init__(game_file, self._view)

    def _handle_keypress(self, e: tk.Event) -> None:
        """ Handles player input and checks if valid.

        Parameters:
            e: Player key press event. 
        """
        # Check if input character is valid
        # Finished state check stops movement after game halts
        if e.char in MOVE_DELTAS and not self._get_finished_state():
            self._handle_move(e.char)

    def _get_finished_state(self) -> bool:
        """ Returns true if the player has won or lost. """
        return self._model.has_won() or self._model.has_lost()

    def _handle_move(self, move: str) -> None:
        self._model.move_player(MOVE_DELTAS.get(move))
        self._handle_level_update()

    def _handle_level_update(self) -> None:
        """ Checks for model state changes. """
        # Update interface with new maze dimensions if level up
        if self._model.did_level_up():
            self._view.set_maze_dimensions(
                self._model.get_current_maze().get_dimensions()
            )

        # Stop game timer when player finishes 
        if self._get_finished_state() and TASK == 2:
            self._view.stop_timer()

        if self._model.has_won():
            self._create_message_box(WIN_MESSAGE)
            return

        if self._model.has_lost():
            self._create_message_box(LOSS_MESSAGE)
            return

        self._redraw()

    def _handle_restart_game(self) -> None:
        """ Restarts the current game file """
        self._create_new_game_file(self._game_file)

    def _handle_new_game(self) -> None:
        """ Prompts player to enter new game file. """
        self._create_file_prompt(self._create_new_game_file)

    def _handle_save_game(self) -> None:
        """ Save current game state into text file. """
        file_path = filedialog.asksaveasfilename(
            defaultextension='.txt', 
            filetypes=[("Text", '*.txt')], 
            title="Save"
        )
        model = self._model
        time = self._view.get_time()

        if file_path is not None:
            MazeRunnerFile(model=model,file_path=file_path,time=time).save()
        
    def _handle_load_game(self) -> None:
        """ Read current game state from text file. """
        file_path = filedialog.askopenfilename()

        if file_path is not None:
            try:
                model_state = MazeRunnerFile(file_path=file_path).load()
                self._create_new_game_model(
                    model_state[0]
                )
                self._view.set_time(model_state[1])
            except:
                self._create_message_box("Select Valid File Type!")
                
    def _handle_quit_game(self) -> None:
        """ Quit current game. """
        if self._create_message_box_quit():
            self._root.destroy()

    def _create_message_box(self, message: str) -> None:
        """ Creates system message box.

        Parameters:
            message: Text displayed in message box.
        """
        messagebox.showinfo("", message)

    def _create_message_box_quit(self) -> bool:
        """ Creates system message box with yes/no prompt.

        Returns:
            True if the player wants to quit, false otherwise.
        """
        return (messagebox.askquestion(
            "", 
            "Are you sure you want to quit?"
        ) == "yes")

    def _apply_item(self, item_name: str) -> None:
        """ Applies item effects to player.

        Parameters:
            item_name: The applied item's name.
        """
        item = self._model.get_player().get_inventory().remove_item(item_name)
        item.apply(self._model.get_player())
        self._redraw()

    def _create_file_prompt(
        self, 
        callback: Callable[[str], None]
    ) -> None:
        """ Creates top level, level load prompt.

        Parameters:
            callback: Function to call when "Ok" button pressed.
        """
        prompt_window = Toplevel()

        prompt_message = tk.Label(
            prompt_window,
            text="Enter file path:",
            font=TEXT_FONT
        )
        prompt_message.pack(
            expand=tk.TRUE,
            padx=DEFAULT_PADDING,
            pady=DEFAULT_PADDING,
        )

        prompt_input = tk.Entry(
            prompt_window,
        )
        prompt_input.pack(
            expand=tk.TRUE,
            fill=tk.BOTH,
            padx=DEFAULT_PADDING,
            pady=DEFAULT_PADDING,
        )

        prompt_button = tk.Button(
            prompt_window,
            text="OK",
            padx=DEFAULT_PADDING,
            pady=DEFAULT_PADDING,
            command=lambda: [
                prompt_window.withdraw(),
                callback(prompt_input.get())
            ]
        )
        prompt_button.pack(
            expand=tk.TRUE,
            padx=DEFAULT_PADDING,
            pady=DEFAULT_PADDING,
        )

    def _try_open_file(self, game_file: str) -> bool:
        """ Attempts to open file. If unable launches message box.

        Parameters:
            game_file: The path to the game file.

        Returns:
            True if file can be opened, false otherwise.
        """

        try:
            with open(game_file) as file:
                return True
        except (FileNotFoundError):
            self._create_message_box("Path Not Found!")
            return False

    def _create_new_game_model(self, model: Model) -> None:
        """ Creates new game with model.

        Parameters:
            model: New game model.
        """
        self._model = model
        self._view.set_maze_dimensions(
            self._model.get_current_maze().get_dimensions()
        )
        self._view.reset_time()
        self._redraw()

    def _create_new_game_file(self, game_file: str) -> None:
        """ Attempts to create new game with file info.

        Parameters:
            game_file: The path to the game file.
        """
        if self._try_open_file(game_file):
            self._create_new_game_model(Model(game_file))
            self._game_file = game_file

    def play(self) -> None:
        self._view.create_interface(
            self._model.get_current_maze().get_dimensions()
        )
        self._view.set_inventory_callback(self._apply_item)
        self._view.bind_keypress(self._handle_keypress)

        if TASK == 2:
            self._view.set_new_game_callback(self._handle_new_game)
            self._view.set_restart_callback(self._handle_restart_game)
            self._view.set_save_game_callback(self._handle_save_game)
            self._view.set_load_game_callback(self._handle_load_game)
            self._view.set_quit_game_callback(self._handle_quit_game)
            self._view.draw_menu()
            self._view.start_timer()

        self._redraw()

    def _redraw(self) -> None:
        self._view.clear_all()
        super()._redraw()

class ImageLevelView(LevelView):
    """ Displaty maze tiles and entities as images on abstract grid. """
    
    def __init__(
        self,
        master: Union[tk.Tk, tk.Frame], 
        dimensions: tuple[int, int], 
        size: tuple[int, int], 
        **kwargs
    ) -> None:
        """ Initialises image level view. """
        super().__init__(master, dimensions, size, **kwargs)
        self._images_raw = {}  # List of PIL.Image
        self._images_tk = {}  # List of PIL.ImageTK
        self._image_size = self.get_cell_size()

    def _draw_tiles(
        self, 
        tile: Tile,
        tile_pos: tuple[int, int]
    ) -> None:
        self._create_image(
            TILE_IMAGES[tile.get_id()], 
            tile_pos, 
            tile.get_id()
        )

    def _draw_items(
        self,
        item: Item
    ) -> None:
        self._create_image(
            ENTITY_IMAGES[item.get_id()], 
            item.get_position(), 
            item.get_id()
        )

    def _draw_player(
        self,
        player_pos: tuple[int, int]
    ) -> None:
        self._create_image(
            ENTITY_IMAGES[PLAYER], 
            player_pos, 
            PLAYER
        )

    def _create_image(
        self, 
        filename: str, 
        tile_pos: tuple[int, int],
        tile_id: str
    ) -> None:
        """ Draws image of tile cell on level canvas.

        Parameters:
            filename: The path to the image file.
            tile_pos: The grid position (row, column) of the tile to add.
            tile_id: The ID of the tile to add.
        """
        cell_mid = self.get_midpoint(tile_pos)
        cell_size = self.get_cell_size()

        self._store_image(tile_id, filename, cell_size)
        self.create_image(cell_mid, image=self._images_tk[tile_id])

    def _store_image(
        self, 
        tile_id: str, 
        filename: str, 
        size: tuple[int, int]
    ) -> None:
        """ Opens file stream to path and stores PIL.Image in memory.

        Parameters:
            tile_id: The ID of the tile to add.
            filename: The path to the image file.
            size: The desired (width, height) of image.
        """
        # Only add image to dictionary if it has not been proccessed
        if tile_id not in self._images_raw:
            with Image.open(IMAGE_FILE + filename) as tile_image:
                # Create dictionary of raw PIL.Image to limit file reads
                self._images_raw[tile_id] = tile_image

                # Resize PIL.Image to fit current cell size
                self._store_image_tk(
                    tile_id, 
                    self._images_raw[tile_id].resize(size)
                )

        # Update image sizes
        if self._image_size != size:
            self._resize_images_tk(size)
            self._image_size = size
         
    def _store_image_tk(
        self, 
        tile_id: str,
        tile_image: Image
    ) -> None:
        """ Stores processed PIL.ImageTK in memory.

        Parameters:
            tile_id: The ID of the tile to add.
            tile_image: Unprocessed Image to store in dictionary.
        """
        # Create dictionary of raw PIL.ImageTK to stop garbage collection
        self._images_tk[tile_id] = ImageTk.PhotoImage(tile_image)

    def _resize_images_tk(
        self, 
        size: tuple[int, int]
    ) -> None:
        """ Resizes all PIL.ImageTK elements to new size.

        Parameters:
            size: The desired (width, height) of image.
        """
        for tile_id, image in self._images_raw.items():
            self._store_image_tk(tile_id, image.resize(size))

class ControlsFrame(tk.Frame):
    """ Displays game state control buttons and timer GUI objects. """
    def __init__(
        self,
        master,
        **kwargs
    ) -> None:
        """ Initialises controls frame. """
        self._master = master
        self._timer_running = True
        self._time = 0
        super().__init__(master, **kwargs)

    def draw(self) -> None:
        """ Draws the Controls Frame's components. """
        self._create_restart_button()
        self._create_new_game_button()
        self._create_timer()

    def set_restart_callback(
        self,
        callback: Callable[[str], None]
    ) -> None:
        """ Set callback for "Restart game" button.

        Parameters:
            callback: Function to call when button pressed.
        """
        self._restart.config(command=callback)

    def set_new_game_callback(
        self,
        callback: Callable[[str], None]
    ) -> None:
        """ Set callback for "New game" button.

        Parameters:
            callback: Function to call when button pressed.
        """
        self._new_game.config(command=callback)

    def _create_restart_button(self) -> None:
        """ Creates the "Restart game" button. """
        self._restart = tk.Button(
            self,
            text="Restart game",
            font=TEXT_FONT,
        )
        self._restart.pack(
            side=tk.LEFT,
            expand=tk.TRUE,
        )

    def _create_new_game_button(self) -> None:
        """ Creates the "New game" button. """
        self._new_game = tk.Button(
            self,
            text="New game",
            font=TEXT_FONT,
        )
        self._new_game.pack(
            side=tk.LEFT,
            expand=tk.TRUE,
        )

    def _create_timer(self) -> None:
        """ Instantiates the timer frame and labels. """

        # Create parent timer frame
        timer_frame = tk.Frame(
            self
        )
        timer_frame.pack(
            side=tk.LEFT,
            expand=tk.TRUE,
            fill=tk.BOTH
        )

        # Create timer header
        timer_label = tk.Label(
            timer_frame,
            text="Timer",
            font=TEXT_FONT
        )
        timer_label.pack(
            side=tk.TOP,
            fill=tk.BOTH
        )

        # Create timer value
        self._timer_value = tk.Label(
            timer_frame,
            text=self._handle_timer_format(self._time),
            font=TEXT_FONT
        )
        self._timer_value.pack(
            side=tk.TOP,
            fill=tk.BOTH
        )

    def get_time(self) -> int:
        """ Get game time"""
        return self._time

    def set_time(self, time: int) -> None:
        self._time = time

        # Cancel current timer
        self._timer_value.after_cancel(self._timer_update)
        self._timer_value.config(text=self._handle_timer_format(self._time))
        self.start_timer()

    def start_timer(self) -> None:
        """ Starts timer. """
        self._handle_timer()

    def stop_timer(self) -> None:
        """ Stops timer. """
        self._timer_value.after_cancel(self._timer_update)
        
    def reset_timer(self) -> None:
        """ Reset timer. """
        self._time = 0
        self._timer_value.config(text=self._handle_timer_format(self._time))

        # Cancel current timer
        self._timer_value.after_cancel(self._timer_update)
        self.start_timer()

    def _handle_timer(self) -> None:
        """ Increments and formats timer every second. """
        self._timer_value.config(text=self._handle_timer_format(self._time))

        # Recursively call function every second
        self._timer_update = self._timer_value.after(1000, self._handle_timer)
        self._time += 1

    def _handle_timer_format(self, time: int) -> str:
        """ Converts time to minutes and seconds in formatted string.

        Parameters:
            time: Game time in seconds since start.

        Return:
            Formatted string in form Xm Xs
        """
        minutes, seconds = divmod(time, 60)
        return f"{minutes}m {seconds}s"

class MenuView(tk.Menu):
    """
    """
    def __init__(
        self,
        master: Union[tk.Tk, tk.Frame], 
        **kwargs
    ) -> None:
        """ Initialise root file menu.

        Parameters:
            master: Root game window.
        """
        super().__init__(master, **kwargs)
        # Add menu view object to root game window menu bar
        master.config(menu=self)

    def set_save_callback(
        self, 
        callback: Callable[[], None]
    ) -> None:
        """ Set save menu callback. """
        self._save_callback = callback

    def set_load_callback(
        self, 
        callback: Callable[[], None]
    ) -> None:
        """ Set load menu callback. """
        self._load_callback = callback

    def set_restart_callback(
        self, 
        callback: Callable[[], None]
    ) -> None:
        """ Set restart menu callback. """
        self._restart_callback = callback

    def set_quit_callback(
        self, 
        callback: Callable[[], None]
    ) -> None:
        """ Set quit menu callback. """
        self._quit_callback = callback

    def create_menus(self) -> None:
        """ Create file menu within menu view. """
        file_menu = Menu(self)
        self.add_cascade(label="File", menu=file_menu)

        self._create_sub_menu(
            "Save game", 
            file_menu, 
            self._save_callback
        )
        self._create_sub_menu(
            "Load game", 
            file_menu, 
            self._load_callback
        )
        self._create_sub_menu(
            "Restart game", 
            file_menu, 
            self._restart_callback
        )

        file_menu.add_separator()

        self._create_sub_menu(
            "Quit", 
            file_menu, 
            self._quit_callback
        )

    def _create_sub_menu(
        self, 
        menu_name: str, 
        parent_menu: tk.Menu, 
        callback: Callable[[], None]
    ) -> None:
        """ Create sub menu element in parent menu.

        Parameters:
            menu_name: Name of the child menu element.
            parent_menu: Root menu of sub element. 
            callable: Function to call when element is pressed.
        """
        parent_menu.add_command(label=menu_name, command=callback)

class MazeRunnerFile():
    def __init__(
        self,
        **kwargs
    ) -> None:
        """ Initialise Maze Runner File with optional parameters.

        Parameters:
            **kwargs: file_path, model, time
        """

        # Save kwargs variable to object
        for key, value in kwargs.items():
            if key == "file_path":
                self._file_path = value
            elif key == "model":
                self._model = value
            elif key == "time":
                self._time = value

    def save(self) -> None:
        """ Saves model as .txt file as file path. """
        model = self._model
        # Create list of save varaiables
        file_write = []

        level_number = f"Level {model._level_num}"
        file_write.append(self._save_formatting(level_number))

        game_file = f"File {model._game_file}" 
        file_write.append(self._save_formatting(game_file))

        level_entities = f'Entities {model.get_current_items()}'
        file_write.append(self._save_formatting(level_entities))

        inventory_items = (
            f'Inventory {model.get_player_inventory().get_items()}'
        )

        file_write.append(self._save_formatting(inventory_items))

        player_stats = f"Stats {model.get_player_stats()}"
        file_write.append(self._save_formatting(player_stats))

        player_position = f"Position {model.get_player().get_position()}"
        file_write.append(self._save_formatting(player_position))

        game_time = f"Time {self._time}"
        file_write.append(self._save_formatting(game_time))

        with open(self._file_path, "w") as file:
            # Write list of saved variables as .txt file
            file.writelines(file_write)

    def load(self) -> tuple[Model, int]:
        """ Loads a saved game .txt file from file path.

        Returns:
            Tuple with new Model as first element and game time as second.
        """
        level_number = 0
        game_file = ""
        level_entities = {}
        inventory_items = {}
        player_stats = ()
        player_position = ()
        game_time = 0

        with open(self._file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith('Level'):
                    level_number = int(line[6:].split(' ')[0])
                elif line.startswith('File'):
                    game_file = line[5:].split(' ')[0]
                elif line.startswith('Entities'):
                    level_entities = eval(line[9:])
                elif line.startswith('Inventory'):
                    inventory_items = eval(line[10:])
                elif line.startswith('Stats'):
                    player_stats = eval(line[6:])
                elif line.startswith('Position'):
                    player_position = eval(line[9:])
                elif line.startswith('Time '):
                    game_time = int(line[5:])

        # Create new model with loaded game file
        model = Model(game_file)

        # Overwrite required model variable to load state
        model._player = Player(player_position)
        model._player._inventory._items = inventory_items
        model._player._health = player_stats[0]
        model._player._hunger = player_stats[1]
        model._player._thirst = player_stats[2]
        model._level_num = level_number
        model._levels[level_number]._items = level_entities
        model._levels[level_number].attempt_unlock_door()
        
        return (model, game_time)
                    
    def _save_formatting(
        self, 
        save_value: str, 
        remove_chars: Optional[str] = ""
    ) -> str:
        """ Formats save variable and removes optional characters. 
        
        Parameters:
            save_value: Unformatted string needing formatting.
            remove_chars: Optional string of characters for removal.

        Returns:
            Formatted string with attached newline character. 
        """
        for character in remove_chars:
            save_value = save_value.replace(character, "")

        return f"{save_value}\n"

def play_game(root: tk.Tk):
    """ Initialises MazerRunner gameplay. """
    game_file = GAME_FILE
    maze_runner = GraphicalMazeRunner(game_file, root)
    maze_runner.play()

    root.mainloop()

def main():
    """ Entry-point to gameplay. """
    root = tk.Tk()
    play_game(root)

if __name__ == '__main__':
    main()
