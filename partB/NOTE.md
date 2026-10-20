# Part B: G1 Walking in a Circle

## What I changed

In `deploy/deploy_mujoco/configs/g1.yaml` I changed one line:

    cmd_init: [0.5, 0, 0]   ->   cmd_init: [0.4, 0, 0.4]

The three values are the velocity command [vx, vy, yaw_rate]:
forward speed (m/s), sideways speed (m/s), turning rate (rad/s).

## Why this produces circular motion

The default command has zero yaw rate, so the robot walks straight.
The policy was trained to track a commanded velocity, so if I command a
constant forward speed v and a constant turning rate w at the same time,
the robot keeps rotating its heading while moving along it. A constant v
with a constant w traces a circle of radius R = v / w = 0.4 / 0.4 = 1 m.
No code was changed, only the command.

## 1. What inputs does the policy receive, and where do they come from?

The policy gets a 47-dimensional observation vector, built in
`deploy_mujoco.py` every 10 simulation steps (50 Hz):

| Indices | Content | Source |
|---|---|---|
| 0-2 | base angular velocity x 0.25 | `d.qvel[3:6]` (MuJoCo state) |
| 3-5 | gravity direction in the body frame | computed from base quaternion `d.qpos[3:7]` |
| 6-8 | command x `cmd_scale` [2, 2, 0.25] | `cmd_init` in g1.yaml (set by me) |
| 9-20 | joint positions minus default angles (12) | `d.qpos[7:]` |
| 21-32 | joint velocities x 0.05 (12) | `d.qvel[6:]` |
| 33-44 | previous action (12) | policy's last output |
| 45-46 | sin and cos of gait phase | computed from sim time, period 0.8 s |

Everything comes from the MuJoCo simulation state, except the command
(from the config file) and the gait clock (computed from time).

## 2. What does the policy output, and how does it become joint torques?

The policy (TorchScript network `motion.pt`) outputs 12 numbers, one per
leg joint (6 per leg). They are not torques. They are converted in two steps:

1. Action to target joint angle:

       target_q = action * action_scale + default_angles     (action_scale = 0.25)

2. A PD controller turns the target angle into torque, evaluated at every
   simulation step (500 Hz, dt = 0.002 s):

       tau = kp * (target_q - q) + kd * (0 - dq)

   with per-joint gains kps = [100, 100, 100, 150, 40, 40, ...] and
   kds = [2, 2, 2, 4, 2, 2, ...] from g1.yaml. The result is written to
   `d.ctrl` and MuJoCo applies it as joint torque.

So the policy runs at 50 Hz (control_decimation = 10) and the PD loop
runs at 500 Hz, holding the last target between policy updates.