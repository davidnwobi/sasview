
import wx
import sys
import colorsys
import numpy
from sans.guiframe.utils import format_number, check_float
from invariant_widgets import OutputTextCtrl
# Dimensions related to chart
RECTANGLE_WIDTH  = 400.0  
RECTANGLE_HEIGHT = 20
#Invariant panel size 
_BOX_WIDTH = 76

#scale to use for a bar of value zero
RECTANGLE_SCALE  = 0.0001
DEFAULT_QSTAR = 1.0  
  
if sys.platform.count("win32")>0:
    _STATICBOX_WIDTH = 450
    PANEL_WIDTH = 500
    PANEL_HEIGHT = 430
    FONT_VARIANT = 0
else:
    _STATICBOX_WIDTH = 480
    PANEL_WIDTH = 530
    PANEL_HEIGHT = 430
    FONT_VARIANT = 1
    
  
    
class InvariantContainer(wx.Object):
    def __init__(self):
        #invariant at low range
        self.qstar_low = 0.0
        #invariant at low range error
        self.qstar_low_err = 0.0
        #invariant 
        self.qstar = 0.0
        #invariant error
        self.qstar_err = 0.0
        #invariant at high range
        self.qstar_high = 0.0
        #invariant at high range error
        self.qstar_high_err = 0.0
        #invariant total
        self.qstar_total = None
        #invariant error
        self.qstar_total_err = None
        #scale
        self.qstar_low_percent = 0.0
        self.qstar_high_percent = 0.0
        self.qstar_percent = 0.0
        # warning message
        self.existing_warning = False
        self.warning_msg = "No Details on calculations available...\n"
        
    def compute_percentage(self):
        """
            Compute percentage of each invariant
        """
        if self.qstar_total is not None and self.qstar_total != 0:
            #compute invariant percentage
            if self.qstar is None:
                self.qstar = 0.0
            self.qstar_percent = self.qstar/self.qstar_total
            #compute low q invariant percentage
            if self.qstar_low is None:
                self.qstar_low = 0.0
            self.qstar_low_percent = self.qstar_low/self.qstar_total
            #compute high q invariant percentage
            if self.qstar_high is None:
                self.qstar_high = 0.0
            self.qstar_high_percent = self.qstar_high/self.qstar_total
        self.check_values()
   
    def check_values(self):
        """
            check the validity if invariant
        """
        #warning to the user when the extrapolated invariant is greater than %5
        if self.qstar_low_percent >= 0.05:
            self.existing_warning = True
            self.warning_msg += "Extrapolated contribution at Low Q is higher "
            self.warning_msg += "than 5% of the invariant.\n"
        if self.qstar_high_percent >= 0.05:
            self.existing_warning = True
            self.warning_msg += "Extrapolated contribution at High Q is higher "
            self.warning_msg += "than 5% of the invariant.\n"
        if self.qstar_low_percent + self.qstar_high_percent >= 0.05:
            self.existing_warning = True
            self.warning_msg += "The sum of all extrapolated contributions is higher "
            self.warning_msg += "than 5% of the invariant.\n"
            
        if self.existing_warning:
            self.warning_msg += "The calculations are likely to be unreliable!\n"
        else:
            self.warning_msg = "No Details on calculations available...\n"
            
