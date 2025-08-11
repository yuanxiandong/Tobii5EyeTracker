import mss
import numpy as np
import cv2
import socket
import time
from typing import Tuple, Optional


class GazeVisualizationConfig:
    """配置类 - 集中管理所有配置参数"""
    
    # 网络配置
    HOST = '127.0.0.1'
    PORT = 1235
    BUFFER_SIZE = 1024
    
    # 显示配置
    BACKGROUND_WIDTH = 1920
    BACKGROUND_HEIGHT = 1080
    BACKGROUND_COLOR = (30, 30, 30)  # 深灰色背景
    WINDOW_NAME = 'Gaze Visualization'
    WINDOW_POSITION = (100, 100)
    
    # 网格和参考线配置
    GRID_SIZE = 100
    REFERENCE_LINE_COLOR = (60, 60, 60)
    GRID_LINE_COLOR = (40, 40, 40)
    
    # 眼动点可视化配置
    GAZE_OUTER_CIRCLE_RADIUS = 20
    GAZE_INNER_CIRCLE_RADIUS = 8
    GAZE_CENTER_RADIUS = 2
    CROSSHAIR_LENGTH = 30
    
    # 颜色配置
    GAZE_OUTER_COLOR = (0, 0, 255)  # 红色
    GAZE_INNER_COLOR = (0, 255, 0)  # 绿色
    GAZE_CENTER_COLOR = (255, 255, 255)  # 白色
    CROSSHAIR_COLOR = (0, 255, 255)  # 黄色
    TEXT_COLOR = (255, 255, 255)  # 白色
    SECONDARY_TEXT_COLOR = (200, 200, 200)  # 浅灰色
    HELP_TEXT_COLOR = (100, 100, 100)  # 深灰色


