import subprocess
import math
import random

import database as db
from tools_data import CATEGORIES

from ursina import *

# --- Bootstrap DB ------------------------------------------------------------
db.init_db()

# --- App ----------------------------------------------------------------------
app = Ursina(
    title='BuiteSuite — Security Research Platform',
    borderless=False,
    development_mode=False,
)
window.color               = color.rgba32(4, 0, 12)
window.exit_button.visible = False
window.fps_counter.enabled = True
camera.position = (0, 0, -14)
camera.fov      = 60


# --- Helper -------------------------------------------------------------------

def mouse_world():
    scale = math.tan(math.radians(camera.fov / 2)) * 14.0 * 2.0
    return Vec3(mouse.x * scale, mouse.y * scale, 0.0)


def _launch(cmd: str):
    """Launch a shell command in a new terminal window."""
    wrapped = f'bash -c "{cmd.replace(chr(34), chr(92)+chr(34))}; echo; echo [DONE — press Enter]; read"'
    for term in ('x-terminal-emulator', 'xterm', 'gnome-terminal', 'konsole'):
        try:
            if term in ('gnome-terminal', 'konsole'):
                subprocess.Popen([term, '--', 'bash', '-c', wrapped])
            else:
                subprocess.Popen([term, '-e', wrapped])
            return True
        except FileNotFoundError:
            continue
    print(f'[EXEC] {cmd}')
    return False


def _copy_to_clipboard(text: str):
    for prog, args in [('xclip', ['-selection', 'clipboard']),
                       ('xsel',  ['--clipboard', '--input'])]:
        try:
            subprocess.run([prog] + args, input=text.encode(), check=True,
                           capture_output=True)
            return True
        except FileNotFoundError:
            continue
    print(f'[COPY] {text}')
    return False


# --- Palette helpers ----------------------------------------------------------

_DARK  = color.rgba32(8,  0, 20, 210)
_PANEL = color.rgba32(12, 0, 28, 220)
_SEL   = color.rgba32(30, 0, 60, 235)
_ACC   = color.rgba32(180, 80, 255, 255)
_DIM   = color.rgba32(120, 80, 180, 170)
_GREEN = color.rgba32(80,  255, 140, 210)
_RED   = color.rgba32(255, 80,  80,  210)
_WHITE = color.rgba32(230, 220, 255, 200)


# ══════════════════════════════════════════════════════════════════════════════
#  MENU SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

