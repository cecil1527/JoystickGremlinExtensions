import dearpygui.dearpygui as dpg
import pyperclip

from jge.utils import Vec2
from jge.tuned_axis import AxisTuning, TunedAxis
from jge.trimmed_axis import Scaling, TrimmedAxis


widget_help_txt = '''Ctrl+click to enter a specific value.
Tab to go to next widget.
Shift+tab to go to previous widget.
'''

plot_help_txt = '''Click legend colors to show/hide lines.
Double-click to auto fit axis zoom.
Scroll over plot area to zoom.
Scroll over axis range to zoom just that axis.
Right-click and drag to select an area on the plot.
Right-click plot area for more options.
'''


def dpg_add_blank_line():
    '''adds blank line in dpg'''
    dpg.add_text()
    # TODO is there some other way to do this?


def calc_slopes(xs, ys):
    slopes = []
    for i in range(1, len(xs) - 1):
        # do average slope around i
        p1 = Vec2(xs[i - 1], ys[i - 1])
        p2 = Vec2(xs[i + 1], ys[i + 1])
        slope = Vec2.Slope(p1, p2)
        slopes.append(abs(slope))

    # we'll end up with 2 less points, since i did averages, so just repeat the
    # end points
    slopes.insert(0, slopes[0])
    slopes.append(slopes[-1])
    return slopes


def draw_box(y_ax, x_range = (-1, 1), y_range = (-1, 1)):
    '''draw a box surrounding x min/max and y min/max'''
    
    points = [
        (x_range[0], y_range[1]),
        (x_range[1], y_range[1]),
        (x_range[1], y_range[0]),
        (x_range[0], y_range[0]),
        (x_range[0], y_range[1]),
    ]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    # https://dearpygui.readthedocs.io/en/latest/documentation/plots.html#colors-and-styles

     # create a theme for the plot
    with dpg.theme(tag="plot_theme"):
        with dpg.theme_component(dpg.mvLineSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 255, 255, 255), category=dpg.mvThemeCat_Plots)
            # dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2, category=dpg.mvThemeCat_Plots)

    dpg.add_line_series(xs, ys, label="Limits", parent=y_ax, tag="series_data")
    dpg.bind_item_theme("series_data", "plot_theme")


class DataSeries:
    def __init__(self, label: str, xs, dpg_parent_axis):
        '''
        adds a line to the dpg parent axis. keeps track of its own xs, ys, and
        dpg tag
        '''

        self.xs = xs
        self.ys = xs
        self.tag = dpg.add_line_series(self.xs, self.ys, label=label, parent=dpg_parent_axis)

    def update_ys(self, new_ys):
        '''update ys values and sets new data for the dpg line'''
        
        self.ys = new_ys
        dpg.set_value(self.tag, [self.xs, self.ys])


class TuningWidgets:
    def __init__(self, label: str, on_update_fn):
        
        with dpg.tree_node(label=label, default_open=True):
            text_tag = dpg.add_text("Tuning (?)")
            with dpg.tooltip(text_tag):
                dpg.add_text(widget_help_txt)

            width = 800

            self.deadzone_tag = dpg.add_slider_floatx(width = width,
                label="Deadzone Point (X, Y) [can create deadzone or get out of built-in deadzone]",
                size=2, min_value=0, max_value=1, default_value=[0, 0], clamped=True, callback=on_update_fn)
            
            self.saturation_tag = dpg.add_slider_floatx(width = width,
                label="Response Curve End (X, Y) [can simulate saturation]",
                size=2, min_value=0, max_value=1, default_value=[1, 1], clamped=True, callback=on_update_fn)
            
            self.curvature_tag = dpg.add_slider_float(width = width,
                label="Curvature [unfortunately not the same as DCS's curvature values]",
                min_value=-1, max_value=1, default_value=0, clamped=True, callback=on_update_fn)
            
            self.invert_tag = dpg.add_checkbox(label="Invert", callback=on_update_fn)
            self.slider_tag = dpg.add_checkbox(label="Slider", callback=on_update_fn)
    
    def get_tuning(self) -> AxisTuning:
        deadzone_pt = Vec2.From(dpg.get_value(self.deadzone_tag))
        saturation_pt = Vec2.From(dpg.get_value(self.saturation_tag))
        curvature = dpg.get_value(self.curvature_tag)
        invert = dpg.get_value(self.invert_tag)
        
        return AxisTuning(curvature, invert, deadzone_pt, saturation_pt)


class DynamicTrimWidgets:
    def __init__(self, label: str, on_update_fn):
        
        with dpg.tree_node(label=label, default_open=True):
            text_tag = dpg.add_text("Trim (?)")
            with dpg.tooltip(text_tag):
                dpg.add_text(widget_help_txt)

            width = 800

            self.dyn_scaling_degree_tag = dpg.add_slider_float(width = width,
                label="Dynamic Scaling Degree",
                min_value=0, max_value=10, default_value=2, clamped=True, callback=on_update_fn)
                
            self.dyn_scaling_delay_tag = dpg.add_slider_float(width = width,
                label="Dynamic Scaling Delay",
                min_value=0, max_value=1, default_value=0.2, clamped=True, callback=on_update_fn)

            dpg_add_blank_line()

            self.trim_tag = dpg.add_slider_float(width = width,
                label="Trim", 
                min_value=-1, max_value=1, default_value=0, clamped=True, callback=on_update_fn)

    def get_vals(self):
        dyn_scaling_degree = dpg.get_value(self.dyn_scaling_degree_tag)
        dyn_scaling_delay = dpg.get_value(self.dyn_scaling_delay_tag)
        trim = dpg.get_value(self.trim_tag)
        
        return dyn_scaling_degree, dyn_scaling_delay, trim


