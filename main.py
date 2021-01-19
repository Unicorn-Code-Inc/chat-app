import urwid # This is for testing, if the .exe file doesn't work I'll look for another library, or I'll use JavaScript (It'll take some time tho)

def exit_on_q(key):
    if key in ("q", "Q"):
        raise urwid.ExitMainLoop()
        

palette = [
    ('banner', 'black', 'light gray'),
    ('streak', 'black', 'dark red'),
    ('bg', 'black', 'dark blue'),
]

txt = urwid.Text(('banner', u" Hello World "), align='center')
map1 = urwid.AttrMap(txt, 'streak')
fill = urwid.Filler(map1)
map2 = urwid.AttrMap(fill, 'bg')
loop = urwid.MainLoop(map2, palette, unhandled_input=exit_on_q)
loop.run()
