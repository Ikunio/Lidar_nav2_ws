#!/usr/bin/env python3
"""
GUI 键盘遥控器 - ROS 2
Apple 风格界面，WASD 控制，Shift 加速，空格急停
毛玻璃背景 + 大字体
"""

import tkinter as tk
import threading
import random
from PIL import Image, ImageFilter, ImageDraw

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# ── Apple 风格配色（低饱和度） ────────────────────────────────────────────
BG          = '#1e1e1e'
BG_CARD     = '#2c2c2e'      # 卡片（略偏暖灰）
BG_KEY      = '#3a3a3c'      # 按键默认
BG_KEY_ON   = '#5e6a78'      # 按键按下（低饱和蓝灰）
BG_KEY_BOOST= '#c9a86c'      # Shift 加速（低饱和暖金）
BG_ESTOP    = '#a85858'      # 急停（低饱和红）
BG_TRACK    = '#38383a'      # 滑块轨道
FG          = '#f0f0f2'      # 主文字
FG_SEC      = '#98989a'      # 次要文字
FG_VAL      = '#f5f5f7'      # 数值高亮
FG_MUTED    = '#6e6e70'      # 弱化文字
BORDER      = '#3a3a3c'
ACCENT      = '#7aaccc'      # 强调色（低饱和蓝）
GREEN       = '#72b88a'      # 状态绿
RED         = '#c07070'      # 状态红
DIVIDER     = '#38383a'

# 高斯模糊背景参数
WIN_W, WIN_H = 780, 640


def rounded_rect(canvas, x, y, w, h, r, fill, outline=''):
    points = [
        x + r, y, x + r, y, x + w - r, y, x + w - r, y,
        x + w, y, x + w, y + r, x + w, y + r, x + w, y + h - r,
        x + w, y + h, x + w, y + h, x + w - r, y + h, x + w - r, y + h,
        x + r, y + h, x + r, y + h, x, y + h, x, y + h - r,
        x, y + r, x, y + r, x, y,
    ]
    canvas.create_polygon(points, fill=fill, outline=outline, smooth=True)