class App:
    def __init__(self, plot_width: int, plot_height: int):
        self.plot_width = plot_width
        self.plot_height = plot_height
        
        self.window_name = "Primary Window"

        # all data series can share the same x-vals
        self.xs = [x / 500.0 for x in range(-500, 500)]
        self.xs = [x for x in self.xs]

        # tag the window. we'll use this tag to make it a primary window later.
        with dpg.window(tag=self.window_name):
            plot_text_tag = dpg.add_text("Plots (?)")
            with dpg.tooltip(plot_text_tag):
                dpg.add_text(plot_help_txt)

            # make graphs
            with dpg.group(horizontal=True):
                # save all data series dictionaries we get back
                self.response, y_ax = self.create_plot(
                    "Response Curves", "Joystick Input", "VJoy Output", True
                )
                draw_box(y_ax)
                self.sensitivity, y_ax = self.create_plot(
                    "Sensitivity Curves\n(Response Curve Derivative)", 
                    "Joystick Input", 
                    "Sensitivity (Delta VJoy Output / Delta Joystick Input)"
                )
                
                self.scaling, y_ax = self.create_plot(
                    "Scaling Curves",
                    "Joystick Input",
                    "Polynomial Scaling Coefficient"
                )
            
            dpg_add_blank_line()
            self.tuning_widgets = TuningWidgets("Tuning", self.update)

            dpg_add_blank_line()
            self.trim_widgets = DynamicTrimWidgets("Trim", self.update)

            dpg_add_blank_line()
            dpg.add_button(label="Copy to clipboard", callback=self.copy_to_clipboard)

        self.update()

    def create_plot(self, label: str, x_ax_label: str, y_ax_label: str, 
                    equal_aspects: bool = False):
        '''
        adds plot. 
        
        returns 
        
        1. dictionary with 3 data series for scaling vals: default, static, and
           dynamic
        2. y_axis tag, so you can plot more points if need be
        '''

        with dpg.plot(label=label, width=self.plot_width, height=self.plot_height, 
                      equal_aspects=equal_aspects):
            
            dpg.add_plot_legend()

            x_ax = dpg.add_plot_axis(dpg.mvXAxis, label=x_ax_label)
            y_ax = dpg.add_plot_axis(dpg.mvYAxis, label=y_ax_label)

            # one dictionary entry for each scaling type
            d = {
                "default": DataSeries("Default Game", self.xs, y_ax),
                "static": DataSeries("Static Scaling", self.xs, y_ax),
                "dynamic": DataSeries("Dynamic Scaling", self.xs, y_ax)
            }

            return d, y_ax

    def update(self):
        # get vals and make trimmed axis

        r_tuning = self.tuning_widgets.get_tuning()
        slider = dpg.get_value(self.tuning_widgets.slider_tag)
        tuned_axis = TunedAxis(1, r_tuning, is_slider=slider)
        
        dyn_scaling_degree, dyn_scaling_delay, trim = self.trim_widgets.get_vals()
        trimmed_axis = TrimmedAxis(tuned_axis, dyn_scaling_degree, dyn_scaling_delay)
        
        trimmed_axis.set_trim(trim)

        # update all data series

        self.response["default"].update_ys([trimmed_axis.calc_output(x, Scaling.Nil) for x in self.xs])
        self.response["static"].update_ys([trimmed_axis.calc_output(x, Scaling.Static) for x in self.xs])
        self.response["dynamic"].update_ys([trimmed_axis.calc_output(x, Scaling.Dynamic) for x in self.xs])

        self.sensitivity["default"].update_ys(calc_slopes(self.xs, self.response["default"].ys))
        self.sensitivity["static"].update_ys(calc_slopes(self.xs, self.response["static"].ys))
        self.sensitivity["dynamic"].update_ys(calc_slopes(self.xs, self.response["dynamic"].ys))

        self.scaling["default"].update_ys([trimmed_axis._get_scaling_coef(x, Scaling.Nil) for x in self.xs])
        self.scaling["static"].update_ys([trimmed_axis._get_scaling_coef(x, Scaling.Static) for x in self.xs])
        self.scaling["dynamic"].update_ys([trimmed_axis._get_scaling_coef(x, Scaling.Dynamic) for x in self.xs])

    def copy_to_clipboard(self):
        tuning = self.tuning_widgets.get_tuning()
        dyn_scaling_degree, dyn_scaling_delay, trim = self.trim_widgets.get_vals()

        s = f"tuning = {str(tuning)}"
        s += "\ntuned_axis = TunedAxis(#1, tuning, is_slider = False)"
        s += f"\ntrimmed_axis = TrimmedAxis(tuned_axis, {dyn_scaling_degree}, {dyn_scaling_delay})"

        pyperclip.copy(s)


if __name__ == "__main__":
    dpg.create_context()
    app = App(600, 600)
    dpg.configure_app(wait_for_input=True)
    dpg.create_viewport(title="Trim Axis Graphs")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.maximize_viewport()
    dpg.set_primary_window(app.window_name, True)
    dpg.start_dearpygui()
    dpg.destroy_context()