class MenuSystem:
    """
    Full-screen overlay menu.
    Left panel  — 14 category buttons.
    Right panel — tool list + command builder + history.
    AI panel    — notes CRUD + usage stats.
    """

    def __init__(self):
        self.is_open       = False
        self.selected_cat  = 0
        self.selected_tool = None
        self._last_target  = ''
        self._note_id_sel  = None   # note selected in AI panel
        self._hud_refs     = []     # idle labels to hide when menu opens

        # UI entity buckets
        self._static   = []   # background + left panel (alive for whole session)
        self._dynamic  = []   # right / AI panel (rebuilt on category change)
        self._cat_btns = []   # refs to category Button objects for re-styling

        # Input field refs (set when panel is built)
        self.target_field     = None
        self.note_title_field = None
        self.note_tags_field  = None
        self.note_body_field  = None

    # -- Lifecycle --------------------------------------------------------------

    def open(self):
        if self.is_open:
            return
        self.is_open = True
        for lbl in self._hud_refs:
            lbl.enabled = False
        self._build_static()
        self._build_right()

    def close(self):
        if not self.is_open:
            return
        self.is_open = False
        for e in self._static + self._dynamic:
            destroy(e)
        self._static.clear()
        self._dynamic.clear()
        self._cat_btns.clear()
        self.target_field = self.note_title_field = None
        self.note_tags_field = self.note_body_field = None
        for lbl in self._hud_refs:
            lbl.enabled = True

    # -- Static left panel ------------------------------------------------------

    def _build_static(self):
        # -- Full screen dim overlay --
        bg = Entity(parent=camera.ui, model='quad',
                    color=color.rgba32(2, 0, 8, 200),
                    scale=(1.85, 1.06), z=0.5)
        self._static.append(bg)

        # -- Left panel background --
        lb = Entity(parent=camera.ui, model='quad',
                    color=_PANEL, scale=(0.50, 1.0), position=(-0.63, 0))
        self._static.append(lb)

        # Left panel top border line
        border_l = Entity(parent=camera.ui, model='quad',
                          color=color.rgba32(100, 40, 180, 180),
                          scale=(0.003, 1.0), position=(-0.38, 0))
        self._static.append(border_l)

        # -- Header bar --
        hdr = Entity(parent=camera.ui, model='quad',
                     color=color.rgba32(15, 0, 35, 240),
                     scale=(1.85, 0.068), position=(0, 0.47))
        self._static.append(hdr)

        t_title = Text('BUITESUITE  COMMAND CENTRE',
                       parent=camera.ui, position=(-0.88, 0.469),
                       scale=1.22, color=color.rgba32(210, 100, 255, 255))
        self._static.append(t_title)

        # Stats summary
        stats = db.get_stats()
        t_stats = Text(
            f"cmds:{stats['commands']}  targets:{stats['targets']}  notes:{stats['notes']}  tools:{stats['tools_used']}",
            parent=camera.ui, position=(0.06, 0.469),
            scale=0.80, color=color.rgba32(120, 100, 160, 180))
        self._static.append(t_stats)

        close_btn = Button(
            text='[ESC]  CLOSE',
            parent=camera.ui,
            scale=(0.14, 0.044),
            position=(0.80, 0.469),
            color=color.rgba32(50, 0, 70, 230),
            on_click=self.close,
        )
        close_btn.text_entity.color = color.rgba32(255, 100, 200, 230)
        close_btn.text_entity.scale = 0.85
        self._static.append(close_btn)

        # -- Category list header --
        t_cat_hdr = Text('-- CATEGORIES --',
                         parent=camera.ui, position=(-0.87, 0.42),
                         scale=0.90, color=_DIM)
        self._static.append(t_cat_hdr)

        # -- Category buttons --
        self._cat_btns.clear()
        for i, cat in enumerate(CATEGORIES):
            self._make_cat_btn(i, cat)

    def _make_cat_btn(self, i, cat):
        r, g, b = cat['color']
        is_sel   = (i == self.selected_cat)
        bg_col   = _SEL if is_sel else _DARK
        txt_col  = color.rgba32(r, g, b, 255) if is_sel \
                   else color.rgba32(int(r*.55), int(g*.55), int(b*.55), 175)

        btn = Button(
            text=f"{'>' if is_sel else '  '} {cat['short']}",
            parent=camera.ui,
            scale=(0.225, 0.044),
            position=(-0.635, 0.375 - i * 0.054),
            color=bg_col,
            on_click=lambda idx=i: self._select_category(idx),
        )
        btn.text_entity.color = txt_col
        btn.text_entity.scale = 0.82
        self._static.append(btn)
        self._cat_btns.append(btn)

    # -- Right panel dispatch ---------------------------------------------------

    def _build_right(self):
        for e in self._dynamic:
            destroy(e)
        self._dynamic.clear()
        self.target_field = self.note_title_field = None
        self.note_tags_field = self.note_body_field = None

        if CATEGORIES[self.selected_cat]['name'] == 'AI Assistant':
            self._build_ai_panel()
        else:
            self._build_tool_panel()

    # -- Tool panel -------------------------------------------------------------

    def _build_tool_panel(self):
        cat  = CATEGORIES[self.selected_cat]
        r, g, b = cat['color']

        # Panel BG
        rb = Entity(parent=camera.ui, model='quad',
                    color=_PANEL, scale=(1.30, 1.0), position=(0.30, 0))
        self._dynamic.append(rb)

        # Category title
        t = Text(f"-- {cat['name'].upper()} --",
                 parent=camera.ui, position=(-0.35, 0.42),
                 scale=1.05, color=color.rgba32(r, g, b, 235))
        self._dynamic.append(t)

        tools    = cat['tools'][:8]          # max 8 rows
        row_h    = 0.052
        top_y    = 0.36

        # -- Tool rows --
        for i, tool in enumerate(tools):
            is_sel = (self.selected_tool and
                      self.selected_tool['name'] == tool['name'])
            bg_c  = _SEL if is_sel else _DARK
            tc    = color.rgba32(r, g, b, 255) if is_sel \
                    else color.rgba32(170, 165, 190, 155)
            label = f"  {'>' if is_sel else ' '} {tool['name']:<16}  {tool['desc'][:42]}"
            btn = Button(
                text=label,
                parent=camera.ui,
                scale=(0.62, 0.042),
                position=(0.30, top_y - i * row_h),
                color=bg_c,
                on_click=lambda t=tool: self._select_tool(t),
            )
            btn.text_entity.color = tc
            btn.text_entity.scale = 0.78
            self._dynamic.append(btn)

        sep_y = top_y - len(tools) * row_h - 0.01
        sep = Text('-' * 75, parent=camera.ui,
                   position=(-0.35, sep_y),
                   scale=0.68, color=color.rgba32(70, 30, 110, 160))
        self._dynamic.append(sep)

        cmd_y = sep_y - 0.045

        # -- Command display --
        cmd_lbl = Text('CMD:', parent=camera.ui,
                       position=(-0.35, cmd_y), scale=0.85,
                       color=_DIM)
        self._dynamic.append(cmd_lbl)

        cmd_str = self.selected_tool['cmd'] if self.selected_tool \
                  else '<- select a tool'
        cmd_val = Text(cmd_str, parent=camera.ui,
                       position=(-0.23, cmd_y), scale=0.83,
                       color=_GREEN)
        self._dynamic.append(cmd_val)
        self._cmd_text_ref = cmd_val

        # -- Target field --
        tgt_y = cmd_y - 0.068
        tgt_lbl = Text('TARGET:', parent=camera.ui,
                       position=(-0.35, tgt_y), scale=0.85, color=_DIM)
        self._dynamic.append(tgt_lbl)

        self.target_field = InputField(
            default_value=self._last_target or 'hostname / IP / path / hash',
            parent=camera.ui,
            scale=(0.50, 0.042),
            position=(0.12, tgt_y),
        )
        self.target_field.color = color.rgba32(10, 0, 22, 245)
        self.target_field.text_field.text_entity.color = _GREEN
        self._dynamic.append(self.target_field)

        # -- Action buttons --
        btn_y = tgt_y - 0.072
        for label, x_off, clr, handler in (
            ('[  EXECUTE  ]',  -0.10, color.rgba32(40, 10, 80, 235), self._execute),
            ('[  COPY CMD ]',   0.10, color.rgba32(20,  5, 50, 235), self._copy),
            ('[  SAVE LOG ]',   0.28, color.rgba32(20,  5, 50, 235), self._save_log),
        ):
            b = Button(text=label, parent=camera.ui,
                       scale=(0.17, 0.046), position=(x_off, btn_y),
                       color=clr, on_click=handler)
            b.text_entity.color = color.rgba32(200, 160, 255, 230)
            b.text_entity.scale = 0.82
            self._dynamic.append(b)

        # -- History --
        hist_y = btn_y - 0.065
        h_hdr = Text('-- RECENT ACTIVITY --', parent=camera.ui,
                     position=(-0.35, hist_y), scale=0.85,
                     color=color.rgba32(90, 70, 130, 180))
        self._dynamic.append(h_hdr)

        history = db.get_history(6)
        for i, row in enumerate(history):
            target, category, tool, command, success, ts = (
                row['target'], row['category'], row['tool'],
                row['command'], row['success'], row['executed_at'])
            icon = '+' if success else '-'
            ic   = _GREEN if success else color.rgba32(160, 130, 200, 155)
            short_cmd = command[:48] + ('...' if len(command) > 48 else '')
            line = Text(
                f'  {icon}  {tool:<14}  {(target or "-")[:16]:<17}  {short_cmd}',
                parent=camera.ui,
                position=(-0.35, hist_y - 0.048 - i * 0.042),
                scale=0.77, color=ic,
            )
            self._dynamic.append(line)

    # -- AI Assistant panel -----------------------------------------------------

    def _build_ai_panel(self):
        # Panel BG
        rb = Entity(parent=camera.ui, model='quad',
                    color=_PANEL, scale=(1.30, 1.0), position=(0.30, 0))
        self._dynamic.append(rb)

        t = Text('-- AI RESEARCH ASSISTANT --',
                 parent=camera.ui, position=(-0.35, 0.42),
                 scale=1.05, color=color.rgba32(180, 100, 255, 235))
        self._dynamic.append(t)

        # -- Usage stats bar --
        stats = db.get_stats()
        st = Text(
            f"total commands: {stats['commands']}   unique targets: {stats['targets']}   saved notes: {stats['notes']}",
            parent=camera.ui, position=(-0.35, 0.36),
            scale=0.80, color=color.rgba32(130, 100, 200, 190))
        self._dynamic.append(st)

        # -- Top tools --
        top_lbl = Text('TOP TOOLS BY USAGE:',
                       parent=camera.ui, position=(-0.35, 0.30),
                       scale=0.83, color=color.rgba32(100, 180, 255, 200))
        self._dynamic.append(top_lbl)

        for i, row in enumerate(db.get_top_tools(5)):
            tool, cat, cnt = row['tool'], row['category'], row['use_count']
            tt = Text(
                f"  {i+1}.  {tool:<18} {cnt:>4}x   [{cat}]",
                parent=camera.ui,
                position=(-0.35, 0.255 - i * 0.042),
                scale=0.80, color=color.rgba32(180, 160, 220, 175))
            self._dynamic.append(tt)

        sep1 = Text('-' * 75, parent=camera.ui,
                    position=(-0.35, 0.045),
                    scale=0.68, color=color.rgba32(70, 30, 110, 160))
        self._dynamic.append(sep1)

        # -- Notes --
        notes_lbl = Text('RESEARCH NOTES:',
                         parent=camera.ui, position=(-0.35, 0.00),
                         scale=0.85, color=color.rgba32(180, 100, 255, 210))
        self._dynamic.append(notes_lbl)

        notes = db.get_notes(limit=5)
        for i, row in enumerate(notes):
            nid, title, content, tags, created = (
                row['id'], row['title'], row['content'],
                row['tags'], row['created_at'])
            is_sel = (nid == self._note_id_sel)
            bg_c   = _SEL if is_sel else _DARK
            tc     = _ACC if is_sel else color.rgba32(170, 130, 220, 190)

            btn = Button(
                text=f"  {'>' if is_sel else ' '} {title[:38]}",
                parent=camera.ui,
                scale=(0.54, 0.042),
                position=(0.04, -0.045 - i * 0.050),
                color=bg_c,
                on_click=lambda n=nid, ti=title, co=content, tg=tags:
                         self._select_note(n, ti, co, tg),
            )
            btn.text_entity.color = tc
            btn.text_entity.scale = 0.82
            self._dynamic.append(btn)

            del_btn = Button(
                text='[X]',
                parent=camera.ui,
                scale=(0.052, 0.042),
                position=(0.64, -0.045 - i * 0.050),
                color=color.rgba32(50, 0, 0, 220),
                on_click=lambda n=nid: self._delete_note(n),
            )
            del_btn.text_entity.color = _RED
            del_btn.text_entity.scale = 0.80
            self._dynamic.append(del_btn)

        sep2 = Text('-' * 75, parent=camera.ui,
                    position=(-0.35, -0.31),
                    scale=0.68, color=color.rgba32(70, 30, 110, 160))
        self._dynamic.append(sep2)

        # -- Note editor --
        new_lbl = Text('NEW / EDIT NOTE:', parent=camera.ui,
                       position=(-0.35, -0.355), scale=0.85,
                       color=color.rgba32(180, 100, 255, 210))
        self._dynamic.append(new_lbl)

        for lbl_text, y_off, attr in (
            ('TITLE:',   -0.405, 'note_title_field'),
            ('TAGS:',    -0.455, 'note_tags_field'),
            ('CONTENT:', -0.455 - 0.050, 'note_body_field'),
        ):
            lbl = Text(lbl_text, parent=camera.ui,
                       position=(-0.35, y_off), scale=0.82, color=_DIM)
            self._dynamic.append(lbl)

            field = InputField(
                default_value=lbl_text.lower().replace(':', '').strip(),
                parent=camera.ui,
                scale=(0.50, 0.040),
                position=(0.12, y_off),
            )
            field.color = color.rgba32(10, 0, 22, 245)
            field.text_field.text_entity.color = color.rgba32(190, 130, 255, 230)
            setattr(self, attr, field)
            self._dynamic.append(field)

        save_note_btn = Button(
            text='[  SAVE NOTE  ]',
            parent=camera.ui,
            scale=(0.20, 0.046),
            position=(0.05, -0.615),
            color=color.rgba32(40, 10, 80, 235),
            on_click=self._save_note,
        )
        save_note_btn.text_entity.color = _ACC
        save_note_btn.text_entity.scale = 0.82
        self._dynamic.append(save_note_btn)

    # -- Action handlers --------------------------------------------------------

    def _select_category(self, idx):
        self.selected_cat  = idx
        self.selected_tool = None
        # Rebuild left panel to update highlight without destroying everything
        for btn in self._cat_btns:
            destroy(btn)
        self._cat_btns.clear()
        static_no_btns = self._static[:]
        self._static.clear()
        for e in static_no_btns:
            self._static.append(e)  # keep bg/headers
        for i, cat in enumerate(CATEGORIES):
            self._make_cat_btn(i, cat)
        self._build_right()

    def _select_tool(self, tool):
        self.selected_tool = tool
        self._build_right()

    def _execute(self):
        if not self.selected_tool:
            return
        target  = self.target_field.text_field.text.strip() if self.target_field else ''
        self._last_target = target
        cmd = self.selected_tool['cmd'].replace('{target}', target)
        cat = CATEGORIES[self.selected_cat]['name']
        launched = _launch(cmd)
        db.log_command(target, cat, self.selected_tool['name'], cmd,
                       success=launched)
        self._build_right()  # refresh history

    def _copy(self):
        if not self.selected_tool:
            return
        target = self.target_field.text_field.text.strip() if self.target_field else ''
        cmd    = self.selected_tool['cmd'].replace('{target}', target)
        _copy_to_clipboard(cmd)

    def _save_log(self):
        if not self.selected_tool:
            return
        target = self.target_field.text_field.text.strip() if self.target_field else ''
        cat    = CATEGORIES[self.selected_cat]['name']
        cmd    = self.selected_tool['cmd'].replace('{target}', target)
        db.log_command(target, cat, self.selected_tool['name'], cmd, success=True)
        self._build_right()

    def _select_note(self, note_id, title, content, tags):
        self._note_id_sel = note_id
        self._build_ai_panel()
        # Pre-fill editor fields
        if self.note_title_field:
            self.note_title_field.text_field.text = title
        if self.note_tags_field:
            self.note_tags_field.text_field.text = tags or ''
        if self.note_body_field:
            self.note_body_field.text_field.text = content or ''

    def _delete_note(self, note_id):
        db.delete_note(note_id)
        if self._note_id_sel == note_id:
            self._note_id_sel = None
        self._build_ai_panel()

    def _save_note(self):
        title   = (self.note_title_field.text_field.text if self.note_title_field else '').strip()
        tags    = (self.note_tags_field.text_field.text  if self.note_tags_field  else '').strip()
        content = (self.note_body_field.text_field.text  if self.note_body_field  else '').strip()
        if not title:
            return
        if self._note_id_sel:
            db.update_note(self._note_id_sel, title, content, tags)
        else:
            cat = CATEGORIES[self.selected_cat]['name']
            db.save_note(title, content, tags, cat)
        self._note_id_sel = None
        self._build_ai_panel()


