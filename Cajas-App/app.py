import wx
import database


def on_press(frame, event):
        value = frame.text_ctrl.GetValue()
        if not value:
            print("You didn't enter anything!")
        else:
            print("You typed:"+value)

class ExampleFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='No mas filas!')
        font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.BOLD)
        wx.Window.SetFont(self, font)  
        self.panel = wx.Panel(self)        
        self.quote = wx.StaticText(self.panel, label="Turno Actual :")
        self.result = wx.StaticText(self.panel, label="")
        self.result.SetForegroundColour(wx.RED)
        self.button = wx.Button(self.panel, label="Actualizar caja")
        self.button2 = wx.Button(self.panel, label="Siguiente Turno!")
        self.lblname = wx.StaticText(self.panel, label="Caja # ")
        self.editname = wx.TextCtrl(self.panel, size=(140, -1))

        # Set sizer for the frame, so we can change frame size to match widgets
        self.windowSizer = wx.BoxSizer(wx.VERTICAL)
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)        

        # Set sizer for the panel content
        self.sizer = wx.GridBagSizer(7, 7)
        self.sizer.Add(self.quote, (5, 0))
        self.sizer.Add(self.result, (5, 1))
        self.sizer.Add(self.button2, (7, 1))
        self.sizer.Add(self.lblname, (1, 1))
        self.sizer.Add(self.editname, (1, 2))
        self.sizer.Add(self.button, (3, 0), (0, 7), flag=wx.EXPAND)

        # Set simple sizer for a nice border
        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5) 

        # Use the sizers
        self.panel.SetSizerAndFit(self.border)  
        self.SetSizerAndFit(self.windowSizer)  

        # Set event handlers
        self.button.Bind(wx.EVT_BUTTON, self.OnButton)
        self.button2.Bind(wx.EVT_BUTTON, self.OnButton2)

    def OnButton(self, e):
        self.result.SetLabel(str( database.get_next( int(self.editname.GetValue()) )) )

    def OnButton2(self, e):
        caja = int(self.editname.GetValue()) 
        cliente = database.next(caja)
        self.result.SetLabel(str(cliente)) 

app = wx.App(False)
frame = ExampleFrame(None)
frame.Show()
app.MainLoop()