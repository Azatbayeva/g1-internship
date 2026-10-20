# Unitree G1 Motion Rendering

## Overview

This project loads a Unitree G1 robot model in MuJoCo, reads a motion sequence exported from UltimateBots Studio as a CSV file, and renders the motion to an MP4 video.

## Files

- `motion.csv` — exported robot motion data.
- `motion.mp4` — rendered motion video.
- `play_motion.py` — Python script used to load the robot, play the motion, and render the video.
- `prompt.txt` — text prompt used to generate the motion.
- `studio_preview.mp4` — preview exported or recorded from UltimateBots Studio.

## Requirements

Python packages:
- `mujoco`
- `numpy`
- `imageio`

Install them with:

```bash
pip install mujoco numpy imageio
```

The Unitree RL Gym repository and the Unitree G1 robot description files must also be available.

## Reproduce

1. Ensure the G1 robot XML model is available.
2. Update the robot description path in `play_motion.py` to match your local installation.
3. Place `motion.csv` in the same directory as `play_motion.py`.
4. Run:

```bash
python play_motion.py
```

The script generates `motion.mp4`.

## How were the CSV columns identified?

The CSV structure was inspected by examining its header and sample rows. The column count was compared with the MuJoCo model's generalized position dimension (`model.nq`), and the playback code was checked to understand how values are assigned to the root position, root quaternion, and joint positions. The exact meaning and ordering of the columns should be confirmed against the UltimateBots Studio export format and the G1 model's joint definitions.