# ══════════════════════════════════════════════════════════════════════════════
#  ORB VISUAL SUBSYSTEMS
# ══════════════════════════════════════════════════════════════════════════════

class InnerCrystal:
    def __init__(self, parent):
        self.nucleus = Entity(parent=parent, model='sphere', scale=0.55,
                              color=color.rgba32(245, 210, 255, 235))
        self.bars = [
            Entity(parent=parent, model='cube', scale=(0.09, 1.8, 0.09),
                   color=color.rgba32(210, 150, 255, 150)),
            Entity(parent=parent, model='cube', scale=(0.09, 1.8, 0.09),
                   rotation=(90, 0, 0), color=color.rgba32(210, 150, 255, 150)),
            Entity(parent=parent, model='cube', scale=(0.09, 1.8, 0.09),
                   rotation=(0, 0, 90), color=color.rgba32(210, 150, 255, 150)),
        ]
        tips = [(0,.95,0),(0,-.95,0),(.95,0,0),(-.95,0,0),(0,0,.95),(0,0,-.95)]
        self.gems = [
            Entity(parent=parent, model='sphere', scale=0.17,
                   position=Vec3(*p), color=color.rgba32(255, 230, 255, 210))
            for p in tips
        ]
        self.orbiters = [
            (Entity(parent=parent, model='sphere', scale=0.11,
                    color=color.rgba32(255, 180, 255, 185)), i * 60)
            for i in range(6)
        ]

    def update(self, t, p, cp):
        v = int(min(255, 200 + p * 55 + cp * 55))
        self.nucleus.color = color.rgba32(v, int(v * .8), 255, 228)
        self.nucleus.scale = 0.55 * (1 + math.sin(t * 3.8) * .13 + cp * .22)
        for i, bar in enumerate(self.bars):
            bar.rotation_y = t * 50 * (1 if i % 2 == 0 else -1)
            bar.rotation_z = t * 32 * (.8 + i * .35)
            bar.color = color.rgba32(210, 140, 255, int(min(255, 128 + p*72 + cp*58)))
        for i, gem in enumerate(self.gems):
            pk = 1 + math.sin(t * 5 + i * 1.05) * .22
            gem.scale = 0.17 * pk
            gem.color  = color.rgba32(255, 220, 255, int(min(255, 165 + p*90 + cp*50)))
        for orb, base in self.orbiters:
            a = math.radians(t * 88 + base)
            r = 0.88
            orb.position = Vec3(r * math.cos(a),
                                r * math.sin(a) * math.sin(math.radians(58)),
                                r * math.sin(a) * math.cos(math.radians(58)))
            orb.color = color.rgba32(255, 185, 255, int(min(255, 148 + p * 107)))


