from dsr_msgs2.srv import ConfigCreateTcp

class TcpManager:
    def __init__(self, node, robot_id='dsr01'):
        self.node = node
        self.client = self.node.create_client(
            ConfigCreateTcp, 
            f'/{robot_id}/tcp/config_create_tcp'
        )

    def set_new_tcp(self, name, pos):
        if not self.client.wait_for_service(timeout_sec=2.0):
            self.node.get_logger().error("TCP 서비스 서버를 찾을 수 없습니다.")
            return False

        req = ConfigCreateTcp.Request()
        req.name = name
        req.pos = pos

        # 비동기로 실행하고 결과를 기다림
        future = self.client.call_async(req)
        return future