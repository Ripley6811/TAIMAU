#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Allow importing relative to the "src" directory.
import sys
sys.path.append('src')

from src import main

app = main.TaimauApp(None, debug=False)
app.title('Taimau')
app.mainloop()