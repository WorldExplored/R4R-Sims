# Frozen Blocks flight route

Defined before the measured runs after inspection of the native Blocks view and the failed smoke captures. The scene spawns Drone1 at NED (-1.0, 8.0, -4.0) m with yaw -45°. Gravity settles it near z=-2.69 m on the Blocks surface before takeoff. The planned route keeps the central open area visible; actual clearance and controller completion remain to be measured.

| Phase | Requested absolute NED position (m) | Yaw | Command |
| --- | --- | --- | --- |
| Takeoff | Native takeoff target from current settled state | -45° initial | Simple Flight `takeoff_async(timeout_sec=25)` |
| Hover 1 | Native achieved hover position | Native heading | `hover_async`; 3 s wall hold |
| Horizontal | (1.5, 8.0, -4.0) | Native heading | `move_to_position_async`, 1 m/s |
| Vertical up | (1.5, 8.0, -5.0) | Native heading | `move_to_position_async`, 1 m/s; NED z decreases |
| Yaw | Same commanded position | -15° absolute (-0.261799 rad) | `rotate_to_yaw_async` |
| Hover 2 | Native achieved position | Native heading | `hover_async`; 3 s wall hold |
| Return | (-1.0, 8.0, -4.0) | Native heading | `move_to_position_async`, 1 m/s |
| Land | Native controller descent | Native heading | `land_async(timeout_sec=25)` |

The takeoff target is determined by Project AirSim's native controller from its current estimated state, so it is logged after execution rather than invented here. Both measured repeats use the same config, route code and scene reload. A false task result is retained as a failed controller outcome even if the vehicle moves.
