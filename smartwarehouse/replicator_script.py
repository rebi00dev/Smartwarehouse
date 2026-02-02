import omni.replicator.core as rep

with rep.new_layer():

    clock = rep.get.prim_at_path("/World/AlarmClock_Retro")
    dice = rep.get.prim_at_path("/World/D6")
    lemon = rep.get.prim_at_path("/World/Lemon_02")

    # ✅ semantics 필수
#    with clock: rep.modify.semantics([('class', 'clock')])
#    with dice: rep.modify.semantics([('class', 'dice')])
#    with lemon: rep.modify.semantics([('class', 'lemon')])

    camera = rep.create.camera()
    render_product = rep.create.render_product(camera, resolution=(640,640))
    light = rep.create.light(light_type="Sphere")

    writer = rep.writers.get("BasicWriter")
    writer.initialize(
        output_dir="/home/rokey/IsaacSim-ros_workspaces/humble_ws/src/smartwarehouse/yolo_data_output",
        rgb=True,
        bounding_box_2d_tight=True,
        semantic_types=["class"]
    )
    writer.attach([render_product])

    targets = [clock, dice, lemon]

    with rep.trigger.on_frame(max_execs=1000):

        with camera:
            rep.modify.attribute("focalLength", rep.distribution.uniform(12, 24))
            rep.modify.pose(
                position=rep.distribution.uniform((-1.6,-0.4,1.8),(-1.2,0.0,2.2)),
                look_at=(-0.803,0.219,1.0)
            )

        with light:
            rep.modify.pose(position=rep.distribution.uniform((-5,-5,5),(5,5,8)))
            rep.modify.attribute("intensity", rep.distribution.uniform(5000,20000))

rep.orchestrator.run()