class EnergyTendril:
    N = 12
    def __init__(self):
        self.nodes  = [Entity(model='sphere', scale=.001,
                              color=color.rgba32(200,100,255,0)) for _ in range(self.N)]
        self.active = False; self.ttl = 0.0
        self.src = Vec3(0,0,0); self.dst = Vec3(0,0,0)

    def fire(self, src, dst):
        self.src = src; self.dst = dst; self.active = True
        self.ttl = random.uniform(.06, .16)

    def update(self, dt, p):
        if not self.active:
            for n in self.nodes: n.scale = .001
            return
        self.ttl -= dt
        if self.ttl <= 0: self.active = False; return
        dx = self.dst.x-self.src.x; dy = self.dst.y-self.src.y; dz = self.dst.z-self.src.z
        L  = max(.01, math.sqrt(dx*dx+dy*dy+dz*dz))
        nm = min(L*.28, .9)
        for i, node in enumerate(self.nodes):
            f  = i/(self.N-1)
            bx = self.src.x+dx*f; by = self.src.y+dy*f; bz = self.src.z+dz*f
            e  = math.sin(f*math.pi)*nm
            node.position = Vec3(bx+random.uniform(-e,e), by+random.uniform(-e,e), bz+random.uniform(-e,e))
            sz = .11 if i==0 else (.08 if i==self.N-1 else (.09 if i%4==2 else .044))
            node.scale = sz*p*(0.6+random.random()*.7)
            a = int(min(255, 180*p*(0.5+random.random()*.5)))
            node.color = color.rgba32(min(255,195+random.randint(-20,30)), 65+random.randint(-20,40), 255, a)


