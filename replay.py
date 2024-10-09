import pyvista as pv

import sys
import time


last_mesh = None
all_points = None
all_point_types = None
plotter = None

colours = {1.1: "lightblue", 2.1: "green", 2.2: "turquoise", 3: "#eeeeee"}
colours = {1.1: "blue", 2.2: "turquoise"}

log_step = None
time_step = None
slider = None

def create_mesh(step):
    step_count = step
    value = step_count
    global last_mesh, all_points, all_point_types, plotter
    global log_step
    global time_step
    global slider

    index = int(value)
    timeindex_offset = 1
    time_ms = (index+timeindex_offset)*log_step*time_step*1000

    curr_points = all_points[index]
    curr_types = all_point_types[index]

    print(
        "Changing to time %g ms, step: %s (%s), displaying %i points "
        % (time_ms, index, value, len(curr_points))
    )

    if last_mesh is None:
        last_mesh = pv.PolyData(curr_points)
        last_mesh["types"] = curr_types
        print(last_mesh)

        plotter.add_mesh(
            last_mesh,
            render_points_as_spheres=True,
            cmap=[c for c in colours.values()],
            point_size=3,
        )
    else:
        last_mesh.points = curr_points

    plotter.render()

    time.sleep(0.1)

    return


def replay_simulation(position_file):
    global last_mesh, all_points, all_point_types, plotter
    global log_step
    global time_step
    global slider

    points = []
    types = []

    line_count = 0
    pcount = 0

    all_points = []
    all_point_types = []

    time_count = 0

    include_boundary = False

    for line in open(position_file):
        ws = line.split()
        # print(ws)

        if line_count == 6:
            numOfElasticP = int(ws[0])
        if line_count == 7:
            numOfLiquidP = int(ws[0])
        if line_count == 8:
            numOfBoundaryP = int(ws[0])
        if line_count == 9:
            time_step = float(ws[0])
        if line_count == 10:
            log_step = int(ws[0])

        if len(ws) == 4:
            type = float(ws[3])

            if not (type == 3 and not include_boundary):
                points.append([float(ws[0]), float(ws[1]), float(ws[2])])
                types.append(type)

        if log_step is not None:
            pcount += 1

            if pcount == numOfBoundaryP + numOfElasticP + numOfLiquidP:
                print(
                    "End of one batch of %i added, %i total points (B: %i, E: %i, L: %i) at line %i, time count: %i"
                    % (
                        len(points),
                        pcount,
                        numOfBoundaryP,
                        numOfElasticP,
                        numOfLiquidP,
                        line_count,
                        time_count,
                    )
                )
                all_points.append(points)
                all_point_types.append(types)

                points = []
                types = []
                pcount = 0
                numOfBoundaryP = 0

                time_count += 1

        line_count += 1

    print(
        "Loaded positions with %i elastic, %i liquid and %i boundary points (%i total), %i lines. Time step: %s, log step:  %s"
        % (
            numOfElasticP,
            numOfLiquidP,
            numOfBoundaryP,
            numOfElasticP + numOfLiquidP + numOfBoundaryP,
            line_count,
            time_step,
            log_step,
        )
    )

    print("Num of time points found: %i" % len(all_points))

    plotter = pv.Plotter()
    plotter.set_background("lightgrey")

    last_mesh = None

    create_mesh(0)

    max_time = len(all_points) - 1

    slider = plotter.add_slider_widget(
        create_mesh, rng=[0, max_time], value=max_time, title="Time point"
    )

    plotter.add_timer_event(
        max_steps=len(all_points), duration=200, callback=create_mesh
    )

    plotter.show()


if __name__ == "__main__":
    position_file = "buffers/position_buffer.txt"

    if len(sys.argv) == 2:
        position_file = sys.argv[1]

    replay_simulation(position_file)
