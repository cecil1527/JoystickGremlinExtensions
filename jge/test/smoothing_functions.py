import dearpygui.dearpygui as dpg

from jge.easing_functions import SmoothStart, SmoothStop, SmoothStep


class App:
    def __init__(self) -> None:
        self.smooth_start = SmoothStart(1)
        self.smooth_stop = SmoothStop(1)
        self.smooth_step = SmoothStep(1, 1)

        dpg.create_context()

        with dpg.window(label="Tutorial") as self.window_id:
            self.degree_id = dpg.add_drag_double(
                label="Power",
                callback=self.update,
                speed=0.01,
                default_value=1,
                min_value=-20,
                max_value=20,
                clamped=True,
            )

            self.make_plot()

        dpg.set_primary_window(self.window_id, True)

        dpg.create_viewport(title="DCS Sigmoid", width=800, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()

    def __del__(self):
        dpg.destroy_context()

    def make_plot(self):
        # https://dearpygui.readthedocs.io/en/latest/documentation/plots.html
        with dpg.plot(
            no_title=True, height=-1, width=-1, equal_aspects=True
        ) as self.plot_id:
            dpg.add_plot_legend()
            self.x_ax_id = dpg.add_plot_axis(dpg.mvXAxis, label="x")
            self.y_ax_id = dpg.add_plot_axis(dpg.mvYAxis, label="y")

        self.xs = [x / 300.0 for x in range(-0, 301, 1)]
        ys = [x for x in self.xs]

        self.smooth_start_tag = dpg.add_line_series(
            self.xs, ys, label="Smooth Start", parent=self.y_ax_id
        )
        self.smooth_stop_tag = dpg.add_line_series(
            self.xs, ys, label="Smooth Stop", parent=self.y_ax_id
        )
        self.smooth_step_tag = dpg.add_line_series(
            self.xs, ys, label="Smooth Step", parent=self.y_ax_id
        )

    def update(self):
        degree = dpg.get_value(self.degree_id)
        # smooth start
        self.smooth_start._degree = degree
        ys = [self.smooth_start(x) for x in self.xs]
        dpg.set_value(self.smooth_start_tag, [self.xs, ys])
        # smooth stop
        self.smooth_stop._degree = degree
        ys = [self.smooth_stop(x) for x in self.xs]
        dpg.set_value(self.smooth_stop_tag, [self.xs, ys])
        # smooth step
        self.smooth_step._smooth_start._degree = degree
        self.smooth_step._smooth_stop._degree = degree
        ys = [self.smooth_step(x) for x in self.xs]
        dpg.set_value(self.smooth_step_tag, [self.xs, ys])


if __name__ == "__main__":
    app = App()