class SurfaceFlare:
    def __init__(self):
        self.e = Entity(model='sphere', scale=.001, color=color.rgba32(255,200,255,0))
        self.active=False; self.life=0; self.ml=.4
        self.cd=random.uniform(.4,2.8); self.tmr=random.uniform(0,2.5)
        self.pos=Vec3(0,0,2.5)

    def _new_pos(self):
        t=random.uniform(0,math.tau); p=random.uniform(0,math.pi); r=2.48
        return Vec3(r*math.sin(p)*math.cos(t), r*math.sin(p)*math.sin(t), r*math.cos(p))

    def update(self, dt, p):
        if not self.active:
            self.tmr += dt
            if self.tmr >= self.cd*(1.-.65*p):
                self.active=True; self.life=0
                self.ml=random.uniform(.2,.65); self.tmr=0; self.pos=self._new_pos()
            return
        self.life += dt
        if self.life >= self.ml:
            self.active=False; self.e.scale=.001; self.cd=random.uniform(.4,2.8); return
        prog=self.life/self.ml
        af=(prog/.15) if prog<.15 else max(0., 1.-(prog-.15)/.85); af=af**.55
        pk=1+math.sin(self.life*35)*.3
        self.e.position=self.pos; self.e.scale=af*pk*(.14+p*.11)
        self.e.color=color.rgba32(255, int(155+af*100), 255, int(min(255,af*(208+p*47))))


