"""Desktop viewer for Icy Grid World; run with the project Python environment."""

import tkinter as tk
from tkinter import ttk

import gymnasium as gym
import icy_gridworld
from policy_playback import POLICY_FILES, DEFAULT_POLICY, load_policy, requested_action


class GridViewer:
    CELL = 28
    PAD = 24

    def __init__(self, root):
        self.root = root
        self.env = gym.make("IcyGridWorld-v0")
        self.running = False
        self.timer = None
        self.done = False
        self.total = 0.0
        self.policy = None
        self.observation = 380
        self.policy_name = tk.StringVar(value=DEFAULT_POLICY)
        root.title("Icy Grid World")
        root.configure(bg="#edf4f8")
        root.resizable(False, False)
        main = ttk.Frame(root, padding=18)
        main.pack()
        ttk.Label(main, text="Icy Grid World", font=("Segoe UI", 22, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(main, text="Reach the gold. Ice can send you sideways.").grid(row=1, column=0, sticky="w", pady=(0, 12))
        size = 20 * self.CELL + 2 * self.PAD
        self.canvas = tk.Canvas(main, width=size, height=size, bg="#edf4f8", highlightthickness=0)
        self.canvas.grid(row=2, column=0, rowspan=8)
        controls = ttk.Frame(main, padding=(18, 0, 0, 0))
        controls.grid(row=2, column=1, sticky="nw")
        ttk.Label(controls, text="Policy").pack(anchor="w")
        self.policy_select = ttk.Combobox(controls, textvariable=self.policy_name,
            values=tuple(POLICY_FILES), state="readonly", width=29)
        self.policy_select.pack(fill="x", pady=(3, 8))
        self.policy_select.bind("<<ComboboxSelected>>", lambda event: self.reset())
        ttk.Label(controls, text="Saved policies play greedily. Ice still slips.\nSARSA and Q-learning are learned policies.",
                  wraplength=235).pack(anchor="w", pady=(0, 8))
        ttk.Label(controls, text="CONTROLS", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(controls, text="Arrow keys or direction buttons\n80% intended · 10% each side").pack(anchor="w", pady=(6, 14))
        arrows = ttk.Frame(controls)
        arrows.pack()
        self.buttons = []
        for name, action, row, col in (("Up", 0, 0, 1), ("Left", 3, 1, 0), ("Down", 2, 1, 1), ("Right", 1, 1, 2)):
            button = ttk.Button(arrows, text=name, width=7, command=lambda a=action: self.manual(a))
            button.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(button)
            root.bind("<" + name + ">", lambda event, a=action: self.manual(a))
        self.play = ttk.Button(controls, text="Play policy", command=self.toggle)
        self.play.pack(fill="x", pady=(14, 5))
        self.single_step = ttk.Button(controls, text="Policy step", command=self.policy_step)
        self.single_step.pack(fill="x", pady=(0, 5))
        ttk.Button(controls, text="Reset episode", command=self.reset).pack(fill="x")
        ttk.Label(controls, text="Seed (nonnegative integer)").pack(anchor="w", pady=(16, 3))
        self.seed = tk.StringVar(value="123")
        ttk.Entry(controls, textvariable=self.seed, width=18).pack(fill="x")
        ttk.Label(controls, text="Applied on reset. Action seed = seed + 1.", wraplength=230).pack(anchor="w", pady=5)
        self.status = tk.StringVar()
        ttk.Label(controls, textvariable=self.status, wraplength=235, justify="left", font=("Segoe UI", 11)).pack(anchor="w", pady=16)
        ttk.Label(controls, text="Blue circle: explorer\nGold star: goal\nDark tiles: rocks\nOutline: starting cell\n\n500-step episode limit", justify="left").pack(anchor="w")
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.reset()

    def stop(self):
        self.running = False
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        self.play.configure(text="Play policy")

    def reset(self):
        try:
            seed = int(self.seed.get())
            if seed < 0:
                raise ValueError
        except ValueError:
            self.stop()
            self.status.set("Enter a nonnegative integer seed, then reset.")
            return
        self.stop()
        try:
            self.policy = load_policy(self.policy_name.get())
        except (ValueError, FileNotFoundError) as error:
            self.done = True
            self.play.configure(state="disabled")
            self.single_step.configure(state="disabled")
            self.status.set(str(error))
            return
        self.env.action_space.seed(seed + 1)
        obs, _ = self.env.reset(seed=seed)
        self.observation = obs
        self.done = False
        self.total = 0.0
        self.play.configure(state="normal")
        self.single_step.configure(state="normal")
        for button in self.buttons:
            button.configure(state="normal")
        self.status.set(f"{self.policy_name.get()}\nReady\nSteps: 0 / 500\nTotal reward: 0\nPosition: (19, 0)")
        self.draw(obs)

    def draw(self, observation):
        canvas = self.canvas
        canvas.delete("all")
        for r in range(20):
            for c in range(20):
                x, y = self.PAD + c * self.CELL, self.PAD + r * self.CELL
                fill = "#34495e" if (r, c) in self.env.unwrapped.obstacles else "#dceef7"
                canvas.create_rectangle(x, y, x + self.CELL, y + self.CELL, fill=fill, outline="#b8d2df")
        if self.policy is not None:
            for state, action in enumerate(self.policy):
                if action not in (0, 1, 2, 3) or state == 19:
                    continue
                r, c = divmod(state, 20)
                if (r, c) in self.env.unwrapped.obstacles:
                    continue
                cx = self.PAD + (c + .5) * self.CELL
                cy = self.PAD + (r + .5) * self.CELL
                dx, dy = ((0, -7), (7, 0), (0, 7), (-7, 0))[action]
                canvas.create_line(cx-dx/2, cy-dy/2, cx+dx, cy+dy,
                                   arrow=tk.LAST, fill="#63849a", width=1)
        for i in range(20):
            offset = self.PAD + i * self.CELL + self.CELL / 2
            canvas.create_text(offset, 12, text=str(i), fill="#4a6374", font=("Segoe UI", 8))
            canvas.create_text(12, offset, text=str(i), fill="#4a6374", font=("Segoe UI", 8))
        def center(cell):
            return self.PAD + (cell[1] + .5) * self.CELL, self.PAD + (cell[0] + .5) * self.CELL
        sx, sy = center(self.env.unwrapped.start)
        canvas.create_rectangle(sx-12, sy-12, sx+12, sy+12, outline="#24819b", width=2)
        gx, gy = center(self.env.unwrapped.goal)
        canvas.create_text(gx, gy, text="★", fill="#b87900", font=("Segoe UI", 23))
        position = divmod(observation, 20)
        x, y = center(position)
        canvas.create_oval(x-10, y-10, x+10, y+10, fill="#158364" if position == self.env.unwrapped.goal else "#236ed1", outline="white", width=2)
        canvas.create_text(x, y, text="✓" if position == self.env.unwrapped.goal else "A", fill="white", font=("Segoe UI", 11, "bold"))

    def manual(self, action):
        self.stop()
        self.step(action)
        return "break"

    def step(self, action):
        if self.done:
            return
        obs, reward, terminated, truncated, info = self.env.step(action)
        self.observation = obs
        self.total += reward
        self.done = terminated or truncated
        names = ("Up", "Right", "Down", "Left")
        outcome = "Gold reached!" if terminated else "Time limit reached" if truncated else "Following policy"
        if terminated and truncated:
            outcome = "Gold reached on step 500!"
        self.status.set(f"{self.policy_name.get()}\n{outcome}\nSteps: {info['steps']} / 500\nReward: {reward:+.0f}   Total: {self.total:.0f}\nPosition: {info['position']}\n\nRequested: {names[action]}\nExecuted: {names[info['executed_action']]}\nSlipped: {info['slipped']}\nBlocked: {info['blocked']}\n\nTerminated: {terminated}\nTruncated: {truncated}")
        self.draw(obs)
        if self.done:
            self.stop()
            self.play.configure(state="disabled")
            self.single_step.configure(state="disabled")
            for button in self.buttons:
                button.configure(state="disabled")

    def policy_step(self):
        self.stop()
        if not self.done:
            self.step(requested_action(self.policy, self.observation, self.env.action_space))

    def toggle(self):
        if self.running:
            self.stop()
        elif not self.done:
            self.running = True
            self.play.configure(text="Pause")
            self.tick()

    def tick(self):
        self.timer = None
        if self.running:
            self.step(requested_action(self.policy, self.observation, self.env.action_space))
            if self.running:
                self.timer = self.root.after(250, self.tick)

    def close(self):
        self.stop()
        self.env.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    GridViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