class InvariantDetailsPanel(wx.Dialog):
    """
        This panel describes proportion of invariants 
    """
    def __init__(self, parent=None, id=-1, qstar_container=None, title="",
                 size=(PANEL_WIDTH, PANEL_HEIGHT)):
        wx.Dialog.__init__(self, parent, id=id, title=title, size=size)
        
        #Font size 
        self.SetWindowVariant(variant=FONT_VARIANT)
        self.parent = parent
        #self.qstar_container
        self.qstar_container = qstar_container
        #warning message
        self.warning_msg = self.qstar_container.warning_msg
   
        #Define scale of each bar
        self.low_inv_percent = self.qstar_container.qstar_low_percent
        self.low_scale = self.get_scale(percentage=self.low_inv_percent,
                                         scale_name="Extrapolated at Low Q")
        self.inv_percent = self.qstar_container.qstar_percent
        self.inv_scale = self.get_scale(percentage=self.inv_percent, 
                                            scale_name="Inv in Q range")
        self.high_inv_percent = self.qstar_container.qstar_high_percent
        self.high_scale = self.get_scale(percentage=self.high_inv_percent,
                                         scale_name="Extrapolated at High Q")
        
        #Default color the extrapolation bar is grey
        self.extrapolation_color_low = wx.Colour(169,  169, 168, 128)
        self.extrapolation_color_high = wx.Colour(169,  169, 168, 128)
        #change color of high and low bar when necessary
        self.set_color_bar()
        #draw the panel itself
        self._do_layout()
        self.set_values()
   
    def _define_structure(self):
        """
            Define main sizers needed for this panel
        """
        #Box sizers must be defined first before defining buttons/textctrls (MAC).
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        #Sizer related to chart
        chart_box = wx.StaticBox(self, -1, "Invariant Chart")
        self.chart_sizer = wx.StaticBoxSizer(chart_box, wx.VERTICAL)
        self.chart_sizer.SetMinSize((PANEL_WIDTH - 50,100))
        #Sizer related to invariant values
        self.invariant_sizer =  wx.GridBagSizer(4, 4)
        invariant_box = wx.StaticBox(self, -1, "Numerical Values")
        self.invariant_box_sizer = wx.StaticBoxSizer(invariant_box,
                                                      wx.HORIZONTAL)

        self.invariant_box_sizer.SetMinSize((PANEL_WIDTH - 50,-1))
        #Sizer related to warning message
        warning_box = wx.StaticBox(self, -1, "Warning")
        self.warning_sizer = wx.StaticBoxSizer(warning_box, wx.VERTICAL)
        self.warning_sizer.SetMinSize((PANEL_WIDTH-50,-1))
        #Sizer related to button
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
      
    def _layout_shart(self):
        """
            Draw widgets related to chart
        """
        self.panel_chart = wx.Panel(self)
        self.panel_chart.Bind(wx.EVT_PAINT, self.on_paint)
        self.chart_sizer.Add(self.panel_chart, 1, wx.EXPAND|wx.ALL, 0)
        
    def _layout_invariant(self):
        """
            Draw widgets related to invariant
        """
        uncertainty = "+/-" 
        unit_invariant = '[1/(cm * A)]'
     
        invariant_txt = wx.StaticText(self, -1, 'Invariant')
        self.invariant_tcl = OutputTextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_tcl.SetToolTipString("Invariant in the data set's Q range.")
        self.invariant_err_tcl = OutputTextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_err_tcl.SetToolTipString("Uncertainty on the invariant.")
        invariant_units_txt = wx.StaticText(self, -1, unit_invariant)
       
        invariant_low_txt = wx.StaticText(self, -1, 'Invariant in low-Q region')
        self.invariant_low_tcl = OutputTextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_low_tcl.SetToolTipString("Invariant computed with the extrapolated low-Q data.")
        self.invariant_low_err_tcl = OutputTextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_low_err_tcl.SetToolTipString("Uncertainty on the invariant.")
        invariant_low_units_txt = wx.StaticText(self, -1,  unit_invariant)
        
        invariant_high_txt = wx.StaticText(self, -1, 'Invariant in high-Q region')
        self.invariant_high_tcl = OutputTextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_high_tcl.SetToolTipString("Invariant computed with the extrapolated high-Q data")
        self.invariant_high_err_tcl = OutputTextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_high_err_tcl.SetToolTipString("Uncertainty on the invariant.")
        invariant_high_units_txt = wx.StaticText(self, -1,  unit_invariant)
   
        #Invariant low
        iy = 0
        ix = 0 
        self.invariant_sizer.Add(invariant_low_txt, (iy, ix), (1,1),
                             wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        self.invariant_sizer.Add(self.invariant_low_tcl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix += 1
        self.invariant_sizer.Add( wx.StaticText(self, -1, uncertainty),
                         (iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix += 1
        self.invariant_sizer.Add(self.invariant_low_err_tcl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1
        self.invariant_sizer.Add(invariant_low_units_txt
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0)  
        #Invariant 
        iy += 1
        ix = 0 
        self.invariant_sizer.Add(invariant_txt, (iy, ix), (1,1),
                             wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        self.invariant_sizer.Add(self.invariant_tcl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix += 1
        self.invariant_sizer.Add(wx.StaticText(self, -1, uncertainty),
                         (iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix += 1
        self.invariant_sizer.Add(self.invariant_err_tcl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix +=1
        self.invariant_sizer.Add(invariant_units_txt
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0)  
        #Invariant high
        iy += 1
        ix = 0 
        self.invariant_sizer.Add(invariant_high_txt, (iy, ix), (1,1),
                             wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        self.invariant_sizer.Add(self.invariant_high_tcl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix += 1
        self.invariant_sizer.Add(wx.StaticText(self, -1, uncertainty),
                         (iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix += 1
        self.invariant_sizer.Add(self.invariant_high_err_tcl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix += 1
        self.invariant_sizer.Add(invariant_high_units_txt
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.invariant_box_sizer.Add(self.invariant_sizer, 0, wx.TOP|wx.BOTTOM, 10)  
       
    def _layout_warning(self):
        """
            Draw widgets related to warning
        """
        #Warning [string]
        self.warning_msg_txt = wx.StaticText(self, -1,self.warning_msg)  
        if self.qstar_container.existing_warning:
            self.warning_msg_txt.SetForegroundColour('red') 
        self.warning_sizer.AddMany([(self.warning_msg_txt, 0,
                                     wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 10)])
        
    def _layout_button(self):
        """
            Draw widgets related to button
        """
        #Close button
        id = wx.NewId()
        button_ok = wx.Button(self, id, "Ok")
        button_ok.SetToolTipString("Give Details on Computation")
        self.Bind(wx.EVT_BUTTON, self.on_close, id=id)
        self.button_sizer.AddMany([((20,20), 0 , wx.LEFT, 350),
                                   (button_ok, 0 , wx.RIGHT, 10)])
    def _do_layout(self):
        """
            Draw window content
        """
        self._define_structure()
        self._layout_shart()
        self._layout_invariant()
        self._layout_warning()
        self._layout_button()
        self.main_sizer.AddMany([(self.chart_sizer, 0, wx.ALL, 10),
                                 ( self.invariant_box_sizer, 0, wx.ALL, 10),
                                  (self.warning_sizer, 0, wx.ALL, 10),
                                  (self.button_sizer, 0, wx.ALL, 10)])
        self.SetSizer(self.main_sizer)
       
        
    def set_values(self):
        """
            Set value of txtcrtl
        """
        self.invariant_tcl.SetValue(format_number(self.qstar_container.qstar))
        self.invariant_err_tcl.SetValue(format_number(self.qstar_container.qstar_err)) 
        self.invariant_low_tcl.SetValue(format_number(self.qstar_container.qstar_low))
        self.invariant_low_err_tcl.SetValue(format_number(self.qstar_container.qstar_low_err)) 
        self.invariant_high_tcl.SetValue(format_number(self.qstar_container.qstar_high))
        self.invariant_high_err_tcl.SetValue(format_number(self.qstar_container.qstar_high_err)) 

    def get_scale(self, percentage, scale_name='scale'):
        """
            Check scale receive in this panel. 
        """
        try: 
            if percentage is None or percentage == 0.0:
                 percentage = RECTANGLE_SCALE
            percentage = float(percentage) 
        except:
            percentage = RECTANGLE_SCALE
            self.warning_msg += "Receive an invalid scale for %s\n"
            self.warning_msg += "check this value : %s\n"%(str(scale_name),str(percentage))
        return  percentage
    
    def set_color_bar(self):
        """
            Change the color for low and high bar when necessary
        """
        #warning to the user when the extrapolated invariant is greater than %5
        if self.low_scale >= 0.05:
            self.extrapolation_color_low = wx.Colour(255,  0, 0, 128)
        if self.high_scale >= 0.05:
            self.extrapolation_color_high = wx.Colour(255,  0, 0, 128)
            
    def on_close(self, event):
        """
            Close the current window
        """
        self.Close()
     
    def on_paint(self, event):
        """
            Draw the chart
        """
        dc = wx.PaintDC(self.panel_chart)
        try:
            gc = wx.GraphicsContext.Create(dc)
        except NotImplementedError:
            dc.DrawText("This build of wxPython does not support the wx.GraphicsContext "
                        "family of classes.", 25, 25)
            return
        #Start the drawing
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        gc.SetFont(font)
        # Draw a rectangle
        path = gc.CreatePath()
        path.AddRectangle(-RECTANGLE_WIDTH/2,-RECTANGLE_HEIGHT/2,
                          RECTANGLE_WIDTH/2,RECTANGLE_HEIGHT/2)
        x_origine = 20
        y_origine = 15
        #Draw low rectangle
        gc.PushState()        
        label = "Q* At Low-Q"
        PathFunc = gc.DrawPath
        w, h = gc.GetTextExtent(label)
        gc.DrawText(label, x_origine, y_origine)
        #Translate the rectangle
        x_center = x_origine + RECTANGLE_WIDTH * self.low_scale/2 + w +10
        y_center = y_origine + h
        gc.Translate(x_center, y_center)    
        gc.SetPen(wx.Pen("black", 1))
        gc.SetBrush(wx.Brush(self.extrapolation_color_low))
        low_percent = format_number(self.low_inv_percent*100)+ '%'
        x_center = 20
        y_center = -h
        gc.DrawText(low_percent, x_center, y_center)
        # Increase width by self.low_scale
        gc.Scale(self.low_scale, 1.0) 
        PathFunc(path)
        gc.PopState()  
        #Draw rectangle for invariant   
        gc.PushState()    # save it again
        y_origine += 20         
        gc.DrawText("Q* In range", x_origine, y_origine)
        # offset to the lower part of the window
        x_center = x_origine + RECTANGLE_WIDTH * self.inv_scale/2 + w + 10
        y_center = y_origine + h
        gc.Translate(x_center, y_center)
        # 128 == half transparent
        gc.SetBrush(wx.Brush(wx.Colour(67,  208,  128, 128))) 
        # Increase width by self.inv_scale
        inv_percent = format_number(self.inv_percent*100)+ '%'
        x_center = 20 
        y_center = -h
        gc.DrawText(inv_percent, x_center, y_center)
        gc.Scale(self.inv_scale, 1.0)    
        gc.DrawPath(path)
        gc.PopState()
        # restore saved state
        #Draw rectangle for high invariant
        gc.PushState() 
        y_origine += 20 
        gc.DrawText("Q* At High-Q", x_origine, y_origine) 
        #define the position of the new rectangle
        x_center = x_origine + RECTANGLE_WIDTH * self.high_scale/2 + w + 10
        y_center = y_origine + h
        gc.Translate(x_center, y_center)
        gc.SetBrush(wx.Brush(self.extrapolation_color_high)) 
        # increase scale by self.high_scale
        high_percent = format_number(self.high_inv_percent*100)+ '%'
        x_center = 20
        y_center = -h
        gc.DrawText(high_percent, x_center, y_center)
       
        gc.Scale(self.high_scale, 1.0)  
        gc.DrawPath(path)
        gc.PopState()
        
class InvariantDetailsWindow(wx.Dialog):
    def __init__(self, parent, qstar_container=None, *args, **kwds):
        kwds["size"]= (PANEL_WIDTH +100, 450)
        wx.Dialog.__init__(self, parent, *args, **kwds)
        self.container = qstar_container
        if self.container is None:
            self.container = InvariantContainer()
            self.container.qstar_total = 1.0
            self.container.qstar = 0.75
            self.container.qstar_low = 0.60
            self.container.qstar_high = 0.0049
        self.panel = InvariantDetailsPanel(parent=self, 
                                           qstar_container=self.container)
        self.Centre()
        self.ShowModal()
        self.Destroy()

class InvariantDetailsTest(wx.Frame):
    def __init__(self, parent, qstar_container=None, *args, **kwds):
        kwds["size"]= (PANEL_WIDTH , PANEL_HEIGHT)
        wx.Frame.__init__(self, parent, *args, **kwds)
        self.container = qstar_container
        if self.container is None:
            self.container = InvariantContainer()
            self.container.qstar_total = 1.0
            self.container.qstar = 0.75
            self.container.qstar_low = 0.60
            self.container.qstar_high = 0.0049
        
        self.panel = InvariantDetailsPanel(parent=self, 
                                           qstar_container=self.container)
        self.panel.ShowModal()
        self.panel.Destroy()
        self.Show()
   
if __name__ =="__main__":
    app  = wx.App()

    container = InvariantContainer()
    container.qstar_total = 100.0
    container.qstar = 15.0
    container.qstar_low = 0.001
    container.qstar_high = 100.0
    container.compute_percentage()
   
    window = InvariantDetailsTest(parent=None, id=-1,qstar_container=container,
                                    title="Invariant Details")
    window.Show()
    app.MainLoop()