class NebulaCloud:
    def __init__(self):
        self.nodes=[]
        for _ in range(55):
            t=random.uniform(0,math.tau); p=random.uniform(0,math.pi); r=random.uniform(3.8,7.5)
            pos=[r*math.sin(p)*math.cos(t), r*math.sin(p)*math.sin(t), r*math.cos(p)]
            vel=[random.uniform(-.08,.08), random.uniform(-.04,.12), random.uniform(-.08,.08)]
            sz=random.uniform(.07,.2); ba=random.randint(5,18)
            node=Entity(model='sphere',scale=sz,position=tuple(pos),color=color.rgba32(110,0,210,ba))
            self.nodes.append([node,pos,vel,ba])

    def update(self, dt, p):
        for data in self.nodes:
            node,pos,vel,ba=data
            pos[0]+=vel[0]*dt; pos[1]+=vel[1]*dt; pos[2]+=vel[2]*dt
            if math.sqrt(pos[0]**2+pos[1]**2+pos[2]**2) > 8.0:
                vel[0]*=-1; vel[1]*=-1; vel[2]*=-1
            node.position=tuple(pos); node.color=color.rgba32(110,0,210,int(min(255,ba+p*22)))


class ScanRing:
    def __init__(self, parent):
        self.ring=Entity(parent=parent,model='sphere',scale=(2.6,.04,2.6),color=color.rgba32(200,160,255,0))
        self.active=False; self.y=-3.5; self.timer=random.uniform(3,7)

    def update(self, dt, p):
        self.timer -= dt
        if not self.active:
            if self.timer<=0: self.active=True; self.y=-3.5; self.timer=random.uniform(4,9)
            return
        self.y+=dt*6; self.ring.y=self.y
        inside=abs(self.y)<2.4
        a=int(min(255,65+p*105)) if inside else int(max(0,(2.4-abs(self.y))/0.8*(48+p*80)))
        self.ring.color=color.rgba32(200,160,255,a)
        if self.y>4: self.active=False; self.ring.color=color.rgba32(200,160,255,0)


class OrbParticle:
    _PAL=[(180,0,255),(200,60,255),(220,130,255),(242,210,255)]
    _WGT=[.55,.25,.12,.08]
    def __init__(self):
        self.entity=Entity(model='sphere',scale=.001); self._spawn(stagger=True)
    def _col(self):
        r=random.random(); acc=0.
        for c,w in zip(self._PAL,self._WGT):
            acc+=w
            if r<acc: return c
        return self._PAL[0]
    def _spawn(self, stagger=False):
        t=random.uniform(0,math.tau); p=random.uniform(0,math.pi); rad=random.uniform(2.1,2.9)
        self.px=rad*math.sin(p)*math.cos(t); self.py=rad*math.sin(p)*math.sin(t); self.pz=rad*math.cos(p)
        spd=random.uniform(.22,1.1); n=1./rad
        self.vx=self.px*n*spd*.5+random.uniform(-.18,.18)
        self.vy=self.py*n*spd*.5+random.uniform(.06,.42)
        self.vz=self.pz*n*spd*.5+random.uniform(-.18,.18)
        self.bsz=random.uniform(.05,.17); self.ml=random.uniform(1.2,3.8)
        self.life=random.uniform(0,self.ml) if stagger else 0.; self.c=self._col()
    def update(self, dt, p):
        self.life+=dt
        if self.life>=self.ml: self._spawn(); return
        m=1.+p*1.3
        self.px+=self.vx*dt*m; self.py+=self.vy*dt*m; self.pz+=self.vz*dt*m
        pr=self.life/self.ml
        af=(pr/.12) if pr<.12 else (1. if pr<.72 else 1.-(pr-.72)/.28)
        twk=1.+math.sin(self.life*13+self.px*4)*.22
        self.entity.scale=self.bsz*af*twk; self.entity.position=(self.px,self.py,self.pz)
        a=int(min(255,af*(145+p*110)))
        self.entity.color=color.rgba32(self.c[0],self.c[1],self.c[2],a)


