import os
import mujoco
import numpy as np
import imageio

HERE = os.path.dirname(os.path.abspath(__file__))
DESC = r"C:\Users\user\g1-internship\unitree_rl_gym\resources\robots\g1_description"
CSV = os.path.join(HERE, "motion.csv")
OUT = os.path.join(HERE, "motion.mp4")
FPS = 30

# Load the 29-DoF G1 and add a simple floor to its XML
xml = open(os.path.join(DESC, "g1_29dof.xml")).read()
floor = '<geom name="floor_plane" type="plane" size="0 0 0.05" rgba="0.6 0.6 0.6 1"/>'
i = xml.rfind("</worldbody>")
xml = xml[:i] + floor + xml[i:]
scene_path = os.path.join(DESC, "g1_29dof_floor.xml")
open(scene_path, "w").write(xml)
model = mujoco.MjModel.from_xml_path(scene_path)



data = mujoco.MjData(model)

motion = np.loadtxt(CSV, delimiter=",")
print("CSV shape:", motion.shape, "| model nq:", model.nq)
assert motion.shape[1] == model.nq, "Column count != model nq; check XML choice"

print("Joint order in model:")
for i in range(1, model.njnt):
    print(i - 1, mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i))

renderer = mujoco.Renderer(model, height=480, width=640)
cam = mujoco.MjvCamera()
cam.distance, cam.azimuth, cam.elevation = 3.0, 140, -15

frames = []
for row in motion:
    data.qpos[0:3] = row[0:3]
    data.qpos[3:7] = [row[6], row[3], row[4], row[5]]  # CSV xyzw -> MuJoCo wxyz
    data.qpos[7:] = row[7:]
    mujoco.mj_forward(model, data)
    cam.lookat[:] = data.qpos[0:3]
    renderer.update_scene(data, cam)
    frames.append(renderer.render())

imageio.mimsave(OUT, frames, fps=FPS)
print("Saved", OUT, "frames:", len(frames))