def generate_blur_bg(w, h):
    """生成 macOS 风格高斯模糊背景"""
    img = Image.new('RGB', (w, h), (28, 28, 30))
    draw = ImageDraw.Draw(img)

    # 随机柔和光斑
    random.seed(42)
    blobs = [
        (int(w * 0.15), int(h * 0.25), 180, (45, 50, 70)),
        (int(w * 0.75), int(h * 0.15), 160, (50, 55, 65)),
        (int(w * 0.5),  int(h * 0.6),  220, (40, 48, 62)),
        (int(w * 0.85), int(h * 0.75), 150, (55, 50, 60)),
        (int(w * 0.2),  int(h * 0.8),  170, (42, 52, 58)),
        (int(w * 0.4),  int(h * 0.1),  130, (48, 45, 65)),
    ]
    for bx, by, r, color in blobs:
        for i in range(r, 0, -2):
            alpha = max(0, min(255, int(20 * (i / r))))
            c = tuple(min(255, ch + alpha // 3) for ch in color)
            draw.ellipse([bx - i, by - i, bx + i, by + i], fill=c)

    # 大半径高斯模糊
    img = img.filter(ImageFilter.GaussianBlur(radius=60))
    return img


class GuiTeleopNode(Node):
    def __init__(self):
        super().__init__('gui_teleop_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('GUI Teleop 节点已启动')


class RoundedFrame(tk.Canvas):
    def __init__(self, parent, radius=16, bg_color=BG_CARD, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent['bg'], **kwargs)
        self._radius = radius
        self._bg_color = bg_color
        self._inner = tk.Frame(self, bg=bg_color)
        self.create_window(0, 0, window=self._inner, anchor='nw')
        self.bind('<Configure>', self._draw)

    def _draw(self, event=None):
        self.delete('bg')
        w, h = self.winfo_width(), self.winfo_height()
        if w > 1 and h > 1:
            rounded_rect(self, 0, 0, w, h, self._radius, self._bg_color, outline='', tags='bg')
        self.tag_lower('bg')

    @property
    def inner(self):
        return self._inner


class KeyWidget(tk.Canvas):
    def __init__(self, parent, label, w=74, h=56, **kwargs):
        super().__init__(parent, width=w, height=h, highlightthickness=0, bd=0,
                         bg=parent['bg'], **kwargs)
        self._label = label
        self._active = False
        self._boost = False
        self._estop = False
        self._draw()

    def _draw(self):
        self.delete('all')
        w, h = int(self['width']), int(self['height'])
        r = 14
        if self._estop:
            fill = BG_ESTOP
            fg = '#fff'
        elif self._active:
            fill = BG_KEY_BOOST if self._boost else BG_KEY_ON
            fg = '#fff'
        else:
            fill = BG_KEY
            fg = FG_SEC
        rounded_rect(self, 0, 0, w, h, r, fill)
        self.create_text(w // 2, h // 2, text=self._label, fill=fg,
                         font=('Helvetica Neue', 18, 'bold'))

    def set_state(self, active, boost=False, estop=False):
        if self._active != active or self._boost != boost or self._estop != estop:
            self._active = active
            self._boost = boost
            self._estop = estop
            self._draw()


class TeleopGUI:
    def __init__(self, node: GuiTeleopNode):
        self.node = node
        self.pressed = set()
        self.linear_x = 0.0
        self.linear_y = 0.0
        self.angular_z = 0.0
        self.max_linear = 0.5
        self.max_angular = 1.0
        self.estop = False
        self.boost_factor = 2.0
        self.prev_lx = 0.0
        self.prev_ly = 0.0
        self.prev_az = 0.0
        self.speed = 0.0
        self.accel = 0.0
        self.ang_accel = 0.0

        self.root = tk.Tk()
        self.root.title('Teleop')
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.geometry(f'{WIN_W}x{WIN_H}')
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)

        # 生成高斯模糊背景
        self._bg_photo = self._make_bg()
        self._bg_label = tk.Label(self.root, image=self._bg_photo, borderwidth=0)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self._build_ui()
        self._bind_keys()

        self.timer = self.node.create_timer(0.05, self.publish_cmd)
        self.tick()

    def _make_bg(self):
        img = generate_blur_bg(WIN_W, WIN_H)
        from PIL import ImageTk
        return ImageTk.PhotoImage(img)

    def _card(self, parent, **pack_kwargs):
        cf = RoundedFrame(parent, radius=18, bg_color=BG_CARD)
        cf.pack(**pack_kwargs)
        return cf.inner

    def _build_ui(self):
        # 所有子组件的父容器放在背景之上
        overlay = tk.Frame(self.root, bg='')
        overlay.place(x=0, y=0, relwidth=1, relheight=1)

        # 标题
        title = tk.Frame(overlay, bg=BG)
        title.pack(fill='x', padx=32, pady=(24, 4))
        tk.Label(title, text='Teleop', font=('Helvetica Neue', 28, 'bold'),
                 bg=BG, fg=FG).pack(side='left')
        tk.Label(title, text='W A S D  ·  Q E  ·  Shift  ·  Space',
                 font=('Helvetica Neue', 12), bg=BG, fg=FG_MUTED).pack(side='right')

        # 主内容
        body = tk.Frame(overlay, bg=BG)
        body.pack(fill='both', expand=True, padx=32, pady=(14, 18))

        # ── 左列：速度 ──
        left = self._card(body, side='left', fill='both', expand=True, padx=(0, 10))

        tk.Label(left, text='Velocity', font=('Helvetica Neue', 13),
                 bg=BG_CARD, fg=FG_SEC).pack(anchor='w', padx=24, pady=(20, 12))

        self.vel_labels = {}
        names = [('Linear X', 'lx'), ('Linear Y', 'ly'), ('Angular Z', 'az')]
        for i, (name, key) in enumerate(names):
            row = tk.Frame(left, bg=BG_CARD)
            row.pack(fill='x', padx=24, pady=(0, 2))
            tk.Label(row, text=name, font=('Helvetica Neue', 12), bg=BG_CARD, fg=FG_SEC
                     ).pack(side='left')
            lbl = tk.Label(row, text='0.000', font=('Helvetica Neue', 22, 'bold'),
                           bg=BG_CARD, fg=FG_VAL, anchor='e')
            lbl.pack(side='right')
            self.vel_labels[key] = lbl
            if i < len(names) - 1:
                tk.Frame(left, bg=DIVIDER, height=1).pack(fill='x', padx=24, pady=10)

        # 速度 & 加速度概览
        tk.Frame(left, bg=DIVIDER, height=1).pack(fill='x', padx=24, pady=(14, 10))

        overview = tk.Frame(left, bg=BG_CARD)
        overview.pack(fill='x', padx=24, pady=(0, 4))
        overview.columnconfigure(0, weight=1)
        overview.columnconfigure(1, weight=1)

        # 左半：速度
        sp_col = tk.Frame(overview, bg=BG_CARD)
        sp_col.grid(row=0, column=0, sticky='w')
        tk.Label(sp_col, text='Speed', font=('Helvetica Neue', 11),
                 bg=BG_CARD, fg=FG_MUTED).pack(anchor='w')
        self.speed_label = tk.Label(sp_col, text='0.000', font=('Helvetica Neue', 20, 'bold'),
                                     bg=BG_CARD, fg=GREEN)
        self.speed_label.pack(anchor='w')
        tk.Label(sp_col, text='m/s', font=('Helvetica Neue', 10),
                 bg=BG_CARD, fg=FG_MUTED).pack(anchor='w')

        # 右半：加速度
        ac_col = tk.Frame(overview, bg=BG_CARD)
        ac_col.grid(row=0, column=1, sticky='e')
        tk.Label(ac_col, text='Accel', font=('Helvetica Neue', 11),
                 bg=BG_CARD, fg=FG_MUTED).pack(anchor='e')
        self.accel_label = tk.Label(ac_col, text='0.000', font=('Helvetica Neue', 20, 'bold'),
                                     bg=BG_CARD, fg=ACCENT)
        self.accel_label.pack(anchor='e')
        tk.Label(ac_col, text='m/s²', font=('Helvetica Neue', 10),
                 bg=BG_CARD, fg=FG_MUTED).pack(anchor='e')

        # 速度条
        tk.Frame(left, bg=DIVIDER, height=1).pack(fill='x', padx=24, pady=(14, 10))
        self.bars = {}
        for name, key in [('X', 'bx'), ('Y', 'by'), ('Z', 'bz')]:
            row = tk.Frame(left, bg=BG_CARD)
            row.pack(fill='x', padx=24, pady=3)
            tk.Label(row, text=name, font=('Helvetica Neue', 11), bg=BG_CARD,
                     fg=FG_MUTED, width=2).pack(side='left')
            c = tk.Canvas(row, bg=BG_TRACK, height=8, highlightthickness=0)
            c.pack(fill='x', padx=(10, 0), expand=True)
            self.bars[key] = c

        # ── 中列：按键 ──
        center = tk.Frame(body, bg=BG)
        center.pack(side='left', padx=10)

        keys_frame = tk.Frame(center, bg=BG)
        keys_frame.pack()

        layout = [
            ('Q', 0, 0), ('W', 1, 0), ('E', 2, 0),
            ('A', 0, 1), ('S', 1, 1), ('D', 2, 1),
        ]
        self.key_widgets = {}
        for label, col, row in layout:
            kw = KeyWidget(keys_frame, label)
            kw.grid(row=row, column=col, padx=6, pady=6)
            self.key_widgets[label.lower()] = kw

        self.shift_widget = KeyWidget(center, 'Shift  ×2', w=240, h=48)
        self.shift_widget.pack(pady=(12, 0))

        self.space_widget = KeyWidget(center, 'Emergency Stop', w=240, h=48)
        self.space_widget.pack(pady=(8, 0))

        # ── 右列：设置 ──
        right = self._card(body, side='right', fill='both', expand=True, padx=(10, 0))

        tk.Label(right, text='Settings', font=('Helvetica Neue', 13),
                 bg=BG_CARD, fg=FG_SEC).pack(anchor='w', padx=24, pady=(20, 10))

        self.linear_var = tk.DoubleVar(value=self.max_linear)
        self._slider(right, 'Max Linear', self.linear_var, 0.1, 2.0, 'm/s')

        self.angular_var = tk.DoubleVar(value=self.max_angular)
        self._slider(right, 'Max Angular', self.angular_var, 0.1, 4.0, 'rad/s')

        tk.Frame(right, bg=DIVIDER, height=1).pack(fill='x', padx=24, pady=(18, 14))

        btn_frame = tk.Frame(right, bg=BG_CARD)
        btn_frame.pack(fill='x', padx=24, pady=6)
        self.estop_btn_canvas = tk.Canvas(btn_frame, height=48, highlightthickness=0,
                                           bd=0, bg=BG_CARD, cursor='hand2')
        self.estop_btn_canvas.pack(fill='x')
        self.estop_btn_canvas.bind('<Button-1>', lambda e: self.toggle_estop())

        # 底部状态
        status = tk.Frame(overlay, bg=BG)
        status.pack(fill='x', side='bottom', padx=32, pady=(0, 18))
        self.status_dot = tk.Canvas(status, width=10, height=10, highlightthickness=0,
                                     bg=BG)
        self.status_dot.pack(side='left', padx=(0, 10))
        self.status_label = tk.Label(status, text='Ready',
                                      font=('Helvetica Neue', 12), bg=BG, fg=FG_SEC)
        self.status_label.pack(side='left')
        tk.Label(status, text='/cmd_vel', font=('Helvetica Neue', 12),
                 bg=BG, fg=FG_MUTED).pack(side='right')

    def _slider(self, parent, label, var, from_, to, unit):
        frame = tk.Frame(parent, bg=BG_CARD)
        frame.pack(fill='x', padx=24, pady=5)
        top = tk.Frame(frame, bg=BG_CARD)
        top.pack(fill='x')
        tk.Label(top, text=label, font=('Helvetica Neue', 12), bg=BG_CARD, fg=FG_SEC
                 ).pack(side='left')
        val_lbl = tk.Label(top, text=f'{var.get():.2f} {unit}',
                           font=('Helvetica Neue', 12, 'bold'), bg=BG_CARD, fg=FG_VAL)
        val_lbl.pack(side='right')

        slider = tk.Scale(frame, variable=var, from_=from_, to=to, orient='horizontal',
                          bg=BG_CARD, fg=FG, troughcolor=BG_TRACK, highlightthickness=0,
                          bd=0, showvalue=False, resolution=0.05, sliderlength=24,
                          command=lambda v, vl=val_lbl, u=unit:
                              vl.config(text=f'{float(v):.2f} {u}'))
        slider.pack(fill='x', pady=(6, 0))

    def _bind_keys(self):
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.focus_set()

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key in ('shift_l', 'shift_r'):
            self.pressed.add('shift')
        elif key in ('w', 'a', 's', 'd', 'q', 'e', 'space'):
            self.pressed.add(key)
            if key == 'space':
                self.estop = not self.estop

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in ('shift_l', 'shift_r'):
            self.pressed.discard('shift')
        else:
            self.pressed.discard(key)

    def toggle_estop(self):
        self.estop = not self.estop

    def publish_cmd(self):
        self.max_linear = self.linear_var.get()
        self.max_angular = self.angular_var.get()

        lx, ly, az = 0.0, 0.0, 0.0
        if not self.estop:
            boost = self.boost_factor if 'shift' in self.pressed else 1.0
            lin = self.max_linear * boost
            ang = self.max_angular * boost
            if 'w' in self.pressed: lx += lin
            if 's' in self.pressed: lx -= lin
            if 'a' in self.pressed: az += ang
            if 'd' in self.pressed: az -= ang
            if 'q' in self.pressed: ly += lin
            if 'e' in self.pressed: ly -= lin

        self.linear_x, self.linear_y, self.angular_z = lx, ly, az

        # 速度大小
        self.speed = (lx**2 + ly**2) ** 0.5

        # 加速度 = d(v)/dt，dt = 0.05s
        dt = 0.05
        dv = ((lx - self.prev_lx)**2 + (ly - self.prev_ly)**2) ** 0.5
        self.accel = dv / dt
        self.ang_accel = abs(az - self.prev_az) / dt
        self.prev_lx, self.prev_ly, self.prev_az = lx, ly, az

        msg = Twist()
        msg.linear.x = lx
        msg.linear.y = ly
        msg.angular.z = az
        self.node.publisher_.publish(msg)

    def tick(self):
        boost = 'shift' in self.pressed

        for key, widget in self.key_widgets.items():
            widget.set_state(key in self.pressed, boost=boost, estop=self.estop)

        self.shift_widget.set_state(boost, boost=True)
        self.space_widget.set_state(self.estop, estop=self.estop)

        for key, val in [('lx', self.linear_x), ('ly', self.linear_y),
                         ('az', self.angular_z)]:
            self.vel_labels[key].config(
                text=f'{val:+.3f}',
                fg=ACCENT if abs(val) > 0.001 else FG_MUTED)

        # 速度 & 加速度
        self.speed_label.config(text=f'{self.speed:.3f}',
                                fg=GREEN if self.speed > 0.001 else FG_MUTED)
        self.accel_label.config(text=f'{self.accel:.3f}',
                                fg=ACCENT if self.accel > 0.01 else FG_MUTED)

        bar_w = 180
        for key, val, max_v in [('bx', self.linear_x, max(self.max_linear, 0.01)),
                                 ('by', self.linear_y, max(self.max_linear, 0.01)),
                                 ('bz', self.angular_z, max(self.max_angular, 0.01))]:
            c = self.bars[key]
            c.delete('all')
            ratio = min(abs(val) / max_v, 1.0)
            w = int(ratio * bar_w)
            if w > 0:
                rounded_rect(c, 0, 0, w, 8, 4, ACCENT if abs(val) > 0.001 else '#48484a')

        # 急停按钮
        self.estop_btn_canvas.delete('all')
        cw = self.estop_btn_canvas.winfo_width()
        if cw > 1:
            fill = BG_ESTOP if self.estop else BG_KEY
            text = 'Release' if self.estop else 'E-STOP'
            rounded_rect(self.estop_btn_canvas, 0, 0, cw, 48, 14, fill)
            self.estop_btn_canvas.create_text(
                cw // 2, 24, text=text, fill='#fff',
                font=('Helvetica Neue', 14, 'bold'))

        # 状态栏
        is_moving = any(k in self.pressed for k in ('w', 'a', 's', 'd', 'q', 'e'))
        self.status_dot.delete('all')
        if self.estop:
            dot_color = RED
            status_text = 'E-Stop'
        elif is_moving:
            dot_color = GREEN
            status_text = 'Moving'
        else:
            dot_color = FG_MUTED
            status_text = 'Ready'
        self.status_dot.create_oval(0, 0, 10, 10, fill=dot_color, outline='')
        self.status_label.config(text=status_text, fg=dot_color)

        self.root.after(50, self.tick)

    def on_close(self):
        msg = Twist()
        self.node.publisher_.publish(msg)
        self.node.destroy_node()
        rclpy.shutdown()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    node = GuiTeleopNode()
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    gui = TeleopGUI(node)
    gui.run()


if __name__ == '__main__':
    main()