class OrbRing:
    def __init__(self, radius, speed, tilt_deg, n=11):
        self.radius=radius; self.speed=speed; self.tilt=math.radians(tilt_deg)
        self.angle=random.uniform(0,360)
        step=360./n
        self.nodes=[(Entity(model='sphere',scale=random.uniform(.045,.115),
                            color=color.rgba32(200,80,255,42)),step*i) for i in range(n)]
    def update(self, dt, p):
        self.angle+=self.speed*dt*(1.+p*.55)
        alpha=int(min(255,36+p*95))
        for node,off in self.nodes:
            a=math.radians(self.angle+off)
            node.position=(self.radius*math.cos(a),
                           self.radius*math.sin(a)*math.cos(self.tilt),
                           self.radius*math.sin(a)*math.sin(self.tilt))
            node.color=color.rgba32(200,80,255,alpha)


# ══════════════════════════════════════════════════════════════════════════════
#  PURPLE ORB  (master orchestrator)
# ══════════════════════════════════════════════════════════════════════════════

class PurpleOrb:
    def __init__(self, menu):
        self.menu        = menu
        self.t           = 0.0
        self.proximity   = 0.0
        self.click_pulse = 0.0
        self.lean_rx     = 0.0
        self.lean_ry     = 0.0
        self._tdl_timer  = 0.0

        self.pivot = Entity()

        self.core = Entity(parent=self.pivot, model='sphere',
                           color=color.rgba32(165,0,255), scale=2.4, collider='sphere')
        self.core.on_click = self._on_click

        self.halos = [
            Entity(parent=self.pivot,model='sphere',color=color.rgba32(175,0,255, 65),scale=3.1),
            Entity(parent=self.pivot,model='sphere',color=color.rgba32(150,0,240, 38),scale=3.8),
            Entity(parent=self.pivot,model='sphere',color=color.rgba32(120,0,200, 18),scale=4.8),
            Entity(parent=self.pivot,model='sphere',color=color.rgba32( 90,0,160,  8),scale=6.2),
        ]
        self.chr_r=Entity(parent=self.pivot,model='sphere',color=color.rgba32(255,0,150,10),scale=3.22)
        self.chr_b=Entity(parent=self.pivot,model='sphere',color=color.rgba32(30,80,255, 8),scale=3.02)

        self.crystal  = InnerCrystal(parent=self.pivot)
        self.scan     = ScanRing(parent=self.pivot)
        self.flares   = [SurfaceFlare() for _ in range(8)]
        self.tendrils = [EnergyTendril() for _ in range(5)]
        self.nebula   = NebulaCloud()
        self.particles= [OrbParticle()  for _ in range(80)]
        self.rings    = [OrbRing(radius=3.5,speed=25,tilt_deg=15),
                         OrbRing(radius=4.2,speed=-18,tilt_deg=65),
                         OrbRing(radius=3.0,speed=40,tilt_deg=-40)]

    def _on_click(self):
        if self.menu.is_open:
            return
        self.click_pulse = 1.0
        for i in range(3):
            invoke(self._make_ring, delay=i*.1)
        self.menu.open()

    def _make_ring(self):
        ring=Entity(model='sphere',scale=(.2,.012,.2),color=color.rgba32(215,80,255,210))
        ring.animate('scale',Vec3(10,.012,10),duration=.85,curve=curve.out_expo)
        ring.animate('color',color.rgba32(215,80,255,0),duration=.85)
        destroy(ring,delay=.9)

    def _tick_tendrils(self, dt, p):
        if p < .28:
            for td in self.tendrils: td.update(dt,p); return
        self._tdl_timer+=dt
        interval=max(.04,.14-p*.10)
        if self._tdl_timer>=interval:
            self._tdl_timer=0.
            for td in self.tendrils:
                if not td.active:
                    th=random.uniform(0,math.tau); ph=random.uniform(.4,math.pi-.4); r=2.52
                    src=Vec3(r*math.sin(ph)*math.cos(th), r*math.sin(ph)*math.sin(th), r*math.cos(ph)-.8)
                    mw=mouse_world(); vec=mw-src
                    vl=math.sqrt(vec.x**2+vec.y**2+vec.z**2)
                    if vl>.01:
                        sc=min(1.,5./vl); dst=src+Vec3(vec.x*sc,vec.y*sc,vec.z*sc)
                    else:
                        dst=src
                    td.fire(src,dst); break
        for td in self.tendrils: td.update(dt,p)

    def update(self, dt):
        # Slow down / dim when menu is open
        menu_open = self.menu.is_open
        if menu_open:
            dt *= 0.25

        self.t+=dt; t=self.t
        raw=math.sqrt(mouse.x**2+mouse.y**2)
        self.proximity+=(max(0.,1.-raw*2.8)-self.proximity)*min(1.,dt*6)
        self.click_pulse=max(0.,self.click_pulse-dt*2.5)
        p=self.proximity; cp=self.click_pulse

        self.lean_rx+=(-mouse.y*15.-self.lean_rx)*min(1.,dt*4)
        self.lean_ry+=( mouse.x*15.-self.lean_ry)*min(1.,dt*4)
        self.pivot.rotation_x=self.lean_rx; self.pivot.rotation_y=self.lean_ry

        freq=1.7+p*2.1; amp=.10+p*.22+cp*.30; pulse=1.+math.sin(t*freq)*amp
        hue=math.sin(t*.65)*22
        rv=int(min(255,max(0,148+p*62+cp*45+hue))); bv=int(min(255,max(0,218+p*37-hue*.4)))
        self.core.color=color.rgba32(rv,0,bv); self.core.scale=(2.4+cp*.5)*pulse; self.core.rotation_y=t*10

        specs=[(3.1,.76,-7,175,0,255,58,92),(3.8,.80,5,150,0,240,32,55),
               (4.8,.55,0,120,0,200,14,28),(6.2,.40,0,90,0,160,5,13)]
        for halo,(bs,af,rs,hr,hg,hb,ba,pa) in zip(self.halos,specs):
            hp=1.+math.sin(t*freq*.7+.5)*(amp*af); halo.scale=bs*hp
            if rs: halo.rotation_y=t*rs
            halo.color=color.rgba32(hr,hg,hb,int(min(255,ba+p*pa+cp*25)))

        self.chr_r.scale=3.22+math.sin(t*1.4)*.14
        self.chr_b.scale=3.02+math.sin(t*1.2+1.)*.11
        self.chr_r.color=color.rgba32(255,30,180,int(9+p*18))
        self.chr_b.color=color.rgba32(30,100,255,int(7+p*14))

        self.crystal.update(t,p,cp)
        self.scan.update(dt,p)
        for f in self.flares:    f.update(dt,p)
        if not menu_open:
            self._tick_tendrils(dt,p)
        for part in self.particles: part.update(dt,p)
        for ring in self.rings:     ring.update(dt,p)