class GazeVisualizer:
    """眼动追踪可视化主类"""
    
    def __init__(self, config: GazeVisualizationConfig = None):
        """初始化可视化器"""
        self.config = config or GazeVisualizationConfig()
        self.show_screenshot = False
        
        # 初始化网络组件
        self.socket = self._setup_socket()
        
        # 初始化屏幕截取
        self.screen_capture = mss.mss()
        self.monitor = self._setup_monitor()
        
        # 初始化显示窗口
        self._setup_window()
        
    def _setup_socket(self) -> socket.socket:
        """设置UDP套接字"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.config.HOST, self.config.PORT))
        return sock
    
    def _setup_monitor(self) -> dict:
        """设置显示器"""
        monitors = self.screen_capture.monitors
        print(f"可用显示器数量: {len(monitors)}")
        
        for i, monitor in enumerate(monitors):
            print(f"显示器 {i}: {monitor}")
        
        # 使用主显示器（索引1通常是主显示器）
        monitor_number = 1 if len(monitors) > 1 else 0
        print(f"使用显示器: {monitor_number}")
        
        return monitors[monitor_number]
    
    def _setup_window(self) -> None:
        """设置显示窗口"""
        cv2.namedWindow(self.config.WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.moveWindow(self.config.WINDOW_NAME, *self.config.WINDOW_POSITION)
    
    def _create_clean_background(self) -> np.ndarray:
        """创建带网格的干净背景"""
        frame = np.full(
            (self.config.BACKGROUND_HEIGHT, self.config.BACKGROUND_WIDTH, 3),
            self.config.BACKGROUND_COLOR,
            dtype=np.uint8
        )
        
        # 添加中心参考线
        self._draw_reference_lines(frame)
        
        # 添加网格线
        self._draw_grid(frame)
        
        return frame
    
    def _draw_reference_lines(self, frame: np.ndarray) -> None:
        """绘制参考线"""
        height, width = frame.shape[:2]
        color = self.config.REFERENCE_LINE_COLOR
        
        # 水平中心线
        cv2.line(frame, (0, height//2), (width, height//2), color, 1)
        # 垂直中心线
        cv2.line(frame, (width//2, 0), (width//2, height), color, 1)
    
    def _draw_grid(self, frame: np.ndarray) -> None:
        """绘制网格"""
        height, width = frame.shape[:2]
        color = self.config.GRID_LINE_COLOR
        grid_size = self.config.GRID_SIZE
        
        # 垂直网格线
        for i in range(0, width, grid_size):
            cv2.line(frame, (i, 0), (i, height), color, 1)
        
        # 水平网格线
        for i in range(0, height, grid_size):
            cv2.line(frame, (0, i), (width, i), color, 1)
    
    def _create_screenshot_background(self) -> np.ndarray:
        """创建截屏背景"""
        try:
            screenshot_monitor = {
                'top': 0,
                'left': 0,
                'width': self.monitor['width'],
                'height': self.monitor['height']
            }
            
            screenshot = self.screen_capture.grab(screenshot_monitor)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2RGB)
            
            # 调整尺寸
            if (frame.shape[1] != self.config.BACKGROUND_WIDTH or 
                frame.shape[0] != self.config.BACKGROUND_HEIGHT):
                frame = cv2.resize(frame, (self.config.BACKGROUND_WIDTH, 
                                         self.config.BACKGROUND_HEIGHT))
            
            return frame
            
        except Exception as e:
            print(f"截屏失败: {e}")
            return self._create_error_frame()
    
    def _create_error_frame(self) -> np.ndarray:
        """创建错误显示帧"""
        frame = np.zeros(
            (self.config.BACKGROUND_HEIGHT, self.config.BACKGROUND_WIDTH, 3),
            dtype=np.uint8
        )
        
        cv2.putText(
            frame, "Screenshot failed - using black background",
            (50, self.config.BACKGROUND_HEIGHT//2),
            cv2.FONT_HERSHEY_SIMPLEX, 1, self.config.TEXT_COLOR, 2
        )
        
        return frame
    
    def _draw_gaze_point(self, frame: np.ndarray, gaze_x: int, gaze_y: int) -> None:
        """绘制眼动点"""
        # 外圈（红色）
        cv2.circle(frame, (gaze_x, gaze_y), 
                  self.config.GAZE_OUTER_CIRCLE_RADIUS, 
                  self.config.GAZE_OUTER_COLOR, 2)
        
        # 内圈（绿色填充）
        cv2.circle(frame, (gaze_x, gaze_y), 
                  self.config.GAZE_INNER_CIRCLE_RADIUS, 
                  self.config.GAZE_INNER_COLOR, -1)
        
        # 中心点（白色）
        cv2.circle(frame, (gaze_x, gaze_y), 
                  self.config.GAZE_CENTER_RADIUS, 
                  self.config.GAZE_CENTER_COLOR, -1)
        
        # 十字准星
        crosshair_len = self.config.CROSSHAIR_LENGTH
        cv2.line(frame, (gaze_x - crosshair_len, gaze_y), 
                (gaze_x + crosshair_len, gaze_y), 
                self.config.CROSSHAIR_COLOR, 1)
        cv2.line(frame, (gaze_x, gaze_y - crosshair_len), 
                (gaze_x, gaze_y + crosshair_len), 
                self.config.CROSSHAIR_COLOR, 1)
    
    def _draw_text_info(self, frame: np.ndarray, gaze_x: int, gaze_y: int, 
                       gaze_x_norm: float, gaze_y_norm: float) -> None:
        """绘制文本信息"""
        # 坐标信息
        coord_text = f"({gaze_x_norm:.3f}, {gaze_y_norm:.3f})"
        cv2.putText(frame, coord_text, (gaze_x + 25, gaze_y - 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.config.TEXT_COLOR, 2)
        
        # 像素坐标
        pixel_text = f"[{gaze_x}, {gaze_y}]"
        cv2.putText(frame, pixel_text, (gaze_x + 25, gaze_y + 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                   self.config.SECONDARY_TEXT_COLOR, 1)
        
        # 顶部信息栏
        mode_text = "Screenshot Mode" if self.show_screenshot else "Clean Background Mode"
        info_text = (f"Gaze Tracking ({mode_text}) | "
                    f"Normalized: ({gaze_x_norm:.3f}, {gaze_y_norm:.3f}) | "
                    f"Pixel: [{gaze_x}, {gaze_y}]")
        cv2.putText(frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.config.TEXT_COLOR, 2)
        
        # 帮助信息
        help_text = "Press SPACE to toggle mode | 'q' or ESC to exit"
        cv2.putText(frame, help_text, 
                   (10, self.config.BACKGROUND_HEIGHT - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                   self.config.HELP_TEXT_COLOR, 1)
    
    def _parse_gaze_data(self, message: bytes) -> Optional[Tuple[float, float]]:
        """解析眼动数据"""
        try:
            row = message.decode('utf-8').split(',')
            if len(row) != 3:
                return None
            
            gaze_x_norm = float(row[1])  # 归一化坐标 (0-1)
            gaze_y_norm = float(row[2])  # 归一化坐标 (0-1)
            
            return gaze_x_norm, gaze_y_norm
            
        except (ValueError, UnicodeDecodeError) as e:
            print(f"数据解析错误: {e}")
            return None
    
    def _handle_key_input(self, key: int) -> bool:
        """处理键盘输入"""
        if key == ord('q') or key == 27:  # q键或ESC键退出
            return False
        elif key == 32:  # 空格键切换模式
            self.show_screenshot = not self.show_screenshot
            mode_name = "截屏模式" if self.show_screenshot else "干净背景模式"
            print(f"切换到: {mode_name}")
        
        return True
    
    def print_startup_info(self) -> None:
        """打印启动信息"""
        print('等待消息中...')
        print('请确保先运行 eye_tracking.exe 来发送眼动数据')
        print('注意：切换到截屏模式时，建议将此程序窗口移动到屏幕边缘以避免递归显示')
        print('快捷键：空格键切换模式，q或ESC退出')
    
    def cleanup(self) -> None:
        """清理资源"""
        cv2.destroyAllWindows()
        self.socket.close()
        print('\n程序已停止\n')
    
    def run(self) -> None:
        """主运行循环"""
        self.print_startup_info()
        
        while True:
            try:
                # 接收眼动数据
                message, client_addr = self.socket.recvfrom(self.config.BUFFER_SIZE)
                
                # 解析数据
                gaze_data = self._parse_gaze_data(message)
                if gaze_data is None:
                    continue
                
                gaze_x_norm, gaze_y_norm = gaze_data
                
                # 创建背景帧
                if self.show_screenshot:
                    frame = self._create_screenshot_background()
                else:
                    frame = self._create_clean_background()
                
                # 计算像素坐标
                gaze_x = int(gaze_x_norm * frame.shape[1])
                gaze_y = int(gaze_y_norm * frame.shape[0])
                
                # 绘制眼动点
                self._draw_gaze_point(frame, gaze_x, gaze_y)
                
                # 绘制文本信息
                self._draw_text_info(frame, gaze_x, gaze_y, gaze_x_norm, gaze_y_norm)
                
                # 显示帧
                cv2.imshow(self.config.WINDOW_NAME, frame)
                
                # 处理键盘输入
                key = cv2.waitKey(1) & 0xFF
                if not self._handle_key_input(key):
                    break
                    
            except KeyboardInterrupt:
                break
        
        self.cleanup()


def main():
    """主函数"""
    visualizer = GazeVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()