# --- Starfield ----------------------------------------------------------------

for _ in range(200):
    Entity(model='sphere', scale=random.uniform(.012,.052),
           position=(random.uniform(-30,30),random.uniform(-20,20),random.uniform(6,24)),
           color=color.rgba32(random.randint(160,255),random.randint(70,170),255,random.randint(45,165)))


# --- HUD labels (idle state) --------------------------------------------------

_hud_title  = Text('BUITESUITE', position=(0,.43), scale=3.0,
                   color=color.rgba32(210,110,255,225), origin=(0,0))
_hud_sub    = Text('Security Research Platform  -  Click the Orb',
                   position=(0,-.44), scale=1.1, color=color.rgba32(155,75,205,155), origin=(0,0))
_hud_armed  = Text('[ SYSTEM ARMED ]', position=(-.85,.46), scale=.88,
                   color=color.rgba32(100,255,180,120), origin=(-1,0))
_hud_ver    = Text('v0.2.0', position=(.85,-.46), scale=.85,
                   color=color.rgba32(120,60,180,100), origin=(1,0))

prox_text = Text('PROXIMITY: 0.00', position=(-.85,.41), scale=.88,
                 color=color.rgba32(100,200,255,90), origin=(-1,0))
tdl_text  = Text('TENDRILS:  0 / 5', position=(-.85,.36), scale=.88,
                 color=color.rgba32(255,155,90,90), origin=(-1,0))

# --- Wire it up & run ---------------------------------------------------------

menu_system = MenuSystem()
menu_system._hud_refs = [_hud_title, _hud_sub, _hud_armed, _hud_ver, prox_text, tdl_text]
orb         = PurpleOrb(menu=menu_system)


def update():
    orb.update(time.dt)
    if not menu_system.is_open:
        prox_text.text = f'PROXIMITY: {orb.proximity:.2f}'
        active = sum(1 for td in orb.tendrils if td.active)
        tdl_text.text  = f'TENDRILS:  {active} / {len(orb.tendrils)}'


def input(key):
    if key == 'escape' and menu_system.is_open:
        menu_system.close()
    elif key == 'space' and not menu_system.is_open:
        orb.click_pulse = 0.8
        for i in range(2):
            invoke(orb._make_ring, delay=i * .12)
        menu_system.open()


app.run()
